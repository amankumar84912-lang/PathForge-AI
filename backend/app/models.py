from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import utcnow
from app.database import Base


def pk():
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class User(Base, Timestamped):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = pk()
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="USER")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile: Mapped[Profile | None] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True)
    token_digest: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_jti: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Profile(Base, Timestamped):
    __tablename__ = "profiles"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), default="")
    education: Mapped[str | None] = mapped_column(String(200))
    experience_level: Mapped[str] = mapped_column(String(32), default="beginner")
    weekly_hours: Mapped[int] = mapped_column(Integer, default=6)
    bio: Mapped[str | None] = mapped_column(Text)
    target_career_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("careers.id"), nullable=True)
    user: Mapped[User] = relationship(back_populates="profile")
    __table_args__ = (CheckConstraint("weekly_hours >= 1 AND weekly_hours <= 80", name="ck_profile_weekly_hours"),)


class Skill(Base, Timestamped):
    __tablename__ = "skills"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(80), default="General")


class Career(Base, Timestamped):
    __tablename__ = "careers"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(120), unique=True)
    category: Mapped[str] = mapped_column(String(80), default="Software Development", server_default="Software Development")
    description: Mapped[str] = mapped_column(Text, default="")
    difficulty_level: Mapped[int] = mapped_column(Integer, default=3)
    __table_args__ = (CheckConstraint("difficulty_level BETWEEN 1 AND 5", name="ck_career_difficulty"),)


class CareerSkill(Base):
    __tablename__ = "career_skills"
    career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    required_level: Mapped[int] = mapped_column(Integer)
    importance: Mapped[float] = mapped_column(Float, default=1)
    relevance: Mapped[float] = mapped_column(Float, default=1)
    __table_args__ = (CheckConstraint("required_level BETWEEN 1 AND 5", name="ck_career_skill_level"), Index("ix_career_skills_skill", "skill_id"))


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    prerequisite_skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    __table_args__ = (CheckConstraint("skill_id <> prerequisite_skill_id", name="ck_no_self_prerequisite"), Index("ix_prerequisite_skill", "prerequisite_skill_id"))


class UserSkill(Base, Timestamped):
    __tablename__ = "user_skills"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    proficiency_level: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("user_id", "skill_id"), CheckConstraint("proficiency_level BETWEEN 1 AND 5", name="ck_user_skill_level"))


class Project(Base, Timestamped):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = pk()
    name: Mapped[str] = mapped_column(String(160), unique=True)
    description: Mapped[str] = mapped_column(Text)
    difficulty_level: Mapped[int] = mapped_column(Integer)
    estimated_hours: Mapped[int] = mapped_column(Integer)
    __table_args__ = (CheckConstraint("difficulty_level BETWEEN 1 AND 5", name="ck_project_difficulty"), CheckConstraint("estimated_hours > 0", name="ck_project_hours"))


class ProjectSkill(Base):
    __tablename__ = "project_skills"
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    importance: Mapped[float] = mapped_column(Float, default=1)


class CareerProject(Base):
    __tablename__ = "career_projects"
    career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    relevance: Mapped[float] = mapped_column(Float, default=1)


class Roadmap(Base, Timestamped):
    __tablename__ = "roadmaps"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("careers.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    summary: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="active")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    phases: Mapped[list[RoadmapPhase]] = relationship(back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapPhase.order_index")
    milestones: Mapped[list[Milestone]] = relationship(back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapPhase(Base):
    __tablename__ = "roadmap_phases"
    id: Mapped[uuid.UUID] = pk()
    roadmap_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer)
    roadmap: Mapped[Roadmap] = relationship(back_populates="phases")
    tasks: Mapped[list[RoadmapTask]] = relationship(back_populates="phase", cascade="all, delete-orphan", order_by="RoadmapTask.order_index")
    __table_args__ = (UniqueConstraint("roadmap_id", "order_index"), CheckConstraint("order_index > 0", name="ck_phase_order"))


class RoadmapTask(Base, Timestamped):
    __tablename__ = "roadmap_tasks"
    id: Mapped[uuid.UUID] = pk()
    phase_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmap_phases.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    skill_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    estimated_hours: Mapped[int] = mapped_column(Integer)
    order_index: Mapped[int] = mapped_column(Integer)
    phase: Mapped[RoadmapPhase] = relationship(back_populates="tasks")
    __table_args__ = (UniqueConstraint("phase_id", "order_index"), CheckConstraint("estimated_hours > 0", name="ck_task_hours"), CheckConstraint("order_index > 0", name="ck_task_order"))


class Milestone(Base):
    __tablename__ = "milestones"
    id: Mapped[uuid.UUID] = pk()
    roadmap_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    order_index: Mapped[int] = mapped_column(Integer)
    roadmap: Mapped[Roadmap] = relationship(back_populates="milestones")
    __table_args__ = (UniqueConstraint("roadmap_id", "order_index"),)


class MilestoneTask(Base):
    __tablename__ = "milestone_tasks"
    milestone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("milestones.id", ondelete="CASCADE"), primary_key=True)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmap_tasks.id", ondelete="CASCADE"), primary_key=True)


class TaskProgress(Base, Timestamped):
    __tablename__ = "task_progress"
    id: Mapped[uuid.UUID] = pk()
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmap_tasks.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="not_started")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("task_id", "user_id"), CheckConstraint("status IN ('not_started','in_progress','completed','skipped')", name="ck_task_status"))


class Resource(Base, Timestamped):
    __tablename__ = "resources"
    id: Mapped[uuid.UUID] = pk()
    title: Mapped[str] = mapped_column(String(180))
    url: Mapped[str] = mapped_column(String(2048))
    resource_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text, default="")


class SkillResource(Base):
    __tablename__ = "skill_resources"
    skill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)


class CareerResource(Base):
    __tablename__ = "career_resources"
    career_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("careers.id", ondelete="CASCADE"), primary_key=True)
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)


class AIGenerationLog(Base):
    __tablename__ = "ai_generation_logs"
    id: Mapped[uuid.UUID] = pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    roadmap_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("roadmaps.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(120))
    prompt_version: Mapped[str] = mapped_column(String(30), default="v1")
    status: Mapped[str] = mapped_column(String(30))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    validation_result: Mapped[str] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
