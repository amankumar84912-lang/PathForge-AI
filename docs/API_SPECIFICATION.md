# AI Career Roadmap Generator — API Specification

## 1. API Style

REST API using JSON.

Base path:

`/api/v1`

Authentication-protected endpoints require the configured authentication mechanism.

## 2. Standard Response

Success:

```json
{
  "success": true,
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": {}
  }
}
```

## 3. Authentication

### POST `/auth/register`
Create a user.

### POST `/auth/login`
Authenticate a user.

### POST `/auth/logout`
Invalidate/clear the current authentication state.

### GET `/auth/me`
Return the authenticated user.

## 4. Profile

### GET `/profile`
Get current user's profile.

### PUT `/profile`
Update current user's profile.

## 5. Skills

### GET `/skills`
List skills.

### GET `/skills/{skill_id}`
Get one skill.

### GET `/profile/skills`
Get current user's skills.

### POST `/profile/skills`
Add a skill with proficiency.

### PATCH `/profile/skills/{skill_id}`
Update proficiency.

### DELETE `/profile/skills/{skill_id}`
Remove a skill.

## 6. Careers

### GET `/careers`
List careers.

### GET `/careers/{career_id}`
Get career details.

### GET `/careers/{career_id}/skills`
Get required career skills.

## 7. Assessment

### POST `/assessments`
Submit/update a skill assessment.

Request example:

```json
{
  "skills": [
    {
      "skill_id": "uuid",
      "proficiency_level": 3
    }
  ]
}
```

## 8. Skill Gap

### GET `/careers/{career_id}/skill-gap`
Calculate the authenticated user's skill gap for a career.

Response should include:
- skill
- current level
- required level
- gap
- importance
- relevance
- priority

## 9. Career Recommendations

### POST `/recommendations/careers`
Return careers ranked by compatibility.

## 10. Roadmaps

### GET `/roadmaps`
List the user's roadmaps.

### POST `/roadmaps/generate`
Generate a roadmap for a target career.

Request should identify the target career and relevant personalization settings.

### GET `/roadmaps/{roadmap_id}`
Get a roadmap.

### PATCH `/roadmaps/{roadmap_id}`
Update allowed roadmap metadata/status (`title`, `active`, `paused`, or `archived`). Only the owner may update it.

### GET `/roadmaps/{roadmap_id}/phases`
Get phases.

### GET `/roadmaps/{roadmap_id}/tasks`
Get tasks.

### POST `/roadmaps/{roadmap_id}/reassess`
Recalculate and, where appropriate, regenerate/adapt the roadmap.

## 11. Tasks

### GET `/tasks/{task_id}`
Get task details.

### PATCH `/tasks/{task_id}`
Update task progress/status.

## 12. Progress

### GET `/roadmaps/{roadmap_id}/progress`
Return:
- completed tasks
- total tasks
- completion percentage
- milestone status

## 13. Projects

### GET `/projects`
List projects with optional filters.

### GET `/recommendations/projects`
Recommend projects based on career and skill gaps.

## 14. Resources

### GET `/resources`
List learning resources.

## 15. AI

### POST `/ai/chat`
Phase 2 conversational career assistant.

The endpoint must not bypass authorization or structured career rules.

## 16. Dashboard

### GET `/dashboard`
Return dashboard summary:
- target career
- key skill gaps
- roadmap
- progress
- recommended projects
- recent activity

## 17. Admin

Admin-only endpoints should support:
- Careers CRUD
- Skills CRUD
- Career-skill mappings
- Prerequisites
- Projects
- Resources

Admin access must be authorized server-side.

Implemented management routes are under `/admin`: create skills and careers, upsert career-skill requirements, add cycle-checked prerequisites, create projects/resources, and upsert project-skill and career-project mappings. Public read routes expose the curated catalog. Administrative routes derive role from the authenticated user and never accept a client-supplied role.

## 18. Current route coverage

Implemented routes cover registration/login/refresh/logout/current user; profile and skill assessment; skill and career catalogs; career requirements/gap/recommendations; roadmap generation/list/detail/metadata/phases/tasks/reassessment/progress; task lookup/status; project and resource catalogs; project recommendations; dashboard; and protected admin catalog/mapping actions. `/ai/chat` remains a documented Phase 2 endpoint and is not implemented in the MVP.

## 19. Status Codes

Use:
- `200` successful read/update
- `201` successful creation
- `204` successful deletion where appropriate
- `400` malformed request
- `401` unauthenticated
- `403` unauthorized
- `404` resource not found
- `409` conflict
- `422` validation error
- `429` rate limited
- `500` unexpected server error
- `502/503` external AI/provider failure where appropriate

## 20. Validation

Validate:
- UUIDs
- enum/status values
- proficiency 1–5
- required fields
- ownership
- pagination/filter parameters
- AI request constraints

## 21. Security

- Never trust user IDs supplied by clients for ownership.
- Derive authenticated identity from the auth context.
- Do not expose secrets.
- Do not expose stack traces.
- Rate-limit expensive AI endpoints.
- Validate AI output before persistence.

## 22. API Development Rules

- Keep business logic in services.
- Keep route handlers thin.
- Use Pydantic schemas.
- Use dependency injection for database/auth services.
- Maintain `/api/v1`.
- Generate and verify OpenAPI documentation.

## 23. Testing

Every endpoint should have:
- Happy-path test
- Validation test
- Authentication test where applicable
- Authorization/ownership test where applicable
- Error-response test

AI endpoints additionally require provider failure and malformed-output tests.
