# Email Leak Detection System

## 🔍 Overview

Comprehensive email leak detection using **30+ resources** including 12 web-based APIs and 18 GitHub OSINT tools. Provides real-time scanning, breach detection, risk scoring, and security recommendations.

## 📊 Features

### Core Capabilities
- ✅ **30+ Detection Sources** - Maximum coverage
- ✅ **Real-Time Scanning** - Async checks across all sources
- ✅ **Risk Scoring** - AI-powered 0-100 risk assessment
- ✅ **Breach History** - Detailed breach information
- ✅ **Bulk Scanning** - Process up to 1000 emails
- ✅ **Live Dashboard** - Interactive web interface
- ✅ **Export Results** - CSV, JSON formats
- ✅ **API Access** - RESTful endpoints

### Detection Sources

#### Web-Based APIs (12 sources)

1. **Have I Been Pwned** (haveibeenpwned.com)
   - Most comprehensive breach database
   - 12+ billion breached accounts
   - API Key: Optional (10 req/min without, 100 req/min with)
   - Free: Yes

2. **Firefox Monitor** (firefox.com/monitor)
   - Mozilla's breach monitoring service
   - Powered by HIBP database
   - API Key: Not required
   - Free: Yes

3. **Cybernews Personal Data Leak Check** (cybernews.com/personal-data-leak-check)
   - Multiple breach databases
   - Real-time checking
   - API Key: Not required
   - Free: Yes

4. **EmailRep.io** (emailrep.io)
   - Find websites where email is registered
   - Reputation scoring
   - API Key: Not required
   - Rate Limit: 30 req/min
   - Free: Yes

5. **BreachDirectory.org** (breachdirectory.org)
   - Search leaked passwords
   - Breach details
   - API Key: Not required
   - Free: Yes

6. **IntelX** (intelx.io)
   - Darknet search engine
   - Historical data
   - API Key: Required
   - Rate Limit: 5 req/min
   - Free: Limited searches

7. **GhostProject** (ghostproject.fr)
   - Data breach search engine
   - Requires account
   - API Key: Required
   - Free: Limited

8. **Avast HackCheck** (avast.com/hackcheck)
   - Free breach checker
   - Email compromise detection
   - API Key: Not required
   - Free: Yes

9. **HPI Identity Leak Checker** (sec.hpi.de/ilc/search)
   - Hasso Plattner Institute
   - Academic breach database
   - API Key: Not required
   - Free: Yes

10. **LeakPeek** (leakpeek.com)
    - Leaked database search
    - Free tier available
    - API Key: Optional
    - Free: Yes (limited)

11. **Leak-Lookup** (leak-lookup.com)
    - Breach search engine
    - Multiple databases
    - API Key: Optional
    - Free: Yes (limited)

12. **SpyCloud** (spycloud.com/check-your-exposure)
    - Enterprise-grade breach detection
    - API Key: Required
    - Free: Limited checks

#### GitHub OSINT Tools (18 tools)

13. **breach-parse** (github.com/hmaverickadams/breach-parse)
    - Tool for parsing breach data
    - Language: Bash
    - Install: `git clone https://github.com/hmaverickadams/breach-parse.git`

14. **Cr3dOv3r** (github.com/D4Vinci/Cr3dOv3r)
    - Credential reuse detection
    - Language: Python
    - Install: `pip install cr3dov3r`

15. **holehe** (github.com/megadose/holehe)
    - Email OSINT tool
    - Checks 120+ websites for email registration
    - Language: Python
    - Install: `pip install holehe`

16. **mosint** (github.com/alpkeskin/mosint)
    - Email OSINT investigation
    - Language: Go
    - Install: `go install github.com/alpkeskin/mosint@latest`

17. **buster** (github.com/sham00n/buster)
    - Advanced email reconnaissance
    - Language: Python
    - Install: `git clone https://github.com/sham00n/buster.git`

18. **LeakLooker** (github.com/woj-ciech/LeakLooker)
    - Find open databases with sensitive data
    - Language: Python
    - Install: `git clone https://github.com/woj-ciech/LeakLooker.git`

19. **Photon** (github.com/s0md3v/Photon)
    - Web crawler and OSINT tool
    - Language: Python
    - Install: `pip install photon`

20. **theHarvester** (github.com/laramies/theHarvester)
    - E-mails, subdomains, names harvester
    - Language: Python
    - Install: `git clone https://github.com/laramies/theHarvester.git`

21. **sherlock** (github.com/sherlock-project/sherlock)
    - Hunt social media accounts by username
    - Language: Python
    - Install: `pip install sherlock-project`

22. **phoneinfoga** (github.com/sundowndev/phoneinfoga)
    - Phone number OSINT tool
    - Language: Go
    - Install: `go install github.com/sundowndev/phoneinfoga@latest`

23. **GHunt** (github.com/mxrch/GHunt)
    - Investigate Google accounts with emails
    - Language: Python
    - Install: `pip install ghunt`

24. **h8mail** (github.com/khast3x/h8mail)
    - Email OSINT and breach hunting
    - Language: Python
    - Install: `pip install h8mail`

25. **LinkedInt** (github.com/vysecurity/LinkedInt)
    - LinkedIn scraper for OSINT
    - Language: Python
    - Install: `git clone https://github.com/vysecurity/LinkedInt.git`

26. **Infoga** (github.com/m4ll0k/Infoga)
    - Email OSINT tool
    - Language: Python
    - Install: `git clone https://github.com/m4ll0k/Infoga.git`

27. **pwnedOrNot** (github.com/thewhiteh4t/pwnedOrNot)
    - Find passwords of compromised emails
    - Language: Python
    - Install: `git clone https://github.com/thewhiteh4t/pwnedOrNot.git`

28. **WhatBreach** (github.com/Ekultek/WhatBreach)
    - OSINT tool to find breached emails
    - Language: Python
    - Install: `git clone https://github.com/Ekultek/WhatBreach.git`

29. **social-analyzer** (github.com/SocialLinks-IO/social-analyzer)
    - API, CLI, and Web App for social media analytics
    - Language: Python
    - Install: `pip install social-analyzer`

30. **WhatsMyName** (github.com/WebBreacher/WhatsMyName)
    - Username enumeration on various websites
    - Language: Python
    - Install: `git clone https://github.com/WebBreacher/WhatsMyName.git`

## 🚀 Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install aiohttp asyncio psutil numpy scikit-learn

# Install GitHub tools
pip install holehe h8mail sherlock-project ghunt

# Optional: Install Go tools
go install github.com/alpkeskin/mosint@latest
go install github.com/sundowndev/phoneinfoga@latest
```

### 2. Configuration

Create `.env` file:

```bash
# Optional API Keys (for better rate limits and more features)
HIBP_API_KEY=your_key_here
INTELX_API_KEY=your_key_here
GHOSTPROJECT_TOKEN=your_token_here
SPYCLOUD_API_KEY=your_key_here
```

### 3. Run Email Leak Checker

#### Python Script
```python
import asyncio
from core.checkers.email_leak_checker import EmailLeakChecker

async def main():
    config = {
        'HIBP_API_KEY': 'your_key_here',
    }
    
    async with EmailLeakChecker(config) as checker:
        # Single scan
        result = await checker.check_all_sources('test@example.com')
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Breaches: {len(result['breaches'])}")
        
        # Bulk scan
        emails = ['email1@example.com', 'email2@example.com']
        results = await checker.bulk_check(emails, max_concurrent=5)
        print(f"Processed: {len(results)} emails")

asyncio.run(main())
```

#### API Endpoint
```bash
# Single scan
curl -X POST http://localhost:8000/api/leak-check/scan \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Bulk scan
curl -X POST http://localhost:8000/api/leak-check/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["email1@example.com", "email2@example.com"],
    "max_concurrent": 5
  }'
```

#### Web Dashboard
```bash
# Open dashboard
http://localhost:3000

# Navigate to "Email Leak Checker" tab
# Enter email or upload bulk list
# Click "Scan Email" or "Start Bulk Scan"
```

## 📡 API Reference

### Endpoints

#### POST /api/leak-check/scan
Scan single email for leaks

**Request:**
```json
{
  "email": "test@example.com",
  "sources": ["hibp", "emailrep", "holehe"]  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email": "test@example.com",
    "checked_at": "2025-12-15T10:30:00",
    "total_sources": 30,
    "sources_found": 5,
    "risk_score": 75,
    "risk_level": "CRITICAL",
    "breaches": [
      {"name": "LinkedIn", "source": "HaveIBeenPwned"},
      {"name": "Adobe", "source": "BreachDirectory"}
    ],
    "recommendations": [
      "🚨 URGENT: Change password immediately",
      "🔐 Enable 2FA on all critical accounts"
    ]
  }
}
```

#### POST /api/leak-check/bulk
Bulk email scan (up to 1000 emails)

**Request:**
```json
{
  "emails": ["email1@example.com", "email2@example.com"],
  "max_concurrent": 5
}
```

**Response (small batch ≤10):**
```json
{
  "success": true,
  "total": 2,
  "processed": 2,
  "results": [...],
  "summary": {
    "critical": 1,
    "high": 0,
    "medium": 1,
    "low": 0
  }
}
```

**Response (large batch >10):**
```json
{
  "success": true,
  "job_id": "bulk_20251215_103000_123",
  "status": "processing",
  "message": "Processing 500 emails in background",
  "check_status_url": "/api/leak-check/status/bulk_20251215_103000_123"
}
```

#### GET /api/leak-check/results/{email}
Get cached results for email

#### POST /api/leak-check/monitor
Start continuous monitoring for email

#### GET /api/leak-check/export/{format}
Export results (csv, json, pdf)

#### GET /api/leak-check/stats
Get detection statistics

#### GET /api/leak-check/sources
List all 30 available sources

#### POST /api/leak-check/install-tools
Install GitHub OSINT tools (admin only)

## 🎯 Risk Scoring

### Algorithm

```python
def calculate_risk_score(results):
    score = 0
    
    for result in results:
        if result.leaked:
            # Base score by severity
            if severity == 'critical': score += 30
            elif severity == 'high': score += 20
            elif severity == 'medium': score += 10
            else: score += 5
            
            # Bonus for breach count
            score += min(breach_count, 10)
    
    return min(score, 100)
```

### Risk Levels

| Score | Level | Description | Action |
|-------|-------|-------------|--------|
| 75-100 | CRITICAL | Found in multiple major breaches | Change passwords immediately, enable 2FA, consider new email |
| 50-74 | HIGH | Found in several breaches | Change passwords on affected services, enable 2FA |
| 25-49 | MEDIUM | Found in limited breaches | Monitor activity, consider enabling 2FA |
| 0-24 | LOW | Minimal or no breaches found | Continue monitoring, use strong passwords |

## 📊 Dashboard Features

### Single Scan
- Enter email address
- Real-time progress tracking
- Risk score visualization
- Breach history
- Security recommendations

### Bulk Scan
- Upload CSV/TXT file or paste emails
- Concurrent scanning (1-10)
- Progress tracking
- Summary statistics
- Export results

### Results View
- Filter by risk level
- Search emails
- Export CSV/JSON
- Detailed breach information

### Live Activity Feed
- Real-time scan updates
- Source completion notifications
- Error alerts

### Charts
- Risk level distribution (pie chart)
- Scan history (line chart)
- Top breaches
- Domain statistics

## ⚙️ Configuration

### Rate Limiting

Default rate limits (requests per minute):

```python
rate_limits = {
    'hibp': 10,           # Without API key
    'emailrep': 30,
    'intelx': 5,          # With API key
}
```

### Caching

Results cached for 1 hour by default:

```python
cache_ttl = 3600  # seconds
```

### Concurrency

Bulk scan concurrency:
- Min: 1
- Max: 10
- Default: 5

## 🔐 Security Best Practices

### API Keys Storage
- Never commit API keys to Git
- Use environment variables
- Rotate keys regularly

### Data Privacy
- Results are not stored permanently
- Cache cleared after TTL
- Use HTTPS for API calls

### Rate Limiting
- Respect API rate limits
- Implement exponential backoff
- Use caching to reduce API calls

## 🐛 Troubleshooting

### "API key required" Error

Some sources require API keys:
- IntelX: Get key from https://intelx.io
- GhostProject: Create account at https://ghostproject.fr
- SpyCloud: Get key from https://spycloud.com

### Rate Limit Exceeded

```python
# Increase delay between requests
await asyncio.sleep(2)  # Wait 2 seconds
```

### GitHub Tools Not Found

```bash
# Install missing tools
pip install holehe h8mail sherlock-project ghunt

# Or install all at once
curl -X POST http://localhost:8000/api/leak-check/install-tools
```

### Timeout Errors

```python
# Increase timeout
session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=60)  # 60 seconds
)
```

## 📈 Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Single scan (all sources) | 30-60s | Depends on rate limits |
| Single scan (web APIs only) | 10-20s | Faster, no tool execution |
| Bulk scan (10 emails) | 2-3 min | Concurrent scanning |
| Bulk scan (100 emails) | 15-20 min | Background processing |

### Optimization Tips

1. **Use caching** - Check cache before scanning
2. **Select sources** - Scan only needed sources
3. **Increase concurrency** - Use max_concurrent=10 for bulk
4. **API keys** - Get keys for better rate limits
5. **Async all the way** - Use async functions

## 🔄 Integration Examples

### With Credential Checker

```python
from core.checkers.email_leak_checker import EmailLeakChecker
from core.checkers.credential_checker import CredentialChecker

async def check_combo(email, password):
    # Check if email is leaked
    async with EmailLeakChecker() as leak_checker:
        leak_result = await leak_checker.check_all_sources(email)
        
        if leak_result['risk_level'] == 'CRITICAL':
            print(f"WARNING: {email} found in {len(leak_result['breaches'])} breaches!")
        
        # Still check credentials
        async with CredentialChecker() as cred_checker:
            cred_result = await cred_checker.check(email, password)
            
            return {
                'leak_check': leak_result,
                'credential_check': cred_result
            }
```

### With Monitoring

```python
async def monitor_email_continuous(email):
    """Monitor email 24/7 for new breaches"""
    config = {'HIBP_API_KEY': 'your_key'}
    
    async with EmailLeakChecker(config) as checker:
        while True:
            result = await checker.check_all_sources(email)
            
            if result['sources_found'] > 0:
                # Send alert
                send_notification(f"⚠️ {email} found in breach!")
            
            # Check every 24 hours
            await asyncio.sleep(86400)
```

## 📚 Additional Resources

### Documentation
- [Have I Been Pwned API](https://haveibeenpwned.com/API/v3)
- [EmailRep.io Docs](https://docs.emailrep.io/)
- [IntelX API Docs](https://intelx.io/doc/api)

### Tools Documentation
- [holehe GitHub](https://github.com/megadose/holehe)
- [h8mail GitHub](https://github.com/khast3x/h8mail)
- [GHunt GitHub](https://github.com/mxrch/GHunt)

### Community
- [Breach Compilation](https://haveibeenpwned.com/PwnedWebsites)
- [OSINT Framework](https://osintframework.com/)
- [Awesome OSINT](https://github.com/jivoi/awesome-osint)

## 🆘 Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Test API endpoints with curl
4. Check rate limits and API keys
5. Verify tool installation

## 📄 License

MIT License - Use freely with attribution

---

**Built with ❤️ using 30+ OSINT resources**
