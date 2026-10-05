"""Render a polished Flow Thesis Ledger demo from the user's real screen capture.

Reads ELEVENLABS_API_KEY from the process environment. Never prints, saves, or
logs the credential. The input is the real `1.mp4` screen recording.
"""

from __future__ import annotations

import argparse
import io
import math
import os
import subprocess
import sys
import wave
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "1.mp4"
OUT_DIR = ROOT / "artifacts"
VIDEO = OUT_DIR / "flow-thesis-demo.mp4"
VOICE = OUT_DIR / "flow-thesis-elevenlabs.mp3"
MIX = OUT_DIR / "flow-thesis-demo-mix.wav"
SILENT = OUT_DIR / "flow-thesis-demo-silent.mp4"
W, H, FPS = 1280, 720, 30

# Source intervals deliberately skip the old in-flight-operation and restart
# error screens. The crop also omits the persistent bottom toast without
# altering any of the application content being presented.
CLIPS = [
    (0.0, 11.5, "LIVE MARKET EVIDENCE", "Unusual Whales Flow Alerts"),
    (18.0, 33.0, "DEFINE THE MONITORING RULE", "Explicit threshold · deterministic evaluation"),
    (102.0, 115.0, "INSPECT THE EVIDENCE", "Source events · predicates · state transitions"),
    (121.0, 141.0, "REPLAY REAL UW EVENTS", "Recompute state from the saved live ledger"),
]
NARRATION = (
    "Market data is easy to display. The harder question is whether new evidence still meets a rule. "
    "Flow Thesis Ledger connects to Unusual Whales, normalizes live Flow Alerts, and stores each observation. "
    "A thesis starts with an explicit monitoring condition. Here, the ledger evaluates each alert with deterministic rules and records the resulting state. "
    "The evidence view exposes source observations, predicate checks, state transitions, and a reproducibility receipt. "
    "Replay then walks the actual saved Unusual Whales events in time order and recomputes the state at each step. "
    "The system is read only: it observes, evaluates, and explains. No trade is placed. "
    "Flow Thesis Ledger turns a stream of market events into a reviewable, auditable monitoring process."
)


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise RuntimeError("The bundled imageio-ffmpeg executable is unavailable.") from exc


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def elevenlabs_voiceover() -> None:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY is not in this PowerShell process. Set it in the "
            "PowerShell session, then run this script again. The key is never requested interactively."
        )
    payload = (
        '{"text":' + __import__("json").dumps(NARRATION, ensure_ascii=False)
        + ',"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.48,'
        '"similarity_boost":0.78,"style":0.18,"use_speaker_boost":true}}'
    ).encode("utf-8")
    req = Request(
        "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb?output_format=mp3_44100_128",
        data=payload,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=90) as response:
            if response.status != 200:
                raise RuntimeError(f"ElevenLabs returned HTTP {response.status}.")
            audio = response.read()
    except HTTPError as exc:
        # Deliberately omit response body: providers can echo request context.
        raise RuntimeError(f"ElevenLabs voice generation returned HTTP {exc.code}.") from None
    except URLError:
        raise RuntimeError("Could not reach ElevenLabs. Check network access and retry.") from None
    if not audio.startswith(b"ID3") and not audio.startswith(b"\xff\xfb"):
        raise RuntimeError("ElevenLabs response was not recognized as MP3 audio.")
    VOICE.write_bytes(audio)
    print("ElevenLabs narration generated; credential was not logged or saved.")


def _overlay(frame: np.ndarray, elapsed: float, total: float, clip_index: int, local_t: float) -> np.ndarray:
    base = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fade = min(1.0, local_t / 0.35, max(0.0, (CLIPS[clip_index][1] - CLIPS[clip_index][0] - local_t) / 0.35))
    alpha = int(240 * fade)
    # Branded animated lower-third, covering the capture's old transient toast.
    d.rounded_rectangle((48, 614, 1232, 700), radius=18, fill=(10, 17, 17, 216))
    d.rounded_rectangle((48, 614, 1232, 700), radius=18, outline=(172, 255, 90, 95), width=1)
    d.rectangle((68, 632, 72 + int(220 * min(1, local_t / 0.7)), 637), fill=(172, 255, 90, alpha))
    d.text((88, 644), CLIPS[clip_index][2], font=_font(21, True), fill=(237, 244, 235, alpha))
    d.text((88, 673), CLIPS[clip_index][3], font=_font(14), fill=(177, 197, 185, alpha))
    # Segment marker animates in from the right on each transition.
    for i in range(len(CLIPS)):
        x = 1138 + i * 22
        r = 5 if i == clip_index else 3
        d.ellipse((x-r, 640-r, x+r, 640+r), fill=(172, 255, 90, alpha if i == clip_index else 95))
    # Subtle progress trace below the card.
    d.rounded_rectangle((48, 710, 1232, 715), radius=2, fill=(225, 235, 225, 70))
    d.rounded_rectangle((48, 710, 48 + int(1184 * min(1.0, elapsed / max(total, 0.1))), 715), radius=2, fill=(172, 255, 90, 230))
    return cv2.cvtColor(np.asarray(Image.alpha_composite(base, layer).convert("RGB")), cv2.COLOR_RGB2BGR)


def render_video() -> float:
    if not SOURCE.exists():
        raise RuntimeError("Place the screen recording at the project root as 1.mp4.")
    cap = cv2.VideoCapture(str(SOURCE))
    if not cap.isOpened():
        raise RuntimeError("Could not open 1.mp4.")
    source_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    source_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    source_fps = cap.get(cv2.CAP_PROP_FPS) or FPS
    # Crop out browser chrome, sidebar and the bottom toast while keeping the
    # actual app panels. Keep crop ratio at exactly 16:9.
    crop_h = min(source_h - 1, 790)
    crop_w = int(crop_h * 16 / 9)
    x0 = max(0, min(source_w - crop_w, 375))
    y0 = 0
    OUT_DIR.mkdir(exist_ok=True)
    writer = cv2.VideoWriter(str(SILENT), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError("Could not initialize video writer.")
    durations = [end - start for start, end, *_ in CLIPS]
    total = sum(durations)
    elapsed = 0.0
    try:
        # Animated title card: flowing green path, moving signal dot, and kinetic typography.
        intro_frames = int(2.6 * FPS)
        for n in range(intro_frames):
            t = n / FPS
            img = Image.new("RGB", (W, H), (10, 15, 16))
            d = ImageDraw.Draw(img)
            for x in range(W):
                g = int(10 + 14 * x / W)
                d.line((x, 0, x, H), fill=(9, g, 15))
            path = []
            for x in range(90, 1190, 5):
                y = 410 + int(60 * math.sin((x / 210) + t * 2.4) * math.exp(-((x-650)/580)**2))
                path.append((x, y))
            d.line(path, fill=(83, 152, 59), width=3)
            px = 90 + int((t / 2.6) * 1080)
            py = 410 + int(60 * math.sin((px / 210) + t * 2.4) * math.exp(-((px-650)/580)**2))
            d.ellipse((px-14, py-14, px+14, py+14), fill=(172, 255, 90))
            reveal = min(1.0, max(0.0, (t - 0.25) / 0.65))
            d.text((92, 240), "FLOW THESIS LEDGER", font=_font(43, True), fill=(240, 246, 238))
            d.text((96, 302), "LIVE MARKET EVIDENCE  /  DETERMINISTIC MONITORING", font=_font(17, True), fill=(172, 255, 90,))
            d.rounded_rectangle((96, 354, 96 + int(220 * reveal), 359), radius=2, fill=(172, 255, 90))
            d.text((96, 625), "A read-only, auditable workflow built on real UW observations", font=_font(17), fill=(173, 192, 180))
            writer.write(cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR))

        for idx, (start, end, *_label) in enumerate(CLIPS):
            cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
            count = int((end - start) * FPS)
            for n in range(count):
                ok, frame = cap.read()
                if not ok:
                    break
                # Center crop slowly pushes in, lending motion without obscuring evidence.
                zoom = 1.0 + 0.022 * (n / max(count, 1))
                cw, ch = int(crop_w / zoom), int(crop_h / zoom)
                cx = x0 + (crop_w - cw) // 2
                cy = y0 + (crop_h - ch) // 2
                view = frame[cy:cy+ch, cx:cx+cw]
                view = cv2.resize(view, (W, H), interpolation=cv2.INTER_LANCZOS4)
                local_t = n / FPS
                view = _overlay(view, elapsed + local_t, total, idx, local_t)
                writer.write(view)
            elapsed += end - start
    finally:
        cap.release()
        writer.release()
    # Convert the intermediate to H.264 before audio muxing.
    subprocess.run([_ffmpeg(), "-y", "-i", str(SILENT), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(SILENT.with_name("flow-thesis-demo-encoded.mp4"))], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SILENT.unlink(missing_ok=True)
    return intro_frames / FPS + total


def make_audio_mix(video_seconds: float) -> None:
    ffmpeg = _ffmpeg()
    # Read narration duration with ffprobe supplied alongside imageio-ffmpeg.
    probe = subprocess.run([ffmpeg, "-i", str(VOICE)], capture_output=True, text=True)
    # ffmpeg reports duration on stderr. Parse without echoing that output.
    import re

    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", probe.stderr)
    if not match:
        raise RuntimeError("Could not determine narration duration.")
    voice_seconds = int(match[1])*3600 + int(match[2])*60 + float(match[3])
    seconds = max(video_seconds, voice_seconds + 0.35)
    sample_rate = 44100
    n = int(seconds * sample_rate)
    t = np.arange(n, dtype=np.float32) / sample_rate
    # Soft instrumental bed: restrained, low-volume warm synth chord and subtle pulse.
    chord = (55.0, 82.41, 110.0, 164.81)
    music = np.zeros(n, dtype=np.float32)
    for i, hz in enumerate(chord):
        music += (0.16 / (i + 1)) * np.sin(2 * np.pi * hz * t + i * 0.55)
    pulse = 0.72 + 0.28 * np.sin(2 * np.pi * 0.16 * t)
    fade = np.minimum(1.0, t / 2.0) * np.minimum(1.0, np.maximum(0, (seconds - t) / 2.8))
    music *= pulse * fade * 0.11
    # Short filtered-noise swishes on each cut. A recursive low-pass keeps the
    # transient soft, while the exponential envelope creates a quick airy sweep.
    swishes = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(117)
    offsets = [2.45]
    offset = 2.45
    for start, end, *_ in CLIPS[:-1]:
        offset += end - start
        offsets.append(offset)
    for at in offsets[1:]:
        dur = int(0.62 * sample_rate)
        begin = int(max(0, at - 0.25) * sample_rate)
        raw = rng.normal(0, 1, dur).astype(np.float32)
        lp = np.empty_like(raw)
        state = 0.0
        for j, val in enumerate(raw):
            state += 0.075 * (val - state)
            lp[j] = state
        env = np.sin(np.linspace(0, np.pi, dur, dtype=np.float32)) ** 1.6
        end_i = min(n, begin + dur)
        swishes[begin:end_i] += lp[:end_i-begin] * env[:end_i-begin] * 0.055
    bed = np.clip(music + swishes, -0.9, 0.9)
    # MP3 TTS is decoded/resampled by ffmpeg; mix with music at a quiet level.
    temp_music = OUT_DIR / "flow-thesis-music-bed.wav"
    stereo = np.column_stack([bed, bed])
    with wave.open(str(temp_music), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((stereo * 32767).astype("<i2").tobytes())
    silent_h264 = SILENT.with_name("flow-thesis-demo-encoded.mp4")
    subprocess.run([
        ffmpeg, "-y", "-i", str(silent_h264), "-i", str(VOICE), "-i", str(temp_music),
        "-filter_complex", "[1:a]aresample=44100,volume=1.0[voice];[2:a]volume=0.55[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=1,alimiter=limit=0.95[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", f"{seconds:.3f}", "-movflags", "+faststart", str(VIDEO)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_music.unlink(missing_ok=True)
    silent_h264.unlink(missing_ok=True)


def write_script_files() -> None:
    (OUT_DIR / "flow-thesis-demo-narration.txt").write_text(NARRATION + "\n", encoding="utf-8")
    (ROOT / "docs" / "DEMO_VIDEO_EDIT.md").write_text(
        "# Demo video edit\n\n"
        "The submission demo is rendered from the real `1.mp4` screen capture. The edit uses an animated title, restrained push-ins, animated section cards, transition swishes, ElevenLabs narration, and a quiet original synthesized music bed. It cuts the old in-flight and restart-notice footage. The app capture is cropped to keep the interface readable and omit transient bottom toasts.\n\n"
        "Run from PowerShell in the repository root: `python scripts/render_demo_video.py`. The script reads `ELEVENLABS_API_KEY` from the process environment, sends it only in ElevenLabs' `xi-api-key` header, and does not print or persist it. It writes `artifacts/flow-thesis-demo.mp4`. Keep the raw capture and all credentials out of Git.\n\n"
        "Narration is in `artifacts/flow-thesis-demo-narration.txt`. The walkthrough describes only visible application behavior: live UW observations, explicit rule evaluation, inspectable evidence, and replay of saved live events.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script-only", action="store_true", help="Write narration/edit documentation without contacting ElevenLabs.")
    args = parser.parse_args()
    try:
        write_script_files()
        if args.script_only:
            print("Narration and video edit instructions written.")
            return 0
        elevenlabs_voiceover()
        duration = render_video()
        make_audio_mix(duration)
        print(f"Demo video rendered: {VIDEO.relative_to(ROOT)} ({duration:.1f}s).")
        print("Check the finished MP4 before submission; the raw screen capture remains untouched.")
        return 0
    except RuntimeError as exc:
        print(f"Video render not completed: {exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError:
        print("Video render failed in the encoder. No credential or provider response was logged.", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
