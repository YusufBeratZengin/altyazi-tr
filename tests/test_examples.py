import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from altyazi_tr import LayoutConfig, __version__, layout
from altyazi_tr.layout import layout_warnings
from scripts.make_examples import SAMPLE_WORDS, generate


class ExamplesTests(unittest.TestCase):
    def test_deterministic_regeneration(self) -> None:
        examples_dir = Path("docs/examples")
        self.assertTrue(examples_dir.is_dir(), "docs/examples must exist.")

        with tempfile.TemporaryDirectory(prefix="altyazi-test-examples-") as tmp:
            tmp_path = Path(tmp)
            generate(tmp_path)

            for filename in ("sample.srt", "sample.vtt", "sample.ass", "report.json"):
                with self.subTest(file=filename):
                    expected = (examples_dir / filename).read_text(encoding="utf-8")
                    actual = (tmp_path / filename).read_text(encoding="utf-8")
                    self.assertEqual(actual, expected)

    def test_report_json_schema(self) -> None:
        report_path = Path("docs/examples/report.json")
        self.assertTrue(report_path.is_file(), "docs/examples/report.json must exist.")
        data = json.loads(report_path.read_text(encoding="utf-8"))

        expected_keys = {
            "version",
            "language",
            "duration",
            "device",
            "compute_type",
            "cue_count",
            "confidence_threshold",
            "low_confidence_words",
            "layout_warnings",
        }
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertEqual(data["version"], __version__)
        self.assertIsInstance(data["language"], str)
        self.assertIsInstance(data["duration"], (int, float))
        self.assertIsInstance(data["cue_count"], int)
        self.assertIsInstance(data["confidence_threshold"], (int, float))
        self.assertIsInstance(data["low_confidence_words"], list)
        self.assertIsInstance(data["layout_warnings"], list)

        word_keys = {"start", "end", "text", "prob"}
        for word_dict in data["low_confidence_words"]:
            self.assertEqual(set(word_dict.keys()), word_keys)

        # Validate that the keys match what the CLI generates directly
        config = LayoutConfig(mode="words", upper=True, turkish_case=True)
        cues = layout(SAMPLE_WORDS, config, duration=7.20)
        cli_emitted_report = {
            "version": __version__,
            "language": "tr",
            "duration": 7.20,
            "device": "cpu",
            "compute_type": "int8",
            "cue_count": len(cues),
            "confidence_threshold": 0.6,
            "low_confidence_words": [asdict(w) for w in SAMPLE_WORDS if w.prob < 0.6],
            "layout_warnings": layout_warnings(cues, config),
        }
        self.assertEqual(set(data.keys()), set(cli_emitted_report.keys()))
