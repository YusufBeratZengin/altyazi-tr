"""Pure UTF-8 subtitle serializers. ASS highlights only the active word."""

import html
from collections.abc import Sequence

from .models import Cue, Word
from .style import Style


def _stamp(seconds: float, *, ass: bool = False, comma: bool = False) -> str:
    scale = 100 if ass else 1000
    ticks = round(seconds * scale)
    hours, ticks = divmod(ticks, 3600 * scale)
    minutes, ticks = divmod(ticks, 60 * scale)
    secs, fraction = divmod(ticks, scale)
    if ass:
        return f"{hours}:{minutes:02}:{secs:02}.{fraction:02}"
    separator = "," if comma else "."
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{fraction:03}"


def _plain(text: str) -> str:
    # Both formats support markup. Escape decoder text, never execute it as tags.
    return html.escape(text, quote=False)


def srt(cues: Sequence[Cue]) -> str:
    return "".join(
        f"{i}\n{_stamp(c.start, comma=True)} --> {_stamp(c.end, comma=True)}\n"
        f"{_plain(c.text)}\n\n" for i, c in enumerate(cues, 1)
    )


def vtt(cues: Sequence[Cue]) -> str:
    return "WEBVTT\n\n" + "".join(
        f"{_stamp(c.start)} --> {_stamp(c.end)}\n{_plain(c.text)}\n\n" for c in cues
    )


def _ass_text(text: str) -> str:
    # Use fullwidth lookalikes so untrusted decoder text cannot introduce overrides
    # or ASS hard breaks. Intentional breaks are added by the serializer itself.
    return text.translate(str.maketrans("\\{}", "＼｛｝"))


def _render(cue: Cue, active: Word | None, style: Style) -> str:
    def token(word: Word) -> str:
        text = _ass_text(word.text)
        if word is active:
            # Inline color syntax uses BBGGRR; style header also carries alpha.
            color = style.highlight_color[4:]
            alpha = style.highlight_color[2:4]
            return f"{{\\1c&H{color}&\\1a&H{alpha}&}}{text}{{\\rDefault}}"
        return text

    return r"\N".join(" ".join(token(w) for w in line) for line in cue.lines)


def ass(cues: Sequence[Cue], *, style: Style | None = None, karaoke: bool = False) -> str:
    style = style or Style()
    alignment = {"bottom": 2, "middle": 5, "upper": 8}[style.position]
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n"
        "WrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{style.font},{style.font_size},{style.primary_color},"
        f"{style.highlight_color},{style.outline_color},&H80000000,"
        f"{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline},0,"
        f"{alignment},60,60,{style.margin_v},1\n\n[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = []
    for cue in cues:
        cuts = sorted({cue.start, cue.end} | (
            {time for w in cue.words for time in (w.start, w.end)} if karaoke else set()
        ))
        for start, end in zip(cuts, cuts[1:], strict=False):
            if _stamp(start, ass=True) == _stamp(end, ass=True):
                continue
            active = next((w for w in cue.words if w.start <= start < w.end), None)
            text = _render(cue, active if karaoke else None, style)
            events.append(
                f"Dialogue: 0,{_stamp(start, ass=True)},{_stamp(end, ass=True)},"
                f"Default,,0,0,0,,{text}\n"
            )
    return header + "".join(events)
