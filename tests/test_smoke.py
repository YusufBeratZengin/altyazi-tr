"""Opt-in local fixture only: pytest -m slow, with both environment paths set."""

import os
import unittest
from pathlib import Path

from altyazi_tr.transcribe import transcribe


@unittest.skipUnless(
    os.environ.get("ALTYAZI_TEST_MODEL") and os.environ.get("ALTYAZI_TEST_AUDIO"),
    "Set ALTYAZI_TEST_MODEL and ALTYAZI_TEST_AUDIO to local, synthetic fixtures.",
)
class LocalModelSmokeTest(unittest.TestCase):
    def test_local_model(self) -> None:
        model = Path(os.environ["ALTYAZI_TEST_MODEL"])
        self.assertTrue(model.is_dir(), "Smoke model must be a local directory.")
        result = transcribe(Path(os.environ["ALTYAZI_TEST_AUDIO"]), model=str(model), device="cpu")
        self.assertTrue(result.words, "Use a synthetic speech fixture, not silence.")
