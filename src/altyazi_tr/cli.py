"""Command line orchestration with no network or model download option."""

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, replace
from pathlib import Path

from . import __version__, writers
from .burn import burn
from .layout import LayoutConfig, layout, layout_warnings
from .style import Style, load_style
from .transcribe import transcribe


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="altyazi-tr", description="Create offline, word-timed subtitles from local media."
    )
    result.add_argument("input", type=Path)
    result.add_argument(
        "-o", "--output", type=Path, help="Output filename or stem (default: input stem)"
    )
    result.add_argument("--format", choices=("srt", "vtt", "ass", "all"), default="srt")
    result.add_argument(
        "--model", default="small", help="Cached model name or local model directory"
    )
    result.add_argument("--mode", choices=("words", "groups"), default="groups")
    result.add_argument("--max-chars", type=int, default=18)
    result.add_argument("--max-lines", type=int, default=2)
    result.add_argument("--pause-threshold", type=float, default=0.6)
    result.add_argument("--min-duration", type=float, default=0.8)
    result.add_argument("--max-cps", type=float, default=18.0)
    result.add_argument("--upper", action="store_true")
    result.add_argument("--burn", action="store_true", help="Also create <stem>.burned.mp4")
    result.add_argument("--lang", default="tr")
    result.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    result.add_argument("--compute-type", default=None)
    result.add_argument("--no-vad", action="store_true")
    result.add_argument("--style", type=Path, help="ASS style JSON or YAML")
    result.add_argument("--position", choices=("bottom", "middle", "upper"))
    result.add_argument("--report", choices=("json",), help="Write <stem>.report.json")
    result.add_argument("--confidence", type=float, default=0.6)
    result.add_argument("--version", action="version", version=__version__)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if not args.input.is_file():
            raise ValueError("Input must be an existing local media file.")
        config = LayoutConfig(
            max_chars=args.max_chars, max_lines=args.max_lines,
            pause_threshold=args.pause_threshold,
            min_duration=args.min_duration, max_cps=args.max_cps, mode=args.mode, upper=args.upper,
            # Dotted/dotless I mapping is wrong outside Turkic languages.
            turkish_case=args.lang.strip().lower().split("-")[0] in ("tr", "az"),
        )
        if not 0 <= args.confidence <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1.")
        style = load_style(args.style) if args.style else Style()
        if args.position:
            style = replace(style, position=args.position)
        target = args.output or args.input.with_suffix("")
        stem = (
            target.with_suffix("") if target.suffix.lower() in (".srt", ".vtt", ".ass") else target
        )
        formats: tuple[str, ...] = (
            ("srt", "vtt", "ass") if args.format == "all" else (args.format,)
        )
        if args.burn and "ass" not in formats:
            formats += ("ass",)
        outputs = {fmt: Path(str(stem) + "." + fmt) for fmt in formats}
        report_path = Path(str(stem) + ".report.json")
        burned_path = Path(str(stem) + ".burned.mp4")
        planned = list(outputs.values())
        if args.report:
            planned.append(report_path)
        if args.burn:
            planned.append(burned_path)
        protected = {args.input.resolve()}
        if args.style:
            protected.add(args.style.resolve())
        if any(p.exists() or p.resolve() in protected for p in planned):
            raise ValueError("Output files must be new and distinct from input and style files.")
        transcript = transcribe(
            args.input, model=args.model, device=args.device, compute_type=args.compute_type,
            language=args.lang, vad=not args.no_vad,
        )
        cues = layout(transcript.words, config, duration=transcript.duration)
        warnings = layout_warnings(cues, config)
        for fmt, path in outputs.items():
            text = (
                writers.ass(cues, style=style, karaoke=args.mode == "words") if fmt == "ass"
                else writers.srt(cues) if fmt == "srt" else writers.vtt(cues)
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
        if args.report:
            report = {
                "version": __version__, "language": transcript.language,
                "duration": transcript.duration, "device": transcript.device,
                "compute_type": transcript.compute_type, "cue_count": len(cues),
                "confidence_threshold": args.confidence,
                "low_confidence_words": [
                    asdict(w) for w in transcript.words if w.prob < args.confidence
                ],
                "layout_warnings": warnings,
            }
            with report_path.open("x", encoding="utf-8", newline="\n") as handle:
                json.dump(report, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
        if args.burn:
            burn(args.input, outputs["ass"], burned_path)
        print(f"Created {len(cues)} subtitle cues.")
        if warnings:
            print(
                f"Warning: {len(warnings)} cues exceed layout targets; use --report json.",
                file=sys.stderr,
            )
        return 0
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
