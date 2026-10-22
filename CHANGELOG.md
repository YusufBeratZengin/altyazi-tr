# Changelog

## Unreleased

- Fix a sentence-final "de." or "ki." being carried into the next cue and falsely reported as a trailing conjunction.
- Apply the Turkish dotted/dotless I mapping to `--upper` only for `--lang tr`/`az`.
- Never report a media duration shorter than the last decoded word.
- Burn with `yuv420p` so the output plays in common players.

## 0.1.0 - 2026-10-22

- Add offline faster-whisper transcription with word timestamps, VAD, and CPU int8 fallback.
- Add pure Turkish subtitle layout with punctuation, pause, conjunction, and reading rules.
- Add SRT, WebVTT, and styled ASS output with timed active-word colors.
- Add local ffmpeg burning, JSON/YAML styles, and low-confidence JSON reports.
- Add English and Turkish documentation, offline unit tests, and CI.
