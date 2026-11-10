# AI Career Roadmap Generator — Software Requirements Specification

## 1. Purpose

The AI Career Roadmap Generator is a web application that helps students and early-career users identify career-related skill gaps and receive a personalized, dependency-aware learning roadmap.

The system combines structured career/skill data, deterministic analysis, prerequisite ordering, project recommendations, progress tracking, and LLM-based personalization.

## 2. Problem Statement

Users often know a desired career but lack a reliable answer to:
- What skills are required?
- Which skills do I already have?
- What am I missing?
- Which missing skills should I learn first?
- Which projects can demonstrate those skills?
- How should the learning sequence be adapted to my available time and progress?

Generic online roadmaps are usually not personalized to the learner's current proficiency.

## 3. Objectives

1. Store structured career and skill requirements.
2. Maintain user skill profiles and proficiency levels.
3. Calculate skill gaps deterministically.
4. Resolve prerequisite dependencies.
5. Recommend compatible careers and projects.
6. Generate personalized learning roadmaps using an LLM.
7. Validate AI output before persistence.
8. Track roadmap task completion and progress.
9. Adapt roadmap recommendations after reassessment.
10. Provide a usable dashboard for monitoring progress.

## 4. Scope

### MVP
- Registration and authentication
- User profile
- Skill management
- Skill assessment
- Career explorer
- Career selection
- Skill-gap analysis
- Skill priority calculation
- Prerequisite ordering
- AI roadmap generation
- Roadmap phases/tasks
- Task completion
- Progress tracking
- Dashboard
- Project recommendations

### Future
- Resume analysis
- GitHub analysis
- Job-market analysis
- Job matching
- AI career assistant
- AI mock interviews
- Advanced recommendations

## 5. Users

### Student/User
Can manage a profile, skills, career goal, roadmap, tasks, and progress.

### Administrator
Can manage structured careers, skills, mappings, projects, and resources.

## 6. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | User can register with valid credentials. |
| FR-02 | User can log in and log out securely. |
| FR-03 | User can view/update their profile. |
| FR-04 | User can browse available skills. |
| FR-05 | User can add, update, and remove personal skills. |
| FR-06 | User can provide a 1–5 proficiency level for skills. |
| FR-07 | User can browse available careers. |
| FR-08 | User can view career-required skills. |
| FR-09 | User can select a target career. |
| FR-10 | System calculates required vs current skill gaps. |
| FR-11 | System calculates skill priority using documented weights. |
| FR-12 | System resolves prerequisite relationships. |
| FR-13 | System can recommend compatible careers. |
| FR-14 | System generates a personalized roadmap through the AI service. |
| FR-15 | System validates AI-generated structured output. |
| FR-16 | System stores roadmap phases and tasks. |
| FR-17 | User can view roadmap details. |
| FR-18 | User can mark tasks as completed/in progress/not started. |
| FR-19 | System calculates roadmap progress. |
| FR-20 | System can recommend projects relevant to skill gaps. |
| FR-21 | System can reassess the roadmap after meaningful progress or profile changes. |
| FR-22 | Dashboard summarizes career, skills, roadmap, tasks, and progress. |

## 7. Non-Functional Requirements

### Performance
- Normal API operations should respond quickly under expected student-project load.
- Database queries should use appropriate indexes.
- AI calls should use explicit timeouts and failure handling.

### Security
- Passwords must be hashed.
- Authentication tokens must be protected.
- Users must only access their own private data.
- Secrets must never be committed.
- Inputs and AI outputs must be validated.

### Reliability
- AI provider failure must not corrupt existing roadmap data.
- Database writes must preserve referential integrity.
- Invalid AI output must not be persisted.

### Maintainability
- Backend follows modular service architecture.
- Frontend uses reusable typed components.
- Business logic is testable independently of HTTP handlers.

### Usability
- Responsive UI.
- Clear loading, empty, success, and error states.
- Roadmap and skill gaps should be understandable without technical knowledge.

## 8. Business Rules

1. Skill proficiency is represented on a 1–5 scale.
2. `Gap = Required Level - Current Level`.
3. A non-positive gap means the user currently meets or exceeds the required level.
4. Priority is based on gap, importance, and relevance according to `AI_ML_DESIGN.md`.
5. Prerequisites should be completed before dependent skills where applicable.
6. Circular prerequisite relationships must be detected and rejected or flagged.
7. Only validated AI output may be persisted.
8. Structured career requirements originate from database data, not from an LLM response.

## 9. External Dependencies

- PostgreSQL
- LLM provider API
- Email or notification service only if later implemented

## 10. Acceptance Criteria

The MVP is acceptable when a new user can:
1. Register and log in.
2. Complete a profile.
3. Enter current skills and proficiency.
4. Select a target career.
5. See a calculated skill-gap analysis.
6. See prerequisite-aware priorities.
7. Generate a personalized roadmap.
8. View roadmap phases/tasks.
9. Complete tasks.
10. See updated progress.

## 11. Constraints

- MVP should remain a modular monolith.
- No unnecessary microservices.
- No claim of a trained ML model unless actually implemented.
- No direct database mutation by the LLM.
- Technology changes require justification.

## 12. Definition of Done

A requirement is complete only when implementation, validation, relevant tests, error handling, and documentation are addressed.
