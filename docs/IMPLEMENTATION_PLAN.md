# AI Career Roadmap Generator — Development & Implementation Plan

## 1. Development Philosophy

Build incrementally. Each phase should leave the repository in a runnable and testable state.

Implementation loop:

`Inspect → Plan → Implement → Test → Fix → Review → Commit`

## 2. Phase 1 — Repository & Environment Setup

Deliver:
- Git repository
- Root structure
- `CLAUDE.md`
- Documentation
- `.gitignore`
- `.env.example`
- Python environment
- Node/Next.js environment
- Initial README

Checkpoint:
- Repository initializes cleanly.
- Backend/frontend can be started in their intended development environments.

## 3. Phase 2 — PostgreSQL Database

Deliver:
- PostgreSQL database
- SQLAlchemy configuration
- Models
- Alembic migrations
- Seed data
- Database tests

Checkpoint:
- Clean database can be migrated and seeded successfully.

## 4. Phase 3 — FastAPI Backend

Deliver:
- FastAPI application
- Configuration
- Database session management
- Base routing
- Error handling
- Pydantic schemas
- Service/repository structure
- Health endpoint

Checkpoint:
- API starts and connects to PostgreSQL.

## 5. Phase 4 — Authentication

Deliver:
- Registration
- Login
- Password hashing
- Token/session handling
- Current-user endpoint
- Protected routes
- Ownership checks

Checkpoint:
- Authenticated users can access protected resources safely.

## 6. Phase 5 — Skills & Careers

Deliver:
- Skill CRUD/services
- Career CRUD/services
- Career-skill mappings
- User-skill management
- Initial curated seed dataset

Checkpoint:
- User can maintain skills and inspect career requirements.

## 7. Phase 6 — Skill-Gap Engine

Deliver:
- Gap calculation
- Priority calculation
- Career compatibility
- Unit tests
- API endpoint

Checkpoint:
- Skill-gap output is deterministic and test-covered.

## 8. Phase 7 — Prerequisite Engine

Deliver:
- Dependency graph
- Traversal
- Topological ordering
- Cycle detection
- Tests for graph edge cases

Checkpoint:
- Roadmap ordering can respect prerequisites.

## 9. Phase 8 — AI Roadmap Generation

Deliver:
- AI provider abstraction
- Context builder
- Prompt templates
- Structured output schema
- Validator
- Retry/timeout handling
- AI generation logging
- Roadmap persistence

Checkpoint:
- Valid AI output becomes a relational roadmap.
- Invalid output is rejected safely.

## 10. Phase 9 — API Completion

Deliver:
- Complete REST contract
- Dashboard endpoint
- Project recommendations
- Progress endpoints
- Reassessment
- Admin endpoints where required
- OpenAPI verification

Checkpoint:
- Frontend has all required APIs.

## 11. Phase 10 — Next.js Frontend

Build in this order:
1. App shell/navigation
2. Authentication
3. Onboarding/profile
4. Skills
5. Career explorer
6. Skill-gap analysis
7. Roadmap generation
8. Roadmap overview
9. Task details/progress
10. Projects
11. Dashboard
12. Settings

Checkpoint:
- UI works against stable API contracts.

## 12. Phase 11 — Integration

Verify:

`Next.js → FastAPI → PostgreSQL`

and:

`FastAPI → AI Provider → Validation → PostgreSQL`

Test complete user journey.

## 13. Phase 12 — Testing

Run:
- Unit tests
- Integration tests
- API tests
- Frontend tests
- E2E
- Security checks
- Performance baseline
- Regression tests

Fix critical/high defects before deployment.

## 14. Phase 13 — Deployment

Deliver:
- Production database
- Backend deployment
- Frontend deployment
- Environment variables
- Secure secrets
- Database migrations
- Smoke tests
- Logging/monitoring appropriate to deployment platform

## 15. Suggested Repository

```text
AI-Career-Roadmap-Generator/
├── CLAUDE.md
├── README.md
├── .env.example
├── .gitignore
├── docs/
├── backend/
├── frontend/
├── database/
├── tests/
└── scripts/
```

## 16. Backend Structure

A reasonable starting structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── api/
│   ├── services/
│   └── ai/
├── migrations/
├── tests/
└── pyproject.toml
```

Adjust only when actual implementation needs justify it.

## 17. Frontend Structure

```text
frontend/
├── app/
├── components/
├── lib/
├── services/
├── hooks/
├── types/
└── tests/
```

## 18. Git Strategy

Prefer small commits at stable checkpoints.

Examples:
- `chore: initialize repository`
- `feat: add postgres models`
- `feat: add authentication`
- `feat: add career skill engine`
- `feat: add prerequisite engine`
- `feat: add AI roadmap generation`
- `test: add roadmap validation tests`

## 19. Scope Control

MVP first.

Do not delay the core system for:
- Resume parsing
- Job scraping
- GitHub analysis
- Interview simulation
- Complex analytics
- Unnecessary infrastructure

## 20. Final Demo Scenario

A successful demo should show:

1. Register.
2. Complete profile.
3. Add current skills.
4. Select a target career.
5. View skill gaps.
6. Explain priority/prerequisites.
7. Generate roadmap.
8. View phases and tasks.
9. Complete a task.
10. Show updated progress.

## 21. Completion Criteria

The implementation is complete when:
- MVP workflow works end-to-end.
- Core algorithms are tested.
- AI output is validated.
- Authentication and ownership are secure.
- APIs are documented.
- Frontend is integrated.
- Critical/high defects are resolved.
- Deployment smoke test passes.
