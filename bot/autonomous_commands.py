"""
Updated Telegram Bot with Full Autonomous System Integration
Adds ML status, training controls, quality reports, and optimization commands
"""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.constants import ParseMode
import json
from datetime import datetime


class AutonomousBotCommands:
    """New commands for autonomous system control"""
    
    def __init__(self, autonomous_system):
        self.system = autonomous_system
    
    async def cmd_ml_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show ML learning metrics"""
        try:
            learning_metrics = self.system.learning_engine.get_metrics()
            
            message = "🤖 **Machine Learning Status**\n\n"
            message += f"📊 **Learning Metrics:**\n"
            message += f"• Accuracy: {learning_metrics.get('accuracy', 0):.1%}\n"
            message += f"• Precision: {learning_metrics.get('precision', 0):.1%}\n"
            message += f"• Total Checks: {learning_metrics.get('total_checks', 0):,}\n"
            message += f"• High Quality Hits: {learning_metrics.get('high_quality_hits', 0):,}\n"
            message += f"• Learning Iterations: {learning_metrics.get('learning_iterations', 0):,}\n\n"
            
            message += f"🧠 **Model State:**\n"
            message += f"• Patterns Learned: {learning_metrics.get('patterns_learned', 0):,}\n"
            message += f"• Q-Table Size: {learning_metrics.get('q_table_size', 0):,}\n"
            message += f"• Experience Buffer: {learning_metrics.get('experience_size', 0):,}/50,000\n"
            message += f"• Exploration Rate: {learning_metrics.get('epsilon', 0.2):.2%}\n\n"
            
            message += f"📈 **Performance:**\n"
            message += f"• Avg Prediction Confidence: {learning_metrics.get('avg_confidence', 0):.1%}\n"
            message += f"• Success Rate: {learning_metrics.get('success_rate', 0):.1%}\n"
            message += f"• False Positive Rate: {learning_metrics.get('false_positive_rate', 0):.1%}\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_quality_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show quality validation statistics"""
        try:
            validation_stats = self.system.quality_validator.get_stats()
            
            message = "✅ **Quality Validation Report**\n\n"
            message += f"📊 **Overall:**\n"
            message += f"• Total Validations: {validation_stats.get('total_validations', 0):,}\n"
            message += f"• Pass Rate: {validation_stats.get('pass_rate', 0):.1%}\n"
            message += f"• Average Confidence: {validation_stats.get('avg_confidence', 0):.1%}\n\n"
            
            message += f"🎯 **Quality Distribution:**\n"
            quality_dist = validation_stats.get('quality_distribution', {})
            message += f"• Excellent: {quality_dist.get('excellent', 0):,}\n"
            message += f"• Very Good: {quality_dist.get('very_good', 0):,}\n"
            message += f"• Good: {quality_dist.get('good', 0):,}\n"
            message += f"• Acceptable: {quality_dist.get('acceptable', 0):,}\n"
            message += f"• Questionable: {quality_dist.get('questionable', 0):,}\n"
            message += f"• Poor: {quality_dist.get('poor', 0):,}\n\n"
            
            message += f"🔍 **Validation Layers:**\n"
            layer_failures = validation_stats.get('layer_failures', {})
            for layer, count in layer_failures.items():
                message += f"• {layer.title()}: {count} failures\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_train(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trigger manual model retraining"""
        try:
            await update.message.reply_text("🔄 Starting model retraining...\n\nThis may take a few minutes.")
            
            from core.training.model_trainer import ModelTrainer
            trainer = ModelTrainer()
            
            # Get training period from args
            days = int(context.args[0]) if context.args else 30
            
            report = trainer.train_and_deploy(days=days)
            
            if 'error' in report:
                await update.message.reply_text(f"❌ Training failed: {report['error']}")
                return
            
            message = "✅ **Model Retraining Complete**\n\n"
            message += f"📊 **Training Data:**\n"
            message += f"• Samples Used: {report.get('training_samples', 0):,}\n"
            message += f"• Time Period: {days} days\n\n"
            
            message += f"🧠 **Pattern Learner:**\n"
            pattern_metrics = report.get('pattern_learner', {})
            message += f"• Patterns Learned: {pattern_metrics.get('patterns_learned', 0):,}\n\n"
            
            message += f"🎯 **Q-Learner:**\n"
            q_metrics = report.get('q_learner', {})
            message += f"• States Learned: {q_metrics.get('states_learned', 0):,}\n"
            message += f"• Experiences: {q_metrics.get('experiences_processed', 0):,}\n\n"
            
            message += f"📈 **Evaluation:**\n"
            eval_metrics = report.get('evaluation', {})
            message += f"• Accuracy: {eval_metrics.get('accuracy', 0):.1%}\n"
            message += f"• Quality Error: {eval_metrics.get('mean_quality_error', 0):.1f}\n\n"
            
            message += f"🚀 **Deployment:**\n"
            message += f"• Status: {'✅ Deployed' if report.get('deployed') else '❌ Rolled Back'}\n"
            message += f"• Training Time: {report.get('training_time', 'N/A')}\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_optimize(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show optimization recommendations"""
        try:
            optimization = await self.system.learning_engine.optimize_system()
            
            message = "⚙️ **System Optimization**\n\n"
            message += f"📊 **Current Performance:**\n"
            message += f"• Accuracy: {optimization.get('current_metrics', {}).get('accuracy', 0):.1%}\n"
            message += f"• Speed: {optimization.get('current_metrics', {}).get('avg_speed', 0):.1f} emails/sec\n"
            message += f"• Success Rate: {optimization.get('current_metrics', {}).get('success_rate', 0):.1%}\n\n"
            
            message += f"💡 **Recommendations:**\n"
            for rec in optimization.get('recommendations', []):
                message += f"• {rec}\n"
            
            # Apply optimizations?
            keyboard = [[
                InlineKeyboardButton("✅ Apply", callback_data="optimize_apply"),
                InlineKeyboardButton("❌ Cancel", callback_data="optimize_cancel")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_autonomous_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show full autonomous system status"""
        try:
            status = self.system.get_system_status()
            
            message = "🤖 **Autonomous System Status**\n\n"
            
            # System state
            uptime = status.get('uptime_seconds', 0)
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            message += f"⚡ **System:**\n"
            message += f"• Status: {'🟢 Running' if status.get('running') else '🔴 Stopped'}\n"
            message += f"• Uptime: {hours}h {minutes}m\n\n"
            
            # Processing stats
            proc_stats = status.get('processing_stats', {})
            message += f"📊 **Processing:**\n"
            message += f"• Total Processed: {proc_stats.get('total_processed', 0):,}\n"
            message += f"• High Quality: {proc_stats.get('high_quality_hits', 0):,}\n"
            message += f"• Medium Quality: {proc_stats.get('medium_quality_hits', 0):,}\n"
            message += f"• Rejected: {proc_stats.get('rejected', 0):,}\n\n"
            
            # Learning metrics
            learning = status.get('learning_metrics', {})
            message += f"🧠 **Learning:**\n"
            message += f"• Accuracy: {learning.get('accuracy', 0):.1%}\n"
            message += f"• Iterations: {learning.get('learning_iterations', 0):,}\n\n"
            
            # Optimization
            optimization = status.get('optimization_report', {})
            message += f"⚙️ **Optimization:**\n"
            message += f"• Workers: {optimization.get('current_settings', {}).get('workers', 0)}\n"
            message += f"• Concurrent: {optimization.get('current_settings', {}).get('concurrent_limit', 0)}\n\n"
            
            # Training data
            training_data = status.get('training_data_size', {})
            total_training = sum(training_data.values())
            message += f"📚 **Training Data:**\n"
            message += f"• Total Samples: {total_training:,}\n"
            message += f"• High Quality: {training_data.get('high_quality', 0):,}\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_export_training_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export training dataset"""
        try:
            from core.training.data_collector import TrainingDataCollector
            
            await update.message.reply_text("📦 Exporting training data...")
            
            collector = TrainingDataCollector()
            
            # Get parameters from args
            days = int(context.args[0]) if len(context.args) > 0 else 7
            min_quality = context.args[1] if len(context.args) > 1 else 'good'
            format = context.args[2] if len(context.args) > 2 else 'csv'
            
            export_path = collector.export_dataset(
                days=days,
                min_quality=min_quality,
                format=format
            )
            
            # Get stats
            distribution = collector.get_quality_distribution()
            total_records = sum(distribution.values())
            
            message = "✅ **Training Data Exported**\n\n"
            message += f"📊 **Export Details:**\n"
            message += f"• File: `{export_path.name}`\n"
            message += f"• Format: {format.upper()}\n"
            message += f"• Time Period: {days} days\n"
            message += f"• Min Quality: {min_quality.title()}\n\n"
            
            message += f"📈 **Quality Distribution:**\n"
            for quality, count in sorted(distribution.items()):
                pct = (count / total_records * 100) if total_records > 0 else 0
                message += f"• {quality.title()}: {count:,} ({pct:.1f}%)\n"
            
            message += f"\n📦 Total Records: {total_records:,}"
            
            # Upload file
            await update.message.reply_document(
                document=open(export_path, 'rb'),
                caption=message,
                parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_start_autonomous(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start autonomous mode with uploaded combo file"""
        try:
            # Check if file was uploaded
            if not hasattr(context, 'last_uploaded_file'):
                await update.message.reply_text(
                    "⚠️ Please upload a combo file first using /upload or by sending a .txt file"
                )
                return
            
            await update.message.reply_text(
                "🚀 Starting autonomous processing...\n\n"
                "✅ AI learning enabled\n"
                "✅ Quality validation active\n"
                "✅ Real-time reporting on\n"
                "✅ Auto-optimization enabled"
            )
            
            # Load combos from file
            combos = []
            with open(context.last_uploaded_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        combos.append((parts[0], parts[1]))
            
            # Process with autonomous system
            results = await self.system.process_batch(combos)
            
            # Results notification is handled by autonomous system
            await update.message.reply_text(
                f"✅ **Autonomous Processing Complete**\n\n"
                f"See batch completion message above for full results!"
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    def register_handlers(self, app):
        """Register all new command handlers"""
        app.add_handler(CommandHandler("ml_status", self.cmd_ml_status))
        app.add_handler(CommandHandler("quality_report", self.cmd_quality_report))
        app.add_handler(CommandHandler("train", self.cmd_train))
        app.add_handler(CommandHandler("optimize", self.cmd_optimize))
        app.add_handler(CommandHandler("autonomous_status", self.cmd_autonomous_status))
        app.add_handler(CommandHandler("export_training", self.cmd_export_training_data))
        app.add_handler(CommandHandler("auto_scan", self.cmd_start_autonomous))


# Update help command to include new commands
AUTONOMOUS_HELP_TEXT = """
🤖 **Autonomous System Commands:**

/ml_status - Show ML learning metrics
/quality_report - Quality validation statistics
/train [days] - Retrain models (default: 30 days)
/optimize - Get optimization recommendations
/autonomous_status - Full system status
/export_training [days] [quality] [format] - Export training data
/auto_scan - Start autonomous processing (upload file first)

**Examples:**
`/train 14` - Retrain with last 14 days
`/export_training 7 good csv` - Export good+ quality from last week
`/auto_scan` - Process uploaded file with full AI pipeline

**Autonomous Features:**
✅ Self-learning AI (improves over time)
✅ 6-layer quality validation
✅ Real-time Telegram notifications
✅ Automatic optimization
✅ Continuous model retraining
✅ High-quality output only (min 75% confidence)
"""


if __name__ == "__main__":
    print("Autonomous Bot Commands Module")
    print("Import this into main bot to add autonomous features")
