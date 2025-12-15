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

# Install mega.py with its dependencies
pip install mega.py pycryptodome

# Fix tenacity conflict (mega.py needs old version, langchain needs new)
# We'll force new version since it's backward compatible
pip install --force-reinstall "tenacity>=8.1.0,<10.0.0"

# Install aiohttp for breach detection
pip install aiohttp

echo -e "${BLUE}⚙️  Creating systemd service...${NC}"

# Create systemd service file
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
StandardOutput=append:/var/log/credential-testing.log
StandardError=append:/var/log/credential-testing-error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}🔄 Reloading systemd...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable credential-testing

echo -e "${BLUE}🛑 Stopping old autonomous-checker service...${NC}"
sudo systemctl stop autonomous-checker || true
sudo systemctl disable autonomous-checker || true

echo -e "${GREEN}✅ Starting credential-testing service...${NC}"
sudo systemctl restart credential-testing

echo ""
echo "========================================"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "========================================"
echo ""
echo "Service Status:"
sudo systemctl status credential-testing --no-pager -l

echo ""
echo "📊 To view logs:"
echo "   sudo journalctl -u credential-testing -f"
echo ""
echo "🔥 To restart:"
echo "   sudo systemctl restart credential-testing"
echo ""
echo "📱 Telegram Bot: @ai_email_checker_bot"
echo "   Send /start to begin"
echo "   Upload combo file (.txt) to test"
echo ""
echo "🎯 What's New:"
echo "   • MEGA account validator (100+ threads)"
echo "   • HaveIBeenPwned breach detection"
echo "   • Account info extraction (recovery keys, files, storage)"
echo "   • Risk scoring (0-100)"
echo "   • Real-time hit notifications"
echo "   • Download results: /get_hits, /get_breaches, /get_report"
echo ""
