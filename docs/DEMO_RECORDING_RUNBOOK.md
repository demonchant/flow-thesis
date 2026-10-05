# Live screen recording runbook

This records the actual live, read-only UW workflow in Flow Thesis Ledger. It does not require OpenAI credit: use **No-cost deterministic rules**. The OpenAI compiler remains available as a separate option, but this recording must not imply that it ran.

## Before recording

1. Start in the PowerShell window where `UW_API_KEY` is already available. Never type, display, or capture the key. OpenAI is not required for this path.
2. From the project folder, check only whether UW is configured:

   ```powershell
   if ($env:UW_API_KEY) { 'UW_API_KEY is available' } else { 'UW_API_KEY is missing' }
   ```

3. Start the app with a fresh local database for a clean, truthful recording:

   ```powershell
   $demoDb = ".local\recording-$((Get-Date).ToString('yyyyMMdd-HHmmss')).sqlite3"
   python -m flow_thesis_ledger.live_web --db $demoDb
   ```

   Leave this PowerShell window running. It should show the localhost URL and that credentials stay in the server process. Do not show environment values.

4. Start screen recording. Capture the app, not the desktop or notification tray. If showing PowerShell at the start, frame only the command and safe startup messages.
5. Open `http://127.0.0.1:8766` and refresh once. Use a browser window without personal bookmarks, account identifiers, or unrelated tabs.
6. If UW currently returns no alerts, stop and retry later. The Replay page only shows live UW alerts saved in the local ledger; it has no example-data fallback.

## What to enter

On **New thesis**:

- Click **Load tickers from UW**.
- Choose a ticker shown in the returned live ticker list. Do not assume a particular symbol: availability changes. Use `QQQ` or `IWM` only if that exact symbol appears in the list now.
- Select **No-cost deterministic rules**.
- Leave the threshold at `100000` USD (or enter `100000` if blank).
- Paste this monitoring statement, replacing `TICKER` with the selected symbol:

  > For TICKER, evaluate live Flow Alert total premium against my explicit $100,000 threshold. Treat total premium and the alert's recorded underlying price as observations only. Do not infer trade direction or predict future price movement. Mark the result indeterminate when required evidence is missing, stale, or incomplete.

- Click **Fetch UW evidence and compile draft** once. Wait for the progress display to finish. Do not double-click or refresh while a job is running.

## Recording sequence and narration

Aim for about 90 seconds. Speak at an even pace; allow the live request to finish rather than speeding up or hiding a long delay with a false result.

| Time | What you do/show | Voiceover |
|---|---|---|
| 0:00–0:08 | Show PowerShell startup safely, then open the local app overview. | “This is Flow Thesis Ledger, a live, read-only monitor for options-flow evidence. The UW key stays in the server process; the browser never receives it.” |
| 0:08–0:17 | Pause on the overview: heading, motion graphic, and short explanation. | “The goal is not to predict where a ticker goes. It is to test a condition I chose against observations from Unusual Whales, and keep a record of why the result changed.” |
| 0:17–0:25 | Let the animated evidence path remain visible. | “The moving diagram shows the path: live Flow Alerts become typed evidence, enter the local ledger, and are checked by deterministic rules.” |
| 0:25–0:38 | New thesis; load ticker list; choose one actually returned. Show count briefly. | “I load the available tickers from the live feed and choose one the account actually returned.” |
| 0:38–0:52 | Show deterministic mode, `$100000`, and the statement. | “I set an explicit one-hundred-thousand-dollar total-premium threshold. The no-cost compiler turns that threshold into support and weakening conditions; it makes no OpenAI request and does not guess what I meant.” |
| 0:52–1:05 | Click fetch once; keep progress in frame while it runs. | “Now the server requests current Flow Alerts, normalizes the returned fields, stores matching observations, creates a draft, and evaluates it. No sample event is substituted.” |
| 1:05–1:16 | Show the draft conditions, result, and evidence/source references. | “The underlying price is only the value recorded with that alert. Missing, stale, or incomplete evidence remains indeterminate.” |
| 1:16–1:25 | Check the explicit approval box and approve read-only monitoring. | “I review the draft before approving read-only monitoring. This product cannot place trades.” |
| 1:25–1:37 | Open Evidence and click **Poll UW now** once. Wait, then show returned count/result. | “The evidence view lets me poll the live feed and inspect the ledger result. I show the state and counts returned by this run; I do not stage a market event.” |
| 1:37–1:50 | Open **Replay**. Show the `LIVE UW LEDGER` badge, real event count, move the slider one position, and point to the source event, recorded time, recomputed state, and receipt hash. | “Replay steps through the actual UW alerts saved for this thesis, in event-time order. At each point, the deterministic evaluator recomputes the result and shows the source event and receipt.” |
| 1:50–1:57 | End on a real replay step or the Evidence result. | “Flow Thesis Ledger turns live market observations into a reviewable evidence trail. It does not predict price or place trades.” |

## Live behavior rules

- Replay reads only actual UW observations already saved for the current thesis. If there are none, it displays an empty state and does not load a sample.
- A ticker with no matching live alert should show the app's real empty/error state. You can return and select another ticker from the live list; do not invent or paste an alert.
- A live result may be `indeterminate`. That is a valid and honest outcome when a required value is missing, stale, or incomplete.
- Polling may return zero new events. Say that it found no new alert; do not claim a transition.
- Replay recomputes state after each saved live alert in event-time order. It does not claim the API delivered a new event during playback; show transitions only when the underlying observations produce them.
- Do not expose raw API payloads, credentials, account data, browser devtools, or local database contents. Show the product's curated evidence fields and counts.
- If the UI reports **Job not found**, stop recording, refresh the page once, restart the app from the same credential-bearing PowerShell session with a new database path, and begin again. Do not narrate a failed run as successful.

## After recording

Save the original screen capture as MP4 and attach it in this conversation. I can then align the narration, captions, animated callouts, and transitions to the actual timings and return the edited video. The current animated evidence-path graphic is already in the app; the final edit can add restrained overlays over the real capture.

Keep the original capture and avoid uploading public real-data footage until the applicable UW terms permit redistribution of the displayed data. Never include secrets in the recording or submission.
