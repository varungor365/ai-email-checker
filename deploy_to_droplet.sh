#!/bin/bash
# Deploy Autonomous Email Checker to DigitalOcean Droplet
# Droplet IP: 143.110.254.40

set -e

echo "============================================================"
echo "  AUTONOMOUS EMAIL CHECKER - DROPLET DEPLOYMENT"
echo "============================================================"
echo ""

# Configuration
DROPLET_IP="143.110.254.40"
DROPLET_USER="root"
APP_DIR="/opt/ai-email-checker"

echo "Droplet IP: $DROPLET_IP"
echo "App Directory: $APP_DIR"
echo ""

# Step 1: Prepare droplet
echo "[1/8] Preparing droplet environment..."
ssh $DROPLET_USER@$DROPLET_IP << 'ENDSSH'
    # Update system
    apt-get update
    apt-get upgrade -y
    
    # Install dependencies
    apt-get install -y \
        docker.io \
        docker-compose \
        git \
        curl \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        certbot \
        python3-certbot-nginx \
        ufw
    
    # Start Docker
    systemctl start docker
    systemctl enable docker
    
    # Configure firewall
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 8000/tcp
    ufw --force enable
    
    echo "✅ Droplet prepared"
ENDSSH

# Step 2: Create app directory
echo ""
echo "[2/8] Creating application directory..."
ssh $DROPLET_USER@$DROPLET_IP << ENDSSH
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # Create directory structure
    mkdir -p {core,bot,api,workers,models,training_data,results,logs}
    mkdir -p core/{ai,validation,notifications,optimization,training,utils,checkers}
    
    echo "✅ Directory structure created"
ENDSSH

# Step 3: Copy files to droplet
echo ""
echo "[3/8] Copying files to droplet..."
rsync -avz --progress \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'models/*' \
    --exclude 'training_data/*' \
    --exclude 'results/*' \
    ./ $DROPLET_USER@$DROPLET_IP:$APP_DIR/

echo "✅ Files copied"

# Step 4: Set up environment
echo ""
echo "[4/8] Setting up environment..."
ssh $DROPLET_USER@$DROPLET_IP << 'ENDSSH'
    cd /opt/ai-email-checker
    
    # Copy .env file
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
    
    # Make scripts executable
    chmod +x *.sh
    
    echo "✅ Environment configured"
ENDSSH

# Step 5: Install Docker Compose services
echo ""
echo "[5/8] Starting Docker services..."
ssh $DROPLET_USER@$DROPLET_IP << 'ENDSSH'
    cd /opt/ai-email-checker
    
    # Pull images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 30
    
    # Check status
    docker-compose ps
    
    echo "✅ Docker services started"
ENDSSH

# Step 6: Install Python dependencies
echo ""
echo "[6/8] Installing Python dependencies..."
ssh $DROPLET_USER@$DROPLET_IP << 'ENDSSH'
    cd /opt/ai-email-checker
    
    # Create virtual environment
    python3 -m venv .venv
    
    # Install dependencies
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
    
    echo "✅ Python dependencies installed"
ENDSSH

# Step 7: Set up systemd service
echo ""
echo "[7/8] Setting up systemd service..."
ssh $DROPLET_USER@$DROPLET_IP << 'ENDSSH'
    # Create systemd service file
    cat > /etc/systemd/system/autonomous-checker.service << 'EOF'
[Unit]
Description=Autonomous Email Checker System
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-email-checker
Environment="PATH=/opt/ai-email-checker/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/ai-email-checker/.venv/bin/python start_autonomous.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable and start service
    systemctl enable autonomous-checker
    systemctl start autonomous-checker
    
    # Check status
    systemctl status autonomous-checker --no-pager
    
    echo "✅ Systemd service configured"
ENDSSH

# Step 8: Configure Nginx reverse proxy
echo ""
echo "[8/8] Configuring Nginx..."
ssh $DROPLET_USER@$DROPLET_IP << 'ENDSSH'
    # Create Nginx config
    cat > /etc/nginx/sites-available/autonomous-checker << 'EOF'
server {
    listen 80;
    server_name 143.110.254.40;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/autonomous-checker /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx config
    nginx -t
    
    # Restart Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    echo "✅ Nginx configured"
ENDSSH

echo ""
echo "============================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Your autonomous system is now running on:"
echo "  IP: http://143.110.254.40"
echo "  API: http://143.110.254.40:8000"
echo ""
echo "Telegram Bot Commands:"
echo "  /auto_scan - Upload combo file and start scan"
echo "  /ml_status - Check ML metrics"
echo "  /quality_report - Validation statistics"
echo ""
echo "Check system status:"
echo "  ssh root@143.110.254.40 'systemctl status autonomous-checker'"
echo ""
echo "View logs:"
echo "  ssh root@143.110.254.40 'journalctl -u autonomous-checker -f'"
echo ""
