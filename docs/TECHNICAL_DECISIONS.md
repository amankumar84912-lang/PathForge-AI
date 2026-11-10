# AI Career Roadmap Generator — Technical Decisions

This document records important architectural decisions so that implementation remains consistent across development sessions and AI coding agents.

---

## TD-001 — Use a Modular Monolith

**Decision:** Build the MVP as a modular monolith.

**Reason:** The project is a B.Tech-level application with interconnected modules. A modular monolith is easier to develop, test, deploy, and demonstrate than a microservice architecture.

**Implication:** Backend modules should have clear boundaries even though they run in one FastAPI application.

---

## TD-002 — PostgreSQL as the Primary Database

**Decision:** Use PostgreSQL.

**Reason:** The system has strongly related entities such as users, skills, careers, career-skill mappings, prerequisites, roadmaps, tasks, projects, and progress records. Relational constraints and joins are appropriate.

**Implication:** Structured application data should remain relational.

---

## TD-003 — FastAPI for the Backend

**Decision:** Use Python + FastAPI.

**Reason:** FastAPI provides typed request/response validation, automatic OpenAPI documentation, and a strong Python ecosystem for AI-related integration.

**Implication:** Backend business logic and AI orchestration are implemented in Python.

---

## TD-004 — Next.js for the Frontend

**Decision:** Use Next.js + TypeScript.

**Reason:** The application requires multiple authenticated screens, reusable UI components, forms, dashboards, and data visualization. TypeScript improves maintainability.

**Implication:** Frontend code should remain strongly typed and API-driven.

---

## TD-005 — Hybrid AI Architecture

**Decision:** Combine deterministic algorithms with an LLM.

**Reason:** Career requirements, skill gaps, and prerequisites should be explainable and reproducible. LLMs are better suited to personalization and natural-language generation.

**Architecture:**

`Career Data → Skill Gap → Priority → Prerequisites → AI Context → LLM → Validation → Roadmap`

---

## TD-006 — LLM Is Not the Source of Truth

**Decision:** The LLM must not determine authoritative career requirements independently.

**Reason:** LLM output can hallucinate, vary between calls, or recommend unsupported skills.

**Implication:** Career requirements and skill relationships come from structured database data. The LLM receives controlled context.

---

## TD-007 — Validate AI Output Before Persistence

**Decision:** All structured AI roadmap output must pass schema and business-rule validation before being stored.

**Reason:** LLM responses are probabilistic and may contain malformed or unsupported data.

**Implication:** Invalid responses are rejected, repaired, or regenerated according to the AI design.

---

## TD-008 — Store Roadmaps Relationally

**Decision:** Store roadmaps using roadmap, phase, task, milestone, and progress records rather than storing the entire roadmap only as one JSON object.

**Reason:** Users need task-level completion, progress calculation, updates, and queries.

**Implication:** AI output is transformed into normalized database records.

---

## TD-009 — Deterministic Skill-Gap Calculation

**Decision:** Calculate skill gaps algorithmically.

**Formula:**

`Gap = Required Level - Current Level`

**Reason:** The calculation should be reproducible and testable.

**Implication:** The LLM does not decide the numerical skill gap.

---

## TD-010 — Prerequisites as a Graph

**Decision:** Represent skill prerequisites as a directed graph.

**Reason:** Some skills depend on other skills. Dependency-aware ordering prevents a roadmap from teaching advanced skills before their foundations.

**Implication:** The system must support traversal and circular-dependency detection.

---

## TD-011 — Provider-Agnostic AI Service

**Decision:** Keep the AI integration behind a service/provider abstraction.

**Reason:** This prevents the rest of the application from being tightly coupled to one LLM vendor.

**Implication:** Changing providers should primarily affect the AI integration layer rather than the entire application.

---

## TD-012 — API Versioning

**Decision:** Use `/api/v1`.

**Reason:** Versioning provides a clear boundary for future API evolution.

**Implication:** Breaking API changes require deliberate versioning rather than silently changing existing contracts.

---

## TD-013 — No Real ML Training in MVP Unless Implemented

**Decision:** Do not describe the system as containing a trained ML model unless an actual model, dataset, training process, and evaluation are implemented.

**Reason:** Academic accuracy is more important than making the project sound more advanced.

**Current description:** Hybrid rule-based + LLM-powered career recommendation and roadmap generation system.

---

## TD-014 — No Microservices in MVP

**Decision:** Do not split the MVP into microservices.

**Reason:** The additional deployment, networking, observability, and operational complexity is not justified by the project scope.

---

## TD-015 — Real APIs Over Mock Data

**Decision:** Use mock data only during early isolated UI development.

**Reason:** Persistent mock data can hide integration problems.

**Implication:** Once a real API exists, frontend features should use it.

---

## TD-016 — Documentation Is Part of the Engineering Contract

**Decision:** Major implementation decisions must remain aligned with the project documentation.

**Reason:** The project is being developed with AI assistance and multiple technical documents. Explicit documentation reduces architectural drift.

**Implication:** If implementation intentionally changes a documented decision, the relevant documentation must be updated.

---

## TD-017 — Security by Default

**Decision:** Treat all external input, user input, retrieved content, and AI output as untrusted.

**Reason:** The system handles authentication, user data, and external AI services.

**Implication:** Validate inputs, isolate user data, protect secrets, and validate AI output.

---

## TD-018 — Configurable Gemini Roadmap Provider

**Decision:** Use Google's Gemini `generateContent` API through a provider interface, defaulting to `gemini-3.5-flash-lite` with JSON response mode and a response schema.

**Reason:** Gemini is the configured LLM provider for roadmap personalization. Its structured JSON output is validated by the application's Pydantic schema and business rules before persistence.

**Implication:** `GEMINI_API_KEY` enables the provider and `GEMINI_MODEL` selects its model. Pydantic and business validation still gate persistence. When the key is absent or Gemini fails, the app uses the separately named deterministic planner.

---

## Decision Change Process

A major decision should be changed only after:

1. Identifying the current decision.
2. Explaining the reason for change.
3. Identifying affected modules.
4. Checking database/API/documentation impact.
5. Updating this document.
6. Updating affected design documents.
7. Implementing and testing the change.
