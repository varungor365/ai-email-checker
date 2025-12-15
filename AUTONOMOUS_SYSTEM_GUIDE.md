# Autonomous Self-Learning Email Checker System

## 🚀 Complete Integration Guide

**Version:** 2.0 - Fully Autonomous with ML Self-Learning

### System Overview

This is a **fully autonomous, self-learning email checking system** that:

✅ **Learns from every check result** (Reinforcement Learning with Q-learning)  
✅ **Validates quality with 6 layers** (Format, Consistency, Source, CrossReference, Historical, AI)  
✅ **Reports everything real-time to Telegram** (Instant alerts, 60-second progress updates)  
✅ **Optimizes itself continuously** (Worker scaling, API tuning, cache optimization)  
✅ **Trains itself and gets stronger** (Automatic model retraining, performance improvement tracking)  
✅ **Provides only high-quality, correct hits** (Minimum 75% confidence, strict validation)

---

## 📦 Components Created

### 1. **Self-Learning Engine** (`core/ai/self_learning_engine.py`)
- **Reinforcement Learning:** Q-learning algorithm (lr=0.1, gamma=0.95)
- **Pattern Learning:** Learns password patterns, email domains, success probabilities
- **Experience Replay:** 50,000-record memory buffer for batch learning
- **Decision Making:** Intelligent check/skip decisions based on learned patterns
- **Model Persistence:** Automatic save/load every 10 iterations
- **Metrics Tracking:** Accuracy, precision, learning iterations, confidence scores

**Key Methods:**
```python
predict_quality(email, password)  # Predict before checking
learn_from_result(email, password, result, quality)  # Learn after checking
should_check(email, password)  # Decide: check or skip?
optimize_system()  # Get optimization recommendations
get_metrics()  # Get learning metrics
```

### 2. **Quality Validator** (`core/validation/quality_validator.py`)
- **6 Validation Layers:**
  1. **FormatValidator** (weight: 0.5) - Email format, timestamps, required fields
  2. **ConsistencyValidator** (weight: 0.8) - Internal consistency checks
  3. **SourceValidator** (weight: 1.0) - Credibility scoring (HIBP: 1.0, EmailRep: 0.9)
  4. **CrossReferenceValidator** (weight: 1.2) - Multi-source agreement
  5. **HistoricalValidator** (weight: 0.7) - Past result consistency
  6. **AIValidator** (weight: 1.5) - Ollama-powered strict validation

- **Weighted Confidence:** Total confidence = Σ(layer_confidence × layer_weight) / Σ(layer_weight)
- **Quality Grades:** EXCELLENT (95%+), VERY_GOOD (85%+), GOOD (75%+), ACCEPTABLE (65%+), QUESTIONABLE (50%+), POOR (<50%)
- **Minimum Confidence:** 75% to pass validation (configurable)

**Key Methods:**
```python
validate(result)  # Validate single result (6 layers)
batch_validate(results)  # Validate up to 20 concurrently
get_high_quality_only(results)  # Filter to confidence >= 80%
get_stats()  # Validation statistics
```

### 3. **Telegram Notifier** (`core/notifications/telegram_notifier.py`)
- **Async Notification Queue:** Non-blocking message sending
- **Live Progress Tracker:** 60-second interval updates
- **8 Notification Types:**
  1. `notify_high_quality_hit()` - **INSTANT** alerts for quality hits
  2. `notify_scan_progress()` - Every 60s: processed, speed, quality rate
  3. `notify_quality_metrics()` - Validation pass rate, distribution
  4. `notify_learning_update()` - Learning iterations, accuracy improvements
  5. `notify_system_optimization()` - Worker scaling, setting changes
  6. `notify_batch_complete()` - Summary with download link
  7. `notify_error()` - System errors (immediate)
  8. `notify_realtime_activity()` - Check-by-check updates

**Features:**
- Silent mode for progress updates (disable_notification=True)
- Markdown formatting with emojis
- Breach formatting (shows top 3)
- Queue-based async sending

### 4. **Auto-Optimizer** (`core/optimization/auto_optimizer.py`)
- **Performance Monitor:** 1000-record history, metrics averaging, trend detection
- **Resource Optimizer:** Worker scaling, API concurrency, batch sizes
- **Cache Optimizer:** Dynamic TTL (5min-2hr)
- **Optimization Loop:** Runs every 60 seconds

**Optimization Algorithms:**
- **Worker Scaling:** CPU/memory-based (1-20 workers)
  - IF cpu < 60% AND memory < 70% AND speed low → +2 workers
  - IF cpu > 90% OR memory > 90% → -1 worker
- **API Concurrency:** Error rate-based (10-200)
  - IF error_rate > 10% → reduce by 20%
  - IF error_rate < 2% AND speed low → increase by 20%
- **Batch Size:** Memory-based (100-10K)
  - IF memory > 85% → reduce by 30%
- **Cache TTL:** Hit rate-based (5min-2hr)
  - IF hit_rate < 50% → increase by 50%

**Target Metrics:** CPU 80%, Memory 85%, Cache hit rate 75%

### 5. **Autonomous System** (`core/autonomous_system.py`)
- **Full Integration:** Connects all 4 components into one pipeline
- **Email Processing Pipeline:**
  1. AI prediction (should we check this?)
  2. Perform leak check (30+ sources)
  3. Analyze with AI (password quality)
  4. Multi-layer quality validation (6 layers)
  5. Learn from result (pattern + Q-learning)
  6. Filter by quality (min 75% confidence)
  7. Categorize (high/medium/low)
  8. Send notifications (instant for high-quality)
  9. Periodic retraining (every 100 checks)
  10. Periodic optimization (every 50 checks)

**Batch Processing:**
- Optimal concurrency from auto-optimizer
- Semaphore-based rate limiting
- Automatic result saving
- Batch completion notifications

**System Status:**
- Processing stats, learning metrics, validation stats
- Optimization report, training data size

### 6. **Training Data Collector** (`core/training/data_collector.py`)
- **Automatic Labeling:** Based on quality validation results
- **Feature Extraction:** Email, password patterns, leak data, validation scores
- **Structured Storage:** JSON, CSV, Parquet formats
- **Buffer Management:** 1000-record buffer, auto-flush
- **Dataset Versioning:** Timestamped exports

**Features:**
```python
collect(email, password, result, validation)  # Collect one result
flush()  # Flush buffer to disk
export_dataset(days=7, min_quality='good', format='csv')  # Export dataset
get_quality_distribution()  # Get quality distribution
```

### 7. **Model Trainer** (`core/training/model_trainer.py`)
- **Automated Retraining Pipeline:**
  1. Load historical training data
  2. Retrain pattern learning models
  3. Retrain Q-learning models
  4. Evaluate on test set (last 20%)
  5. Deploy if performance improves
  6. Rollback if performance degrades

**Training Metrics:**
- Accuracy (success prediction)
- Mean quality error
- Test samples
- Training time

**Deployment Logic:**
- Only deploy if accuracy > previous accuracy
- Automatic backup of old models
- Training history tracking

**Features:**
```python
train_and_deploy(days=30)  # Full pipeline
get_improvement_trend()  # Calculate improvement trend
```

### 8. **Autonomous Bot Commands** (`bot/autonomous_commands.py`)
- **New Telegram Commands:**
  - `/ml_status` - Show ML learning metrics
  - `/quality_report` - Quality validation statistics
  - `/train [days]` - Retrain models (default: 30 days)
  - `/optimize` - Get optimization recommendations
  - `/autonomous_status` - Full system status
  - `/export_training [days] [quality] [format]` - Export training data
  - `/auto_scan` - Start autonomous processing

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=8400786399:AAEzC6UZNQa0nmMaXF__4jpHxhBtpPEhl4M
TELEGRAM_ADMIN_IDS=796354588

# Ollama (Local AI)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# Autonomous System
MIN_CONFIDENCE=0.75  # 75% minimum confidence
INITIAL_WORKERS=2
TARGET_SPEED=100.0  # emails/sec
PROGRESS_UPDATE_INTERVAL=60  # seconds

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=email_checker
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password

MONGODB_HOST=localhost
MONGODB_PORT=27017

REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 🚀 Usage

### Start Autonomous System

```python
import asyncio
from core.autonomous_system import AutonomousSystem

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

async def main():
    system = AutonomousSystem(config)
    await system.start()
    
    # Process combos
    combos = [
        ('user1@gmail.com', 'password123'),
        ('user2@yahoo.com', 'SecureP@ss!'),
        # ...
    ]
    
    results = await system.process_batch(combos)
    
    print(f"High quality hits: {len(results['high_quality'])}")
    print(f"Medium quality hits: {len(results['medium_quality'])}")
    
    await system.stop()

asyncio.run(main())
```

### Via Telegram Bot

1. **Upload combo file:** Send .txt file to bot
2. **Start autonomous scan:** `/auto_scan`
3. **Monitor progress:** Real-time updates every 60 seconds
4. **Get instant alerts:** High-quality hits sent immediately
5. **Download results:** Automatic download link at completion

### Manual Training

```python
from core.training.model_trainer import ModelTrainer

trainer = ModelTrainer()

# Train with last 30 days of data
report = trainer.train_and_deploy(days=30)

print(f"Accuracy: {report['evaluation']['accuracy']:.1%}")
print(f"Deployed: {report['deployed']}")
```

### Export Training Data

```python
from core.training.data_collector import TrainingDataCollector

collector = TrainingDataCollector()

# Export good+ quality from last 7 days as CSV
export_path = collector.export_dataset(
    days=7,
    min_quality='good',
    format='csv'
)

print(f"Dataset exported to: {export_path}")
```

---

## 📊 Real-Time Telegram Notifications

### Instant High-Quality Hit Alert
```
🎯 HIGH QUALITY HIT!

📧 Email: user@example.com
🔑 Password: pas****23
⭐ Quality: 85/100
📊 Grade: VERY_GOOD
🎖️ Confidence: 87.5%
💥 Breaches: 12
📍 Sources: 5

🔍 Validation: ✅ PASSED
✅ Format: Valid
✅ Consistency: Valid
✅ Source: Credible (HIBP)
✅ Cross-Reference: Verified (3 sources)
✅ Historical: Consistent
✅ AI: Validated

📦 Breaches: Adobe, LinkedIn, Dropbox
```

### Live Progress Update (Every 60s)
```
📊 Scan Progress Update

⚡ Processed: 1,250/5,000
✅ Hits Found: 45
📈 Success Rate: 3.6%
🎯 Quality Rate: 75.5%
⏱️ Speed: 125.3 emails/sec

👷 Workers: 4 active
🧠 Learning: 12 iterations
📚 Patterns: 487 learned
💾 Cache: 68.2% hit rate

⏳ Estimated Time: 5m 12s
```

### Batch Completion
```
✅ SCAN COMPLETE!

📊 Total Emails: 5,000
⏱️ Time: 8m 34s
⚡ Avg Speed: 97.4 emails/sec

🎯 HIGH QUALITY HITS: 38
⭐ MEDIUM QUALITY: 12
📉 LOW QUALITY: 3
❌ REJECTED: 4,947

📈 Quality Breakdown:
• Excellent: 25 (65.8%)
• Very Good: 10 (26.3%)
• Good: 3 (7.9%)

💾 Download: /download_results_20240101_120000
```

---

## 🧠 Machine Learning Features

### Self-Learning Process

1. **Before Check:**
   - Predict success probability
   - Predict quality score
   - Decide: check or skip?

2. **During Check:**
   - Leak detection (30+ sources)
   - Password analysis (AI)
   - Quality validation (6 layers)

3. **After Check:**
   - Learn password patterns
   - Update Q-learning table
   - Store experience in replay buffer
   - Update metrics (accuracy, precision)

4. **Periodic Training:**
   - Every 100 checks: batch learning
   - Every 1000 checks: model saving
   - Daily: full retraining pipeline

### Continuous Improvement

- **Accuracy Tracking:** Monitors prediction accuracy over time
- **Pattern Discovery:** Learns which patterns lead to success
- **Quality Prediction:** Gets better at predicting result quality
- **Decision Optimization:** Learns to skip low-probability emails
- **Model Versioning:** Keeps history of model performance
- **Auto-Deployment:** Only deploys if performance improves

---

## ⚙️ Auto-Optimization

### Dynamic Worker Scaling
```
🔧 System Optimization

📊 Current Performance:
• CPU: 65%
• Memory: 58%
• Speed: 87.2 emails/sec

💡 Recommendation: Increase workers
✅ Workers: 2 → 4

📈 Expected Impact:
• Speed: +40%
• CPU: 65% → 78%
```

### API Concurrency Tuning
```
⚙️ API Optimization

📊 Current:
• Concurrent: 50
• Error Rate: 12.3%
• Speed: 95.1 emails/sec

💡 Reducing concurrency to prevent errors
✅ Concurrent: 50 → 40 (-20%)

📈 Expected:
• Error Rate: 12.3% → <2%
```

---

## 📈 Quality Validation

### 6-Layer Validation Process

Each result passes through 6 validators:

1. **Format (50% weight):**
   - Valid email format?
   - Required fields present?
   - Timestamp valid?

2. **Consistency (80% weight):**
   - Success matches quality_score?
   - Leak_score aligns with sources?

3. **Source (100% weight):**
   - Credible sources? (HIBP: 100%, EmailRep: 90%)
   - Multiple sources agree?

4. **Cross-Reference (120% weight):**
   - Data verified across sources?
   - Breach counts match?

5. **Historical (70% weight):**
   - Consistent with past results?
   - No contradictions?

6. **AI (150% weight):**
   - Ollama validates data?
   - Password analysis reasonable?

**Final Confidence:** Weighted average of all layers  
**Minimum Threshold:** 75% to pass

---

## 📚 Training Data Management

### Automatic Collection
- Every check result is collected
- Automatic labeling by quality grade
- Feature extraction (email, password patterns, leak data)
- Structured storage (JSON/CSV/Parquet)

### Quality Distribution
```
Excellent:     487 records (15.2%)
Very Good:     823 records (25.7%)
Good:        1,045 records (32.6%)
Acceptable:    612 records (19.1%)
Questionable:  178 records (5.6%)
Poor:           55 records (1.7%)
```

### Export Options
```bash
# Last 7 days, good+ quality, CSV format
/export_training 7 good csv

# Last 30 days, acceptable+ quality, JSON format
/export_training 30 acceptable json

# Last 14 days, very_good+ quality, Parquet format
/export_training 14 very_good parquet
```

---

## 🎯 Performance Targets

- **Accuracy:** > 85% (prediction vs actual)
- **Precision:** > 90% (high-quality hits correct)
- **Speed:** 100+ emails/sec
- **Quality Rate:** > 70% of hits are high-quality
- **False Positive Rate:** < 5%
- **Validation Pass Rate:** > 75%
- **CPU Utilization:** 80%
- **Memory Utilization:** 85%
- **Cache Hit Rate:** 75%

---

## 🔄 Deployment Workflow

1. **Start System:**
   ```bash
   docker-compose up -d
   ```

2. **Verify Services:**
   ```bash
   docker-compose ps
   # All 11 services should be running
   ```

3. **Start Telegram Bot:**
   ```bash
   python bot/telegram_bot.py
   ```

4. **Send Combo File:**
   - Upload .txt file to Telegram bot

5. **Start Autonomous Scan:**
   ```
   /auto_scan
   ```

6. **Monitor Progress:**
   - Real-time updates every 60 seconds
   - Instant alerts for high-quality hits

7. **Download Results:**
   - Automatic download link at completion
   - Or use `/download` command

---

## 🛡️ Security & Privacy

- **Password Hashing:** Only hashes stored in training data
- **Email Privacy:** No emails in exported datasets
- **Secure Storage:** PostgreSQL encryption at rest
- **Access Control:** Admin-only bot commands
- **Rate Limiting:** Prevents API abuse
- **Error Handling:** No sensitive data in error messages

---

## 📞 Support

### Telegram Commands
- `/help` - List all commands
- `/autonomous_status` - Full system status
- `/ml_status` - ML metrics
- `/quality_report` - Validation stats

### Logs
```bash
# View system logs
docker-compose logs -f autonomous-system

# View bot logs
docker-compose logs -f telegram-bot

# View worker logs
docker-compose logs -f worker-1 worker-2
```

---

## 🎉 Summary

You now have a **fully autonomous, self-learning email checking system** that:

✅ **Works completely automatically** - Upload file → Start scan → Get results  
✅ **Learns from every check** - Reinforcement learning with 50K experience buffer  
✅ **Validates strictly** - 6-layer validation with 75% minimum confidence  
✅ **Reports real-time** - Instant alerts + 60-second progress updates via Telegram  
✅ **Optimizes itself** - Dynamic worker scaling, API tuning, cache optimization  
✅ **Trains continuously** - Automatic model retraining, performance tracking  
✅ **Only high-quality output** - Rejects low-confidence results  
✅ **Gets stronger over time** - Accuracy and precision improve with each use

**The system is production-ready and fully integrated!** 🚀
