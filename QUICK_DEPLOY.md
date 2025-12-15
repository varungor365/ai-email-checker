# ⚡ ONE COMMAND DEPLOYMENT

## Quick Start (30 Seconds to Deploy)

### Option 1: Automated Setup (Recommended)

```powershell
.\setup_github.ps1
```

**What it does:**
1. Asks for your GitHub username
2. Adds remote and pushes code
3. Deploys to droplet 143.110.254.40
4. Starts all services automatically

---

### Option 2: Manual (3 Commands)

```powershell
# 1. Push to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-email-checker.git
git push -u origin main

# 2. Deploy to droplet (replace YOUR_USERNAME)
bash deploy_git.sh YOUR_USERNAME/ai-email-checker

# 3. Test Telegram bot
# Open Telegram → @hackingmasterr → Send /start
```

---

## After Deployment

### Test in Telegram

1. **Open Telegram** → Search `@hackingmasterr`
2. **Send** `/start`
3. **Upload** a combo file (email:password format)
4. **Bot auto-detects** file type
5. **Send** `/auto_scan`
6. **Watch** real-time progress!

---

## Your System Includes

✅ **11 Docker Services**
- PostgreSQL, MongoDB, Redis
- Ollama AI (Mistral model)
- API server, Workers, Telegram bot
- Monitoring & optimization

✅ **Smart File Detection**
- Auto-detects combo lists
- Auto-detects OpenBullet configs
- Auto-detects proxy lists
- Auto-detects wordlists

✅ **Autonomous Processing**
- Self-learning AI
- 6-layer quality validation
- Real-time Telegram notifications
- Auto-scaling workers
- Continuous ML training

✅ **Auto-Start**
- Systemd service
- Restarts on crash
- Starts on boot

✅ **Web Access**
- Nginx reverse proxy
- Firewall configured
- API: http://143.110.254.40

---

## Update Later

```powershell
# Make changes locally
git add .
git commit -m "My changes"
git push

# Update on droplet
ssh root@143.110.254.40 'cd /opt/ai-email-checker && git pull && systemctl restart autonomous-checker'
```

---

## View Logs

```bash
ssh root@143.110.254.40 'journalctl -u autonomous-checker -f'
```

---

## That's It! 

**Run:** `.\setup_github.ps1`

**Then:** Test on Telegram @hackingmasterr

🎉 **Your autonomous system is live!**
