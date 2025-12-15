"""
Breach Detection Service
Finds all breached passwords for email addresses using HaveIBeenPwned API
"""

import logging
import hashlib
import aiohttp
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class BreachDetectionService:
    """
    Find all breached passwords for email addresses
    Uses Have I Been Pwned API (free, no auth required)
    """
    
    def __init__(self):
        self.hibp_breach_api = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        self.hibp_paste_api = "https://haveibeenpwned.com/api/v3/pasteaccount/{email}"
        self.headers = {
            'User-Agent': 'AI-Email-Checker',
            'hibp-api-key': ''  # Will add support for API key later
        }
        self.session = None
        self.rate_limit_delay = 1.5  # HIBP requires 1.5 sec between requests
        self.last_request_time = 0
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
            logger.info("✅ Breach detection service initialized")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("🔒 Breach detection service closed")
    
    async def _rate_limit_wait(self):
        """Ensure we don't exceed HIBP rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    async def check_email_breaches(self, email: str) -> Dict:
        """
        Check if email appears in any breaches
        
        Returns:
            {
                'email': str,
                'breached': bool,
                'breach_count': int,
                'breaches': [
                    {
                        'name': str,
                        'title': str,
                        'domain': str,
                        'breach_date': str,
                        'added_date': str,
                        'modified_date': str,
                        'pwn_count': int,
                        'description': str,
                        'data_classes': [str],  # Types of data leaked
                        'is_verified': bool,
                        'is_fabricated': bool,
                        'is_sensitive': bool,
                        'is_retired': bool,
                        'is_spam_list': bool
                    }
                ],
                'paste_count': int,
                'pastes': [
                    {
                        'source': str,
                        'id': str,
                        'title': str,
                        'date': str,
                        'email_count': int
                    }
                ],
                'data_exposed': [str],  # All types of data exposed
                'risk_score': int,  # 0-100
                'risk_level': str  # CRITICAL/HIGH/MEDIUM/LOW
            }
        """
        await self.initialize()
        
        result = {
            'email': email,
            'breached': False,
            'breach_count': 0,
            'breaches': [],
            'paste_count': 0,
            'pastes': [],
            'data_exposed': set(),
            'risk_score': 0,
            'risk_level': 'LOW',
            'checked_at': datetime.now().isoformat()
        }
        
        try:
            # Check breaches
            await self._rate_limit_wait()
            breach_url = self.hibp_breach_api.format(email=email)
            
            async with self.session.get(breach_url) as response:
                if response.status == 200:
                    breaches = await response.json()
                    result['breached'] = True
                    result['breach_count'] = len(breaches)
                    result['breaches'] = breaches
                    
                    # Collect all exposed data types
                    for breach in breaches:
                        if 'DataClasses' in breach:
                            result['data_exposed'].update(breach['DataClasses'])
                    
                    logger.info(f"🔥 {email}: Found in {len(breaches)} breaches")
                
                elif response.status == 404:
                    # No breaches found - good!
                    logger.info(f"✅ {email}: No breaches found")
                
                elif response.status == 429:
                    # Rate limited
                    logger.warning(f"⏸️  Rate limited - waiting 60 seconds")
                    await asyncio.sleep(60)
                    return await self.check_email_breaches(email)  # Retry
                
                else:
                    logger.error(f"❌ Error checking {email}: HTTP {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Error checking breaches for {email}: {e}")
        
        try:
            # Check pastes
            await self._rate_limit_wait()
            paste_url = self.hibp_paste_api.format(email=email)
            
            async with self.session.get(paste_url) as response:
                if response.status == 200:
                    pastes = await response.json()
                    result['paste_count'] = len(pastes)
                    result['pastes'] = pastes
                    logger.info(f"📋 {email}: Found in {len(pastes)} pastes")
                
                elif response.status == 404:
                    # No pastes - good!
                    pass
        
        except Exception as e:
            logger.error(f"❌ Error checking pastes for {email}: {e}")
        
        # Convert set to list
        result['data_exposed'] = list(result['data_exposed'])
        
        # Calculate risk score
        result['risk_score'], result['risk_level'] = self._calculate_risk(result)
        
        return result
    
    def _calculate_risk(self, breach_data: Dict) -> Tuple[int, str]:
        """
        Calculate risk score (0-100) based on breach data
        
        Risk factors:
        - Number of breaches (up to 30 points)
        - Number of pastes (up to 20 points)
        - Sensitive data exposed (up to 50 points)
        """
        score = 0
        
        # Breach count (max 30)
        score += min(breach_data['breach_count'] * 5, 30)
        
        # Paste count (max 20)
        score += min(breach_data['paste_count'] * 2, 20)
        
        # Sensitive data exposed (max 50)
        sensitive_classes = {
            'Passwords': 20,
            'Password hints': 5,
            'Security questions and answers': 10,
            'Credit cards': 15,
            'Banking information': 15,
            'Social security numbers': 15,
            'Physical addresses': 5,
            'Phone numbers': 5,
            'Email addresses': 5,
            'IP addresses': 5,
            'Geographic locations': 5,
            'Dates of birth': 5,
            'Genders': 2,
            'Names': 2,
            'Usernames': 3
        }
        
        for data_class in breach_data['data_exposed']:
            if data_class in sensitive_classes:
                score += sensitive_classes[data_class]
        
        score = min(score, 100)
        
        # Determine risk level
        if score >= 80:
            level = 'CRITICAL'
        elif score >= 60:
            level = 'HIGH'
        elif score >= 30:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return score, level
    
    async def check_password_breach(self, password: str) -> Dict:
        """
        Check if password has been breached using k-anonymity
        (Doesn't send full password to API)
        
        Returns:
            {
                'password_hash': str,  # First 5 chars of SHA-1
                'breached': bool,
                'times_seen': int,  # How many times this password appeared in breaches
                'risk_level': str  # CRITICAL/HIGH/MEDIUM/LOW
            }
        """
        await self.initialize()
        
        # Hash the password with SHA-1
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        result = {
            'password_hash': prefix,
            'breached': False,
            'times_seen': 0,
            'risk_level': 'LOW'
        }
        
        try:
            await self._rate_limit_wait()
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    hashes = await response.text()
                    
                    # Search for our suffix in the response
                    for line in hashes.split('\n'):
                        if ':' in line:
                            hash_suffix, count = line.split(':')
                            if hash_suffix == suffix:
                                result['breached'] = True
                                result['times_seen'] = int(count.strip())
                                
                                # Determine risk level
                                if result['times_seen'] > 10000:
                                    result['risk_level'] = 'CRITICAL'
                                elif result['times_seen'] > 1000:
                                    result['risk_level'] = 'HIGH'
                                elif result['times_seen'] > 100:
                                    result['risk_level'] = 'MEDIUM'
                                else:
                                    result['risk_level'] = 'LOW'
                                
                                break
        
        except Exception as e:
            logger.error(f"❌ Error checking password breach: {e}")
        
        return result
    
    async def check_combo_breaches(self, combos: List[Tuple[str, str]], 
                                   progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        Check breaches for multiple email:password combos
        
        Args:
            combos: List of (email, password) tuples
            progress_callback: Optional callback(current, total)
            
        Returns:
            List of combined breach results
        """
        await self.initialize()
        
        results = []
        total = len(combos)
        
        for idx, (email, password) in enumerate(combos):
            try:
                # Check email breaches
                email_result = await self.check_email_breaches(email)
                
                # Check password breach
                password_result = await self.check_password_breach(password)
                
                # Combine results
                combined = {
                    **email_result,
                    'password': password,
                    'password_breached': password_result['breached'],
                    'password_breach_count': password_result['times_seen'],
                    'password_risk_level': password_result['risk_level']
                }
                
                results.append(combined)
                
                if progress_callback:
                    progress_callback(idx + 1, total)
                
                logger.info(f"✅ Checked {idx + 1}/{total}: {email} - "
                          f"{email_result['breach_count']} breaches, "
                          f"password seen {password_result['times_seen']} times")
            
            except Exception as e:
                logger.error(f"Error checking combo {email}:{password}: {e}")
                results.append({
                    'email': email,
                    'password': password,
                    'error': str(e)
                })
        
        return results
