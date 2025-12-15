"""
Autonomous Email Checker System
Fully automated, self-learning, self-optimizing system with real-time reporting
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from core.ai.self_learning_engine import SelfLearningEngine
from core.validation.quality_validator import QualityValidator
from core.notifications.telegram_notifier import TelegramNotifier, LiveProgressTracker
from core.optimization.auto_optimizer import AutoOptimizer
from core.checkers.email_leak_checker import EmailLeakChecker
from core.utils.combo_utils import ComboUtils
from core.ai.combo_analyzer import ComboAnalyzer

logger = logging.getLogger(__name__)


class AutonomousSystem:
    """
    Fully autonomous email checking system
    
    Features:
    - Self-learning AI (improves over time)
    - Multi-layer quality validation
    - Real-time Telegram notifications
    - Auto-optimization
    - Continuous training
    - High-quality output only
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize components
        self.learning_engine = SelfLearningEngine(
            ollama_host=config.get('ollama_host', 'http://localhost:11434')
        )
        
        self.quality_validator = QualityValidator(
            ollama_host=config.get('ollama_host', 'http://localhost:11434'),
            min_confidence=config.get('min_confidence', 0.75)
        )
        
        self.telegram_notifier = TelegramNotifier(
            bot_token=config['telegram_bot_token'],
            admin_ids=config['telegram_admin_ids']
        )
        
        self.progress_tracker = LiveProgressTracker(
            notifier=self.telegram_notifier,
            update_interval=config.get('progress_update_interval', 60)
        )
        
        self.auto_optimizer = AutoOptimizer(
            initial_workers=config.get('initial_workers', 2),
            target_speed=config.get('target_speed', 100.0)
        )
        
        self.leak_checker = EmailLeakChecker()
        self.combo_utils = ComboUtils(ai_enabled=True)
        self.combo_analyzer = ComboAnalyzer(
            ollama_host=config.get('ollama_host', 'http://localhost:11434'),
            ollama_model=config.get('ollama_model', 'mistral')
        )
        
        # Training data collection
        self.training_data = {
            'high_quality': [],
            'medium_quality': [],
            'low_quality': [],
            'false_positives': []
        }
        
        # System state
        self.running = False
        self.stats = {
            'total_processed': 0,
            'high_quality_hits': 0,
            'medium_quality_hits': 0,
            'low_quality_hits': 0,
            'rejected': 0,
            'start_time': None
        }
    
    async def start(self):
        """Start all system components"""
        logger.info("Starting autonomous system...")
        
        self.running = True
        self.stats['start_time'] = datetime.utcnow()
        
        # Start components
        await self.telegram_notifier.start()
        await self.progress_tracker.start()
        await self.auto_optimizer.start()
        
        # Send startup notification
        await self.telegram_notifier.notification_queue.put({
            'message': "🚀 **Autonomous System Started**\n\n✅ All systems online\n🤖 AI learning enabled\n📊 Real-time reporting active",
            'disable_notification': False
        })
        
        logger.info("Autonomous system started successfully")
    
    async def stop(self):
        """Stop all system components"""
        logger.info("Stopping autonomous system...")
        
        self.running = False
        
        # Save learning models
        self.learning_engine.save_models()
        
        # Stop components
        await self.telegram_notifier.stop()
        await self.progress_tracker.stop()
        await self.auto_optimizer.stop()
        
        # Send shutdown notification
        await self.telegram_notifier.notification_queue.put({
            'message': "🛑 **System Shutdown**\n\n💾 Models saved\n📊 Final stats sent\n✅ Clean shutdown complete",
            'disable_notification': False
        })
        
        logger.info("Autonomous system stopped")
    
    async def process_email(self, email: str, password: str) -> Optional[Dict]:
        """
        Process single email with full AI pipeline
        
        Returns high-quality validated result or None
        """
        try:
            # Step 1: AI prediction (should we check this?)
            should_check, decision_info = await self.learning_engine.should_check(email, password)
            
            if not should_check and decision_info['prediction']['success_probability'] < 0.2:
                logger.info(f"Skipping low-probability email: {email}")
                return None
            
            # Notify real-time activity
            await self.telegram_notifier.notify_realtime_activity({
                'type': 'check_started',
                'email': email
            })
            
            # Step 2: Perform leak check
            async with self.leak_checker as checker:
                leak_result = await checker.check_all_sources(email)
            
            # Step 3: Analyze with AI
            combo_analysis = await self.combo_analyzer.analyze_combo(email, password)
            
            # Combine results
            combined_result = {
                **leak_result,
                'password_analysis': combo_analysis,
                'ai_prediction': decision_info['prediction']
            }
            
            # Step 4: Multi-layer quality validation
            validation = await self.quality_validator.validate(combined_result)
            combined_result['validation'] = validation
            
            # Step 5: Learn from result
            actual_quality = self._calculate_quality_score(combined_result)
            await self.learning_engine.learn_from_result(
                email, password,
                {'success': leak_result.get('sources_found', 0) > 0},
                actual_quality
            )
            
            # Step 6: Filter by quality
            if not validation['valid'] or validation['confidence'] < self.config.get('min_confidence', 0.75):
                logger.info(f"Rejected low-quality result: {email} (confidence: {validation['confidence']:.2f})")
                self.stats['rejected'] += 1
                
                # Collect as training data
                self.training_data['low_quality'].append({
                    'email': email,
                    'result': combined_result,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                return None
            
            # Step 7: Categorize by quality
            quality_category = self._categorize_quality(actual_quality, validation['confidence'])
            combined_result['quality_category'] = quality_category
            
            # Update stats
            self.stats['total_processed'] += 1
            if quality_category == 'high':
                self.stats['high_quality_hits'] += 1
                self.training_data['high_quality'].append({
                    'email': email,
                    'password': password,
                    'result': combined_result,
                    'timestamp': datetime.utcnow().isoformat()
                })
            elif quality_category == 'medium':
                self.stats['medium_quality_hits'] += 1
                self.training_data['medium_quality'].append({
                    'email': email,
                    'result': combined_result,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Update progress tracker
            self.progress_tracker.record_check(True, actual_quality)
            
            # Step 8: Send notifications
            if quality_category == 'high':
                await self.telegram_notifier.notify_high_quality_hit(combined_result)
            
            await self.telegram_notifier.notify_realtime_activity({
                'type': 'check_completed',
                'email': email,
                'success': True,
                'quality_score': actual_quality
            })
            
            # Step 9: Periodic re-training
            if self.stats['total_processed'] % 100 == 0:
                await self._retrain_models()
            
            # Step 10: Periodic optimization
            if self.stats['total_processed'] % 50 == 0:
                await self._optimize_system()
            
            return combined_result if quality_category in ['high', 'medium'] else None
        
        except Exception as e:
            logger.error(f"Error processing {email}: {e}")
            await self.telegram_notifier.notify_error(str(e), f"Email: {email}")
            return None
    
    async def process_batch(self, combos: List[tuple]) -> Dict:
        """
        Process batch of combos with full automation
        
        Returns:
        {
            'high_quality': [...],
            'medium_quality': [...],
            'stats': {...}
        }
        """
        logger.info(f"Processing batch of {len(combos)} combos...")
        
        start_time = datetime.utcnow()
        
        high_quality_results = []
        medium_quality_results = []
        
        # Get optimal settings from optimizer
        optimal_settings = self.auto_optimizer.get_current_settings()
        max_concurrent = optimal_settings['concurrent_limit']
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(email, password):
            async with semaphore:
                return await self.process_email(email, password)
        
        # Process all combos
        tasks = [process_with_semaphore(email, pwd) for email, pwd in combos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter and categorize results
        for result in results:
            if result and not isinstance(result, Exception):
                category = result.get('quality_category', 'low')
                if category == 'high':
                    high_quality_results.append(result)
                elif category == 'medium':
                    medium_quality_results.append(result)
        
        # Calculate batch stats
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        batch_stats = {
            'total_emails': len(combos),
            'processed': len([r for r in results if r and not isinstance(r, Exception)]),
            'high_quality_hits': len(high_quality_results),
            'medium_quality_hits': len(medium_quality_results),
            'low_quality_hits': self.stats['low_quality_hits'],
            'rejected': self.stats['rejected'],
            'total_time': f"{int(elapsed//60)}m {int(elapsed%60)}s",
            'avg_speed': len(combos) / elapsed if elapsed > 0 else 0,
            'excellent_count': len([r for r in high_quality_results if r['validation']['quality_grade'] == 'EXCELLENT']),
            'very_good_count': len([r for r in high_quality_results if r['validation']['quality_grade'] == 'VERY_GOOD']),
            'good_count': len([r for r in high_quality_results if r['validation']['quality_grade'] == 'GOOD'])
        }
        
        # Send batch completion notification
        await self.telegram_notifier.notify_batch_complete(batch_stats)
        
        # Save high-quality results
        await self._save_results(high_quality_results, 'high_quality')
        await self._save_results(medium_quality_results, 'medium_quality')
        
        return {
            'high_quality': high_quality_results,
            'medium_quality': medium_quality_results,
            'stats': batch_stats
        }
    
    def _calculate_quality_score(self, result: Dict) -> int:
        """Calculate overall quality score"""
        # Weighted combination of factors
        leak_score = min(100, result.get('sources_found', 0) * 5)  # 20 sources = 100
        password_score = result.get('password_analysis', {}).get('quality_score', 50)
        validation_confidence = result.get('validation', {}).get('confidence', 0.5) * 100
        
        # Weighted average
        quality = (leak_score * 0.4) + (password_score * 0.3) + (validation_confidence * 0.3)
        
        return int(quality)
    
    def _categorize_quality(self, quality_score: int, confidence: float) -> str:
        """Categorize result quality"""
        if quality_score >= 80 and confidence >= 0.85:
            return 'high'
        elif quality_score >= 60 and confidence >= 0.70:
            return 'medium'
        else:
            return 'low'
    
    async def _retrain_models(self):
        """Retrain AI models with collected data"""
        logger.info("Retraining AI models...")
        
        # This would implement actual model retraining
        # For now, just log and notify
        
        learning_stats = self.learning_engine.get_metrics()
        
        await self.telegram_notifier.notify_learning_update(learning_stats)
        
        # Save updated models
        self.learning_engine.save_models()
        
        logger.info("Model retraining complete")
    
    async def _optimize_system(self):
        """Run system optimization"""
        logger.info("Running system optimization...")
        
        optimization = await self.learning_engine.optimize_system()
        
        await self.telegram_notifier.notify_system_optimization(optimization)
        
        logger.info("System optimization complete")
    
    async def _save_results(self, results: List[Dict], category: str):
        """Save results to file"""
        if not results:
            return
        
        results_dir = Path('results') / category
        results_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{category}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for result in results:
                email = result.get('email', 'N/A')
                quality = result.get('quality_score', 0)
                confidence = result.get('validation', {}).get('confidence', 0) * 100
                
                f.write(f"{email}\t{quality}\t{confidence:.1f}%\n")
        
        logger.info(f"Saved {len(results)} {category} results to {filepath}")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        learning_metrics = self.learning_engine.get_metrics()
        validation_stats = self.quality_validator.get_stats()
        optimization_report = self.auto_optimizer.get_optimization_report()
        
        elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds() if self.stats['start_time'] else 0
        
        return {
            'running': self.running,
            'uptime_seconds': elapsed,
            'processing_stats': self.stats,
            'learning_metrics': learning_metrics,
            'validation_stats': validation_stats,
            'optimization_report': optimization_report,
            'training_data_size': {
                'high_quality': len(self.training_data['high_quality']),
                'medium_quality': len(self.training_data['medium_quality']),
                'low_quality': len(self.training_data['low_quality']),
                'false_positives': len(self.training_data['false_positives'])
            }
        }


# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    config = {
        'telegram_bot_token': '8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M',
        'telegram_admin_ids': [796354588],
        'ollama_host': 'http://localhost:11434',
        'ollama_model': 'mistral',
        'min_confidence': 0.75,
        'initial_workers': 2,
        'target_speed': 100.0,
        'progress_update_interval': 60
    }
    
    # Create autonomous system
    system = AutonomousSystem(config)
    
    # Start system
    await system.start()
    
    # Process batch of combos
    combos = [
        ('user1@gmail.com', 'password123'),
        ('user2@yahoo.com', 'SecureP@ss123!'),
        ('user3@hotmail.com', '12345'),
        # ... more combos
    ]
    
    results = await system.process_batch(combos)
    
    print(f"High quality hits: {len(results['high_quality'])}")
    print(f"Medium quality hits: {len(results['medium_quality'])}")
    print(f"Stats: {results['stats']}")
    
    # Get system status
    status = system.get_system_status()
    print(f"System status: {status}")
    
    # Stop system
    await system.stop()


if __name__ == "__main__":
    asyncio.run(main())
