# Git Push Script for URE Project

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Git Push to sandeepudeg/AURE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

# Change to project root
Set-Location $PSScriptRoot\..

Write-Host "`n[1/4] Checking git status..." -ForegroundColor Yellow
git status

Write-Host "`n[2/4] Adding all files..." -ForegroundColor Yellow
git add .

Write-Host "`n[3/4] Committing changes..." -ForegroundColor Yellow
$commitMessage = @"
Add complete web UI with full Streamlit feature parity

- Created complete.html with all sidebar and chat features
- Added complete.css with Streamlit-matching styles  
- Implemented complete.js with full functionality
- Features: language selector, user profile, help guide, quick actions, feedback system, image upload
- Updated deployment scripts for new web UI
- Added comprehensive documentation (COMPLETE_WEB_UI_GUIDE.md)
"@

git commit -m $commitMessage

Write-Host "`n[4/4] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "✅ Push complete!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

Write-Host "`nRepository: https://github.com/sandeepudeg/AURE" -ForegroundColor Cyan
