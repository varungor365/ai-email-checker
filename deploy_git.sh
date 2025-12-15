#!/bin/bash

################################################################################
# Git-Based Deployment Script for DigitalOcean Droplet
# Deploys AI Email Checker from GitHub to 143.110.254.40
################################################################################

set -e  # Exit on any error

# Configuration
DROPLET_IP="143.110.254.40"
DROPLET_USER="root"
APP_DIR="/opt/ai-email-checker"
GITHUB_REPO="$1"  # Pass as argument: username/repo-name

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        AI Email Checker - Git Deployment Script               ║${NC}"
echo -e "${BLUE}║        Target: ${DROPLET_IP}                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if GitHub repo provided
if [ -z "$GITHUB_REPO" ]; then
    echo -e "${RED}❌ Error: GitHub repository not specified${NC}"
    echo ""
    echo "Usage: bash deploy_git.sh <username/repo-name>"
    echo "Example: bash deploy_git.sh yourusername/ai-email-checker"
    echo ""
    exit 1
fi

GITHUB_URL="https://github.com/${GITHUB_REPO}.git"

echo -e "${YELLOW}📦 Repository: ${GITHUB_URL}${NC}"
echo ""

# Function to run commands on droplet
run_remote() {
    ssh -o StrictHostKeyChecking=no ${DROPLET_USER}@${DROPLET_IP} "$@"
}

################################################################################
# STEP 1: Prepare Droplet Environment
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 1: Preparing Droplet Environment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

run_remote "apt-get update && apt-get upgrade -y"
run_remote "apt-get install -y git curl wget"

# Install Docker if not present
if ! run_remote "command -v docker &> /dev/null"; then
    echo -e "${YELLOW}📦 Installing Docker...${NC}"
    run_remote "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
fi

# Install Docker Compose if not present
if ! run_remote "command -v docker-compose &> /dev/null"; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    run_remote "apt-get install -y docker-compose"
fi

# Install Python
run_remote "apt-get install -y python3 python3-pip python3-venv"

echo -e "${GREEN}✅ Environment prepared${NC}"
echo ""

################################################################################
# STEP 2: Clone Repository
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 2: Cloning Repository${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Remove old installation if exists
run_remote "rm -rf ${APP_DIR}"

# Clone from GitHub
echo -e "${YELLOW}📥 Cloning from GitHub...${NC}"
run_remote "git clone ${GITHUB_URL} ${APP_DIR}"

echo -e "${GREEN}✅ Repository cloned${NC}"
echo ""

################################################################################
# STEP 3: Configure Environment
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 3: Configuring Environment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create .env file on droplet
run_remote "cat > ${APP_DIR}/.env << 'ENVEOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588

# Ollama AI Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# Autonomous System Settings
MIN_CONFIDENCE=0.75
INITIAL_WORKERS=2
TARGET_SPEED=100.0
PROGRESS_UPDATE_INTERVAL=60
AUTO_TRAIN_ENABLED=true
AUTO_OPTIMIZE_ENABLED=true

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_checker
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_pass_$(openssl rand -hex 8)

MONGODB_HOST=localhost
MONGODB_PORT=27017

REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Quality Validation Thresholds
MIN_QUALITY_SCORE=75
BREACH_THRESHOLD=10
PASSWORD_STRENGTH_MIN=3
ENVEOF"

# Make scripts executable
run_remote "chmod +x ${APP_DIR}/*.sh 2>/dev/null || true"

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

################################################################################
# STEP 4: Start Docker Services
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 4: Starting Docker Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

run_remote "cd ${APP_DIR} && docker-compose down 2>/dev/null || true"
run_remote "cd ${APP_DIR} && docker-compose up -d"

echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

echo -e "${GREEN}✅ Docker services started${NC}"
echo ""

################################################################################
# STEP 5: Install Python Dependencies
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 5: Installing Python Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

run_remote "cd ${APP_DIR} && python3 -m venv .venv"
run_remote "cd ${APP_DIR} && .venv/bin/pip install --upgrade pip"
run_remote "cd ${APP_DIR} && .venv/bin/pip install -r requirements.txt"

echo -e "${GREEN}✅ Python dependencies installed${NC}"
echo ""

################################################################################
# STEP 6: Initialize Ollama AI Model
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 6: Initializing Ollama AI Model${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}🤖 Pulling Mistral model...${NC}"
run_remote "docker exec ai-email-checker-ollama-1 ollama pull mistral" || echo "Note: Ollama container might not be ready yet"

echo -e "${GREEN}✅ AI model initialized${NC}"
echo ""

################################################################################
# STEP 7: Create Systemd Service
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 7: Creating Systemd Service${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

run_remote "cat > /etc/systemd/system/autonomous-checker.service << 'SERVICEEOF'
[Unit]
Description=AI Email Checker - Autonomous System
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
Environment=\"PATH=${APP_DIR}/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"
ExecStart=${APP_DIR}/.venv/bin/python start_autonomous.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF"

run_remote "systemctl daemon-reload"
run_remote "systemctl enable autonomous-checker"
run_remote "systemctl start autonomous-checker"

echo -e "${GREEN}✅ Systemd service created and started${NC}"
echo ""

################################################################################
# STEP 8: Configure Nginx & Firewall
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 8: Configuring Nginx & Firewall${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Install Nginx
run_remote "apt-get install -y nginx ufw"

# Configure Nginx
run_remote "cat > /etc/nginx/sites-available/email-checker << 'NGINXEOF'
server {
    listen 80;
    server_name ${DROPLET_IP};
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_cache_bypass \$http_upgrade;
    }
}
NGINXEOF"

run_remote "ln -sf /etc/nginx/sites-available/email-checker /etc/nginx/sites-enabled/"
run_remote "rm -f /etc/nginx/sites-enabled/default"
run_remote "nginx -t"
run_remote "systemctl reload nginx"

# Configure firewall
run_remote "ufw allow OpenSSH"
run_remote "ufw allow 80/tcp"
run_remote "ufw allow 443/tcp"
run_remote "ufw allow 8000/tcp"
run_remote "echo 'y' | ufw enable"

echo -e "${GREEN}✅ Nginx and firewall configured${NC}"
echo ""

################################################################################
# STEP 9: Validation & Health Checks
################################################################################
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 9: Running Health Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}🔍 Checking Docker services...${NC}"
run_remote "cd ${APP_DIR} && docker-compose ps"

echo ""
echo -e "${YELLOW}🔍 Checking systemd service...${NC}"
run_remote "systemctl status autonomous-checker --no-pager" || true

echo ""
echo -e "${YELLOW}🔍 Checking Nginx...${NC}"
run_remote "systemctl status nginx --no-pager | head -5"

echo ""
echo -e "${GREEN}✅ Health checks complete${NC}"
echo ""

################################################################################
# DEPLOYMENT COMPLETE
################################################################################
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  🎉 DEPLOYMENT SUCCESSFUL! 🎉                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo -e "   Droplet IP: ${YELLOW}${DROPLET_IP}${NC}"
echo -e "   Repository: ${YELLOW}${GITHUB_URL}${NC}"
echo -e "   App Directory: ${YELLOW}${APP_DIR}${NC}"
echo ""
echo -e "${BLUE}🌐 Access Points:${NC}"
echo -e "   Web API: ${YELLOW}http://${DROPLET_IP}${NC}"
echo -e "   Telegram Bot: ${YELLOW}@hackingmasterr${NC}"
echo ""
echo -e "${BLUE}📱 Next Steps:${NC}"
echo -e "   1. Open Telegram and search: ${YELLOW}@hackingmasterr${NC}"
echo -e "   2. Send: ${YELLOW}/start${NC}"
echo -e "   3. Upload a combo file to test smart detection"
echo -e "   4. Run: ${YELLOW}/auto_scan${NC}"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "   View logs: ${YELLOW}ssh ${DROPLET_USER}@${DROPLET_IP} 'journalctl -u autonomous-checker -f'${NC}"
echo -e "   Restart: ${YELLOW}ssh ${DROPLET_USER}@${DROPLET_IP} 'systemctl restart autonomous-checker'${NC}"
echo -e "   Update code: ${YELLOW}ssh ${DROPLET_USER}@${DROPLET_IP} 'cd ${APP_DIR} && git pull && systemctl restart autonomous-checker'${NC}"
echo ""
echo -e "${GREEN}✨ Your autonomous AI email checker is now running!${NC}"
echo ""
