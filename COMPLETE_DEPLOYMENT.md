# 🚀 COMPLETE DEPLOYMENT GUIDE - AI Email Checker with Local AI

## Droplet: 143.110.254.40
## Telegram Bot: @hackingmasterr (ID: 796354588)
## Bot Token: 8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M

---

## 📋 Prerequisites

- DigitalOcean Droplet (Ubuntu 22.04 LTS)
- 8GB RAM minimum (for AI model)
- 50GB disk space
- Root SSH access
- Domain (optional, for SSL)

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Connect to Droplet

```bash
ssh root@143.110.254.40
```

### Step 2: Clone Repository

```bash
# Install git if needed
apt-get update && apt-get install -y git

# Clone your repository
git clone https://github.com/YOUR_USERNAME/ai-email-checker.git
cd ai-email-checker
```

### Step 3: Run Deployment Script

```bash
chmod +x deploy_droplet.sh
./deploy_droplet.sh
```

The script will:
- Install Docker & Docker Compose
- Install Python 3.11 & Node.js 20
- Create 8GB swap file
- Configure firewall (ports 22, 80, 443, 3000, 8000)
- Set up nginx reverse proxy
- Install dependencies
- Start all services
- Initialize AI model

**Estimated time: 8-10 minutes**

### Step 4: Verify Services

```bash
docker-compose ps
```

You should see:
- ✅ postgres (healthy)
- ✅ mongodb (healthy)
- ✅ redis (healthy)
- ✅ ollama (healthy) **← AI model**
- ✅ api (running)
- ✅ brain (running)
- ✅ worker-1 (running)
- ✅ worker-2 (running)
- ✅ telegram-bot (running) **← Your bot**
- ✅ prometheus (running)
- ✅ grafana (running)

### Step 5: Initialize AI Model

```bash
# Download Mistral model (one-time, ~4GB)
chmod +x scripts/init_ollama.sh
./scripts/init_ollama.sh
```

This will:
- Download Mistral 7B model
- Configure for local inference
- Test AI capabilities

**Estimated time: 5-10 minutes** (depends on internet speed)

### Step 6: Test Telegram Bot

Open Telegram and search for **@hackingmasterr**

```
/start
```

You should receive:
```
🤖 AI Email Checker Bot

Welcome Hanker!

This bot gives you complete control over the AI Email Checker system.

🔍 Features:
• Email leak detection (30+ sources)
• AI-powered combo sorting
• Bulk scanning
• Real-time results
• System monitoring
• Worker scaling
• File management
```

---

## 🔧 Manual Deployment (Step-by-Step)

### 1. System Setup

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Python 3.11
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install dependencies
apt-get install -y build-essential curl wget git nginx
```

### 2. Configure Environment

```bash
# Create .env file (already exists in your project)
cat > .env << 'EOF'
# Database
POSTGRES_PASSWORD=your_secure_password_here
MONGO_INITDB_ROOT_PASSWORD=your_mongo_password_here
REDIS_PASSWORD=your_redis_password_here

# API Keys
HIBP_API_KEY=your_hibp_key_here
EMAILREP_KEY=your_emailrep_key_here
INTELX_KEY=your_intelx_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588

# Ollama (Local AI)
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral
AI_ENABLED=true
AI_AUTO_SORT=true
AI_COMBO_ANALYSIS=true

# System
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

# Secure .env file
chmod 600 .env
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Configure Firewall

```bash
# Enable UFW
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 3000/tcp  # Grafana
ufw allow 8000/tcp  # API
ufw --force enable

# Check status
ufw status
```

### 5. Configure Nginx (Optional - for domain)

```bash
# Create nginx config
cat > /etc/nginx/sites-available/ai-checker << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    # Dashboard
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/ai-checker /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 6. SSL Certificate (Optional)

```bash
# Install certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d YOUR_DOMAIN.com
```

---

## 🤖 AI Model Setup

### Initialize Ollama

The deployment script automatically runs this, but you can manually initialize:

```bash
# Wait for Ollama service to be ready
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Waiting for Ollama..."
    sleep 5
done

# Pull Mistral model (recommended)
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "mistral"}'

# Pull Llama 2 (alternative)
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "llama2"}'

# Check available models
curl http://localhost:11434/api/tags
```

### Test AI Model

```bash
# Test generation
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "Analyze this password: MyPassword123. Is it secure?",
    "stream": false
  }'
```

Expected response:
```json
{
  "response": "This password is WEAK because it uses a common word pattern with simple number substitution. It lacks special characters and is vulnerable to dictionary attacks. Recommendation: Use a longer passphrase with random words.",
  "done": true
}
```

---

## 📱 Telegram Bot Usage

### Basic Commands

#### Start Bot
```
/start
```

#### Scan Email
```
/scan user@example.com
```

Response:
```
🔍 Scan Results

📧 Email: user@example.com
🎯 Risk Score: 85/100 (HIGH)
🔍 Sources Checked: 30
⚠️ Leaks Found: 12
🗃️ Breaches: 8

Top Breaches:
• LinkedIn (2012)
• Adobe (2013)
• MyFitnessPal (2018)
```

#### AI Combo Analysis
```
/analyze user@gmail.com:MyPass123
```

Response:
```
📊 Combo Analysis

📧 Email: user@gmail.com
🔐 Password: ***********

Password Strength:
Score: 45/100
Level: WEAK
Length: 9 chars
Upper: ✅
Lower: ✅
Digits: ✅
Special: ❌

Security Assessment:
Breach Risk: 70%
Quality Score: 42.5/100
Quality Level: MEDIUM

Recommendations:
• ⚠️ Password is weak - consider changing it
• 🚨 High breach risk detected
• Add special characters to password
• Use a longer password (12+ characters)
• 💡 AI Insight: This password appears in common wordlists. Use a passphrase instead.
```

#### Sort Combos with AI
```
/sort
```

Then upload `combos.txt` file:
```
user1@gmail.com:password123
user2@yahoo.com:SecureP@ss123!
user3@hotmail.com:12345
...
```

Response:
```
✅ AI Sorting Complete!

📊 Results:
Premium: 450 combos (9.0%)
High Quality: 1,800 combos (36.0%)
Medium Quality: 2,100 combos (42.0%)
Low Quality: 650 combos (13.0%)

📁 Files saved to: results/sorted/796354588

Use /download to get your sorted files!
```

#### Validate Combos
```
/validate
```

Upload file, get:
```
✅ Validation Complete!

📊 Results:
Original: 10,000 combos
Valid: 8,500 combos
Duplicates Removed: 1,200
Final Count: 7,300

📈 Statistics:
Unique Domains: 350
Top Domain: gmail.com (1,200 emails)
Avg Password Length: 10.5 chars

📁 Cleaned file: results/validated/796354588/cleaned.txt

Use /download to get your cleaned file!
```

#### System Stats
```
/stats
```

Response:
```
📊 System Statistics

⏱️ Uptime: 2 days, 5 hours
🔄 Active Workers: 2
📧 Emails Scanned: 15,247
⚡ Scan Speed: 125 emails/min
💾 Cache Hit Rate: 85%

🔥 AI Model:
Model: mistral
Status: ✅ Online
Requests: 1,234
Avg Response: 2.5s

📈 Last 24h:
Scans: 3,450
API Calls: 12,680
Cache Hits: 10,778
```

#### Scale Workers
```
/workers 5
```

Response:
```
✅ Successfully scaled to 5 workers

Active workers will be adjusted for optimal performance.
```

---

## 🌐 Web Dashboard

### Access

```
http://143.110.254.40:3000
```

Or with domain:
```
https://your-domain.com
```

### Default Credentials

**Grafana:**
- Username: `admin`
- Password: Set in `.env` as `GRAFANA_PASSWORD` (default: `admin`)

### Features

- 📊 Real-time metrics
- 📈 Performance graphs
- 🔍 Email scan history
- 💾 Database statistics
- 🤖 AI model performance
- ⚙️ Worker status
- 📁 Result downloads

---

## 🔌 API Endpoints

### Email Leak Detection

```bash
# Scan single email
curl -X POST http://143.110.254.40:8001/api/leak-check/scan \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Bulk scan
curl -X POST http://143.110.254.40:8001/api/leak-check/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["user1@example.com", "user2@example.com"],
    "max_concurrent": 5
  }'
```

### ComboUtils AI Features

```bash
# Extract combos
curl -X POST http://143.110.254.40:8001/api/combo/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "user1@gmail.com:pass123\nuser2@yahoo.com:secret456"
  }'

# AI analysis
curl -X POST http://143.110.254.40:8001/api/combo/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "MyPassword123"
  }'

# AI sorting
curl -X POST http://143.110.254.40:8001/api/combo/sort \
  -F "file=@combos.txt"

# Validate
curl -X POST http://143.110.254.40:8001/api/combo/validate \
  -F "file=@combos.txt"
```

---

## 🎛️ System Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f telegram-bot
docker-compose logs -f ollama
docker-compose logs -f api
docker-compose logs -f worker-1

# Last 100 lines
docker-compose logs --tail=100 telegram-bot
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart telegram-bot
docker-compose restart ollama
docker-compose restart api

# Rebuild and restart
docker-compose up -d --build
```

### Scale Workers

```bash
# Scale to 5 workers
docker-compose up -d --scale worker-1=5

# Or use API
curl -X POST http://localhost:8001/api/workers/scale \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'
```

### Monitor Resources

```bash
# System resources
htop

# Docker stats
docker stats

# Disk usage
df -h
docker system df
```

### Backup Data

```bash
# Backup PostgreSQL
docker exec ai-checker-postgres pg_dump -U postgres ai_email_checker > backup.sql

# Backup MongoDB
docker exec ai-checker-mongo mongodump --out /backup

# Backup volumes
docker run --rm -v ai-email-checker_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

---

## 🔍 Troubleshooting

### Bot Not Responding

```bash
# Check bot logs
docker-compose logs telegram-bot

# Restart bot
docker-compose restart telegram-bot

# Check if token is correct
grep TELEGRAM_BOT_TOKEN .env
```

### AI Model Not Working

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama

# Re-download model
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "mistral"}'

# Check model files
docker exec -it ai-checker-ollama ls -lh /root/.ollama/models
```

### High Memory Usage

```bash
# Check memory
free -h

# Reduce workers
docker-compose up -d --scale worker-1=1

# Use smaller AI model
# Edit .env: OLLAMA_MODEL=mistral  (instead of llama2-13b)
docker-compose restart ollama api telegram-bot
```

### Slow AI Analysis

```bash
# Option 1: Reduce concurrent limit
# Edit bot/telegram_bot.py:
# max_concurrent=50  →  max_concurrent=25

# Option 2: Use faster model
# Edit .env:
# OLLAMA_MODEL=mistral  (faster than llama2)

# Restart
docker-compose restart telegram-bot
```

### Service Won't Start

```bash
# Check port conflicts
netstat -tulpn | grep -E ':(5432|27017|6379|11434|8001|3000)'

# Check logs
docker-compose logs <service-name>

# Remove and recreate
docker-compose down
docker-compose up -d
```

---

## 📊 Performance Optimization

### Increase Worker Count

```bash
# Edit docker-compose.yml to add more workers
# Or scale existing:
docker-compose up -d --scale worker-1=10
```

### Redis Cache Tuning

```bash
# Increase cache TTL
# Edit core/checkers/email_leak_checker.py:
# self.cache_ttl = 3600  →  self.cache_ttl = 7200  (2 hours)
```

### Database Optimization

```bash
# PostgreSQL: Increase shared_buffers
docker exec -it ai-checker-postgres psql -U postgres -c "ALTER SYSTEM SET shared_buffers = '2GB';"
docker-compose restart postgres

# MongoDB: Enable compression
docker exec -it ai-checker-mongo mongosh --eval "db.adminCommand({setParameter: 1, internalQueryExecYieldIterations: 128})"
```

### AI Model Optimization

```bash
# Use 4-bit quantized model (faster, less memory)
# Edit .env:
OLLAMA_MODEL=mistral:7b-instruct-q4_0

# Or use Llama 2 7B instead of 13B
OLLAMA_MODEL=llama2:7b
```

---

## 🔒 Security Hardening

### Change Default Passwords

```bash
# Edit .env and change:
POSTGRES_PASSWORD=your_new_secure_password
MONGO_INITDB_ROOT_PASSWORD=your_new_mongo_password
GRAFANA_PASSWORD=your_new_grafana_password

# Restart services
docker-compose down
docker-compose up -d
```

### Enable SSL

```bash
# Install certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
certbot renew --dry-run
```

### Restrict API Access

```bash
# Edit nginx config to add IP whitelist
# /etc/nginx/sites-available/ai-checker

location /api {
    allow YOUR_IP;
    deny all;
    proxy_pass http://localhost:8001;
}

# Reload nginx
nginx -t && systemctl reload nginx
```

### Enable Fail2Ban

```bash
# Install fail2ban
apt-get install -y fail2ban

# Configure
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

# Start
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 📈 Monitoring & Alerts

### Prometheus Metrics

```
http://143.110.254.40:9090
```

### Grafana Dashboards

```
http://143.110.254.40:3000
```

### Set Up Alerts

```bash
# Edit monitoring/prometheus.yml to add alerting rules
# Edit monitoring/grafana/dashboards/alerts.json to configure notifications
```

### Telegram Notifications

Bot automatically sends notifications for:
- ✅ Scan completion
- ❌ System errors
- ⚠️ High resource usage
- 🔄 Worker scaling events

---

## 🚀 Next Steps

1. **Test Everything**
   ```bash
   # Test Telegram bot
   # Send /start to @hackingmasterr
   
   # Test API
   curl http://143.110.254.40:8001/api/health
   
   # Test AI
   curl -X POST http://localhost:11434/api/generate \
     -d '{"model": "mistral", "prompt": "Test", "stream": false}'
   ```

2. **Upload Test Combo File**
   - Send `/sort` to bot
   - Upload `combos.txt` file
   - Download sorted results

3. **Configure API Keys**
   - Get HIBP API key: https://haveibeenpwned.com/API/Key
   - Get EmailRep key: https://emailrep.io
   - Get IntelX key: https://intelx.io
   - Add to `.env` and restart

4. **Set Up Monitoring**
   - Access Grafana at http://143.110.254.40:3000
   - Configure dashboards
   - Set up alerts

5. **Scale for Production**
   ```bash
   # Increase workers
   docker-compose up -d --scale worker-1=10
   
   # Enable auto-scaling
   # Edit config/worker_config.yaml
   ```

---

## 📞 Support

### Telegram Bot Commands

```
/help - Show all commands
/system - System control
/stats - View statistics
/logs - View live logs
```

### Check System Health

```bash
# Run health check
curl http://143.110.254.40:8001/api/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "postgres": "up",
    "mongodb": "up",
    "redis": "up",
    "ollama": "up"
  },
  "ai_model": "mistral",
  "workers": 2
}
```

---

## 🎉 You're All Set!

Your AI Email Checker system is now running with:

✅ **30+ Email Leak Detection Sources**
✅ **Local AI Model (Mistral 7B)** - No external APIs needed!
✅ **ComboUtils Integration** - Smart sorting & validation
✅ **Telegram Bot Control** - @hackingmasterr
✅ **Web Dashboard** - Real-time monitoring
✅ **Auto-Scaling Workers**
✅ **Prometheus + Grafana** - Metrics & alerts

**Bot Info:**
- Bot: @hackingmasterr
- Admin ID: 796354588
- Token: 8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M

**Droplet:**
- IP: 143.110.254.40
- Dashboard: http://143.110.254.40:3000
- API: http://143.110.254.40:8001

**Test it now:**
1. Open Telegram
2. Search @hackingmasterr
3. Send: `/start`
4. Try: `/analyze test@gmail.com:password123`

🚀 **Happy Hacking!**
