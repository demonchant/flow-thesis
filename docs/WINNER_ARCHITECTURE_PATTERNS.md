# Reusable architecture patterns from the project set

These patterns are supported by the inspected RecallReady and Parallel ZIPs, PlusOne ZIP, public OurSpaces README, and official rubric. OurSpaces code and demo were not locally available, so its pattern evidence is README-level. A pattern is valuable only when it addresses the product's real hidden work.

## A. External event → verify → claim → process → state → verify

- **Purpose:** safely turn a provider webhook/email into durable application state.
- **Observed in:** RecallReady and Parallel; PlusOne has explicit signature verification and a first-touch idempotent claim. OurSpaces README describes inbound dedup.
- **Architecture:** verify signature + timestamp → parse/validate minimal envelope → claim unique provider event in transaction → acknowledge quickly → process through internal action/workflow → persist outcome/error → independently show resulting state.
- **Use when:** providers retry, operations have side effects, and event delivery can duplicate or arrive out of order.
- **Do not use when:** no external events exist; a simple authenticated mutation is enough.
- **Requirements:** stable external ID, idempotent mutation, bounded processing, auth at boundaries, explicit failed/pending state, no secret in browser.
- **Failure modes:** accepting unsigned payloads; dedup on a non-unique field; returning success before durable claim; side effect succeeds but status write fails.
- **Tests:** replay; invalid signature; stale timestamp; malformed payload; concurrent duplicate; provider timeout; retry after partial success.
- **Demo:** show a real event once, replay it, show one resulting record and a clear duplicate outcome.
- **Hackathon value:** immediately visible integration depth and reliability.

## B. Unstructured external data → structured record → deterministic decision → provenance

- **Purpose:** transform webpage/email/PDF content into action-safe product state.
- **Observed in:** all four concepts: recall extraction/matching, conference agenda/session scoring, vendor search/quotes, and OurSpaces link/email filing.
- **Architecture:** fetch and retain source identity/time/hash → schema-constrained extraction → deterministic validation/normalization → decision engine → save source refs and decision reasons.
- **Use when:** the source is unstructured but the outcome must be auditable.
- **Do not use when:** API already supplies trustworthy structured fields or LLM adds no value.
- **Requirements:** schema, validation, normalization, provenance, uncertainty path, versioned fixtures.
- **Failure modes:** hallucinated fields, stale page, lost timezone/currency, hidden source truncation, wrong entity attribution.
- **Tests:** adversarial source fixtures, schema violations, normalization edges, exact evidence verification, duplicate import.
- **Demo:** point from outcome to the exact source line/field and explain what deterministic code decided.
- **Hackathon value:** AI is visible but bounded; sponsor data capability participates in core workflow.

## C. AI proposal → deterministic guard → explicit authorization → side effect

- **Purpose:** let AI prepare useful actions without giving it unsafe authority.
- **Observed in:** PlusOne vendor emails require review; Parallel email reply actions require confidence/state guards; RecallReady lets AI extract but deterministic matching controls the alert.
- **Architecture:** model returns typed proposal → validate against current data, permissions and constraints → show preview/reasons → human confirms when external or consequential → idempotent execution → persist provider receipt/state.
- **Use when:** actions send messages, change money/schedules, or could harm trust.
- **Do not use when:** action is reversible, low impact, and deterministic; do not add a human click to every harmless read.
- **Failure modes:** prompt injection in source content; stale proposal; duplicate execution; authorization bypass; confirmation not tied to exact proposed payload.
- **Tests:** malicious input, changed source/current state, duplicate click, wrong role, provider failure, proposal tampering.
- **Demo:** show proposal, one concise validation reason, approve, then provider/state evidence.
- **Hackathon value:** makes AI competence and safety equally legible.

## D. Goal + constraints → deterministic optimizer → explainable plan

- **Purpose:** allocate scarce resources where choices interact.
- **Observed in:** Parallel's unique contribution: weighted goal coverage, duplicate attendance penalty, preferences, pins, conflicts, and repair-change penalty.
- **Architecture:** normalize inputs → hard feasibility checks → explicit objective → deterministic exact search when within bound, bounded fallback otherwise → persist solution status/objective/bound → explain assignments.
- **Use when:** local greedy choices cause globally worse outcomes and a measurable objective exists.
- **Do not use when:** one rule or ranking is enough; avoid naming heuristics an optimizer without objective/invariant proof.
- **Requirements:** declared constraints, objective weights, complexity bound, infeasible result, deterministic tie behavior, benchmark/reference solver.
- **Failure modes:** objective gaming, bad weights, false “optimal” label after budget exhaustion, missing edge cases, unexplainable outcomes.
- **Tests:** tiny cases checked against brute force; randomized invariants; pins/time conflicts; infeasible cases; determinism; compute budget exhaustion.
- **Demo:** compare baseline and planned objective, reveal constraints, change one fact, show repair and preserved invariants.
- **Hackathon value:** high technical differentiation when the user's problem truly requires coordination/optimization.

## E. Plan → execute → observe → compare → replan

- **Purpose:** handle an environment that changes after an initial plan.
- **Observed in:** Parallel agenda revisions, stale-plan guard, disruption detection and repair; PlusOne scheduled follow-up is a simpler monitoring loop.
- **Architecture:** persist plan revision → execute actions linked to revision → observe provider/user event → compare current constraints vs plan → mark stale → compute minimal safe repair → request consent if needed → publish new revision.
- **Use when:** external state can invalidate previous work and automatic correction has user value.
- **Do not use when:** environment is static or replan would be cosmetic.
- **Failure modes:** overwriting user edits; applying repair to stale revision; oscillation; losing accepted state; silently dropping a required item.
- **Tests:** stale write, duplicate event, concurrent edits, changed constraint, no feasible solution, repair minimality.
- **Demo:** make one realistic disruption; visibly mark old plan stale; repair; show preserved assignments and changed score.
- **Hackathon value:** a concise, memorable proof of stateful technical depth.

## F. Durable workflow → bounded fan-out → visible partial progress

- **Purpose:** run multi-step integration work reliably while results arrive at different times.
- **Observed in:** Parallel agenda import/scoring fan-out and PlusOne vendor research batches/workflows; OurSpaces README describes workpool/workflow/queues.
- **Architecture:** create run record → process idempotent steps → bounded retries and concurrency → checkpoint outputs → progress subscription → finish/partial/fail state.
- **Use when:** the task is long or has independent work whose progress matters.
- **Do not use when:** a short action fits one transaction/action.
- **Failure modes:** retrying a non-idempotent call, indefinite loops, unbounded fan-out, stale progress, hiding partial failure.
- **Tests:** crash between steps; retry; timeout; rate limiting; partial batch; duplicate run; concurrency limit.
- **Demo:** show actual streamed progress and one recovery/partial result path.
- **Hackathon value:** supports genuine integration depth and reliable demos.

## G. Grounded synthesis → citation check → delivery

- **Purpose:** summarize collected notes into useful output without invented claims.
- **Observed in:** Parallel brief path; RecallReady's evidence-backed alert view is a narrower deterministic version.
- **Architecture:** retrieve approved source records → generate typed claims with references → validate each reference against input set → reject unsupported claims → persist draft → user confirms recipients/send → store delivery result.
- **Use when:** output is derived from multiple sources and someone will rely on it.
- **Do not use when:** answer is a direct deterministic lookup.
- **Failure modes:** unsupported citations, source drift, omitted negative findings, delivery mismatch.
- **Tests:** fabricated source IDs, paraphrase not grounded, empty/low-substance input, wrong recipient, repeated send.
- **Demo:** click a claim and expose its actual source; show unsupported output rejected.
- **Hackathon value:** turns AI text into auditable product value.

## H. Persistent collaborative state → realtime subscriptions → conflict policy

- **Purpose:** give multiple users one current shared view.
- **Observed in:** RecallReady households, Parallel conference boards, PlusOne collaborative wedding work, and OurSpaces' core product.
- **Architecture:** normalized indexed records → authenticated/scoped read-write functions → transactional updates → subscriptions → explicit edit/claim/revision policy for conflicts.
- **Use when:** collaboration itself changes the outcome or coordination cost.
- **Do not use when:** single-user ephemeral output; no realtime stack for appearance.
- **Failure modes:** client-side ownership trust, blind overwrite, optimistic UI without refusal handling, stale cache duplication.
- **Tests:** cross-tenant access, concurrent writes, rejected optimistic update, reconnect/reload consistency.
- **Demo:** two real browser sessions; one writes, the second updates; then show a conflict guard.
- **Hackathon value:** judges can see Convex's backend capability doing product work.

## Pattern selection rule

Choose the smallest pattern set that completely covers the core user outcome. Combining webhook ingestion + structured extraction + deterministic decision + durable monitoring is appropriate for RecallReady. Adding an optimizer, RAG, or multiple agents is not justified unless the safety product acquires a real constrained planning task.
