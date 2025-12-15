# PowerShell Deployment Script for DigitalOcean Droplet
# Deploys AI Email Checker from GitHub to 143.110.254.40

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubRepo
)

$ErrorActionPreference = "Continue"

# Configuration
$DROPLET_IP = "143.110.254.40"
$DROPLET_USER = "root"
$APP_DIR = "/opt/ai-email-checker"
$GITHUB_URL = "https://github.com/$GitHubRepo.git"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║        AI Email Checker - Droplet Deployment                  ║" -ForegroundColor Blue
Write-Host "║        Target: $DROPLET_IP                        ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""
Write-Host "📦 Repository: $GITHUB_URL" -ForegroundColor Yellow
Write-Host ""

# Function to run SSH commands
function Invoke-SSHCommand {
    param([string]$Command)
    $sshCommand = "ssh -o StrictHostKeyChecking=no ${DROPLET_USER}@${DROPLET_IP} '$Command'"
    Invoke-Expression $sshCommand
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 1: Preparing Droplet Environment" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
ssh ${DROPLET_USER}@${DROPLET_IP} "apt-get update && apt-get install -y git curl wget docker.io docker-compose python3 python3-pip python3-venv nginx ufw"

Write-Host "✅ Environment prepared" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 2: Cloning Repository" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

ssh ${DROPLET_USER}@${DROPLET_IP} "rm -rf $APP_DIR && git clone $GITHUB_URL $APP_DIR"

Write-Host "✅ Repository cloned" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 3: Configuring Environment" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

$envContent = @"
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
MIN_CONFIDENCE=0.75
INITIAL_WORKERS=2
TARGET_SPEED=100.0
PROGRESS_UPDATE_INTERVAL=60
AUTO_TRAIN_ENABLED=true
AUTO_OPTIMIZE_ENABLED=true
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_checker
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password_123
MONGODB_HOST=localhost
MONGODB_PORT=27017
REDIS_HOST=localhost
REDIS_PORT=6379
API_HOST=0.0.0.0
API_PORT=8000
MIN_QUALITY_SCORE=75
BREACH_THRESHOLD=10
PASSWORD_STRENGTH_MIN=3
"@

ssh ${DROPLET_USER}@${DROPLET_IP} "cat > $APP_DIR/.env << 'ENVEOF'
$envContent
ENVEOF"

Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 4: Starting Docker Services" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

ssh ${DROPLET_USER}@${DROPLET_IP} "cd $APP_DIR && docker-compose down 2>/dev/null || true"
ssh ${DROPLET_USER}@${DROPLET_IP} "cd $APP_DIR && docker-compose up -d"

Write-Host "⏳ Waiting for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "✅ Docker services started" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 5: Installing Python Dependencies" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

ssh ${DROPLET_USER}@${DROPLET_IP} "cd $APP_DIR && python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt"

Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 6: Creating Systemd Service" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

$serviceContent = @"
[Unit]
Description=AI Email Checker - Autonomous System
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$APP_DIR/.venv/bin/python start_autonomous.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"@

ssh ${DROPLET_USER}@${DROPLET_IP} "cat > /etc/systemd/system/autonomous-checker.service << 'SERVICEEOF'
$serviceContent
SERVICEEOF"

ssh ${DROPLET_USER}@${DROPLET_IP} "systemctl daemon-reload && systemctl enable autonomous-checker && systemctl start autonomous-checker"

Write-Host "✅ Systemd service created" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 7: Configuring Nginx & Firewall" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

ssh ${DROPLET_USER}@${DROPLET_IP} "ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 8000/tcp && echo 'y' | ufw enable"

Write-Host "✅ Firewall configured" -ForegroundColor Green
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  🎉 DEPLOYMENT SUCCESSFUL! 🎉                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Summary:" -ForegroundColor Blue
Write-Host "   Droplet IP: $DROPLET_IP" -ForegroundColor Yellow
Write-Host "   Repository: $GITHUB_URL" -ForegroundColor Yellow
Write-Host "   App Directory: $APP_DIR" -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 Next Steps:" -ForegroundColor Blue
Write-Host "   1. Open Telegram: @hackingmasterr" -ForegroundColor White
Write-Host "   2. Send: /start" -ForegroundColor White
Write-Host "   3. Upload combo file" -ForegroundColor White
Write-Host "   4. Run: /auto_scan" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Check status:" -ForegroundColor Blue
Write-Host "   ssh ${DROPLET_USER}@${DROPLET_IP} 'systemctl status autonomous-checker'" -ForegroundColor Yellow
Write-Host ""
