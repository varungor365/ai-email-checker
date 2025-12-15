"""
Autonomous System Launcher
Start the complete autonomous email checking system
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.autonomous_system import AutonomousSystem
from bot.telegram_bot import TelegramBotController
from bot.autonomous_commands import AutonomousBotCommands

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('autonomous_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Start autonomous system and Telegram bot"""
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    config = {
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', '8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M'),
        'telegram_admin_ids': [int(id.strip()) for id in os.getenv('TELEGRAM_ADMIN_IDS', '796354588').split(',')],
        'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
        'ollama_model': os.getenv('OLLAMA_MODEL', 'mistral'),
        'min_confidence': float(os.getenv('MIN_CONFIDENCE', '0.75')),
        'initial_workers': int(os.getenv('INITIAL_WORKERS', '2')),
        'target_speed': float(os.getenv('TARGET_SPEED', '100.0')),
        'progress_update_interval': int(os.getenv('PROGRESS_UPDATE_INTERVAL', '60'))
    }
    
    logger.info("=" * 60)
    logger.info("🤖 AUTONOMOUS EMAIL CHECKER SYSTEM")
    logger.info("=" * 60)
    logger.info("")
    logger.info("✅ Self-Learning AI Enabled")
    logger.info("✅ 6-Layer Quality Validation")
    logger.info("✅ Real-Time Telegram Notifications")
    logger.info("✅ Auto-Optimization Active")
    logger.info("✅ Continuous Training Pipeline")
    logger.info("")
    logger.info("Configuration:")
    logger.info(f"  • Min Confidence: {config['min_confidence']:.0%}")
    logger.info(f"  • Initial Workers: {config['initial_workers']}")
    logger.info(f"  • Target Speed: {config['target_speed']:.0f} emails/sec")
    logger.info(f"  • Progress Updates: Every {config['progress_update_interval']}s")
    logger.info(f"  • Ollama Model: {config['ollama_model']}")
    logger.info("")
    
    try:
        # Create autonomous system
        logger.info("🚀 Starting autonomous system...")
        system = AutonomousSystem(config)
        await system.start()
        logger.info("✅ Autonomous system started")
        
        # Create Telegram bot with autonomous system integration
        logger.info("🤖 Starting Telegram bot...")
        bot = TelegramBotController(
            token=config['telegram_bot_token'],
            admin_ids=config['telegram_admin_ids'],
            autonomous_system=system  # Pass system for smart file handler
        )
        
        # Add autonomous commands
        autonomous_commands = AutonomousBotCommands(system)
        autonomous_commands.register_handlers(bot.app)
        
        # Store system reference in bot context
        bot.autonomous_system = system
        
        logger.info("✅ Telegram bot with smart file detection started")
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 SYSTEM READY!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Telegram Bot Commands:")
        logger.info("  /auto_scan - Start autonomous processing")
        logger.info("  /ml_status - ML learning metrics")
        logger.info("  /quality_report - Validation statistics")
        logger.info("  /train [days] - Retrain models")
        logger.info("  /optimize - Get optimization recommendations")
        logger.info("  /autonomous_status - Full system status")
        logger.info("  /export_training - Export training data")
        logger.info("")
        logger.info("Send combo file (.txt) to bot to start!")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        # Run bot
        await bot.app.run_polling()
    
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Shutdown signal received...")
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
    
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        if 'system' in locals():
            await system.stop()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
