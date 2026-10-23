"""Generate a static terminal-style demo SVG showing CLI usage and real output."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path


def capture_help_output() -> list[str]:
    """Run CLI to capture real output and trim to ~18-20 lines."""
    cmd = [sys.executable, "-m", "altyazi_tr", "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    raw_lines = result.stdout.strip().splitlines()

    # Capture real lines: usage summary, description, and key options
    selected: list[str] = []

    # 1. First 4 lines of usage
    selected.extend(raw_lines[:4])
    selected.append("                  [--burn] [--upper] [--report {json}] [input]")
    selected.append("")
    selected.append(raw_lines[12])  # "Create offline, word-timed subtitles from local media."
    selected.append("")
    selected.append("options:")

    # Key options from real output
    key_options = [
        "-h, --help",
        "-o, --output",
        "--format",
        "--model",
        "--mode",
        "--upper",
        "--burn",
        "--style",
        "--report",
        "--words-json",
    ]

    for line in raw_lines[18:]:
        stripped = line.strip()
        for opt in key_options:
            if stripped.startswith(opt):
                selected.append(line)
                break

    return selected


def build_svg(lines: list[str]) -> str:
    """Render terminal lines into an SVG with dark background, rounded window, and 3 dots."""
    width = 820
    header_height = 40
    padding_x = 24
    padding_top = 68
    line_height = 20
    font_size = 13

    # Total height: header + content + bottom padding
    total_lines = len(lines) + 1  # +1 for prompt line
    height = padding_top + (total_lines * line_height) + 16

    content_spans: list[str] = []

    # Command prompt line
    prompt_y = padding_top
    content_spans.append(
        f'  <text x="{padding_x}" y="{prompt_y}">'
        f'<tspan fill="#3fb950" font-weight="bold">$ </tspan>'
        f'<tspan fill="#f0f6fc" font-weight="bold">altyazi-tr </tspan>'
        f'<tspan fill="#79c0ff">--help</tspan>'
        f"</text>"
    )

    for i, line in enumerate(lines, 1):
        y = padding_top + (i * line_height)
        if not line.strip():
            continue

        escaped = html.escape(line)

        if line.startswith("usage:"):
            styled = (
                f'<tspan fill="#ff7b72" font-weight="bold">usage: </tspan>'
                f'<tspan fill="#c9d1d9">{html.escape(line[len("usage:") :])}</tspan>'
            )
        elif line.startswith("positional arguments:") or line.startswith("options:"):
            styled = f'<tspan fill="#d2a8ff" font-weight="bold">{escaped}</tspan>'
        elif line.strip().startswith("-"):
            # Option flag and description
            indent = " " * (len(line) - len(line.lstrip()))
            parts = re.split(r"\s{2,}", line.strip(), maxsplit=1)
            flag = html.escape(indent + parts[0])
            desc = html.escape("   " + parts[1]) if len(parts) > 1 else ""
            styled = (
                f'<tspan fill="#79c0ff" font-weight="500">{flag}</tspan>'
                f'<tspan fill="#8b949e">{desc}</tspan>'
            )
        elif line.startswith("                  "):
            styled = f'<tspan fill="#8b949e">{escaped}</tspan>'
        elif "Create offline" in line:
            styled = f'<tspan fill="#a5d6ff" font-weight="500">{escaped}</tspan>'
        else:
            styled = f'<tspan fill="#c9d1d9">{escaped}</tspan>'

        content_spans.append(f'  <text x="{padding_x}" y="{y}">{styled}</text>')

    body_content = "\n".join(content_spans)
    title_font = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    mono_font = "ui-monospace, 'SF Mono', 'Cascadia Code', 'Fira Code', Menlo, Consolas, monospace"

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="altyazi-tr CLI demo">\n'
        f"  <defs>\n"
        f'    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">\n'
        f'      <feDropShadow dx="0" dy="6" stdDeviation="12" '
        f'flood-color="#000000" flood-opacity="0.4"/>\n'
        f"    </filter>\n"
        f"  </defs>\n\n"
        f"  <!-- Terminal Window Background -->\n"
        f'  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" ry="10" '
        f'fill="#0d1117" stroke="#30363d" stroke-width="1.2" filter="url(#shadow)"/>\n\n'
        f"  <!-- Window Header / Title Bar -->\n"
        f'  <path d="M 1 11 A 10 10 0 0 1 11 1 L {width - 11} 1 A 10 10 0 0 1 {width - 1} 11 '
        f'L {width - 1} {header_height} L 1 {header_height} Z" fill="#161b22"/>\n'
        f'  <line x1="1" y1="{header_height}" x2="{width - 1}" y2="{header_height}" '
        f'stroke="#30363d" stroke-width="1"/>\n\n'
        f"  <!-- Window Controls (3 dots: Red, Yellow, Green) -->\n"
        f'  <circle cx="20" cy="20" r="5.5" fill="#ff5f56" stroke="#e0443e" '
        f'stroke-width="0.5"/>\n'
        f'  <circle cx="38" cy="20" r="5.5" fill="#ffbd2e" stroke="#dea123" '
        f'stroke-width="0.5"/>\n'
        f'  <circle cx="56" cy="20" r="5.5" fill="#27c93f" stroke="#1aab29" '
        f'stroke-width="0.5"/>\n\n'
        f"  <!-- Centered Window Title -->\n"
        f'  <text x="{width // 2}" y="24" text-anchor="middle" fill="#8b949e" '
        f'font-family="{title_font}" font-size="12" font-weight="500">'
        f"altyazi-tr — terminal</text>\n\n"
        f"  <!-- Monospace Terminal Lines -->\n"
        f'  <g font-family="{mono_font}" font-size="{font_size}" xml:space="preserve">\n'
        f"{body_content}\n"
        f"  </g>\n"
        f"</svg>\n"
    )
    return svg


def main() -> int:
    dest = Path("docs/demo.svg")
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = capture_help_output()
    svg = build_svg(lines)
    dest.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Generated {dest} ({len(lines) + 1} terminal lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
