# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-23

### Added
- **Offline Speech Recognition**: Local Turkish speech-to-text with faster-whisper, word timestamps, Silero VAD filtering, and automatic CPU int8 fallback when CUDA is unavailable.
- **Vertical Video Layout Engine**: Constraint-driven text layout optimized for 9:16 vertical video (18 chars/line, 1–4 lines, pause thresholds, reading speed targets).
- **Turkish Linguistic Rules**: Punctuation-aware cue breaks, prevention of stranded conjunctions (`ve`, `ama`, `ki`, `de`/`da`) at line ends, and correct dotted/dotless I uppercase mapping (`i→İ`, `ı→I`).
- **Multi-Format Subtitle Exporters**: Output generators for SRT, WebVTT, and styled ASS with active-word karaoke animations and silence intervals.
- **Local ffmpeg Video Burn-in**: Direct subtitle hardcoding (`--burn`) using libass and `yuv420p` pixel format, hardened against paths with drive letters, spaces, and quotes.
- **Decoupled Re-layout Workflow**: `--save-words` and `--words-json` options to persist recognized tokens and experiment with layout rules and styles without reloading the model.
- **Configurable ASS Styles**: Customizable JSON and YAML style definitions with font, outline, size, color, and vertical positions (`bottom`, `middle`, `upper`).
- **Execution Reports & Error Handling**: Comprehensive exit codes (0, 1, 2), actionable error messages, and `--report json` documenting low-confidence words and layout warnings.
- **Developer Experience & Quality**: Terminal-style SVG demo generator (`scripts/make-demo.py`), unit test suite with >98% coverage, strict typechecking (mypy strict), Ruff linting, Dependabot, CodeQL workflow, and multi-OS CI matrix (Ubuntu, Windows) across Python 3.10, 3.12, and 3.14.
- **Documentation**: Comprehensive documentation in both English (`README.md`) and Turkish (`README.tr.md`), contributing guidelines, code of conduct, and security policy.

[Unreleased]: https://github.com/YusufBeratZengin/altyazi-tr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YusufBeratZengin/altyazi-tr/releases/tag/v0.1.0
