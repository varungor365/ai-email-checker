# DigitalOcean Deployment Guide

Complete guide for deploying the AI-Driven Framework to DigitalOcean Droplets with remote access.

---

## 🖥️ Recommended Droplet Configurations

### Option 1: Budget-Friendly (Best for Testing)
```
Droplet Type: Basic
CPU: 2 vCPUs (Intel)
RAM: 4 GB
SSD: 80 GB
Transfer: 4 TB
Price: $24/month
Location: New York/San Francisco (closest to you)

✅ Good for: Testing, light workloads (1,000-5,000 checks/day)
✅ Can handle: 5-10 concurrent checkers
✅ Proxy workers: 2-3 workers
```

### Option 2: Performance (Best Value) ⭐ RECOMMENDED
```
Droplet Type: CPU-Optimized
CPU: 4 vCPUs (Dedicated)
RAM: 8 GB
SSD: 100 GB
Transfer: 5 TB
Price: $63/month
Location: New York/San Francisco

✅ Good for: Production workloads (10,000-50,000 checks/day)
✅ Can handle: 20-30 concurrent checkers
✅ Proxy workers: 5-10 workers
✅ AI optimization: Smooth ML operations
```

### Option 3: High-Performance (For Scale)
```
Droplet Type: CPU-Optimized
CPU: 8 vCPUs (Dedicated)
RAM: 16 GB
SSD: 200 GB
Transfer: 6 TB
Price: $126/month
Location: New York/San Francisco

✅ Good for: Heavy workloads (100,000+ checks/day)
✅ Can handle: 50+ concurrent checkers
✅ Proxy workers: 20+ workers
✅ AI optimization: Full ML with training
```

### Option 4: Enterprise (Maximum Power)
```
Droplet Type: CPU-Optimized
CPU: 16 vCPUs (Dedicated)
RAM: 32 GB
SSD: 400 GB
Transfer: 7 TB
Price: $252/month
Location: New York/San Francisco

✅ Good for: Massive scale (500,000+ checks/day)
✅ Can handle: 100+ concurrent checkers
✅ Proxy workers: 50+ workers
✅ AI optimization: Full ML with distributed training
```

---

## 🌍 Best Data Center Locations

### North America
- **New York 3** - Best for East Coast (fastest US connectivity)
- **San Francisco 3** - Best for West Coast
- **Toronto 1** - Best for Canada

### Europe
- **London 1** - Best for UK/Europe
- **Frankfurt 1** - Best for Central Europe
- **Amsterdam 3** - Best for Netherlands/EU

### Asia
- **Singapore 1** - Best for Southeast Asia
- **Bangalore 1** - Best for India

**Recommendation:** Choose the location **closest to your target services** for lowest latency.

---

## 📦 My Recommendation

**For smooth 24/7 operation with AI optimization:**

```
Droplet: CPU-Optimized 4 vCPU
RAM: 8 GB
Storage: 100 GB SSD
Price: $63/month
Location: New York 3 (or closest to you)

Why this configuration:
✅ Dedicated CPUs (no noisy neighbors)
✅ 8GB RAM (smooth AI/ML operations)
✅ 100GB SSD (fast I/O for databases)
✅ 5TB transfer (plenty for proxy traffic)
✅ Sweet spot for price/performance
```

**Estimated Performance:**
- **20,000-50,000 checks/day**
- **500-800 CPM** (checks per minute)
- **20-30 concurrent workers**
- **Smooth AI self-optimization**
- **99.9% uptime**

---

## 🚀 Automated Deployment Script

Run this on your **local machine** to deploy to DigitalOcean:

```powershell
# Save as: deploy-to-digitalocean.ps1

# DigitalOcean API Token (get from: https://cloud.digitalocean.com/account/api/tokens)
$DO_TOKEN = "your_digitalocean_api_token_here"

# Configuration
$DROPLET_NAME = "ai-checker-prod"
$DROPLET_SIZE = "c-4"  # CPU-Optimized 4 vCPU, 8GB RAM
$DROPLET_REGION = "nyc3"  # New York 3
$DROPLET_IMAGE = "ubuntu-22-04-x64"

Write-Host "🚀 Deploying to DigitalOcean..." -ForegroundColor Green

# Create Droplet
$headers = @{
    "Authorization" = "Bearer $DO_TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    name = $DROPLET_NAME
    region = $DROPLET_REGION
    size = $DROPLET_SIZE
    image = $DROPLET_IMAGE
    ssh_keys = @()
    backups = $true  # Enable automatic backups
    ipv6 = $true
    monitoring = $true  # Enable monitoring
    tags = @("ai-checker", "production")
    user_data = @"
#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt-get install -y git

# Install Python 3.11
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev

# Install Node.js (for web dashboard)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install nginx (reverse proxy for dashboard)
apt-get install -y nginx

# Install monitoring tools
apt-get install -y htop iotop nethogs

# Create swap (for AI optimization on 8GB RAM)
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Enable firewall
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP (dashboard)
ufw allow 443/tcp  # HTTPS (dashboard)
ufw allow 8000/tcp # API
ufw --force enable

# Create app directory
mkdir -p /opt/ai-checker
cd /opt/ai-checker

# Clone repository (you'll need to push your code to GitHub/GitLab first)
# git clone https://github.com/yourusername/ai-email-checker.git .

echo "✅ System setup complete!" > /root/setup-complete.txt
"@
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/droplets" -Method Post -Headers $headers -Body $body

$dropletId = $response.droplet.id
Write-Host "✅ Droplet created with ID: $dropletId" -ForegroundColor Green

# Wait for droplet to be active
Write-Host "⏳ Waiting for droplet to be active..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Get droplet IP
$droplet = Invoke-RestMethod -Uri "https://api.digitalocean.com/v2/droplets/$dropletId" -Headers $headers
$ipAddress = $droplet.droplet.networks.v4 | Where-Object { $_.type -eq "public" } | Select-Object -ExpandProperty ip_address

Write-Host "✅ Droplet IP Address: $ipAddress" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. SSH into your droplet: ssh root@$ipAddress"
Write-Host "2. Upload your code or clone from Git"
Write-Host "3. Run: docker-compose up -d"
Write-Host "4. Access dashboard at: http://$ipAddress"
Write-Host ""
Write-Host "🔐 Save this IP address: $ipAddress" -ForegroundColor Yellow
```

---

## 🎯 Quick Deployment Steps

### Step 1: Create Droplet via DigitalOcean Dashboard

1. Go to: https://cloud.digitalocean.com/droplets/new
2. Choose **CPU-Optimized** → **4 vCPU, 8GB RAM** ($63/month)
3. Select **Ubuntu 22.04 LTS**
4. Choose **New York 3** (or closest region)
5. Enable **Backups** ($6.30/month extra - RECOMMENDED)
6. Enable **Monitoring** (FREE)
7. Add **SSH Key** (or use password)
8. Click **Create Droplet**

### Step 2: Connect to Droplet

```powershell
# Get your droplet IP from DigitalOcean dashboard
$IP = "your.droplet.ip.address"

# SSH into droplet
ssh root@$IP
```

### Step 3: Install Everything

```bash
# Run this on your droplet
curl -fsSL https://raw.githubusercontent.com/yourusername/ai-email-checker/main/setup-digitalocean.sh | bash
```

---

## 📁 File Transfer to Droplet

### Option 1: SCP (Secure Copy)

```powershell
# From your local machine
scp -r d:\ai-email-checker root@your.droplet.ip:/opt/ai-checker
```

### Option 2: Git (Recommended)

```bash
# On droplet
cd /opt/ai-checker
git clone https://github.com/yourusername/ai-email-checker.git .
```

### Option 3: SFTP (GUI)

Use **WinSCP** or **FileZilla**:
- Host: your.droplet.ip
- Port: 22
- Username: root
- Password/Key: your credentials

---

## ⚙️ Droplet Setup Script

Save as `setup-digitalocean.sh` and upload to your droplet:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up AI-Driven Framework on DigitalOcean..."

# Update system
echo "📦 Updating system..."
apt-get update
apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

# Install Docker Compose
echo "🐙 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install Node.js (for dashboard)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install nginx
echo "🌐 Installing Nginx..."
apt-get install -y nginx certbot python3-certbot-nginx

# Install monitoring tools
echo "📊 Installing monitoring tools..."
apt-get install -y htop iotop nethogs ncdu

# Create swap for AI optimization
echo "💾 Creating 8GB swap..."
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Optimize system for production
echo "⚡ Optimizing system..."
cat >> /etc/sysctl.conf << EOF
# Network optimization
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15

# File handles
fs.file-max = 2097152

# Memory
vm.swappiness = 10
vm.dirty_ratio = 60
vm.dirty_background_ratio = 2
EOF

sysctl -p

# Set file limits
cat >> /etc/security/limits.conf << EOF
* soft nofile 1000000
* hard nofile 1000000
* soft nproc 1000000
* hard nproc 1000000
EOF

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 8000/tcp # API
ufw allow 3000/tcp # Dashboard
ufw --force enable

# Create app directory
echo "📁 Creating app directory..."
mkdir -p /opt/ai-checker
cd /opt/ai-checker

# Install Docker monitoring
echo "📊 Installing Docker monitoring..."
docker run -d \
  --name=watchtower \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --cleanup \
  --interval 3600

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Upload your code to /opt/ai-checker"
echo "2. Copy .env.example to .env and configure"
echo "3. Run: docker-compose up -d"
echo "4. Access dashboard at: http://$(curl -s ifconfig.me)"
```

---

## 🔒 Security Hardening

### SSL Certificate (Free with Let's Encrypt)

```bash
# On your droplet
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured)
certbot renew --dry-run
```

### SSH Key Authentication (Disable Password)

```bash
# On droplet
nano /etc/ssh/sshd_config

# Change these lines:
PasswordAuthentication no
PermitRootLogin prohibit-password

# Restart SSH
systemctl restart sshd
```

### Fail2Ban (Prevent Brute Force)

```bash
apt-get install -y fail2ban

cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
```

---

## 📊 Monitoring Setup

### Option 1: Built-in Monitoring (DigitalOcean)

DigitalOcean provides **FREE monitoring**:
- CPU usage
- Memory usage
- Disk usage
- Network I/O

Access at: https://cloud.digitalocean.com/droplets/[your-droplet-id]/graphs

### Option 2: Advanced Monitoring (Grafana + Prometheus)

Already included in `docker-compose.yml`:

```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  volumes:
    - grafana_data:/var/lib/grafana

prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

Access:
- Grafana: http://your-ip:3001 (admin/admin)
- Prometheus: http://your-ip:9090

---

## 🎨 Interactive Dashboard Access

### Access Methods:

1. **Direct IP Access**
   ```
   http://your.droplet.ip:3000
   ```

2. **Domain Name** (Recommended)
   - Point your domain to droplet IP
   - Access: https://yourdomain.com

3. **SSH Tunnel** (Secure)
   ```powershell
   ssh -L 3000:localhost:3000 root@your.droplet.ip
   # Then access: http://localhost:3000
   ```

4. **VPN** (Most Secure)
   - Install WireGuard on droplet
   - Connect via VPN
   - Access internal network

---

## 💾 Backup Strategy

### Automated Backups (DigitalOcean)

Enable in droplet settings: **$6.30/month**
- Daily backups
- 4 backup snapshots retained
- One-click restore

### Manual Backup Script

```bash
#!/bin/bash
# Save as: /opt/backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Backup databases
docker exec postgres pg_dumpall -U postgres > $BACKUP_DIR/postgres-$DATE.sql
docker exec mongo mongodump --out $BACKUP_DIR/mongo-$DATE

# Backup config and data
tar -czf $BACKUP_DIR/ai-checker-$DATE.tar.gz /opt/ai-checker

# Upload to S3/DigitalOcean Spaces (optional)
# s3cmd put $BACKUP_DIR/* s3://your-bucket/

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
# Backup daily at 2 AM
0 2 * * * /opt/backup.sh >> /var/log/backup.log 2>&1
```

---

## 🔄 Auto-Recovery and Self-Healing

### Docker Auto-Restart

```yaml
# In docker-compose.yml (already configured)
services:
  api:
    restart: unless-stopped  # Auto-restart on failure
    
  postgres:
    restart: unless-stopped
```

### Health Checks

```yaml
# Health check example (already in docker-compose.yml)
api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### Watchtower (Auto-Update)

Automatically updates Docker containers:
```bash
docker run -d \
  --name watchtower \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --cleanup \
  --interval 3600
```

---

## 📈 Scaling Options

### Vertical Scaling (Resize Droplet)

1. Go to DigitalOcean Dashboard
2. Droplet → Resize
3. Choose larger size
4. Power off → Resize → Power on

**No data loss, 5-10 minutes downtime**

### Horizontal Scaling (Multiple Droplets)

```
Load Balancer ($10/month)
    ↓
Worker 1 (8GB) - Checker tasks
Worker 2 (8GB) - Checker tasks  
Worker 3 (8GB) - Checker tasks
    ↓
Database Droplet (16GB)
```

---

## 💰 Cost Breakdown

### Recommended Setup ($63/month base)

| Component | Cost/Month |
|-----------|-----------|
| CPU-Optimized Droplet (4 vCPU, 8GB) | $63.00 |
| Backups (10% of droplet) | $6.30 |
| 100GB Block Storage (optional) | $10.00 |
| **TOTAL** | **$79.30** |

### With Load Balancer (for scale)

| Component | Cost/Month |
|-----------|-----------|
| 3x Worker Droplets (4 vCPU each) | $189.00 |
| 1x Database Droplet (8 vCPU, 16GB) | $126.00 |
| Load Balancer | $10.00 |
| Backups | $31.50 |
| **TOTAL** | **$356.50** |

---

## 🚀 Quick Start Commands

```bash
# On your local machine - Deploy code
scp -r d:\ai-email-checker root@your.droplet.ip:/opt/

# On droplet - Start services
cd /opt/ai-email-checker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Access dashboard
# Open browser: http://your.droplet.ip:3000
```

---

## 📱 Remote Management

### SSH from Anywhere

```powershell
# From Windows
ssh root@your.droplet.ip

# From Android (Termux app)
ssh root@your.droplet.ip

# From iPhone (Blink Shell app)
ssh root@your.droplet.ip
```

### Web-Based SSH

Use **DigitalOcean Console**:
1. Go to your droplet
2. Click "Access" → "Launch Droplet Console"
3. Browser-based terminal

---

## 🎯 Performance Tuning

### For 8GB RAM Droplet

```bash
# Optimize PostgreSQL
echo "shared_buffers = 2GB" >> /var/lib/postgresql/data/postgresql.conf
echo "effective_cache_size = 6GB" >> /var/lib/postgresql/data/postgresql.conf
echo "work_mem = 32MB" >> /var/lib/postgresql/data/postgresql.conf

# Optimize Redis
echo "maxmemory 1gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf

# Restart services
docker-compose restart postgres redis
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Droplet is running: `ssh root@your.droplet.ip`
- [ ] Docker installed: `docker --version`
- [ ] Services running: `docker-compose ps`
- [ ] API accessible: `curl http://localhost:8000/health`
- [ ] Dashboard accessible: `http://your.droplet.ip:3000`
- [ ] Database connected: `docker exec postgres psql -U postgres -c '\l'`
- [ ] Firewall configured: `ufw status`
- [ ] Backups enabled: Check DigitalOcean dashboard
- [ ] Monitoring active: Check graphs in dashboard

---

**Next:** See `REMOTE_DASHBOARD.md` for interactive dashboard setup!
