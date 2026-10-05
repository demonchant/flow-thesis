# Demo video edit

The submission demo is rendered from the real `1.mp4` screen capture. The edit uses an animated title, restrained push-ins, animated section cards, transition swishes, ElevenLabs narration, and a quiet original synthesized music bed. It cuts the old in-flight and restart-notice footage. The app capture is cropped to keep the interface readable and omit transient bottom toasts.

Run from PowerShell in the repository root: `python scripts/render_demo_video.py`. The script reads `ELEVENLABS_API_KEY` from the process environment, sends it only in ElevenLabs' `xi-api-key` header, and does not print or persist it. It writes `artifacts/flow-thesis-demo.mp4`. Keep the raw capture and all credentials out of Git.

Narration is in `artifacts/flow-thesis-demo-narration.txt`. The walkthrough describes only visible application behavior: live UW observations, explicit rule evaluation, inspectable evidence, and replay of saved live events.
