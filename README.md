# altyazi-tr

altyazi-tr creates offline, word-timed Turkish subtitles for short vertical videos using faster-whisper.

[![CI](https://img.shields.io/badge/CI-configured-lightgrey)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Türkçe](README.tr.md)

The CLI reads local video or audio and writes SRT, WebVTT, or styled ASS. It handles
Turkish capitalization, short lines, pauses, and reading targets. Audio and text
stay on your machine. No API account or paid service is required. The CI badge
links to the workflow; it is not a claim that a hosted run has passed. Once a
GitHub remote exists, it can be replaced with that repository's live Actions badge.

## Installation

Python 3.10 or newer is required. From a checkout:

```sh
python -m venv .venv
# Linux / macOS:
. .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install .
```

`faster-whisper` is a required dependency. Optional extras:

```sh
python -m pip install ".[ffmpeg,yaml]"
```

ffmpeg is needed **only for `--burn`**. Recognition uses faster-whisper's PyAV
decoder and does not require the ffmpeg executable. Discovery order for burning:

1. `ffmpeg` on `PATH`.
2. `imageio_ffmpeg.get_ffmpeg_exe()` from the `ffmpeg` extra. That package may
   honor `IMAGEIO_FFMPEG_EXE` and its own executable selection rules.

The selected ffmpeg must support `ass`/libass, `libx264`, and AAC. Some bundled
builds lack libass; install a suitable system build if burning fails. Choose and
install the font used in your style; missing fonts can alter wrapping.

### Local models and offline operation

Package installation and initial model acquisition need internet access. This
CLI **never downloads a model**, including on first use: the adapter always passes
`local_files_only=True`. A named model such as `small` must already be in the
Hugging Face cache. Alternatively, supply a complete faster-whisper/CTranslate2
model directory containing its tokenizer assets. A raw OpenAI checkpoint is not
interchangeable with a converted model directory.

Acquire a model separately on a connected machine, following the
[upstream model instructions](https://github.com/SYSTRAN/faster-whisper#model-conversion),
then copy the complete directory to the offline machine. Do not upload recordings
to download a model. `--model ./models/small` avoids dependence on a user cache.
Missing models produce an error; transcription does not send audio, text, or
reports to a service. Model files and media are excluded from Git.

### CPU, GPU, and Windows

`--device auto` selects CUDA when CTranslate2 reports a GPU; otherwise it uses
CPU with `int8`. If automatic CUDA inference fails with a runtime error, it retries
on CPU int8. `--device cpu` avoids GPU dependencies. `--compute-type` overrides
the normal default (`int8` on CPU, `float16` on CUDA); automatic CUDA fallback
still uses int8. Explicit `--device cuda` failures remain errors.

GPU use requires a compatible NVIDIA driver, CUDA and cuDNN installation; check
the [upstream GPU requirements](https://github.com/SYSTRAN/faster-whisper#gpu).
GPU setup changes between CTranslate2 versions. Do not assume installing this
package installs a working GPU stack. On Windows, use a Python/architecture with
wheels for the native dependencies, add a suitable ffmpeg to `PATH` if needed,
quote paths with spaces, and use a locally installed font such as `Arial` in the
style if DejaVu Sans is unavailable. Files are UTF-8.

## Quick start

With a previously acquired local model:

```sh
altyazi-tr invented-clip.mp4 --model ./models/small -o captions --format all
altyazi-tr invented-clip.mp4 --model ./models/small -o karaoke --format ass --mode words --upper --report json
altyazi-tr invented-clip.mp4 --model ./models/small -o rendered --format ass --burn --style docs/style.json --position middle
```

These commands use illustrative filenames, not bundled recordings. Default
language is `tr`; for another supported language, pass e.g. `--lang en` and use a
multilingual model. Uppercase conversion is opt-in (`--upper`); the dotted/dotless I
mapping is applied only for `--lang tr` and `az`, other languages use plain uppercase.

`-o` accepts a stem or a subtitle filename. `-o clip.v1.srt --format all` writes
`clip.v1.srt`, `clip.v1.vtt`, and `clip.v1.ass`. Without `-o`, the input stem is used.
Parent directories are created. Existing output files are refused. `--burn` also
writes ASS if necessary, then `<stem>.burned.mp4` (H.264/AAC, requiring a video
stream). Subtitle/report files already written remain available if burning fails.

`groups` shows a word group per cue. `words` starts with one word per cue; short
neighbours can merge to meet reading targets. In ASS, `words` highlights only the
currently spoken word, with no highlight during gaps; SRT/VTT remain static and
cannot reproduce the color animation. Use `--min-duration 0.01 --max-cps 10000`
to minimize merging for strictly word-by-word plain subtitles.

![Illustrative preview placeholder, not a screenshot](docs/preview-placeholder.svg)

The [docs folder](docs/README.md) reserves space for a real GIF or screenshot.

## Layout and styling

Defaults: 18 characters per line, at most 2 lines, 0.6-second pause threshold,
0.8-second minimum display time, 18 characters per second. Spaces and punctuation
count toward line length and reading speed. Width is a character count, not a
font measurement. `--max-lines` supports 1–4 lines.

Punctuation and pauses suggest breaks. The line search avoids leaving `ve`,
`ama`, `ki`, and separately written `de`/`da` at the end where space permits.
Short neighbours merge if they fit and are not separated by a long pause. Cues
may extend into silence, capped at the next cue or media end. They never overlap.

Constraints can conflict: a single long word is preserved, and dense speech may
exceed the reading target. Text is never silently discarded to enforce a width
or speed limit. The CLI warns; `--report json` lists `long_word`, `short_duration`,
`reading_speed`, or `trailing_conjunction` notices. It also lists words below
`--confidence` (default 0.6), with original text, probability and timestamps.
Probabilities are model estimates, not calibrated accuracy scores. The report is
local and can contain sensitive transcript text; treat it like the recording.

ASS uses a 1080×1920 reference canvas, bold text, outline, and bottom alignment
with a 320-pixel vertical margin. Positions are `bottom`, `middle`, and `upper`;
`--position` overrides the style file. Middle ignores the vertical margin under
ASS alignment rules; upper uses it from the top. Other aspect ratios need an
appropriate style. JSON works without extras; YAML needs `[yaml]` and uses a safe
loader. See [JSON](docs/style.json) and [YAML](docs/style.yaml) examples. Supported
fields are `font`, `font_size` (1–300), `primary_color`, `highlight_color`,
`outline_color`, `outline` (0–20), `bold`, `position`, and `margin_v` (0–900).
Colors use ASS `&HAABBGGRR` (alpha, blue, green, red); unknown fields are rejected.

## API summary

```python
from altyazi_tr import LayoutConfig, Word, layout
from altyazi_tr.writers import ass, srt, vtt

# Entirely invented phrase, no model needed.
words = [Word(0.0, 0.4, "iyi", 0.95), Word(0.5, 1.0, "ışık", 0.90)]
cues = layout(words, LayoutConfig(upper=True), duration=2.0)
print(srt(cues))
animated = ass(cues, karaoke=True)
web_subtitles = vtt(cues)
```

| Entry point | Purpose |
| --- | --- |
| `Word(start, end, text, prob)` | Validated, immutable timed token; seconds, probability 0–1 |
| `Cue(start, end, lines)` | Immutable subtitle block; lines contain `Word` tuples |
| `layout(words, config, duration=None)` | Pure layout; preserves order and rejects overlapping words |
| `turkish_upper(text)` | `i→İ`, `ı→I`, then Unicode uppercase |
| `layout_warnings(cues, config)` | Unavoidable constraint notices |
| `transcribe.transcribe(path, ...)` | Local recognition with model/device/precision/language/VAD controls |
| `style.load_style(path)` | Validated JSON/YAML ASS style |
| `writers.srt/vtt/ass(cues)` | Serialize to a string; caller controls storage |
| `burn.burn(source, subtitles, output)` | Burn an ASS file with local ffmpeg; refuses overwrites |

The `layout_warnings` function lives in `altyazi_tr.layout` (import it from that
module). Importing the package does not load recognition libraries or models.
The adapter skips empty or zero-duration decoder words, splits multiword tokens
proportionally, and clips overlapping decoder intervals to the previous word end.
The pure API accepts already valid, chronological words. Omit `duration` to avoid
inventing time after the final word. Errors are English; CLI exits 0 on success,
1 on processing errors, and 2 on argument parsing errors.

## Model tradeoffs and limits

Approximate model scales, not measurements of this project:

| Multilingual model | Parameters (approx.) | Relative speed | Typical accuracy tradeoff |
| --- | ---: | --- | --- |
| tiny | 39M | Fastest | More Turkish recognition errors |
| base | 74M | Fast | Useful for drafts |
| small (default) | 244M | Moderate | Practical starting point |
| medium | 769M | Slower | Often better in difficult speech |
| large-v3 | 1,550M | Slowest here | Often strongest; more memory needed |

Actual speed, memory and accuracy vary with hardware, quantization, noise, speech
and language. These are qualitative expectations, not a Turkish benchmark or
guarantee. See [upstream models](https://github.com/openai/whisper#available-models-and-languages).
No diarization, translation, forced alignment, or video reframing is included.
Music, overlapping voices, silence, and punctuation can produce recognition
errors or hallucinations. Review the subtitles and timing before publishing.
SRT/VTT do not retain ASS styles. ASS timestamps have centisecond precision;
events shorter than that may disappear after rounding. Original input media is
never overwritten. The package itself has no network-calling code, but installation
and external model acquisition are separate online steps.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, offline tests, lint/type checks,
and the staged credential guard. CI covers Python 3.10 and 3.12 on Linux and
Windows, without models. `python -m pytest -m slow` selects the opt-in local-model
smoke test; no model or real recording is bundled. Keep examples synthetic and
the English and Turkish READMEs in sync. Released under the [MIT License](LICENSE).
