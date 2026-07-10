# video

Cockpit package for token-optimized video processing. Slices video files into JPEG frames so AI agents can analyze them as images instead of sending the full video stream.

## Purpose

Sending a raw video to a multimodal LLM is expensive: Gemini samples at 1 frame/second (≈258 tokens each), so a 1-minute clip costs ~15 480 image tokens. `video` slices the file at a configurable interval (default: every 5 s), cutting token usage by up to 5×.

It also installs:
- A **skill** (`video-slice`) that guides the agent to always slice before analyzing.
- A **rule** (`video-processing`) that enforces the slicing protocol automatically.

## Requirements

| Dependency | Minimum version |
|---|---|
| AICockpit (`cockpit`) | `0.1.0` |
| `ffmpeg` | any recent (must be in `$PATH`) |

## Installation

```bash
cockpit pkg install video
```

## Usage

```bash
# Slice a video into frames (one JPEG every 5 seconds)
cockpit video slice path/to/recording.mp4

# Custom interval (1 frame every 2 seconds — for fast motion)
cockpit video slice path/to/recording.mp4 --interval 2

# Custom output directory
cockpit video slice path/to/recording.mp4 --output /tmp/frames

# Show help
cockpit video --help
```

Output frames are saved to:

```
~/.cockpit/workspace/video-slice/<video-name>/slices/
```

After slicing, read the images in order with your agent's file-viewer tool.

## AI rule / skill

The installed rule (`video-processing.md`) instructs agents to **never** send a raw video file directly to the LLM. Instead:

1. Run `cockpit video slice <path>`.
2. Read the generated JPEG frames.
3. Only send the video directly when the audio track or sub-second motion is strictly required.

## Package structure

```
video/
├── bin/
│   └── video              # CLI entry point (Bash)
├── skills/
│   └── video-slice/       # AI skill definition
├── rules/
│   └── video-processing.md  # Enforcement rule
├── cockpit-package.yml
└── README.md
```

## Supported providers

`antigravity`, `devin`, `goose`

## License

MIT
