# Repository Structure

```text
shell-dg-logistics-narrated-video/
├── .github/
│   └── workflows/
│       └── build-narrated-video.yml
├── assets/
│   ├── audio/
│   │   ├── mix/
│   │   │   └── AIONOS_DG_Final_Audio_Mix.wav
│   │   └── narration/
│   │       ├── AIONOS_DG_Narration_Aligned_64s.mp3
│   │       └── AIONOS_DG_Narration_Aligned_64s.wav
│   └── video/
│       ├── final/
│       │   └── AIONOS_DG_Platform_Demo_Narrated.mp4
│       └── source/
│           └── AIONOS_DG_Platform_Demo.mp4
├── captions/
│   ├── AIONOS_DG_Platform_Demo.en.srt
│   └── AIONOS_DG_Platform_Demo.en.vtt
├── docs/
│   ├── AIONOS_Shell_Deck.pptx
│   └── Walkthrough_Script_DG_Platform_Demo.md
├── scripts/
│   ├── generate_narration.py
│   └── mux_final_video.sh
├── asset-manifest.json
├── BUILD_NOTES.md
├── index.html
├── package.json
├── README.md
├── requirements.txt
├── tts.config.json
└── REPO_STRUCTURE.md
```

## Key additions

- `.github/workflows/build-narrated-video.yml` automates the full MP3 + MP4 build on GitHub.
- `tts.config.json` includes `gb-en-ryan-neural` as an alias for `en-GB-RyanNeural`.
- `scripts/generate_narration.py` uses Edge neural TTS first and falls back to eSpeak locally if required.
