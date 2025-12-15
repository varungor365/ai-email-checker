"""
Advanced Proxy Management System
Automated proxy acquisition, rotation, health checking, and load balancing
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class ProxyType(Enum):
    """Types of proxies"""
    RESIDENTIAL = "residential"
    MOBILE = "mobile"
    DATACENTER = "datacenter"
    TOR = "tor"


class ProxyProtocol(Enum):
    """Proxy protocols"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class Proxy:
    """Proxy instance with health and performance tracking"""
    proxy_id: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    proxy_type: ProxyType = ProxyType.DATACENTER
    location: Optional[str] = None
    
    # Health tracking
    is_active: bool = True
    health_score: float = 1.0
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    
    # Blacklist tracking
    blacklisted_services: Set[str] = field(default_factory=set)
    
    # Cost tracking (for paid proxies)
    cost_per_request: float = 0.0
    requests_made: int = 0
    
    def get_url(self) -> str:
        """Get proxy URL for use in requests"""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        else:
            auth = ""
        
        return f"{self.protocol.value}://{auth}{self.host}:{self.port}"
    
    def record_success(self, response_time: float):
        """Record a successful request"""
        self.success_count += 1
        self.requests_made += 1
        self.last_used = datetime.utcnow()
        
        # Update average response time (moving average)
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (
                self.avg_response_time * 0.7 + response_time * 0.3
            )
        
        # Update health score
        self._update_health_score()
    
    def record_failure(self, service: Optional[str] = None):
        """Record a failed request"""
        self.failure_count += 1
        self.requests_made += 1
        self.last_used = datetime.utcnow()
        
        if service:
            self.blacklisted_services.add(service)
        
        self._update_health_score()
        
        # Deactivate if too many failures
        if self.failure_count > 10 and self.success_rate < 0.3:
            self.is_active = False
            logger.warning(f"Deactivated proxy {self.proxy_id} due to high failure rate")
    
    def _update_health_score(self):
        """Calculate health score based on performance"""
        if self.requests_made == 0:
            self.health_score = 1.0
            return
        
        # Success rate component (60% weight)
        success_rate_score = self.success_rate * 0.6
        
        # Response time component (20% weight)
        # Penalize slow proxies (>2s is bad)
        response_score = max(0, 1 - (self.avg_response_time / 2000)) * 0.2
        
        # Freshness component (20% weight)
        if self.last_used:
            hours_since_use = (datetime.utcnow() - self.last_used).total_seconds() / 3600
            freshness_score = max(0, 1 - (hours_since_use / 24)) * 0.2
        else:
            freshness_score = 0.2
        
        self.health_score = success_rate_score + response_score + freshness_score
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.requests_made == 0:
            return 1.0
        return self.success_count / self.requests_made
    
    def is_blacklisted_for(self, service: str) -> bool:
        """Check if proxy is blacklisted for a service"""
        return service in self.blacklisted_services
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'proxy_id': self.proxy_id,
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol.value,
            'type': self.proxy_type.value,
            'location': self.location,
            'is_active': self.is_active,
            'health_score': round(self.health_score, 2),
            'success_rate': round(self.success_rate, 2),
            'avg_response_time': round(self.avg_response_time, 0),
            'requests_made': self.requests_made
        }


class ProxyPool:
    """
    Manages a pool of proxies with health checking and rotation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.proxies: Dict[str, Proxy] = {}
        
        # Health checking
        self.health_check_interval = self.config.get('health_check_interval', 300)
        self.health_check_task: Optional[asyncio.Task] = None
        
        logger.info("Proxy Pool initialized")
    
    def add_proxy(self, proxy: Proxy):
        """Add a proxy to the pool"""
        self.proxies[proxy.proxy_id] = proxy
        logger.debug(f"Added proxy {proxy.proxy_id} to pool")
    
    def remove_proxy(self, proxy_id: str):
        """Remove a proxy from the pool"""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]
            logger.debug(f"Removed proxy {proxy_id} from pool")
    
    def get_proxy(
        self,
        service: Optional[str] = None,
        preferred_type: Optional[ProxyType] = None,
        exclude_ids: List[str] = None
    ) -> Optional[Proxy]:
        """
        Get the best proxy for a request
        
        Selection criteria:
        1. Not blacklisted for the service
        2. Active and healthy
        3. Matches preferred type
        4. Highest health score
        5. Least recently used
        """
        
        exclude_ids = exclude_ids or []
        
        # Filter proxies
        candidates = [
            p for p in self.proxies.values()
            if (
                p.is_active
                and p.proxy_id not in exclude_ids
                and (not service or not p.is_blacklisted_for(service))
                and (not preferred_type or p.proxy_type == preferred_type)
            )
        ]
        
        if not candidates:
            logger.warning("No suitable proxies available")
            return None
        
        # Sort by health score and last used time
        candidates.sort(
            key=lambda p: (p.health_score, -(p.last_used.timestamp() if p.last_used else 0)),
            reverse=True
        )
        
        return candidates[0]
    
    def get_random_proxy(
        self,
        service: Optional[str] = None,
        proxy_type: Optional[ProxyType] = None
    ) -> Optional[Proxy]:
        """Get a random proxy from healthy proxies"""
        
        candidates = [
            p for p in self.proxies.values()
            if (
                p.is_active
                and p.health_score > 0.5
                and (not service or not p.is_blacklisted_for(service))
                and (not proxy_type or p.proxy_type == proxy_type)
            )
        ]
        
        if not candidates:
            return None
        
        return random.choice(candidates)
    
    async def health_check_all(self):
        """Check health of all proxies"""
        logger.info("Starting health check for all proxies")
        
        tasks = [
            self._check_proxy_health(proxy)
            for proxy in self.proxies.values()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Report health statistics
        active_count = sum(1 for p in self.proxies.values() if p.is_active)
        avg_health = sum(p.health_score for p in self.proxies.values()) / max(len(self.proxies), 1)
        
        logger.info(
            f"Health check complete: {active_count}/{len(self.proxies)} active, "
            f"avg health: {avg_health:.2f}"
        )
    
    async def _check_proxy_health(self, proxy: Proxy):
        """Check health of a single proxy"""
        
        test_url = self.config.get('health_check_url', 'https://httpbin.org/ip')
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    test_url,
                    proxy=proxy.get_url(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                        proxy.record_success(response_time)
                        proxy.last_checked = datetime.utcnow()
                    else:
                        proxy.record_failure()
        
        except Exception as e:
            logger.debug(f"Proxy {proxy.proxy_id} health check failed: {e}")
            proxy.record_failure()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pool statistics"""
        
        if not self.proxies:
            return {
                'total': 0,
                'active': 0,
                'by_type': {},
                'avg_health': 0
            }
        
        by_type = {}
        for proxy in self.proxies.values():
            proxy_type = proxy.proxy_type.value
            if proxy_type not in by_type:
                by_type[proxy_type] = {'total': 0, 'active': 0}
            
            by_type[proxy_type]['total'] += 1
            if proxy.is_active:
                by_type[proxy_type]['active'] += 1
        
        return {
            'total': len(self.proxies),
            'active': sum(1 for p in self.proxies.values() if p.is_active),
            'by_type': by_type,
            'avg_health': sum(p.health_score for p in self.proxies.values()) / len(self.proxies)
        }


class ProxyManager:
    """
    High-level proxy management with automatic acquisition and rotation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.pool = ProxyPool(config)
        
        # Proxy acquisition APIs
        self.acquisition_apis = self.config.get('acquisition_apis', {})
        
        # Auto-scaling
        self.min_proxies = self.config.get('min_proxies', 10)
        self.max_proxies = self.config.get('max_proxies', 100)
        self.auto_scale_enabled = self.config.get('auto_scale', True)
        
        logger.info("Proxy Manager initialized")
    
    async def initialize(self):
        """Initialize the proxy manager with initial proxies"""
        
        # Load proxies from config
        static_proxies = self.config.get('static_proxies', [])
        for proxy_data in static_proxies:
            proxy = Proxy(**proxy_data)
            self.pool.add_proxy(proxy)
        
        # Acquire additional proxies if needed
        if len(self.pool.proxies) < self.min_proxies:
            needed = self.min_proxies - len(self.pool.proxies)
            await self.acquire_proxies(needed)
        
        # Start health checking
        await self.pool.health_check_all()
        
        logger.info(f"Proxy Manager initialized with {len(self.pool.proxies)} proxies")
    
    async def acquire_proxies(
        self,
        count: int,
        proxy_type: ProxyType = ProxyType.RESIDENTIAL
    ) -> int:
        """
        Acquire new proxies from configured APIs
        
        Returns:
            Number of proxies acquired
        """
        
        logger.info(f"Acquiring {count} {proxy_type.value} proxies")
        
        # This would integrate with real proxy APIs
        # For now, simulate with placeholder
        
        acquired = 0
        # TODO: Integrate with real APIs:
        # - Bright Data
        # - Smartproxy
        # - Oxylabs
        # - ProxyBroker for free proxies
        
        logger.info(f"Acquired {acquired} proxies")
        return acquired
    
    async def get_proxy_for_service(
        self,
        service: str,
        exclude_ids: List[str] = None
    ) -> Optional[Proxy]:
        """Get the best proxy for a specific service"""
        
        # Check service requirements
        service_config = self.config.get('services', {}).get(service, {})
        preferred_type = ProxyType(service_config.get('proxy_type', 'residential'))
        
        proxy = self.pool.get_proxy(
            service=service,
            preferred_type=preferred_type,
            exclude_ids=exclude_ids
        )
        
        # Auto-scale if running low
        if self.auto_scale_enabled:
            active_count = sum(1 for p in self.pool.proxies.values() if p.is_active)
            if active_count < self.min_proxies:
                asyncio.create_task(self.acquire_proxies(self.min_proxies - active_count))
        
        return proxy
    
    def report_proxy_result(
        self,
        proxy_id: str,
        success: bool,
        response_time: float = 0,
        service: Optional[str] = None
    ):
        """Report the result of using a proxy"""
        
        proxy = self.pool.proxies.get(proxy_id)
        if not proxy:
            return
        
        if success:
            proxy.record_success(response_time)
        else:
            proxy.record_failure(service)
