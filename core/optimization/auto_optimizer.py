"""
Auto-Optimization System
Continuously optimizes workers, API calls, and processing based on performance metrics
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import psutil
import numpy as np

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor system performance metrics"""
    
    def __init__(self):
        self.metrics_history = []
        self.current_metrics = {}
    
    def record_metrics(self, metrics: Dict):
        """Record current metrics"""
        metrics['timestamp'] = datetime.utcnow()
        self.metrics_history.append(metrics)
        self.current_metrics = metrics
        
        # Keep last 1000 records
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_average_metric(self, metric_name: str, window_minutes: int = 5) -> float:
        """Get average of a metric over time window"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.get('timestamp', datetime.min) > cutoff
        ]
        
        if not recent_metrics:
            return 0.0
        
        values = [m.get(metric_name, 0) for m in recent_metrics]
        return np.mean(values)
    
    def get_trend(self, metric_name: str, window_minutes: int = 10) -> str:
        """Detect if metric is trending up, down, or stable"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.get('timestamp', datetime.min) > cutoff
        ]
        
        if len(recent_metrics) < 2:
            return "stable"
        
        values = [m.get(metric_name, 0) for m in recent_metrics]
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"


class ResourceOptimizer:
    """Optimize system resources"""
    
    def __init__(self):
        self.min_workers = 1
        self.max_workers = 20
        self.target_cpu = 80.0  # Target 80% CPU usage
        self.target_memory = 85.0  # Target 85% memory usage
    
    def calculate_optimal_workers(self, current_workers: int, cpu_usage: float, memory_usage: float, speed: float, target_speed: float) -> int:
        """Calculate optimal worker count"""
        # If resources are underutilized and speed is low, increase workers
        if cpu_usage < 60 and memory_usage < 70 and speed < target_speed * 0.8:
            return min(self.max_workers, current_workers + 2)
        
        # If resources are maxed out, decrease workers
        if cpu_usage > 90 or memory_usage > 90:
            return max(self.min_workers, current_workers - 1)
        
        # If speed is good but resources are high, decrease by 1
        if speed >= target_speed and (cpu_usage > 85 or memory_usage > 85):
            return max(self.min_workers, current_workers - 1)
        
        # If speed is low and resources are available, increase workers
        if speed < target_speed * 0.7 and cpu_usage < 75 and memory_usage < 75:
            return min(self.max_workers, current_workers + 1)
        
        # Otherwise, keep current workers
        return current_workers
    
    def calculate_optimal_concurrent_limit(self, current_limit: int, api_error_rate: float, speed: float) -> int:
        """Calculate optimal concurrent API limit"""
        min_limit = 10
        max_limit = 200
        
        # If high error rate, reduce concurrency
        if api_error_rate > 0.1:  # More than 10% errors
            return max(min_limit, int(current_limit * 0.8))
        
        # If low error rate and low speed, increase concurrency
        if api_error_rate < 0.02 and speed < 100:
            return min(max_limit, int(current_limit * 1.2))
        
        # Otherwise, keep current limit
        return current_limit
    
    def calculate_optimal_batch_size(self, current_batch: int, memory_usage: float, processing_time: float) -> int:
        """Calculate optimal batch size"""
        min_batch = 100
        max_batch = 10000
        
        # If high memory usage, reduce batch size
        if memory_usage > 85:
            return max(min_batch, int(current_batch * 0.7))
        
        # If low memory and fast processing, increase batch size
        if memory_usage < 60 and processing_time < 10:
            return min(max_batch, int(current_batch * 1.3))
        
        return current_batch


class CacheOptimizer:
    """Optimize caching strategy"""
    
    def __init__(self):
        self.min_ttl = 300  # 5 minutes
        self.max_ttl = 7200  # 2 hours
        self.target_hit_rate = 0.75  # 75% hit rate
    
    def calculate_optimal_ttl(self, current_ttl: int, hit_rate: float, api_call_count: int) -> int:
        """Calculate optimal cache TTL"""
        # If hit rate is low, increase TTL
        if hit_rate < 0.5:
            return min(self.max_ttl, int(current_ttl * 1.5))
        
        # If hit rate is high and many API calls, reduce TTL (fresher data)
        if hit_rate > 0.85 and api_call_count > 1000:
            return max(self.min_ttl, int(current_ttl * 0.8))
        
        return current_ttl
    
    def should_use_cache(self, email: str, last_check_time: Optional[datetime], cache_ttl: int) -> bool:
        """Decide if cache should be used"""
        if not last_check_time:
            return False
        
        age = (datetime.utcnow() - last_check_time).total_seconds()
        return age < cache_ttl


class AutoOptimizer:
    """
    Automatic system optimization
    
    Features:
    - Dynamic worker scaling
    - API concurrency optimization
    - Batch size adjustment
    - Cache TTL optimization
    - Resource balancing
    """
    
    def __init__(self, initial_workers: int = 2, target_speed: float = 100.0):
        self.performance_monitor = PerformanceMonitor()
        self.resource_optimizer = ResourceOptimizer()
        self.cache_optimizer = CacheOptimizer()
        
        # Current settings
        self.settings = {
            'workers': initial_workers,
            'concurrent_limit': 50,
            'batch_size': 1000,
            'cache_ttl': 3600,
            'target_speed': target_speed
        }
        
        # Optimization history
        self.optimization_history = []
        
        # Running state
        self.running = False
    
    async def start(self):
        """Start auto-optimization"""
        self.running = True
        asyncio.create_task(self._optimization_loop())
        logger.info("Auto-optimizer started")
    
    async def stop(self):
        """Stop auto-optimization"""
        self.running = False
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Optimize every minute
                
                # Collect current metrics
                metrics = await self._collect_metrics()
                self.performance_monitor.record_metrics(metrics)
                
                # Run optimization
                optimization_result = await self._optimize(metrics)
                
                # Apply optimizations
                if optimization_result['changes_made']:
                    await self._apply_optimizations(optimization_result)
                    self.optimization_history.append(optimization_result)
            
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
    
    async def _collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Application metrics (would be collected from actual system)
        metrics = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_usage': psutil.disk_usage('/').percent,
            
            # Performance metrics (mocked for now, replace with real data)
            'current_speed': 0,  # emails/sec
            'api_error_rate': 0,  # percentage
            'cache_hit_rate': 0,  # percentage
            'api_call_count': 0,
            'active_workers': self.settings['workers'],
            'concurrent_limit': self.settings['concurrent_limit'],
            'batch_size': self.settings['batch_size'],
            'cache_ttl': self.settings['cache_ttl']
        }
        
        return metrics
    
    async def _optimize(self, metrics: Dict) -> Dict:
        """Run optimization algorithms"""
        changes = {}
        
        # Optimize workers
        optimal_workers = self.resource_optimizer.calculate_optimal_workers(
            current_workers=metrics['active_workers'],
            cpu_usage=metrics['cpu_usage'],
            memory_usage=metrics['memory_usage'],
            speed=metrics['current_speed'],
            target_speed=self.settings['target_speed']
        )
        
        if optimal_workers != self.settings['workers']:
            changes['workers'] = {
                'old': self.settings['workers'],
                'new': optimal_workers,
                'reason': self._get_worker_change_reason(metrics, optimal_workers)
            }
        
        # Optimize concurrent limit
        optimal_concurrent = self.resource_optimizer.calculate_optimal_concurrent_limit(
            current_limit=metrics['concurrent_limit'],
            api_error_rate=metrics['api_error_rate'],
            speed=metrics['current_speed']
        )
        
        if optimal_concurrent != self.settings['concurrent_limit']:
            changes['concurrent_limit'] = {
                'old': self.settings['concurrent_limit'],
                'new': optimal_concurrent,
                'reason': 'API error rate optimization'
            }
        
        # Optimize batch size
        optimal_batch = self.resource_optimizer.calculate_optimal_batch_size(
            current_batch=metrics['batch_size'],
            memory_usage=metrics['memory_usage'],
            processing_time=10.0  # Would be measured
        )
        
        if optimal_batch != self.settings['batch_size']:
            changes['batch_size'] = {
                'old': self.settings['batch_size'],
                'new': optimal_batch,
                'reason': 'Memory usage optimization'
            }
        
        # Optimize cache TTL
        optimal_ttl = self.cache_optimizer.calculate_optimal_ttl(
            current_ttl=metrics['cache_ttl'],
            hit_rate=metrics['cache_hit_rate'],
            api_call_count=metrics['api_call_count']
        )
        
        if optimal_ttl != self.settings['cache_ttl']:
            changes['cache_ttl'] = {
                'old': self.settings['cache_ttl'],
                'new': optimal_ttl,
                'reason': 'Cache hit rate optimization'
            }
        
        return {
            'timestamp': datetime.utcnow(),
            'metrics': metrics,
            'changes': changes,
            'changes_made': len(changes) > 0
        }
    
    def _get_worker_change_reason(self, metrics: Dict, new_workers: int) -> str:
        """Get reason for worker count change"""
        if new_workers > self.settings['workers']:
            if metrics['cpu_usage'] < 60:
                return "Low CPU usage - adding workers for more throughput"
            else:
                return "Speed below target - scaling up workers"
        else:
            if metrics['cpu_usage'] > 90:
                return "High CPU usage - reducing workers to prevent overload"
            elif metrics['memory_usage'] > 90:
                return "High memory usage - scaling down workers"
            else:
                return "Optimizing for better resource utilization"
    
    async def _apply_optimizations(self, optimization_result: Dict):
        """Apply optimization changes"""
        changes = optimization_result['changes']
        
        for setting_name, change_info in changes.items():
            old_value = change_info['old']
            new_value = change_info['new']
            reason = change_info['reason']
            
            self.settings[setting_name] = new_value
            
            logger.info(f"Optimized {setting_name}: {old_value} → {new_value} ({reason})")
        
        # Notify about changes (would integrate with TelegramNotifier)
        logger.info(f"Applied {len(changes)} optimizations")
    
    def get_current_settings(self) -> Dict:
        """Get current optimized settings"""
        return self.settings.copy()
    
    def get_optimization_report(self) -> Dict:
        """Get optimization report"""
        if not self.optimization_history:
            return {'optimizations': 0, 'message': 'No optimizations yet'}
        
        recent = self.optimization_history[-10:]
        
        total_changes = sum(len(opt['changes']) for opt in recent)
        
        return {
            'total_optimizations': len(self.optimization_history),
            'recent_changes': total_changes,
            'current_settings': self.settings,
            'performance_trend': self._calculate_performance_trend(),
            'recommendations': self._get_recommendations()
        }
    
    def _calculate_performance_trend(self) -> Dict:
        """Calculate performance trend"""
        speed_trend = self.performance_monitor.get_trend('current_speed', window_minutes=30)
        cpu_trend = self.performance_monitor.get_trend('cpu_usage', window_minutes=30)
        
        avg_speed = self.performance_monitor.get_average_metric('current_speed', window_minutes=30)
        
        return {
            'speed_trend': speed_trend,
            'cpu_trend': cpu_trend,
            'avg_speed_30min': avg_speed
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        current = self.performance_monitor.current_metrics
        
        if current.get('cpu_usage', 0) > 90:
            recommendations.append("Consider upgrading CPU or reducing worker count")
        
        if current.get('memory_usage', 0) > 90:
            recommendations.append("Consider adding more RAM or reducing batch sizes")
        
        if current.get('cache_hit_rate', 0) < 0.5:
            recommendations.append("Cache hit rate is low - consider increasing TTL")
        
        if current.get('api_error_rate', 0) > 0.1:
            recommendations.append("High API error rate - reduce concurrency or check API limits")
        
        if not recommendations:
            recommendations.append("System performing optimally")
        
        return recommendations


# ==================== USAGE EXAMPLE ====================

async def main():
    """Example usage"""
    optimizer = AutoOptimizer(initial_workers=2, target_speed=100.0)
    
    await optimizer.start()
    
    # Let it run for a while
    await asyncio.sleep(120)
    
    # Get current settings
    settings = optimizer.get_current_settings()
    print(f"Current settings: {settings}")
    
    # Get optimization report
    report = optimizer.get_optimization_report()
    print(f"Optimization report: {report}")
    
    await optimizer.stop()


if __name__ == "__main__":
    asyncio.run(main())
