# Run Streamlit UI with Local Agents (Development Mode)
# This script starts the Streamlit interface using local agents

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "        URE MVP - Streamlit UI with Local Agents" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment 'rural'..." -ForegroundColor Yellow
    if (Test-Path "rural\Scripts\Activate.ps1") {
        & ".\rural\Scripts\Activate.ps1"
        Write-Host "✓ Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "✗ Virtual environment 'rural' not found!" -ForegroundColor Red
        Write-Host "Please create it first: python -m venv rural" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment already active: $env:VIRTUAL_ENV" -ForegroundColor Green
}

Write-Host ""

# Set environment variables for local mode
$env:USE_API_MODE = "false"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Mode: Local Development" -ForegroundColor White
Write-Host "  Using: Local agents (no AWS connection)" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  Note: Local mode requires:" -ForegroundColor Yellow
Write-Host "  - All dependencies installed" -ForegroundColor Gray
Write-Host "  - .env file configured" -ForegroundColor Gray
Write-Host "  - AWS credentials for Bedrock access" -ForegroundColor Gray
Write-Host ""

Write-Host "Starting Streamlit..." -ForegroundColor Yellow
Write-Host "The UI will open in your browser automatically." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
streamlit run src/ui/app.py
