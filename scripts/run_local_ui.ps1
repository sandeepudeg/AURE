# Run URE MVP Streamlit UI locally
# This connects to the deployed AWS backend

Write-Host "`n=== Starting URE MVP Local UI ===" -ForegroundColor Cyan
Write-Host "This will start the Streamlit interface that connects to AWS backend`n" -ForegroundColor Yellow

# Check if virtual environment is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✓ Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not detected" -ForegroundColor Yellow
    Write-Host "Activating 'rural' environment..." -ForegroundColor Gray
    & ".\rural\Scripts\Activate.ps1"
}

# Set environment variable for API mode
$env:USE_API_MODE = "true"
$env:API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

Write-Host "`nConfiguration:" -ForegroundColor Cyan
Write-Host "  Mode: API (connects to AWS)" -ForegroundColor White
Write-Host "  Endpoint: $env:API_ENDPOINT" -ForegroundColor White
Write-Host ""

Write-Host "Starting Streamlit..." -ForegroundColor Yellow
Write-Host "The UI will open in your browser automatically." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server.`n" -ForegroundColor Gray

# Start Streamlit
streamlit run src/ui/app.py
