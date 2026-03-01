#!/usr/bin/env pwsh
# Run Streamlit locally with Mumbai API
# This provides the fastest experience for users in India

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Starting Local Streamlit with Mumbai API" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# Set environment variables for API mode
$env:USE_API_MODE = "true"
$env:API_ENDPOINT = "https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Mode: API Mode (using Mumbai backend)" -ForegroundColor White
Write-Host "  API Endpoint: $env:API_ENDPOINT" -ForegroundColor White
Write-Host "  Expected Performance:" -ForegroundColor White
Write-Host "    - UI Load: < 1 second (local)" -ForegroundColor Green
Write-Host "    - API Latency: 50-100ms (Mumbai)" -ForegroundColor Green
Write-Host "`n"

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment 'rural'..." -ForegroundColor Yellow
    & ".\rural\Scripts\Activate.ps1"
}

# Run Streamlit
Write-Host "Starting Streamlit..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

py -m streamlit run src/ui/app.py
