# ⚡ Quick Reference Guide

## 🚀 Essential Commands

### Setup & Installation
```powershell
# One-command setup
.\setup.ps1

# Manual setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### Docker Operations
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f brain
docker-compose logs -f worker-1

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Check service health
docker-compose ps
```

### Running Locally (Without Docker)
```bash
# Terminal 1 - API Server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Celery Worker
celery -A workers.tasks worker --loglevel=info --concurrency=4

# Terminal 3 - Monitoring (optional)
prometheus --config.file=monitoring/prometheus.yml
```

## 📡 API Quick Reference

### Start Operation
```bash
curl -X POST http://localhost:8000/api/v1/operations/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_emails": ["test@example.com"],
    "services": ["mega"],
    "priority": 8
  }'
```

### Check Status
```bash
curl http://localhost:8000/api/v1/operations/status/OP-123
```

### Get Results
```bash
curl http://localhost:8000/api/v1/operations/results/OP-123
```

### System Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/stats
```

## 🔧 Configuration Quick Edits

### Enable/Disable Features (.env)
```bash
# AI Features
AI_ENABLED=true
LLM_ENABLED=true

# Workers
MAX_WORKERS=10
TASKS_PER_WORKER=5

# Rate Limiting
GLOBAL_RATE_LIMIT=100
PER_SERVICE_RATE_LIMIT=10
```

### Add API Keys (.env)
```bash
# OSINT
DEHASHED_API_KEY=your_key
INTELX_API_KEY=your_key

# Proxies
BRIGHTDATA_USERNAME=username
BRIGHTDATA_PASSWORD=password

# CAPTCHA
TWOCAPTCHA_API_KEY=your_key
```

## 🏗️ File Structure Quick Map

```
ai-email-checker/
├── core/               # Brain & orchestration
│   ├── brain/         # Decision engine
│   ├── queue/         # Task queue
│   └── state/         # State management
├── identity/          # Anonymity layer
│   ├── proxies/       # Proxy management
│   ├── fingerprints/  # Browser fingerprinting
│   └── sessions/      # Session isolation
├── checkers/          # Service checkers
│   ├── base/          # Base classes
│   └── cloud_storage/ # Cloud storage checkers
├── api/               # REST API
│   ├── main.py        # FastAPI app
│   ├── config.py      # Settings
│   └── routes/        # API endpoints
├── docker/            # Docker configs
├── docs/              # Documentation
├── .env               # Your configuration
└── requirements.txt   # Dependencies
```

## 🎯 Creating New Checkers (Fast)

```python
# 1. Create file: checkers/SERVICE_TYPE/service_name.py

from ..base import BaseChecker, CheckResult, CheckerResult

class YourServiceChecker(BaseChecker):
    def __init__(self, config=None):
        super().__init__("service_name", config)
    
    async def check_single(self, email, password, proxy=None, fingerprint=None):
        # Your login logic here
        return CheckResult(
            status=CheckerResult.SUCCESS,
            email=email,
            password=password,
            service=self.service_name
        )
    
    async def is_account_exists(self, email, proxy=None):
        # Check if account exists
        return True

# 2. Register in checkers/__init__.py
from .SERVICE_TYPE.service_name import YourServiceChecker

CHECKER_REGISTRY = {
    'service_name': YourServiceChecker
}
```

## 🔍 Debugging Quick Tips

### View Logs
```bash
# Docker
docker-compose logs -f brain
docker-compose logs -f worker-1

# Local
tail -f logs/api.log
tail -f logs/worker.log
```

### Check Database
```bash
# PostgreSQL
docker exec -it ai-checker-postgres psql -U postgres -d ai_email_checker

# MongoDB
docker exec -it ai-checker-mongo mongosh

# Redis
docker exec -it ai-checker-redis redis-cli
```

### Test Components
```python
# Test Decision Engine
from core.brain import DecisionEngine
engine = DecisionEngine()
stats = engine.get_statistics()
print(stats)

# Test Proxy Manager
from identity.proxies import ProxyManager
manager = ProxyManager()
await manager.initialize()
stats = manager.pool.get_statistics()
print(stats)

# Test Checker
from checkers.cloud_storage.mega import MegaChecker
checker = MegaChecker()
result = await checker.check_single("test@example.com", "password123")
print(result)
```

## 📊 Monitoring Quick Access

| Service | URL | Default Creds |
|---------|-----|---------------|
| API Docs | http://localhost:8000/docs | - |
| Health Check | http://localhost:8000/health | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |

## ⚠️ Common Issues & Fixes

### "Redis connection failed"
```bash
docker-compose restart redis
# or
redis-server
```

### "Playwright browsers not found"
```bash
playwright install chromium firefox
```

### "Database migration needed"
```bash
alembic upgrade head
```

### "Permission denied"
```bash
# Linux/Mac
chmod +x setup.sh

# Windows
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 🎨 Python SDK Quick Example

```python
import requests

# Start operation
resp = requests.post(
    'http://localhost:8000/api/v1/operations/start',
    json={
        'target_emails': ['user@example.com'],
        'services': ['mega', 'dropbox']
    }
)
op_id = resp.json()['operation_id']

# Check status
status = requests.get(f'http://localhost:8000/api/v1/operations/status/{op_id}')
print(status.json())

# Get results
results = requests.get(f'http://localhost:8000/api/v1/operations/results/{op_id}')
print(results.json())
```

## 📚 Documentation Quick Links

- **Installation**: `docs/guides/installation.md`
- **Custom Checkers**: `docs/guides/custom-checkers.md`
- **API Reference**: `docs/api/reference.md`
- **Architecture**: `README.md`
- **Project Summary**: `PROJECT_SUMMARY.md`

## 🎯 Testing Quick Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_decision_engine.py

# Run with coverage
pytest --cov=core --cov=identity --cov=checkers

# Run integration tests
pytest tests/integration/
```

## 🔐 Security Checklist

- [ ] API keys added to `.env`
- [ ] `.env` added to `.gitignore`
- [ ] Strong database passwords set
- [ ] Rate limiting configured
- [ ] Monitoring enabled
- [ ] Logs reviewed regularly
- [ ] Access control implemented (production)

## 💡 Pro Tips

1. **Use Docker** for easiest setup
2. **Start small** - test with 1-2 emails first
3. **Monitor logs** - watch for errors
4. **Scale gradually** - add workers as needed
5. **Test checkers** before production use
6. **Keep API keys secure** - never commit them
7. **Document changes** - help future you

---

## 🆘 Need Help?

1. Check the full documentation
2. Review example implementations
3. Look at logs for errors
4. Test components individually
5. Verify API keys are correct
6. Ensure services are running

**Remember: This is for authorized testing only! 🔒**
