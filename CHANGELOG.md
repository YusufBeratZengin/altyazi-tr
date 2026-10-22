# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--words-json FILE` CLI option to layout and export subtitles from a pre-saved word list without loading faster-whisper.
- `--save-words FILE` CLI option to persist recognized word tokens with timestamps and confidence scores.
- Real deterministic demo output and excerpts (`sample.srt`, `sample.vtt`, `sample.ass`, `report.json`) in `docs/examples/`.
- Release workflow (`.github/workflows/release.yml`) for PyPI trusted publishing and GitHub releases on tag push.
- Comprehensive exit-code reference table (0 success, 1 processing error, 2 argument error) in documentation.
- Detailed `--report json` schema reference with example in documentation.
- Community health files: SECURITY.md, CODE_OF_CONDUCT.md, issue templates for bug reports and feature requests, and pull request template.
- Python 3.14 testing in CI matrix (Ubuntu) and separate clean-venv wheel installation check.
- Package metadata in `pyproject.toml`: Source and Changelog URLs, keywords, and classifiers.

### Changed
- Converted CHANGELOG to Keep a Changelog standard format with version compare links.
- Replaced static CI status badge with live GitHub Actions status badge in English and Turkish READMEs.
- Hardened ffmpeg subtitle burn filter against complex Windows paths containing drive letters, spaces, and apostrophes.
- Actionable error messages for missing models, empty audio files, and unsupported languages without raw tracebacks.
- Documented release process and added version consistency tests in `CONTRIBUTING.md`.

### Fixed
- Prevent sentence-final conjunctions ("de.", "ki.") from being carried into the next cue and falsely reported as trailing conjunctions.
- Apply Turkish dotted/dotless I mapping to `--upper` only for Turkic languages (`--lang tr`, `az`).
- Ensure media duration is never reported shorter than the last decoded word timestamp.
- Burn subtitles using `yuv420p` pixel format for broad media player compatibility.

## [0.1.0] - 2026-10-22

### Added
- Offline faster-whisper transcription with word timestamps, VAD, and CPU int8 fallback.
- Pure Turkish subtitle layout with punctuation, pause, conjunction, and reading speed rules.
- SRT, WebVTT, and styled ASS output with timed active-word karaoke highlights.
- Local ffmpeg video burn-in, JSON/YAML styles, and low-confidence JSON reports.
- English and Turkish documentation, offline unit tests, and CI.

[Unreleased]: https://github.com/YusufBeratZengin/altyazi-tr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YusufBeratZengin/altyazi-tr/releases/tag/v0.1.0
