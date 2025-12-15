# GitHub Repository Setup & Deployment Guide

## 📋 Prerequisites

- GitHub account
- DigitalOcean droplet (143.110.254.40)
- SSH access to droplet
- Git installed locally

## 🚀 Step 1: Create GitHub Repository

### Option A: GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `ai-email-checker`
3. Description: `AI-Driven Email Leak Detection & Credential Checker with 30+ OSINT sources`
4. Choose: **Public** or **Private**
5. **DO NOT** initialize with README (we have one)
6. Click "Create repository"

### Option B: GitHub CLI

```bash
gh repo create ai-email-checker --public --description "AI Email Checker with 30+ sources"
```

## 📤 Step 2: Push Code to GitHub

### Initialize Git (if not already)

```powershell
cd d:\ai-email-checker

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI Email Checker with 30+ sources, Telegram bot, DigitalOcean deployment"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-email-checker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔐 Step 3: Configure Secrets

Create `.env.example` file (template for users):

```bash
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=CHANGE_THIS
DB_NAME=ai_checker

# MongoDB
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_USER=admin
MONGO_PASSWORD=CHANGE_THIS
MONGO_DB=ai_checker

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API Configuration
API_SECRET_KEY=CHANGE_THIS
API_HOST=0.0.0.0
API_PORT=8000

# Telegram Bot (GET FROM @BotFather)
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_ADMIN_IDS=YOUR_USER_ID_HERE

# Email Leak Checker API Keys (Optional)
HIBP_API_KEY=
INTELX_API_KEY=
GHOSTPROJECT_TOKEN=
SPYCLOUD_API_KEY=

# AI Optimizer
OPTIMIZER_ENABLED=true
OPTIMIZER_INTERVAL=60
MIN_WORKERS=1
MAX_WORKERS=20
TARGET_CPU=70
TARGET_MEMORY=80
```

## 🖥️ Step 4: Deploy to DigitalOcean Droplet

### Connect to Droplet

```bash
ssh root@143.110.254.40
```

### Install Prerequisites

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt install -y git

# Install Python 3.11
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install nginx
apt install -y nginx certbot python3-certbot-nginx
```

### Clone Repository

```bash
# Create app directory
mkdir -p /opt/ai-checker
cd /opt/ai-checker

# Clone from GitHub (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/ai-email-checker.git .

# Or if private repo, use SSH:
# git clone git@github.com:YOUR_USERNAME/ai-email-checker.git .
```

### Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Changes:**
1. Set `DB_PASSWORD` to strong password
2. Set `MONGO_PASSWORD` to strong password
3. Set `API_SECRET_KEY` to random string (use: `openssl rand -hex 32`)
4. Set `TELEGRAM_BOT_TOKEN` (from @BotFather)
5. Set `TELEGRAM_ADMIN_IDS` (your Telegram user ID)

### Create Required Directories

```bash
mkdir -p /opt/ai-checker/{uploads/{combos,configs,proxies},results/{hits,logs},logs,tools/osint}
chmod -R 755 /opt/ai-checker
```

### Install Python Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install OSINT tools
pip install holehe h8mail sherlock-project ghunt
```

### Install Dashboard Dependencies

```bash
cd dashboard/backend
npm install
cd ../..
```

### Start Services with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Configure Nginx (Optional - for SSL)

```bash
# Create nginx config
cat > /etc/nginx/sites-available/ai-checker << 'EOF'
server {
    listen 80;
    server_name 143.110.254.40;

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Dashboard
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/ai-checker /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Optional: Setup SSL with Let's Encrypt (requires domain name)
# certbot --nginx -d yourdomain.com
```

### Configure Firewall

```bash
# Allow necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 3000/tcp  # Dashboard
ufw allow 8000/tcp  # API
ufw --force enable
```

### Start Telegram Bot

```bash
# Run as systemd service
cat > /etc/systemd/system/telegram-bot.service << 'EOF'
[Unit]
Description=AI Email Checker Telegram Bot
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-checker
Environment="PATH=/opt/ai-checker/venv/bin:/usr/bin:/usr/local/bin"
EnvironmentFile=/opt/ai-checker/.env
ExecStart=/opt/ai-checker/venv/bin/python bot/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot
systemctl status telegram-bot
```

## ✅ Step 5: Verify Deployment

### Check All Services

```bash
# Docker containers
docker-compose ps

# Expected output:
# postgres      running
# mongodb       running
# redis         running
# api           running
# worker (x5)   running
# dashboard     running
# optimizer     running
# telegram-bot  running (if using Docker)

# Telegram bot (if systemd)
systemctl status telegram-bot

# Nginx
systemctl status nginx
```

### Test API

```bash
curl http://143.110.254.40:8000/api/health
# Expected: {"status": "healthy"}
```

### Test Dashboard

```bash
curl http://143.110.254.40:3000
# Expected: HTML response
```

### Test Telegram Bot

1. Open Telegram
2. Search for your bot (@ai_email_checker_bot)
3. Send `/start`
4. Should receive welcome message

## 🔄 Step 6: Setup Auto-Updates (Optional)

### Watchtower for Docker

```bash
docker run -d \
  --name watchtower \
  --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --cleanup \
  --interval 3600
```

### GitHub Webhook for Auto-Deploy

```bash
# Install webhook listener
apt install -y webhook

# Create deploy script
cat > /opt/ai-checker/deploy.sh << 'EOF'
#!/bin/bash
cd /opt/ai-checker
git pull origin main
docker-compose up -d --build
systemctl restart telegram-bot
EOF

chmod +x /opt/ai-checker/deploy.sh

# Configure webhook
cat > /etc/webhook.conf << 'EOF'
[
  {
    "id": "ai-checker-deploy",
    "execute-command": "/opt/ai-checker/deploy.sh",
    "command-working-directory": "/opt/ai-checker",
    "response-message": "Deploying AI Checker..."
  }
]
EOF

# Start webhook service
webhook -hooks /etc/webhook.conf -verbose -port 9000 &
```

Then in GitHub:
1. Go to repository Settings → Webhooks
2. Add webhook: `http://143.110.254.40:9000/hooks/ai-checker-deploy`
3. Content type: `application/json`
4. Events: `push`

## 📊 Step 7: Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker

# Telegram bot
journalctl -u telegram-bot -f

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### System Resources

```bash
# CPU, Memory, Disk
htop

# Docker stats
docker stats

# Disk usage
df -h

# Memory
free -h
```

## 🛠️ Troubleshooting

### Services Won't Start

```bash
# Check Docker logs
docker-compose logs

# Restart all
docker-compose down
docker-compose up -d

# Check permissions
chown -R root:root /opt/ai-checker
chmod -R 755 /opt/ai-checker
```

### Telegram Bot Not Responding

```bash
# Check status
systemctl status telegram-bot

# View logs
journalctl -u telegram-bot -n 50

# Restart
systemctl restart telegram-bot

# Test token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Out of Memory

```bash
# Create swap
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Reduce workers
docker-compose up -d --scale worker=3
```

### High CPU Usage

```bash
# Scale down workers
docker-compose up -d --scale worker=2

# Check AI optimizer
docker-compose logs optimizer
```

## 🔄 Update Deployment

### Pull Latest Changes

```bash
cd /opt/ai-checker
git pull origin main
docker-compose up -d --build
systemctl restart telegram-bot
```

### Rollback

```bash
git log --oneline  # Find commit hash
git checkout <commit-hash>
docker-compose up -d --build
systemctl restart telegram-bot
```

## 🎯 Quick Commands Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart api

# Scale workers
docker-compose up -d --scale worker=10

# View logs
docker-compose logs -f

# Update code
git pull && docker-compose up -d --build

# Backup database
docker exec postgres pg_dump -U postgres ai_checker > backup.sql

# Restore database
cat backup.sql | docker exec -i postgres psql -U postgres ai_checker
```

## 🌐 Access URLs

- **Dashboard**: http://143.110.254.40:3000
- **API**: http://143.110.254.40:8000
- **API Docs**: http://143.110.254.40:8000/docs
- **Telegram Bot**: @ai_email_checker_bot (search in Telegram)

## 🔐 Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set strong `API_SECRET_KEY`
- [ ] Configure firewall (UFW)
- [ ] Setup fail2ban: `apt install fail2ban`
- [ ] Disable root SSH: `PermitRootLogin no` in `/etc/ssh/sshd_config`
- [ ] Setup SSL certificate (if using domain)
- [ ] Regular backups
- [ ] Update system: `apt update && apt upgrade`

## 📈 Performance Tuning

### PostgreSQL

```bash
docker exec -it postgres bash
psql -U postgres

# Increase shared buffers
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
SELECT pg_reload_conf();
```

### Redis

```bash
docker exec -it redis redis-cli
CONFIG SET maxmemory 1gb
CONFIG SET maxmemory-policy allkeys-lru
CONFIG REWRITE
```

### Workers

```bash
# Scale based on CPU cores
docker-compose up -d --scale worker=$(nproc)
```

## 🆘 Support

If issues persist:
1. Check logs: `docker-compose logs`
2. Verify `.env` configuration
3. Test network connectivity
4. Check disk space: `df -h`
5. Review firewall rules: `ufw status`

---

**Deployment Status: 🟢 Ready**

Your IP: `143.110.254.40`
