#!/bin/bash
# AI Email Checker - Complete Deployment Script
# Run on DigitalOcean droplet: 143.110.254.40

set -e

echo "=================================="
echo "AI Email Checker Deployment"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="YOUR_GITHUB_USERNAME/ai-email-checker"
INSTALL_DIR="/opt/ai-checker"
DOMAIN=""  # Optional: yourdomain.com

# Functions
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Step 1: Update System
print_step "Updating system packages..."
apt update
DEBIAN_FRONTEND=noninteractive apt upgrade -y

# Step 2: Install Docker
print_step "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    print_step "Docker installed successfully"
else
    print_step "Docker already installed"
fi

# Step 3: Install Docker Compose
print_step "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_step "Docker Compose installed successfully"
else
    print_step "Docker Compose already installed"
fi

# Step 4: Install Git
print_step "Installing Git..."
apt install -y git

# Step 5: Install Python 3.11
print_step "Installing Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    apt install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt update
    apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    print_step "Python 3.11 installed successfully"
else
    print_step "Python 3.11 already installed"
fi

# Step 6: Install Node.js 20
print_step "Installing Node.js 20..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    print_step "Node.js installed successfully"
else
    print_step "Node.js already installed"
fi

# Step 7: Install nginx
print_step "Installing nginx..."
apt install -y nginx certbot python3-certbot-nginx

# Step 8: Install monitoring tools
print_step "Installing monitoring tools..."
apt install -y htop iotop nethogs ncdu fail2ban

# Step 9: Create swap
print_step "Creating 8GB swap..."
if [ ! -f /swapfile ]; then
    fallocate -l 8G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    print_step "Swap created successfully"
else
    print_step "Swap already exists"
fi

# Step 10: System optimization
print_step "Optimizing system settings..."
cat >> /etc/sysctl.conf << 'EOF'
# AI Email Checker Optimizations
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

# Step 11: Configure firewall
print_step "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp
ufw allow 8000/tcp
ufw --force enable

# Step 12: Clone repository
print_step "Cloning repository..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

if [ -d ".git" ]; then
    print_step "Repository already exists, pulling latest..."
    git pull origin main
else
    print_step "Cloning from GitHub..."
    read -p "Enter your GitHub username: " github_user
    git clone https://github.com/$github_user/ai-email-checker.git .
fi

# Step 13: Create directories
print_step "Creating required directories..."
mkdir -p $INSTALL_DIR/{uploads/{combos,configs,proxies},results/{hits,logs},logs,tools/osint}
chmod -R 755 $INSTALL_DIR

# Step 14: Setup .env file
print_step "Setting up environment variables..."

if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate random passwords
    DB_PASSWORD=$(openssl rand -hex 16)
    MONGO_PASSWORD=$(openssl rand -hex 16)
    API_SECRET=$(openssl rand -hex 32)
    
    # Update .env
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
    sed -i "s/MONGO_PASSWORD=.*/MONGO_PASSWORD=$MONGO_PASSWORD/" .env
    sed -i "s/API_SECRET_KEY=.*/API_SECRET_KEY=$API_SECRET/" .env
    
    print_step "Generated random passwords"
    
    # Telegram bot configuration
    echo ""
    print_warning "Telegram Bot Setup Required"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send: /newbot"
    echo "3. Follow instructions to create bot"
    echo "4. Copy the bot token"
    echo ""
    read -p "Enter Telegram Bot Token: " bot_token
    read -p "Enter Your Telegram User ID (from @userinfobot): " admin_id
    
    sed -i "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$bot_token/" .env
    sed -i "s/TELEGRAM_ADMIN_IDS=.*/TELEGRAM_ADMIN_IDS=$admin_id/" .env
    
    print_step ".env file configured"
else
    print_step ".env file already exists"
fi

# Step 15: Install Python dependencies
print_step "Installing Python dependencies..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install OSINT tools
print_step "Installing OSINT tools..."
pip install holehe h8mail sherlock-project ghunt

# Step 16: Install dashboard dependencies
print_step "Installing dashboard dependencies..."
cd dashboard/backend
npm install
cd ../..

# Step 17: Configure nginx
print_step "Configuring nginx..."
cat > /etc/nginx/sites-available/ai-checker << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 500M;

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    # Dashboard
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ai-checker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Step 18: Build and start Docker containers
print_step "Building and starting Docker containers..."
docker-compose up -d --build

# Wait for containers to be healthy
print_step "Waiting for containers to be healthy..."
sleep 30

# Step 19: Setup Telegram bot systemd service (alternative to Docker)
print_step "Setting up Telegram bot service..."
cat > /etc/systemd/system/telegram-bot.service << EOF
[Unit]
Description=AI Email Checker Telegram Bot
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/bin:/usr/local/bin"
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/python bot/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot

# Step 20: Install Watchtower for auto-updates
print_step "Installing Watchtower for auto-updates..."
docker run -d \
    --name watchtower \
    --restart always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    containrrr/watchtower \
    --cleanup \
    --interval 3600

# Step 21: Verification
print_step "Verifying deployment..."

echo ""
echo "Checking services..."
docker-compose ps

echo ""
echo "Checking Telegram bot..."
systemctl status telegram-bot --no-pager

echo ""
echo "Testing API..."
curl -s http://localhost:8000/api/health || echo "API not ready yet"

echo ""
echo "=================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================="
echo ""
echo "📍 Access Information:"
echo "  Dashboard: http://$(curl -s ifconfig.me):3000"
echo "  API: http://$(curl -s ifconfig.me):8000"
echo "  API Docs: http://$(curl -s ifconfig.me):8000/docs"
echo "  Telegram Bot: Search for your bot in Telegram"
echo ""
echo "🔐 Credentials:"
echo "  Database Password: $DB_PASSWORD"
echo "  MongoDB Password: $MONGO_PASSWORD"
echo "  API Secret: $API_SECRET"
echo "  (Saved in $INSTALL_DIR/.env)"
echo ""
echo "📊 Monitor Services:"
echo "  docker-compose ps"
echo "  docker-compose logs -f"
echo "  systemctl status telegram-bot"
echo ""
echo "🔄 Manage Services:"
echo "  docker-compose restart"
echo "  systemctl restart telegram-bot"
echo ""
echo "✅ Next Steps:"
echo "  1. Open Telegram and start your bot"
echo "  2. Send /start command"
echo "  3. Access dashboard at http://$(curl -s ifconfig.me):3000"
echo "  4. Upload combo lists and start checking!"
echo ""
echo "🔒 Security Recommendations:"
echo "  1. Setup SSL: certbot --nginx -d yourdomain.com"
echo "  2. Change default Grafana password"
echo "  3. Setup backups: see GITHUB_DEPLOYMENT.md"
echo "  4. Monitor logs regularly"
echo ""
