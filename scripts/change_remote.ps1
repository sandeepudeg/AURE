# Change Git Remote Repository

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Change Git Remote to sandeepudeg/AURE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

# Change to project root
Set-Location $PSScriptRoot\..

Write-Host "`n[1/4] Checking current remote..." -ForegroundColor Yellow
git remote -v

Write-Host "`n[2/4] Removing old remote..." -ForegroundColor Yellow
git remote remove origin

Write-Host "`n[3/4] Adding new remote (sandeepudeg/AURE)..." -ForegroundColor Yellow
git remote add origin https://github.com/sandeepudeg/AURE.git

Write-Host "`n[4/4] Verifying new remote..." -ForegroundColor Yellow
git remote -v

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "✅ Remote changed successfully!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

Write-Host "`nNew repository: https://github.com/sandeepudeg/AURE" -ForegroundColor Cyan
Write-Host "`nNow run: .\scripts\git_push.ps1 to push your code" -ForegroundColor Yellow
