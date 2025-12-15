# 🚀 Quick GitHub Deployment Guide

## Setup in 3 Steps

### Step 1: Create GitHub Repository

**Option A: Via GitHub Website (Easiest)**

1. Go to: https://github.com/new
2. Repository name: `ai-email-checker`
3. Description: `Autonomous AI Email Checker with Smart Detection`
4. Set to: **Private** (recommended for security)
5. Click: **Create repository**

**Option B: Via GitHub CLI**

```bash
# Install GitHub CLI first: https://cli.github.com/
gh repo create ai-email-checker --private --source=. --remote=origin
```

---

### Step 2: Push Code to GitHub

```powershell
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-email-checker.git

# Push code
git branch -M main
git push -u origin main
```

**Example:**
```powershell
git remote add origin https://github.com/john/ai-email-checker.git
git branch -M main
git push -u origin main
```

You'll be prompted for GitHub credentials. Use a **Personal Access Token** instead of password:
- Go to: https://github.com/settings/tokens
- Click: Generate new token (classic)
- Select scopes: `repo` (all)
- Copy the token and paste when prompted for password

---

### Step 3: Deploy to Droplet

```bash
# Deploy from GitHub to your droplet
bash deploy_git.sh YOUR_USERNAME/ai-email-checker
```

**Example:**
```bash
bash deploy_git.sh john/ai-email-checker
```

---

## Complete Example Flow

```powershell
# 1. Verify Git status
git status

# 2. Add GitHub remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/ai-email-checker.git

# 3. Push to GitHub
git branch -M main
git push -u origin main

# 4. Deploy to droplet
bash deploy_git.sh YOUR_USERNAME/ai-email-checker
```

---

## After Deployment

### ✅ Verify Telegram Bot

1. Open Telegram
2. Search: `@hackingmasterr`
3. Send: `/start`

Expected response:
```
🤖 AI Email Checker Bot

Your autonomous system is ready!
```

### ✅ Test Smart File Detection

Upload a combo file:
```
user1@gmail.com:password123
user2@yahoo.com:SecurePass!
```

Bot should auto-detect it as "Combo List"

---

## Update Code Later

After making local changes:

```powershell
# Commit changes
git add .
git commit -m "Description of changes"
git push

# Update on droplet
ssh root@143.110.254.40 'cd /opt/ai-email-checker && git pull && systemctl restart autonomous-checker'
```

---

## Troubleshooting

### Problem: Git push asks for password repeatedly

**Solution:** Use SSH instead of HTTPS

```powershell
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
Get-Content ~/.ssh/id_ed25519.pub | clip

# Add to GitHub: https://github.com/settings/keys
# Then change remote URL:
git remote set-url origin git@github.com:YOUR_USERNAME/ai-email-checker.git
```

### Problem: "Permission denied" when deploying

**Solution:** Set up SSH key for droplet

```powershell
# Copy SSH key to droplet
ssh-copy-id root@143.110.254.40
```

---

## What Gets Deployed?

The deployment script automatically:

✅ Clones your code from GitHub
✅ Installs Docker & Docker Compose
✅ Starts 11 Docker services
✅ Installs Python dependencies
✅ Downloads Ollama AI model (Mistral)
✅ Creates systemd auto-start service
✅ Configures Nginx reverse proxy
✅ Sets up firewall
✅ Starts autonomous system

---

## Your Repository Structure

```
ai-email-checker/
├── .git/                  # Git repository
├── .gitignore            # Ignored files
├── bot/                  # Telegram bot
│   ├── smart_file_handler.py  # Auto file detection
│   └── autonomous_commands.py  # Bot commands
├── core/                 # Core system
│   ├── ai/              # Self-learning AI
│   ├── validation/      # Quality validation
│   └── autonomous_system.py
├── docker-compose.yml    # 11 Docker services
├── requirements.txt      # Python dependencies
├── deploy_git.sh        # Deployment script
└── start_autonomous.py  # Main entry point
```

---

## Security Notes

### Keep These Private:

❌ Never commit to public repo:
- `.env` file (already in .gitignore)
- Telegram bot token
- Database passwords
- API keys

✅ Safe to share:
- `.env.example` template
- All code files
- Documentation

### Private Repository Recommended

For maximum security, keep your GitHub repo **Private**. The deployment script works with both public and private repos.

For private repos, you may need to authenticate on the droplet:

```bash
# On droplet, configure Git credentials
ssh root@143.110.254.40
git config --global credential.helper store
# Then git pull will ask for credentials once
```

---

## 🎉 You're Ready!

1. Create GitHub repo
2. Push code: `git push -u origin main`
3. Deploy: `bash deploy_git.sh YOUR_USERNAME/ai-email-checker`
4. Test Telegram bot: `/start`
5. Upload combo file
6. Run: `/auto_scan`

**Questions?** Check logs:
```bash
ssh root@143.110.254.40 'journalctl -u autonomous-checker -f'
```
