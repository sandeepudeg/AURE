# Test Complete Web UI locally

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "GramSetu Complete Web UI - Local Test" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

$port = 8080
$directory = "src\web"

Write-Host "`nStarting server..." -ForegroundColor Yellow

# Change to project root
Set-Location $PSScriptRoot\..

Write-Host "`n✓ Server running at: http://localhost:$port" -ForegroundColor Green
Write-Host "✓ Serving files from: $directory\" -ForegroundColor Green
Write-Host "`n✓ Open in browser: http://localhost:$port/complete.html" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

# Run Python server
py -m http.server $port --directory $directory
