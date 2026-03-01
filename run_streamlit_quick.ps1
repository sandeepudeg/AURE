# Quick Streamlit Local Runner
# Runs Streamlit UI locally with local agents

Write-Host "Starting Streamlit UI (Local Mode)..." -ForegroundColor Green
Write-Host ""

# Set environment variables for local mode
$env:USE_API_MODE = "false"

# Run Streamlit
Write-Host "Opening browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

streamlit run src/ui/app.py --server.port=8501 --server.address=localhost
