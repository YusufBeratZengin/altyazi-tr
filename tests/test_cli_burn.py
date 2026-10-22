import io
import json
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from altyazi_tr import Word
from altyazi_tr.burn import burn, find_ffmpeg
from altyazi_tr.cli import main
from altyazi_tr.transcribe import Transcript


class CapturedFile(io.StringIO):
    def close(self) -> None:
        # Retain text for assertions after the application's context manager exits.
        pass


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = {}
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        self.transcript = Transcript((Word(0, 0.4, "iyi", 0.3), Word(0.5, 1, "ışık")),
                                     "tr", 2, "cpu", "int8")
        self.asr = MagicMock(return_value=self.transcript)

        def open_output(path, *args, **kwargs):
            self.assertEqual(args[0], "x")
            self.assertEqual(kwargs["encoding"], "utf-8")
            result = CapturedFile()
            self.files[path.name] = result
            return result

        patches = [
            patch("altyazi_tr.cli.transcribe", self.asr),
            patch.object(Path, "is_file", return_value=True),
            patch.object(Path, "exists", return_value=False),
            patch.object(Path, "mkdir"),
            patch.object(Path, "open", open_output),
            redirect_stdout(self.stdout), redirect_stderr(self.stderr),
        ]
        for item in patches:
            item.__enter__()
            self.addCleanup(item.__exit__, None, None, None)

    def test_all_formats_and_report(self) -> None:
        code = main(["invented.mp4", "-o", "out/demo", "--format", "all", "--upper",
                     "--mode", "words", "--report", "json"])
        self.assertEqual(code, 0, self.stderr.getvalue())
        self.assertEqual(set(self.files), {"demo.srt", "demo.vtt", "demo.ass", "demo.report.json"})
        self.assertIn("İYİ", self.files["demo.srt"].getvalue())
        self.assertIn(r"\1c", self.files["demo.ass"].getvalue())
        report = json.loads(self.files["demo.report.json"].getvalue())
        self.assertEqual(report["low_confidence_words"], [
            {"start": 0, "end": 0.4, "text": "iyi", "prob": 0.3}
        ])
        self.assertEqual(report["device"], "cpu")

    def test_output_suffix_and_multiple_dots(self) -> None:
        self.assertEqual(main(["invented.mp4", "-o", "clip.v1.srt"]), 0)
        self.assertEqual(set(self.files), {"clip.v1.srt"})

    def test_style_file_applied(self) -> None:
        with patch.object(Path, "read_text", return_value='{"font_size":60,"bold":false}'):
            self.assertEqual(main(["invented.mp4", "--format", "ass", "--style", "style.json"]), 0)
        self.assertIn("Default,DejaVu Sans,60,", self.files["invented.ass"].getvalue())

    def test_invalid_yaml_is_a_processing_error(self) -> None:
        with patch("altyazi_tr.cli.load_style", side_effect=ValueError("Style YAML is invalid")):
            self.assertEqual(main(["invented.mp4", "--style", "invalid.yaml"]), 1)
        self.asr.assert_not_called()

    def test_silence_outputs_and_report(self) -> None:
        self.asr.return_value = Transcript((), "tr", 2, "cpu", "int8")
        self.assertEqual(main(["invented.mp4", "--report", "json"]), 0)
        self.assertEqual(self.files["invented.srt"].getvalue(), "")
        self.assertEqual(json.loads(self.files["invented.report.json"].getvalue())["cue_count"], 0)

    def test_burn_also_writes_ass(self) -> None:
        with patch("altyazi_tr.cli.burn") as render:
            self.assertEqual(main(["invented.mp4", "--burn", "--position", "upper"]), 0)
            self.assertIn("invented.ass", self.files)
            self.assertIn(",8,60,60,320,1", self.files["invented.ass"].getvalue())
            render.assert_called_once_with(Path("invented.mp4"), Path("invented.ass"),
                                           Path("invented.burned.mp4"))

    def test_invalid_layout_and_confidence_before_asr(self) -> None:
        for args in (["--max-chars", "0"], ["--max-lines", "0"], ["--max-cps", "nan"],
                     ["--confidence", "nan"], ["--confidence", "1.1"]):
            with self.subTest(args=args):
                self.assertEqual(main(["invented.mp4", *args]), 1)
        self.asr.assert_not_called()

    def test_missing_input(self) -> None:
        with patch.object(Path, "is_file", return_value=False):
            self.assertEqual(main(["missing.mp4"]), 1)
        self.asr.assert_not_called()

    def test_overwrite_refused_before_asr(self) -> None:
        with patch.object(Path, "exists", return_value=True):
            self.assertEqual(main(["invented.mp4"]), 1)
        self.asr.assert_not_called()

    def test_input_collision_refused(self) -> None:
        self.assertEqual(main(["invented.srt"]), 1)
        self.asr.assert_not_called()

    def test_asr_errors_are_english_and_nonzero(self) -> None:
        self.asr.side_effect = OSError("Model not cached")
        self.assertEqual(main(["invented.mp4"]), 1)
        self.assertIn("Error: Model not cached", self.stderr.getvalue())
        self.assertEqual(self.files, {})

    def test_invalid_arguments(self) -> None:
        with self.assertRaises(SystemExit) as exc:
            main(["invented.mp4", "--format", "xml"])
        self.assertEqual(exc.exception.code, 2)

    def test_options_forwarded(self) -> None:
        self.assertEqual(main(["invented.wav", "--lang", "en", "--device", "cpu",
                               "--compute-type", "float32", "--no-vad"]), 0)
        self.assertEqual(self.asr.call_args.kwargs["language"], "en")
        self.assertFalse(self.asr.call_args.kwargs["vad"])


class BurnTests(unittest.TestCase):
    def test_path_first(self) -> None:
        with patch("altyazi_tr.burn.shutil.which", return_value="system-ffmpeg"):
            self.assertEqual(find_ffmpeg(), "system-ffmpeg")

    def test_imageio_fallback(self) -> None:
        module = SimpleNamespace(get_ffmpeg_exe=lambda: "bundled-ffmpeg")
        with patch("altyazi_tr.burn.shutil.which", return_value=None), \
                patch.dict("sys.modules", {"imageio_ffmpeg": module}), \
                patch.object(Path, "is_file", return_value=True):
            self.assertEqual(find_ffmpeg(), "bundled-ffmpeg")

    def test_missing_ffmpeg(self) -> None:
        with patch("altyazi_tr.burn.shutil.which", return_value=None), \
                patch.dict("sys.modules", {"imageio_ffmpeg": None}), \
                self.assertRaises(RuntimeError):
            find_ffmpeg()

    def test_bundled_executable_missing(self) -> None:
        module = SimpleNamespace(get_ffmpeg_exe=lambda: "absent-ffmpeg")
        with patch("altyazi_tr.burn.shutil.which", return_value=None), \
                patch.dict("sys.modules", {"imageio_ffmpeg": module}), \
                patch.object(Path, "is_file", return_value=False), self.assertRaises(RuntimeError):
            find_ffmpeg()

    def test_missing_input(self) -> None:
        with patch.object(Path, "is_file", return_value=False), self.assertRaises(ValueError):
            burn(Path("in.mp4"), Path("in.ass"), Path("out.mp4"))

    def test_overwrite_refused(self) -> None:
        with patch.object(Path, "is_file", return_value=True), \
                patch.object(Path, "exists", return_value=True), self.assertRaises(ValueError):
            burn(Path("in.mp4"), Path("in.ass"), Path("out.mp4"))

    def test_command_uses_safe_relative_filter_and_argument_list(self) -> None:
        folder = MagicMock()
        folder.__enter__.return_value = "temporary-workspace"
        with patch.object(Path, "is_file", return_value=True), \
                patch.object(Path, "exists", return_value=False), patch.object(Path, "mkdir"), \
                patch("altyazi_tr.burn.find_ffmpeg", return_value="ffmpeg"), \
                patch("altyazi_tr.burn.tempfile.TemporaryDirectory", return_value=folder), \
                patch("altyazi_tr.burn.shutil.copyfile") as copy, \
                patch("altyazi_tr.burn.subprocess.run") as run:
            source = Path("invented ' [clip],.mp4")
            burn(source, Path("invented ' [,].ass"), Path("out.mp4"))
            args = run.call_args.args[0]
            self.assertIn(str(source.resolve()), args)
            self.assertIn("ass=captions.ass", args)
            self.assertIn("-n", args)
            self.assertNotIn("shell", run.call_args.kwargs)
            self.assertEqual(copy.call_args.args[1], Path("temporary-workspace/captions.ass"))
            run.side_effect = subprocess.CalledProcessError(1, args)
            with self.assertRaisesRegex(RuntimeError, "libass"):
                burn(source, Path("in.ass"), Path("other.mp4"))
