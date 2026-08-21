#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
import fathomnet
import pathlib
p = pathlib.Path(fathomnet.__file__).parent
print("fathomnet at", p)
for f in p.rglob("*.py"):
    text = f.read_text(errors="ignore")
    if "http" in text and "fathom" in text.lower():
        for line in text.splitlines():
            if "http" in line and "fathom" in line.lower():
                print(f"{f.name}: {line.strip()}")
PY
which fathomnet-generate || true
fathomnet-generate --count --concepts Cheloniidae --taxa fathomnet 2>&1 | tail -20
