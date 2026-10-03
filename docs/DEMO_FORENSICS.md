# Demo forensics

## Evidence and limits

Demo scripts, named video links, build-log claims and the local RecallReady MP4 were located. The videos themselves were not visually or acoustically reviewed here. Therefore timing, narration, music, transitions and exact screen movements are **UNKNOWN** unless the repository documents them. Do not attribute ElevenLabs, AI voice, music, or editing software without direct media/metadata evidence.

## What the materials establish

| Project | Confirmed from materials | Not independently confirmed |
|---|---|---|
| RecallReady | `docs/DEMO_SCRIPT.md` targets 2:40 and calls for a real AgentMail receipt, extraction, live inventory, Firecrawl check, source evidence, alert, resolution, and activity history. `docs/SUBMISSION.md` says its exported video is 2:20. | Actual cut/order, voiceover quality, music, transitions, whether live network succeeds in recording, actual MP4 duration/contents. |
| Parallel | `hackathon.md` links a 2:40 demo and specifies a 60-second judge path with live board, demo run, email, two-tab realtime update, and adversarial attacks. | Video soundtrack, interaction pacing, attack results in the linked clip. |
| PlusOne | README links a three-minute video; repo contains product/screenshots and measured research notes. | Exact film structure, voiceover, music, sponsor calls shown, whether external sends use real recipients. |
| OurSpaces | README links a 2:56 video and a “try it in a minute” flow: two tabs/vote, drag/cursors, email a receipt, paste a link. | Actual clip style/audio, exact latency, whether every described integration is shown in the clip. |

## Strong demonstration mechanisms

The strongest scripts compress a full mechanism into a visible before/action/after sequence. Parallel documents its exceptional technical beat: plan coverage 90.5 → disruption lowers it to 88.8 → accepted cover returns it to 90.5. The repository discloses that its conference activity was played out and some teammates/replies were synthetic; those numbers are run values, not real conference attendance evidence. That qualification belongs in any retelling.

RecallReady's intended demo has an unusually clear human stake, but its documented flow should be updated to show only what the archived production build can actually do. In particular, a manual “Check sources now” is not recurring monitoring. The demo should not imply a scheduled watch until one exists.

OurSpaces' README proposes a crisp multi-surface demo: visible collaboration in two tabs, email-created board content, and a crawled page. That connects product to technical path quickly, though it remains a README description until video/source review.

## Reusable 2:30 proof structure

1. **0:00–0:10 — Problem and stakes:** one user, one painful moment, one sentence.
2. **0:10–0:25 — Starting state:** real or explicitly labeled fixture; show the relevant constraint/state.
3. **0:25–1:05 — Core input:** perform the meaningful action in the running product; identify the external service doing its actual job.
4. **1:05–1:35 — System decision:** reveal structured AI result and deterministic check/plan, not a generic spinner or chatbot answer.
5. **1:35–2:00 — Change/failure:** create one realistic duplicate, changed constraint, source outage, or invalid result; show state transition/recovery.
6. **2:00–2:20 — Verification:** expose source/receipt/event/solver objective/result ID, and show it in a second client or reload.
7. **2:20–2:30 — User outcome:** show what changed for the person; end on a factual product claim.

### Recording rules

- Prefer direct screen capture and real app interaction. Keep every use of fixture/simulated data visibly labeled.
- Use voiceover only to explain a step the viewer is seeing. Music is optional and must not compete with product audio/voice. Do not fabricate a “cinematic” technical moment.
- Avoid spending the first 20 seconds on logo animation. Do not show a wall of dashboards or source code unless a source/trace is the proof.
- Prepare deterministic demo data and a reset path; keep a live fallback if a third-party service is flaky. Label fallback output.
- Use readable zoom, deliberate cursor movement, and one visible technical proof per criterion.
- Finish within the actual rules limit; event-specific limit overrides this template.

## Demo review checklist

- Can a cold viewer restate the problem after 10 seconds?
- Is the first input real or disclosed as a fixture?
- Can the viewer see what AI interpreted and what deterministic logic checked?
- Is sponsor technology visible in the core path, not just a logo?
- Does at least one state transition persist after refresh/reconnect?
- Is any simulated participation or generated content labeled?
- Does the demo show a postcondition, not only a success toast?
- Do all claims, numbers and URLs match the repository and deployed commit?
