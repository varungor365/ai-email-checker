#!/bin/bash
# Set up BotFather commands and description

echo "🤖 Telegram Bot Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Open Telegram and message @BotFather"
echo ""
echo "Then send these commands:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  SET BOT DESCRIPTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Send: /setdescription"
echo "Select: @ai_email_checker_bot"
echo "Then paste this:"
echo ""

cat << 'DESC'
🤖 AI-Powered Email Checker & Validator

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
Dashboard: http://143.110.254.40
DESC

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  SET BOT ABOUT TEXT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Send: /setabouttext"
echo "Select: @ai_email_checker_bot"
echo "Then paste this:"
echo ""

cat << 'ABOUT'
Autonomous AI Email Checker with smart file detection, quality validation, and real-time learning. Upload combos/configs/proxies and get instant results!
ABOUT

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  SET BOT COMMANDS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Send: /setcommands"
echo "Select: @ai_email_checker_bot"
echo "Then paste this:"
echo ""

cat << 'COMMANDS'
start - 🚀 Start bot & welcome message
help - 📖 Show all commands & features
auto_scan - ⚡ Start autonomous scanning
autonomous_status - 📊 System status & statistics
ml_status - 🧠 ML learning progress
quality_report - 🎯 Quality validation report
train - 🔄 Retrain ML models
optimize - ⚙️ Optimize system resources
pause - ⏸️ Pause current processing
resume - ▶️ Resume processing
stop - 🛑 Stop current scan
download - 💾 Download results
settings - ⚙️ Configure system settings
stats - 📈 View processing statistics
COMMANDS

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  SET BOT PROFILE PICTURE (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Send: /setuserpic"
echo "Select: @ai_email_checker_bot"
echo "Upload a bot avatar image"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ After configuring, test your bot:"
echo ""
echo "   1. Open @ai_email_checker_bot"
echo "   2. Send /start"
echo "   3. You should see commands in the menu button"
echo ""
echo "🎉 Bot configuration complete!"
echo ""
