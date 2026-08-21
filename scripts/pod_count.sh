#!/usr/bin/env bash
set -euo pipefail
echo "=== FathomNet concept counts ==="
for c in Cheloniidae Testudines "Caretta caretta" "Dermochelys coriacea" "Lepidochelys kempii" Fish Actinopterygii Elasmobranchii; do
  echo "--- $c ---"
  fathomnet-generate --count --concepts "$c" --taxa fathomnet 2>&1 | tail -8
done
