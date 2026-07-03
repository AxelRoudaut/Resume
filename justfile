port := "8000"

# list available recipes
default:
    just --list

# serve the site locally at http://localhost:8000
serve:
    uv run python -m http.server {{port}}

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
