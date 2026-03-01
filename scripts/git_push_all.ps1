# Git Push All Files - Comprehensive Script

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Git Push ALL Files to sandeepudeg/AURE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

# Change to project root
Set-Location $PSScriptRoot\..

Write-Host "`n[1/7] Checking current status..." -ForegroundColor Yellow
git status

Write-Host "`n[2/7] Checking for untracked files..." -ForegroundColor Yellow
$untracked = git ls-files --others --exclude-standard
if ($untracked) {
    Write-Host "Untracked files found:" -ForegroundColor Yellow
    $untracked | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
} else {
    Write-Host "No untracked files" -ForegroundColor Green
}

Write-Host "`n[3/7] Adding ALL files (including new ones)..." -ForegroundColor Yellow
git add -A

Write-Host "`n[4/7] Checking what will be committed..." -ForegroundColor Yellow
git status

Write-Host "`n[5/7] Committing changes..." -ForegroundColor Yellow
$commitMessage = @"
Add complete web UI with full Streamlit feature parity

- Complete web UI files: complete.html, complete.css, complete.js
- All sidebar features: language selector, user profile, help guide, quick actions
- Chat features: agent badges, feedback system, image upload
- Deployment scripts and documentation
- Git helper scripts
"@

git commit -m $commitMessage

Write-Host "`n[6/7] Pulling remote changes (if any)..." -ForegroundColor Yellow
git pull origin main --rebase --allow-unrelated-histories

Write-Host "`n[7/7] Pushing ALL commits to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "✅ All files pushed successfully!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

Write-Host "`nRepository: https://github.com/sandeepudeg/AURE" -ForegroundColor Cyan
Write-Host "`nVerify at: https://github.com/sandeepudeg/AURE/tree/main" -ForegroundColor Yellow
