"""Wrap a diagram SVG into the site's dark-theme card HTML.

Reads an SVG file (exported from a .drawio / .excalidraw source) and emits a
self-contained images/<name>.html matching the look of the hand-authored
diagrams — the same .diagram-card shell index.html embeds via <iframe>.

Usage: uv run python scripts/wrap_diagram.py <input.svg> <output.html> [--title "..."]

Called by the `just diagrams` recipe; not usually run by hand.
"""

import argparse
import re
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: #1b1f28;
    color: #e8eaed;
  }}
  .diagram-card {{
    padding: 16px;
  }}
  .diagram-card svg {{
    display: block;
    width: 100%;
    height: auto;
  }}
</style>
</head>
<body>
  <div class="diagram-card">
{svg}<!-- codespell:ignore -->
  </div>
</body>
</html>
"""


def extract_svg(raw: str) -> str:
    """Return just the <svg>...</svg> element, dropping any XML/doctype prolog."""
    match = re.search(r"<svg\b.*?</svg>", raw, re.DOTALL | re.IGNORECASE)
    if not match:
        raise SystemExit("no <svg> element found in input")
    svg = match.group(0)
    # Let the responsive CSS (width:100%) drive size instead of fixed px.
    svg = re.sub(r'(<svg\b[^>]*?)\s+width="[^"]*"', r"\1", svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\s+height="[^"]*"', r"\1", svg, count=1)
    return svg


def title_from_name(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("svg", type=Path, help="input SVG file")
    ap.add_argument("html", type=Path, help="output HTML file")
    ap.add_argument("--title", help="page <title> (default: derived from filename)")
    args = ap.parse_args()

    svg = extract_svg(args.svg.read_text(encoding="utf-8"))
    title = args.title or title_from_name(args.html)
    args.html.write_text(TEMPLATE.format(title=title, svg=svg), encoding="utf-8")
    print(f"wrote {args.html} ({args.html.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
