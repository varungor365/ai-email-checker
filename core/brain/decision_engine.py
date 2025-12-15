"""
Decision Engine - Core AI Logic
Makes intelligent decisions about attack strategies, routing, and adaptation
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions the engine can make"""
    PASSWORD_STRATEGY = "password_strategy"
    PROXY_SELECTION = "proxy_selection"
    CHECKER_ROUTING = "checker_routing"
    CAPTCHA_HANDLING = "captcha_handling"
    RATE_LIMIT_RESPONSE = "rate_limit_response"
    FAILURE_RECOVERY = "failure_recovery"
    RESOURCE_ALLOCATION = "resource_allocation"


class AttackStrategy(Enum):
    """Available attack strategies"""
    LEAKED_PASSWORDS = "leaked_passwords"
    MUTATION_RULES = "mutation_rules"
    LLM_GENERATED = "llm_generated"
    COMMON_PASSWORDS = "common_passwords"
    PERSONALIZED = "personalized"
    HYBRID = "hybrid"


@dataclass
class DecisionContext:
    """Context information for making decisions"""
    target_service: str
    target_email: str
    available_resources: Dict[str, Any]
    historical_data: Dict[str, Any]
    current_state: Dict[str, Any]
    constraints: Dict[str, Any]
    
    def __post_init__(self):
        self.timestamp = datetime.utcnow()


@dataclass
class Decision:
    """A decision made by the engine"""
    decision_type: DecisionType
    action: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class DecisionEngine:
    """
    AI-powered decision engine that makes intelligent choices about:
    - Which passwords to try and in what order
    - Which proxies to use
    - How to handle failures
    - When to escalate or abort
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.decision_history: List[Decision] = []
        self.learning_enabled = self.config.get('learning_enabled', True)
        self.ml_model = None  # Will be loaded if available
        
        # Performance tracking
        self.strategy_success_rates: Dict[str, float] = {}
        self.service_intelligence: Dict[str, Dict] = {}
        
        logger.info("Decision Engine initialized")
    
    async def decide_password_strategy(
        self, 
        context: DecisionContext
    ) -> Decision:
        """
        Decide which password strategy to use based on available intelligence
        
        Logic:
        1. If breach data available -> use leaked passwords first
        2. If no breach data but OSINT available -> use personalized
        3. Apply mutation rules to successful patterns
        4. Use LLM for intelligent generation if available
        5. Fall back to common passwords
        """
        
        has_breach_data = context.available_resources.get('breach_data', False)
        has_osint_data = context.available_resources.get('osint_data', False)
        has_llm = context.available_resources.get('llm_available', False)
        
        # Check historical success for this service
        service_history = self.service_intelligence.get(
            context.target_service, 
            {}
        )
        best_strategy = service_history.get('best_strategy')
        
        # Decision logic
        if best_strategy and self.learning_enabled:
            # Use learned best strategy for this service
            strategy = AttackStrategy[best_strategy.upper()]
            confidence = service_history.get('confidence', 0.7)
            reasoning = f"Learned strategy based on {service_history.get('sample_size', 0)} previous attempts"
            
        elif has_breach_data:
            strategy = AttackStrategy.LEAKED_PASSWORDS
            confidence = 0.85
            reasoning = "Breach data available - highest success probability"
            
        elif has_osint_data and has_llm:
            strategy = AttackStrategy.HYBRID
            confidence = 0.75
            reasoning = "OSINT + LLM available for intelligent generation"
            
        elif has_osint_data:
            strategy = AttackStrategy.PERSONALIZED
            confidence = 0.65
            reasoning = "OSINT data available for personalization"
            
        else:
            strategy = AttackStrategy.COMMON_PASSWORDS
            confidence = 0.40
            reasoning = "No intelligence available - using common patterns"
        
        decision = Decision(
            decision_type=DecisionType.PASSWORD_STRATEGY,
            action=strategy.value,
            parameters={
                'strategy': strategy.value,
                'apply_mutations': has_breach_data or has_osint_data,
                'use_llm': has_llm,
                'max_attempts': self._calculate_max_attempts(context)
            },
            confidence=confidence,
            reasoning=reasoning
        )
        
        self._record_decision(decision)
        return decision
    
    async def decide_proxy_selection(
        self, 
        context: DecisionContext,
        failed_proxies: List[str] = None
    ) -> Decision:
        """
        Intelligently select the best proxy based on:
        - Target service requirements (residential vs datacenter)
        - Proxy health and performance
        - Geographic requirements
        - Cost optimization
        """
        
        failed_proxies = failed_proxies or []
        available_proxies = context.available_resources.get('proxies', [])
        
        # Filter out failed proxies
        healthy_proxies = [
            p for p in available_proxies 
            if p['id'] not in failed_proxies
        ]
        
        if not healthy_proxies:
            return Decision(
                decision_type=DecisionType.PROXY_SELECTION,
                action="ACQUIRE_NEW_PROXIES",
                parameters={'count': 10, 'type': 'residential'},
                confidence=1.0,
                reasoning="No healthy proxies available"
            )
        
        # Service-specific proxy requirements
        service_config = self.config.get('services', {}).get(
            context.target_service, 
            {}
        )
        preferred_type = service_config.get('proxy_type', 'residential')
        
        # Score proxies
        scored_proxies = []
        for proxy in healthy_proxies:
            score = self._score_proxy(proxy, preferred_type, context)
            scored_proxies.append((proxy, score))
        
        # Sort by score (highest first)
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        best_proxy = scored_proxies[0][0]
        
        decision = Decision(
            decision_type=DecisionType.PROXY_SELECTION,
            action="USE_PROXY",
            parameters={
                'proxy_id': best_proxy['id'],
                'proxy_type': best_proxy['type'],
                'location': best_proxy.get('location', 'unknown'),
                'backup_proxies': [p[0]['id'] for p in scored_proxies[1:4]]
            },
            confidence=scored_proxies[0][1],
            reasoning=f"Selected {best_proxy['type']} proxy with score {scored_proxies[0][1]:.2f}"
        )
        
        self._record_decision(decision)
        return decision
    
    async def decide_captcha_handling(
        self, 
        context: DecisionContext,
        captcha_type: str
    ) -> Decision:
        """
        Decide how to handle CAPTCHA challenges:
        - Which solving service to use
        - Whether to retry or skip
        - Cost vs success probability tradeoff
        """
        
        available_solvers = context.available_resources.get('captcha_solvers', [])
        
        # Map CAPTCHA types to best solvers
        solver_preferences = {
            'recaptcha_v2': ['2captcha', 'anti-captcha', 'capmonster'],
            'recaptcha_v3': ['anti-captcha', '2captcha'],
            'hcaptcha': ['capmonster', '2captcha', 'anti-captcha'],
            'funcaptcha': ['anti-captcha', 'capmonster'],
            'geetest': ['capmonster', '2captcha'],
            'image': ['2captcha', 'anti-captcha']
        }
        
        preferred_solvers = solver_preferences.get(
            captcha_type.lower(), 
            ['2captcha']
        )
        
        # Find available solver from preferences
        selected_solver = None
        for solver in preferred_solvers:
            if solver in available_solvers:
                selected_solver = solver
                break
        
        if not selected_solver:
            # No solver available - mark target as high protection
            return Decision(
                decision_type=DecisionType.CAPTCHA_HANDLING,
                action="SKIP_TARGET",
                parameters={
                    'reason': 'no_solver_available',
                    'mark_target': 'high_protection'
                },
                confidence=0.9,
                reasoning=f"No solver available for {captcha_type}"
            )
        
        # Calculate expected success probability
        solver_stats = context.historical_data.get('solver_stats', {})
        success_rate = solver_stats.get(selected_solver, {}).get('success_rate', 0.85)
        
        decision = Decision(
            decision_type=DecisionType.CAPTCHA_HANDLING,
            action="SOLVE_CAPTCHA",
            parameters={
                'solver': selected_solver,
                'captcha_type': captcha_type,
                'max_retries': 2,
                'timeout': 120,
                'fallback_solver': preferred_solvers[1] if len(preferred_solvers) > 1 else None
            },
            confidence=success_rate,
            reasoning=f"Using {selected_solver} with {success_rate:.0%} success rate"
        )
        
        self._record_decision(decision)
        return decision
    
    async def decide_failure_recovery(
        self,
        context: DecisionContext,
        failure_type: str,
        failure_count: int
    ) -> Decision:
        """
        Decide how to recover from failures:
        - Retry with different strategy
        - Switch proxy
        - Escalate to different checker
        - Abort and mark target
        """
        
        max_retries = self.config.get('max_retries', 3)
        
        if failure_count >= max_retries:
            return Decision(
                decision_type=DecisionType.FAILURE_RECOVERY,
                action="ABORT",
                parameters={
                    'reason': 'max_retries_exceeded',
                    'mark_target': 'failed',
                    'failure_type': failure_type
                },
                confidence=1.0,
                reasoning=f"Exceeded max retries ({max_retries})"
            )
        
        # Different recovery strategies based on failure type
        recovery_strategies = {
            'ip_blocked': 'ROTATE_PROXY',
            'rate_limited': 'BACKOFF_RETRY',
            'captcha_failed': 'CHANGE_SOLVER',
            'invalid_credentials': 'NEXT_PASSWORD',
            'account_locked': 'ABORT',
            'service_down': 'RETRY_LATER',
            'network_error': 'RETRY_IMMEDIATELY'
        }
        
        action = recovery_strategies.get(failure_type, 'RETRY_WITH_BACKOFF')
        
        # Calculate backoff time
        backoff = min(2 ** failure_count, 60)  # Exponential backoff, max 60s
        
        decision = Decision(
            decision_type=DecisionType.FAILURE_RECOVERY,
            action=action,
            parameters={
                'failure_type': failure_type,
                'failure_count': failure_count,
                'backoff_seconds': backoff,
                'change_proxy': failure_type in ['ip_blocked', 'rate_limited'],
                'change_fingerprint': failure_type == 'ip_blocked'
            },
            confidence=0.7,
            reasoning=f"Recovery strategy for {failure_type}: {action}"
        )
        
        self._record_decision(decision)
        return decision
    
    def _score_proxy(
        self, 
        proxy: Dict, 
        preferred_type: str,
        context: DecisionContext
    ) -> float:
        """Score a proxy based on multiple factors"""
        score = 0.5  # Base score
        
        # Type preference
        if proxy['type'] == preferred_type:
            score += 0.3
        
        # Health status
        health = proxy.get('health_score', 0.5)
        score += health * 0.2
        
        # Speed
        response_time = proxy.get('avg_response_time', 1000)
        if response_time < 500:
            score += 0.15
        elif response_time < 1000:
            score += 0.10
        
        # Success rate
        success_rate = proxy.get('success_rate', 0.5)
        score += success_rate * 0.15
        
        # Cost optimization (prefer cheaper if similar quality)
        cost_factor = 1.0 - (proxy.get('cost_per_request', 0.01) / 0.05)
        score += cost_factor * 0.05
        
        return min(score, 1.0)
    
    def _calculate_max_attempts(self, context: DecisionContext) -> int:
        """Calculate maximum password attempts based on service and context"""
        service_config = self.config.get('services', {}).get(
            context.target_service,
            {}
        )
        
        # Base attempts
        base_attempts = service_config.get('max_attempts', 10)
        
        # Adjust based on available resources
        if context.available_resources.get('breach_data'):
            # More attempts if we have good data
            return base_attempts * 2
        
        return base_attempts
    
    def _record_decision(self, decision: Decision):
        """Record decision for learning and analytics"""
        self.decision_history.append(decision)
        
        # Keep only recent decisions (memory management)
        if len(self.decision_history) > 10000:
            self.decision_history = self.decision_history[-5000:]
    
    async def learn_from_outcome(
        self,
        decision: Decision,
        outcome: Dict[str, Any]
    ):
        """
        Learn from decision outcomes to improve future decisions
        This is where the "AI" learns and adapts
        """
        
        if not self.learning_enabled:
            return
        
        success = outcome.get('success', False)
        service = outcome.get('service')
        
        if decision.decision_type == DecisionType.PASSWORD_STRATEGY and service:
            # Update service intelligence
            if service not in self.service_intelligence:
                self.service_intelligence[service] = {
                    'attempts': 0,
                    'successes': 0,
                    'strategy_performance': {}
                }
            
            service_data = self.service_intelligence[service]
            service_data['attempts'] += 1
            
            if success:
                service_data['successes'] += 1
                strategy = decision.parameters.get('strategy')
                
                if strategy not in service_data['strategy_performance']:
                    service_data['strategy_performance'][strategy] = {
                        'attempts': 0,
                        'successes': 0
                    }
                
                service_data['strategy_performance'][strategy]['attempts'] += 1
                service_data['strategy_performance'][strategy]['successes'] += 1
                
                # Update best strategy
                best_strategy = max(
                    service_data['strategy_performance'].items(),
                    key=lambda x: x[1]['successes'] / max(x[1]['attempts'], 1)
                )
                
                service_data['best_strategy'] = best_strategy[0]
                service_data['confidence'] = (
                    best_strategy[1]['successes'] / best_strategy[1]['attempts']
                )
                service_data['sample_size'] = service_data['attempts']
        
        logger.debug(
            f"Learned from outcome: {decision.decision_type.value} "
            f"-> {'success' if success else 'failure'}"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics and performance metrics"""
        return {
            'total_decisions': len(self.decision_history),
            'service_intelligence': self.service_intelligence,
            'decision_type_distribution': self._get_decision_distribution(),
            'learning_enabled': self.learning_enabled
        }
    
    def _get_decision_distribution(self) -> Dict[str, int]:
        """Get distribution of decision types"""
        distribution = {}
        for decision in self.decision_history:
            decision_type = decision.decision_type.value
            distribution[decision_type] = distribution.get(decision_type, 0) + 1
        return distribution
