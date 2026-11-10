# AI Career Roadmap Generator — Testing & QA Specification

## 1. Testing Objective

Verify that the system is functionally correct, secure, reliable, explainable, and robust against invalid inputs and AI failures.

## 2. Testing Levels

1. Unit testing
2. Integration testing
3. API testing
4. Frontend/component testing
5. System testing
6. End-to-end testing
7. Security testing
8. Performance testing
9. Regression testing
10. User acceptance testing

## 3. Authentication Tests

- Register valid user.
- Reject duplicate email.
- Reject invalid email.
- Reject weak/invalid password according to policy.
- Login with valid credentials.
- Reject invalid credentials.
- Access protected endpoint without auth.
- Access another user's resource.
- Logout behavior.

## 4. Profile Tests

- Create/read/update profile.
- Validate required fields.
- Validate weekly hours.
- Verify user isolation.

## 5. Skill Tests

- List skills.
- Add skill.
- Update proficiency.
- Delete skill.
- Reject proficiency below 1 or above 5.
- Reject invalid skill ID.
- Prevent duplicate user-skill records.

## 6. Skill-Gap Tests

Test:
- No current skills.
- Complete match.
- Partial match.
- Missing skills.
- Required > current.
- Required = current.
- Current > required.
- Multiple required skills.
- Missing/invalid mappings.

Verify deterministic formula:
`Gap = Required - Current`

## 7. Priority Tests

Verify:
- Higher gap increases priority.
- Higher importance increases priority.
- Higher relevance increases priority.
- Equal inputs produce deterministic results.
- Invalid values are rejected.

## 8. Prerequisite Tests

Test:
- Simple chain.
- Multiple prerequisites.
- Independent skills.
- Missing node.
- Duplicate edge.
- Circular dependency.
- Deep dependency chain.

The engine must terminate safely on cycles.

## 9. AI Roadmap Tests

Verify:
- Valid AI response produces roadmap.
- Malformed JSON is rejected.
- Invalid skill ID is rejected.
- Unsupported skill is rejected.
- Missing phase/task is rejected.
- Negative/invalid hours are rejected.
- Provider timeout is handled.
- Provider failure is handled.
- Retry limit is respected.
- Invalid output is never persisted.

## 10. AI Security Tests

Test prompt injection through:
- Profile text
- Notes
- User preferences
- Chat messages
- Imported content

Verify user content cannot override system constraints.

## 11. Roadmap Tests

- Create roadmap.
- Retrieve roadmap.
- Retrieve only owned roadmap.
- Retrieve phases.
- Retrieve tasks.
- Update allowed metadata.
- Reassess roadmap.

## 12. Progress Tests

- Mark task complete.
- Mark task incomplete.
- Calculate completion percentage.
- Verify completed/total counts.
- Verify milestone status.
- Prevent unauthorized updates.

## 13. Project Recommendation Tests

- Match projects to missing skills.
- Verify career relevance.
- Verify level compatibility.
- Handle no matching projects.

## 14. API Tests

Verify:
- Correct status codes.
- Validation responses.
- Auth requirements.
- Ownership.
- Error format.
- Rate limiting on expensive operations.

## 15. Database Tests

Verify:
- PK/FK constraints.
- Unique constraints.
- Check constraints.
- Migration from clean database.
- Seed data integrity.
- Transaction rollback.
- Index presence for important queries.

## 16. Frontend Tests

Test:
- Navigation.
- Form validation.
- API loading/error states.
- Protected routes.
- Skill editing.
- Career selection.
- Skill-gap visualization.
- Roadmap rendering.
- Task completion.
- Dashboard data.

## 17. End-to-End Scenario

```text
Register
  ↓
Login
  ↓
Complete profile
  ↓
Add skills
  ↓
Select career
  ↓
Calculate skill gap
  ↓
Generate roadmap
  ↓
View phases/tasks
  ↓
Complete task
  ↓
Verify progress
  ↓
Reassess
```

## 18. Security Testing

Check:
- Authentication bypass
- Authorization bypass
- IDOR/resource ownership
- SQL injection protection
- XSS protection
- CSRF considerations
- Secret exposure
- Excessive error information
- Rate limiting
- Prompt injection

## 19. Performance Testing

Measure:
- Normal API latency
- Database query performance
- Concurrent normal users
- AI request latency
- Timeout behavior

Do not optimize prematurely; first establish baseline measurements.

## 20. Defect Severity

### Critical
Security failure, data corruption, authentication bypass.

### High
Core feature unusable or incorrect roadmap generation.

### Medium
Feature works with significant limitation.

### Low
Minor UI/documentation issue.

## 21. AI Quality Evaluation

Use:
- Career relevance — 20%
- Skill-gap coverage — 20%
- Prerequisite correctness — 20%
- Personalization — 15%
- Project relevance — 10%
- Actionability — 10%
- Output validity — 5%

## 22. Definition of Done

A feature is done when:
- Code implemented.
- Relevant tests added.
- Tests pass.
- Validation exists.
- Security considered.
- Documentation updated if needed.
- No critical regression remains.

## 23. Recommended Tooling

Backend:
- pytest
- FastAPI test client
- Ruff
- mypy where appropriate

Frontend:
- TypeScript checks
- ESLint
- React/Next.js testing tools
- Playwright for E2E where appropriate

API:
- OpenAPI-generated documentation
- Postman/Insomnia or equivalent

## 24. Continuous Testing Workflow

For each feature:

`Implement → Unit Test → Integration Test → Lint/Type Check → Review → Commit`

Do not postpone all testing until the end.
