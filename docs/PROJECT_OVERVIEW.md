# AI Career Roadmap Generator — Project Overview

## 1. Project Title

**AI Career Roadmap Generator**

## 2. Project Summary

The AI Career Roadmap Generator is a web-based system that helps students and early-career users plan a career path based on their current skills, target career, skill gaps, prerequisite dependencies, learning availability, and project interests.

The system combines structured career and skill data with deterministic analysis and LLM-based personalization.

## 3. Core Problem

Students often know the career they want but do not know:
- Which skills are actually required
- Which skills they already have
- Which skills are missing
- Which skills should be learned first
- Which projects will demonstrate those skills
- How to organize learning into a practical sequence

Generic roadmaps do not adequately account for the learner's existing knowledge, time availability, and progress.

## 4. Proposed Solution

The system:

1. Collects the user's profile.
2. Records current skills and proficiency.
3. Lets the user select a target career.
4. Retrieves required career skills from structured data.
5. Calculates skill gaps.
6. Assigns priorities.
7. Resolves skill prerequisites.
8. Builds controlled AI context.
9. Uses an LLM to personalize the learning roadmap.
10. Validates the AI output.
11. Stores the roadmap.
12. Tracks task completion and progress.
13. Reassesses and adapts the roadmap.

## 5. Core Differentiator

This is not intended to be a simple chatbot that asks for a career and generates generic text.

The key architecture is:

`Structured Career Knowledge + Deterministic Skill Intelligence + Prerequisite Graph + LLM Personalization + Progress Adaptation`

## 6. MVP

The MVP includes:

- User registration/login
- Student profile
- Skill management
- Skill proficiency assessment
- Career explorer
- Career selection
- Skill-gap analysis
- Skill priority calculation
- Prerequisite ordering
- AI roadmap generation
- Roadmap phases and tasks
- Task completion
- Progress tracking
- Dashboard

## 7. Future Enhancements

Possible Phase 2 features:
- Resume analyzer
- GitHub profile analysis
- Job-market analysis
- Job matching
- AI career assistant
- AI mock interview
- Advanced project recommendations

These are not required for the initial MVP.

## 8. Technology Stack

### Frontend
Next.js, TypeScript, Tailwind CSS, component library, Recharts

### Backend
Python, FastAPI, SQLAlchemy, Pydantic

### Database
PostgreSQL

### AI
LLM API through a provider abstraction

## 9. High-Level Architecture

`User → Next.js → FastAPI → Services → PostgreSQL`

For roadmap generation:

`FastAPI → Skill Gap Engine → Prerequisite Engine → AI Context Builder → LLM → Validator → Roadmap Persistence`

## 10. Academic Accuracy

The project should be described accurately.

Unless an actual ML model is trained and evaluated, do not claim that the system contains a trained machine-learning prediction model.

The intended MVP is a **hybrid rule-based + LLM-powered career recommendation and roadmap generation system**.
