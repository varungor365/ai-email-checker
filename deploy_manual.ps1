# Simple Deployment Commands
# Copy and paste these into your SSH session

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║          AI Email Checker - Manual Deployment Guide           ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

Write-Host "🔑 Droplet Password: " -NoNewline -ForegroundColor Cyan
Write-Host "varun@365Varun" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 1: Connect to your droplet" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""
Write-Host "ssh root@143.110.254.40" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to continue..." -ForegroundColor Gray
$null = Read-Host

Write-Host ""
Write-Host "Step 2: Once connected, run these commands" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

$commands = @"
# Update system and install dependencies
apt-get update && apt-get install -y git curl docker.io docker-compose python3 python3-pip python3-venv nginx ufw

# Clone your repository
cd /opt
rm -rf ai-email-checker
git clone https://github.com/varungor365/ai-email-checker.git
cd ai-email-checker

# Create environment file
cat > .env << 'ENVEOF'
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
POSTGRES_PASSWORD=secure_pass_123
MONGODB_HOST=localhost
MONGODB_PORT=27017
REDIS_HOST=localhost
REDIS_PORT=6379
API_HOST=0.0.0.0
API_PORT=8000
MIN_QUALITY_SCORE=75
BREACH_THRESHOLD=10
PASSWORD_STRENGTH_MIN=3
ENVEOF

# Start Docker services
docker-compose up -d

# Wait for services to start
sleep 15

# Install Python dependencies
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Pull AI model (optional, will auto-download on first use)
docker exec ai-email-checker-ollama-1 ollama pull mistral

# Create systemd service for auto-start
cat > /etc/systemd/system/autonomous-checker.service << 'SVCEOF'
[Unit]
Description=AI Email Checker - Autonomous System
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-email-checker
Environment="PATH=/opt/ai-email-checker/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ai-email-checker/.venv/bin/python start_autonomous.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

# Enable and start the service
systemctl daemon-reload
systemctl enable autonomous-checker
systemctl start autonomous-checker

# Configure firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
echo 'y' | ufw enable

# Check status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deployment Complete! Checking status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose ps
echo ""
systemctl status autonomous-checker --no-pager | head -10
"@

Write-Host $commands -ForegroundColor Cyan

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Write-Host "📋 Commands copied to clipboard!" -ForegroundColor Green
$commands | Set-Clipboard

Write-Host ""
Write-Host "✨ Quick Start:" -ForegroundColor Cyan
Write-Host "   1. Run: " -NoNewline
Write-Host "ssh root@143.110.254.40" -ForegroundColor Yellow
Write-Host "   2. Password: " -NoNewline
Write-Host "varun@365Varun" -ForegroundColor Yellow
Write-Host "   3. Paste the commands (Ctrl+V or Right-click)" -ForegroundColor White
Write-Host "   4. Wait ~5 minutes for installation" -ForegroundColor White
Write-Host ""

Write-Host "📱 After Deployment:" -ForegroundColor Cyan
Write-Host "   • Open Telegram → @hackingmasterr" -ForegroundColor White
Write-Host "   • Send: /start" -ForegroundColor White
Write-Host "   • Upload combo file" -ForegroundColor White
Write-Host "   • Send: /auto_scan" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Monitor Progress:" -ForegroundColor Cyan
Write-Host "   journalctl -u autonomous-checker -f" -ForegroundColor Yellow
Write-Host ""

Write-Host "🎉 Ready to deploy!" -ForegroundColor Green
Write-Host ""
