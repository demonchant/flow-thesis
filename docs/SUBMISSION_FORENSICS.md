# Submission forensics

## Evidence reviewed

Inspected RecallReady's README, `docs/ARCHITECTURE.md`, `docs/DEMO_SCRIPT.md`, `docs/SUBMISSION.md`, `hackathon.md`, package manifest and selected source/test files; Parallel's build log/package/schema/test inventory; PlusOne's README, product brief, build log, package/schema/workflows and Firecrawl evaluation docs; OurSpaces public README/build log; and the official event page.

## What is easy to understand

- **RecallReady:** strong problem statement; unusually clear input-to-alert workflow; safety boundary and demo-vs-live distinction; setup, test commands, live URL, demo link and sponsor map are surfaced. But `SUBMISSION.md` still marks social post and submission pending. Archive content cannot prove the final Vibe Apps form was sent.
- **Parallel:** build log acts as a technical map and gives a fast judge path, live boards, demo link and a detailed verified-run account. It also discloses simulated conference attendance/replies. It links extensive tests and the relevant implementation files. Density is a risk: a judge needs a short front door before the deep log.
- **PlusOne:** product and culture/context are well described; market/research/evaluation material exists; exact workflow and user approval boundaries are documented. `PRODUCT.md` contains extensive spec and evidence labels. A test command is absent from package scripts and no test files appeared in this archive's entry list.
- **OurSpaces:** README has a one-line explanation, live link, short video, one-minute click path, stack, component roles, schema/query table, and sponsor descriptions. It is strong reviewer orientation. Current README and historical `hackathon.md` counts/features differ, so a commit pin is needed to reconcile claims. Full source and test inventory were not available in this review.

## What a judge can verify quickly

Best proof patterns include: live app plus second client, real inbound email, source-backed result, immutable/reproducible run record, visible state transition, targeted reliability route/tests, data/source provenance, and a short demo. Parallel's evidence board and attack route are a particularly direct bridge from claim to mechanism. RecallReady's source architecture and code demonstrate meaningful foundations; its ongoing-monitor claim is contradicted by the empty cron module.

## Claims that need qualification

- README and build logs prove that a claim was made, not that production behavior still works.
- Social counts stated in the conversation are **UNKNOWN** to this review; no screenshots/platform record were in the inspected archive.
- Parallel's real emails and provider webhook are claimed in the log; its conference attendance/takeaways are explicitly simulated. Preserve that distinction.
- RecallReady's `SUBMISSION.md` describes successful production integrations but keeps final form/social completion unchecked. The artifact does not resolve the contradiction.
- OurSpaces' current counts and integration depth are README claims, not code-verified in this workspace.
- A passing local build/test report is not equivalent to a clean reviewer setup or current deployed proof.

## Submission pattern to reuse

At repository root, provide one reviewer landing page that answers: What is it? Who is it for? What exact path should I try? Which operations are live versus simulated? What technical capability is hardest? Where is source/evidence? How do I run it? How do I reproduce the key test?

Keep `hackathon.md` short enough to scan: outcome, stack roles, live app, short demo, start date, one core architecture, test command, and links to detailed evidence. Pin submission claims to a release/commit. Add a “known limits” section. Make public routes safe to open without secrets or invitations.

## Final reviewer trust checklist

- Public repo/deployment/video all resolve from a cold browser.
- README and root build log do not contradict the actual commit.
- Sponsor action is linked to the code path that performs it.
- Demo says what is synthetic and shows real postconditions.
- Setup works from a clean environment using documented commands.
- Tests cover failure behavior tied to the central claim.
- Deployment health and seeded demo are reproducible/resettable.
- Final submission status is factual and backed by a receipt/URL; no “pending” checklist remains after cutoff.
- Security/privacy boundary and limitations are explicit.
