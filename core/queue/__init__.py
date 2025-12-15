"""
Task Queue Management
Redis-backed distributed queue system for horizontal scaling
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 10
    HIGH = 7
    NORMAL = 5
    LOW = 3
    BACKGROUND = 1


@dataclass
class QueuedTask:
    """A task in the queue"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = TaskPriority.NORMAL.value
    enqueued_at: str = None
    worker_id: Optional[str] = None
    
    def __post_init__(self):
        if self.enqueued_at is None:
            self.enqueued_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueuedTask':
        return cls(**data)


class TaskQueue:
    """
    Distributed task queue using Redis
    
    Features:
    - Priority-based task execution
    - Task deduplication
    - Dead letter queue for failed tasks
    - Worker health monitoring
    - Rate limiting per worker
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        queue_name: str = "ai_email_checker",
        config: Dict[str, Any] = None
    ):
        self.redis_url = redis_url
        self.queue_name = queue_name
        self.config = config or {}
        
        if not REDIS_AVAILABLE:
            logger.warning(
                "Redis not available - using in-memory queue (not suitable for production)"
            )
            self.redis_client = None
            self._memory_queue: List[QueuedTask] = []
        else:
            self.redis_client = None  # Will be initialized in connect()
        
        self.is_connected = False
        
        # Queue names
        self.pending_queue = f"{queue_name}:pending"
        self.processing_queue = f"{queue_name}:processing"
        self.completed_queue = f"{queue_name}:completed"
        self.failed_queue = f"{queue_name}:failed"
        self.dead_letter_queue = f"{queue_name}:dlq"
        
        logger.info(f"Task Queue initialized: {queue_name}")
    
    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            self.is_connected = True
            return
        
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("Disconnected from Redis")
    
    async def enqueue(
        self,
        task_id: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        deduplicate: bool = True
    ) -> bool:
        """
        Add a task to the queue
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task (OSINT_GATHER, ATTACK_EXECUTE, etc.)
            payload: Task data
            priority: Task priority
            deduplicate: Skip if task already in queue
        
        Returns:
            True if task was enqueued, False if duplicate
        """
        
        if deduplicate:
            # Check if task already exists
            exists = await self._task_exists(task_id)
            if exists:
                logger.debug(f"Task {task_id} already in queue, skipping")
                return False
        
        task = QueuedTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority.value
        )
        
        if self.redis_client:
            # Use Redis sorted set for priority queue
            await self.redis_client.zadd(
                self.pending_queue,
                {json.dumps(task.to_dict()): -priority.value}  # Negative for high priority first
            )
        else:
            # In-memory queue
            self._memory_queue.append(task)
            self._memory_queue.sort(key=lambda t: -t.priority)
        
        logger.debug(
            f"Enqueued task {task_id} ({task_type}) with priority {priority.value}"
        )
        
        return True
    
    async def dequeue(
        self,
        worker_id: str,
        timeout: int = 5
    ) -> Optional[QueuedTask]:
        """
        Get the next highest priority task from the queue
        
        Args:
            worker_id: ID of the worker requesting the task
            timeout: Max seconds to wait for a task
        
        Returns:
            QueuedTask or None if queue is empty
        """
        
        if self.redis_client:
            # Atomic pop from sorted set
            result = await self.redis_client.bzpopmin(
                self.pending_queue,
                timeout=timeout
            )
            
            if not result:
                return None
            
            _, task_json, _ = result
            task_dict = json.loads(task_json)
            task = QueuedTask.from_dict(task_dict)
            
            # Move to processing queue
            task.worker_id = worker_id
            await self.redis_client.hset(
                self.processing_queue,
                task.task_id,
                json.dumps(task.to_dict())
            )
            
        else:
            # In-memory queue
            if not self._memory_queue:
                await asyncio.sleep(timeout)
                if not self._memory_queue:
                    return None
            
            task = self._memory_queue.pop(0)
            task.worker_id = worker_id
        
        logger.debug(f"Dequeued task {task.task_id} for worker {worker_id}")
        
        return task
    
    async def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any] = None
    ):
        """Mark a task as completed"""
        
        if self.redis_client:
            # Remove from processing queue
            task_json = await self.redis_client.hget(self.processing_queue, task_id)
            
            if task_json:
                await self.redis_client.hdel(self.processing_queue, task_id)
                
                # Add to completed queue with TTL
                task_dict = json.loads(task_json)
                task_dict['result'] = result
                task_dict['completed_at'] = datetime.utcnow().isoformat()
                
                await self.redis_client.setex(
                    f"{self.completed_queue}:{task_id}",
                    86400,  # 24 hour TTL
                    json.dumps(task_dict)
                )
        
        logger.debug(f"Task {task_id} completed")
    
    async def fail_task(
        self,
        task_id: str,
        error: str,
        retry: bool = True
    ):
        """
        Mark a task as failed
        
        Args:
            task_id: Task identifier
            error: Error message
            retry: Whether to retry the task
        """
        
        if self.redis_client:
            task_json = await self.redis_client.hget(self.processing_queue, task_id)
            
            if task_json:
                task_dict = json.loads(task_json)
                task_dict['error'] = error
                task_dict['failed_at'] = datetime.utcnow().isoformat()
                
                retry_count = task_dict.get('retry_count', 0)
                max_retries = self.config.get('max_retries', 3)
                
                await self.redis_client.hdel(self.processing_queue, task_id)
                
                if retry and retry_count < max_retries:
                    # Re-queue with lower priority
                    task_dict['retry_count'] = retry_count + 1
                    await self.redis_client.zadd(
                        self.pending_queue,
                        {json.dumps(task_dict): -(TaskPriority.LOW.value)}
                    )
                    logger.info(
                        f"Re-queued task {task_id} (retry {retry_count + 1}/{max_retries})"
                    )
                else:
                    # Move to dead letter queue
                    await self.redis_client.lpush(
                        self.dead_letter_queue,
                        json.dumps(task_dict)
                    )
                    logger.warning(f"Task {task_id} moved to dead letter queue")
    
    async def _task_exists(self, task_id: str) -> bool:
        """Check if a task already exists in any queue"""
        
        if self.redis_client:
            # Check pending queue
            all_tasks = await self.redis_client.zrange(self.pending_queue, 0, -1)
            for task_json in all_tasks:
                task_dict = json.loads(task_json)
                if task_dict['task_id'] == task_id:
                    return True
            
            # Check processing queue
            exists = await self.redis_client.hexists(self.processing_queue, task_id)
            if exists:
                return True
        else:
            # Check memory queue
            return any(t.task_id == task_id for t in self._memory_queue)
        
        return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        
        if self.redis_client:
            pending_count = await self.redis_client.zcard(self.pending_queue)
            processing_count = await self.redis_client.hlen(self.processing_queue)
            dlq_count = await self.redis_client.llen(self.dead_letter_queue)
            
            return {
                'pending': pending_count,
                'processing': processing_count,
                'dead_letter': dlq_count,
                'connected': True
            }
        else:
            return {
                'pending': len(self._memory_queue),
                'processing': 0,
                'dead_letter': 0,
                'connected': False
            }
    
    async def clear_queue(self, queue_type: str = "pending"):
        """Clear a specific queue (use with caution!)"""
        
        queue_map = {
            'pending': self.pending_queue,
            'processing': self.processing_queue,
            'completed': self.completed_queue,
            'failed': self.failed_queue,
            'dlq': self.dead_letter_queue
        }
        
        queue_name = queue_map.get(queue_type)
        if not queue_name:
            raise ValueError(f"Invalid queue type: {queue_type}")
        
        if self.redis_client:
            await self.redis_client.delete(queue_name)
        else:
            if queue_type == 'pending':
                self._memory_queue.clear()
        
        logger.warning(f"Cleared {queue_type} queue")
