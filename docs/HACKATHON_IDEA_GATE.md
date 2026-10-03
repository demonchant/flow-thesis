# Pre-build idea gate

Use this before implementing the product. It is an internal go/no-go tool, not a prediction of judging outcome.

## Rating anchors

Score each dimension from 0 to 4 using the strongest evidence available:

- **0 — absent:** no concrete answer.
- **1 — assertion:** appealing pitch, but mechanism/user evidence is mostly guessed.
- **2 — designed:** named user, real workflow, and a technically plausible approach with known dependencies.
- **3 — evidenced:** primary rules/docs/source/user evidence supports the problem and integrations; risks and demo path are identified.
- **4 — validated:** a short research/spike or direct user/source evidence has tested the riskiest assumption; proof artifact exists.

Do not score a plan as a 4 merely because it sounds detailed. Record a one-line evidence pointer or uncertainty for every score. Maximum: 64. Re-score after a vertical slice and during final review; do not compare the raw score between unrelated hackathons as if it were an objective win probability.

## Dimensions (16)

| Dimension | Score 0–4 by answering |
|---|---|
| Problem strength | Is there a specific recurring/high-consequence problem and a named user? |
| User value | Does a successful result save time, risk, money, or coordination in a way the user can recognize immediately? |
| Technical depth | Is the hard work intrinsic to the outcome (constraints, extraction, state, matching, optimization, recovery)? |
| AI necessity | Is there ambiguous/unstructured cognitive work that code alone handles poorly? |
| Agentic potential | Does the user benefit from tool choice, result inspection, multi-step execution, or adaptation? |
| Statefulness | Does useful state persist/change over time or across actors? |
| Integration depth | Do external systems enable actual input/action in the core workflow? |
| Sponsor indispensability | Would removing the required sponsor capability materially weaken/break/change the product? |
| Technical novelty | Is the combination/algorithm/workflow differentiated and explainable, beyond an AI wrapper? |
| Demoability | Can the central mechanism be shown in under 3 minutes without faking it? |
| Proof potential | Can results be independently checked through sources, postconditions, tests, logs or receipts? |
| Failure/recovery potential | Is there a realistic failure/change case and a useful recovery path to demonstrate? |
| Repository quality | Can the implementation be documented, tested and reproduced with the time/team available? |
| Submission clarity | Can a cold reviewer find product, live URL, evidence, sponsor paths and demo quickly? |
| Time feasibility | Can a narrow end-to-end outcome plus evidence be completed before cutoff? |
| Competitive differentiation | Does the idea stand apart from obvious copycats and fit the actual rubric? |

## Decision thresholds

- **Go:** at least **40/64**, and no score below 2 for problem strength, user value, technical depth, sponsor indispensability when sponsor use is required, proof potential, demoability, and time feasibility.
- **Redesign:** **32–39**, or any mandatory floor missed. Change the problem slice/architecture until the weak dimension has a credible mechanism. Re-score.
- **Stop/pivot:** below **32**, or a central dependency/eligibility rule is impossible to satisfy within the time. Do not rescue the idea with polish or unrelated APIs.

Why these thresholds: scores 0–1 mean there is no evidence-backed design; the mandatory floors require at least a concrete mechanism in every category that can cause project failure. A 40 total asks for an average above “designed” across dimensions without pretending this number has statistical calibration. It is a disciplined conversation aid, not a claim about winning odds. If the event does not require a particular sponsor, score indispensability against the core product integration instead.

## Gate worksheet

```text
Idea:
User and painful moment:
One-sentence useful outcome:
Hardest technical problem:
AI input → typed output → bounded decision:
External/sponsor system's indispensable job:
State that persists and changes:
One failure and recovery path:
Independent proof:
3-minute demo sequence:
Riskiest assumption + 30-minute validation:
Time-boxed core build and cut line:

Scores (0–4, with evidence/unknown per row):
Problem __  User value __  Depth __  AI __  Agent __  State __
Integration __  Sponsor __  Novelty __  Demo __  Proof __  Recovery __
Repo __  Submission __  Time __  Differentiation __
Total __ / 64; floors pass? __; decision: Go / Redesign / Stop
```

## Evidence checklist before passing

- Read complete rules, disqualification/eligibility, exact submission form, rubric, sponsor docs and API docs.
- Check whether the idea is a permitted “new app” and whether the required AI/Convex/sponsor pieces are mandatory.
- Inspect 2–5 comparable products/submissions at source/demo level where possible; record unknowns.
- Validate API availability, price/rate limits, auth needs, deployment and data rights with a minimal spike.
- Write the critical path and failure path before UI scope.
- Reject the idea if its strongest technical claim has no possible test or demo proof.
