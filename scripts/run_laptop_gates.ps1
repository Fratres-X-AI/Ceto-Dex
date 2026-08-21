Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot\..

pip install -e ".[dev]"
pytest -q
python -m cetodex.laptop_gate @args

Pop-Location
