# Live demo voiceover and shot list

Use this script only after a live run succeeds with rotated credentials. Record the app responding to actual UW Flow Alerts and a successful OpenAI draft. Do not use the synthetic replay as if it were live, and do not edit values to imply a real state transition.

## Preflight

1. Start `python -m flow_thesis_ledger.live_web` in the PowerShell process that has the rotated `UW_API_KEY` and `OPENAI_API_KEY` environment variables.
2. Open `http://127.0.0.1:8766` and choose a ticker that currently has at least one Flow Alert available to this UW account.
3. Confirm the live fetch, draft generation, underlying reference price, and initial deterministic evaluation all succeed before recording.
4. Keep the raw provider feed and credentials out of view. The video should show the app’s normalized evidence and should be shared only in a way permitted by UW’s data terms.
5. If UW has no matching alert, OpenAI generation fails, or the result is indeterminate, stop and explain the actual result. Do not cut to synthetic replay as though it were the live event.

## Shot list and voiceover

Target length: 65–85 seconds. Keep the cursor still while the viewer reads each state. Use gentle cuts and a restrained zoom toward the real state/evidence fields; do not add fabricated market values, generated ticker data, or a simulated state change.

| Time | Screen action | Voiceover |
|---|---|---|
| 0–8s | Overview screen, show the product title and workflow illustration. | “Options flow is evidence, not a conclusion. Flow Thesis Ledger tests a stated thesis against live Unusual Whales Flow Alerts.” |
| 8–18s | Open New Thesis. Enter a ticker with a current alert and a user-defined, measurable thesis. | “I enter a ticker and describe the conditions I want to evaluate.” |
| 18–34s | Submit; show progress, then the AI summary, proposed conditions, uncertainty notes, and draft status. | “The app retrieves the live alert, normalizes and stores its fields, and shows the underlying reference price recorded with that alert. OpenAI proposes structured rules and states what remains uncertain.” |
| 34–45s | Slowly show a condition and the source/evidence reference. | “The proposal is validated as a draft. It cannot place a trade, and the model does not decide the thesis outcome.” |
| 45–55s | Tick the explicit review box, approve read-only monitoring, and show the status change. | “After reviewing the rules, I explicitly approve read-only monitoring.” |
| 55–72s | Open Evidence, click Poll UW now, then show the actual evaluation, predicate results, timestamps, and receipt hashes. | “A poll checks for new observations, avoids duplicate records, and evaluates the stored evidence with deterministic rules. The receipt makes the inputs and result traceable.” |
| 72–82s | End on the actual app state and evidence table. | “You can see what the available evidence supports, what it does not, and when it is incomplete. Flow Thesis Ledger is an evidence monitor—not a price prediction or trading bot.” |

## Editing notes

- Use the real browser recording as the base video. Add the voiceover above it, trim pauses, and use subtle zooms to direct attention to actual UI details.
- Add captions from the voiceover transcript. Use short labels such as “Live UW alert”, “Underlying at alert”, “AI draft”, “Human approval”, and “Deterministic evaluation” only when those elements are actually visible.
- Keep timestamps and state labels legible. Do not overlay a different price or ticker than the one in the recording.
- The app currently shows the underlying reference price carried in the UW alert. It is not a separately fetched real-time quote.
- The contest requires a short demo video/GIF or screenshots, a project description, endpoints, run steps, and the repository link. Post the repository and demo in the specified Unusual Whales hackathon forum thread.
