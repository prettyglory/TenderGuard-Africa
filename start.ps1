$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "TenderGuard Africa"
Write-Host "=================="
Write-Host ""

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating Python 3.12 virtual environment..."
    py -3.12 -m venv .venv
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing project dependencies..."
python -m pip install -e ".[dev]" | Out-Host

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama is not installed. Install it from https://ollama.com/download"
}

Write-Host "Checking Qwen3 model..."

$modelInstalled = ollama list | Select-String "qwen3:1.7b"

if (-not $modelInstalled) {
    Write-Host "Downloading qwen3:1.7b..."
    ollama pull qwen3:1.7b
}

Write-Host ""
Write-Host "Starting TenderGuard demo..."
Write-Host ""

python -m app.agent.run `
    --tender TG-DEMO-001 `
    --bid BID-BETA-001