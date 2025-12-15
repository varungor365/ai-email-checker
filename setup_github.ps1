#!/usr/bin/env pwsh
# Quick Setup Script for GitHub + Droplet Deployment

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║     AI Email Checker - GitHub + Droplet Quick Setup           ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check if git is initialized
$gitExists = Test-Path ".git"
if (-not $gitExists) {
    Write-Host "❌ Git not initialized. Run 'git init' first." -ForegroundColor Red
    exit 1
}

# Get GitHub username
Write-Host "📝 GitHub Setup" -ForegroundColor Cyan
Write-Host ""
$username = Read-Host "Enter your GitHub username"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ Username cannot be empty" -ForegroundColor Red
    exit 1
}

$repoName = "ai-email-checker"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "🔗 Repository will be: $repoUrl" -ForegroundColor Yellow
Write-Host ""

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "⚠️  Remote 'origin' already exists: $remoteExists" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/n)"
    if ($overwrite -eq 'y') {
        git remote remove origin
        Write-Host "✅ Old remote removed" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Keeping existing remote" -ForegroundColor Cyan
        $repoUrl = $remoteExists
    }
}

# Add remote if needed
if (-not $remoteExists -or $overwrite -eq 'y') {
    Write-Host "🔗 Adding GitHub remote..." -ForegroundColor Cyan
    git remote add origin $repoUrl
    Write-Host "✅ Remote added" -ForegroundColor Green
}

Write-Host ""
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan

# Try to push
try {
    git branch -M main
    git push -u origin main
    Write-Host "✅ Code pushed to GitHub!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "⚠️  Push failed. You may need to:" -ForegroundColor Yellow
    Write-Host "   1. Create the repository on GitHub first: https://github.com/new" -ForegroundColor White
    Write-Host "   2. Repository name: $repoName" -ForegroundColor White
    Write-Host "   3. Set it to Private" -ForegroundColor White
    Write-Host "   4. Don't initialize with README" -ForegroundColor White
    Write-Host "   5. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "   Or use GitHub CLI: gh repo create $repoName --private --source=. --remote=origin" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   ✅ GITHUB SETUP COMPLETE!                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Ask about deployment
Write-Host "🚀 Deploy to Droplet?" -ForegroundColor Cyan
Write-Host ""
Write-Host "Droplet IP: 143.110.254.40" -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor White
Write-Host "  ✅ Clone from GitHub to droplet" -ForegroundColor White
Write-Host "  ✅ Install Docker & dependencies" -ForegroundColor White
Write-Host "  ✅ Start all services" -ForegroundColor White
Write-Host "  ✅ Configure Telegram bot" -ForegroundColor White
Write-Host ""

$deploy = Read-Host "Deploy now? (y/n)"

if ($deploy -eq 'y') {
    Write-Host ""
    Write-Host "🚀 Starting deployment..." -ForegroundColor Cyan
    Write-Host ""
    
    # Run deployment script
    bash deploy_git.sh "$username/$repoName"
    
} else {
    Write-Host ""
    Write-Host "ℹ️  To deploy later, run:" -ForegroundColor Cyan
    Write-Host "   bash deploy_git.sh $username/$repoName" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open Telegram: @hackingmasterr" -ForegroundColor White
Write-Host "   2. Send: /start" -ForegroundColor White
Write-Host "   3. Upload a combo file" -ForegroundColor White
Write-Host "   4. Run: /auto_scan" -ForegroundColor White
Write-Host ""
Write-Host "🎉 All done!" -ForegroundColor Green
Write-Host ""
