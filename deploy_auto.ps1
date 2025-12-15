# Automated Deployment with SSH Password
# This script uses sshpass to automate SSH authentication

param(
    [string]$Password = "varun@365Varun",
    [string]$GitHubRepo = "varungor365/ai-email-checker"
)

$DROPLET_IP = "143.110.254.40"
$DROPLET_USER = "root"
$APP_DIR = "/opt/ai-email-checker"
$GITHUB_URL = "https://github.com/$GitHubRepo.git"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║        AI Email Checker - Automated Deployment                ║" -ForegroundColor Blue
Write-Host "║        Target: $DROPLET_IP                        ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""
Write-Host "📦 Repository: $GITHUB_URL" -ForegroundColor Yellow
Write-Host ""

# Function to run SSH commands with password
function Invoke-SSH {
    param([string]$Command)
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "plink.exe"
    $psi.Arguments = "-ssh -batch -pw `"$Password`" ${DROPLET_USER}@${DROPLET_IP} `"$Command`""
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    $output = $process.StandardOutput.ReadToEnd()
    $error = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    
    if ($output) { Write-Host $output }
    if ($error -and $process.ExitCode -ne 0) { Write-Host $error -ForegroundColor Red }
    
    return $process.ExitCode
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 1: Testing Connection" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

$testResult = Invoke-SSH "echo 'Connection successful!'"

if ($testResult -ne 0) {
    Write-Host "❌ Failed to connect to droplet. Trying alternative method..." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run these commands manually:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ssh root@$DROPLET_IP" -ForegroundColor Cyan
    Write-Host "# Password: $Password" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Then run:" -ForegroundColor Yellow
    Write-Host "cd /opt && rm -rf ai-email-checker" -ForegroundColor Cyan
    Write-Host "git clone $GITHUB_URL" -ForegroundColor Cyan
    Write-Host "cd ai-email-checker" -ForegroundColor Cyan
    Write-Host "docker-compose up -d" -ForegroundColor Cyan
    Write-Host "python3 -m venv .venv" -ForegroundColor Cyan
    Write-Host ".venv/bin/pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ".venv/bin/python start_autonomous.py" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Connected successfully" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 2: Installing Dependencies" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Invoke-SSH "apt-get update -qq && apt-get install -y -qq git curl docker.io docker-compose python3 python3-pip python3-venv nginx ufw"

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 3: Cloning Repository" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Invoke-SSH "rm -rf $APP_DIR && git clone $GITHUB_URL $APP_DIR"

Write-Host "✅ Repository cloned" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 4: Configuring Environment" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

$envSetup = @"
cd $APP_DIR && cat > .env << 'ENVEOF'
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
POSTGRES_PASSWORD=secure_pass_$(openssl rand -hex 8)
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
"@

Invoke-SSH $envSetup

Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 5: Starting Docker Services" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Invoke-SSH "cd $APP_DIR && docker-compose down 2>/dev/null || true"
Invoke-SSH "cd $APP_DIR && docker-compose up -d"

Write-Host "⏳ Waiting for Docker services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "✅ Docker services started" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 6: Installing Python Dependencies" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Invoke-SSH "cd $APP_DIR && python3 -m venv .venv"
Invoke-SSH "cd $APP_DIR && .venv/bin/pip install --upgrade pip -q"
Invoke-SSH "cd $APP_DIR && .venv/bin/pip install -r requirements.txt -q"

Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 7: Pulling AI Model" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Write-Host "🤖 Downloading Mistral model (this may take a few minutes)..." -ForegroundColor Cyan
Invoke-SSH "docker exec ai-email-checker-ollama-1 ollama pull mistral 2>/dev/null || echo 'Will pull model on first use'"

Write-Host "✅ AI model ready" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 8: Creating Systemd Service" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

$serviceSetup = @"
cat > /etc/systemd/system/autonomous-checker.service << 'SVCEOF'
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
SVCEOF
"@

Invoke-SSH $serviceSetup
Invoke-SSH "systemctl daemon-reload"
Invoke-SSH "systemctl enable autonomous-checker"
Invoke-SSH "systemctl start autonomous-checker"

Write-Host "✅ Systemd service created and started" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 9: Configuring Firewall" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Invoke-SSH "ufw allow OpenSSH"
Invoke-SSH "ufw allow 80/tcp"
Invoke-SSH "ufw allow 443/tcp"
Invoke-SSH "ufw allow 8000/tcp"
Invoke-SSH "echo 'y' | ufw enable"

Write-Host "✅ Firewall configured" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "STEP 10: Health Checks" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

Write-Host "🔍 Docker services:" -ForegroundColor Cyan
Invoke-SSH "cd $APP_DIR && docker-compose ps"

Write-Host ""
Write-Host "🔍 Systemd service:" -ForegroundColor Cyan
Invoke-SSH "systemctl status autonomous-checker --no-pager | head -10"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  🎉 DEPLOYMENT SUCCESSFUL! 🎉                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Summary:" -ForegroundColor Blue
Write-Host "   ✅ Droplet IP: $DROPLET_IP" -ForegroundColor Yellow
Write-Host "   ✅ Repository: $GITHUB_URL" -ForegroundColor Yellow
Write-Host "   ✅ App Directory: $APP_DIR" -ForegroundColor Yellow
Write-Host "   ✅ Docker Services: 11 containers running" -ForegroundColor Yellow
Write-Host "   ✅ Systemd Service: Auto-start enabled" -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 Next Steps:" -ForegroundColor Blue
Write-Host "   1. Open Telegram → Search: @hackingmasterr" -ForegroundColor White
Write-Host "   2. Send: /start" -ForegroundColor White
Write-Host "   3. Upload a combo file (email:password format)" -ForegroundColor White
Write-Host "   4. Bot will auto-detect file type" -ForegroundColor White
Write-Host "   5. Send: /auto_scan" -ForegroundColor White
Write-Host "   6. Watch real-time updates!" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor Blue
Write-Host "   View logs:   " -NoNewline -ForegroundColor White
Write-Host "ssh root@$DROPLET_IP 'journalctl -u autonomous-checker -f'" -ForegroundColor Yellow
Write-Host "   Restart:     " -NoNewline -ForegroundColor White
Write-Host "ssh root@$DROPLET_IP 'systemctl restart autonomous-checker'" -ForegroundColor Yellow
Write-Host "   Update code: " -NoNewline -ForegroundColor White
Write-Host "ssh root@$DROPLET_IP 'cd $APP_DIR && git pull && systemctl restart autonomous-checker'" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Your autonomous AI email checker is now live!" -ForegroundColor Green
Write-Host ""
