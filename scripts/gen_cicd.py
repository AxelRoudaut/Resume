"""Generate images/cicd-security-pipeline.html — a dark-theme SVG diagram of the
GitLab CI dependency-packaging + air-gap replication + security-scanning pipeline.

Authored directly in the site's dark palette (css/style.css design tokens) so no
post-hoc recolor pass is needed. Run: uv run python tmp/gen_cicd.py
"""

from html import escape
from pathlib import Path

W, H = 2000, 1180

# --- site design tokens (css/style.css) ---
CARD = "#1b1f28"
CARD2 = "#20242e"
FG = "#e8eaed"
MUT = "#9aa0a8"
DIM = "#c7cbd1"
BORDER = "#3a4150"
ACCENT = "#4fd1c5"

# --- tool / brand accents (tuned for legibility on dark) ---
GITLAB = "#FC6D26"
GO = "#00ADD8"
DOCKER = "#2496ED"
VMWARE = "#5AA9C9"
DIODE = "#E67E22"
APT = "#E0567A"
MSVC = "#A375D6"
ARCHIVE = "#F0B429"
OSV = "#5B8DEF"
ET = "#EF5350"
COV = "#34D399"

# --- flow colors ---
FLOW = "#38BDF8"  # build / artifact flow
ONE_WAY = "#E67E22"  # one-way diode replication
USE_DB = "#4fd1c5"  # security-DB usage (dashed teal)

ONLINE_BORDER = "#29ABE2"
OFFLINE_BORDER = "#5B8DEF"

parts: list[str] = []
_marker_colors: set[str] = set()


def mid(color: str) -> str:
    return f"ar-{color.lstrip('#')}"


def arrow(x1, y1, x2, y2, color=FLOW, width=2.4, dashed=False):
    _marker_colors.add(color)
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    parts.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{width}"{dash} marker-end="url(#{mid(color)})"/>'
    )


def path_arrow(d, color=FLOW, width=2.4, dashed=False):
    _marker_colors.add(color)
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    parts.append(
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
        f'{dash} marker-end="url(#{mid(color)})"/>'
    )


def text(
    x, y, s, size, color=FG, weight="400", anchor="start", spacing=None, mono=False
):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    fam = ' font-family="monospace"' if mono else ""
    parts.append(
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color}" text-anchor="{anchor}"{sp}{fam}>{escape(s)}</text>'
    )


def zone(x, y, w, h, stroke, label):
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="none" '
        f'stroke="{stroke}" stroke-width="2.5"/>'
    )
    text(x + 24, y + 32, label, 15, stroke, weight="800", spacing="1.5")


def node(x, y, w, h, accent, title, lines, mono_letter):
    """A rounded node box with a monogram icon circle, title and caption lines."""
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="13" fill="{CARD}" '
        f'stroke="{accent}" stroke-width="2.5"/>'
    )
    cx = x + w / 2
    cy = y + 48
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="25" fill="{CARD2}" stroke="{accent}" stroke-width="2"/>'
    )
    text(cx, cy + 6, mono_letter, 18, accent, weight="800", anchor="middle", mono=True)
    text(cx, y + 100, title, 16, FG, weight="700", anchor="middle")
    ly = y + 126
    for ln in lines:
        text(cx, ly, ln, 12, MUT, anchor="middle")
        ly += 18


def dashed_group(x, y, w, h, label, items):
    """External-input dashed box listing several sources, each with a color chip."""
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" '
        f'stroke="#6b7480" stroke-width="2" stroke-dasharray="7 5"/>'
    )
    iy = y + 40
    for color, name, sub in items:
        parts.append(
            f'<rect x="{x + 20}" y="{iy - 12}" width="14" height="14" rx="3" '
            f'fill="none" stroke="{color}" stroke-width="2.5"/>'
        )
        text(x + 44, iy, name, 13, FG, weight="600")
        if sub:
            text(x + 44, iy + 16, sub, 11, MUT)
        iy += 46
    text(x + w / 2, y + h - 14, label, 13, "#8b95a1", weight="600", anchor="middle")


# ======================= build the diagram =======================

# canvas bg
parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{CARD}"/>')

# --- zones ---
zone(30, 90, 770, 1000, ONLINE_BORDER, "ONLINE NETWORK (INTERNET-CONNECTED)")
zone(1010, 90, 960, 1000, OFFLINE_BORDER, "OFFLINE NETWORK (AIR-GAPPED)")

# lane eyebrow labels — online
text(60, 138, "1 · DEPENDENCY PACKAGING", 13, "#7FB2D8", weight="700", spacing="1")
text(60, 560, "2 · SECURITY FEEDS MIRROR", 13, "#7FB2D8", weight="700", spacing="1")

# --- online: build lane ---
dashed_group(
    55,
    158,
    175,
    210,
    "build-spec.yaml",
    [
        (MUT, "URL list", "direct downloads"),
        (APT, "APT packages", "Linux deps"),
        (MSVC, "MSVC packages", "Windows deps"),
    ],
)
node(
    260,
    158,
    210,
    210,
    GO,
    "Go Packager",
    ["Resolve & fetch deps", "from URLs / APT / MSVC", "Build archive + SHA-256"],
    "Go",
)
node(
    500,
    158,
    175,
    210,
    ARCHIVE,
    "Artifacts",
    [".tar.zst / .zip", "+ SHA-256", "checksums"],
    "◰",
)

# --- online: security-feed lane ---
dashed_group(
    55,
    588,
    175,
    250,
    "vuln / rule sources",
    [
        (OSV, "OSV.dev", "advisory DB"),
        (ET, "Emerging Threats", "IDS ruleset"),
        (COV, "Coverity", "SAST models"),
    ],
)
node(
    500,
    600,
    175,
    210,
    ACCENT,
    "DB Snapshots",
    ["OSV · ET · Coverity", "pulled + verified", "signed · versioned"],
    "DB",
)

# --- export staging (converge both lanes) ---
node(
    690,
    400,
    95,
    360,
    "#9AA7B4",
    "Export",
    [],
    "⇥",
)
text(690 + 47, 400 + 250, "Staging", 12, MUT, anchor="middle")
text(690 + 47, 400 + 268, "store", 12, MUT, anchor="middle")

# --- diode ---
DIODE_X, DIODE_Y, DIODE_W, DIODE_H = 850, 520, 110, 110
parts.append(
    f'<rect x="{DIODE_X}" y="{DIODE_Y}" width="{DIODE_W}" height="{DIODE_H}" rx="12" '
    f'fill="#2a2116" stroke="{DIODE}" stroke-width="3"/>'
)
dcx = DIODE_X + DIODE_W / 2
dcy = DIODE_Y + 46
parts.append(
    f'<g stroke="{DIODE}" stroke-width="3" fill="{DIODE}">'
    f'<line x1="{dcx - 26}" y1="{dcy}" x2="{dcx - 4}" y2="{dcy}"/>'
    f'<polygon points="{dcx - 4},{dcy - 12} {dcx - 4},{dcy + 12} {dcx + 20},{dcy}"/>'
    f'<line x1="{dcx + 22}" y1="{dcy - 14}" x2="{dcx + 22}" y2="{dcy + 14}"/>'
    f"</g>"
)
text(dcx, DIODE_Y + 88, "Data Diode", 13, DIODE, weight="700", anchor="middle")

# --- offline: import store (from diode) ---
node(
    1035,
    490,
    165,
    180,
    "#9AA7B4",
    "Import Store",
    ["Replicated artifacts", "+ DB snapshots", "checksum-verified"],
    "⇤",
)

# --- offline: CI runners (provisioned envs that back the build jobs) ---
node(
    1035,
    700,
    165,
    190,
    "#B7C0CC",
    "CI Runners",
    ["bash / PowerShell", "Docker (Linux)", "VMware (Windows)"],
    "⚙",
)

# --- offline: GitLab CI pipeline container ---
BUILD = "#7CC29B"
DOCS = "#B79CE8"
zone(1330, 170, 620, 760, GITLAB, "GitLab CI  ·  PIPELINE")
text(1432, 250, "BUILD", 12, MUT, weight="700", anchor="middle", spacing="1")
text(1620, 250, "SECURITY SCAN", 12, MUT, weight="700", anchor="middle", spacing="1")
text(1815, 250, "DOC GENERATION", 12, MUT, weight="700", anchor="middle", spacing="1")

node(
    1350,
    290,
    165,
    170,
    BUILD,
    "Build · Linux",
    ["compile on", "Docker runner"],
    "L",
)
node(
    1350,
    520,
    165,
    170,
    BUILD,
    "Build · Windows",
    ["compile on", "VMware runner"],
    "W",
)
node(
    1540,
    395,
    160,
    230,
    ET,
    "Security Scan",
    ["osv-scanner (deps)", "Coverity (SAST)", "ET rules · gate", "on new findings"],
    "⚲",
)
node(
    1730,
    395,
    170,
    230,
    DOCS,
    "Doc Generation",
    ["Markdown source", "pandoc →", "DOCX · PDF · HTML"],
    "▤",
)

# ======================= arrows =======================

RUNNER = "#93A5B4"

# online build lane
arrow(230, 263, 256, 263)  # yaml -> go packager
arrow(470, 263, 496, 263)  # go -> artifacts
# online security lane (sources feed the snapshot store directly)
arrow(230, 705, 496, 705)  # sources -> db snapshots
text(363, 695, "pull · verify · pin", 11, MUT, anchor="middle")
# converge into export (clean box-edge entries)
path_arrow("M587 368 C 660 380, 737 378, 737 398")  # artifacts -> export top edge
arrow(675, 705, 688, 705)  # db snapshots -> export left edge
# export -> diode
arrow(785, 575, DIODE_X - 4, 575, color=ONE_WAY, width=3.4)
# diode -> import store
arrow(DIODE_X + DIODE_W + 4, 575, 1031, 575, color=ONE_WAY, width=3.4)

# --- offline pipeline flow ---
# import artifacts -> build stage
path_arrow("M1200 555 C 1270 520, 1300 490, 1346 482")
text(1268, 502, "artifacts + deps", 11, MUT, anchor="middle")
# CI runners back the build jobs (dashed "runs on")
path_arrow(
    "M1200 760 C 1275 720, 1290 430, 1346 392", color=RUNNER, width=2, dashed=True
)
path_arrow(
    "M1200 810 C 1290 780, 1300 610, 1346 598", color=RUNNER, width=2, dashed=True
)
# build jobs -> security scan
path_arrow("M1515 380 C 1528 410, 1538 440, 1538 468")
path_arrow("M1515 600 C 1528 570, 1538 545, 1538 552")
# security scan -> doc generation
arrow(1700, 510, 1726, 510)
# mirrored DBs feed the security scan (dashed teal, routed under the build jobs)
path_arrow(
    "M1200 640 C 1360 745, 1500 748, 1600 690 C 1622 674, 1620 650, 1620 627",
    color=USE_DB,
    width=2.2,
    dashed=True,
)
text(1420, 748, "mirrored DBs", 11, USE_DB, anchor="middle")

# ======================= legend =======================
LEG_Y = 1110
parts.append(
    f'<rect x="30" y="{LEG_Y - 32}" width="1940" height="60" rx="12" '
    f'fill="{CARD2}" stroke="{BORDER}" stroke-width="1.5"/>'
)
text(52, LEG_Y + 4, "LEGEND", 13, DIM, weight="700", spacing="1")

lx = 150
# online swatch
parts.append(
    f'<rect x="{lx}" y="{LEG_Y - 12}" width="26" height="18" rx="4" fill="none" stroke="{ONLINE_BORDER}" stroke-width="2.5"/>'
)
text(lx + 36, LEG_Y + 3, "Online network", 12.5, DIM)
lx += 230
parts.append(
    f'<rect x="{lx}" y="{LEG_Y - 12}" width="26" height="18" rx="4" fill="none" stroke="{OFFLINE_BORDER}" stroke-width="2.5"/>'
)
text(lx + 36, LEG_Y + 3, "Offline (air-gapped)", 12.5, DIM)
lx += 270
parts.append(
    f'<rect x="{lx}" y="{LEG_Y - 12}" width="26" height="18" rx="4" fill="none" stroke="#6b7480" stroke-width="2" stroke-dasharray="6 4"/>'
)
text(lx + 36, LEG_Y + 3, "External input", 12.5, DIM)
lx += 210
parts.append(
    f'<line x1="{lx}" y1="{LEG_Y - 3}" x2="{lx + 40}" y2="{LEG_Y - 3}" stroke="{FLOW}" stroke-width="2.5" marker-end="url(#{mid(FLOW)})"/>'
)
text(lx + 52, LEG_Y + 3, "Build / artifact flow", 12.5, DIM)
lx += 260
parts.append(
    f'<line x1="{lx}" y1="{LEG_Y - 3}" x2="{lx + 40}" y2="{LEG_Y - 3}" stroke="{ONE_WAY}" stroke-width="3.4" marker-end="url(#{mid(ONE_WAY)})"/>'
)
text(lx + 52, LEG_Y + 3, "One-way diode", 12.5, DIM)
lx += 220
parts.append(
    f'<line x1="{lx}" y1="{LEG_Y - 3}" x2="{lx + 40}" y2="{LEG_Y - 3}" stroke="{USE_DB}" stroke-width="2.2" stroke-dasharray="6 4" marker-end="url(#{mid(USE_DB)})"/>'
)
text(lx + 52, LEG_Y + 3, "Security DB usage", 12.5, DIM)

# ======================= assemble =======================
markers = "".join(
    f'<marker id="{mid(c)}" markerWidth="10" markerHeight="10" refX="8" refY="4" '
    f'orient="auto"><path d="M0 0 L9 4 L0 8 Z" fill="{c}"/></marker>'
    for c in sorted(_marker_colors)
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f"font-family=\"'Helvetica Neue', Arial, sans-serif\">"
    f"<defs>{markers}</defs>" + "".join(parts) + "</svg>"
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CI/CD Security Pipeline</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: #1b1f28;
    color: #e8eaed;
  }}
  .diagram-card {{ padding: 16px; }}
  .diagram-card svg {{ display: block; width: 100%; height: auto; }}
</style>
</head>
<body>
  <div class="diagram-card">
{svg}
  </div>
</body>
</html>
"""

out = Path("images/cicd-security-pipeline.html")
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html)} bytes)")
