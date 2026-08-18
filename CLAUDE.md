# Resume

Static personal resume site served via GitHub Pages (Jekyll, theme `jekyll-theme-cayman`).

## Working style

- For multi-step work, keep a visible todo list and only check off an item once
  it has been **verified** done (test/lint/build passes, output inspected) — not
  merely written.

## Python

This project uses `uv` for all Python work (see `pyproject.toml`).

- Run scripts with `uv run <script>` — never invoke `python`/`python3` directly.
- Add new dependencies with `uv add <package>` — never edit `pyproject.toml`'s
  `dependencies` list by hand or use `pip install`.

## Task running

Common dev tasks are defined in `justfile` — use `just <recipe>` instead of
retyping the underlying commands. Run `just --list` (or `just` with no args)
to see them all. Current recipes:

- `just init` — install everything needed to work on the project (Python deps,
  Biome, git hooks). Run this first on a fresh clone. Also runs `bindep-check`.
- `just bindep-check` / `just bindep-list` — verify (or list) the system APT
  packages declared in `bindep.txt`: the diagram skills' image-export runtime,
  the LaTeX toolchain, hunspell, and pandoc (document conversion).
  `bindep-check` is non-fatal and prints the `apt install` line for any
  missing packages.
- `just serve` / `just serve-bg` / `just stop` — serve the site locally at
  http://localhost:8000 (foreground / background / stop the background server)
- `just diagrams` — regenerate the `diagrams/html/<name>.html` cards from the
  `.drawio` sources in `diagrams/drawio/` (all files, or `just diagrams FILE.drawio`).
  Exports each source to SVG via the draw.io desktop CLI and wraps it in the
  dark-theme card `index.html` embeds via `<iframe>`. Requires the draw.io
  desktop CLI.
- `just diagrams-pdf` — export the same `.drawio` sources to vector PDF under
  `diagrams/pdf/`, for the LaTeX documents that embed them with
  `\includegraphics`.
- `just extract-cv` — extract text from the source CV PDF
- `just clean` — remove local scratch files under `tmp/`
- `just hooks-install` — install the pre-commit git hooks (one-time setup)
- `just lint` — run all pre-commit checks against every file
- `just lint-html` — lint HTML with djlint (Jekyll profile)
- `just lint-web` — lint JS + CSS with Biome
- `just spell [FILE...]` — bilingual (EN+FR) spell check of the LaTeX sources
  via hunspell; proper nouns / tech terms are whitelisted in `.hunspell-allow.txt`

When adding a new recurring command to this project, add it to `justfile`
rather than only documenting it in prose.

## Linting

- **Python** — ruff (via pre-commit).
- **HTML** — djlint with the `jekyll` profile (`.djlintrc`); the generated
  diagram cards under `diagrams/html/` are excluded.
- **JS + CSS** — Biome (`biome.json`), installed as a standalone binary to
  `~/.local/bin` by `just init` (no Node required). Configured as a linter only;
  its formatter is disabled to avoid churning hand-authored CSS.
- The djlint and Biome hooks invoke their tool through
  `scripts/with-local-bin.sh`, which puts `~/.local/bin` on `PATH`. Editors
  spawn git without the login shell's profile, so a bare `uv` / `biome` is not
  found when committing from the IDE even though it works from a terminal.
  Use that wrapper for any new hook that calls a tool installed by `just init`.
- **Spelling** — two layers: codespell (English typos; French files skipped via
  `[tool.codespell]` in `pyproject.toml`) and hunspell (`just spell`, bilingual
  EN+FR over `latex/`). The hunspell pre-commit hook no-ops with a warning when
  the optional `hunspell*` packages (`bindep.txt`) aren't installed.
