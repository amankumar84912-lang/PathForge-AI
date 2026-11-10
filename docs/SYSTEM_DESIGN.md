# AI Career Roadmap Generator — System Design

## 1. Design Goal

Design a maintainable web system in which deterministic career intelligence and LLM personalization work together without allowing probabilistic AI output to become the source of truth.

## 2. High-Level Architecture

```text
User
  |
  v
Next.js + TypeScript
  |
  v
FastAPI REST API
  |
  +-------------------+
  |                   |
  v                   v
Application       AI Service
Services              |
  |                   v
  |                  LLM
  v                   |
PostgreSQL <--- Validation
```

## 3. Layers

### Presentation Layer
Next.js handles:
- Routing
- Forms
- Authentication UI
- Dashboards
- Roadmap visualization
- Progress visualization

### API/Application Layer
FastAPI handles:
- Request validation
- Authentication
- Authorization
- API routing
- Service orchestration
- Error responses

### Career Intelligence Layer
Responsible for:
- Skill-gap calculation
- Skill priority
- Career compatibility
- Prerequisite graph traversal
- Project matching

### AI Service Layer
Responsible for:
- Context construction
- Prompt construction
- LLM calls
- Structured output parsing
- Output validation
- Retry/failure handling

### Database Layer
PostgreSQL stores:
- Users
- Profiles
- Skills
- Careers
- Career-skill mappings
- Prerequisites
- Projects
- Roadmaps
- Tasks
- Progress
- Resources
- AI generation logs

## 4. Core Modules

```text
auth
profiles
skills
careers
assessment
skill_gap
prerequisites
recommendations
roadmaps
projects
progress
ai
dashboard
admin
```

## 5. Skill-Gap Engine

Inputs:
- Target career
- Career-required skills
- User skill levels

Process:
1. Retrieve required skills.
2. Retrieve current user levels.
3. Calculate gap for each skill.
4. Calculate priority.
5. Return structured analysis.

Formula:

`Gap = Required Level - Current Level`

## 6. Prerequisite Engine

Represent prerequisites as directed edges:

`Prerequisite Skill → Dependent Skill`

The engine should:
- Traverse dependencies.
- Order foundational skills before dependent skills.
- Detect cycles.
- Avoid duplicate nodes.
- Return a deterministic ordering.

## 7. AI Roadmap Pipeline

```text
Target Career
     +
User Profile
     +
Skill Gaps
     +
Priority
     +
Prerequisites
     +
Learning Constraints
     |
     v
AI Context Builder
     |
     v
Prompt
     |
     v
LLM
     |
     v
Structured Output
     |
     v
Schema + Business Validation
     |
     v
Roadmap Persistence
```

## 8. AI Context Rules

The context sent to the LLM should contain controlled data such as:
- Target career
- Current skills
- Required skills
- Gaps
- Priority scores
- Prerequisite order
- Available study time
- Preferred learning style where supported
- Relevant projects/resources

The LLM should not be asked to invent authoritative career requirements.

## 9. Roadmap Structure

```text
Roadmap
 ├── Phase
 │    ├── Task
 │    ├── Task
 │    └── Milestone
 ├── Phase
 │    └── Tasks
 └── Phase
```

## 10. Progress Architecture

Task completion updates task progress.

Roadmap progress is calculated from task completion rather than manually entered percentages.

A future adaptive system may trigger reassessment when:
- User changes target career.
- User changes skill level.
- Major roadmap milestones are completed.
- User requests regeneration.

## 11. Project Recommendation

Projects are matched against:
- Skill coverage
- Career relevance
- User level compatibility

The recommendation engine should use structured mappings rather than relying solely on free-form AI suggestions.

## 12. Security Architecture

- Protected API routes require authentication.
- Authorization checks resource ownership.
- Passwords are hashed.
- Secrets remain server-side.
- AI API keys are never exposed to the browser.
- User-generated text is treated as untrusted.
- AI output is validated before database persistence.

## 13. Error Handling

Expected categories:
- Validation errors
- Authentication errors
- Authorization errors
- Resource-not-found errors
- Database errors
- AI provider errors
- AI validation errors
- Rate-limit errors

Return consistent API error structures.

## 14. Deployment Architecture

For the MVP:

```text
Browser
  |
  v
Hosted Next.js
  |
  v
Hosted FastAPI
  |
  +----> PostgreSQL
  |
  +----> LLM Provider
```

Keep deployment simple unless requirements justify additional infrastructure.

## 15. Core Design Principle

**The LLM is a personalization layer, not the source of truth.**

The structured database and deterministic engines decide:
- What skills matter.
- What the user is missing.
- What should have priority.
- Which prerequisites exist.

The LLM decides primarily:
- How to explain.
- How to organize learning activities.
- How to personalize the roadmap within the supplied constraints.

## 16. Full Workflow

```text
User Profile
   ↓
Career Goal
   ↓
Skill Assessment
   ↓
Skill Gap
   ↓
Priority
   ↓
Prerequisites
   ↓
AI Context
   ↓
Personalized Roadmap
   ↓
Tasks + Milestones
   ↓
Progress
   ↓
Reassessment
```
