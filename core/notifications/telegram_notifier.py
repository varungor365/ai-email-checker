"""
Real-Time Telegram Notifications System
Live progress updates, quality metrics, instant hit reporting
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
import json

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Real-time notification system for Telegram
    
    Features:
    - Live progress updates
    - Instant hit notifications
    - Quality metrics reporting
    - System status alerts
    - Learning progress updates
    """
    
    def __init__(self, bot_token: str, admin_ids: List[int]):
        self.bot = Bot(token=bot_token)
        self.admin_ids = admin_ids
        self.notification_queue = asyncio.Queue()
        self.running = False
    
    async def start(self):
        """Start notification worker"""
        self.running = True
        asyncio.create_task(self._notification_worker())
        logger.info("Telegram notifier started")
    
    async def stop(self):
        """Stop notification worker"""
        self.running = False
    
    async def _notification_worker(self):
        """Process notification queue"""
        while self.running:
            try:
                notification = await asyncio.wait_for(
                    self.notification_queue.get(),
                    timeout=1.0
                )
                
                await self._send_notification(notification)
            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Notification worker error: {e}")
    
    async def _send_notification(self, notification: Dict):
        """Send notification to admins"""
        message = notification.get('message', '')
        parse_mode = notification.get('parse_mode', ParseMode.MARKDOWN)
        disable_notification = notification.get('disable_notification', False)
        
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode=parse_mode,
                    disable_notification=disable_notification
                )
            except Exception as e:
                logger.error(f"Failed to send notification to {admin_id}: {e}")
    
    async def notify_high_quality_hit(self, result: Dict):
        """Notify about high-quality hit immediately"""
        validation = result.get('validation', {})
        confidence = validation.get('confidence', 0) * 100
        quality_grade = validation.get('quality_grade', 'N/A')
        
        message = f"""
🎯 **HIGH QUALITY HIT!**

📧 **Email**: `{result.get('email', 'N/A')}`
🔐 **Password**: `{'*' * 10}`
⭐ **Quality**: {result.get('quality_score', 0)}/100
🎖️ **Grade**: {quality_grade}
📊 **Confidence**: {confidence:.1f}%

🗃️ **Breaches Found**: {len(result.get('breaches', []))}
{self._format_breaches(result.get('breaches', [])[:3])}

🔍 **Sources**: {result.get('sources_found', 0)}/{result.get('total_sources', 0)}

⏰ **Time**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

✅ **Validation**: {validation.get('recommendation', 'Validated')}
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': False
        })
    
    async def notify_scan_progress(self, stats: Dict):
        """Send progress update"""
        message = f"""
📊 **Scan Progress Update**

⏱️ **Running Time**: {stats.get('running_time', 'N/A')}
📧 **Emails Processed**: {stats.get('total_processed', 0):,}
✅ **Hits Found**: {stats.get('hits_found', 0):,}
❌ **Failed**: {stats.get('failed', 0):,}

📈 **Success Rate**: {stats.get('success_rate', 0):.1f}%
🎯 **Quality Rate**: {stats.get('quality_rate', 0):.1f}%

⚡ **Speed**: {stats.get('speed', 0):.1f} emails/sec
🔄 **Active Workers**: {stats.get('active_workers', 0)}

🤖 **AI Learning**: {stats.get('learning_iterations', 0)} iterations
📚 **Patterns Learned**: {stats.get('patterns_learned', 0):,}

💾 **Cache Hit Rate**: {stats.get('cache_hit_rate', 0):.1f}%
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': True
        })
    
    async def notify_quality_metrics(self, metrics: Dict):
        """Send quality metrics update"""
        message = f"""
📊 **Quality Metrics Report**

🎯 **Validation Statistics**:
✅ Pass Rate: {metrics.get('pass_rate', 0) * 100:.1f}%
📋 Total Validations: {metrics.get('total_validations', 0):,}
✔️ Passed: {metrics.get('passed_validations', 0):,}
✖️ Failed: {metrics.get('failed_validations', 0):,}

📈 **Quality Distribution**:
⭐⭐⭐⭐⭐ Excellent: {metrics.get('excellent', 0):,}
⭐⭐⭐⭐ Very Good: {metrics.get('very_good', 0):,}
⭐⭐⭐ Good: {metrics.get('good', 0):,}
⭐⭐ Acceptable: {metrics.get('acceptable', 0):,}
⭐ Questionable: {metrics.get('questionable', 0):,}

🤖 **AI Performance**:
🎓 Accuracy: {metrics.get('accuracy', 0) * 100:.1f}%
🎯 Precision: {metrics.get('precision', 0) * 100:.1f}%
🧠 Patterns: {metrics.get('patterns_learned', 0):,}
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': True
        })
    
    async def notify_learning_update(self, learning_stats: Dict):
        """Notify about AI learning progress"""
        message = f"""
🧠 **AI Learning Update**

📚 **Training Progress**:
Iterations: {learning_stats.get('learning_iterations', 0):,}
Experience Size: {learning_stats.get('experience_size', 0):,}
Q-Table Size: {learning_stats.get('q_table_size', 0):,}

📊 **Performance Improvement**:
Current Accuracy: {learning_stats.get('accuracy', 0) * 100:.1f}%
Current Precision: {learning_stats.get('precision', 0) * 100:.1f}%
Exploration Rate: {learning_stats.get('exploration_rate', 0) * 100:.1f}%

✅ **Results**:
Total Checks: {learning_stats.get('total_checks', 0):,}
Successful: {learning_stats.get('successful_checks', 0):,}
High Quality: {learning_stats.get('high_quality_hits', 0):,}

🎯 **Recommendations**:
{self._format_recommendations(learning_stats.get('recommendations', []))}

💾 Models saved successfully!
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': True
        })
    
    async def notify_system_optimization(self, optimization: Dict):
        """Notify about system optimization"""
        optimal_settings = optimization.get('optimal_settings', {})
        
        message = f"""
⚙️ **System Optimization Update**

🔧 **Optimal Settings Applied**:
👥 Workers: {optimal_settings.get('worker_count', 2)}
🔄 Concurrent Limit: {optimal_settings.get('concurrent_limit', 50)}
🎯 Quality Threshold: {optimal_settings.get('quality_threshold', 70)}%

📈 **Performance Impact**:
Expected Speed: +{optimization.get('speed_improvement', 0):.1f}%
Expected Accuracy: +{optimization.get('accuracy_improvement', 0):.1f}%

✅ System optimized for maximum efficiency!
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': True
        })
    
    async def notify_error(self, error: str, context: str = ""):
        """Notify about system error"""
        message = f"""
❌ **System Error**

**Error**: {error}

{f'**Context**: {context}' if context else ''}

**Time**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Please check system logs for details.
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': False
        })
    
    async def notify_batch_complete(self, batch_stats: Dict):
        """Notify about batch completion"""
        message = f"""
✅ **Batch Scan Complete!**

📊 **Summary**:
Total Emails: {batch_stats.get('total_emails', 0):,}
Processed: {batch_stats.get('processed', 0):,}
High Quality Hits: {batch_stats.get('high_quality_hits', 0):,}
Medium Quality: {batch_stats.get('medium_quality_hits', 0):,}
Low Quality: {batch_stats.get('low_quality_hits', 0):,}

⏱️ **Time**: {batch_stats.get('total_time', 'N/A')}
⚡ **Avg Speed**: {batch_stats.get('avg_speed', 0):.1f} emails/sec

🎯 **Quality Breakdown**:
⭐⭐⭐⭐⭐ Excellent: {batch_stats.get('excellent_count', 0)}
⭐⭐⭐⭐ Very Good: {batch_stats.get('very_good_count', 0)}
⭐⭐⭐ Good: {batch_stats.get('good_count', 0)}

📁 **Download**: Use /download to get results
"""
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': False
        })
    
    async def notify_realtime_activity(self, activity: Dict):
        """Send real-time activity update"""
        activity_type = activity.get('type', 'unknown')
        
        if activity_type == 'check_started':
            message = f"🔍 Checking: `{activity.get('email', 'N/A')}`"
        
        elif activity_type == 'check_completed':
            emoji = "✅" if activity.get('success') else "❌"
            message = f"{emoji} Completed: `{activity.get('email', 'N/A')}` - Quality: {activity.get('quality_score', 0)}/100"
        
        elif activity_type == 'worker_scaled':
            message = f"🔄 Workers scaled to {activity.get('count', 0)}"
        
        elif activity_type == 'learning_iteration':
            message = f"🧠 Learning iteration #{activity.get('iteration', 0)} completed"
        
        else:
            message = f"ℹ️ {activity.get('message', 'Activity update')}"
        
        await self.notification_queue.put({
            'message': message,
            'parse_mode': ParseMode.MARKDOWN,
            'disable_notification': True
        })
    
    def _format_breaches(self, breaches: List[Dict]) -> str:
        """Format breach list"""
        if not breaches:
            return ""
        
        formatted = []
        for breach in breaches:
            name = breach.get('name', 'Unknown')
            date = breach.get('date', 'Unknown date')
            formatted.append(f"  • {name} ({date})")
        
        return '\n'.join(formatted)
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations list"""
        if not recommendations:
            return "  • System performing optimally"
        
        return '\n'.join([f"  • {rec}" for rec in recommendations[:5]])


class LiveProgressTracker:
    """Track and report live progress"""
    
    def __init__(self, notifier: TelegramNotifier, update_interval: int = 60):
        self.notifier = notifier
        self.update_interval = update_interval
        self.stats = {
            'start_time': None,
            'total_processed': 0,
            'hits_found': 0,
            'high_quality_hits': 0,
            'failed': 0,
            'last_update': None
        }
        self.running = False
    
    async def start(self):
        """Start progress tracking"""
        self.stats['start_time'] = datetime.utcnow()
        self.stats['last_update'] = datetime.utcnow()
        self.running = True
        
        asyncio.create_task(self._progress_updater())
        logger.info("Live progress tracker started")
    
    async def stop(self):
        """Stop progress tracking"""
        self.running = False
    
    async def _progress_updater(self):
        """Periodically send progress updates"""
        while self.running:
            await asyncio.sleep(self.update_interval)
            
            # Calculate stats
            elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds()
            speed = self.stats['total_processed'] / elapsed if elapsed > 0 else 0
            success_rate = (self.stats['hits_found'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
            quality_rate = (self.stats['high_quality_hits'] / self.stats['hits_found'] * 100) if self.stats['hits_found'] > 0 else 0
            
            progress_stats = {
                'running_time': str(timedelta(seconds=int(elapsed))),
                'total_processed': self.stats['total_processed'],
                'hits_found': self.stats['hits_found'],
                'failed': self.stats['failed'],
                'success_rate': success_rate,
                'quality_rate': quality_rate,
                'speed': speed,
                'active_workers': 0,  # Updated by system
                'learning_iterations': 0,  # Updated by learning engine
                'patterns_learned': 0,  # Updated by learning engine
                'cache_hit_rate': 0  # Updated by cache system
            }
            
            await self.notifier.notify_scan_progress(progress_stats)
            self.stats['last_update'] = datetime.utcnow()
    
    def record_check(self, success: bool, quality_score: int):
        """Record a check result"""
        self.stats['total_processed'] += 1
        
        if success:
            self.stats['hits_found'] += 1
            
            if quality_score >= 70:
                self.stats['high_quality_hits'] += 1
        else:
            self.stats['failed'] += 1
    
    def get_current_stats(self) -> Dict:
        """Get current statistics"""
        elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds() if self.stats['start_time'] else 0
        
        return {
            **self.stats,
            'elapsed_seconds': elapsed,
            'speed': self.stats['total_processed'] / elapsed if elapsed > 0 else 0
        }


# ==================== USAGE EXAMPLE ====================

from datetime import timedelta

async def main():
    """Example usage"""
    # Initialize notifier
    notifier = TelegramNotifier(
        bot_token="YOUR_BOT_TOKEN",
        admin_ids=[123456789]
    )
    
    await notifier.start()
    
    # High quality hit notification
    result = {
        'email': 'test@example.com',
        'quality_score': 95,
        'validation': {
            'confidence': 0.98,
            'quality_grade': 'EXCELLENT',
            'recommendation': 'ACCEPT - High confidence result'
        },
        'breaches': [
            {'name': 'LinkedIn', 'date': '2012-05-05'},
            {'name': 'Adobe', 'date': '2013-10-04'}
        ],
        'sources_found': 15,
        'total_sources': 30
    }
    
    await notifier.notify_high_quality_hit(result)
    
    # Progress update
    await notifier.notify_scan_progress({
        'running_time': '00:15:30',
        'total_processed': 1500,
        'hits_found': 450,
        'failed': 1050,
        'success_rate': 30.0,
        'quality_rate': 85.0,
        'speed': 100.0,
        'active_workers': 5,
        'learning_iterations': 150,
        'patterns_learned': 1250,
        'cache_hit_rate': 75.0
    })
    
    # Wait for notifications to be sent
    await asyncio.sleep(2)
    
    await notifier.stop()


if __name__ == "__main__":
    asyncio.run(main())
