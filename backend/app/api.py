from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import (
    AdminUser,
    CurrentUser,
    DbSession,
    api_error,
    decode_token,
    enforce_same_origin,
    hash_password,
    settings,
    token_hash,
    utcnow,
    verify_password,
)
from app.models import (
    Career,
    CareerSkill,
    Milestone,
    MilestoneTask,
    Project,
    RefreshToken,
    Resource,
    Roadmap,
    RoadmapPhase,
    RoadmapTask,
    Skill,
    SkillPrerequisite,
    SkillResource,
    TaskProgress,
    User,
    UserSkill,
)
from app.schemas import (
    AssessmentIn,
    AuthOut,
    CareerIn,
    CareerOut,
    CareerProjectIn,
    CareerSkillIn,
    GenerateRoadmapIn,
    LoginIn,
    PrerequisiteIn,
    ProfileIn,
    ProjectIn,
    ProjectOut,
    ProjectSkillIn,
    RegisterIn,
    ResourceIn,
    ResourceOut,
    RoadmapPatchIn,
    SkillIn,
    TaskOrderIn,
    TaskStatusIn,
    UserOut,
    UserSkillIn,
)
from app.services import (
    PrerequisiteCycleError,
    compatibility,
    gap_report,
    generate_roadmap,
    issue_session,
    recommended_projects,
    record_generation_failure,
)

router = APIRouter(prefix="/api/v1")


def ok(data, response: Response | None = None, created: bool = False):
    if response and created:
        response.status_code = status.HTTP_201_CREATED
    return {"success": True, "data": data}


def set_refresh_cookie(response: Response, refresh: str) -> None:
    response.set_cookie("refresh_token", refresh, httponly=True, secure=settings.environment == "production", samesite="lax", max_age=settings.refresh_token_days * 86400, path="/api/v1/auth")


def as_skill(value: Skill) -> dict:
    return {"id": value.id, "name": value.name, "description": value.description, "category": value.category}


def as_profile(value) -> dict:
    return {"id": value.id, "user_id": value.user_id, "full_name": value.full_name, "education": value.education, "experience_level": value.experience_level, "weekly_hours": value.weekly_hours, "bio": value.bio, "target_career_id": value.target_career_id}


@router.post("/auth/register")
def register(payload: RegisterIn, response: Response, db: DbSession):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise api_error("CONFLICT", "An account with this email already exists", 409)
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    from app.models import Profile
    user.profile = Profile(full_name=payload.full_name)
    db.add(user)
    db.flush()
    access, refresh = issue_session(db, user.id)
    db.commit()
    set_refresh_cookie(response, refresh)
    response.status_code = 201
    return ok(AuthOut(access_token=access, user=UserOut.model_validate(user)).model_dump())


@router.post("/auth/login")
def login(payload: LoginIn, response: Response, db: DbSession):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise api_error("INVALID_CREDENTIALS", "Email or password is incorrect", 401)
    if not user.is_active:
        raise api_error("ACCOUNT_INACTIVE", "This account is inactive", 403)
    access, refresh = issue_session(db, user.id)
    db.commit()
    set_refresh_cookie(response, refresh)
    return ok(AuthOut(access_token=access, user=UserOut.model_validate(user)).model_dump())


@router.post("/auth/refresh")
def refresh(response: Response, request: Request, db: DbSession, refresh_token: str | None = Cookie(default=None)):
    enforce_same_origin(request)
    if not refresh_token:
        raise api_error("UNAUTHENTICATED", "Refresh token is required", 401)
    payload = decode_token(refresh_token, "refresh")
    token = db.scalar(select(RefreshToken).where(RefreshToken.jti == payload["jti"]))
    if not token or token.token_digest != token_hash(refresh_token):
        raise api_error("UNAUTHENTICATED", "Invalid refresh token", 401)
    if token.revoked_at:
        db.query(RefreshToken).filter(RefreshToken.user_id == token.user_id, RefreshToken.revoked_at.is_(None)).update({RefreshToken.revoked_at: utcnow()})
        db.commit()
        raise api_error("TOKEN_REUSE", "Session was revoked for safety; please log in again", 401)
    token.revoked_at = utcnow()
    access, new_refresh = issue_session(db, token.user_id)
    new_payload = decode_token(new_refresh, "refresh")
    token.replaced_by_jti = new_payload["jti"]
    db.commit()
    set_refresh_cookie(response, new_refresh)
    return ok({"access_token": access, "token_type": "bearer"})


@router.post("/auth/logout")
def logout(response: Response, request: Request, db: DbSession, refresh_token: str | None = Cookie(default=None)):
    enforce_same_origin(request)
    if refresh_token:
        try:
            payload = decode_token(refresh_token, "refresh")
            token = db.scalar(select(RefreshToken).where(RefreshToken.jti == payload["jti"]))
            if token:
                token.revoked_at = utcnow()
                db.commit()
        except HTTPException:
            pass
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return ok({"logged_out": True})


@router.get("/auth/me")
def me(user: CurrentUser):
    return ok(UserOut.model_validate(user).model_dump())


@router.get("/profile")
def get_profile(user: CurrentUser):
    return ok(as_profile(user.profile))


@router.put("/profile")
def update_profile(payload: ProfileIn, user: CurrentUser, db: DbSession):
    if payload.target_career_id and not db.get(Career, payload.target_career_id):
        raise api_error("NOT_FOUND", "Career not found", 404)
    for key, value in payload.model_dump().items():
        setattr(user.profile, key, value)
    db.commit()
    db.refresh(user.profile)
    return ok(as_profile(user.profile))


@router.get("/skills")
def list_skills(db: DbSession):
    return ok([as_skill(value) for value in db.scalars(select(Skill).order_by(Skill.name)).all()])


@router.get("/skills/{skill_id}")
def get_skill(skill_id: UUID, db: DbSession):
    value = db.get(Skill, skill_id)
    if not value: raise api_error("NOT_FOUND", "Skill not found", 404)
    return ok(as_skill(value))


@router.get("/profile/skills")
def profile_skills(user: CurrentUser, db: DbSession):
    rows = db.execute(select(UserSkill, Skill).join(Skill).where(UserSkill.user_id == user.id)).all()
    return ok([{"id": row.id, "skill_id": row.skill_id, "proficiency_level": row.proficiency_level, "notes": row.notes, "skill": as_skill(skill)} for row, skill in rows])


@router.post("/profile/skills")
def add_profile_skill(payload: UserSkillIn, response: Response, user: CurrentUser, db: DbSession):
    if not db.get(Skill, payload.skill_id): raise api_error("NOT_FOUND", "Skill not found", 404)
    record = UserSkill(user_id=user.id, **payload.model_dump())
    db.add(record)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise api_error("CONFLICT", "This skill is already in your profile", 409)
    response.status_code = 201
    return ok({"id": record.id, **payload.model_dump()}, response)


@router.patch("/profile/skills/{skill_id}")
def patch_profile_skill(skill_id: UUID, payload: UserSkillIn, user: CurrentUser, db: DbSession):
    if skill_id != payload.skill_id: raise api_error("VALIDATION_ERROR", "Path and body skill IDs must match", 422)
    record = db.scalar(select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.skill_id == skill_id))
    if not record: raise api_error("NOT_FOUND", "Your skill record was not found", 404)
    record.proficiency_level, record.notes = payload.proficiency_level, payload.notes
    db.commit()
    return ok({"id": record.id, **payload.model_dump()})


@router.delete("/profile/skills/{skill_id}", status_code=204)
def delete_profile_skill(skill_id: UUID, user: CurrentUser, db: DbSession):
    record = db.scalar(select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.skill_id == skill_id))
    if not record: raise api_error("NOT_FOUND", "Your skill record was not found", 404)
    db.delete(record); db.commit()
    return Response(status_code=204)


@router.post("/assessments")
def submit_assessment(payload: AssessmentIn, user: CurrentUser, db: DbSession):
    if len({item.skill_id for item in payload.skills}) != len(payload.skills): raise api_error("VALIDATION_ERROR", "Skills must be unique", 422)
    for item in payload.skills:
        if not db.get(Skill, item.skill_id): raise api_error("NOT_FOUND", "Skill not found", 404)
        record = db.scalar(select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.skill_id == item.skill_id))
        if record:
            record.proficiency_level, record.notes = item.proficiency_level, item.notes
        else: db.add(UserSkill(user_id=user.id, **item.model_dump()))
    db.commit()
    return ok({"updated": len(payload.skills)})


@router.get("/careers")
def list_careers(db: DbSession, q: str | None = None):
    query = select(Career).order_by(Career.name)
    if q:
        term = f"%{q.strip()}%"
        query = query.where(Career.name.ilike(term) | Career.category.ilike(term) | Career.description.ilike(term))
    return ok([CareerOut.model_validate(value).model_dump() for value in db.scalars(query).all()])


@router.get("/careers/{career_id}")
def get_career(career_id: UUID, db: DbSession):
    value = db.get(Career, career_id)
    if not value: raise api_error("NOT_FOUND", "Career not found", 404)
    return ok(CareerOut.model_validate(value).model_dump())


@router.get("/careers/{career_id}/skills")
def career_skills(career_id: UUID, db: DbSession):
    if not db.get(Career, career_id): raise api_error("NOT_FOUND", "Career not found", 404)
    rows = db.execute(select(CareerSkill, Skill).join(Skill).where(CareerSkill.career_id == career_id)).all()
    return ok([{"career_id": row.career_id, "skill_id": row.skill_id, "required_level": row.required_level, "importance": row.importance, "relevance": row.relevance, "skill": as_skill(skill)} for row, skill in rows])


@router.get("/careers/{career_id}/skill-gap")
def skill_gap(career_id: UUID, user: CurrentUser, db: DbSession):
    try: return ok(gap_report(db, user.id, career_id).model_dump())
    except (ValueError, PrerequisiteCycleError) as exc: raise api_error("ANALYSIS_ERROR", str(exc), 422)


@router.post("/recommendations/careers")
def career_recommendations(user: CurrentUser, db: DbSession):
    entries = []
    for career in db.scalars(select(Career)).all():
        try: entries.append({**CareerOut.model_validate(career).model_dump(), "compatibility": compatibility(db, user.id, career.id)})
        except ValueError: continue
    return ok(sorted(entries, key=lambda item: item["compatibility"], reverse=True))


def task_with_status(db: Session, task: RoadmapTask, user_id: UUID) -> dict:
    progress = db.scalar(select(TaskProgress).where(TaskProgress.task_id == task.id, TaskProgress.user_id == user_id))
    resources = []
    if task.skill_id:
        resources = db.execute(select(Resource).join(SkillResource, SkillResource.resource_id == Resource.id).where(SkillResource.skill_id == task.skill_id).order_by(Resource.title)).scalars().all()
    return {"id": task.id, "title": task.title, "description": task.description, "skill_id": task.skill_id, "estimated_hours": task.estimated_hours, "order_index": task.order_index, "status": progress.status if progress else "not_started", "resources": [ResourceOut.model_validate(value).model_dump() for value in resources]}


def serialize_roadmap(db: Session, roadmap: Roadmap, user_id: UUID) -> dict:
    phases = db.scalars(select(RoadmapPhase).where(RoadmapPhase.roadmap_id == roadmap.id).order_by(RoadmapPhase.order_index)).all()
    serialized_phases = []
    for phase in phases:
        tasks = db.scalars(select(RoadmapTask).where(RoadmapTask.phase_id == phase.id).order_by(RoadmapTask.order_index)).all()
        milestones = db.scalars(select(Milestone).where(Milestone.roadmap_id == roadmap.id, Milestone.order_index == phase.order_index)).all()
        serialized_phases.append({
            "id": phase.id, "title": phase.title, "description": phase.description,
            "order_index": phase.order_index,
            "milestones": [{"id": milestone.id, "title": milestone.title, "description": milestone.description,
                            "task_ids": db.scalars(select(MilestoneTask.task_id).where(MilestoneTask.milestone_id == milestone.id)).all()}
                           for milestone in milestones],
            "tasks": [task_with_status(db, task, user_id) for task in tasks],
        })
    return {"id": roadmap.id, "career_id": roadmap.career_id, "title": roadmap.title, "summary": roadmap.summary, "status": roadmap.status, "generated_at": roadmap.generated_at, "generation_mode": getattr(roadmap, "generation_mode", None), "phases": serialized_phases}


@router.post("/roadmaps/generate")
def create_roadmap(payload: GenerateRoadmapIn, response: Response, user: CurrentUser, db: DbSession):
    career = db.get(Career, payload.career_id)
    if not career: raise api_error("NOT_FOUND", "Career not found", 404)
    try:
        roadmap = generate_roadmap(db, user.id, career, payload.weekly_hours or user.profile.weekly_hours)
        for previous in db.scalars(select(Roadmap).where(Roadmap.user_id == user.id, Roadmap.status == "active", Roadmap.id != roadmap.id)).all():
            previous.status = "superseded"
        db.commit()
    except Exception as exc:
        db.rollback()
        record_generation_failure(db, user.id)
        raise api_error("AI_GENERATION_FAILED", "Roadmap generation could not be completed safely", 503) from exc
    response.status_code = 201
    return ok(serialize_roadmap(db, roadmap, user.id))


@router.get("/roadmaps")
def list_roadmaps(user: CurrentUser, db: DbSession):
    values = db.scalars(
        select(Roadmap)
        .where(Roadmap.user_id == user.id)
        .order_by(case((Roadmap.status == "active", 0), else_=1), Roadmap.generated_at.desc())
    ).all()
    return ok([serialize_roadmap(db, value, user.id) for value in values])


def owned_roadmap(db: Session, roadmap_id: UUID, user_id: UUID) -> Roadmap:
    roadmap = db.scalar(select(Roadmap).where(Roadmap.id == roadmap_id, Roadmap.user_id == user_id))
    if not roadmap: raise api_error("NOT_FOUND", "Roadmap not found", 404)
    return roadmap


@router.get("/roadmaps/{roadmap_id}")
def get_roadmap(roadmap_id: UUID, user: CurrentUser, db: DbSession):
    return ok(serialize_roadmap(db, owned_roadmap(db, roadmap_id, user.id), user.id))


@router.patch("/roadmaps/{roadmap_id}")
def patch_roadmap(roadmap_id: UUID, payload: RoadmapPatchIn, user: CurrentUser, db: DbSession):
    roadmap = owned_roadmap(db, roadmap_id, user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(roadmap, field, value)
    db.commit()
    return ok(serialize_roadmap(db, roadmap, user.id))


@router.get("/roadmaps/{roadmap_id}/phases")
def roadmap_phases(roadmap_id: UUID, user: CurrentUser, db: DbSession):
    roadmap = owned_roadmap(db, roadmap_id, user.id)
    return ok(serialize_roadmap(db, roadmap, user.id)["phases"])


@router.get("/roadmaps/{roadmap_id}/tasks")
def roadmap_tasks(roadmap_id: UUID, user: CurrentUser, db: DbSession):
    roadmap = owned_roadmap(db, roadmap_id, user.id)
    tasks = db.execute(select(RoadmapTask).join(RoadmapPhase).where(RoadmapPhase.roadmap_id == roadmap.id).order_by(RoadmapPhase.order_index, RoadmapTask.order_index)).scalars().all()
    return ok([task_with_status(db, task, user.id) for task in tasks])


@router.post("/roadmaps/{roadmap_id}/reassess")
def reassess(roadmap_id: UUID, user: CurrentUser, db: DbSession):
    current = owned_roadmap(db, roadmap_id, user.id)
    try:
        replacement = generate_roadmap(db, user.id, db.get(Career, current.career_id), user.profile.weekly_hours)
        current.status = "superseded"; db.commit()
        return ok(serialize_roadmap(db, replacement, user.id))
    except Exception as exc:
        db.rollback()
        record_generation_failure(db, user.id)
        raise api_error("AI_GENERATION_FAILED", "Reassessment could not be completed safely", 503) from exc


@router.get("/tasks/{task_id}")
def get_task(task_id: UUID, user: CurrentUser, db: DbSession):
    task = db.get(RoadmapTask, task_id)
    if not task: raise api_error("NOT_FOUND", "Task not found", 404)
    roadmap = db.scalar(select(Roadmap).join(RoadmapPhase).where(RoadmapPhase.id == task.phase_id, Roadmap.user_id == user.id))
    if not roadmap: raise api_error("NOT_FOUND", "Task not found", 404)
    return ok(task_with_status(db, task, user.id))


@router.patch("/tasks/{task_id}")
def update_task(task_id: UUID, payload: TaskStatusIn, user: CurrentUser, db: DbSession):
    task = db.get(RoadmapTask, task_id)
    if not task: raise api_error("NOT_FOUND", "Task not found", 404)
    if not db.scalar(select(Roadmap).join(RoadmapPhase).where(RoadmapPhase.id == task.phase_id, Roadmap.user_id == user.id)): raise api_error("NOT_FOUND", "Task not found", 404)
    record = db.scalar(select(TaskProgress).where(TaskProgress.task_id == task.id, TaskProgress.user_id == user.id))
    if not record: record = TaskProgress(task_id=task.id, user_id=user.id); db.add(record)
    record.status = payload.status; record.completed_at = utcnow() if payload.status == "completed" else None
    db.commit()
    return ok(task_with_status(db, task, user.id))


@router.patch("/tasks/{task_id}/order")
def reorder_task(task_id: UUID, payload: TaskOrderIn, user: CurrentUser, db: DbSession):
    task = db.get(RoadmapTask, task_id)
    if not task or not db.scalar(select(Roadmap).join(RoadmapPhase).where(RoadmapPhase.id == task.phase_id, Roadmap.user_id == user.id)):
        raise api_error("NOT_FOUND", "Task not found", 404)
    siblings = db.scalars(select(RoadmapTask).where(RoadmapTask.phase_id == task.phase_id).order_by(RoadmapTask.order_index)).all()
    old_index = next(index for index, value in enumerate(siblings) if value.id == task.id)
    new_index = min(payload.order_index - 1, len(siblings) - 1)
    if old_index != new_index:
        moved = siblings.pop(old_index)
        siblings.insert(new_index, moved)
        # Move out of the unique range before assigning contiguous positions.
        offset = max(value.order_index for value in siblings) + len(siblings)
        for index, value in enumerate(siblings, start=1):
            value.order_index = offset + index
        db.flush()
        for index, value in enumerate(siblings, start=1):
            value.order_index = index
        db.commit()
    return ok(task_with_status(db, task, user.id))


@router.get("/roadmaps/{roadmap_id}/progress")
def progress(roadmap_id: UUID, user: CurrentUser, db: DbSession):
    roadmap = owned_roadmap(db, roadmap_id, user.id)
    task_ids = db.execute(select(RoadmapTask.id).join(RoadmapPhase).where(RoadmapPhase.roadmap_id == roadmap.id)).scalars().all()
    completed = db.scalar(select(func.count()).select_from(TaskProgress).where(TaskProgress.user_id == user.id, TaskProgress.task_id.in_(task_ids), TaskProgress.status == "completed")) or 0
    skipped = db.scalar(select(func.count()).select_from(TaskProgress).where(TaskProgress.user_id == user.id, TaskProgress.task_id.in_(task_ids), TaskProgress.status == "skipped")) or 0
    milestones = db.scalars(select(Milestone).where(Milestone.roadmap_id == roadmap.id).order_by(Milestone.order_index)).all()
    milestone_data = []
    for milestone in milestones:
        ids = db.scalars(select(MilestoneTask.task_id).where(MilestoneTask.milestone_id == milestone.id)).all()
        done = db.scalar(select(func.count()).select_from(TaskProgress).where(TaskProgress.user_id == user.id, TaskProgress.task_id.in_(ids), TaskProgress.status.in_(["completed", "skipped"]))) or 0
        milestone_data.append({"id": milestone.id, "title": milestone.title, "completed": done == len(ids), "progress": round(100 * done / len(ids), 1) if ids else 0})
    return ok({"completed_tasks": completed, "skipped_tasks": skipped, "total_tasks": len(task_ids), "completion_percentage": round(100 * (completed + skipped) / len(task_ids), 1) if task_ids else 0, "milestones": milestone_data})


@router.get("/projects")
def list_projects(db: DbSession, difficulty: int | None = None):
    query = select(Project).order_by(Project.name)
    if difficulty: query = query.where(Project.difficulty_level == difficulty)
    return ok([ProjectOut.model_validate(value).model_dump() for value in db.scalars(query).all()])


@router.get("/recommendations/projects")
def project_recommendations(career_id: UUID, user: CurrentUser, db: DbSession):
    if not db.get(Career, career_id): raise api_error("NOT_FOUND", "Career not found", 404)
    return ok([{**ProjectOut.model_validate(project).model_dump(), "score": score} for project, score in recommended_projects(db, user.id, career_id)])


@router.get("/resources")
def list_resources(db: DbSession):
    return ok([ResourceOut.model_validate(value).model_dump() for value in db.scalars(select(Resource).order_by(Resource.title)).all()])


@router.get("/dashboard")
def dashboard(user: CurrentUser, db: DbSession):
    roadmaps = db.scalars(select(Roadmap).where(Roadmap.user_id == user.id, Roadmap.status == "active").order_by(Roadmap.generated_at.desc())).all()
    roadmap = roadmaps[0] if roadmaps else None
    career = db.get(Career, user.profile.target_career_id) if user.profile.target_career_id else None
    report = None
    if career:
        try: report = gap_report(db, user.id, career.id)
        except (ValueError, PrerequisiteCycleError): pass
    projects = recommended_projects(db, user.id, career.id)[:3] if career and report else []
    progress_data = progress(roadmap.id, user, db)["data"] if roadmap else {"completed_tasks": 0, "total_tasks": 0, "completion_percentage": 0, "milestones": []}
    roadmap_data = serialize_roadmap(db, roadmap, user.id) if roadmap else None
    next_task = next((task for phase in roadmap_data["phases"] for task in phase["tasks"] if task["status"] not in {"completed", "skipped"}), None) if roadmap_data else None
    weekly_goal_hours = user.profile.weekly_hours
    week_ago = utcnow() - timedelta(days=7)
    weekly_completed_hours = 0
    remaining_hours = 0
    if roadmap:
        task_rows = db.execute(select(RoadmapTask, TaskProgress).join(RoadmapPhase).outerjoin(TaskProgress, (TaskProgress.task_id == RoadmapTask.id) & (TaskProgress.user_id == user.id)).where(RoadmapPhase.roadmap_id == roadmap.id)).all()
        weekly_completed_hours = sum(task.estimated_hours for task, state in task_rows if state and state.status == "completed" and state.updated_at and (state.updated_at.replace(tzinfo=week_ago.tzinfo) if state.updated_at.tzinfo is None else state.updated_at) >= week_ago)
        remaining_hours = sum(task.estimated_hours for task, state in task_rows if not state or state.status not in {"completed", "skipped"})
    estimated_weeks = (remaining_hours + weekly_goal_hours - 1) // weekly_goal_hours if remaining_hours else 0
    estimated_finish = (utcnow().date() + timedelta(days=estimated_weeks * 7)).isoformat() if remaining_hours else None
    setup_steps = {"career_selected": career is not None, "skills_added": bool(db.scalar(select(func.count()).select_from(UserSkill).where(UserSkill.user_id == user.id))), "roadmap_created": roadmap is not None}
    return ok({"target_career": CareerOut.model_validate(career).model_dump() if career else None, "roadmap": roadmap_data, "progress": progress_data, "key_skill_gaps": [item.model_dump() for item in report.items[:5]] if report else [], "next_task": next_task, "recommended_projects": [{**ProjectOut.model_validate(project).model_dump(), "score": score} for project, score in projects], "weekly_goal_hours": weekly_goal_hours, "weekly_completed_hours": weekly_completed_hours, "estimated_weeks_remaining": estimated_weeks, "estimated_finish_date": estimated_finish, "setup_steps": setup_steps})


# Admin data management. Role is never accepted from clients.
@router.post("/admin/skills")
def admin_create_skill(payload: SkillIn, response: Response, _: AdminUser, db: DbSession):
    value = Skill(**payload.model_dump()); db.add(value)
    try: db.commit()
    except IntegrityError: db.rollback(); raise api_error("CONFLICT", "Skill already exists", 409)
    response.status_code = 201; return ok(as_skill(value))


@router.post("/admin/careers")
def admin_create_career(payload: CareerIn, response: Response, _: AdminUser, db: DbSession):
    value = Career(**payload.model_dump()); db.add(value)
    try: db.commit()
    except IntegrityError: db.rollback(); raise api_error("CONFLICT", "Career already exists", 409)
    response.status_code = 201; return ok(CareerOut.model_validate(value).model_dump())


@router.put("/admin/careers/{career_id}/skills")
def admin_upsert_career_skill(career_id: UUID, payload: CareerSkillIn, _: AdminUser, db: DbSession):
    if not db.get(Career, career_id) or not db.get(Skill, payload.skill_id): raise api_error("NOT_FOUND", "Career or skill not found", 404)
    value = db.get(CareerSkill, {"career_id": career_id, "skill_id": payload.skill_id})
    if value:
        for key, val in payload.model_dump(exclude={"skill_id"}).items(): setattr(value, key, val)
    else: value = CareerSkill(career_id=career_id, **payload.model_dump()); db.add(value)
    db.commit(); return ok({"career_id": career_id, **payload.model_dump()})


@router.post("/admin/prerequisites")
def admin_add_prerequisite(payload: PrerequisiteIn, _: AdminUser, db: DbSession):
    if payload.skill_id == payload.prerequisite_skill_id: raise api_error("VALIDATION_ERROR", "A skill cannot depend on itself", 422)
    db.add(SkillPrerequisite(**payload.model_dump()))
    try:
        db.flush(); gap_nodes = [row[0] for row in db.execute(select(Skill.id)).all()]
        from app.services import prerequisite_order
        graph = {}
        for dep, pre in db.execute(select(SkillPrerequisite.skill_id, SkillPrerequisite.prerequisite_skill_id)).all(): graph.setdefault(dep, []).append(pre)
        prerequisite_order(gap_nodes, graph); db.commit()
    except (IntegrityError, PrerequisiteCycleError): db.rollback(); raise api_error("VALIDATION_ERROR", "Prerequisite is duplicate or creates a cycle", 422)
    return ok(payload.model_dump())


@router.post("/admin/projects")
def admin_create_project(payload: ProjectIn, response: Response, _: AdminUser, db: DbSession):
    value = Project(**payload.model_dump()); db.add(value); db.commit(); response.status_code = 201
    return ok(ProjectOut.model_validate(value).model_dump())


@router.post("/admin/resources")
def admin_create_resource(payload: ResourceIn, response: Response, _: AdminUser, db: DbSession):
    value = Resource(**payload.model_dump(mode="json")); db.add(value); db.commit(); response.status_code = 201
    return ok(ResourceOut.model_validate(value).model_dump())


@router.put("/admin/projects/{project_id}/skills")
def admin_upsert_project_skill(project_id: UUID, payload: ProjectSkillIn, _: AdminUser, db: DbSession):
    from app.models import ProjectSkill
    if not db.get(Project, project_id) or not db.get(Skill, payload.skill_id): raise api_error("NOT_FOUND", "Project or skill not found", 404)
    value = db.get(ProjectSkill, {"project_id": project_id, "skill_id": payload.skill_id})
    if value: value.importance = payload.importance
    else: db.add(ProjectSkill(project_id=project_id, **payload.model_dump()))
    db.commit()
    return ok({"project_id": project_id, **payload.model_dump()})


@router.put("/admin/careers/{career_id}/projects")
def admin_upsert_career_project(career_id: UUID, payload: CareerProjectIn, _: AdminUser, db: DbSession):
    from app.models import CareerProject
    if not db.get(Career, career_id) or not db.get(Project, payload.project_id): raise api_error("NOT_FOUND", "Career or project not found", 404)
    value = db.get(CareerProject, {"career_id": career_id, "project_id": payload.project_id})
    if value: value.relevance = payload.relevance
    else: db.add(CareerProject(career_id=career_id, **payload.model_dump()))
    db.commit()
    return ok({"career_id": career_id, **payload.model_dump()})
