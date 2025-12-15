# Installation & Setup Guide

## Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (recommended)
- **PostgreSQL 16+**
- **Redis 7+**
- **MongoDB 7+**
- **Node.js 18+** (for Playwright)

## Quick Start with Docker

The fastest way to get started is using Docker Compose, which will set up all services automatically.

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd ai-email-checker

# Copy environment configuration
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

### 2. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Initialize Ollama (LLM)

```bash
# Pull the AI model (one-time setup)
docker exec -it ai-checker-ollama ollama pull mistral

# Verify
docker exec -it ai-checker-ollama ollama list
```

### 4. Access the System

- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Manual Installation

If you prefer to install without Docker:

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip postgresql-16 redis-server mongodb-org
```

**macOS:**
```bash
brew install python@3.11 postgresql@16 redis mongodb-community
```

**Windows:**
```powershell
# Install via Chocolatey
choco install python311 postgresql redis mongodb

# Or use WSL2 (recommended)
wsl --install
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium firefox
```

### 3. Configure Databases

**PostgreSQL:**
```bash
# Create database
createdb ai_email_checker

# Run migrations
alembic upgrade head
```

**MongoDB:**
```bash
# Start MongoDB
mongod --dbpath ./data/mongodb

# MongoDB will auto-create database on first use
```

**Redis:**
```bash
# Start Redis
redis-server

# Verify
redis-cli ping
```

### 4. Install Ollama (Local LLM)

```bash
# Linux
curl https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Windows
# Download from https://ollama.ai/download

# Start Ollama
ollama serve

# Pull model
ollama pull mistral
```

### 5. Start the Application

**Terminal 1 - API Server:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A workers.tasks worker --loglevel=info --concurrency=4
```

**Terminal 3 - Monitoring (optional):**
```bash
# Start Prometheus
prometheus --config.file=monitoring/prometheus.yml

# Start Grafana
grafana-server --config=monitoring/grafana/grafana.ini
```

## Configuration

### Required API Keys

You'll need to obtain API keys for:

1. **OSINT Services** (at least one):
   - Dehashed: https://dehashed.com/
   - IntelX: https://intelx.io/
   - BreachDirectory: https://breachdirectory.org/

2. **Proxy Services** (recommended):
   - Bright Data: https://brightdata.com/
   - Smartproxy: https://smartproxy.com/
   - Oxylabs: https://oxylabs.io/

3. **CAPTCHA Solvers** (at least one):
   - 2Captcha: https://2captcha.com/
   - Anti-Captcha: https://anti-captcha.com/
   - CapMonster: https://capmonster.cloud/

### Edit .env File

```bash
# OSINT APIs
DEHASHED_API_KEY=your_key_here
INTELX_API_KEY=your_key_here

# Proxy Services
BRIGHTDATA_USERNAME=your_username
BRIGHTDATA_PASSWORD=your_password

# CAPTCHA Solvers
TWOCAPTCHA_API_KEY=your_key_here
```

## Verification

Test that everything is working:

```bash
# Check API health
curl http://localhost:8000/health

# Check system stats
curl http://localhost:8000/stats

# Run a test operation (via API docs)
# Navigate to: http://localhost:8000/docs
```

## Troubleshooting

### Common Issues

**1. Redis Connection Failed**
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server
```

**2. PostgreSQL Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql
```

**3. Playwright Browser Installation Failed**
```bash
# Install system dependencies
playwright install-deps

# Reinstall browsers
playwright install
```

**4. Ollama Model Not Found**
```bash
# Pull the model
ollama pull mistral

# List available models
ollama list
```

### Logs

Check logs for errors:

```bash
# Docker logs
docker-compose logs -f brain
docker-compose logs -f worker-1

# Manual installation
tail -f logs/api.log
tail -f logs/worker.log
```

## Next Steps

- Read the [Architecture Documentation](../architecture/overview.md)
- Learn how to [Create Custom Checkers](./custom-checkers.md)
- Set up [Monitoring & Alerting](./monitoring.md)
- Review [Security Best Practices](./security.md)

## Support

For issues and questions:
- Check the [FAQ](./faq.md)
- Review [Troubleshooting Guide](./troubleshooting.md)
- Open an issue on GitHub
