"""
Complete Example: Autonomous Email Checking

This example shows the complete workflow:
1. Load combo file
2. Start autonomous system
3. Process with ML learning
4. Validate quality
5. Get real-time notifications
6. Train models
7. Export results
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from core.autonomous_system import AutonomousSystem
from core.training.data_collector import TrainingDataCollector
from core.training.model_trainer import ModelTrainer


async def example_autonomous_scan():
    """
    Complete autonomous scan example
    """
    
    # Load environment
    load_dotenv()
    
    # Configuration
    config = {
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'telegram_admin_ids': [int(os.getenv('TELEGRAM_ADMIN_IDS'))],
        'ollama_host': 'http://localhost:11434',
        'ollama_model': 'mistral',
        'min_confidence': 0.75,  # 75% minimum confidence
        'initial_workers': 2,
        'target_speed': 100.0,
        'progress_update_interval': 60  # Update every 60 seconds
    }
    
    print("🤖 AUTONOMOUS EMAIL CHECKER")
    print("=" * 60)
    print()
    
    # Initialize system
    print("1️⃣ Initializing autonomous system...")
    system = AutonomousSystem(config)
    await system.start()
    print("   ✅ System started")
    print()
    
    # Load combos from file
    print("2️⃣ Loading combo file...")
    combo_file = Path('test_combos.txt')
    
    combos = []
    if combo_file.exists():
        with open(combo_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    email, password = line.split(':', 1)
                    combos.append((email, password))
        print(f"   ✅ Loaded {len(combos)} combos")
    else:
        # Example combos
        combos = [
            ('test1@gmail.com', 'password123'),
            ('test2@yahoo.com', 'SecurePass!2024'),
            ('test3@hotmail.com', 'qwerty'),
            ('test4@outlook.com', 'MyP@ssw0rd'),
            ('test5@gmail.com', '12345678')
        ]
        print(f"   ℹ️ Using {len(combos)} example combos")
    print()
    
    # Process batch with autonomous system
    print("3️⃣ Starting autonomous processing...")
    print("   🧠 AI learning enabled")
    print("   ✅ Quality validation active")
    print("   📱 Real-time notifications on")
    print("   ⚙️ Auto-optimization running")
    print()
    
    results = await system.process_batch(combos)
    
    # Display results
    print()
    print("4️⃣ Processing complete!")
    print("=" * 60)
    print()
    print(f"📊 Results Summary:")
    print(f"   • Total Emails: {results['stats']['total_emails']:,}")
    print(f"   • High Quality Hits: {len(results['high_quality']):,}")
    print(f"   • Medium Quality Hits: {len(results['medium_quality']):,}")
    print(f"   • Rejected: {results['stats']['rejected']:,}")
    print()
    print(f"⏱️ Performance:")
    print(f"   • Time: {results['stats']['total_time']}")
    print(f"   • Speed: {results['stats']['avg_speed']:.1f} emails/sec")
    print()
    print(f"🎯 Quality Breakdown:")
    print(f"   • Excellent: {results['stats']['excellent_count']}")
    print(f"   • Very Good: {results['stats']['very_good_count']}")
    print(f"   • Good: {results['stats']['good_count']}")
    print()
    
    # Show some high-quality hits
    if results['high_quality']:
        print("🏆 Top High-Quality Hits:")
        print()
        for i, hit in enumerate(results['high_quality'][:3], 1):
            print(f"   {i}. {hit['email']}")
            print(f"      Quality: {hit['quality_score']}/100")
            print(f"      Grade: {hit['validation']['quality_grade']}")
            print(f"      Confidence: {hit['validation']['confidence']:.1%}")
            print(f"      Breaches: {hit.get('total_breaches', 0)}")
            print()
    
    # Get system status
    print("5️⃣ System Status:")
    print("=" * 60)
    status = system.get_system_status()
    
    learning = status['learning_metrics']
    print(f"🧠 Machine Learning:")
    print(f"   • Accuracy: {learning.get('accuracy', 0):.1%}")
    print(f"   • Precision: {learning.get('precision', 0):.1%}")
    print(f"   • Patterns Learned: {learning.get('patterns_learned', 0):,}")
    print(f"   • Learning Iterations: {learning.get('learning_iterations', 0):,}")
    print()
    
    validation = status['validation_stats']
    print(f"✅ Quality Validation:")
    print(f"   • Pass Rate: {validation.get('pass_rate', 0):.1%}")
    print(f"   • Avg Confidence: {validation.get('avg_confidence', 0):.1%}")
    print()
    
    # Stop system
    print("6️⃣ Shutting down...")
    await system.stop()
    print("   ✅ System stopped gracefully")
    print()
    print("=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)


async def example_model_training():
    """
    Example: Train models with collected data
    """
    
    print()
    print("🧠 MODEL TRAINING EXAMPLE")
    print("=" * 60)
    print()
    
    trainer = ModelTrainer()
    
    print("1️⃣ Loading training data (last 30 days)...")
    df = trainer.load_training_data(days=30)
    print(f"   ✅ Loaded {len(df)} records")
    print()
    
    print("2️⃣ Training pattern learner...")
    pattern_metrics = trainer.train_pattern_learner(df)
    print(f"   ✅ Learned {pattern_metrics.get('patterns_learned', 0)} patterns")
    print()
    
    print("3️⃣ Training Q-learner...")
    q_metrics = trainer.train_q_learner(df)
    print(f"   ✅ Processed {q_metrics.get('experiences_processed', 0)} experiences")
    print()
    
    print("4️⃣ Evaluating models...")
    eval_metrics = trainer.evaluate_models(df)
    print(f"   ✅ Accuracy: {eval_metrics.get('accuracy', 0):.1%}")
    print(f"   ✅ Quality Error: {eval_metrics.get('mean_quality_error', 0):.1f}")
    print()
    
    print("5️⃣ Deploying models...")
    deployed = trainer.deploy_models(eval_metrics)
    if deployed:
        print("   ✅ Models deployed successfully")
    else:
        print("   ⚠️ Models rolled back (no improvement)")
    print()
    
    print("6️⃣ Improvement trend...")
    trend = trainer.get_improvement_trend()
    print(f"   • Current Accuracy: {trend.get('current_accuracy', 0):.1%}")
    print(f"   • Recent Average: {trend.get('recent_average', 0):.1%}")
    print(f"   • Trend: {trend.get('trend', 'unknown').upper()}")
    print()
    
    print("=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)


async def example_export_training_data():
    """
    Example: Export training data
    """
    
    print()
    print("📦 EXPORT TRAINING DATA EXAMPLE")
    print("=" * 60)
    print()
    
    collector = TrainingDataCollector()
    
    print("1️⃣ Collecting statistics...")
    stats = collector.get_stats()
    print(f"   Total Collected: {stats.get('total_collected', 0):,}")
    print()
    
    print("2️⃣ Quality distribution...")
    distribution = collector.get_quality_distribution()
    for quality, count in sorted(distribution.items()):
        print(f"   {quality.title()}: {count:,}")
    print()
    
    print("3️⃣ Exporting dataset...")
    print("   • Period: Last 7 days")
    print("   • Min Quality: Good")
    print("   • Format: CSV")
    export_path = collector.export_dataset(
        days=7,
        min_quality='good',
        format='csv'
    )
    print(f"   ✅ Exported to: {export_path}")
    print()
    
    print("=" * 60)
    print("✅ EXPORT COMPLETE!")
    print("=" * 60)


async def main():
    """
    Run all examples
    """
    
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║  AUTONOMOUS EMAIL CHECKER - COMPLETE EXAMPLES          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    # Example 1: Autonomous scan
    await example_autonomous_scan()
    
    # Example 2: Model training
    await example_model_training()
    
    # Example 3: Export training data
    await example_export_training_data()
    
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║  ALL EXAMPLES COMPLETED SUCCESSFULLY! 🎉               ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    asyncio.run(main())
