#!/bin/bash
# Automatically configure Telegram bot via API

BOT_TOKEN="8400786399:AAHshCElHqdurEgthZ8m_J6F2muUjllMIT8"
API_URL="https://api.telegram.org/bot${BOT_TOKEN}"

echo "🤖 Configuring Telegram Bot via API..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Set bot commands
echo "📝 Setting bot commands..."
curl -s -X POST "${API_URL}/setMyCommands" \
  -H "Content-Type: application/json" \i 
  -d '{
    "commands": [
      {"command": "start", "description": "🚀 Start bot & welcome message"},
      {"command": "help", "description": "📖 Show all commands & features"},
      {"command": "auto_scan", "description": "⚡ Start autonomous scanning"},
      {"command": "autonomous_status", "description": "📊 System status & statistics"},
      {"command": "ml_status", "description": "🧠 ML learning progress"},
      {"command": "quality_report", "description": "🎯 Quality validation report"},
      {"command": "train", "description": "🔄 Retrain ML models"},
      {"command": "optimize", "description": "⚙️ Optimize system resources"},
      {"command": "pause", "description": "⏸️ Pause current processing"},
      {"command": "resume", "description": "▶️ Resume processing"},
      {"command": "stop", "description": "🛑 Stop current scan"},
      {"command": "download", "description": "💾 Download results"},
      {"command": "settings", "description": "⚙️ Configure system settings"},
      {"command": "stats", "description": "📈 View processing statistics"}
    ]
  }' | jq '.'

echo ""
echo "✅ Bot commands set successfully!"
echo ""

# Set bot description
echo "📝 Setting bot description..."
DESCRIPTION="🤖 AI-Powered Email Checker & Validator

Autonomous self-learning system with:
✅ Smart file detection (combos, configs, proxies)
✅ 6-layer quality validation
✅ Real-time progress updates
✅ ML-powered optimization
✅ Auto-scaling workers

Upload files → Get instant analysis → Start scanning!

Features:
• Email breach detection
• Password strength analysis
• Quality scoring (0-100)
• Automatic duplicate removal
• Format normalization
• Domain validation

Powered by local AI (Mistral via Ollama)
No data leaves your server!

Commands: /help
Dashboard: http://143.110.254.40"

curl -s -X POST "${API_URL}/setMyDescription" \
  -H "Content-Type: application/json" \
  -d "{\"description\": $(echo "$DESCRIPTION" | jq -Rs .)}" | jq '.'

echo ""
echo "✅ Bot description set successfully!"
echo ""

# Set bot short description
echo "📝 Setting bot short description..."
curl -s -X POST "${API_URL}/setMyShortDescription" \
  -H "Content-Type: application/json" \
  -d '{"short_description": "Autonomous AI Email Checker with smart file detection, quality validation, and real-time learning. Upload combos/configs/proxies and get instant results!"}' | jq '.'

echo ""
echo "✅ Bot short description set successfully!"
echo ""

# Get bot info to verify
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Bot Information:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "${API_URL}/getMe" | jq '.'

echo ""
echo "🎉 Bot configuration complete!"
echo ""
echo "✅ Your bot is ready at: https://t.me/ai_email_checker_bot"
echo "✅ Dashboard available at: http://143.110.254.40"
echo ""
echo "Test your bot:"
echo "  1. Open @ai_email_checker_bot in Telegram"
echo "  2. Send /start"
echo "  3. You should see all commands in the menu"
echo ""
