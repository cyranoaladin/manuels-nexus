#!/usr/bin/env bash
# Compile tous les .tex du pack en PDF (pdflatex, halt-on-error), puis nettoie.
# nsi-preamble.sty provient de la source unique 02_modeles_documents/.
set -uo pipefail
shopt -s nullglob

PACK_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PACK_DIR"
REPO_ROOT="$(cd "../../../.." && pwd)"
export TEXINPUTS="${REPO_ROOT}/02_modeles_documents:${TEXINPUTS:-}"

fail=0
for tex in *.tex; do
  printf '→ %-32s ' "$tex"
  logfile="${tex%.tex}.log"
  if pdflatex -interaction=nonstopmode -halt-on-error "$tex" >/dev/null 2>&1; then
    echo "✓ ${tex%.tex}.pdf"
  else
    echo "✗ ÉCHEC"
    if [ -f "$logfile" ]; then
      echo "--- dernières 20 lignes de $logfile ---"
      tail -20 "$logfile"
      echo "---"
    fi
    fail=1
  fi
done
# Nettoyer les auxiliaires, mais PRÉSERVER les .log en cas d'échec
if [ "$fail" -eq 0 ]; then
  rm -f ./*.aux ./*.log ./*.out ./*.toc
else
  rm -f ./*.aux ./*.out ./*.toc
  echo "⚠ .log préservés pour diagnostic"
fi
exit $fail
