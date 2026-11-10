# AI Career Roadmap Generator — Database Design

## 1. Database

**PostgreSQL**

Use UUID primary keys for application entities where practical.

## 2. Tables

### users
- `id` PK
- `email` UNIQUE
- `password_hash`
- `is_active`
- `created_at`
- `updated_at`

### profiles
- `id` PK
- `user_id` FK → users.id
- `full_name`
- `education`
- `experience_level`
- `weekly_hours`
- `bio`
- timestamps

### skills
- `id` PK
- `name` UNIQUE
- `description`
- `category`
- timestamps

### careers
- `id` PK
- `name` UNIQUE
- `description`
- `difficulty_level`
- timestamps

### career_skills
- `career_id` FK
- `skill_id` FK
- `required_level`
- `importance`
- `relevance`
- composite/unique key on career + skill

### skill_prerequisites
- `skill_id` FK
- `prerequisite_skill_id` FK
- unique pair
- prevent self-reference at application/database validation level

### user_skills
- `user_id` FK
- `skill_id` FK
- `proficiency_level`
- timestamps
- unique user + skill

### projects
- `id` PK
- `name`
- `description`
- `difficulty_level`
- `estimated_hours`
- timestamps

### project_skills
- `project_id` FK
- `skill_id` FK
- `importance`
- unique project + skill

### career_projects
- `career_id` FK
- `project_id` FK
- relevance
- unique career + project

### roadmaps
- `id` PK
- `user_id` FK
- `career_id` FK
- `title`
- `status`
- `generated_at`
- timestamps

### roadmap_phases
- `id` PK
- `roadmap_id` FK
- `title`
- `description`
- `order_index`

### roadmap_tasks
- `id` PK
- `phase_id` FK
- `title`
- `description`
- `skill_id` nullable FK
- `estimated_hours`
- `order_index`

### milestones
- `id` PK
- `roadmap_id` FK
- `title`
- `description`
- `order_index`

### milestone_tasks
- `milestone_id` FK
- `task_id` FK

### task_progress
- `id` PK
- `task_id` FK
- `user_id` FK
- `status`
- `completed_at`
- timestamps

### resources
- `id` PK
- `title`
- `url`
- `resource_type`
- `description`

### skill_resources
- `skill_id` FK
- `resource_id` FK

### career_resources
- `career_id` FK
- `resource_id` FK

### ai_generation_logs
- `id` PK
- `user_id` FK
- `roadmap_id` nullable FK
- provider
- model
- prompt_version
- status
- latency_ms
- token/input-output metadata where available
- validation_result
- error_message
- created_at

## 3. Relationship Summary

```text
users 1---1 profiles
users 1---N user_skills N---1 skills

careers 1---N career_skills N---1 skills

skills 1---N skill_prerequisites
skills 1---N skill_prerequisites (as prerequisite)

projects 1---N project_skills N---1 skills
careers N---N projects

users 1---N roadmaps N---1 careers
roadmaps 1---N roadmap_phases
roadmap_phases 1---N roadmap_tasks
roadmaps 1---N milestones
milestones N---N roadmap_tasks
roadmap_tasks 1---N task_progress
```

## 4. Integrity Rules

- Use PK/FK constraints.
- Use unique constraints for natural duplicates such as skill names and career names.
- Use check constraints where appropriate for proficiency and ordering values.
- Use transactions for multi-table roadmap persistence.
- Apply deliberate delete behavior; avoid accidental cascading deletion of important user history.

## 5. Indexing

Recommended indexes:
- users.email
- profiles.user_id
- user_skills.user_id
- user_skills.skill_id
- career_skills.career_id
- career_skills.skill_id
- skill_prerequisites.skill_id
- skill_prerequisites.prerequisite_skill_id
- roadmaps.user_id
- roadmaps.career_id
- roadmap_phases.roadmap_id
- roadmap_tasks.phase_id
- task_progress.user_id
- task_progress.task_id

## 6. Normalization

The schema should remain approximately in Third Normal Form:
- Skills are stored once.
- Careers are stored once.
- Many-to-many relationships use mapping tables.
- Roadmap tasks are separate records so progress can be tracked.

## 7. Roadmap Persistence

Do not store the entire roadmap only as an opaque JSON blob.

AI output should be transformed into:
`roadmap → phases → tasks → milestones → progress`

JSON may still be retained for debugging/versioning where appropriate, but it must not replace the relational model.

## 8. AI-to-Database Pipeline

```text
LLM JSON
  ↓
Pydantic/schema validation
  ↓
Business-rule validation
  ↓
Skill/career ID verification
  ↓
Database transaction
  ↓
Roadmap + phases + tasks
```

If validation fails, do not partially persist the roadmap.

## 9. Seed Data

Initial seed data should include a small, curated set of:
- Skills
- Careers
- Career-skill requirements
- Skill prerequisites
- Projects
- Project-skill mappings
- Learning resources

Start small and expand after the core system works.

## 10. Migration Strategy

Use a migration tool such as Alembic with SQLAlchemy.

Rules:
- Every schema change should be represented by a migration.
- Never rely on manual production edits.
- Test migrations from a clean database.
