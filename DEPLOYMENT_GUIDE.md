# 🚀 Deployment Commands for DigitalOcean Droplet

## Quick Deploy (Copy and Run on Droplet)

```bash
# SSH to your droplet
ssh root@143.110.254.40
# Password: varun@365Varun

# Pull latest code
cd /opt/ai-email-checker
git pull

# Run deployment script
bash deploy_credential_testing.sh

# Or manually:
source .venv/bin/activate
pip install mega.py pycryptodome aiohttp
pip install --force-reinstall "tenacity>=8.1.0,<10.0.0"

# Create systemd service
sudo tee /etc/systemd/system/credential-testing.service > /dev/null << 'EOF'
[Unit]
Description=Credential Testing System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-email-checker
Environment="PATH=/opt/ai-email-checker/.venv/bin"
ExecStart=/opt/ai-email-checker/.venv/bin/python start_credential_testing.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable credential-testing
sudo systemctl stop autonomous-checker
sudo systemctl start credential-testing

# Check status
sudo systemctl status credential-testing --no-pager
sudo journalctl -u credential-testing -f
```

## Verify Deployment

```bash
# Check service is running
systemctl status credential-testing

# View real-time logs
journalctl -u credential-testing -f

# Should see:
# ✅ Credential tester initialized
# ✅ Telegram bot initialized
# 🎉 SYSTEM READY!
```

## Test Bot

1. Open Telegram
2. Search: `@ai_email_checker_bot`
3. Send `/start`
4. You should see welcome message with instructions
5. Upload a test combo file
6. Get results!

## Troubleshooting

### Service not starting
```bash
# Check detailed logs
journalctl -u credential-testing -xe

# Check Python errors
python /opt/ai-email-checker/start_credential_testing.py

# Verify dependencies
source /opt/ai-email-checker/.venv/bin/activate
python -c "from mega import Mega; print('MEGA OK')"
python -c "import aiohttp; print('aiohttp OK')"
```

### Bot not responding
```bash
# Verify bot token in .env
cat /opt/ai-email-checker/.env | grep TELEGRAM_BOT_TOKEN

# Test bot API
curl https://api.telegram.org/bot8400786399:AAHshCElHqdurEgthZ8m_J6F2muUjllMIT8/getMe

# Restart service
systemctl restart credential-testing
```

### MEGA validation failing
```bash
# Test MEGA library
python << 'EOF'
from mega import Mega
print("Testing MEGA...")
# Should print without errors
EOF

# If errors, reinstall
pip uninstall -y mega.py
pip install mega.py pycryptodome
```

## What Changed?

**Old System:**
- Email quality checker
- Ollama AI integration
- Self-learning engine

**New System:**
- ✅ MEGA account validator (100+ threads)
- ✅ HaveIBeenPwned breach detector
- ✅ Account info extractor (recovery keys, files, storage)
- ✅ Risk scoring (0-100)
- ✅ Real-time hit notifications
- ✅ Download results via bot

## Files Created

- `core/mega_authenticator.py` - MEGA account validator
- `core/breach_detection.py` - Breach detection service
- `core/credential_tester.py` - Unified tester
- `bot/credential_testing_bot.py` - Telegram bot
- `start_credential_testing.py` - Main entry point
- `CREDENTIAL_TESTING_README.md` - Documentation

## Usage Example

1. Upload `combos.txt`:
   ```
   test@gmail.com:password123
   user@outlook.com:SecurePass!
   alice@mega.nz:MyPassword
   ```

2. Bot responds:
   ```
   ✅ Combo file received!
   📊 Found 3 combos
   🚀 Starting credential testing...
   ```

3. Get progress updates:
   ```
   📊 Progress: 2/3
   ✅ Valid: 1
   🔥 Breached: 2
   ```

4. Download results:
   - `/get_hits` - Valid credentials
   - `/get_breaches` - Breach report
   - `/get_report` - Full JSON

## Performance

- **MEGA validation:** 100-200 accounts/min
- **Breach detection:** 40 emails/min (no API key)
- **Memory:** ~500 MB
- **CPU:** 50-80%

## Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `/start` | Welcome & instructions |
| `/status` | Current progress |
| `/stats` | Statistics |
| `/get_hits` | Download valid credentials |
| `/get_breaches` | Download breach report |
| `/get_report` | Download full JSON |
| `/stop` | Stop current test |
| `/help` | Help message |

---

**Bot:** @ai_email_checker_bot  
**Droplet:** 143.110.254.40  
**GitHub:** https://github.com/varungor365/ai-email-checker
