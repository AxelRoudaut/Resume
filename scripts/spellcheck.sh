#!/usr/bin/env bash
# Bilingual (English + French) spell check for LaTeX sources via hunspell.
#
# A word is reported only if it is unknown in BOTH dictionaries (-d en_US,fr_FR),
# so genuine French and English words both pass. Proper nouns and tech terms that
# neither dictionary knows (Kubernetes, Thales, ksqlDB, ...) live in the personal
# allow-list .hunspell-allow.txt at the repo root.
#
# Usage:
#   scripts/spellcheck.sh                 # check every latex/**/*.tex
#   scripts/spellcheck.sh a.tex b.tex     # check the given files (pre-commit passes these)
set -uo pipefail

# The git-commit environment may export an ungenerated locale (e.g. LC_ALL set to
# en_US.UTF-8 when only C.UTF-8 exists). hunspell then falls back to a byte locale
# and splits every accented word ("Ingénieur" -> "Ing" + "nieur"), producing a
# storm of false positives. Force a valid UTF-8 locale so French tokenizes right.
export LC_ALL=C.UTF-8 LANG=C.UTF-8

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALLOW="$ROOT/.hunspell-allow.txt"
DICTS="en_US,fr_FR"

# hunspell + its dictionaries are optional, manually-installed deps (see bindep.txt).
# Don't block contributors who haven't installed them — warn and pass.
if ! command -v hunspell >/dev/null 2>&1; then
    echo "spellcheck: hunspell not installed — skipping." >&2
    echo "  Install: sudo apt install hunspell hunspell-en-us hunspell-fr" >&2
    exit 0
fi
# A missing dictionary makes hunspell exit non-zero; probe before running for real.
if ! printf 'probe\n' | hunspell -l -d "$DICTS" >/dev/null 2>&1; then
    echo "spellcheck: dictionaries '$DICTS' not both available — skipping." >&2
    echo "  Install: sudo apt install hunspell-en-us hunspell-fr" >&2
    exit 0
fi

# Files: those passed by pre-commit, else every LaTeX source under latex/.
files=("$@")
if [ "${#files[@]}" -eq 0 ]; then
    mapfile -t files < <(find "$ROOT/latex" -name '*.tex' | sort)
fi

status=0
for f in "${files[@]}"; do
    [ -f "$f" ] || continue
    # -l: list unknown words only  -t: TeX mode (skip \commands & % comments)  -p: allow-list
    # Drop tokens containing digits — LaTeX dimensions (12cm, 0.8pt) and reference
    # codes (offer numbers) leak through TeX mode but are never dictionary words.
    # Image file names (\schema{foo-bar.pdf}, \includegraphics{...}) are paths,
    # not prose: strip them so they don't force junk into the allow-list.
    bad="$(sed -E 's/\\(schema|includegraphics)(\[[^]]*\])?\{[^}]*\}/ /g' "$f" \
        | hunspell -l -t -d "$DICTS" -p "$ALLOW" 2>/dev/null | grep -vE '[0-9]' | sort -u)"
    if [ -n "$bad" ]; then
        status=1
        echo "✗ ${f#"$ROOT"/}" >&2
        sed 's/^/    /' <<<"$bad" >&2
    fi
done

if [ "$status" -ne 0 ]; then
    echo >&2
    echo "Unknown words above. Fix real typos, or add names/tech terms to .hunspell-allow.txt" >&2
fi
exit "$status"
