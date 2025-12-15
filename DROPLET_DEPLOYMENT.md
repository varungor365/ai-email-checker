# 🚀 Droplet Deployment Guide

## Your DigitalOcean Droplet

**IP:** `143.110.254.40`  
**User:** `root`  
**Status:** Ready for deployment ✅

---

## Quick Deploy (One Command)

### Option 1: Automated Script (Recommended)

```bash
# On your local machine (Windows PowerShell)
bash deploy_to_droplet.sh
```

This will:
1. ✅ Prepare droplet environment
2. ✅ Install Docker & dependencies
3. ✅ Copy all files to droplet
4. ✅ Start Docker services
5. ✅ Install Python dependencies
6. ✅ Set up systemd service
7. ✅ Configure Nginx reverse proxy
8. ✅ Start autonomous system

---

### Option 2: Manual Deployment

If you prefer manual control:

```bash
# 1. SSH into droplet
ssh root@143.110.254.40

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Install Docker Compose
apt-get install -y docker-compose

# 4. Install Python
apt-get install -y python3 python3-pip python3-venv git

# 5. Clone or copy your code
mkdir -p /opt/ai-email-checker
cd /opt/ai-email-checker

# 6. Copy files (from local machine)
# Run this on your Windows machine:
scp -r d:/ai-email-checker/* root@143.110.254.40:/opt/ai-email-checker/

# 7. Back on droplet, set up environment
cd /opt/ai-email-checker
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 8. Configure .env
nano .env
# Add your Telegram bot token and admin ID

# 9. Start Docker services
docker-compose up -d

# 10. Start autonomous system
.venv/bin/python start_autonomous.py
```

---

## 🔧 Configure Telegram Bot

### 1. Update .env on Droplet

```bash
ssh root@143.110.254.40

cat > /opt/ai-email-checker/.env << 'EOF'
# Telegram Bot
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588

# Ollama (Local AI)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# Autonomous System
MIN_CONFIDENCE=0.75
INITIAL_WORKERS=2
TARGET_SPEED=100.0
PROGRESS_UPDATE_INTERVAL=60

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_checker
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password_here

MONGODB_HOST=localhost
MONGODB_PORT=27017

REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

### 2. Restart Services

```bash
systemctl restart autonomous-checker
systemctl status autonomous-checker
```

---

## 📱 Using Telegram Bot

### Access Your Bot

Open Telegram → Search: `@hackingmasterr`

### Upload Files (Auto-Detection)

The bot **automatically detects** file types:

**1. Upload Combo List:**
```
user1@gmail.com:password123
user2@yahoo.com:SecurePass!
```
→ Bot detects: "Combo List" → Offers `/auto_scan`

**2. Upload OpenBullet Config:**
```
[SETTINGS]
[REQUEST]
[KEYCHECK]
```
→ Bot detects: "Config" → Auto-loads for scanning

**3. Upload Proxy List:**
```
192.168.1.1:8080
10.0.0.1:3128
```
→ Bot detects: "Proxy List" → Auto-configures

**4. Upload Wordlist:**
```
password123
qwerty
SecurePass2024
```
→ Bot detects: "Password Wordlist" → Uses for ML mutations

### Commands After Upload

```
/auto_scan - Start autonomous scan (uses all uploaded files)
/ml_status - Check ML learning progress
/quality_report - Validation statistics
/train - Retrain models
/optimize - System optimization
/autonomous_status - Full system status
```

---

## 🎯 Complete Workflow Example

### 1. Upload Combo File

Drop `combos.txt` in Telegram

Bot responds:
```
✅ Combo List Detected!

📊 Stats:
• Total Combos: 10,000
• File: combos.txt

🤖 Ready for autonomous processing!

Options:
1️⃣ /auto_scan - Start scan
2️⃣ /validate_combos - Check format
3️⃣ /preview_combos - Preview first 10
```

### 2. Optionally Upload Config

Drop `config.loli` in Telegram

Bot responds:
```
✅ OpenBullet Config Detected!

📊 Config Info:
• Name: Gmail Checker
• Settings Block: ✅
• Requests: ✅
• Keychecks: ✅
• Total Blocks: 5

Config auto-loaded!
```

### 3. Optionally Upload Proxies

Drop `proxies.txt` in Telegram

Bot responds:
```
✅ Proxy List Detected!

📊 Stats:
• Total Proxies: 1,000

Proxies auto-configured!
```

### 4. Start Scan

Send: `/auto_scan`

Bot responds:
```
🚀 Starting autonomous processing...

✅ AI learning enabled
✅ Quality validation active
✅ Real-time notifications on
✅ Auto-optimization enabled

Processing 10,000 combos...
```

### 5. Get Real-Time Updates

Every 60 seconds:
```
📊 Scan Progress Update

⚡ Processed: 1,250/10,000
✅ Hits Found: 45
📈 Success Rate: 3.6%
🎯 Quality Rate: 75.5%
⏱️ Speed: 125 emails/sec

🧠 Learning: 12 iterations
💾 Cache: 68% hit rate
```

Instant alerts for quality hits:
```
🎯 HIGH QUALITY HIT!

📧 Email: user@example.com
⭐ Quality: 87/100
📊 Grade: VERY_GOOD
🎖️ Confidence: 89.2%
💥 Breaches: 15
```

### 6. Download Results

At completion:
```
✅ SCAN COMPLETE!

📊 Total: 10,000
🎯 High Quality: 38
⭐ Medium Quality: 12

💾 Download: [Link]
```

---

## 🔍 Monitor System on Droplet

### Check System Status

```bash
# SSH into droplet
ssh root@143.110.254.40

# Check autonomous system
systemctl status autonomous-checker

# View live logs
journalctl -u autonomous-checker -f

# Check Docker services
docker-compose ps

# Check resource usage
htop
```

### View System Metrics

```bash
# CPU/Memory
top

# Disk usage
df -h

# Network
netstat -tulpn | grep LISTEN
```

---

## 🛡️ Security Best Practices

### 1. Firewall Configuration

```bash
# Already configured by deployment script
ufw status

# Should show:
# 22/tcp - SSH
# 80/tcp - HTTP
# 443/tcp - HTTPS (if using SSL)
# 8000/tcp - API
```

### 2. Secure Telegram Bot Token

```bash
# Ensure .env is protected
chmod 600 /opt/ai-email-checker/.env
```

### 3. Regular Updates

```bash
# Update system
apt-get update && apt-get upgrade -y

# Update Docker images
cd /opt/ai-email-checker
docker-compose pull
docker-compose up -d
```

---

## 📊 Performance Optimization

### Scale Workers

```bash
# Scale to 4 workers
docker-compose scale worker=4

# Or edit docker-compose.yml
nano docker-compose.yml
# Change worker replicas
docker-compose up -d
```

### Monitor Ollama

```bash
# Check Ollama logs
docker-compose logs -f ollama

# Test Ollama
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"test"}'
```

---

## 🔄 Update System

### Pull Latest Code

```bash
# On your local machine
rsync -avz --progress d:/ai-email-checker/* root@143.110.254.40:/opt/ai-email-checker/

# On droplet
ssh root@143.110.254.40
cd /opt/ai-email-checker
systemctl restart autonomous-checker
```

---

## 📞 Troubleshooting

### Bot Not Responding?

```bash
# Check service
systemctl status autonomous-checker

# Restart
systemctl restart autonomous-checker

# View logs
journalctl -u autonomous-checker -f
```

### Ollama Not Working?

```bash
# Check Ollama container
docker ps | grep ollama

# Restart Ollama
docker-compose restart ollama

# Pull Mistral model
docker exec -it ai-email-checker-ollama-1 ollama pull mistral
```

### Out of Memory?

```bash
# Check memory
free -h

# Reduce workers
nano docker-compose.yml
# Set workers: 2
docker-compose up -d
```

---

## ✅ Deployment Checklist

- [ ] Droplet created (143.110.254.40) ✅
- [ ] SSH access working
- [ ] Run deployment script: `bash deploy_to_droplet.sh`
- [ ] Verify services: `docker-compose ps`
- [ ] Update .env with credentials
- [ ] Test Telegram bot: Send `/start`
- [ ] Upload test combo file
- [ ] Run `/auto_scan`
- [ ] Verify real-time notifications
- [ ] Check ML learning: `/ml_status`

---

## 🎉 You're Ready!

Your autonomous system is deployed and accessible via Telegram!

**Next Steps:**
1. Run: `bash deploy_to_droplet.sh`
2. Open Telegram: `@hackingmasterr`
3. Upload combo file
4. Send: `/auto_scan`
5. Get results! 🚀

---

**Questions?** SSH into droplet and check logs:
```bash
ssh root@143.110.254.40
journalctl -u autonomous-checker -f
```
