# 🚀 Quick Start Script

# This script sets up the complete AI Email Checker framework from scratch

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  AI-Driven Autonomous Email Security Research Framework Setup   " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/10] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ Docker found" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Docker not found (optional, but recommended)" -ForegroundColor Yellow
}

# Create .env from example
Write-Host "`n[2/10] Creating environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "  ✓ Created .env file" -ForegroundColor Green
    Write-Host "  ⚠ IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ .env already exists" -ForegroundColor Green
}

# Create virtual environment
Write-Host "`n[3/10] Creating Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path venv)) {
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[4/10] Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "`n[5/10] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "  ✓ Pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host "`n[6/10] Installing Python dependencies (this may take a while)..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host "`n[7/10] Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium firefox
Write-Host "  ✓ Playwright browsers installed" -ForegroundColor Green

# Create necessary directories
Write-Host "`n[8/10] Creating directory structure..." -ForegroundColor Yellow
$directories = @(
    "logs",
    "data",
    "data/cache",
    "data/results",
    "vault",
    "vault/sessions",
    "models"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "  ✓ Directory structure created" -ForegroundColor Green

# Check if Docker is available for services
Write-Host "`n[9/10] Checking for backend services..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  Docker is available. You can start services with:" -ForegroundColor Green
    Write-Host "    docker-compose up -d" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠ Please install and configure manually:" -ForegroundColor Yellow
    Write-Host "    - PostgreSQL" -ForegroundColor White
    Write-Host "    - Redis" -ForegroundColor White
    Write-Host "    - MongoDB" -ForegroundColor White
    Write-Host "    - Ollama (for LLM features)" -ForegroundColor White
}

# Final instructions
Write-Host "`n[10/10] Setup complete!" -ForegroundColor Yellow
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "                         NEXT STEPS                               " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Edit .env and add your API keys:" -ForegroundColor Yellow
Write-Host "   - OSINT APIs (Dehashed, IntelX)" -ForegroundColor White
Write-Host "   - Proxy services (BrightData, Smartproxy)" -ForegroundColor White
Write-Host "   - CAPTCHA solvers (2Captcha, Anti-Captcha)" -ForegroundColor White
Write-Host ""
Write-Host "2. Start backend services:" -ForegroundColor Yellow
Write-Host "   Option A (Docker - Recommended):" -ForegroundColor White
Write-Host "     docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Option B (Manual):" -ForegroundColor White
Write-Host "     - Start PostgreSQL" -ForegroundColor Cyan
Write-Host "     - Start Redis" -ForegroundColor Cyan
Write-Host "     - Start MongoDB" -ForegroundColor Cyan
Write-Host "     - Start Ollama (optional)" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Start the application:" -ForegroundColor Yellow
Write-Host "   Terminal 1 - API Server:" -ForegroundColor White
Write-Host "     uvicorn api.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Terminal 2 - Worker:" -ForegroundColor White
Write-Host "     celery -A workers.tasks worker --loglevel=info" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Access the system:" -ForegroundColor Yellow
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Health: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "For detailed documentation, see: docs/guides/installation.md" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
