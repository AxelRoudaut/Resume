# Global variables
set windows-shell := ["C:/tools/cygwinbin/bash.exe", "-uc"]
set shell := ["/bin/bash", "-uc"]
tmp_dir := if os_family() == "windows" { "C:/tmp" } else { "/tmp" }
root_dir := replace(justfile_dir(), "\\", "/")
sudo := if env('USER','not_defined') != "root" { "sudo" } else { "" }

port := "8000"

latex_dir := root_dir / "latex"

# list available recipes
default:
    just --list

# install everything needed to work on this project (Python deps, Biome, git hooks)
init:
    #!/usr/bin/env bash
    set -euo pipefail
    # Python toolchain + project deps (pypdf, djlint, pre-commit, ...)
    uv sync
    # Biome standalone binary — JS/CSS linter, no Node required
    if ! command -v biome >/dev/null 2>&1; then
        echo "Installing Biome to ~/.local/bin ..."
        mkdir -p "$HOME/.local/bin"
        case "$(uname -s)-$(uname -m)" in
            Linux-x86_64)  asset=biome-linux-x64 ;;
            Linux-aarch64) asset=biome-linux-arm64 ;;
            Darwin-x86_64) asset=biome-darwin-x64 ;;
            Darwin-arm64)  asset=biome-darwin-arm64 ;;
            *) echo "Unsupported platform for auto Biome install; see https://biomejs.dev" >&2; exit 1 ;;
        esac
        url=$(curl -s "https://api.github.com/repos/biomejs/biome/releases/latest" \
            | grep -oP "\"browser_download_url\":\s*\"\K[^\"]*${asset}(?=\")" | head -1)
        curl -sL "$url" -o "$HOME/.local/bin/biome"
        chmod +x "$HOME/.local/bin/biome"
    fi
    biome --version
    # git hooks (pre-commit + commit-msg)
    uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
    # verify system (APT) packages the diagram skills need (warns, never fails init)
    just bindep-check || true
    echo "Project ready. Ensure ~/.local/bin is on your PATH, then run 'just lint'."

# Enable just shell completion (generates the script and wires it into your shell rc)
enable_just_completion:
    #!/usr/bin/env bash
    set -euo pipefail
    shell=$(basename "$SHELL")
    completion="{{home_directory()}}/just-completion.sh"
    rc="{{home_directory()}}/.${shell}rc"
    just --completions "$shell" > "$completion"
    line="source \"$completion\""
    if [ -f "$rc" ] && grep -qF "$completion" "$rc"; then
        echo "Completion already sourced in $rc"
    else
        echo "$line" >> "$rc"
        echo "Added completion sourcing to $rc"
    fi
    echo "Run 'source $rc' (or open a new shell) to activate it."

# print the APT packages declared in bindep.txt (space-separated)
bindep-list:
    @grep -vE '^\s*(#|$)' bindep.txt | awk '{print $1}' | tr '\n' ' '

# verify the APT packages in bindep.txt are installed (non-fatal; prints what's missing)
bindep-check:
    #!/usr/bin/env bash
    set -uo pipefail
    if ! command -v dpkg-query >/dev/null 2>&1; then
        echo "bindep-check: not a dpkg/APT system — skipping." >&2
        exit 0
    fi
    missing=()
    for pkg in $(just bindep-list); do
        if dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed"; then
            printf '  \033[32m✓\033[0m %s\n' "$pkg"
        else
            printf '  \033[31m✗\033[0m %s\n' "$pkg"
            missing+=("$pkg")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo
        echo "Missing ${#missing[@]} package(s). Install with:" >&2
        {{ sudo  }} apt install ${missing[*]}
    fi
    echo "All bindep.txt packages installed."

# serve the site locally at http://localhost:8000
serve:
    uv run python -m http.server {{port}}

# serve the site in the background at http://localhost:8000
serve-bg:
    mkdir -p tmp
    uv run python -m http.server {{port}} > tmp/server.log 2>&1 & echo $! > tmp/server.pid
    @echo "serving at http://localhost:{{port}} (pid $(cat tmp/server.pid))"

# stop the background server started by serve-bg
stop:
    pkill -f "http.server {{port}}"
    rm -f tmp/server.pid

# Exports each .drawio to SVG via the draw.io desktop CLI, then wraps it in the
# dark-theme card the site embeds via <iframe> (headless runtime libs: bindep.txt).
# regenerate images/<name>.html diagram cards from diagrams/ (or `just diagrams FILE.drawio`)
diagrams file="":
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ root_dir }}"
    # resolve the draw.io CLI: Homebrew/Linux 'drawio', older 'draw.io', or the
    # Windows desktop exe reached from WSL2 via /mnt/c
    if command -v drawio >/dev/null 2>&1; then DRAWIO=(drawio)
    elif command -v draw.io >/dev/null 2>&1; then DRAWIO=(draw.io)
    elif [ -f "/mnt/c/Program Files/draw.io/draw.io.exe" ]; then DRAWIO=("/mnt/c/Program Files/draw.io/draw.io.exe")
    else
        echo "draw.io desktop CLI not found — install it to regenerate diagrams:" >&2
        echo "  https://github.com/jgraph/drawio-desktop/releases  (Homebrew: brew install --cask drawio)" >&2
        exit 1
    fi
    # headless Linux needs a virtual X server; the Windows exe (and any real
    # DISPLAY) does not
    RUN=()
    if [[ "${DRAWIO[0]}" != *.exe ]] && [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
        RUN=(xvfb-run -a --server-args="-screen 0 1600x1200x24")
    fi
    mkdir -p tmp
    files="{{ file }}"
    [ -n "$files" ] || files=$(ls diagrams/*.drawio)
    for f in $files; do
        f="diagrams/$(basename "$f")"
        name="$(basename "$f" .drawio)"
        # use the <diagram name="..."> attribute as the page <title>
        title="$(grep -oP '(?<=<diagram name=")[^"]+' "$f" | head -1)"
        echo "==> $name"
        export HOME="${HOME:-/tmp}"
        "${RUN[@]}" "${DRAWIO[@]}" -x -f svg -o "tmp/$name.svg" "$f" --no-sandbox
        if [ -n "$title" ]; then
            uv run python scripts/wrap_diagram.py "tmp/$name.svg" "images/$name.html" --title "$title"
        else
            uv run python scripts/wrap_diagram.py "tmp/$name.svg" "images/$name.html"
        fi
    done

# extract text from the source CV PDF (requires pypdf, see pyproject.toml)
extract-cv:
    uv run python -c "import pypdf; r = pypdf.PdfReader('ROUDAUT_Axel_CV_EN_2026.pdf'); print('\n'.join(p.extract_text() for p in r.pages))"

# build PDFs from the LaTeX sources in latex/ (all files, or `just pdf FILE.tex`)
pdf file="":
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ latex_dir }}"
    if ! command -v latexmk >/dev/null 2>&1; then
        echo "latexmk not found — see the 'LaTeX PDF build' section of bindep.txt." >&2
        echo "Install with: {{ sudo }} apt install latexmk texlive-latex-extra texlive-fonts-extra texlive-pictures texlive-lang-french" >&2
        exit 1
    fi
    files="{{ file }}"
    [ -n "$files" ] || files=$(ls *.tex)
    for f in $files; do
        f="${f#latex/}"
        echo "==> $f"
        latexmk -pdf -interaction=nonstopmode -halt-on-error "$f"
    done
    # drop the auxiliary build files, keep the PDFs
    latexmk -c

# remove LaTeX build artifacts in latex/ (keeps the generated PDFs)
pdf-clean:
    cd "{{ latex_dir }}" && latexmk -c

# remove local scratch files
clean:
    rm -rf tmp/*

# install the pre-commit git hook (one-time setup)
hooks-install:
    uv run pre-commit install

# run all pre-commit checks against every file
lint:
    uv run pre-commit run --all-files

# lint HTML only (djlint, Jekyll profile)
lint-html:
    uv run djlint --lint index.html

# lint JS + CSS only (Biome)
lint-web:
    biome lint js/ css/
