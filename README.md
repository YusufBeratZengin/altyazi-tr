# altyazi-tr

> **Moved to [subtitle-tools](https://github.com/YusufBeratZengin/subtitle-tools).**
> altyazi-tr is now part of subtitle-tools as `subtool transcribe`, with the same
> options. New work happens there; this repository is kept for reference.
> Until subtitle-tools is on PyPI, run `pip install -e ".[transcribe]"` in its clone.
>
> ```sh
> pip install "subtitle-tools[transcribe]"
> subtool transcribe video.mp4 --model ./models/small -o captions --format all
> ```

Offline, word-timed Turkish subtitles for short vertical videos using faster-whisper.

[![CI](https://github.com/YusufBeratZengin/altyazi-tr/actions/workflows/ci.yml/badge.svg)](https://github.com/YusufBeratZengin/altyazi-tr/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Türkçe](README.tr.md)

![altyazi-tr terminal demo](docs/demo.svg)

## Why altyazi-tr?

- **100% Offline & Private**: Zero external API calls, zero telemetry, and zero automatic model downloads. Your recordings, audio, and subtitle texts stay on your local machine.
- **Engineered for Vertical Video (9:16)**: Built specifically for Shorts, Reels, and TikTok with tight line widths (18 characters), smart pause-aware line wrapping, and active-word karaoke animations for styled ASS subtitles.
- **Native Turkish Language Rules**: Proper Turkish uppercase handling (`i→İ`, `ı→I`), avoidance of stranded conjunctions (`ve`, `ama`, `ki`, `de`/`da`) at line ends, and actionable confidence warning reports.

---

## Quick start

### 1. Installation

Python 3.10 or newer is required.

**Not on PyPI yet.** Clone this repository and install from the checkout with
`python -m pip install .`:

```sh
git clone https://github.com/YusufBeratZengin/altyazi-tr.git
cd altyazi-tr

# Create and activate virtual environment
python -m venv .venv

# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

# Install core package from the checkout
python -m pip install .

# Or with burning and YAML support from checkout:
python -m pip install ".[ffmpeg,yaml]"
```

Verify the installation:

```sh
altyazi-tr --help
```

### 2. Copy-paste verified working demo

Test subtitle generation immediately using pre-saved deterministic word tokens (no faster-whisper model download needed):

```sh
altyazi-tr --words-json docs/examples/sample.words.json -o captions --format all --mode words --upper
```

This writes `captions.srt`, `captions.vtt`, and `captions.ass` to the current directory.

### 3. Transcribe a local video

When you have a faster-whisper model (e.g. `small` in your local cache or local directory):

```sh
altyazi-tr video.mp4 --model ./models/small -o captions --format all
```

---

## Usage examples

### Standard Subtitles (SRT & WebVTT)

```sh
altyazi-tr video.mp4 --model ./models/small -o captions --format srt
altyazi-tr video.mp4 --model ./models/small -o captions --format vtt
```

Trimmed SRT excerpt ([`docs/examples/sample.srt`](docs/examples/sample.srt)):

```srt
1
00:00:00,000 --> 00:00:02,050
BUGÜN DİKEY
VİDEOLAR İÇİN

2
00:00:02,120 --> 00:00:04,100
ALTYAZI
HAZIRLIYORUZ ÇÜNKÜ

3
00:00:04,180 --> 00:00:07,100
İYİ IŞIK VE NET
SES ÇOK ÖNEMLİ.
```

### Karaoke Active-Word ASS Subtitles

The `words` mode highlights each active word as it is spoken and removes the highlight during pauses:

```sh
altyazi-tr video.mp4 --model ./models/small -o karaoke --format ass --mode words --upper --report json
```

Karaoke ASS excerpt ([`docs/examples/sample.ass`](docs/examples/sample.ass)):

```ass
Dialogue: 0,0:00:00.00,0:00:00.42,Default,,0,0,0,,{\1c&H00FFFF&\1a&H00&}BUGÜN{\rDefault} DİKEY\NVİDEOLAR İÇİN
Dialogue: 0,0:00:00.42,0:00:00.48,Default,,0,0,0,,BUGÜN DİKEY\NVİDEOLAR İÇİN
Dialogue: 0,0:00:00.48,0:00:00.95,Default,,0,0,0,,BUGÜN {\1c&H00FFFF&\1a&H00&}DİKEY{\rDefault}\NVİDEOLAR İÇİN
Dialogue: 0,0:00:00.95,0:00:01.02,Default,,0,0,0,,BUGÜN DİKEY\NVİDEOLAR İÇİN
Dialogue: 0,0:00:01.02,0:00:01.60,Default,,0,0,0,,BUGÜN DİKEY\N{\1c&H00FFFF&\1a&H00&}VİDEOLAR{\rDefault} İÇİN
```

### Video Hardcoding / Burn-in (`--burn`)

Burn stylized ASS subtitles directly into video using local ffmpeg:

```sh
altyazi-tr video.mp4 --model ./models/small -o rendered --format ass --burn --style docs/style.json --position middle
```

Produces `rendered.burned.mp4` encoded with H.264 (`yuv420p`) and AAC audio.

### Decoupled Re-layout and Re-styling

Persist recognized tokens to JSON once, then test different layout rules and styles instantly without re-running inference:

```sh
# 1. Transcribe once and save recognized word tokens
altyazi-tr video.mp4 --model ./models/small --save-words words.json -o captions

# 2. Re-layout or re-style from JSON in milliseconds
altyazi-tr --words-json words.json -o captions_v2 --format all --mode words --max-chars 14 --upper
```

### Python API

```python
from altyazi_tr import LayoutConfig, Word, layout
from altyazi_tr.writers import ass, srt, vtt

words = [Word(0.0, 0.4, "iyi", 0.95), Word(0.5, 1.0, "ışık", 0.90)]
cues = layout(words, LayoutConfig(upper=True), duration=2.0)

print(srt(cues))
vtt_text = vtt(cues)
ass_karaoke = ass(cues, karaoke=True)
```

| Entry point | Purpose |
| --- | --- |
| `Word(start, end, text, prob)` | Validated, immutable timed token (seconds, probability 0–1). |
| `Cue(start, end, lines)` | Immutable subtitle block containing lines of `Word` tuples. |
| `layout(words, config, duration=None)` | Pure layout engine; enforces line limits, breaks, and reading speed. |
| `turkish_upper(text)` | Correct Turkish uppercase mapping (`i→İ`, `ı→I`). |
| `layout_warnings(cues, config)` | Detects unavoidable layout constraint notices. |
| `transcribe.transcribe(path, ...)` | Local faster-whisper speech recognition with offline protection. |
| `style.load_style(path)` | Parses and validates JSON/YAML ASS styles. |
| `writers.srt/vtt/ass(cues)` | Formats subtitle cues to standard strings. |
| `burn.burn(source, subtitles, output)` | Burns ASS into video via local ffmpeg. |

---

## Configuration

### Layout Parameters

| Option | Default | Description |
| --- | :---: | --- |
| `--mode {words,groups}` | `groups` | `groups` displays word groups; `words` highlights each spoken word in ASS. |
| `--max-chars` | `18` | Maximum characters per line (including spaces and punctuation). |
| `--max-lines` | `2` | Maximum lines per subtitle block (supported: 1–4). |
| `--pause-threshold` | `0.6` | Silence duration (seconds) that triggers an automatic cue break. |
| `--min-duration` | `0.8` | Minimum on-screen display duration (seconds) for each subtitle cue. |
| `--max-cps` | `18.0` | Maximum reading speed (characters per second). |
| `--upper` | `False` | Convert subtitles to uppercase (uses Turkish dotted/dotless I for `tr` and `az`). |

### ASS Style Configuration

Custom styles can be specified via JSON or YAML files (e.g. [`docs/style.json`](docs/style.json) or [`docs/style.yaml`](docs/style.yaml)):

```json
{
  "font": "DejaVu Sans",
  "font_size": 72,
  "primary_color": "&H00FFFFFF",
  "highlight_color": "&H0000FFFF",
  "outline_color": "&H00000000",
  "outline": 4.0,
  "bold": true,
  "position": "bottom",
  "margin_v": 320
}
```

- **Canvas**: Reference 1080×1920 canvas designed for vertical 9:16 video.
- **Colors**: ASS format `&HAABBGGRR` (alpha, blue, green, red in hex).
- **Position**: `bottom` (uses `margin_v` from bottom), `middle` (centered), `upper` (`margin_v` from top).

### Exit Codes

| Exit code | Category | Description |
| :---: | --- | --- |
| `0` | Success | Subtitle cues generated and written successfully. |
| `1` | Processing error | Runtime failure such as missing input file, empty/unreadable audio, un-cached offline model, output file collision, or invalid ASS style. |
| `2` | Argument error | Invalid command-line arguments, unsupported options, or missing required parameters. |

### Report JSON Schema

Running with `--report json` generates `<stem>.report.json` ([`docs/examples/report.json`](docs/examples/report.json)):

| Field | Type | Description |
| --- | --- | --- |
| `version` | string | Package version used to produce the report. |
| `language` | string | Language code used during transcription. |
| `duration` | float | Media duration in seconds (capped to last word end). |
| `device` | string | Device used for inference (`cpu`, `cuda`, or `none`). |
| `compute_type` | string | Precision used for inference (`int8`, `float16`, or `none`). |
| `cue_count` | integer | Total number of subtitle cues produced. |
| `confidence_threshold` | float | Threshold used to flag low-confidence words. |
| `low_confidence_words` | array | List of `{start, end, text, prob}` tokens where probability is below threshold. |
| `layout_warnings` | array | List of `{cue, codes}` items where cues exceed layout constraints. |

---

## FAQ & Limitations

### Offline Operation & Model Acquisition

Package installation and initial model acquisition require internet access. However, the CLI **never downloads a model**, including on first use: the adapter always passes `local_files_only=True`.

A named model such as `small` must already reside in your Hugging Face cache, or you can provide a complete local faster-whisper/CTranslate2 model directory via `--model /path/to/model`. See upstream [faster-whisper model conversion](https://github.com/SYSTRAN/faster-whisper#model-conversion).

### Model Scale & Tradeoffs

| Multilingual model | Parameters (approx.) | Relative speed | Typical accuracy tradeoff |
| --- | ---: | --- | --- |
| `tiny` | 39M | Fastest | Higher Turkish recognition error rate |
| `base` | 74M | Fast | Useful for quick drafts |
| `small` (recommended) | 244M | Moderate | Practical starting point for Turkish speech |
| `medium` | 769M | Slower | Stronger accuracy in noisy speech |
| `large-v3` | 1,550M | Slowest | Maximum accuracy; requires more VRAM / RAM |

### CPU, GPU, and Hardware Acceleration

- `--device auto`: Automatically selects CUDA if CTranslate2 detects an available GPU; otherwise falls back to CPU with `int8`. If CUDA inference fails with a runtime error, it safely retries on CPU int8.
- `--device cpu`: Forces CPU inference and avoids GPU dependencies.
- `--compute-type`: Overrides default quantization (`int8` on CPU, `float16` on CUDA).

### Known Limitations

- **No Diarization or Translation**: Does not separate multiple speakers or translate between languages.
- **Background Music**: Heavy background music or singing can cause Whisper hallucinations or timing drift.
- **Burning Requirements**: Burning (`--burn`) requires ffmpeg built with `libass` support.
- **Aspect Ratio**: Default ASS canvas is 1080×1920 (9:16 vertical). Adapt the style file for landscape videos.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup, offline testing instructions, lint/type checks, and security guardrails.

```sh
# Run offline test suite with coverage
python -m pytest

# Run linter and strict type checker
python -m ruff check .
python -m ruff format --check .
python -m mypy
```

All contributions must preserve offline guarantees and privacy guardrails.

---

## License

This project is licensed under the [MIT License](LICENSE).
