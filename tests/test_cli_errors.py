import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from altyazi_tr.cli import main


class CLIErrorsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.out_patch = redirect_stdout(self.stdout)
        self.err_patch = redirect_stderr(self.stderr)
        self.out_patch.__enter__()
        self.err_patch.__enter__()
        self.addCleanup(self.err_patch.__exit__, None, None, None)
        self.addCleanup(self.out_patch.__exit__, None, None, None)
        os.environ["HF_HUB_OFFLINE"] = "1"

    def test_missing_model_actionable_message(self) -> None:
        with tempfile.TemporaryDirectory(prefix="altyazi-test-model-") as folder:
            media = Path(folder) / "sample.mp4"
            media.write_bytes(b"dummy-audio-bytes")

            code = main([str(media), "--model", "nonexistent-model-xyz"])
            self.assertEqual(code, 1)
            err = self.stderr.getvalue()
            self.assertIn("--model", err)
            self.assertIn("offline", err.lower())
            self.assertNotIn("Traceback", err)

    def test_empty_audio_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="altyazi-test-empty-") as folder:
            media = Path(folder) / "empty.mp4"
            media.write_bytes(b"")  # 0 bytes

            code = main([str(media)])
            self.assertEqual(code, 1)
            err = self.stderr.getvalue()
            self.assertIn("empty", err.lower())
            self.assertNotIn("Traceback", err)

    def test_output_exists_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="altyazi-test-out-") as folder:
            media = Path(folder) / "sample.mp4"
            media.write_bytes(b"dummy-audio-bytes")
            existing_out = Path(folder) / "sample.srt"
            existing_out.write_text("existing content", encoding="utf-8")

            code = main([str(media)])
            self.assertEqual(code, 1)
            err = self.stderr.getvalue()
            self.assertIn("Output files must be new and distinct", err)
            self.assertNotIn("Traceback", err)

    def test_style_unknown_field(self) -> None:
        with tempfile.TemporaryDirectory(prefix="altyazi-test-style-") as folder:
            media = Path(folder) / "sample.mp4"
            media.write_bytes(b"dummy-audio-bytes")
            style_file = Path(folder) / "bad_style.json"
            style_file.write_text('{"unknown_color_attr": 42}', encoding="utf-8")

            code = main([str(media), "--style", str(style_file)])
            self.assertEqual(code, 1)
            err = self.stderr.getvalue()
            self.assertIn("Unknown style fields: unknown_color_attr", err)
            self.assertNotIn("Traceback", err)

    def test_unsupported_language(self) -> None:
        with tempfile.TemporaryDirectory(prefix="altyazi-test-lang-") as folder:
            media = Path(folder) / "sample.mp4"
            media.write_bytes(b"dummy-audio-bytes")

            code = main([str(media), "--lang", "klingon"])
            self.assertEqual(code, 1)
            err = self.stderr.getvalue()
            self.assertIn("Language 'klingon' is not supported", err)
            self.assertNotIn("Traceback", err)

    def test_exit_codes(self) -> None:
        # Exit code 2: argument parsing error
        with self.assertRaises(SystemExit) as exc:
            main([])
        self.assertEqual(exc.exception.code, 2)

        with self.assertRaises(SystemExit) as exc:
            main(["invented.mp4", "--format", "unsupported_fmt"])
        self.assertEqual(exc.exception.code, 2)
