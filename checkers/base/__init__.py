"""
Base Checker Class
All service checkers inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class CheckerResult(Enum):
    """Checker result status"""
    SUCCESS = "success"
    FAILURE = "failure"
    CAPTCHA = "captcha"
    RATE_LIMITED = "rate_limited"
    IP_BLOCKED = "ip_blocked"
    ACCOUNT_LOCKED = "account_locked"
    MFA_REQUIRED = "mfa_required"
    ERROR = "error"


@dataclass
class CheckResult:
    """Result from a checker attempt"""
    status: CheckerResult
    email: str
    password: Optional[str] = None
    service: str = ""
    message: str = ""
    session_data: Optional[Dict[str, Any]] = None
    response_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseChecker(ABC):
    """
    Base class for all service checkers
    
    Each checker must implement:
    - check_single(): Check a single email/password combination
    - is_account_exists(): Check if an account exists for an email
    """
    
    def __init__(
        self,
        service_name: str,
        config: Dict[str, Any] = None
    ):
        self.service_name = service_name
        self.config = config or {}
        
        # Rate limiting
        self.max_attempts = self.config.get('max_attempts', 10)
        self.rate_limit_delay = self.config.get('rate_limit_delay', 1.0)
        
        # Proxy configuration
        self.use_proxy = self.config.get('use_proxy', True)
        self.proxy_type = self.config.get('proxy_type', 'residential')
        
        # CAPTCHA handling
        self.captcha_solver = self.config.get('captcha_solver')
        
        logger.info(f"Initialized checker for {service_name}")
    
    @abstractmethod
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """
        Check a single email/password combination
        
        Args:
            email: Target email address
            password: Password to test
            proxy: Proxy to use for the request
            fingerprint: Browser fingerprint to use
        
        Returns:
            CheckResult with status and details
        """
        pass
    
    @abstractmethod
    async def is_account_exists(
        self,
        email: str,
        proxy: Optional[Any] = None
    ) -> bool:
        """
        Check if an account exists for the given email
        
        Args:
            email: Email to check
            proxy: Proxy to use for the request
        
        Returns:
            True if account exists, False otherwise
        """
        pass
    
    async def check_multiple(
        self,
        email: str,
        passwords: List[str],
        proxy_manager: Any = None,
        fingerprint_gen: Any = None
    ) -> List[CheckResult]:
        """
        Check multiple passwords for a single email
        
        Handles rate limiting and proxy rotation automatically
        """
        
        results = []
        current_proxy = None
        
        for i, password in enumerate(passwords[:self.max_attempts]):
            # Get proxy
            if proxy_manager and self.use_proxy:
                current_proxy = await proxy_manager.get_proxy_for_service(
                    self.service_name
                )
            
            # Get fingerprint
            fingerprint = None
            if fingerprint_gen:
                fingerprint = fingerprint_gen.generate()
            
            # Attempt check
            try:
                result = await self.check_single(
                    email=email,
                    password=password,
                    proxy=current_proxy,
                    fingerprint=fingerprint
                )
                
                results.append(result)
                
                # Report proxy result
                if current_proxy and proxy_manager:
                    proxy_manager.report_proxy_result(
                        proxy_id=current_proxy.proxy_id,
                        success=(result.status == CheckerResult.SUCCESS),
                        response_time=result.response_time,
                        service=self.service_name
                    )
                
                # Break if successful
                if result.status == CheckerResult.SUCCESS:
                    logger.info(f"✓ Success: {email} on {self.service_name}")
                    break
                
                # Handle special cases
                if result.status == CheckerResult.IP_BLOCKED:
                    logger.warning(f"IP blocked, rotating proxy...")
                    continue
                
                if result.status == CheckerResult.RATE_LIMITED:
                    logger.warning(f"Rate limited, backing off...")
                    await asyncio.sleep(self.rate_limit_delay * 2)
                
                # Normal rate limiting
                await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error checking {email}: {e}", exc_info=True)
                results.append(CheckResult(
                    status=CheckerResult.ERROR,
                    email=email,
                    password=password,
                    service=self.service_name,
                    message=str(e)
                ))
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get checker statistics"""
        return {
            'service': self.service_name,
            'max_attempts': self.max_attempts,
            'use_proxy': self.use_proxy
        }
