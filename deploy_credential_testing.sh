#!/bin/bash
# Deploy Credential Testing System to DigitalOcean Droplet
# Run on droplet: bash deploy_credential_testing.sh

echo "🔓 Deploying Credential Testing System"
echo "========================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📥 Pulling latest code from GitHub...${NC}"
cd /opt/ai-email-checker
git fetch --all
git reset --hard origin/main
git pull

echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
source .venv/bin/activate

# Install dependencies in correct order to avoid conflicts
echo -e "${YELLOW}Installing mega.py dependencies...${NC}"

# First, install pycryptodome (needed by mega.py)
pip install pycryptodome

# Install pathlib separately
pip install pathlib

# Install mega.py with --no-deps to avoid tenacity conflict
pip install --no-deps mega.py

# Now install requests (mega.py dependency)
pip install requests

# Finally, install correct tenacity version (for langchain)
# mega.py will work fine with newer tenacity despite its requirements
pip install --force-reinstall "tenacity>=8.1.0,<10.0.0"

# Install aiohttp for breach detection
pip install aiohttp

echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "${BLUE}⚙️  Creating systemd service...${NC}"

# Stop and disable old service if exists
sudo systemctl stop autonomous-checker 2>/dev/null || true
sudo systemctl disable autonomous-checker 2>/dev/null || true

# Remove old service file if exists
sudo rm -f /etc/systemd/system/autonomous-checker.service

# Create new systemd service file
sudo tee /etc/systemd/system/credential-testing.service > /dev/null << 'EOF'
[Unit]
Description=Credential Testing System - MEGA Validator + Breach Detector
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-email-checker
Environment="PATH=/opt/ai-email-checker/.venv/bin"
ExecStart=/opt/ai-email-checker/.venv/bin/python start_credential_testing.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}🔄 Reloading systemd...${NC}"
sudo systemctl daemon-reload

echo -e "${BLUE}✅ Enabling credential-testing service...${NC}"
sudo systemctl enable credential-testing

echo -e "${GREEN}🚀 Starting credential-testing service...${NC}"
sudo systemctl start credential-testing

# Wait a moment for service to start
sleep 3
echo ""
echo "========================================"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "========================================"
echo ""

# Check service status
echo -e "${BLUE}📊 Service Status:${NC}"
sudo systemctl status credential-testing --no-pager -l

echo ""
echo -e "${BLUE}📋 Quick Commands:${NC}"
echo "   View logs:     sudo journalctl -u credential-testing -f"
echo "   Restart:       sudo systemctl restart credential-testing"
echo "   Stop:          sudo systemctl stop credential-testing"
echo "   Status:        sudo systemctl status credential-testing"
echo ""
echo -e "${BLUE}📱 Telegram Bot:${NC} @ai_email_checker_bot"
echo "   Commands: /start, /status, /help"
echo "   Upload combo file (.txt) to test credentials"
echo ""
echo -e "${BLUE}🎯 System Features:${NC}"
echo "   • MEGA account validator (100+ threads)"
echo "   • HaveIBeenPwned breach detection"
echo "   • Account info extraction (recovery keys, files, storage)"
echo "   • Risk scoring (0-100)"
echo "   • Real-time hit notifications"
echo ""

# Test if service is running
if systemctl is-active --quiet credential-testing; then
    echo -e "${GREEN}✅ Service is running successfully!${NC}"
else
    echo -e "${RED}⚠️  Service may not be running. Check logs:${NC}"
    echo "   sudo journalctl -u credential-testing -xe"
fi

echo ""
echo -e "${BLUE}📂 Upload combo files:${NC} /start → Upload .txt file"
echo -e "${BLUE}📊 Download results:${NC} /get_hits, /get_breaches, /get_report"
echo ""
