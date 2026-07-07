# AIONOS x Shell — DG Logistics Nerve Centre Narrated Demo

GitHub-ready repository for the **AIONOS x Shell intracity dangerous-goods logistics pitch video**.

This repo aligns the provided walkthrough narration with the uploaded 64-second MP4 demo, generates a timed MP3 narration track, preserves the original video music/click bed, and exports a final narrated MP4 ready for client playback or GitHub Pages hosting.

## What changed in this version

- Added GitHub Actions workflow: `.github/workflows/build-narrated-video.yml`
- Added Microsoft Neural voice configuration: `tts.config.json`
- Standardized the requested `gb-en-ryan-neural` voice alias to the Microsoft/Edge voice ID `en-GB-RyanNeural`
- Workflow now generates the MP3 narration first, merges it with the MP4, uploads final media artifacts, and deploys the static preview to GitHub Pages when Pages is enabled

## Final deliverables

| Asset | Path | Purpose |
|---|---|---|
| Final narrated MP4 | `assets/video/final/AIONOS_DG_Platform_Demo_Narrated.mp4` | Client-ready video with VO + original click/music bed |
| Timed narration MP3 | `assets/audio/narration/AIONOS_DG_Narration_Aligned_64s.mp3` | Generated narration track aligned to the 64-second timeline |
| Final mixed WAV | `assets/audio/mix/AIONOS_DG_Final_Audio_Mix.wav` | Original demo audio mixed with VO |
| Captions | `captions/AIONOS_DG_Platform_Demo.en.vtt` and `.srt` | Optional subtitles for web/video platforms |
| Source demo video | `assets/video/source/AIONOS_DG_Platform_Demo.mp4` | Uploaded Shell DG demo video |
| Walkthrough script | `docs/Walkthrough_Script_DG_Platform_Demo.md` | Original timed narration markdown |
| Shell deck | `docs/AIONOS_Shell_Deck.pptx` | Supporting Shell pitch deck context |
| TTS config | `tts.config.json` | Ryan Neural voice + fallback settings |
| GitHub Actions | `.github/workflows/build-narrated-video.yml` | Automated MP3 generation, MP4 muxing, artifact upload and Pages deploy |

## Preview locally

Open `index.html` in a browser, or run:

```bash
python3 -m http.server 8080
```

Then visit:

```text
http://localhost:8080
```

## Rebuild locally

System requirements:

- `python3`
- `ffmpeg`
- Python package dependencies in `requirements.txt`
- Optional offline fallback: `espeak`

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Generate the timed MP3 narration:

```bash
python3 scripts/generate_narration.py
```

Mux the final narrated video:

```bash
bash scripts/mux_final_video.sh
```

Or run both through npm:

```bash
npm run build
```

## Voice configuration

The repo is configured for the requested British male neural voice:

```text
gb-en-ryan-neural → en-GB-RyanNeural
```

`gb-en-ryan-neural` is preserved as a supported alias in `tts.config.json`, while `en-GB-RyanNeural` is the normalized Microsoft Edge/Azure Neural voice ID used by the build.

To override the voice in GitHub Actions or locally:

```bash
EDGE_TTS_VOICE=en-GB-RyanNeural python3 scripts/generate_narration.py
```

To use another Edge/Azure voice:

```bash
EDGE_TTS_VOICE=en-GB-LibbyNeural python3 scripts/generate_narration.py
```

The local script attempts `edge-tts` first. If Edge neural TTS is unavailable, it falls back to `espeak` so the repo remains rebuildable even without cloud access. GitHub Actions is configured to use `edge-tts` with `en-GB-RyanNeural`.

## GitHub Actions workflow

The included workflow runs on:

- Push to `main`
- Push to `master`
- Manual `workflow_dispatch`

It performs the full build chain:

1. Checks out the repo
2. Installs Python, `ffmpeg`, and fallback `espeak`
3. Installs `pydub` and `edge-tts`
4. Generates the MP3 narration using `en-GB-RyanNeural`
5. Muxes the narration with the source MP4
6. Validates the final MP4 with `ffprobe`
7. Uploads the final MP4, MP3, WAV mix, and captions as a GitHub Actions artifact
8. Uploads and deploys the static site to GitHub Pages on `main` / `master`

### Enable GitHub Pages

After uploading the repo to GitHub:

1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**
3. Push to `main` or run the workflow manually
4. Open the deployed Pages URL after the workflow completes

## Narration timing

The generated VO follows these source script segments:

1. `00:01–00:11` — Command Centre
2. `00:13–00:24` — Trip View
3. `00:26–00:36` — HITL Approvals
4. `00:38–00:46` — Live Reroute
5. `00:48–00:57` — Compliance & Scorecard
6. `00:58–01:03` — End Card

The original video’s click sounds/music bed are retained and mixed below the VO, so the result still feels like a real screen recording.

## Client context

The video supports the AIONOS x Shell proposition: an AI-assisted dangerous-goods logistics nerve centre for intracity fuel movement, covering dispatch, route risk, live exceptions, HITL approvals, rerouting, compliance evidence and scorecard outcomes.

All demo data, IDs, scores and KPI values are illustrative and should be presented as pilot-ready synthetic data until validated against Shell operational baselines.
