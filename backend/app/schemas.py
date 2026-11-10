from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(char.islower() for char in value) or not any(char.isupper() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("Password must include uppercase, lowercase, and a number")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(APIModel):
    id: UUID
    email: EmailStr
    role: Literal["USER", "ADMIN"]
    is_active: bool


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    education: str | None = Field(default=None, max_length=200)
    experience_level: Literal["beginner", "student", "junior", "mid", "senior"] = "beginner"
    weekly_hours: int = Field(ge=1, le=80)
    bio: str | None = Field(default=None, max_length=2000)
    target_career_id: UUID | None = None


class ProfileOut(ProfileIn, APIModel):
    id: UUID
    user_id: UUID


class SkillIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    category: str = Field(default="General", max_length=80)


class SkillOut(SkillIn, APIModel):
    id: UUID


class UserSkillIn(BaseModel):
    skill_id: UUID
    proficiency_level: int = Field(ge=1, le=5)
    notes: str | None = Field(default=None, max_length=1000)


class UserSkillOut(UserSkillIn, APIModel):
    id: UUID
    skill: SkillOut | None = None


class CareerIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="Software Development", min_length=1, max_length=80)
    description: str = Field(default="", max_length=3000)
    difficulty_level: int = Field(default=3, ge=1, le=5)


class CareerOut(CareerIn, APIModel):
    id: UUID


class CareerSkillIn(BaseModel):
    skill_id: UUID
    required_level: int = Field(ge=1, le=5)
    importance: float = Field(ge=0.1, le=5)
    relevance: float = Field(ge=0.1, le=5)


class CareerSkillOut(CareerSkillIn, APIModel):
    career_id: UUID
    skill: SkillOut | None = None


class PrerequisiteIn(BaseModel):
    skill_id: UUID
    prerequisite_skill_id: UUID


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=3000)
    difficulty_level: int = Field(ge=1, le=5)
    estimated_hours: int = Field(gt=0, le=1000)


class ProjectOut(ProjectIn, APIModel):
    id: UUID
    score: float | None = None


class ResourceIn(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    url: HttpUrl
    resource_type: str = Field(min_length=1, max_length=50)
    description: str = Field(default="", max_length=2000)


class ResourceOut(ResourceIn, APIModel):
    id: UUID


class AssessmentIn(BaseModel):
    skills: list[UserSkillIn] = Field(min_length=1, max_length=100)


class GapItem(BaseModel):
    skill_id: UUID
    skill_name: str
    current_level: int
    required_level: int
    gap: int
    importance: float
    relevance: float
    priority: float
    prerequisites: list[UUID]


class GapReport(BaseModel):
    career_id: UUID
    items: list[GapItem]
    ordered_skill_ids: list[UUID]


class AITaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=3000)
    skill_id: UUID | None = None
    estimated_hours: int = Field(gt=0, le=200)
    order: int = Field(gt=0)


class AIPhaseIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=3000)
    order: int = Field(gt=0)
    milestone_title: str | None = Field(default=None, max_length=160)
    tasks: list[AITaskIn] = Field(min_length=1, max_length=15)


class AIRoadmapIn(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    summary: str = Field(min_length=1, max_length=5000)
    phases: list[AIPhaseIn] = Field(min_length=1, max_length=8)


class GenerateRoadmapIn(BaseModel):
    career_id: UUID
    weekly_hours: int | None = Field(default=None, ge=1, le=80)


class RoadmapPatchIn(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    status: Literal["active", "paused", "archived"] | None = None


class ProjectSkillIn(BaseModel):
    skill_id: UUID
    importance: float = Field(ge=0.1, le=5)


class CareerProjectIn(BaseModel):
    project_id: UUID
    relevance: float = Field(ge=0.1, le=5)


class TaskOut(APIModel):
    id: UUID
    title: str
    description: str
    skill_id: UUID | None
    estimated_hours: int
    order_index: int
    status: Literal["not_started", "in_progress", "completed", "skipped"] = "not_started"


class PhaseOut(APIModel):
    id: UUID
    title: str
    description: str
    order_index: int
    tasks: list[TaskOut]


class RoadmapOut(APIModel):
    id: UUID
    career_id: UUID
    title: str
    summary: str
    status: str
    generated_at: datetime
    phases: list[PhaseOut] = []


class TaskStatusIn(BaseModel):
    status: Literal["not_started", "in_progress", "completed", "skipped"]


class TaskOrderIn(BaseModel):
    order_index: int = Field(gt=0)


class ProgressOut(BaseModel):
    completed_tasks: int
    total_tasks: int
    completion_percentage: float
    milestones: list[dict]


class Envelope(BaseModel):
    success: bool = True
    data: object

