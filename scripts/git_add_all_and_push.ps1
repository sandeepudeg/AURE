# Git Add All Files and Push to GitHub
# This script adds ALL untracked files and pushes to the repository

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Git Add All Files and Push" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Step 1: Show current status
Write-Host "[1/6] Checking current git status..." -ForegroundColor Yellow
$status = git status --short
$untrackedCount = ($status | Where-Object { $_ -match '^\?\?' }).Count
$modifiedCount = ($status | Where-Object { $_ -match '^ M' }).Count
Write-Host "✓ Found $untrackedCount untracked files" -ForegroundColor Green
Write-Host "✓ Found $modifiedCount modified files`n" -ForegroundColor Green

# Step 2: Add all files
Write-Host "[2/6] Adding all files to git..." -ForegroundColor Yellow
git add -A
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All files added successfully`n" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to add files" -ForegroundColor Red
    exit 1
}

# Step 3: Show what will be committed
Write-Host "[3/6] Files staged for commit:" -ForegroundColor Yellow
$stagedFiles = git diff --cached --name-only
$stagedCount = ($stagedFiles | Measure-Object).Count
Write-Host "✓ Total files staged: $stagedCount" -ForegroundColor Green
Write-Host "`nKey directories being committed:" -ForegroundColor Cyan
$stagedFiles | ForEach-Object {
    if ($_ -match '^src/') { $srcCount++ }
    if ($_ -match '^scripts/') { $scriptsCount++ }
    if ($_ -match '^tests/') { $testsCount++ }
    if ($_ -match '^docs/') { $docsCount++ }
    if ($_ -match '^cloudformation/') { $cfCount++ }
}
if ($srcCount) { Write-Host "  - src/: $srcCount files" -ForegroundColor White }
if ($scriptsCount) { Write-Host "  - scripts/: $scriptsCount files" -ForegroundColor White }
if ($testsCount) { Write-Host "  - tests/: $testsCount files" -ForegroundColor White }
if ($docsCount) { Write-Host "  - docs/: $docsCount files" -ForegroundColor White }
if ($cfCount) { Write-Host "  - cloudformation/: $cfCount files" -ForegroundColor White }
Write-Host ""

# Step 4: Commit
Write-Host "[4/6] Creating commit..." -ForegroundColor Yellow
$commitMessage = "Add all project files including complete web UI, scripts, and documentation"
git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Commit created successfully`n" -ForegroundColor Green
} else {
    Write-Host "✗ Commit failed" -ForegroundColor Red
    exit 1
}

# Step 5: Pull with rebase
Write-Host "[5/6] Pulling latest changes from remote..." -ForegroundColor Yellow
git pull --rebase origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Successfully pulled and rebased`n" -ForegroundColor Green
} else {
    Write-Host "⚠ Pull with rebase had issues - you may need to resolve conflicts" -ForegroundColor Yellow
    Write-Host "After resolving conflicts, run: git rebase --continue" -ForegroundColor Yellow
    Write-Host "Then run: git push origin main`n" -ForegroundColor Yellow
    exit 1
}

# Step 6: Push to GitHub
Write-Host "[6/6] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Successfully pushed to GitHub!`n" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "SUCCESS! All files pushed to GitHub" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "`nRepository: https://github.com/sandeepudeg/AURE" -ForegroundColor White
    Write-Host "Branch: main" -ForegroundColor White
    Write-Host "`nKey files pushed:" -ForegroundColor Cyan
    Write-Host "  ✓ Complete Web UI (src/web/complete.html, complete.css, complete.js)" -ForegroundColor White
    Write-Host "  ✓ Lambda handlers and agents (src/)" -ForegroundColor White
    Write-Host "  ✓ Deployment scripts (scripts/)" -ForegroundColor White
    Write-Host "  ✓ Tests (tests/)" -ForegroundColor White
    Write-Host "  ✓ Documentation (docs/, *.md files)" -ForegroundColor White
    Write-Host "  ✓ CloudFormation templates (cloudformation/)" -ForegroundColor White
} else {
    Write-Host "✗ Push failed" -ForegroundColor Red
    Write-Host "You may need to pull changes first or resolve conflicts" -ForegroundColor Yellow
    exit 1
}
