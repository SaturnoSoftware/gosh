param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = "Stop"

Push-Location $ProjectRoot
try {
    python -m pip install coverage
    if ($LASTEXITCODE -ne 0) {
        throw "pip install coverage failed with exit code $LASTEXITCODE."
    }

    coverage run -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "coverage run failed with exit code $LASTEXITCODE."
    }

    coverage report --fail-under=80
    if ($LASTEXITCODE -ne 0) {
        throw "coverage report failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
