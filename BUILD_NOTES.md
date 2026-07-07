# Build Notes

## Objective

Create a GitHub-ready repo that converts the uploaded AIONOS x Shell dangerous-goods logistics demo into a narrated walkthrough video.

The build chain is:

```text
Markdown narration → MP3 voiceover → audio mix → final MP4 → GitHub Pages preview
```

## Voice

The requested voice is included as an alias:

```text
gb-en-ryan-neural
```

The normalized Microsoft Edge/Azure Neural ID used by the workflow is:

```text
en-GB-RyanNeural
```

This is configured in `tts.config.json` and the GitHub Actions workflow environment.

## GitHub workflow

Workflow file:

```text
.github/workflows/build-narrated-video.yml
```

The workflow:

1. Installs Python 3.11
2. Installs `ffmpeg` and fallback `espeak`
3. Installs Python dependencies, including `edge-tts`
4. Generates the timed MP3 narration using `en-GB-RyanNeural`
5. Mixes narration over the original MP4 audio bed/clicks
6. Exports the final narrated MP4
7. Uploads final media as a GitHub Actions artifact
8. Deploys the repo preview to GitHub Pages when Pages is enabled

## Local build behaviour

`python3 scripts/generate_narration.py` attempts Edge neural TTS first. If it cannot reach the TTS service, it falls back to eSpeak so the repo can still build offline.

Useful commands:

```bash
pip install -r requirements.txt
npm run build
```

## Main output paths

```text
assets/audio/narration/AIONOS_DG_Narration_Aligned_64s.mp3
assets/audio/mix/AIONOS_DG_Final_Audio_Mix.wav
assets/video/final/AIONOS_DG_Platform_Demo_Narrated.mp4
```

## Production note

For an actual client room, the `en-GB-RyanNeural` workflow output should be preferred over the offline fallback voice. A human-recorded 48 kHz WAV can also replace the MP3 while preserving the same timing windows.
