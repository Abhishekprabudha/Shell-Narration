#!/usr/bin/env python3
"""
Generate a timed narration MP3/WAV from docs/Walkthrough_Script_DG_Platform_Demo.md.

Default production path:
- Use Microsoft Edge/Azure Neural voice: en-GB-RyanNeural
- Accept the user-requested alias: gb-en-ryan-neural
- Align each generated segment to the script's timestamp windows

Offline fallback:
- If edge-tts is unavailable or the cloud TTS call fails, fall back to eSpeak
  so the repo still builds in offline/local environments.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from pydub import AudioSegment, effects

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_MD = ROOT / "docs" / "Walkthrough_Script_DG_Platform_Demo.md"
CONFIG_JSON = ROOT / "tts.config.json"
OUT_DIR = ROOT / "assets" / "audio" / "narration"
DURATION_SECONDS_DEFAULT = 64


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def load_config() -> dict[str, Any]:
    if CONFIG_JSON.exists():
        return json.loads(CONFIG_JSON.read_text(encoding="utf-8"))
    return {}


def normalize_voice(voice: str, config: dict[str, Any]) -> str:
    aliases = config.get("voice_aliases", {}) or {}
    if voice in aliases:
        return aliases[voice]
    voice_lower = voice.lower().replace("_", "-")
    for key, value in aliases.items():
        if key.lower().replace("_", "-") == voice_lower:
            return value
    return voice


def parse_timecode(mm: str, ss: str) -> int:
    return int(mm) * 60 + int(ss)


def clean_for_tts(text: str) -> str:
    # Pronunciation helpers only; original copy remains preserved in markdown/captions.
    replacements = {
        "AIONOS": "AI-on-OS",
        "DG": "D G",
        "ePOD": "e P O D",
        "HITL": "H I T L",
        "ETA": "E T A",
        "AI ": "A I ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def parse_segments(markdown: str) -> list[dict[str, str | int]]:
    pattern = re.compile(
        r"\*\*\[(\d\d):(\d\d) - (\d\d):(\d\d)\]\s*([^*]+?)\*\*\s*\n\"([\s\S]*?)\"",
        re.MULTILINE,
    )
    segments = []
    for i, match in enumerate(pattern.finditer(markdown), start=1):
        start = parse_timecode(match.group(1), match.group(2))
        end = parse_timecode(match.group(3), match.group(4))
        title = " ".join(match.group(5).split())
        text = " ".join(match.group(6).split())
        segments.append({"index": i, "start": start, "end": end, "title": title, "text": text})
    if not segments:
        raise ValueError("No timed narration segments found in the markdown script.")
    return segments


def write_captions(segments: list[dict[str, str | int]]) -> None:
    captions_dir = ROOT / "captions"
    captions_dir.mkdir(exist_ok=True)
    vtt = ["WEBVTT", ""]
    srt: list[str] = []

    def tc_vtt(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}.000"

    def tc_srt(seconds: int) -> str:
        return tc_vtt(seconds).replace(".", ",")

    for seg in segments:
        idx = int(seg["index"])
        start = int(seg["start"])
        end = int(seg["end"])
        text = str(seg["text"])
        vtt.extend([f"{tc_vtt(start)} --> {tc_vtt(end)}", text, ""])
        srt.extend([str(idx), f"{tc_srt(start)} --> {tc_srt(end)}", text, ""])

    (captions_dir / "AIONOS_DG_Platform_Demo.en.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (captions_dir / "AIONOS_DG_Platform_Demo.en.srt").write_text("\n".join(srt), encoding="utf-8")


async def synthesize_edge_tts(text: str, out_path: Path, config: dict[str, Any]) -> None:
    try:
        import edge_tts  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("edge-tts is not installed") from exc

    edge_cfg = config.get("edge_tts", {}) or {}
    raw_voice = os.environ.get("EDGE_TTS_VOICE") or os.environ.get("AZURE_TTS_VOICE") or edge_cfg.get("voice") or "en-GB-RyanNeural"
    voice = normalize_voice(raw_voice, config)
    rate = os.environ.get("EDGE_TTS_RATE") or edge_cfg.get("rate") or "+18%"
    volume = os.environ.get("EDGE_TTS_VOLUME") or edge_cfg.get("volume") or "+0%"
    pitch = os.environ.get("EDGE_TTS_PITCH") or edge_cfg.get("pitch") or "+0Hz"

    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume, pitch=pitch)
    await communicate.save(str(out_path))


def synthesize_espeak(text: str, out_path: Path, config: dict[str, Any]) -> None:
    if not shutil.which("espeak"):
        raise RuntimeError("eSpeak fallback is required but not installed.")

    fallback = config.get("fallback_espeak", {}) or {}
    voice = os.environ.get("ESPEAK_VOICE") or fallback.get("voice") or "en-gb"
    speed = os.environ.get("ESPEAK_SPEED") or fallback.get("speed") or "225"
    pitch = os.environ.get("ESPEAK_PITCH") or fallback.get("pitch") or "42"
    amplitude = os.environ.get("ESPEAK_AMPLITUDE") or fallback.get("amplitude") or "160"

    # eSpeak writes WAV directly.
    run([
        "espeak",
        "-v", str(voice),
        "-s", str(speed),
        "-p", str(pitch),
        "-a", str(amplitude),
        "-w", str(out_path),
        text,
    ])


def fit_segment_to_window(voice: AudioSegment, window_ms: int) -> AudioSegment:
    """Keep each VO segment inside its timestamp window with small guardrails."""
    max_ms = max(250, window_ms - 160)
    if len(voice) <= max_ms:
        return voice

    # First try pydub speedup for moderate compression.
    ratio = len(voice) / max_ms
    if ratio <= 1.5:
        voice = effects.speedup(voice, playback_speed=ratio + 0.03, chunk_size=80, crossfade=20)

    # If still long, trim gently at the end rather than letting it collide with next screen.
    if len(voice) > max_ms:
        voice = voice[:max_ms]
    return voice


def audio_settings(config: dict[str, Any]) -> tuple[int, int, int, float]:
    audio_cfg = config.get("audio", {}) or {}
    duration_seconds = int(audio_cfg.get("duration_seconds", DURATION_SECONDS_DEFAULT))
    sample_rate = int(audio_cfg.get("sample_rate", 48000))
    channels = int(audio_cfg.get("channels", 2))
    headroom_db = float(audio_cfg.get("headroom_db", 2.0))
    return duration_seconds, sample_rate, channels, headroom_db


def main() -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required to encode and mux audio/video.")

    config = load_config()
    duration_seconds, sample_rate, channels, headroom_db = audio_settings(config)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = OUT_DIR / "segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    markdown = SCRIPT_MD.read_text(encoding="utf-8")
    segments = parse_segments(markdown)
    write_captions(segments)

    preferred_engine = (os.environ.get("TTS_ENGINE") or config.get("preferred_engine") or "edge-tts").lower()
    raw_voice = os.environ.get("EDGE_TTS_VOICE") or os.environ.get("AZURE_TTS_VOICE") or config.get("preferred_voice") or "en-GB-RyanNeural"
    selected_voice = normalize_voice(str(raw_voice), config)

    print(f"Preferred TTS engine: {preferred_engine}")
    print(f"Selected neural voice: {selected_voice} (alias gb-en-ryan-neural supported)")

    timeline = AudioSegment.silent(duration=duration_seconds * 1000, frame_rate=sample_rate).set_channels(channels)

    for seg in segments:
        idx = int(seg["index"])
        start_ms = int(seg["start"]) * 1000
        end_ms = int(seg["end"]) * 1000
        window_ms = max(500, end_ms - start_ms)
        text_for_tts = clean_for_tts(str(seg["text"]))

        segment_media = temp_dir / f"segment_{idx:02d}.mp3"
        segment_wav = temp_dir / f"segment_{idx:02d}.wav"

        used_engine = "edge-tts"
        try:
            if preferred_engine in {"edge", "edge-tts", "azure", "azure-tts"}:
                asyncio.run(synthesize_edge_tts(text_for_tts, segment_media, config))
                voice = AudioSegment.from_file(segment_media).set_frame_rate(sample_rate).set_channels(channels)
            else:
                used_engine = "espeak"
                synthesize_espeak(text_for_tts, segment_wav, config)
                voice = AudioSegment.from_wav(segment_wav).set_frame_rate(sample_rate).set_channels(channels)
        except Exception as exc:
            used_engine = "espeak-fallback"
            print(f"Segment {idx:02d}: edge-tts unavailable/failed ({exc}); using eSpeak fallback.")
            synthesize_espeak(text_for_tts, segment_wav, config)
            voice = AudioSegment.from_wav(segment_wav).set_frame_rate(sample_rate).set_channels(channels)

        voice = fit_segment_to_window(voice, window_ms)
        voice = voice.fade_in(40).fade_out(80)
        timeline = timeline.overlay(voice, position=start_ms)
        print(f"Segment {idx:02d}: {used_engine}, start={start_ms/1000:.2f}s, window={window_ms/1000:.2f}s, audio={len(voice)/1000:.2f}s")

    timeline = effects.normalize(timeline, headroom=headroom_db)
    wav_out = OUT_DIR / "AIONOS_DG_Narration_Aligned_64s.wav"
    mp3_out = OUT_DIR / "AIONOS_DG_Narration_Aligned_64s.mp3"
    timeline.export(wav_out, format="wav")
    timeline.export(mp3_out, format="mp3", bitrate="192k")

    print(f"Generated narration WAV: {wav_out}")
    print(f"Generated narration MP3: {mp3_out}")


if __name__ == "__main__":
    main()
