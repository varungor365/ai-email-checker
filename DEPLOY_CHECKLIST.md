# 🚀 Deployment Checklist

## Pre-Deployment

### ✅ Step 1: Verify SSH Access

```bash
# Test connection to droplet
ssh root@143.110.254.40 'echo "✅ SSH connection successful!"'
```

**Expected Output:** `✅ SSH connection successful!`

If you get a password prompt, that's fine - enter your password.

If you want passwordless access:
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096

# Copy to droplet
ssh-copy-id root@143.110.254.40
```

---

### ✅ Step 2: Verify .env Configuration

Check your `.env` file has correct Telegram credentials:

```env
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588
```

Run:
```powershell
Get-Content .env | Select-String "TELEGRAM"
```

---

### ✅ Step 3: Verify Docker Compose

Check docker-compose.yml exists:
```powershell
Test-Path docker-compose.yml
```

Should return: `True`

---

## Deployment

### 🚀 Option 1: Automated (Recommended)

**Single command deployment:**

```bash
bash deploy_to_droplet.sh
```

This will:
1. ✅ Install Docker, Docker Compose, Python, Nginx
2. ✅ Copy all files to `/opt/ai-email-checker`
3. ✅ Start 11 Docker services
4. ✅ Install Python dependencies
5. ✅ Create systemd auto-start service
6. ✅ Configure Nginx reverse proxy
7. ✅ Set up firewall (UFW)
8. ✅ Start autonomous system

**Time:** ~5-10 minutes

---

### 🛠️ Option 2: Manual (If Automated Fails)

#### Step 1: Connect to Droplet
```bash
ssh root@143.110.254.40
```

#### Step 2: Install Dependencies
```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install other tools
apt-get install -y docker-compose python3 python3-pip python3-venv git nginx ufw
```

#### Step 3: Create Directory
```bash
mkdir -p /opt/ai-email-checker
cd /opt/ai-email-checker
```

#### Step 4: Copy Files (From Your Local Machine)

**Option A: Using rsync (Recommended)**
```bash
rsync -avz --progress \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude '*.pyc' \
  d:/ai-email-checker/* \
  root@143.110.254.40:/opt/ai-email-checker/
```

**Option B: Using scp**
```bash
scp -r d:/ai-email-checker/* root@143.110.254.40:/opt/ai-email-checker/
```

#### Step 5: Set Up Environment (On Droplet)
```bash
# Create .env
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
MIN_CONFIDENCE=0.75
INITIAL_WORKERS=2
TARGET_SPEED=100.0
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_checker
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password_123
MONGODB_HOST=localhost
MONGODB_PORT=27017
REDIS_HOST=localhost
REDIS_PORT=6379
EOF

# Make scripts executable
chmod +x *.sh
```

#### Step 6: Start Docker Services
```bash
docker-compose up -d
docker-compose ps
```

Expected: 11 services running

#### Step 7: Install Python Dependencies
```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

#### Step 8: Create Systemd Service
```bash
cat > /etc/systemd/system/autonomous-checker.service << 'EOF'
[Unit]
Description=AI Email Checker Autonomous System
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-email-checker
Environment="PATH=/opt/ai-email-checker/.venv/bin:/usr/bin:/bin"
ExecStart=/opt/ai-email-checker/.venv/bin/python start_autonomous.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable autonomous-checker
systemctl start autonomous-checker
```

#### Step 9: Configure Nginx
```bash
cat > /etc/nginx/sites-available/email-checker << 'EOF'
server {
    listen 80;
    server_name 143.110.254.40;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/email-checker /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### Step 10: Configure Firewall
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable
```

---

## Post-Deployment Verification

### ✅ Check 1: System Service
```bash
ssh root@143.110.254.40 'systemctl status autonomous-checker'
```

Should show: `Active: active (running)`

---

### ✅ Check 2: Docker Services
```bash
ssh root@143.110.254.40 'cd /opt/ai-email-checker && docker-compose ps'
```

Should show 11 services with "Up" status:
- postgres
- mongodb
- redis
- ollama
- api
- worker (may have multiple)
- telegram_bot
- trainer
- optimizer

---

### ✅ Check 3: Web API
```bash
curl http://143.110.254.40
```

Should return JSON response

---

### ✅ Check 4: Telegram Bot

1. Open Telegram
2. Search: `@hackingmasterr`
3. Send: `/start`

Expected response:
```
🤖 AI Email Checker Bot

Your autonomous system is ready!

Upload files to get started:
📁 Combo lists (.txt)
⚙️ Configs (.loli)
🔌 Proxies (.txt)

Commands:
/help - Show all commands
/autonomous_status - System status
```

---

### ✅ Check 5: Smart File Detection

**Test combo upload:**

1. Create test file: `test_combos.txt`
```
test1@gmail.com:password123
test2@yahoo.com:SecurePass!
test3@outlook.com:MyPass456
```

2. Upload to bot

Expected response:
```
✅ Combo List Detected!

📊 Stats:
• Total Combos: 3
• File: test_combos.txt
• Sample Format: email:password

🤖 Ready for autonomous processing!

Available Commands:
1️⃣ /auto_scan - Start autonomous scan
2️⃣ /validate_combos - Validate format
3️⃣ /preview_combos - Preview entries
```

---

### ✅ Check 6: Logs
```bash
ssh root@143.110.254.40 'journalctl -u autonomous-checker -n 50'
```

Look for:
- `✅ Autonomous system started`
- `✅ Telegram bot with smart file detection started`
- No error messages

---

## Troubleshooting

### Problem: SSH Connection Refused
```bash
# Check if droplet is running
ping 143.110.254.40

# Try with password
ssh -o PreferredAuthentications=password root@143.110.254.40
```

---

### Problem: Docker Not Found
```bash
ssh root@143.110.254.40

# Reinstall Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

---

### Problem: Service Not Starting
```bash
ssh root@143.110.254.40

# Check logs
journalctl -u autonomous-checker -f

# Check Python environment
cd /opt/ai-email-checker
.venv/bin/python --version

# Reinstall dependencies
.venv/bin/pip install -r requirements.txt
```

---

### Problem: Telegram Bot Not Responding
```bash
ssh root@143.110.254.40

# Restart service
systemctl restart autonomous-checker

# Check bot is running
ps aux | grep telegram

# Test Telegram connection
.venv/bin/python -c "from telegram import Bot; print(Bot('YOUR_TOKEN').get_me())"
```

---

### Problem: Ollama Not Working
```bash
ssh root@143.110.254.40

# Check Ollama container
docker ps | grep ollama

# Restart Ollama
docker-compose restart ollama

# Pull Mistral model
docker exec -it ai-email-checker-ollama-1 ollama pull mistral

# Test Ollama
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"test"}'
```

---

## Quick Commands Reference

### View Live Logs
```bash
ssh root@143.110.254.40 'journalctl -u autonomous-checker -f'
```

### Restart System
```bash
ssh root@143.110.254.40 'systemctl restart autonomous-checker'
```

### Check Resource Usage
```bash
ssh root@143.110.254.40 'htop'
```

### Update Code
```bash
# From local machine
rsync -avz --progress d:/ai-email-checker/* root@143.110.254.40:/opt/ai-email-checker/

# Restart on droplet
ssh root@143.110.254.40 'systemctl restart autonomous-checker'
```

---

## Success Criteria

✅ SSH connection works
✅ All Docker services running
✅ Systemd service active
✅ Nginx responding on port 80
✅ Telegram bot responds to `/start`
✅ Smart file detection working (combo upload shows analysis)
✅ `/auto_scan` command available
✅ Real-time notifications working
✅ Ollama AI responding

---

## Next Steps After Successful Deployment

1. **Upload Real Combo List**
   - Drop your combo file in Telegram
   - Bot will auto-detect and analyze

2. **Upload OpenBullet Config** (Optional)
   - Drop .loli file
   - Bot will auto-load for scanning

3. **Upload Proxy List** (Optional)
   - Drop proxy file
   - Bot will auto-configure

4. **Start Autonomous Scan**
   ```
   /auto_scan
   ```

5. **Monitor Progress**
   - Real-time updates every 60 seconds
   - Instant notifications for quality hits
   - ML learning progress reports

6. **Download Results**
   ```
   /download
   ```

---

## Emergency Commands

### Stop Everything
```bash
ssh root@143.110.254.40 'systemctl stop autonomous-checker && docker-compose down'
```

### Start Everything
```bash
ssh root@143.110.254.40 'docker-compose up -d && systemctl start autonomous-checker'
```

### Full Reset
```bash
ssh root@143.110.254.40 'systemctl stop autonomous-checker && docker-compose down -v && rm -rf /opt/ai-email-checker/*'
```

Then re-deploy from scratch.

---

🎉 **Ready to deploy!** Run: `bash deploy_to_droplet.sh`
