# Git Push Essential Files Only
# This script creates a new orphan branch with only essential files

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Git Push Essential Files" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "[1/5] Creating new orphan branch..." -ForegroundColor Yellow
git checkout --orphan temp-clean-branch
Write-Host "✓ Created temp-clean-branch`n" -ForegroundColor Green

Write-Host "[2/5] Adding essential files..." -ForegroundColor Yellow
# Add only essential directories and files
git add src/
git add scripts/
git add tests/
git add docs/
git add cloudformation/
git add .ebextensions/
git add .streamlit/
git add *.md
git add *.txt
git add *.py
git add *.yaml
git add *.yml
git add *.json
git add *.toml
git add .gitignore
git add .env.example
git add Dockerfile
git add Procfile
git add application.py
Write-Host "✓ Added essential files`n" -ForegroundColor Green

Write-Host "[3/5] Creating commit..." -ForegroundColor Yellow
git commit -m "Clean repository with essential files only"
Write-Host "✓ Commit created`n" -ForegroundColor Green

Write-Host "[4/5] Replacing main branch..." -ForegroundColor Yellow
git branch -D main
git branch -m main
Write-Host "✓ Replaced main branch`n" -ForegroundColor Green

Write-Host "[5/5] Force pushing to GitHub..." -ForegroundColor Yellow
git push -f origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Successfully pushed to GitHub!`n" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "SUCCESS! Clean repository pushed to GitHub" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
} else {
    Write-Host "✗ Push failed" -ForegroundColor Red
    exit 1
}
