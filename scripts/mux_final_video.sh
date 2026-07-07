#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_VIDEO="$ROOT/assets/video/source/AIONOS_DG_Platform_Demo.mp4"
VO_MP3="$ROOT/assets/audio/narration/AIONOS_DG_Narration_Aligned_64s.mp3"
MIX_WAV="$ROOT/assets/audio/mix/AIONOS_DG_Final_Audio_Mix.wav"
FINAL_VIDEO="$ROOT/assets/video/final/AIONOS_DG_Platform_Demo_Narrated.mp4"

mkdir -p "$ROOT/assets/audio/mix" "$ROOT/assets/video/final"

if [[ ! -f "$VO_MP3" ]]; then
  python3 "$ROOT/scripts/generate_narration.py"
fi

# Mix original demo audio (music/clicks) under the generated narration.
# Original audio is kept, reduced slightly so the narration stays intelligible.
ffmpeg -y \
  -i "$SRC_VIDEO" \
  -i "$VO_MP3" \
  -filter_complex "[0:a]volume=0.42[a0];[1:a]volume=1.35[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95,aresample=48000[mix]" \
  -map "[mix]" -c:a pcm_s16le "$MIX_WAV"

# Preserve source video quality, replace audio with the final mix.
ffmpeg -y \
  -i "$SRC_VIDEO" \
  -i "$MIX_WAV" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart \
  "$FINAL_VIDEO"

echo "Generated final narrated video: $FINAL_VIDEO"
