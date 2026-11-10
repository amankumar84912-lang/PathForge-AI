# AI Career Roadmap Generator — UI/UX Specification

## 1. UX Goal

Provide a clear workflow from career exploration to personalized roadmap generation and progress tracking.

Primary principle:

**The user should always understand what the system recommends, why it recommends it, and what to do next.**

## 2. Navigation

### Public
- Landing
- Login
- Register

### Authenticated
- Dashboard
- My Roadmap
- Skills
- Career Explorer
- Projects
- Progress
- Profile/Settings

## 3. Screen Inventory

### 1. Landing
Purpose: Explain product value and start onboarding.

Components:
- Hero
- Value proposition
- How it works
- CTA
- Footer

### 2. Login
Fields:
- Email
- Password

States:
- Validation
- Loading
- Invalid credentials
- Success

### 3. Register
Fields:
- Name
- Email
- Password
- Confirm password

### 4. Onboarding
Collect:
- Education
- Experience level
- Weekly study time
- Initial career interests

### 5. Profile Setup
Allow editing of profile and preferences.

### 6. Skills Assessment
Display skills with:
- Skill name
- Description
- 1–5 proficiency selector
- Optional evidence/notes

### 7. Career Selection
Show careers with:
- Name
- Description
- Difficulty
- High-level skill requirements

### 8. Skill Gap Analysis
Show:
- Current level
- Required level
- Gap
- Priority
- Prerequisites

Use bars/charts where useful.

### 9. Roadmap Generation
Show:
- Target career
- Skill-gap summary
- Study time
- Generation progress
- Clear error/retry state

### 10. Dashboard
Show:
- Target career
- Overall roadmap progress
- Top skill gaps
- Current phase
- Next task
- Recommended project
- Recent activity

### 11. Roadmap Overview
Show phases in sequence:
- Phase title
- Description
- Tasks
- Completion
- Milestones

### 12. Phase/Task Detail
Show:
- Objective
- Skills addressed
- Estimated time
- Tasks
- Resources
- Completion state

### 13. Task Detail
Actions:
- Mark complete
- Mark in progress
- Reopen
- View resources

### 14. My Skills
Show:
- Current skills
- Proficiency
- Edit/remove
- Add skill

### 15. Career Explorer
Search/filter careers.

### 16. Career Detail
Show:
- Overview
- Required skills
- Skill-level expectations
- Example projects
- Start roadmap CTA

### 17. Projects
Show recommended projects and filters.

### 18. Project Detail
Show:
- Objective
- Skills
- Difficulty
- Estimated time
- Suggested outcome

### 19. Progress & Analytics
Show:
- Completion rate
- Tasks completed
- Skills improved
- Milestones
- Activity history

### 20. AI Career Assistant
Phase 2. Conversational guidance grounded in the user's structured data.

### 21. Profile & Settings
Manage:
- Profile
- Preferences
- Security
- Logout

## 4. UI States

Every data-driven screen should support:
- Loading
- Empty
- Error
- Success
- Unauthorized
- Retry

## 5. Responsive Design

Support:
- Desktop
- Tablet
- Mobile

Roadmap visualizations must remain usable on narrow screens.

## 6. Component Architecture

Prefer reusable components:

```text
components/
├── ui/
├── layout/
├── forms/
├── skills/
├── careers/
├── roadmap/
├── progress/
└── dashboard/
```

## 7. API Integration

Keep API calls in dedicated typed client/service modules.

Screens should consume backend APIs rather than duplicate business logic.

## 8. Design System

Use:
- Consistent typography
- Consistent spacing
- Accessible contrast
- Reusable buttons/forms/cards
- Consistent status indicators

Avoid excessive animation.

## 9. Accessibility

- Keyboard navigation
- Visible focus states
- Labels for form controls
- Semantic HTML
- Meaningful error messages
- Accessible charts/alternative summaries

## 10. AI UX Rules

AI-generated information should be presented as recommendations, not unquestionable facts.

Where useful, show:
- Why a skill is prioritized
- Which prerequisite causes the ordering
- Which user data influenced personalization

Do not expose raw prompts or internal AI implementation details to ordinary users.

## 11. Roadmap Visualization

The roadmap should communicate:
`Phase → Tasks → Milestone → Completion`

A user should be able to reach the next actionable task quickly.

## 12. MVP Priority

### P0
- Login/Register
- Onboarding/Profile
- Skills
- Career selection
- Skill gap
- Roadmap
- Dashboard
- Task completion

### P1
- Projects
- Progress analytics
- Career explorer improvements

### P2
- AI assistant
- Advanced analytics
- Resume/GitHub/job features
