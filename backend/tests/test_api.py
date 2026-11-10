
import pytest

from app.models import AIGenerationLog, Career, CareerSkill, Resource, Skill, SkillResource

PASSWORD = "SecurePass123"

def auth(client, email="student@example.com"):
    response = client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD, "full_name": "Student"})
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

def seeded_career(db):
    python = Skill(name="Python", description="", category="Programming")
    api = Skill(name="FastAPI", description="", category="Backend")
    career = Career(name="Backend Developer", description="", difficulty_level=3)
    db.add_all([python, api, career]); db.flush()
    db.add_all([CareerSkill(career_id=career.id, skill_id=python.id, required_level=4, importance=1.5, relevance=1.5), CareerSkill(career_id=career.id, skill_id=api.id, required_level=3, importance=1.5, relevance=1.5)])
    db.commit()
    return career, python, api

def test_end_to_end_assessment_roadmap_and_progress(client, db):
    headers = auth(client)
    career, python, _ = seeded_career(db)
    profile = client.get("/api/v1/profile", headers=headers).json()["data"]
    response = client.put("/api/v1/profile", headers=headers, json={**profile, "target_career_id": str(career.id), "weekly_hours": 8})
    assert response.status_code == 200
    response = client.post("/api/v1/assessments", headers=headers, json={"skills": [{"skill_id": str(python.id), "proficiency_level": 2}]})
    assert response.status_code == 200
    gap = client.get(f"/api/v1/careers/{career.id}/skill-gap", headers=headers)
    assert gap.status_code == 200
    gaps = gap.json()["data"]["items"]
    assert next(item for item in gaps if item["skill_id"] == str(python.id))["gap"] == 2
    generated = client.post("/api/v1/roadmaps/generate", headers=headers, json={"career_id": str(career.id), "weekly_hours": 8})
    assert generated.status_code == 201, generated.text
    roadmap = generated.json()["data"]
    assert roadmap["generation_mode"] == "deterministic-local"
    resource = Resource(title="Python quickstart", url="https://docs.python.org/3/tutorial/", resource_type="documentation", description="Official Python guide")
    db.add(resource); db.flush(); db.add(SkillResource(skill_id=python.id, resource_id=resource.id)); db.commit()
    roadmap = client.get(f"/api/v1/roadmaps/{roadmap['id']}", headers=headers).json()["data"]
    python_tasks = [task for phase in roadmap["phases"] for task in phase["tasks"] if task["skill_id"] == str(python.id)]
    assert python_tasks[0]["resources"][0]["title"] == "Python quickstart"
    if len(roadmap["phases"][0]["tasks"]) > 1:
        first_phase = roadmap["phases"][0]
        first = first_phase["tasks"][0]
        reordered = client.patch(f"/api/v1/tasks/{first['id']}/order", headers=headers, json={"order_index": 2})
        assert reordered.status_code == 200
        moved = client.get(f"/api/v1/roadmaps/{roadmap['id']}", headers=headers).json()["data"]["phases"][0]["tasks"]
        assert moved[1]["id"] == first["id"]
    task = roadmap["phases"][0]["tasks"][0]
    updated = client.patch(f"/api/v1/tasks/{task['id']}", headers=headers, json={"status":"completed"})
    assert updated.status_code == 200
    progress = client.get(f"/api/v1/roadmaps/{roadmap['id']}/progress", headers=headers)
    assert progress.json()["data"]["completed_tasks"] == 1


def test_skipped_tasks_count_toward_plan_completion_but_not_completed_count(client, db):
    headers = auth(client)
    career, _, _ = seeded_career(db)
    generated = client.post("/api/v1/roadmaps/generate", headers=headers, json={"career_id": str(career.id)})
    roadmap = generated.json()["data"]
    task = roadmap["phases"][0]["tasks"][0]
    skipped = client.patch(f"/api/v1/tasks/{task['id']}", headers=headers, json={"status": "skipped"})
    assert skipped.status_code == 200
    progress = client.get(f"/api/v1/roadmaps/{roadmap['id']}/progress", headers=headers).json()["data"]
    assert progress["completed_tasks"] == 0
    assert progress["skipped_tasks"] == 1
    assert progress["completion_percentage"] > 0


def test_ai_provider_outage_falls_back_to_local_planner(client, db, monkeypatch):
    headers = auth(client)
    career, _, _ = seeded_career(db)

    class OfflineGemini:
        name = "gemini"
        model = "configured-model"
        def generate(self, context):
            from app.services import GeminiProviderError
            raise GeminiProviderError("Gemini API request failed")

    from app import services
    monkeypatch.setattr(services, "provider", lambda: OfflineGemini())
    response = client.post("/api/v1/roadmaps/generate", headers=headers, json={"career_id": str(career.id)})
    assert response.status_code == 201
    assert response.json()["data"]["generation_mode"] == "deterministic-local"
    log = db.query(AIGenerationLog).order_by(AIGenerationLog.created_at.desc()).first()
    assert log.provider == "deterministic-local"
    assert "Gemini unavailable" in log.error_message


def test_ai_response_that_omits_priority_gaps_falls_back_to_local_planner(client, db, monkeypatch):
    headers = auth(client)
    career, python, _ = seeded_career(db)

    class IncompleteGemini:
        name = "gemini"
        model = "configured-model"
        def generate(self, context):
            from app.schemas import AIRoadmapIn
            return AIRoadmapIn.model_validate({
                "title": "Incomplete plan",
                "summary": "This plan intentionally omits a priority skill.",
                "phases": [{
                    "title": "Python", "description": "Build Python foundations.", "order": 1,
                    "milestone_title": "Python foundations shown",
                    "tasks": [{"title": "Practice Python", "description": "Write a small script.", "skill_id": str(python.id), "estimated_hours": 3, "order": 1}],
                }],
            })

    from app import services
    monkeypatch.setattr(services, "provider", lambda: IncompleteGemini())
    response = client.post("/api/v1/roadmaps/generate", headers=headers, json={"career_id": str(career.id)})

    assert response.status_code == 201, response.text
    assert response.json()["data"]["generation_mode"] == "deterministic-local"
    log = db.query(AIGenerationLog).order_by(AIGenerationLog.created_at.desc()).first()
    assert log.provider == "deterministic-local"
    assert "failed validation" in log.error_message


def test_career_search_includes_goal_categories(client, db):
    _, _, _ = seeded_career(db)
    from app.models import Career
    db.add(Career(name="Data Analyst", category="Data & AI", description="Analyze business data.", difficulty_level=2))
    db.commit()

    response = client.get("/api/v1/careers?q=Data")

    assert response.status_code == 200
    assert [career["name"] for career in response.json()["data"]] == ["Data Analyst"]
    assert response.json()["data"][0]["category"] == "Data & AI"

def test_user_cannot_access_another_users_roadmap(client, db):
    headers = auth(client, "one@example.com")
    career, _, _ = seeded_career(db)
    generated = client.post("/api/v1/roadmaps/generate", headers=headers, json={"career_id": str(career.id)})
    roadmap_id = generated.json()["data"]["id"]
    other_headers = auth(client, "two@example.com")
    response = client.get(f"/api/v1/roadmaps/{roadmap_id}", headers=other_headers)
    assert response.status_code == 404

def test_registration_rejects_weak_password(client):
    response = client.post("/api/v1/auth/register", json={"email":"bad@example.com", "password":"lowercaseonly", "full_name":"Bad"})
    assert response.status_code == 422


def test_refresh_token_rotation_and_reuse_revocation(client):
    auth(client)
    original = client.cookies.get("refresh_token")
    assert original

    rotated = client.post("/api/v1/auth/refresh")
    assert rotated.status_code == 200
    assert client.cookies.get("refresh_token") != original

    client.cookies.set("refresh_token", original, path="/api/v1/auth")
    replay = client.post("/api/v1/auth/refresh")
    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "TOKEN_REUSE"


def test_regular_user_cannot_use_admin_routes(client):
    headers = auth(client)
    response = client.post("/api/v1/admin/skills", headers=headers, json={"name":"Root access", "category":"General"})
    assert response.status_code == 403


def test_localhost_alias_can_reach_api_but_untrusted_origin_is_rejected(client):
    from app.core import settings

    loopback_origin = next(
        (origin for origin in settings.allowed_frontend_origins if origin == "http://127.0.0.1:3000"),
        None,
    )
    if loopback_origin is None:
        pytest.skip("Configured frontend origin is not the local development hostname")

    preflight = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": loopback_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == loopback_origin

    rejected = client.post("/api/v1/auth/refresh", headers={"Origin": "https://untrusted.example"})
    assert rejected.status_code == 403
    assert rejected.json()["error"]["code"] == "CSRF_REJECTED"
