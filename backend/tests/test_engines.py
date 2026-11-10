import json
from uuid import uuid4

import httpx
import pytest

from app.database import normalize_database_url
from app.models import Career, CareerSkill, Skill, User, UserSkill
from app.schemas import AIRoadmapIn
from app.services import (
    GeminiProvider,
    GeminiProviderError,
    PrerequisiteCycleError,
    gap_report,
    prerequisite_order,
    validate_generated_roadmap,
)


def test_provider_postgres_urls_use_psycopg3_without_changing_credentials():
    assert normalize_database_url("postgresql://user:p%25ss@db.example/pathforge") == "postgresql+psycopg://user:p%25ss@db.example/pathforge"
    assert normalize_database_url("postgres://user:pass@db.example/pathforge") == "postgresql+psycopg://user:pass@db.example/pathforge"
    assert normalize_database_url("sqlite:///./pathforge.db") == "sqlite:///./pathforge.db"


def test_prerequisites_are_ordered_before_dependents():
    foundation, advanced, independent = uuid4(), uuid4(), uuid4()
    result = prerequisite_order([advanced, independent, foundation], {advanced: [foundation]})
    assert result.index(foundation) < result.index(advanced)
    assert set(result) == {foundation, advanced, independent}

def test_prerequisite_cycle_is_rejected():
    first, second = uuid4(), uuid4()
    with pytest.raises(PrerequisiteCycleError):
        prerequisite_order([first, second], {first: [second], second: [first]})


def test_gap_priority_uses_required_current_importance_and_relevance(db):
    user = User(email="gap@example.com", password_hash="not-used")
    python = Skill(name="Python", description="", category="Programming")
    sql = Skill(name="SQL", description="", category="Data")
    career = Career(name="Data Engineer", description="", difficulty_level=3)
    db.add_all([user, python, sql, career])
    db.flush()
    db.add_all([
        CareerSkill(career_id=career.id, skill_id=python.id, required_level=4, importance=2, relevance=1.5),
        CareerSkill(career_id=career.id, skill_id=sql.id, required_level=2, importance=1, relevance=1),
        UserSkill(user_id=user.id, skill_id=python.id, proficiency_level=2),
    ])
    db.commit()

    report = gap_report(db, user.id, career.id)
    by_name = {item.skill_name: item for item in report.items}
    assert by_name["Python"].gap == 2
    assert by_name["Python"].priority == 6
    assert by_name["SQL"].current_level == 0
    assert by_name["SQL"].priority == 2


def test_generated_roadmap_rejects_unknown_skill_id():
    unsupported = uuid4()
    roadmap = AIRoadmapIn.model_validate({
        "title": "Plan", "summary": "Summary", "phases": [{
            "title": "Phase", "description": "Description", "order": 1,
            "tasks": [{"title": "Task", "description": "Learn it", "skill_id": str(unsupported), "estimated_hours": 2, "order": 1}],
        }],
    })
    with pytest.raises(ValueError, match="unsupported skill"):
        validate_generated_roadmap(roadmap, set())


def test_generated_roadmap_requires_every_priority_skill():
    required, omitted = uuid4(), uuid4()
    roadmap = AIRoadmapIn.model_validate({
        "title": "Plan", "summary": "Summary", "phases": [{
            "title": "Phase", "description": "Description", "order": 1,
            "tasks": [{"title": "Task", "description": "Learn it", "skill_id": str(required), "estimated_hours": 2, "order": 1}],
        }],
    })
    with pytest.raises(ValueError, match="omitted one or more priority"):
        validate_generated_roadmap(roadmap, {required, omitted}, {required, omitted})


def test_gemini_provider_sends_structured_request_and_parses_roadmap(monkeypatch):
    from app import services

    skill_id = uuid4()
    captured = {}
    payload = {
        "title": "A learning plan", "summary": "A focused summary.", "phases": [{
            "title": "Foundations", "description": "Build the basics.", "order": 1,
            "milestone_title": "First project", "tasks": [{
                "title": "Practice Python", "description": "Write a small script.",
                "skill_id": str(skill_id), "estimated_hours": 3, "order": 1,
            }],
        }],
    }
    response = httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]}, request=httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"))

    def fake_post(url, *, headers, json, timeout):
        captured.update(url=url, headers=headers, payload=json, timeout=timeout)
        return response

    monkeypatch.setattr(services.httpx, "post", fake_post)
    monkeypatch.setattr(services.settings, "gemini_api_key", "test-gemini-key")
    monkeypatch.setattr(services.settings, "gemini_model", "gemini-3.5-flash-lite")

    generated = GeminiProvider().generate({"career_name": "Backend Developer", "weekly_hours": 6, "gaps": []})

    assert captured["headers"]["x-goog-api-key"] == "test-gemini-key"
    assert captured["payload"]["generationConfig"]["responseMimeType"] == "application/json"
    assert generated.phases[0].tasks[0].skill_id == skill_id


def test_gemini_provider_converts_unassigned_skill_to_none(monkeypatch):
    from app import services

    request = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent")
    payload = {"title": "Portfolio plan", "summary": "Show your existing skills.", "phases": [{
        "title": "Portfolio", "description": "Build evidence.", "order": 1, "milestone_title": "Portfolio ready",
        "tasks": [{"title": "Publish your work", "description": "Write a project case study.", "skill_id": "", "estimated_hours": 4, "order": 1}],
    }]}
    response = httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]}, request=request)
    monkeypatch.setattr(services.httpx, "post", lambda *args, **kwargs: response)
    monkeypatch.setattr(services.settings, "gemini_api_key", "test-gemini-key")
    generated = GeminiProvider().generate({})
    assert generated.phases[0].tasks[0].skill_id is None


def test_gemini_provider_sanitizes_http_failures(monkeypatch):
    from app import services

    request = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/test:generateContent")
    response = httpx.Response(401, request=request)
    monkeypatch.setattr(services.httpx, "post", lambda *args, **kwargs: response)
    monkeypatch.setattr(services.settings, "gemini_api_key", "test-gemini-key")
    with pytest.raises(GeminiProviderError, match="HTTP 401"):
        GeminiProvider().generate({})

