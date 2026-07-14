port := "8000"

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
    echo "Project ready. Ensure ~/.local/bin is on your PATH, then run 'just lint'."

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

# extract text from the source CV PDF (requires pypdf, see pyproject.toml)
extract-cv:
    uv run python -c "import pypdf; r = pypdf.PdfReader('ROUDAUT_Axel_CV_EN_2026.pdf'); print('\n'.join(p.extract_text() for p in r.pages))"

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
