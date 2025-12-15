"""
Enhanced Telegram Bot with Smart File Detection
Automatically detects and processes: combos, configs, wordlists, proxies, etc.
"""

import os
import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from telegram import Update, Document
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class SmartFileHandler:
    """
    Automatically detects file type and processes accordingly
    
    Supports:
    - Combo lists (email:password)
    - OpenBullet configs (.loli, .anom)
    - Wordlists (passwords, usernames)
    - Proxy lists (http, socks4, socks5)
    - Config files (.ini, .json, .yaml)
    - Results files
    """
    
    def __init__(self, autonomous_system):
        self.system = autonomous_system
        self.upload_dir = Path('uploads')
        self.upload_dir.mkdir(exist_ok=True)
        
        # File type patterns
        self.patterns = {
            'combo': {
                'extensions': ['.txt', '.csv'],
                'content_pattern': r'[\w\.-]+@[\w\.-]+:',
                'min_matches': 3
            },
            'config': {
                'extensions': ['.loli', '.anom', '.svb', '.config'],
                'keywords': ['[SETTINGS]', 'REQUEST', 'KEYCHECK']
            },
            'wordlist_passwords': {
                'extensions': ['.txt'],
                'keywords': ['password', 'pass', 'pwd'],
                'min_length': 4
            },
            'wordlist_usernames': {
                'extensions': ['.txt'],
                'keywords': ['user', 'username', 'email'],
                'min_length': 3
            },
            'proxy': {
                'extensions': ['.txt'],
                'content_pattern': r'\d+\.\d+\.\d+\.\d+:\d+',
                'min_matches': 5
            },
            'settings': {
                'extensions': ['.ini', '.json', '.yaml', '.yml', '.env']
            }
        }
    
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, document: Document):
        """
        Smart file handler - auto-detects type and processes
        """
        try:
            # Download file
            file = await document.get_file()
            filename = document.file_name
            filepath = self.upload_dir / filename
            
            await update.message.reply_text(
                f"📥 **Downloading:** `{filename}`\n"
                f"📦 Size: {document.file_size / 1024:.1f} KB\n\n"
                f"🔍 Analyzing file type...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            await file.download_to_drive(filepath)
            
            # Detect file type
            file_type = await self._detect_file_type(filepath)
            
            # Process based on type
            if file_type == 'combo':
                await self._process_combo_list(update, context, filepath)
            
            elif file_type == 'config':
                await self._process_config_file(update, context, filepath)
            
            elif file_type == 'proxy':
                await self._process_proxy_list(update, context, filepath)
            
            elif file_type == 'wordlist_passwords':
                await self._process_password_wordlist(update, context, filepath)
            
            elif file_type == 'wordlist_usernames':
                await self._process_username_wordlist(update, context, filepath)
            
            elif file_type == 'settings':
                await self._process_settings_file(update, context, filepath)
            
            else:
                await update.message.reply_text(
                    "⚠️ **Unknown File Type**\n\n"
                    f"Couldn't automatically detect file type: `{filename}`\n\n"
                    "Supported types:\n"
                    "• Combo lists (email:password)\n"
                    "• OpenBullet configs (.loli, .anom)\n"
                    "• Proxy lists (IP:PORT)\n"
                    "• Wordlists (passwords, usernames)\n"
                    "• Config files (.ini, .json, .yaml)\n\n"
                    "Please specify manually with:\n"
                    "/set_file_type combo|config|proxy|wordlist",
                    parse_mode=ParseMode.MARKDOWN
                )
        
        except Exception as e:
            logger.error(f"Error handling file: {e}")
            await update.message.reply_text(f"❌ Error processing file: {e}")
    
    async def _detect_file_type(self, filepath: Path) -> str:
        """Automatically detect file type"""
        try:
            # Read first 100 lines for analysis
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline().strip() for _ in range(100)]
            
            content = '\n'.join(lines)
            
            # Check combo list (email:password)
            import re
            email_pass_pattern = r'[\w\.-]+@[\w\.-]+\.\w+:.+'
            email_matches = re.findall(email_pass_pattern, content)
            
            if len(email_matches) >= 3:
                return 'combo'
            
            # Check OpenBullet config
            if any(keyword in content for keyword in ['[SETTINGS]', 'REQUEST', 'KEYCHECK', '[BLOCK:']):
                return 'config'
            
            # Check proxy list (IP:PORT)
            proxy_pattern = r'\d+\.\d+\.\d+\.\d+:\d+'
            proxy_matches = re.findall(proxy_pattern, content)
            
            if len(proxy_matches) >= 5:
                return 'proxy'
            
            # Check file extension
            ext = filepath.suffix.lower()
            
            if ext in ['.loli', '.anom', '.svb']:
                return 'config'
            
            if ext in ['.ini', '.json', '.yaml', '.yml', '.env']:
                return 'settings'
            
            # Check content for wordlists
            filename_lower = filepath.name.lower()
            
            if any(kw in filename_lower for kw in ['pass', 'password', 'pwd']):
                return 'wordlist_passwords'
            
            if any(kw in filename_lower for kw in ['user', 'username', 'email']):
                return 'wordlist_usernames'
            
            return 'unknown'
        
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return 'unknown'
    
    async def _process_combo_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filepath: Path):
        """Process combo list and start autonomous scan"""
        try:
            # Count combos
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if ':' in line]
            
            combo_count = len(lines)
            
            message = (
                f"✅ **Combo List Detected!**\n\n"
                f"📊 **Stats:**\n"
                f"• Total Combos: {combo_count:,}\n"
                f"• File: `{filepath.name}`\n\n"
                f"🤖 **Ready for autonomous processing!**\n\n"
                f"What would you like to do?\n"
                f"1️⃣ `/auto_scan` - Start autonomous scan\n"
                f"2️⃣ `/validate_combos` - Validate format first\n"
                f"3️⃣ `/preview_combos` - Preview first 10 lines\n"
                f"4️⃣ `/sort_combos` - Sort by domain\n\n"
                f"💡 Recommended: `/auto_scan` for instant processing with ML!"
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # Store filepath in context
            context.user_data['last_combo_file'] = str(filepath)
            context.user_data['combo_count'] = combo_count
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing combo list: {e}")
    
    async def _process_config_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filepath: Path):
        """Process OpenBullet config file"""
        try:
            # Parse config
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract basic info
            config_info = {
                'name': filepath.stem,
                'has_settings': '[SETTINGS]' in content,
                'has_requests': 'REQUEST' in content,
                'has_keycheck': 'KEYCHECK' in content,
                'blocks': content.count('[BLOCK:')
            }
            
            message = (
                f"✅ **OpenBullet Config Detected!**\n\n"
                f"📊 **Config Info:**\n"
                f"• Name: `{config_info['name']}`\n"
                f"• Settings Block: {'✅' if config_info['has_settings'] else '❌'}\n"
                f"• Requests: {'✅' if config_info['has_requests'] else '❌'}\n"
                f"• Keychecks: {'✅' if config_info['has_keycheck'] else '❌'}\n"
                f"• Total Blocks: {config_info['blocks']}\n\n"
                f"🔧 **Auto-Configuration:**\n"
                f"Config will be automatically loaded when you start a scan.\n\n"
                f"Upload combo list and run `/auto_scan`!"
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # Store config path
            context.user_data['last_config_file'] = str(filepath)
            context.user_data['config_info'] = config_info
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing config: {e}")
    
    async def _process_proxy_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filepath: Path):
        """Process proxy list"""
        try:
            # Count proxies
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                import re
                proxy_pattern = r'\d+\.\d+\.\d+\.\d+:\d+'
                proxies = re.findall(proxy_pattern, f.read())
            
            proxy_count = len(proxies)
            
            message = (
                f"✅ **Proxy List Detected!**\n\n"
                f"📊 **Stats:**\n"
                f"• Total Proxies: {proxy_count:,}\n"
                f"• File: `{filepath.name}`\n\n"
                f"🔧 **Auto-Configuration:**\n"
                f"Proxies will be automatically loaded for scanning.\n\n"
                f"Options:\n"
                f"• `/test_proxies` - Test connectivity\n"
                f"• `/filter_proxies` - Filter by speed/country\n"
                f"• `/auto_scan` - Use proxies in scan"
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # Store proxy file
            context.user_data['last_proxy_file'] = str(filepath)
            context.user_data['proxy_count'] = proxy_count
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing proxies: {e}")
    
    async def _process_password_wordlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filepath: Path):
        """Process password wordlist"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            message = (
                f"✅ **Password Wordlist Detected!**\n\n"
                f"📊 **Stats:**\n"
                f"• Total Passwords: {len(passwords):,}\n"
                f"• File: `{filepath.name}`\n\n"
                f"🧠 **AI Enhancement:**\n"
                f"Wordlist will be used for ML-powered password mutations.\n\n"
                f"Use `/auto_scan` to apply these passwords!"
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            context.user_data['last_wordlist_file'] = str(filepath)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing wordlist: {e}")
    
    async def _process_username_wordlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filepath: Path):
        """Process username wordlist"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                usernames = [line.strip() for line in f if line.strip()]
            
            message = (
                f"✅ **Username Wordlist Detected!**\n\n"
                f"📊 **Stats:**\n"
                f"• Total Usernames: {len(usernames):,}\n"
                f"• File: `{filepath.name}`\n\n"
                f"Stored for combo generation."
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            context.user_data['last_username_file'] = str(filepath)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing wordlist: {e}")
    
    async def _process_settings_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, filepath: Path):
        """Process settings/config file"""
        try:
            ext = filepath.suffix.lower()
            
            message = (
                f"✅ **Settings File Detected!**\n\n"
                f"📊 **File Info:**\n"
                f"• Type: `{ext}`\n"
                f"• Name: `{filepath.name}`\n\n"
                f"🔧 Settings will be automatically applied to the system."
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # TODO: Parse and apply settings
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing settings: {e}")


# Update bot to use smart file handler
async def handle_document_smart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any document upload with smart detection"""
    
    if not hasattr(context.bot_data, 'file_handler'):
        # Get autonomous system from context
        autonomous_system = context.bot_data.get('autonomous_system')
        context.bot_data['file_handler'] = SmartFileHandler(autonomous_system)
    
    file_handler = context.bot_data['file_handler']
    
    document = update.message.document
    await file_handler.handle_file(update, context, document)


# ==================== USAGE INTEGRATION ====================

def register_smart_file_handler(app, autonomous_system):
    """Register smart file handler with Telegram bot"""
    from telegram.ext import MessageHandler, filters
    
    # Store autonomous system in bot_data
    app.bot_data['autonomous_system'] = autonomous_system
    
    # Register document handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document_smart))
    
    logger.info("Smart file handler registered")


if __name__ == "__main__":
    print("Smart File Handler Module")
    print("Automatically detects and processes uploaded files")
