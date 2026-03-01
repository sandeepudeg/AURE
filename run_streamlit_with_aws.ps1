# Run Streamlit UI with AWS Deployed Backend
# This script starts the Streamlit interface connected to your deployed AWS API

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "           URE MVP - Streamlit UI with AWS Backend" -ForegroundColor Cyan
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

# Set environment variables for API mode
$env:USE_API_MODE = "true"
$env:API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Mode: AWS Deployed API" -ForegroundColor White
Write-Host "  Endpoint: $env:API_ENDPOINT" -ForegroundColor White
Write-Host ""

Write-Host "Features available:" -ForegroundColor Cyan
Write-Host "  ✓ Multi-agent AI system (Supervisor, Agri-Expert, Policy Navigator, Resource Optimizer)" -ForegroundColor Gray
Write-Host "  ✓ Multilingual support (English, Hindi, Marathi)" -ForegroundColor Gray
Write-Host "  ✓ Image upload for crop disease detection" -ForegroundColor Gray
Write-Host "  ✓ Automatic location detection" -ForegroundColor Gray
Write-Host "  ✓ User profile management" -ForegroundColor Gray
Write-Host "  ✓ Feedback system" -ForegroundColor Gray
Write-Host "  ✓ Conversation history" -ForegroundColor Gray
Write-Host ""

Write-Host "Starting Streamlit..." -ForegroundColor Yellow
Write-Host "The UI will open in your browser automatically." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
streamlit run src/ui/app.py
