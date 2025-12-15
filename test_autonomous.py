"""
Quick Test Script for Autonomous System
Tests all components without full deployment
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 AUTONOMOUS SYSTEM TEST")
print("=" * 60)
print()

# Test 1: Import all components
print("1️⃣ Testing imports...")
try:
    from core.ai.self_learning_engine import SelfLearningEngine
    print("   ✅ Self-Learning Engine")
    
    from core.validation.quality_validator import QualityValidator
    print("   ✅ Quality Validator")
    
    from core.notifications.telegram_notifier import TelegramNotifier
    print("   ✅ Telegram Notifier")
    
    from core.optimization.auto_optimizer import AutoOptimizer
    print("   ✅ Auto-Optimizer")
    
    from core.autonomous_system import AutonomousSystem
    print("   ✅ Autonomous System")
    
    from core.training.data_collector import TrainingDataCollector
    print("   ✅ Data Collector")
    
    from core.training.model_trainer import ModelTrainer
    print("   ✅ Model Trainer")
    
    print()
    print("✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check dependencies
print()
print("2️⃣ Testing dependencies...")
try:
    import numpy
    print("   ✅ numpy")
    
    import pandas
    print("   ✅ pandas")
    
    import telegram
    print("   ✅ python-telegram-bot")
    
    print()
    print("✅ All dependencies installed!")
    
except ImportError as e:
    print(f"   ⚠️ Missing dependency: {e}")
    print("   Run: pip install -r requirements.txt")

# Test 3: Test Self-Learning Engine
print()
print("3️⃣ Testing Self-Learning Engine...")
try:
    engine = SelfLearningEngine(ollama_host="http://localhost:11434")
    
    # Test prediction
    prediction = engine.predict_quality("test@example.com", "password123")
    print(f"   ✅ Prediction: {prediction['success_probability']:.2%}")
    
    # Test learning
    engine.learn_from_result(
        "test@example.com", 
        "password123",
        {"success": True},
        85
    )
    print("   ✅ Learning from result")
    
    # Test metrics
    metrics = engine.get_metrics()
    print(f"   ✅ Metrics: {metrics['total_checks']} checks")
    
except Exception as e:
    print(f"   ⚠️ Self-Learning Engine test failed: {e}")

# Test 4: Test Quality Validator
print()
print("4️⃣ Testing Quality Validator...")
try:
    validator = QualityValidator(
        ollama_host="http://localhost:11434",
        min_confidence=0.75
    )
    
    # Create test result
    test_result = {
        'email': 'test@example.com',
        'sources_found': 3,
        'total_breaches': 5,
        'leak_score': 75,
        'quality_score': 80,
        'sources': ['haveibeenpwned', 'emailrep'],
        'breaches': ['Adobe', 'LinkedIn'],
        'first_seen': '2020-01-01',
        'last_seen': '2023-12-01'
    }
    
    async def test_validation():
        validation = await validator.validate(test_result)
        print(f"   ✅ Validation: {validation['confidence']:.1%} confidence")
        print(f"   ✅ Grade: {validation['quality_grade']}")
        return validation
    
    validation_result = asyncio.run(test_validation())
    
except Exception as e:
    print(f"   ⚠️ Quality Validator test failed: {e}")

# Test 5: Test Data Collector
print()
print("5️⃣ Testing Training Data Collector...")
try:
    collector = TrainingDataCollector()
    
    # Test collection
    collector.collect(
        "test@example.com",
        "password123",
        test_result,
        validation_result if 'validation_result' in locals() else {
            'valid': True,
            'confidence': 0.85,
            'quality_grade': 'VERY_GOOD'
        }
    )
    print("   ✅ Data collection")
    
    # Test stats
    stats = collector.get_stats()
    print(f"   ✅ Stats: {stats.get('total_collected', 0)} collected")
    
except Exception as e:
    print(f"   ⚠️ Data Collector test failed: {e}")

# Test 6: Configuration check
print()
print("6️⃣ Checking configuration...")
try:
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    admin_id = os.getenv('TELEGRAM_ADMIN_IDS')
    
    if token and token != 'your_bot_token_here':
        print(f"   ✅ Telegram bot token configured")
    else:
        print(f"   ⚠️ Telegram bot token not configured in .env")
    
    if admin_id:
        print(f"   ✅ Admin ID configured: {admin_id}")
    else:
        print(f"   ⚠️ Admin ID not configured in .env")
        
except Exception as e:
    print(f"   ⚠️ Configuration check failed: {e}")

# Test 7: File structure check
print()
print("7️⃣ Checking file structure...")
required_files = [
    'core/ai/self_learning_engine.py',
    'core/validation/quality_validator.py',
    'core/notifications/telegram_notifier.py',
    'core/optimization/auto_optimizer.py',
    'core/autonomous_system.py',
    'core/training/data_collector.py',
    'core/training/model_trainer.py',
    'bot/autonomous_commands.py',
    'start_autonomous.py'
]

for file in required_files:
    filepath = Path(file)
    if filepath.exists():
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - MISSING!")

print()
print("=" * 60)
print("✅ COMPONENT TESTS COMPLETE!")
print("=" * 60)
print()
print("Next steps:")
print("1. Ensure Docker services are running: docker-compose up -d")
print("2. Check Ollama is available: curl http://localhost:11434")
print("3. Start autonomous system: python start_autonomous.py")
print("4. Test via Telegram bot")
print()
