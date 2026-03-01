# Simple local web server for testing URE Web UI

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "URE Web UI - Local Test Server" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

$port = 8080
$directory = "src\web"

Write-Host "`nStarting server..." -ForegroundColor Yellow

# Change to project root
Set-Location $PSScriptRoot\..

# Start Python HTTP server
Write-Host "`n✓ Server running at: http://localhost:$port" -ForegroundColor Green
Write-Host "✓ Serving files from: $directory\" -ForegroundColor Green
Write-Host "`n✓ Open in browser: http://localhost:$port/index.html" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

# Run Python server
py -m http.server $port --directory $directory
