# Telegram Bot Setup Guide

## 📱 Create Telegram Bot

### 1. Create Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Start chat and send `/newbot`
3. Enter bot name: `AI Email Checker Bot`
4. Enter bot username: `ai_email_checker_bot` (must end with 'bot')
5. BotFather will give you a **token** like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **Save this token** - you'll need it!

### 2. Get Your Admin ID

1. Search for `@userinfobot` on Telegram
2. Start chat - it will send you your user ID
3. **Save your user ID** - example: `123456789`

### 3. Configure Bot

Add to `.env` file:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_IDS=123456789,987654321  # Comma-separated admin IDs
```

## 🚀 Quick Start

### Install Dependencies

```bash
pip install python-telegram-bot aiohttp psutil
```

### Run Bot

```bash
# Standalone
python bot/telegram_bot.py

# With Docker
docker-compose up -d telegram-bot
```

## 📋 Available Commands

### Email Scanning
- `/scan <email>` - Scan single email for leaks
- `/bulk` - Upload email list for bulk scanning
- `/results` - View recent scan results

### System Control (Admin Only)
- `/stats` - System statistics (CPU, memory, workers)
- `/system` - System control panel
- `/workers <count>` - Scale worker count (1-50)
- `/status` - Quick system status
- `/logs` - View live logs

### File Management
- `/download` - Download results (CSV/JSON)
- 📎 **Upload files:**
  - `.txt` or `.csv` - Bulk email lists
  - `.loli` - OpenBullet configs

## 💡 Usage Examples

### Scan Single Email
```
/scan test@example.com
```

Bot will respond with:
```
🔍 Scanning test@example.com...
Checking 30+ sources...

🔴 Scan Results

📧 Email: test@example.com
🎯 Risk Score: 75/100 (CRITICAL)
🔍 Sources Checked: 30
⚠️ Leaks Found: 5
🗃️ Breaches: 3

Top Breaches:
• LinkedIn (via HaveIBeenPwned)
• Adobe (via BreachDirectory)
• Dropbox (via EmailRep.io)

Recommendations:
• 🚨 URGENT: Change password immediately
• 🔐 Enable 2FA on all critical accounts
• 📧 Consider changing email address
```

### Bulk Scan
```
1. Send command: /bulk
2. Upload .txt file with emails (one per line):
   email1@example.com
   email2@example.com
   email3@example.com
3. Bot processes and sends results
```

### System Control
```
/system
```

Shows inline buttons:
- ▶️ Start
- ⏸️ Stop
- 🔄 Restart
- 📊 Status
- 📈 Scale Workers

### Scale Workers
```
/workers 10
```

Response:
```
⚙️ Scaling to 10 workers...
✅ Successfully scaled to 10 workers
```

### View Stats
```
/stats
```

Response:
```
📊 System Statistics

System Resources:
🖥️ CPU: 45%
💾 Memory: 60% (5GB / 8GB)
💿 Disk: 40% (40GB / 100GB)

Workers:
Active Workers: 5
Queue Size: 120
Tasks Completed: 1,543

Performance:
CPM: 650
Success Rate: 82%
Uptime: 2d 5h 32m
```

### Download Results
```
/download
```

Shows buttons:
- 📥 Download CSV
- 📥 Download JSON
- 📥 Download Logs

## 🔐 Security Features

### Admin-Only Commands
Only users with IDs in `TELEGRAM_ADMIN_IDS` can:
- Control system (start/stop/restart)
- Scale workers
- View logs
- Access system control panel

### File Upload Validation
- File type checking (.txt, .csv, .loli only)
- Size limits (configurable)
- Virus scanning (optional)

### Rate Limiting
- Prevent spam
- Configurable limits per user
- Admin exemption

## 🎨 Inline Keyboards

Bot uses interactive buttons for:
- Quick actions
- System control
- File downloads
- Results navigation

Example:
```
/start
```

Shows:
```
🤖 AI Email Checker Bot

Welcome @username!

[📊 Stats] [🔍 Scan Email] [📈 Results]
```

## 📊 Real-Time Updates

Bot sends automatic notifications for:
- Bulk scan completion
- System alerts
- High-risk email detection
- Worker scaling events

## 🔧 Advanced Configuration

### Custom Commands

Add to `telegram_bot.py`:

```python
async def cmd_custom(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command"""
    await update.message.reply_text("Custom response")

# Register handler
self.app.add_handler(CommandHandler("custom", self.cmd_custom))
```

### Scheduled Messages

```python
from telegram.ext import JobQueue

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    """Send daily stats report"""
    stats = await get_daily_stats()
    await context.bot.send_message(
        chat_id=ADMIN_IDS[0],
        text=f"📊 Daily Report\n\n{stats}"
    )

# Schedule job
job_queue.run_daily(send_daily_report, time=datetime.time(hour=9))
```

### Webhook Mode (Production)

For production, use webhooks instead of polling:

```python
# Instead of run_polling()
self.app.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path="telegram_webhook",
    webhook_url="https://yourdomain.com/telegram_webhook"
)
```

## 🐛 Troubleshooting

### Bot Not Responding

1. Check token is correct
2. Verify bot is running: `ps aux | grep telegram_bot`
3. Check logs: `tail -f logs/telegram_bot.log`
4. Test API connection: `curl https://api.telegram.org/bot<TOKEN>/getMe`

### "Admin access required" Error

1. Verify your user ID is in `TELEGRAM_ADMIN_IDS`
2. Check `.env` file is loaded
3. Restart bot

### File Upload Fails

1. Check file size (default max 500MB)
2. Verify file type is supported
3. Check disk space
4. Review file permissions

## 📈 Production Deployment

### Systemd Service

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=AI Email Checker Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-checker
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/opt/ai-checker/.env
ExecStart=/usr/bin/python3 bot/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable telegram-bot
systemctl start telegram-bot
systemctl status telegram-bot
```

### Docker Compose

Add to `docker-compose.yml`:

```yaml
  telegram-bot:
    build:
      context: .
      dockerfile: bot/Dockerfile
    container_name: telegram-bot
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
      - ./results:/app/results
    depends_on:
      - api
    networks:
      - ai-checker-network
```

Create `bot/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/
COPY core/ ./core/

CMD ["python", "bot/telegram_bot.py"]
```

## 🌟 Pro Tips

1. **Use inline buttons** for better UX
2. **Send progress updates** for long operations
3. **Format messages** with Markdown/HTML
4. **Add emojis** for visual clarity
5. **Implement command aliases** for convenience
6. **Log all actions** for audit trail
7. **Rate limit users** to prevent abuse
8. **Send notifications** for important events

## 📱 Mobile Access

Bot works perfectly on:
- Telegram mobile app (iOS/Android)
- Telegram Desktop
- Telegram Web

## 🔗 Integration with Dashboard

Bot can:
- Trigger scans that appear in web dashboard
- Access same database as web interface
- Control same workers
- Download same results

## 🆘 Support

For help:
1. Send `/help` command to bot
2. Check logs: `docker logs telegram-bot`
3. Review Telegram Bot API docs: https://core.telegram.org/bots/api

---

**Bot Status: 🟢 Active**
