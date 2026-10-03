# AI architecture patterns

## What the inspected projects do

| Project | Confirmed AI role | State/action effect | Boundary and recovery | Classification |
|---|---|---|---|---|
| RecallReady | Extracts product name/brand/model/retailer from receipt email using strict schema | Structured result can create inventory | Required-field check; deterministic model/brand matcher; webhook idempotency | AI feature inside a stateful workflow |
| Parallel | Extracts agenda, scores session-goal relevance, parses email intent/quote, writes brief | Scores guide deterministic solver; guarded reply may change constraints; brief is persisted/sent | Schemas, confidence, quote evidence, revision/frozen checks, source verification and test coverage | AI workflow with bounded agentic control |
| PlusOne | Plans web search, extracts/ranks vendors and quotes, drafts emails, parses RSVP/vendor replies, wedding assistant tools | Can start search/add a need; emails need approval; quote extraction updates budget | role checks, structured schemas, explicit confirmation, bounded follow-ups; empirical Firecrawl evaluation | AI workflow plus limited tool-using assistant |
| OurSpaces | README describes AI filing and question generation, an agent thread and RAG-grounded “ask the space” | Email classification becomes a widget; saved state is the answer context | README claims rate limiting, retries/caching, persistent streaming; source-level verification unavailable | Claimed AI workflow/agent; code classification remains provisional |

No project evidence supports “more AI calls = stronger project.” Parallel's deterministic optimizer is the technical center; its LLM does semantic work around it. RecallReady's deterministic match is the safety center; adding a planner would not improve it.

## Recommended hierarchy for future work

1. **Deterministic product logic first.** If a rule can be explicit, testable code, do not ask a model to guess it.
2. **AI as extractor/classifier.** Give unstructured input, a narrow typed schema, length/enum/range constraints and an uncertainty outcome.
3. **AI as scorer/planner proposal.** Ask for ranked alternatives or a constrained proposal, then independently evaluate feasibility/objective in code.
4. **AI with tools.** Provide only the few tools needed for the user's task; authorize each write server-side; check tool output before the next step.
5. **AI coordinator/controller.** Use a persisted run state machine, bounded steps, explicit stop conditions, retry policy, idempotency and human approval for consequential actions.
6. **AI with evaluation and recovery.** Maintain representative fixtures, compare outcomes, record version/cost/latency, reject unsafe outputs, and make restart/replan behavior visible.

Climb only as far as the problem needs. A real one-pass extraction can be the right design; an autonomous loop is a liability unless state changes and tool results make the loop useful.

## Required AI contract

For every model call document:

- **Input:** source IDs, user goal, relevant state, truncation and untrusted-data boundaries.
- **Output:** schema, allowed values, optional/unknown representation, validation rules.
- **Decision authority:** what state transition the result may request; what it may never decide.
- **Tools:** name, args schema, read/write scope, permission check and idempotency strategy.
- **State:** run/thread ID, step, attempt, inputs/version, result, status and audit link.
- **Wrong-output behavior:** reject, ask human, or fall back safely; never convert parse failure into a positive/clean claim.
- **External failure:** retry only transient failures; bounded exponential backoff; no duplicate side effect.
- **Evaluation:** fixed examples, edge cases, success criteria, source/citation correctness and regression threshold.
- **Observability:** model/version, schema version, duration, status, token/cost if available, not secrets or unnecessary personal content.

## Appropriate RecallReady AI design

```text
Receipt text (untrusted)
→ strict extraction proposal
→ field presence + plausibility + evidence checks
→ uncertain/multi-item cases queued for correction
→ deterministic canonical product record
→ exact/source-backed recall matcher
→ alert only after actionable evidence; otherwise review state
```

OpenAI is useful for messy receipt formats and product identity extraction. It should not decide that an official notice matches a household appliance by semantic similarity alone. The archive's rule-based matcher is the right foundation; it needs broader measured fixtures and an uncertainty path. Use deterministic identifier normalization and exact/alias matching, with human review for partial identifiers.

## Why this is not a fake agent standard

Do not split a single extraction into “researcher, analyst and verifier agents” unless each has distinct access, distinct evidence, and a measurable reason to cooperate. Do not let an LLM repeatedly call itself to make a routine workflow seem autonomous. Record a state machine in code; let the model handle the unstructured reasoning that code cannot reasonably supply.
