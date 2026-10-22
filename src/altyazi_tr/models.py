"""Immutable values shared by recognition, layout, and writers."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Word:
    start: float
    end: float
    text: str
    prob: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.start) or not isfinite(self.end) or not 0 <= self.start < self.end:
            raise ValueError("Word timestamps must be finite, non-negative, and increasing.")
        if not self.text or any(char.isspace() for char in self.text):
            raise ValueError("Word text must be a non-empty token without whitespace.")
        if not isfinite(self.prob) or not 0 <= self.prob <= 1:
            raise ValueError("Word probability must be between 0 and 1.")


@dataclass(frozen=True)
class Cue:
    start: float
    end: float
    lines: tuple[tuple[Word, ...], ...]

    def __post_init__(self) -> None:
        if not isfinite(self.start) or not isfinite(self.end) or not 0 <= self.start < self.end:
            raise ValueError("Cue timestamps must be finite, non-negative, and increasing.")
        if not self.lines or any(not line for line in self.lines):
            raise ValueError("Cue lines must not be empty.")
        words = self.words
        if self.start > words[0].start or self.end < words[-1].end:
            raise ValueError("Cue must contain its word timestamps.")
        if any(left.end > right.start for left, right in zip(words, words[1:], strict=False)):
            raise ValueError("Cue words must be chronological and non-overlapping.")

    @property
    def words(self) -> tuple[Word, ...]:
        return tuple(word for line in self.lines for word in line)

    @property
    def text(self) -> str:
        return "\n".join(" ".join(word.text for word in line) for line in self.lines)
