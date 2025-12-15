<#
.SYNOPSIS
    Deploy AI Checker to DigitalOcean with one command

.DESCRIPTION
    Automated deployment script for AI-Driven Autonomous Security Research Framework
    Creates droplet, uploads code, starts services, and provides dashboard access

.PARAMETER DOToken
    DigitalOcean API token (required)
    Get from: https://cloud.digitalocean.com/account/api/tokens

.PARAMETER DropletName
    Name for the droplet (default: ai-checker-prod)

.PARAMETER Region
    DigitalOcean region (default: nyc3)
    Options: nyc1, nyc3, sfo3, ams3, sgp1, lon1, fra1, tor1

.PARAMETER Size
    Droplet size (default: c-4 = 4 vCPU, 8GB RAM)
    Options:
    - s-2vcpu-4gb: $24/month (2 vCPU, 4GB RAM) - Budget
    - c-4: $63/month (4 vCPU, 8GB RAM) - Recommended
    - c-8: $126/month (8 vCPU, 16GB RAM) - Performance
    - c-16: $252/month (16 vCPU, 32GB RAM) - Enterprise

.PARAMETER EnableBackups
    Enable automated backups (default: true)
    Cost: 10% of droplet price

.EXAMPLE
    .\deploy.ps1 -DOToken "dop_v1_abc123..."
    
.EXAMPLE
    .\deploy.ps1 -DOToken "dop_v1_abc123..." -Size "c-8" -Region "sfo3"

.NOTES
    Author: AI Checker Team
    Requires: PowerShell 5.1+, Internet connection
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="DigitalOcean API token")]
    [string]$DOToken,
    
    [string]$DropletName = "ai-checker-prod",
    
    [ValidateSet("nyc1", "nyc3", "sfo3", "ams3", "sgp1", "lon1", "fra1", "tor1", "blr1")]
    [string]$Region = "nyc3",
    
    [ValidateSet("s-2vcpu-4gb", "c-4", "c-8", "c-16")]
    [string]$Size = "c-4",
    
    [bool]$EnableBackups = $true
)

# Color output functions
function Write-Step {
    param([string]$Message)
    Write-Host "`n$Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Banner
Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   AI-Driven Autonomous Security Research Framework          ║
║   DigitalOcean Deployment Script                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""

# Validate token
if ($DOToken.Length -lt 50) {
    Write-Error "Invalid DigitalOcean API token"
    Write-Host "Get your token from: https://cloud.digitalocean.com/account/api/tokens"
    exit 1
}

# Configuration summary
Write-Step "Deployment Configuration"
Write-Host "  Droplet Name: $DropletName"
Write-Host "  Region: $Region"
Write-Host "  Size: $Size"
Write-Host "  Backups: $EnableBackups"
Write-Host ""

# Pricing info
$pricing = @{
    "s-2vcpu-4gb" = 24
    "c-4" = 63
    "c-8" = 126
    "c-16" = 252
}
$monthlyCost = $pricing[$Size]
if ($EnableBackups) {
    $monthlyCost += [math]::Round($monthlyCost * 0.1, 2)
}

Write-Host "  Estimated Cost: `$$monthlyCost/month" -ForegroundColor Yellow
Write-Host ""

# Confirm
$confirm = Read-Host "Continue with deployment? (y/n)"
if ($confirm -ne 'y') {
    Write-Warning "Deployment cancelled"
    exit 0
}

# API headers
$headers = @{
    "Authorization" = "Bearer $DOToken"
    "Content-Type" = "application/json"
}

try {
    # Step 1: SSH Key
    Write-Step "Step 1/6: SSH Key Setup"
    
    $sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa.pub"
    
    if (-not (Test-Path $sshKeyPath)) {
        Write-Warning "SSH key not found. Generating new key..."
        ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N '""' | Out-Null
        Write-Success "SSH key generated"
    }
    
    $sshKey = Get-Content $sshKeyPath -Raw
    
    # Upload SSH key
    $sshKeyBody = @{
        name = "ai-checker-key-$(Get-Date -Format 'yyyyMMdd')"
        public_key = $sshKey.Trim()
    } | ConvertTo-Json
    
    try {
        $sshKeyResponse = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/account/keys" `
            -Method Post -Headers $headers -Body $sshKeyBody
        $sshKeyId = $sshKeyResponse.ssh_key.id
        Write-Success "SSH key uploaded (ID: $sshKeyId)"
    } catch {
        # Key might already exist, try to find it
        $existingKeys = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/account/keys" -Headers $headers
        $sshKeyId = ($existingKeys.ssh_keys | Where-Object { $_.public_key.Trim() -eq $sshKey.Trim() })[0].id
        
        if ($sshKeyId) {
            Write-Success "Using existing SSH key (ID: $sshKeyId)"
        } else {
            throw "Failed to upload SSH key"
        }
    }
    
    # Step 2: Create Droplet
    Write-Step "Step 2/6: Creating Droplet"
    
    $userData = @'
#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

echo "🚀 AI Checker Setup Starting..."

# Update system
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Python 3.11
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install nginx
apt-get install -y nginx certbot python3-certbot-nginx

# Install monitoring tools
apt-get install -y htop iotop nethogs ncdu

# Create 8GB swap
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# System optimization
cat >> /etc/sysctl.conf << 'EOF'
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
fs.file-max = 2097152
vm.swappiness = 10
vm.dirty_ratio = 60
vm.dirty_background_ratio = 2
EOF
sysctl -p

# File limits
cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 1000000
* hard nofile 1000000
EOF

# Firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp
ufw allow 8000/tcp
ufw --force enable

# Create app directory
mkdir -p /opt/ai-checker/{uploads/{combos,configs,proxies},results/{hits,logs},logs}
cd /opt/ai-checker

# Create .env
cat > .env << 'ENVEOF'
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=SecureP@ssw0rd!ChangeThis
DB_NAME=ai_checker

MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_USER=admin
MONGO_PASSWORD=SecureP@ssw0rd!ChangeThis
MONGO_DB=ai_checker

REDIS_HOST=redis
REDIS_PORT=6379

API_SECRET_KEY=ChangeThisToRandomString123!
API_HOST=0.0.0.0
API_PORT=8000

OPTIMIZER_ENABLED=true
OPTIMIZER_INTERVAL=60
MIN_WORKERS=1
MAX_WORKERS=20
TARGET_CPU=70
TARGET_MEMORY=80
ENVEOF

# Install Watchtower
docker run -d --name watchtower --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower --cleanup --interval 3600

echo "✅ Setup completed at $(date)" > /root/setup-complete.txt
'@
    
    $dropletBody = @{
        name = $DropletName
        region = $Region
        size = $Size
        image = "ubuntu-22-04-x64"
        ssh_keys = @($sshKeyId)
        backups = $EnableBackups
        ipv6 = $true
        monitoring = $true
        tags = @("ai-checker", "production")
        user_data = $userData
    } | ConvertTo-Json
    
    $droplet = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/droplets" `
        -Method Post -Headers $headers -Body $dropletBody
    $dropletId = $droplet.droplet.id
    
    Write-Success "Droplet created (ID: $dropletId)"
    
    # Step 3: Wait for droplet
    Write-Step "Step 3/6: Waiting for Droplet Boot"
    Write-Host "  This takes about 60 seconds..." -ForegroundColor Gray
    
    Start-Sleep -Seconds 60
    
    # Get droplet info
    $dropletInfo = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/droplets/$dropletId" -Headers $headers
    $ipAddress = $dropletInfo.droplet.networks.v4 | Where-Object { $_.type -eq "public" } | Select-Object -ExpandProperty ip_address
    
    Write-Success "Droplet IP: $ipAddress"
    
    # Step 4: Wait for setup to complete
    Write-Step "Step 4/6: Waiting for Setup Script"
    Write-Host "  Installing Docker, Python, Node.js..." -ForegroundColor Gray
    
    $setupComplete = $false
    $maxAttempts = 30
    $attempt = 0
    
    while (-not $setupComplete -and $attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 10
        $attempt++
        
        try {
            $result = ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$ipAddress "test -f /root/setup-complete.txt && echo 'complete'"
            if ($result -eq "complete") {
                $setupComplete = $true
            }
        } catch {
            # Still setting up
        }
        
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    
    if ($setupComplete) {
        Write-Success "Setup script completed"
    } else {
        Write-Warning "Setup script may still be running. Continue deployment..."
    }
    
    # Step 5: Upload code
    Write-Step "Step 5/6: Uploading Code"
    
    $localPath = (Get-Location).Path
    scp -o StrictHostKeyChecking=no -r "$localPath\*" root@${ipAddress}:/opt/ai-checker/
    
    Write-Success "Code uploaded"
    
    # Step 6: Start services
    Write-Step "Step 6/6: Starting Services"
    
    ssh -o StrictHostKeyChecking=no root@$ipAddress @"
cd /opt/ai-checker
docker-compose up -d --build
"@
    
    Write-Success "Services started"
    
    # Success banner
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "║               🎉 DEPLOYMENT SUCCESSFUL! 🎉                   ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📍 Droplet Information:" -ForegroundColor Cyan
    Write-Host "  ID: $dropletId"
    Write-Host "  IP: $ipAddress"
    Write-Host "  Region: $Region"
    Write-Host "  Size: $Size"
    Write-Host ""
    
    Write-Host "🌐 Access Your System:" -ForegroundColor Cyan
    Write-Host "  Dashboard: http://$ipAddress:3000" -ForegroundColor Yellow
    Write-Host "  API: http://$ipAddress:8000" -ForegroundColor Yellow
    Write-Host "  SSH: ssh root@$ipAddress" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "📝 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Open dashboard: http://$ipAddress:3000"
    Write-Host "  2. Upload combo list (Combos tab)"
    Write-Host "  3. Start checking (System Control)"
    Write-Host "  4. Monitor real-time stats"
    Write-Host "  5. Download results when complete"
    Write-Host ""
    
    Write-Host "🔒 Security Recommendations:" -ForegroundColor Yellow
    Write-Host "  1. Change passwords in /opt/ai-checker/.env"
    Write-Host "  2. Setup SSL: certbot --nginx -d yourdomain.com"
    Write-Host "  3. Create non-root user: adduser admin"
    Write-Host "  4. Disable root SSH: PermitRootLogin no"
    Write-Host ""
    
    Write-Host "💰 Monthly Cost: `$$monthlyCost" -ForegroundColor Cyan
    Write-Host ""
    
    # Save deployment info
    $deployInfo = @"
AI Checker Deployment Information
===================================

Deployed: $(Get-Date)

Droplet Details:
  ID: $dropletId
  Name: $DropletName
  IP: $ipAddress
  Region: $Region
  Size: $Size
  Backups: $EnableBackups
  Cost: `$$monthlyCost/month

Access:
  Dashboard: http://$ipAddress:3000
  API: http://$ipAddress:8000
  SSH: ssh root@$ipAddress

Credentials:
  Database: See /opt/ai-checker/.env
  Dashboard: No auth (set up basic auth)

Next Steps:
  1. Change passwords in .env
  2. Setup SSL certificate
  3. Create admin user
  4. Upload combo lists
  5. Start checking

Support:
  Documentation: See docs/ folder
  Deployment Guide: REMOTE_DEPLOYMENT_SUMMARY.md
  Dashboard Guide: REMOTE_DASHBOARD.md
  Optimization: AI_OPTIMIZATION.md
"@
    
    $deployInfo | Out-File -FilePath "deployment-info-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    Write-Success "Deployment info saved to deployment-info-*.txt"
    
    Write-Host ""
    Write-Host "🚀 Your AI Checker is now running 24/7!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Error "Deployment failed: $_"
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check your DigitalOcean API token"
    Write-Host "  2. Verify account has credit"
    Write-Host "  3. Try a different region"
    Write-Host "  4. Check deployment-info-*.txt for details"
    Write-Host ""
    exit 1
}
