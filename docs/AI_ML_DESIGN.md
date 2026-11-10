# AI Career Roadmap Generator — AI/ML Design

## 1. AI Objective

Generate personalized and actionable career learning roadmaps while keeping career intelligence deterministic, explainable, and grounded in structured data.

## 2. Hybrid Architecture

```text
Structured Career Data
        ↓
Skill-Gap Engine
        ↓
Priority Engine
        ↓
Prerequisite Engine
        ↓
AI Context Builder
        ↓
LLM
        ↓
Structured Output
        ↓
Validation
        ↓
Roadmap
```

## 3. Proficiency Model

Use a 1–5 scale:

| Level | Meaning |
|---|---|
| 1 | Beginner / awareness |
| 2 | Basic |
| 3 | Intermediate |
| 4 | Advanced |
| 5 | Strong / professional |

## 4. Skill Gap

`Gap = Required Level - Current Level`

Interpretation:
- `Gap > 0`: learning required.
- `Gap = 0`: requirement met.
- `Gap < 0`: user exceeds the required level.

Clamp/display behavior should be defined consistently in code and UI.

## 5. Skill Priority

Conceptual formula:

`Priority Score = Gap × Importance × Relevance`

Where importance and relevance are structured career-skill values.

Normalize or cap scores if required for UI ranking.

## 6. Career Compatibility

For career recommendations:

`Compatibility = Weighted Skill Match / Total Skill Weight`

A skill match should account for the user's current proficiency versus the career's required level.

## 7. Prerequisite Graph

Represent:

`Prerequisite → Dependent Skill`

Use graph traversal/topological ordering to place foundational skills before dependent skills.

Required protections:
- Cycle detection
- Duplicate elimination
- Missing-node handling
- Deterministic output

A circular dependency must never produce an infinite traversal.

## 8. Project Recommendation

Conceptual score:

`Project Score = Skill Coverage × Career Relevance × Level Compatibility`

Projects should cover missing/high-priority skills and be appropriate to the user's level.

## 9. Personalization Inputs

The AI context may include:
- User education/experience
- Current skill levels
- Target career
- Required skills
- Skill gaps
- Priority scores
- Prerequisite ordering
- Weekly study hours
- Preferred learning constraints
- Recommended projects/resources

## 10. AI Responsibilities

The LLM may:
- Explain skill gaps.
- Organize learning activities.
- Personalize descriptions.
- Propose task wording.
- Suggest realistic sequencing within supplied constraints.
- Produce a structured roadmap.

The LLM must not be the authoritative source for:
- Career skill requirements
- User skill levels
- Numerical gap calculations
- Database ownership
- Prerequisite relationships

## 11. Prompt Architecture

Use a versioned prompt template with:
1. System instructions
2. Controlled user context
3. Structured career requirements
4. Skill-gap analysis
5. Prerequisites
6. Output schema
7. Constraints

Example instruction:

```text
Generate a practical learning roadmap for the supplied
career and learner profile.

Use only the supplied career skills and prerequisite
information as authoritative requirements.

Prioritize missing high-impact skills and respect
prerequisite ordering.

Return only the requested structured schema.
Do not invent database identifiers.
```

## 12. Structured Output

The roadmap response should contain a predictable structure similar to:

```json
{
  "title": "string",
  "summary": "string",
  "phases": [
    {
      "title": "string",
      "description": "string",
      "order": 1,
      "tasks": [
        {
          "title": "string",
          "description": "string",
          "skill_id": "uuid-or-null",
          "estimated_hours": 5,
          "order": 1
        }
      ]
    }
  ]
}
```

The exact schema must be implemented with Pydantic and kept aligned with the API/database design.

## 13. Validation

Validate:
- JSON/schema
- Required fields
- Data types
- Valid skill IDs
- Valid career context
- Positive hours
- Reasonable task counts
- Phase/task ordering
- No unsupported requirements
- No dangerous or irrelevant instructions

## 14. Hallucination Control

Reduce hallucinations by:
- Supplying structured context.
- Restricting allowed skill IDs.
- Validating identifiers.
- Rejecting unsupported skills.
- Using deterministic calculations.
- Regenerating invalid output.

## 15. Retry Strategy

If the AI call fails:
1. Record the failure.
2. Retry only within a controlled limit.
3. Use timeout/backoff.
4. Validate the retry response.
5. Return a clear error if all attempts fail.

Do not endlessly retry.

## 16. Prompt Injection Protection

Treat user-entered text and retrieved content as untrusted.

The system prompt should clearly separate:
- Developer/system rules
- Structured application data
- User preferences
- Untrusted text

Never allow user text to override system constraints or database rules.

## 17. Cost and Performance

- Keep prompts focused.
- Avoid sending unnecessary database data.
- Use compact structured context.
- Record latency and token usage when available.
- Cache deterministic computations rather than repeatedly asking the LLM.

## 18. AI Evaluation

Evaluate generated roadmaps using:

| Criterion | Weight |
|---|---:|
| Career Relevance | 20% |
| Skill-Gap Coverage | 20% |
| Prerequisite Correctness | 20% |
| Personalization | 15% |
| Project Relevance | 10% |
| Actionability | 10% |
| Output Validity | 5% |

## 19. Adaptive Roadmap

When the user progresses or changes profile data:
1. Recalculate relevant skill gaps.
2. Recalculate priorities.
3. Re-evaluate prerequisites.
4. Decide whether regeneration is necessary.
5. Generate a revised roadmap only when justified.

Do not regenerate on every page load.

## 20. Academic Accuracy

The MVP is an **AI-powered hybrid rule-based + LLM system**.

Do not claim that a trained machine-learning model predicts careers unless an actual dataset, model, training pipeline, and evaluation have been implemented.

## 21. MVP AI Features

Required:
- Skill-gap analysis
- Priority ordering
- Prerequisite-aware roadmap context
- LLM roadmap generation
- Structured output validation
- AI failure/retry handling
- AI generation logging

Future:
- Resume analysis
- Job-market intelligence
- Job matching
- Interview simulation
- Personalized career assistant

## 22. Implemented provider configuration

The implementation uses Google's Gemini `generateContent` API through a provider interface. The default model is `gemini-3.5-flash-lite`, with JSON response mode and a response schema; Pydantic and application checks remain authoritative after generation. `GEMINI_MODEL` can select another compatible Gemini model without changing career-intelligence or persistence code.

If `GEMINI_API_KEY` is not configured, the application selects the deterministic local planner and identifies it as such in generation logs. When Gemini is unavailable, the application records a sanitized provider error and falls back to the deterministic planner. This mode makes the flow demoable without claiming LLM-generated personalization.
