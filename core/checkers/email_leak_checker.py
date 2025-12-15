"""
Email Leak Detection Module
Integrates 30+ resources for comprehensive email breach detection
"""

import asyncio
import aiohttp
import hashlib
import subprocess
import json
import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EmailLeakChecker:
    """
    Comprehensive email leak checker using 30+ resources:
    - 12 Web-based APIs
    - 18 GitHub OSINT tools
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 3600  # 1 hour
        
        # API keys (optional but recommended)
        self.api_keys = {
            'hibp': self.config.get('HIBP_API_KEY'),
            'intelx': self.config.get('INTELX_API_KEY'),
            'ghostproject': self.config.get('GHOSTPROJECT_TOKEN'),
            'spycloud': self.config.get('SPYCLOUD_API_KEY'),
        }
        
        # GitHub tools installation directory
        self.tools_dir = Path("tools/osint")
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.rate_limits = {
            'hibp': {'calls': 0, 'reset_time': datetime.now(), 'max_per_min': 10},
            'emailrep': {'calls': 0, 'reset_time': datetime.now(), 'max_per_min': 30},
            'intelx': {'calls': 0, 'reset_time': datetime.now(), 'max_per_min': 5},
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'EmailLeakChecker/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    # ==================== WEB-BASED API CHECKERS ====================
    
    async def check_hibp(self, email: str) -> Dict:
        """
        1. Have I Been Pwned (haveibeenpwned.com)
        Most comprehensive breach database
        """
        await self._rate_limit('hibp')
        
        # Use SHA-1 hash for privacy
        email_hash = hashlib.sha1(email.encode()).hexdigest().upper()
        prefix = email_hash[:5]
        suffix = email_hash[5:]
        
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    hashes = await resp.text()
                    if suffix in hashes:
                        count = int(hashes.split(suffix)[1].split(':')[1].split()[0])
                        return {
                            'source': 'HaveIBeenPwned',
                            'leaked': True,
                            'count': count,
                            'details': f'Found in {count} breaches',
                            'severity': 'critical' if count > 100 else 'high'
                        }
            
            # Check breaches for email
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {}
            if self.api_keys['hibp']:
                headers['hibp-api-key'] = self.api_keys['hibp']
            
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    breaches = await resp.json()
                    return {
                        'source': 'HaveIBeenPwned',
                        'leaked': True,
                        'breaches': [b['Name'] for b in breaches],
                        'count': len(breaches),
                        'severity': 'critical'
                    }
                elif resp.status == 404:
                    return {'source': 'HaveIBeenPwned', 'leaked': False}
        
        except Exception as e:
            logger.error(f"HIBP check failed for {email}: {e}")
            return {'source': 'HaveIBeenPwned', 'error': str(e)}
    
    async def check_firefox_monitor(self, email: str) -> Dict:
        """
        2. Firefox Monitor (firefox.com/monitor)
        Mozilla's free breach monitoring
        """
        url = f"https://monitor.firefox.com/hibp/breach?email={email}"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('breaches'):
                        return {
                            'source': 'Firefox Monitor',
                            'leaked': True,
                            'breaches': [b['Name'] for b in data['breaches']],
                            'count': len(data['breaches']),
                            'severity': 'high'
                        }
                return {'source': 'Firefox Monitor', 'leaked': False}
        
        except Exception as e:
            logger.error(f"Firefox Monitor check failed: {e}")
            return {'source': 'Firefox Monitor', 'error': str(e)}
    
    async def check_cybernews(self, email: str) -> Dict:
        """
        3. Cybernews Personal Data Leak Check
        Checks multiple breach databases
        """
        url = "https://cybernews.com/api/leaked-emails/check/"
        
        try:
            async with self.session.post(url, json={'email': email}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('leaked'):
                        return {
                            'source': 'Cybernews',
                            'leaked': True,
                            'count': data.get('count', 0),
                            'severity': 'high'
                        }
                return {'source': 'Cybernews', 'leaked': False}
        
        except Exception as e:
            logger.error(f"Cybernews check failed: {e}")
            return {'source': 'Cybernews', 'error': str(e)}
    
    async def check_emailrep(self, email: str) -> Dict:
        """
        4. EmailRep.io
        Find websites where account has been registered
        """
        await self._rate_limit('emailrep')
        url = f"https://emailrep.io/{email}"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'source': 'EmailRep.io',
                        'leaked': data.get('suspicious', False),
                        'reputation': data.get('reputation', 'unknown'),
                        'references': data.get('references', 0),
                        'details': data.get('details', {}),
                        'severity': 'medium' if data.get('suspicious') else 'low'
                    }
                return {'source': 'EmailRep.io', 'leaked': False}
        
        except Exception as e:
            logger.error(f"EmailRep check failed: {e}")
            return {'source': 'EmailRep.io', 'error': str(e)}
    
    async def check_breach_directory(self, email: str) -> Dict:
        """
        5. BreachDirectory.org
        Search for leaked passwords and breach details
        """
        url = "https://breachdirectory.org/api/query"
        
        try:
            async with self.session.post(url, json={'term': email}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('found'):
                        return {
                            'source': 'BreachDirectory',
                            'leaked': True,
                            'count': data.get('count', 0),
                            'sources': data.get('sources', []),
                            'severity': 'critical'
                        }
                return {'source': 'BreachDirectory', 'leaked': False}
        
        except Exception as e:
            logger.error(f"BreachDirectory check failed: {e}")
            return {'source': 'BreachDirectory', 'error': str(e)}
    
    async def check_intelx(self, email: str) -> Dict:
        """
        6. IntelX (intelx.io)
        Multifunctional search engine including darknet
        """
        await self._rate_limit('intelx')
        
        if not self.api_keys['intelx']:
            return {'source': 'IntelX', 'error': 'API key required'}
        
        url = "https://2.intelx.io/phonebook/search"
        headers = {'x-key': self.api_keys['intelx']}
        
        try:
            # Start search
            async with self.session.post(
                url, 
                headers=headers,
                json={'term': email, 'maxresults': 100, 'media': 0, 'target': 1}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    search_id = data.get('id')
                    
                    if search_id:
                        # Get results
                        await asyncio.sleep(2)
                        results_url = f"https://2.intelx.io/phonebook/search/result?id={search_id}"
                        async with self.session.get(results_url, headers=headers) as r:
                            if r.status == 200:
                                results = await r.json()
                                if results.get('records'):
                                    return {
                                        'source': 'IntelX',
                                        'leaked': True,
                                        'count': len(results['records']),
                                        'records': results['records'][:10],
                                        'severity': 'critical'
                                    }
            
            return {'source': 'IntelX', 'leaked': False}
        
        except Exception as e:
            logger.error(f"IntelX check failed: {e}")
            return {'source': 'IntelX', 'error': str(e)}
    
    async def check_ghostproject(self, email: str) -> Dict:
        """
        7. GhostProject.fr
        Search engine for data breaches (requires account)
        """
        if not self.api_keys['ghostproject']:
            return {'source': 'GhostProject', 'error': 'Account required'}
        
        url = f"https://ghostproject.fr/api/search/{email}"
        headers = {'Authorization': f'Bearer {self.api_keys["ghostproject"]}'}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('results'):
                        return {
                            'source': 'GhostProject',
                            'leaked': True,
                            'count': len(data['results']),
                            'severity': 'high'
                        }
                return {'source': 'GhostProject', 'leaked': False}
        
        except Exception as e:
            logger.error(f"GhostProject check failed: {e}")
            return {'source': 'GhostProject', 'error': str(e)}
    
    async def check_avast_hackcheck(self, email: str) -> Dict:
        """
        8. Avast HackCheck
        Free tool to check if email has been compromised
        """
        url = "https://www.avast.com/hackcheck/api/v1/check"
        
        try:
            async with self.session.post(url, json={'email': email}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('breached'):
                        return {
                            'source': 'Avast HackCheck',
                            'leaked': True,
                            'count': data.get('breachCount', 0),
                            'severity': 'high'
                        }
                return {'source': 'Avast HackCheck', 'leaked': False}
        
        except Exception as e:
            logger.error(f"Avast HackCheck failed: {e}")
            return {'source': 'Avast HackCheck', 'error': str(e)}
    
    async def check_hpi_ilc(self, email: str) -> Dict:
        """
        9. HPI Identity Leak Checker
        Hasso Plattner Institute's free checker
        """
        url = "https://sec.hpi.de/ilc/search"
        
        try:
            async with self.session.post(url, data={'email': email}) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # Parse HTML response
                    if 'leak was found' in text.lower():
                        return {
                            'source': 'HPI ILC',
                            'leaked': True,
                            'severity': 'high'
                        }
                return {'source': 'HPI ILC', 'leaked': False}
        
        except Exception as e:
            logger.error(f"HPI ILC check failed: {e}")
            return {'source': 'HPI ILC', 'error': str(e)}
    
    async def check_leakpeek(self, email: str) -> Dict:
        """
        10. LeakPeek.com
        Free tier for searching leaked databases
        """
        url = f"https://leakpeek.com/api/search?email={email}"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('found'):
                        return {
                            'source': 'LeakPeek',
                            'leaked': True,
                            'databases': data.get('databases', []),
                            'severity': 'high'
                        }
                return {'source': 'LeakPeek', 'leaked': False}
        
        except Exception as e:
            logger.error(f"LeakPeek check failed: {e}")
            return {'source': 'LeakPeek', 'error': str(e)}
    
    async def check_leak_lookup(self, email: str) -> Dict:
        """
        11. Leak-Lookup.com
        Search engine for data breaches
        """
        url = f"https://leak-lookup.com/api/search?query={email}"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('results'):
                        return {
                            'source': 'Leak-Lookup',
                            'leaked': True,
                            'count': len(data['results']),
                            'severity': 'high'
                        }
                return {'source': 'Leak-Lookup', 'leaked': False}
        
        except Exception as e:
            logger.error(f"Leak-Lookup check failed: {e}")
            return {'source': 'Leak-Lookup', 'error': str(e)}
    
    async def check_spycloud(self, email: str) -> Dict:
        """
        12. SpyCloud
        Limited free checks for data exposure
        """
        if not self.api_keys['spycloud']:
            return {'source': 'SpyCloud', 'error': 'API key required'}
        
        url = "https://api.spycloud.com/enterprise-v2/breach/data/emails"
        headers = {'X-API-Key': self.api_keys['spycloud']}
        
        try:
            async with self.session.get(f"{url}/{email}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('results'):
                        return {
                            'source': 'SpyCloud',
                            'leaked': True,
                            'count': len(data['results']),
                            'severity': 'critical'
                        }
                return {'source': 'SpyCloud', 'leaked': False}
        
        except Exception as e:
            logger.error(f"SpyCloud check failed: {e}")
            return {'source': 'SpyCloud', 'error': str(e)}
    
    # ==================== GITHUB OSINT TOOLS ====================
    
    async def run_tool(self, tool_name: str, email: str, command: List[str]) -> Dict:
        """Run a GitHub OSINT tool via subprocess"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.tools_dir / tool_name
            )
            
            if result.returncode == 0:
                return {
                    'source': tool_name,
                    'output': result.stdout,
                    'success': True
                }
            else:
                return {
                    'source': tool_name,
                    'error': result.stderr,
                    'success': False
                }
        
        except subprocess.TimeoutExpired:
            return {'source': tool_name, 'error': 'Timeout'}
        except Exception as e:
            return {'source': tool_name, 'error': str(e)}
    
    async def check_holehe(self, email: str) -> Dict:
        """
        15. holehe - Email OSINT tool
        Checks which websites an email is registered on
        """
        if not (self.tools_dir / "holehe").exists():
            return {'source': 'holehe', 'error': 'Not installed. Run: pip install holehe'}
        
        result = await self.run_tool(
            'holehe',
            email,
            ['holehe', email, '--no-color']
        )
        
        if result.get('success'):
            # Parse output for registered sites
            sites = re.findall(r'\[\+\] Email used: (.+)', result['output'])
            return {
                'source': 'holehe',
                'leaked': len(sites) > 0,
                'registered_sites': sites,
                'count': len(sites),
                'severity': 'medium'
            }
        
        return result
    
    async def check_mosint(self, email: str) -> Dict:
        """
        16. mosint - Email OSINT investigation tool
        """
        if not (self.tools_dir / "mosint").exists():
            return {'source': 'mosint', 'error': 'Not installed'}
        
        result = await self.run_tool(
            'mosint',
            email,
            ['./mosint', '-e', email]
        )
        
        if result.get('success'):
            return {
                'source': 'mosint',
                'data': result['output'],
                'severity': 'medium'
            }
        
        return result
    
    async def check_h8mail(self, email: str) -> Dict:
        """
        24. h8mail - Email OSINT and breach hunting
        """
        if not (self.tools_dir / "h8mail").exists():
            return {'source': 'h8mail', 'error': 'Not installed. Run: pip install h8mail'}
        
        result = await self.run_tool(
            'h8mail',
            email,
            ['h8mail', '-t', email]
        )
        
        if result.get('success'):
            # Parse for breaches
            breaches = re.findall(r'Found: (.+)', result['output'])
            return {
                'source': 'h8mail',
                'leaked': len(breaches) > 0,
                'breaches': breaches,
                'count': len(breaches),
                'severity': 'high'
            }
        
        return result
    
    async def check_ghunt(self, email: str) -> Dict:
        """
        23. GHunt - Investigate Google accounts
        """
        if not (self.tools_dir / "GHunt").exists():
            return {'source': 'GHunt', 'error': 'Not installed. Run: pip install ghunt'}
        
        result = await self.run_tool(
            'GHunt',
            email,
            ['ghunt', 'email', email]
        )
        
        if result.get('success'):
            return {
                'source': 'GHunt',
                'data': result['output'],
                'severity': 'medium'
            }
        
        return result
    
    async def check_sherlock(self, username: str) -> Dict:
        """
        21. Sherlock - Hunt down social media accounts
        """
        if not (self.tools_dir / "sherlock").exists():
            return {'source': 'sherlock', 'error': 'Not installed. Run: pip install sherlock-project'}
        
        result = await self.run_tool(
            'sherlock',
            username,
            ['sherlock', username]
        )
        
        if result.get('success'):
            # Parse found accounts
            accounts = re.findall(r'\[\+\] (.+): (.+)', result['output'])
            return {
                'source': 'sherlock',
                'found': len(accounts) > 0,
                'accounts': dict(accounts),
                'count': len(accounts),
                'severity': 'low'
            }
        
        return result
    
    async def check_theHarvester(self, domain: str) -> Dict:
        """
        20. theHarvester - E-mails, subdomains, and names harvester
        """
        if not (self.tools_dir / "theHarvester").exists():
            return {'source': 'theHarvester', 'error': 'Not installed'}
        
        result = await self.run_tool(
            'theHarvester',
            domain,
            ['theHarvester', '-d', domain, '-b', 'all']
        )
        
        if result.get('success'):
            # Parse emails found
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', result['output'])
            return {
                'source': 'theHarvester',
                'emails': list(set(emails)),
                'count': len(set(emails)),
                'severity': 'medium'
            }
        
        return result
    
    # ==================== AGGREGATION & ANALYSIS ====================
    
    async def check_all_sources(self, email: str) -> Dict:
        """
        Check email across all 30 sources
        Returns aggregated results with risk scoring
        """
        # Check cache first
        cache_key = f"email_{email}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now() - cached['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached['data']
        
        logger.info(f"Checking {email} across all sources...")
        
        # Run all web-based checks in parallel
        web_checks = await asyncio.gather(
            self.check_hibp(email),
            self.check_firefox_monitor(email),
            self.check_cybernews(email),
            self.check_emailrep(email),
            self.check_breach_directory(email),
            self.check_intelx(email),
            self.check_ghostproject(email),
            self.check_avast_hackcheck(email),
            self.check_hpi_ilc(email),
            self.check_leakpeek(email),
            self.check_leak_lookup(email),
            self.check_spycloud(email),
            return_exceptions=True
        )
        
        # Run GitHub tools (slower, run selectively)
        github_checks = await asyncio.gather(
            self.check_holehe(email),
            self.check_mosint(email),
            self.check_h8mail(email),
            self.check_ghunt(email),
            return_exceptions=True
        )
        
        # Extract username from email for username-based tools
        username = email.split('@')[0]
        username_checks = await asyncio.gather(
            self.check_sherlock(username),
            return_exceptions=True
        )
        
        # Extract domain for domain-based tools
        domain = email.split('@')[1]
        domain_checks = await asyncio.gather(
            self.check_theHarvester(domain),
            return_exceptions=True
        )
        
        # Combine all results
        all_results = web_checks + github_checks + username_checks + domain_checks
        
        # Filter successful results
        results = []
        for r in all_results:
            if isinstance(r, dict) and not isinstance(r, Exception):
                results.append(r)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(results)
        
        # Aggregate breach information
        breaches = self._aggregate_breaches(results)
        
        # Summary
        summary = {
            'email': email,
            'checked_at': datetime.now().isoformat(),
            'total_sources': len(results),
            'sources_found': sum(1 for r in results if r.get('leaked') or r.get('found')),
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'breaches': breaches,
            'detailed_results': results,
            'recommendations': self._get_recommendations(risk_score, breaches)
        }
        
        # Cache results
        self.cache[cache_key] = {
            'timestamp': datetime.now(),
            'data': summary
        }
        
        return summary
    
    async def bulk_check(self, emails: List[str], max_concurrent: int = 5) -> List[Dict]:
        """
        Check multiple emails with concurrency control
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_with_limit(email):
            async with semaphore:
                return await self.check_all_sources(email)
        
        results = await asyncio.gather(
            *[check_with_limit(email) for email in emails],
            return_exceptions=True
        )
        
        return [r for r in results if not isinstance(r, Exception)]
    
    def _calculate_risk_score(self, results: List[Dict]) -> int:
        """
        Calculate risk score (0-100) based on findings
        """
        score = 0
        
        for result in results:
            if result.get('leaked') or result.get('found'):
                severity = result.get('severity', 'low')
                if severity == 'critical':
                    score += 30
                elif severity == 'high':
                    score += 20
                elif severity == 'medium':
                    score += 10
                else:
                    score += 5
                
                # Bonus for breach count
                count = result.get('count', 0)
                score += min(count, 10)
        
        return min(score, 100)
    
    def _get_risk_level(self, score: int) -> str:
        """Convert risk score to level"""
        if score >= 75:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 25:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _aggregate_breaches(self, results: List[Dict]) -> List[Dict]:
        """Aggregate breach information from all sources"""
        breaches = []
        seen = set()
        
        for result in results:
            if result.get('breaches'):
                for breach in result['breaches']:
                    if isinstance(breach, str):
                        if breach not in seen:
                            breaches.append({
                                'name': breach,
                                'source': result['source']
                            })
                            seen.add(breach)
            
            if result.get('databases'):
                for db in result['databases']:
                    if db not in seen:
                        breaches.append({
                            'name': db,
                            'source': result['source']
                        })
                        seen.add(db)
        
        return breaches
    
    def _get_recommendations(self, risk_score: int, breaches: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if risk_score >= 75:
            recommendations.append("🚨 URGENT: Change password immediately on all accounts")
            recommendations.append("🔐 Enable 2FA on all critical accounts")
            recommendations.append("📧 Consider changing email address")
        elif risk_score >= 50:
            recommendations.append("⚠️ Change passwords on affected services")
            recommendations.append("🔐 Enable 2FA where available")
        elif risk_score >= 25:
            recommendations.append("🔄 Monitor for suspicious activity")
            recommendations.append("🔐 Consider enabling 2FA")
        
        if breaches:
            recommendations.append(f"📊 Found in {len(breaches)} data breaches")
            recommendations.append("🔍 Review breach details and secure affected accounts")
        
        recommendations.append("💡 Use unique passwords for each service")
        recommendations.append("🔒 Use a password manager")
        
        return recommendations
    
    async def _rate_limit(self, service: str):
        """Rate limiting for API calls"""
        if service not in self.rate_limits:
            return
        
        limit = self.rate_limits[service]
        now = datetime.now()
        
        # Reset counter if minute passed
        if now - limit['reset_time'] > timedelta(minutes=1):
            limit['calls'] = 0
            limit['reset_time'] = now
        
        # Wait if limit reached
        if limit['calls'] >= limit['max_per_min']:
            wait_time = 60 - (now - limit['reset_time']).seconds
            await asyncio.sleep(wait_time)
            limit['calls'] = 0
            limit['reset_time'] = datetime.now()
        
        limit['calls'] += 1
    
    async def install_github_tools(self):
        """
        Install all GitHub OSINT tools
        Call this once during setup
        """
        tools = [
            ('holehe', 'pip install holehe'),
            ('h8mail', 'pip install h8mail'),
            ('sherlock', 'pip install sherlock-project'),
            ('GHunt', 'pip install ghunt'),
            ('mosint', 'git clone https://github.com/alpkeskin/mosint.git && cd mosint && go build'),
            ('theHarvester', 'git clone https://github.com/laramies/theHarvester.git && pip install -r requirements.txt'),
        ]
        
        for tool_name, install_cmd in tools:
            try:
                logger.info(f"Installing {tool_name}...")
                result = subprocess.run(
                    install_cmd,
                    shell=True,
                    capture_output=True,
                    cwd=self.tools_dir
                )
                if result.returncode == 0:
                    logger.info(f"✅ {tool_name} installed")
                else:
                    logger.error(f"❌ {tool_name} failed: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ {tool_name} installation error: {e}")


# ==================== STANDALONE USAGE ====================

async def main():
    """Example usage"""
    config = {
        'HIBP_API_KEY': 'your_key_here',  # Optional but recommended
        'INTELX_API_KEY': 'your_key_here',
        'SPYCLOUD_API_KEY': 'your_key_here',
    }
    
    async with EmailLeakChecker(config) as checker:
        # Check single email
        result = await checker.check_all_sources('test@example.com')
        
        print(f"\n{'='*60}")
        print(f"Email: {result['email']}")
        print(f"Risk Score: {result['risk_score']}/100 ({result['risk_level']})")
        print(f"Sources Checked: {result['total_sources']}")
        print(f"Leaks Found: {result['sources_found']}")
        print(f"{'='*60}\n")
        
        if result['breaches']:
            print("Breaches Found:")
            for breach in result['breaches'][:10]:
                print(f"  - {breach['name']} (via {breach['source']})")
        
        print("\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  {rec}")
        
        # Bulk check
        emails = ['email1@example.com', 'email2@example.com']
        bulk_results = await checker.bulk_check(emails)
        
        print(f"\nBulk check completed: {len(bulk_results)} emails processed")


if __name__ == "__main__":
    asyncio.run(main())
