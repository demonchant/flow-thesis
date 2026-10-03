# Hackathon Build Standard V2

**Purpose:** carry a hackathon project from event discovery through a verifiable submission. Optimize for a real user outcome, technical substance that serves that outcome, meaningful integrations, reliability, proof and reviewer comprehension. Use this as the default operating procedure when the builder supplies a hackathon, rules, repo or sponsor resources.

## Codex operating instruction

Use this document as the operating procedure for the entire hackathon. The user may provide it alongside official rules, judging criteria, sponsor documentation, repositories or APIs. Read those materials, resolve the rubric, and carry the project from discovery through a concrete, verified submission. Do not wait for the user to dictate routine engineering steps. Make reasonable choices, keep the user informed, and ask only when a missing decision materially changes the product or an external/irreversible action requires approval. Continue useful independent work while waiting for a genuinely blocking answer.

This document is designed to work on its own. If linked supporting templates are unavailable, create equivalent sections in the working project and continue. Do not stop after producing analysis: once the idea passes the gates, implement the highest-value next capability within the authorized scope.

### Four mandatory gates

1. **Hardest-promise gate:** name the single hardest promise in the product pitch. Implement it as a real, observable behavior or narrow the pitch until it matches what works. A README assertion, mocked result, empty cron, or planned workflow does not pass.
2. **Operational-depth gate:** make the hard work arise from the user's real problem. When conditions can change, show a meaningful state transition and response (for example, detect → repair → verify). Do not add state machines, optimization, agents, queues or integrations without a product reason.
3. **Evidence gate:** measure important AI/data decisions against explicit expected outcomes, representative fixtures or independent postconditions. Record sample size, method, errors and limits. Improve the system based on observed failure, not an unqualified “AI works” claim.
4. **Claim-to-proof gate:** every major pitch/README/demo claim must map to implemented behavior, a test or independent evidence, and a demo/reviewer path. If any link is missing, mark it planned/unknown, remove it from the current-tense pitch, or implement it before polish/submission.

These gates apply at idea selection, after the first end-to-end slice, and before submission. A failed gate triggers repair, scope reduction or pivot, never cosmetic work to hide the gap.

## Operating principles

1. The rubric and eligibility rules outrank personal preference. Read the official source before designing.
2. Find a real, specific user problem; do not start from a technology list.
3. Identify the hidden technical difficulty, then use the smallest architecture that solves it.
4. AI must do cognitive work with defined inputs, output, authority, validation and recovery.
5. Sponsor technology must have a real job in the critical path when the event requires it.
6. Build one end-to-end proof early. Do not polish a shell around a missing system.
7. Treat failure, duplicates, stale state, security, and evidence as product behavior.
8. Never fabricate functionality, users, test results, production success, engagement or sponsor involvement.
9. Label every claim `CONFIRMED`, `INFERRED`, `UNKNOWN`, `SIMULATED`, `PLANNED`, or `VERIFIED` precisely.
10. Complexity earns its place only when it creates user value, rubric value or a clear demonstration.

## Phase 0 — event and evidence intake

Collect official event page/rules, judging criteria, submission form/requirements, sponsor docs, APIs/SDKs, permitted technologies, deadlines/timezone, prior winners, competitors, relevant existing project/repo and build standard. Prefer organizer/sponsor primary sources. Record URL, retrieval date and exact eligibility restrictions. If materials conflict, use the latest official source and document uncertainty.

Create or update:

- `docs/hackathon-analysis.md`
- `docs/rubric-matrix.md`
- `docs/dependency-audit.md`
- `docs/competitive-analysis.md`
- `docs/PROJECT_FORENSICS.md` when prior/competitor artifacts exist

Do not begin substantial implementation before the required rule/rubric/research review. A tiny integration spike to test feasibility is research, not product implementation.

### Required initial report

Summarize: event; rules/deadline; rubric mapped to engineering, evidence and demo; sponsor requirements; competitive set; idea candidates and comparison; selected concept and why; hardest technical/data/AI/integration/reliability problems; architecture; AI contract; integrations; failure model; evidence/demo plan; implementation/time plan; pivot conditions; unknowns.

## Phase 1 — rubric engineering matrix

For each criterion record:

| Rubric field | Required answer |
|---|---|
| Criterion/source | Exact criterion and official link |
| Judge intent | Observable capability the wording implies |
| Engineering requirement | Concrete system behavior or artifact |
| Implementation | Code path, state, service or design that will satisfy it |
| Proof | Test, source record, deployment, receipt, reproducible run or other evidence |
| Demo beat | Exact user action and visible result |
| Repository path | Where a reviewer can confirm it |
| Point-loss risk | Eligibility, missing proof, fake integration, unclear value, failure or contradiction |

Also create a **claim-to-behavior ledger** for every major product and technical claim, even if the claim is not a rubric item:

| Pitch/README claim | Observable behavior that must exist | State transition/output | Failure case | Proof/test | Demo/reviewer path | Status |
|---|---|---|---|---|---|---|

The behavior must satisfy the complete meaning of the claim. “Monitors continuously” requires a recurring, observable check and freshness/failure state. “Recovers automatically” requires a real injected or natural failure followed by a persisted recovery. “Optimizes” requires explicit constraints/objective and a checkable result. “Verified” requires a postcondition independent of the API's success response. If the system cannot meet that bar, narrow the wording.

Convert “innovation” into a differentiated mechanism; “AI” into a specific task; “use sponsor” into an indispensable workflow; “technical achievement” into architecture and invariants that can be inspected.

## Phase 2 — generate, compare and gate ideas

Generate at least three genuinely different ideas. For each write: problem/user/pain/constraint, hidden complexity, AI role, state, external systems, sponsor job, novelty, evidence, demo, failure modes, dependency risk, time estimate and competitive alternatives. Reject developer tools if the event explicitly wants everyday apps. Prefer one high-value user outcome over a feature menu.

Complete [`HACKATHON_IDEA_GATE.md`](HACKATHON_IDEA_GATE.md). Go only when its score and mandatory floors pass. Validate the riskiest API/data/eligibility assumption with a short spike. A sponsor service must change what the product can do; if removing it has no meaningful effect, redesign that integration or concept.

## Phase 3 — architecture before implementation

Write a concrete data flow:

```text
user/event input
→ durable application state
→ AI or deterministic reasoning
→ tool/external integration
→ normalized result
→ validated decision
→ authorized side effect
→ persistent state change
→ independent verification
→ user-visible outcome
```

If no meaningful state exists, do not add a database merely for appearance. If the environment changes over time, consider `PLAN → EXECUTE → OBSERVE → COMPARE → REPLAN`, and use it only when changed conditions would otherwise harm the user.

Define before code:

- Canonical entities, indexes and tenant boundaries.
- State machine and permitted transitions.
- Current revision/version or locking rule for concurrent writes.
- AI contract and deterministic checks.
- Tool privileges, human approval boundary and side-effect idempotency.
- Job/workflow decision based on duration/retries/fan-out, not fashion.
- Failure/error/recovery and reconciliation model.
- Evidence records and safe demo fixtures.
- Architecture and test locations in repo.

Use [`TECHNICAL_DEPTH_CHECKLIST.md`](TECHNICAL_DEPTH_CHECKLIST.md). When editing Convex code, follow current official Convex docs and project-specific instructions; never assume old syntax or component behavior.

## Phase 4 — end-to-end proof first

Implement the thinnest real path that covers input → logic/AI → integration → side effect → durable state → verification → user result. Do not spend significant time on secondary features until this works in the intended environment.

### Hardest-promise acceptance gate

Before UI polish or secondary features, write and demonstrate:

```text
Hardest promise:
User-visible trigger:
Real system behavior:
Persisted before/after state:
Independent postcondition:
One abnormal case and safe outcome:
Reproduction instructions:
```

Pass only when the promised behavior works end to end on the target deployment or the product wording has been narrowed to the verified capability. A planned cron, simulated webhook, hard-coded answer or successful provider response alone is not a pass. Capture the evidence and update the claim-to-behavior ledger before proceeding.

Use real external credentials for real integration claims. Provide fixture mode for reliable demos, visibly labeled. Never silently replace a provider failure with a success-looking fixture. Persist run status and output source IDs where useful.

## Phase 5 — depth, sponsor work and AI

Use sponsor tech in the core flow, not only the stack list. Document what it reads, transforms or sends and which persistent result it creates. Show the user capability that would materially change without it.

Design AI as extractor/classifier/planner/proposal maker/coordinator only where uncertainty requires it. Use typed structured output where possible. Validate shape and semantics, enforce constraints deterministically, constrain tools, keep writes server-authorized, ask a person before irreversible/high-impact sends or commitments, and preserve evidence. Add state/memory only to continue a meaningful task, not to imitate agent architecture.

### AI/data measurement gate

For each central extraction, ranking, matching, classification or generation capability, create a small but representative evaluation before claiming quality. Define expected outputs and error categories first; include hard negatives, ambiguous/missing data and realistic input noise. Record fixture count, selection source, pass rule, per-category results and important limits. For retrieval, verify that returned facts and prices appear in the cited source. For matching/safety decisions, track false positives and false negatives separately and route uncertainty safely. Compare a baseline with the revised system when changing prompts, models or pipeline stages. Do not invent a sample size (for example, 500) to sound rigorous; choose a sample that can be labeled and inspected, and state its limits.

## Phase 6 — reliability, security and technical tests

For every core path consider:

- provider unavailable/rate limited/slow;
- invalid or incomplete model result;
- duplicate webhook/click/job;
- event ordering and stale version;
- process crash after partial success;
- provider success but local response/state loss;
- concurrent actors/workers;
- external source changes or disappears;
- authorization/tenant boundary misuse;
- unsafe content/prompt injection and oversized inputs.

Tests should target critical invariants, model schema/validation, source grounding, cross-tenant authorization, state transitions, idempotency, concurrency, retry/recovery, and independently verified postconditions. Do not add tests merely to inflate counts. Run requested build/tests and report exact results; do not claim a test ran when it did not. Build small fixed evaluation fixtures for AI/data quality rather than anecdotal model demos.

## Phase 7 — evidence and repository

Maintain `claim → implementation → test/evidence → demo step → status` throughout development. Save stable fixtures and machine-readable run reports where they strengthen reproducibility. Keep sample secrets out of code and browser bundles. Document setup, environment variables, deploy, seed/reset, known limits and simulated paths.

No major claim may be marked `VERIFIED` from generated copy alone. A verifier must be a postcondition such as a persisted record, an independently fetched external state, a source citation check, an event/receipt, a deterministic invariant, or an observed second-client/reload result. Record the exact run/commit and distinguish a real external event from a played-out scenario.

README first screen should explain problem, user, result, live URL, demo, hardest mechanism, integrations by role, setup/verify commands and evidence links. Include architecture diagram/state machine if it reduces review time. Keep the root event build log factual and synced to the submitted commit. Pin important claims to source links and numbers to the exact run/version.

## Phase 8 — product/UI and reviewer demo

Once core system and proof work, build a UI that makes state, decision and evidence understandable. Design for the judge's first minute: what it is, why it matters, what works, what is technical, how sponsors help and where proof is.

Use [`DEMO_FORENSICS.md`](DEMO_FORENSICS.md). Rehearse a sub-three-minute path where rules allow: problem → input → system decision → real integration → meaningful failure/change → verified state/result → user value. Keep voiceover concise. Music and cinematic editing are optional and cannot obscure proof. Label fixtures, synthetic replies, generated content and played-out scenarios.

## Phase 9 — continuous competitive review

At every milestone ask:

- Is the problem still the strongest rubric fit?
- Is the hardest capability real and demonstrable?
- Does AI do necessary work, with deterministic safety checks?
- Does each sponsor have an important/core job?
- Does state survive reloads and external changes?
- Are results independently verified?
- What is the single biggest competitive weakness, and what one change improves real capability most?
- Does every major pitch claim pass the claim-to-proof gate, including the hardest promise?
- Have we measured the most consequential AI/data output against expected outcomes and disclosed the limits?

Inspect competitors at implementation/demo level when evidence is available; compare mechanisms, not only screenshots. Do not copy their architecture if it does not fit the problem.

## Make-it-deeper procedure

When a prototype works but feels shallow, ask in sequence: persistent state? explicit constraints? plan before acting? meaningful tools? external change detection? replan? independent verification? recovery from failure? concurrency? durable restart? audit/evaluation? safe side effects? multiple actors? measurable optimization? Add only the capability that improves the user outcome and can be tested/demoed. A solver, RAG layer, multi-agent setup, queue or blockchain without this test is rejected.

## No-fake-technicality rule

Reject fake agents, purposeless chained LLM calls, technology name-dropping, arbitrary APIs, unnecessary microservices/queues/vector DBs/blockchain, artificial distributed architecture, inflated test counts, unsupported benchmark claims, and complexity that cannot be demonstrated or does not solve the problem. Prefer a clear state machine to an LLM loop; a deterministic calculation to probabilistic output; one useful integration to several superficial ones.

## Stop conditions before polish

Do not move into polish while any of these is true:

- The hardest user promise does not work end to end and the pitch has not been narrowed.
- A required sponsor integration is decorative, unavailable, or not part of a real user outcome.
- A consequential AI/data claim has no validation/evaluation path.
- A failure can make the UI report success/clean state without verifying the postcondition.
- A feature is described as automatic/continuous but has no actual trigger, persisted status and failure path.
- The only demo result is a mock but the product copy presents it as live.

Fix, narrow scope, or pivot. Do not attempt to compensate with more pages, agents, tests or visual polish.

## Time plan

Plan backward from the official deadline and hold a protected final period for build validation, evidence, deployment, demo, documentation and form submission. Reallocate as facts change:

- **Early:** rules, sources, user/problem, idea gate, risk spikes, core architecture and end-to-end proof.
- **Middle:** difficult capability, sponsor/external integration, durable state, failure handling, tests and evidence.
- **Late:** reliability fix, UX for core path, demo capture, README/build log, submission links/receipt.

Cut optional features before evidence, core integration, failure handling or final submission. If a central API is unavailable, document its effect and pivot to the strongest honest path early.

## Pivot rules

Immediately report a failed central assumption, affected criteria, technical/competitive ceiling, repair, pivot and time cost. Pivot when eligibility fails, required sponsor capability cannot work, core data cannot be accessed lawfully/reliably, or the remaining repair is larger than time available. Keep the project useful and truthful; never present a mocked dependency as live.

## Final submission gate (all required)

- Eligibility/new-app/team rules and exact submission form verified against official source.
- Public repo and permitted public deployment resolve in a cold browser.
- A fresh setup/build/critical test command succeeds and the results are recorded accurately.
- Core workflow works end to end; key side effects have postcondition evidence.
- Required sponsor technologies perform real work in the path and are visible in demo.
- Demo fits event length, opens on the real product, labels simulated data, and matches the release commit.
- README/build log describe actual features and distinguish live/simulated/planned/unknown.
- Each rubric row maps to code, proof, demo and submission artifact.
- Security/permissions, known limitations and failure behavior are documented.
- Submission form has been sent before deadline; save confirmation/receipt and final URL.
- Social post is published if required; link and available engagement evidence recorded without inventing metrics.
- Hostile review asks why it matters, what is hard, what was built, what sponsor/AI actually did, what can fail, what is verified, and what a competitor does better. Fix the highest-impact feasible gap.

## Evidence-derived recurring formula

### Higher confidence (multiple project artifacts)

- A specific everyday problem with a simple user-facing explanation.
- Sponsor/external systems participate in the product path, not only the README.
- Persistent typed state and a clear workflow make integration results visible.
- Structured AI output plus deterministic boundaries is more trustworthy than free-form model authority.
- Short judge path, live deployment, root build log and direct demo/evidence links reduce reviewer effort.

### Medium confidence (some projects)

- A state change/failure-and-repair demo can communicate more technical depth than a feature tour (especially Parallel).
- Adversarial tests and immutable run evidence are valuable differentiators where the product has side effects (Parallel, RecallReady foundations).
- Measured source/model quality work can catch hidden data failures (PlusOne evaluation docs).
- Realtime multi-actor behavior is powerful when collaboration is the product (OurSpaces README, plus the others' shared state).

### Unsupported assumptions

- More technologies, agents, tests, or code cause wins.
- Any one inspected project won specifically because of one architecture feature.
- Social engagement alone predicts judging outcome; user-supplied counts are not independently verified here.
- Visual polish or AI voiceover was used by a given winner without inspecting its media.

Treat this formula as a set of design hypotheses supported by artifacts, not a universal recipe or guarantee.

## Competitive Winning Loop — 2026 Unusual Whales Hackathon

Apply this section throughout discovery, architecture, implementation and final review. Meeting the rules is only eligibility; it does not establish that a submission is competitive. Compare the project against the strongest publicly discoverable submissions and against Unusual Whales' own products and API capabilities. Record evidence and unknowns separately.

### Checkpoint questions

At each major checkpoint, answer:

1. What does this project do that a normal UW dashboard does not?
2. What does it do that a generic AI market chatbot cannot do?
3. What technically difficult behavior can be demonstrated that a typical submission is unlikely to demonstrate?
4. Which implemented capability would take another builder meaningful effort to reproduce, and what user outcome justifies that effort?
5. What evidence proves the capability works?
6. How does it react when market state changes?
7. What happens when data is incomplete, delayed, contradictory or unavailable?
8. What happens when AI returns invalid or unsupported output?
9. What happens when a user's original thesis no longer holds? Can the system detect and explain the change?
10. Can a judge understand the innovation within 30 seconds?
11. Can the important workflow be shown live, and can the repository prove that the behavior is real?

Record the strongest criticism as well as the strongest claim. Do not invent praise or treat lack of discovered competitors as proof of uniqueness.

### Competitive moat

Identify at least one real technical moat: implemented data processing, evaluation, workflow design, optimization, state handling, verification, reliability or another difficult capability. A prompt, API call, model choice, dashboard or visual design is not a technical moat by itself. State what removing the moat would make materially weaker or impossible, and how the product benefits.

### Judge memory test

Complete: “They will remember this project because ______.” The answer must name a distinctive system behavior or user outcome. If the answer is only “nice UI,” “uses AI,” “uses the UW API,” or “has many features,” reject or redesign the concept.

### One-minute proof test

Plan a concise demonstration that shows, where the problem warrants it:

1. A real market event or meaningful input.
2. UW data being retrieved.
3. Non-trivial analysis.
4. Meaningful AI reasoning, if AI is part of the solution.
5. Deterministic validation or constraints.
6. State creation or change.
7. A second event or changed condition.
8. The system reacting to that change.
9. Evidence for the result.
10. A clear user outcome.

If an item does not fit the problem, justify the deviation. Clearly label fixtures, replays and simulated events. Do not stage a simulation as a live market event.

### Anti-wrapper and product-displacement tests

Before approving implementation, describe the project as “UW API + LLM + dashboard.” If this captures most of the product, reject or redesign it. Identify the meaningful system layer between UW data and the user outcome.

For each major feature, check whether UW already provides substantially the same capability. Remove duplicates, transform them into a harder workflow, combine them with other UW data to make a new capability, or use the existing UW feature as evidence within a larger system. Cite the official product or endpoint checked and mark any unverified comparison as unknown.

### Technical depth without component collecting

Increase depth only when the problem creates a real requirement: normalization, event correlation, historical evaluation, optimization, stateful monitoring, constraint solving, anomaly detection, replanning, verification, reconciliation, recovery, streaming, structured AI reasoning, tool orchestration, evaluation, auditability or reproducible evidence. For each component, state the behavior lost if it is removed. Do not add complexity that exists only to decorate an architecture diagram.

### Competitive reassessment checkpoints

At 20%, 35%, 50%, 65%, 80% and 90% completion, pause and record:

1. Is the concept still competitive based on current evidence?
2. Is the hardest promise implemented and demonstrable?
3. Is UW indispensable to the implemented workflow?
4. Is AI doing meaningful work?
5. Is the system deeper than a normal API wrapper?
6. Is the demo becoming stronger?
7. Have competitors or UW product research revealed a better pattern?
8. Is there a higher-value capability that should replace lower-value work?
9. What would a strong technical judge criticize?
10. What might a non-technical judge fail to understand?
11. What evidence is still missing?

If the project is becoming an ordinary dashboard, chatbot or alert feed, pivot before polishing. Save each checkpoint in a short dated note so the reassessment is auditable.

### Final judge simulation

Run three reviews before submission:

- **Technical judge:** “Is there real engineering here?”
- **Product judge:** “Does this solve a problem worth solving?”
- **Hackathon judge:** “Why should I remember this among many UW API projects?”

The submission is not ready if the last answer is unclear. Record the strongest criticism, then fix the highest-value issue that is feasible before the deadline. The goal is to maximize competitive factors truthfully, not to promise or predict a win.

## Required Codex progress and finish report

At meaningful milestones, report the highest-value finding, evidence, current gate status, and next engineering action. Keep updates concise; continue implementation after analysis. At completion, report:

- the user problem and shipped capability;
- hardest promise and its verified behavior;
- AI and sponsor roles in the actual code path;
- evidence/evaluation and failure behavior;
- what is real, simulated, planned or unknown;
- tests/builds actually run and their exact outcomes;
- deployed/repository/submission links and any outstanding blocker;
- remaining competitive weakness, if any.

Do not claim the hackathon submission is complete until the required form has actually been submitted and its confirmation recorded.
