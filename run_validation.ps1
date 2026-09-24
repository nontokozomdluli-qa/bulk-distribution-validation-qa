$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py .\validate_distribution.py
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python .\validate_distribution.py
    exit $LASTEXITCODE
}

Write-Error "Python was not found on PATH. Install Python or activate the project's virtual environment first."
exit 1
