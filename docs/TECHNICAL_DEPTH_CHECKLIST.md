# Technical depth checklist

Complete this before substantial code, then revisit immediately after the first working vertical slice. A short answer is acceptable only if backed by a concrete example.

## Product and hard problem

- What exact user outcome should happen?
- What appears simple to the user but is technically difficult underneath?
- What makes the problem non-trivial: data quality, constraints, concurrency, uncertainty, external change, or side effects?
- Which system capability materially differentiates the product?
- What can be cut without weakening that core capability?

## State and workflow

- What state exists? Which records are canonical and which are derived?
- Which user, model, provider event, cron or workflow step changes it?
- What are the valid states/transitions and who can make each transition?
- Which state survives process restart/reload?
- Are revisions or version checks required to reject stale writes?
- Is work short/transactional or long/durable? Why is the chosen workflow primitive appropriate?
- Are retries, queues, fan-out, cron or presence genuinely needed by observed work?

## AI and tools

- What does the model receive, including provenance and untrusted content boundaries?
- What typed output does it produce?
- What decision is allowed to depend on that output?
- What tools can it select/call, and what is the least privilege for each?
- What happens when output is incomplete, invalid, wrong, ambiguous or prompt-injected?
- Which checks remain deterministic?
- Can the model/tool result change external state? Where is explicit user approval needed?
- What evaluation fixtures demonstrate quality and regressions?

## Integrations

- What real capability does each external/sponsor system add?
- What input does it receive and what result changes product state?
- Is the integration core, important, supporting or decorative?
- What would materially break if it were removed?
- How are credentials stored, requests authenticated, sources attributed and outputs validated?
- What if the provider times out, rate-limits, changes shape, duplicates an event, or succeeds while our status write fails?

## Reliability and safety

- Is every externally triggered side effect idempotent?
- What is the operation's stable idempotency key?
- Can concurrent workers create conflicts or duplicate sends?
- How is stale data detected and reconciled?
- What is retried, what is not, and what is escalated to a human?
- Can a failed refresh be mistaken for “no issue” or “success”?
- Is there an audit trail connecting intent → execution → external response → verified postcondition?
- Are tenant access, role checks, input bounds, privacy and secret handling enforced server-side?

## Depth review: make it deeper only when value rises

Try the following questions in order; stop at the first level that solves the user's real problem:

1. Can the system preserve meaningful state?
2. Can it reason over explicit constraints instead of prompting vaguely?
3. Can it plan a sequence before acting?
4. Can it use a tool and inspect the result?
5. Can it observe an external/user change and replan?
6. Can it verify the postcondition independently?
7. Can it recover from duplicate delivery, timeout, crash, stale state or concurrency?
8. Can it produce an auditable/evaluable record?
9. Can multiple actors collaborate under a clear permission/conflict model?
10. Is optimization/multi-agent/distributed execution genuinely needed?

Do not jump to item 10 for appearance. For RecallReady, recurring source ingestion and safe matching are natural depth; multi-agent orchestration is not.

## Evidence questions

- What exact test proves the core invariant?
- What failure injection proves recovery?
- What independent source/postcondition proves external success?
- Can a clean checkout reproduce the demo state?
- Can a reviewer connect the output to code and source evidence?
- Are simulated behavior and live behavior labeled distinctly?

If answers to state, AI authority, failure, verification and evidence are vague, pause feature work and redesign the vertical slice.
