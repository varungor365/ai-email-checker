# 🔓 Credential Testing System

**MEGA account validator + HaveIBeenPwned breach detector + Account information extractor**

> ⚠️ **EDUCATIONAL & AUTHORIZED TESTING ONLY**  
> This tool is for authorized security testing, penetration testing, and educational purposes only.

---

## 🎯 What Does This System Do?

This is a **fully automated credential testing platform** that:

1. **✅ Tests email:password validity** against MEGA accounts (100+ threads)
2. **🔥 Finds ALL breached passwords** for each email using HaveIBeenPwned
3. **📊 Extracts account information** (recovery keys, storage, files, folders)
4. **⚡ Calculates risk scores** (0-100) for each credential
5. **📱 Sends real-time notifications** via Telegram bot
6. **💾 Generates detailed reports** (hits, breaches, JSON data)

### Why Use This Instead of Manual Testing?

- **Speed**: Test 1000s of combos per hour with parallel processing
- **Comprehensive**: Combines validity checking + breach detection + data extraction
- **Automated**: Upload combos → Get results → Download reports
- **Intelligent**: Calculates risk scores based on breach history and account value
- **Real-time**: Instant Telegram alerts for high-value hits

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/varungor365/ai-email-checker
cd ai-email-checker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install mega.py pycryptodome  # MEGA validator
```

### 2. Configuration

Create `.env` file:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_telegram_user_id

# Optional: HaveIBeenPwned API key (for higher rate limits)
HIBP_API_KEY=your_api_key  # Get from https://haveibeenpwned.com/API/Key
```

### 3. Run System

```bash
python start_credential_testing.py
```

### 4. Use Telegram Bot

1. Open Telegram
2. Find bot: `@ai_email_checker_bot`
3. Send `/start`
4. Upload combo file (`.txt` format)
5. Get real-time progress updates
6. Download results with `/get_hits`, `/get_breaches`, `/get_report`

---

## 📁 Combo File Format

**Required format:** `email:password` (one per line)

Example `combos.txt`:
```
test1@gmail.com:password123
john@outlook.com:SecurePass!
alice@mega.nz:MyPassword456
```

**Supported:**
- Any email provider
- Any password format
- Duplicates (auto-removed)
- Mixed case
- Special characters

**Not supported:**
- Email only (must have `:password`)
- Different delimiters (`;`, `|`, etc.)
- Comments (#)

---

## 🎮 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with instructions |
| `/status` | Current system status and progress |
| `/stats` | Detailed testing statistics |
| `/get_hits` | Download valid credentials file |
| `/get_breaches` | Download breach report |
| `/get_report` | Download full JSON report |
| `/stop` | Stop current test |
| `/help` | Show help message |

---

## 📊 What Gets Tested?

### MEGA Account Validation
- ✅ Login validity
- 📦 Account type (Pro/Free/Empty)
- 💾 Total storage (GB)
- 📁 Used storage (GB)
- 🗂️ File count
- 📂 Folder count
- 🛡️ Recovery key
- 👤 User information

### Breach Detection
- 🔥 Email breach history (HaveIBeenPwned)
- 📋 Number of breaches
- 📄 Breach details (name, date, data exposed)
- 📌 Paste appearances
- 🔑 Password breach frequency
- ⚠️ Times password was seen in breaches

### Risk Assessment
- 🎯 Overall risk score (0-100)
- 📊 Risk level (CRITICAL/HIGH/MEDIUM/LOW)
- 💎 Account value (Pro accounts with data = high value)
- 🔓 Credential exposure level

---

## 📈 Example Results

### Valid Credential (Hit)
```
🎯 VALID ACCOUNT FOUND
============================================================
📧 Email: user@example.com
🔑 Password: SecurePass123
🛡️ Recovery Key: ABC123XYZ789

📊 ACCOUNT DETAILS:
├── Type: PRO
├── Total Storage: 400 GB
├── Used Storage: 127.45 GB
├── Files: 1,234
└── Folders: 89

🔥 BREACH STATUS:
├── Email Breaches: 3
├── Password Seen: 127 times
├── Risk Level: HIGH
└── Risk Score: 75/100
```

### Breach Report
```
user@example.com:password123 | Breaches: 5 | Password seen: 10,245 times
john@gmail.com:MyPass456 | Breaches: 2 | Password seen: 87 times
alice@outlook.com:Test123 | Breaches: 0 | Password seen: 0 times
```

---

## 🔥 Real-Time Hit Notifications

When a high-value hit is found, you get instant Telegram alerts:

```
🎯 HIGH-VALUE HIT FOUND!

📧 Email: premium@user.com
🔑 Password: ***********
🛡️ Recovery Key: XYZ789ABC123

📊 Account:
• Type: PRO
• Storage: 400 GB (278.5 GB used)
• Files: 5,678 | Folders: 234

🔥 Security:
• Breaches: 3
• Password Seen: 1,245 times
• Risk: HIGH (82/100)
```

---

## 📦 Output Files

After testing completes, you get 4 files:

1. **`hits_TIMESTAMP.txt`** - All valid credentials with full details
2. **`breached_TIMESTAMP.txt`** - All emails found in breaches
3. **`high_risk_TIMESTAMP.txt`** - High-risk accounts (risk >= 60)
4. **`full_report_TIMESTAMP.json`** - Complete JSON data for analysis

All files saved to: `results/YOUR_CHAT_ID/`

---

## ⚙️ Advanced Configuration

### Adjust Thread Count

Edit `start_credential_testing.py`:
```python
tester = CredentialTester(max_threads=200)  # Default: 100
```

Higher threads = faster testing, but may hit rate limits

### HaveIBeenPwned Rate Limits

**Without API key:** 1.5 seconds per request (slow)  
**With API key:** Higher limits (recommended for large tests)

Get API key: https://haveibeenpwned.com/API/Key

Add to `.env`:
```env
HIBP_API_KEY=your_key_here
```

---

## 🛠️ Troubleshooting

### Bot not responding

```bash
# Check logs
tail -f credential_testing.log

# Verify bot token
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"

# Test bot API
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### MEGA login fails

- **Rate limited:** MEGA blocks after too many requests. Wait 1 hour.
- **Invalid credentials:** Expected - most combos will fail
- **mega.py error:** Reinstall with `pip install --force-reinstall mega.py`

### Breach detection slow

- **Normal:** HIBP requires 1.5s between requests without API key
- **Solution:** Get API key from https://haveibeenpwned.com/API/Key
- **Alternative:** Test in smaller batches

---

## 📊 Performance Stats

| Metric | Value |
|--------|-------|
| MEGA validation speed | 100-200 accounts/min (100 threads) |
| Breach detection speed | ~40 emails/min (no API key) |
| Breach detection speed | ~500 emails/min (with API key) |
| Memory usage | ~500 MB |
| CPU usage | 50-80% (parallel processing) |

---

## 🔗 Integration with HYPERION

This system integrates the best components from [HYPERION-Elite-Bot](https://github.com/varungor365/HYPERION-Elite-Bot):

- ✅ `UltraMegaAuthenticator` - High-performance MEGA validation
- ✅ Multi-threaded account checking
- ✅ Account type detection (Pro/Free/Empty)
- ✅ Recovery key extraction
- ✅ File/folder enumeration

**New additions:**
- 🔥 HaveIBeenPwned breach detection
- 📊 Risk scoring algorithm
- 🎯 Combined credential + breach testing
- 📱 Telegram bot integration
- 💾 Multi-format report generation

---

## 🚀 Deployment (Docker + DigitalOcean)

### Deploy to VPS

```bash
# SSH to droplet
ssh root@your_droplet_ip

# Pull latest code
cd /opt/ai-email-checker
git pull

# Install dependencies
source .venv/bin/activate
pip install mega.py pycryptodome aiohttp

# Update .env with new bot token
nano .env

# Restart service
systemctl restart credential-testing

# Check status
systemctl status credential-testing
journalctl -u credential-testing -f
```

### Create systemd service

Create `/etc/systemd/system/credential-testing.service`:

```ini
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
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable credential-testing
systemctl start credential-testing
```

---

## 📜 License

MIT License - See LICENSE file

---

## ⚠️ Legal Disclaimer

**IMPORTANT: READ BEFORE USING**

This tool is provided for **authorized security testing and educational purposes only**.

**YOU MUST:**
- ✅ Have explicit written permission to test accounts
- ✅ Only test accounts you own or have authorization for
- ✅ Comply with all applicable laws and regulations
- ✅ Use responsibly and ethically

**YOU MUST NOT:**
- ❌ Test accounts without authorization
- ❌ Use for unauthorized access attempts
- ❌ Violate terms of service of any platform
- ❌ Use for illegal activities

**The authors assume no liability for misuse of this tool.**

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📧 Contact

- **GitHub**: [varungor365](https://github.com/varungor365)
- **Telegram**: @ai_email_checker_bot

---

## 🔄 Version History

### v2.0.0 - Credential Testing System (Current)
- ✅ Complete rebuild for credential testing
- ✅ MEGA account validator integrated
- ✅ HaveIBeenPwned breach detection
- ✅ Account information extraction
- ✅ Risk scoring algorithm
- ✅ Telegram bot interface
- ✅ Multi-format report generation

### v1.0.0 - Email Quality Checker (Legacy)
- Email validation
- Ollama AI integration
- Quality scoring
- Self-learning system

---

**🔓 Built for security researchers, penetration testers, and authorized testing professionals.**
