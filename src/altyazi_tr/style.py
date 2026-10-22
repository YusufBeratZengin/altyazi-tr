"""Validated ASS appearance, loaded from JSON or optional safe YAML."""

import json
import re
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Style:
    font: str = "DejaVu Sans"
    font_size: int = 72
    primary_color: str = "&H00FFFFFF"
    highlight_color: str = "&H0000FFFF"
    outline_color: str = "&H00000000"
    outline: int = 4
    bold: bool = True
    position: Literal["bottom", "middle", "upper"] = "bottom"
    margin_v: int = 320

    def __post_init__(self) -> None:
        if not isinstance(self.font, str) or not self.font.strip() or any(
            char in self.font for char in ",\n\r{}\\"
        ):
            raise ValueError("Font must be a non-empty name without ASS separators.")
        for name, low, high in (("font_size", 1, 300), ("outline", 0, 20), ("margin_v", 0, 900)):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer between {low} and {high}.")
        for name in ("primary_color", "highlight_color", "outline_color"):
            value = getattr(self, name)
            if not isinstance(value, str) or re.fullmatch(r"&H[0-9a-fA-F]{8}", value) is None:
                raise ValueError(f"{name} must be an ASS &HAABBGGRR color.")
        if type(self.bold) is not bool:
            raise ValueError("bold must be a boolean.")
        if self.position not in ("bottom", "middle", "upper"):
            raise ValueError("position must be bottom, middle, or upper.")


def load_style(path: Path) -> Style:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as exc:
            raise ValueError("YAML styles require the 'yaml' extra; JSON needs no extra.") from exc
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError("Style YAML is invalid or contains unsafe tags.") from exc
    else:
        raise ValueError("Style file must be JSON or YAML.")
    if not isinstance(data, dict) or any(not isinstance(key, str) for key in data):
        raise ValueError("Style must be a mapping with string keys.")
    unknown = set(data) - {field.name for field in fields(Style)}
    if unknown:
        raise ValueError("Unknown style fields: " + ", ".join(sorted(unknown)))
    return Style(**data)
