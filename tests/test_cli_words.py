import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from altyazi_tr import Word
from altyazi_tr.cli import main
from altyazi_tr.transcribe import Transcript


class CLIWordsTests(unittest.TestCase):
    def test_words_json_without_importing_faster_whisper(self) -> None:
        # Verify that faster_whisper has not been imported yet
        self.assertNotIn("faster_whisper", sys.modules)

        words_data = [
            {"start": 0.0, "end": 0.42, "text": "Bugün", "prob": 0.98},
            {"start": 0.48, "end": 0.95, "text": "dikey", "prob": 0.97},
            {"start": 1.02, "end": 1.60, "text": "videolar", "prob": 0.95},
        ]

        with tempfile.TemporaryDirectory(prefix="altyazi-words-") as folder:
            words_file = Path(folder) / "input_words.json"
            words_file.write_text(json.dumps(words_data), encoding="utf-8")
            out_prefix = Path(folder) / "out_captions"

            # Run CLI with --words-json
            code = main(
                [
                    "--words-json",
                    str(words_file),
                    "-o",
                    str(out_prefix),
                    "--format",
                    "all",
                    "--report",
                    "json",
                ]
            )
            self.assertEqual(code, 0)

            # Confirm output files exist
            srt_path = Path(folder) / "out_captions.srt"
            vtt_path = Path(folder) / "out_captions.vtt"
            ass_path = Path(folder) / "out_captions.ass"
            rep_path = Path(folder) / "out_captions.report.json"
            self.assertTrue(srt_path.is_file())
            self.assertTrue(vtt_path.is_file())
            self.assertTrue(ass_path.is_file())
            self.assertTrue(rep_path.is_file())

            srt_text = srt_path.read_text(encoding="utf-8")
            self.assertIn("Bugün dikey", srt_text)

            report = json.loads(rep_path.read_text(encoding="utf-8"))
            self.assertEqual(report["cue_count"], 1)
            self.assertEqual(report["device"], "none")

            # CRITICAL ACCEPTANCE CHECK: faster_whisper must NOT be loaded into sys.modules
            self.assertNotIn("faster_whisper", sys.modules)

    def test_save_words_and_reload(self) -> None:
        transcript = Transcript(
            (
                Word(0.0, 0.4, "iyi", 0.95),
                Word(0.5, 1.0, "ışık", 0.90),
            ),
            "tr",
            2.0,
            "cpu",
            "int8",
        )
        with tempfile.TemporaryDirectory(prefix="altyazi-save-words-") as folder:
            media = Path(folder) / "dummy.mp4"
            media.write_bytes(b"dummy-audio-content")
            saved_words = Path(folder) / "saved_words.json"

            with patch("altyazi_tr.cli.transcribe", MagicMock(return_value=transcript)):
                code = main(
                    [
                        str(media),
                        "--save-words",
                        str(saved_words),
                        "-o",
                        str(Path(folder) / "out"),
                    ]
                )
                self.assertEqual(code, 0)

            self.assertTrue(saved_words.is_file())
            loaded = json.loads(saved_words.read_text(encoding="utf-8"))
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0]["text"], "iyi")
            self.assertEqual(loaded[1]["text"], "ışık")
            self.assertEqual(loaded[0]["prob"], 0.95)

            # Re-layout using the saved file
            reout = Path(folder) / "reout"
            code2 = main(
                [
                    "--words-json",
                    str(saved_words),
                    "-o",
                    str(reout),
                    "--format",
                    "srt",
                    "--upper",
                ]
            )
            self.assertEqual(code2, 0)
            srt_content = (Path(folder) / "reout.srt").read_text(encoding="utf-8")
            self.assertIn("İYİ IŞIK", srt_content)
