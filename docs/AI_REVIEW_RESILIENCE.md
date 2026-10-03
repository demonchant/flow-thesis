# AI review resilience

## Goal

Make a repository legible to an automated first-pass reviewer without hiding limits or stuffing it with judge-directed slogans. A legitimate reviewer should be able to map each claim to code, tests, deployment and demo evidence.

## What an AI reviewer can reliably extract

From a clean repository it can usually identify:

1. Product purpose and user from README/product brief.
2. Runtime stack and commands from manifests/config.
3. Convex tables/indexes/functions and API boundaries from `convex/`.
4. Model/provider use and structured schemas from action files.
5. Sponsor use only if integration code is connected to a product path.
6. Test architecture from test files/scripts, though not whether tests pass unless executed.
7. Deployment claims from build log/links, though not current health.
8. Simulation boundaries only if explicitly labeled.

It cannot establish current live behavior, private submission-form completion, social engagement, actual external side effects, or test success from prose alone.

## Findings in this dataset

- **RecallReady:** high discoverability: README, architecture, submission copy, demo script and build log align on the intended product path. Source inspection finds the important mismatch: empty `crons.ts` vs “keeps watching” language. The exact match utility/tests and signed webhook are easy to locate. Submission state is ambiguous because checkboxes are pending.
- **Parallel:** very high proof discoverability: root build log maps criteria to files, numbers and an explicit judge route. The log distinguishes actual email interactions from played-out conference activity and calls out placeholder participants. There are many test directories; reviewers can locate adversarial coverage by name. Ensure a compact summary appears before a long build log.
- **PlusOne:** architecture and product boundaries are explicit; Firecrawl measurement includes raw JSON and scripts, a strong reproducibility affordance. Repository has no standard test script/test files in the archive, which an automated reviewer can interpret as a verification weakness even though empirical evaluation scripts exist.
- **OurSpaces:** current README gives an unusually broad explicit component map and realtime-query map. README/build-log version drift may cause a reviewer to distrust counts. Local source/test verification is outstanding.

## Repository design rules

- Put a literal “Run locally” and “Verify” section in the first screenful of README.
- Maintain a table `claim → implementation path → test/evidence → demo timestamp → status`.
- Use explicit terms `live`, `fixture`, `simulated`, `planned`, `verified` consistently.
- Pin factual totals to the inspected commit. Do not leave obsolete function/table/component counts in a current README.
- Name tests after behavior and failure mode; link key tests near the claim.
- Put API keys in environment configuration, include a safe `.env.example`, and prove secrets are absent from history/bundle.
- Describe sponsor capability in a sentence tied to an input and persisted output.
- Include test/build/seed/reset commands that do not depend on undocumented production credentials.
- Provide a non-secret demo route that uses clearly labeled fixtures if a live integration is unavailable.
- Include architecture diagram and table/state transition summary; no diagram should imply an unimplemented scheduled/agent path.
- Document operational limits: rate limits, retries, source freshness, auth model, demo/live differences.
- Keep `hackathon.md` complete and consistent with root README and deployment.

## Machine-readable evidence

Where useful, save fixtures and JSON run reports with fields such as:

```json
{
  "runId": "stable-demo-run-id",
  "commit": "git-sha",
  "inputFixture": "fixtures/notice-17.json",
  "sourceUrl": "https://authority.example/notice/17",
  "modelVersion": "recorded-model",
  "schemaVersion": 2,
  "decision": "review",
  "reasonCodes": ["model_identifier_partial"],
  "expected": "review",
  "observed": "review"
}
```

Use real data only when allowed and scrub personal information. Machine-readable records improve reproducibility; they do not replace clear prose or a real demo.

## Final AI-first-pass self-test

Ask a fresh reviewer (human or model) to answer, using only repository files: what works, what is simulated, where each sponsor is used, how to run it, which test proves the central claim, what fails safely, and what is still incomplete. If any answer is guessed, fix documentation or implementation evidence. Do not prompt-inject, hide contradictory files, or claim unsupported results.
