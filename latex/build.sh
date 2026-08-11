#!/usr/bin/env bash
# Compile TOUS les packs : parcourt latex/packs/<niveau>/<SEQ>/ et lance chaque build.sh local.
set -uo pipefail
cd "$(dirname "$0")"
fail=0
found=0
for d in packs/*/*/; do
  [ -x "$d/build.sh" ] || continue
  found=1
  echo "=== $d ==="
  if (cd "$d" && ./build.sh); then
    echo "=== $d OK ==="
  else
    echo "=== $d ÉCHEC ==="
    fail=1
  fi
  echo
done
if [ "$found" -eq 0 ]; then
  echo "Aucun pack trouvé dans packs/*/*/"
  exit 1
fi
exit $fail
