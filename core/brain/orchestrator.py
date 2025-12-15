"""
Task Orchestrator - Workflow Management
Coordinates complex multi-step attack chains
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

from .decision_engine import DecisionEngine, DecisionContext

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Types of tasks in the workflow"""
    OSINT_GATHER = "osint_gather"
    SERVICE_DISCOVER = "service_discover"
    BREACH_CHECK = "breach_check"
    PASSWORD_GENERATE = "password_generate"
    ATTACK_EXECUTE = "attack_execute"
    RESULT_VALIDATE = "result_validate"
    RESULT_STORE = "result_store"
    CLEANUP = "cleanup"


@dataclass
class Task:
    """Individual task in a workflow"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.OSINT_GATHER
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type.value,
            'target': self.target,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retry_count': self.retry_count
        }


@dataclass
class Workflow:
    """A complete workflow for processing an email target"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_email: str = ""
    tasks: List[Task] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(self, task: Task):
        """Add a task to the workflow"""
        self.tasks.append(task)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (all dependencies met)"""
        ready_tasks = []
        completed_task_ids = {
            t.task_id for t in self.tasks 
            if t.status == TaskStatus.COMPLETED
        }
        
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = all(
                dep_id in completed_task_ids 
                for dep_id in task.dependencies
            )
            
            if dependencies_met:
                ready_tasks.append(task)
        
        return ready_tasks
    
    def is_complete(self) -> bool:
        """Check if all tasks in the workflow are complete"""
        return all(
            t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            for t in self.tasks
        )


class TaskOrchestrator:
    """
    Orchestrates complex multi-step workflows for each email target
    
    Workflow Example:
    1. OSINT_Gather (collect breach data, personal info)
    2. Service_Discover (find which services the email is registered on)
    3. Attack_Execute (attempt login on each service)
    4. Result_Store (save successful credentials)
    """
    
    def __init__(
        self, 
        decision_engine: DecisionEngine,
        config: Dict[str, Any] = None
    ):
        self.decision_engine = decision_engine
        self.config = config or {}
        
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_handlers: Dict[TaskType, Callable] = {}
        
        # Performance tracking
        self.workflows_completed = 0
        self.workflows_failed = 0
        
        logger.info("Task Orchestrator initialized")
    
    def register_handler(self, task_type: TaskType, handler: Callable):
        """Register a handler function for a task type"""
        self.workflow_handlers[task_type] = handler
        logger.debug(f"Registered handler for {task_type.value}")
    
    async def create_workflow(
        self, 
        target_email: str,
        services: List[str] = None,
        custom_tasks: List[Task] = None
    ) -> Workflow:
        """
        Create a complete workflow for processing an email target
        
        The workflow will include:
        1. OSINT gathering
        2. Service discovery (or use provided services)
        3. Attack execution for each service
        4. Result validation and storage
        """
        
        workflow = Workflow(target_email=target_email)
        
        if custom_tasks:
            # Use custom task list
            for task in custom_tasks:
                workflow.add_task(task)
        else:
            # Create standard workflow
            
            # 1. OSINT Gathering (no dependencies)
            osint_task = Task(
                task_type=TaskType.OSINT_GATHER,
                target=target_email,
                parameters={
                    'sources': ['dehashed', 'intelx', 'breachdirectory'],
                    'include_personal_info': True
                },
                priority=10
            )
            workflow.add_task(osint_task)
            
            # 2. Service Discovery (depends on OSINT)
            if not services:
                discover_task = Task(
                    task_type=TaskType.SERVICE_DISCOVER,
                    target=target_email,
                    parameters={
                        'check_popular': True,
                        'check_breach_mentions': True
                    },
                    dependencies=[osint_task.task_id],
                    priority=9
                )
                workflow.add_task(discover_task)
                service_task_id = discover_task.task_id
            else:
                service_task_id = osint_task.task_id  # Skip discovery
            
            # 3. Password Generation (depends on OSINT)
            password_task = Task(
                task_type=TaskType.PASSWORD_GENERATE,
                target=target_email,
                parameters={
                    'use_breach_data': True,
                    'apply_mutations': True,
                    'use_llm': self.config.get('llm_enabled', False)
                },
                dependencies=[osint_task.task_id],
                priority=8
            )
            workflow.add_task(password_task)
            
            # 4. Attack Execution (one per service)
            target_services = services or self.config.get('default_services', ['mega'])
            
            for service in target_services:
                attack_task = Task(
                    task_type=TaskType.ATTACK_EXECUTE,
                    target=target_email,
                    parameters={
                        'service': service,
                        'use_generated_passwords': True
                    },
                    dependencies=[service_task_id, password_task.task_id],
                    priority=7
                )
                workflow.add_task(attack_task)
            
            # 5. Cleanup (depends on all attack tasks)
            attack_task_ids = [
                t.task_id for t in workflow.tasks 
                if t.task_type == TaskType.ATTACK_EXECUTE
            ]
            
            cleanup_task = Task(
                task_type=TaskType.CLEANUP,
                target=target_email,
                parameters={'clear_cache': True},
                dependencies=attack_task_ids,
                priority=1
            )
            workflow.add_task(cleanup_task)
        
        # Store workflow
        self.active_workflows[workflow.workflow_id] = workflow
        
        logger.info(
            f"Created workflow {workflow.workflow_id} for {target_email} "
            f"with {len(workflow.tasks)} tasks"
        )
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow, managing task dependencies and execution order
        """
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = TaskStatus.IN_PROGRESS
        logger.info(f"Starting workflow execution: {workflow_id}")
        
        try:
            while not workflow.is_complete():
                # Get tasks ready to execute
                ready_tasks = workflow.get_ready_tasks()
                
                if not ready_tasks:
                    # No tasks ready - check if we're stuck
                    pending_tasks = [
                        t for t in workflow.tasks 
                        if t.status == TaskStatus.PENDING
                    ]
                    
                    if pending_tasks:
                        logger.error(
                            f"Workflow {workflow_id} stuck - {len(pending_tasks)} "
                            "tasks pending with unmet dependencies"
                        )
                        workflow.status = TaskStatus.FAILED
                        break
                    else:
                        # All tasks are in progress or complete
                        await asyncio.sleep(0.1)
                        continue
                
                # Execute ready tasks in parallel
                task_coroutines = [
                    self._execute_task(workflow, task) 
                    for task in ready_tasks
                ]
                
                await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Workflow complete
            workflow.completed_at = datetime.utcnow()
            
            # Count successes and failures
            completed = sum(
                1 for t in workflow.tasks 
                if t.status == TaskStatus.COMPLETED
            )
            failed = sum(
                1 for t in workflow.tasks 
                if t.status == TaskStatus.FAILED
            )
            
            if failed == 0:
                workflow.status = TaskStatus.COMPLETED
                self.workflows_completed += 1
            else:
                workflow.status = TaskStatus.FAILED
                self.workflows_failed += 1
            
            logger.info(
                f"Workflow {workflow_id} finished: "
                f"{completed} completed, {failed} failed"
            )
            
            return {
                'workflow_id': workflow_id,
                'status': workflow.status.value,
                'tasks_completed': completed,
                'tasks_failed': failed,
                'duration': (
                    workflow.completed_at - workflow.created_at
                ).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} error: {e}", exc_info=True)
            workflow.status = TaskStatus.FAILED
            self.workflows_failed += 1
            raise
    
    async def _execute_task(self, workflow: Workflow, task: Task):
        """Execute a single task"""
        
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        
        logger.debug(
            f"Executing task {task.task_id} ({task.task_type.value}) "
            f"for {task.target}"
        )
        
        try:
            # Get handler for this task type
            handler = self.workflow_handlers.get(task.task_type)
            
            if not handler:
                raise ValueError(f"No handler registered for {task.task_type.value}")
            
            # Build execution context
            context = self._build_task_context(workflow, task)
            
            # Execute handler
            result = await handler(task, context)
            
            # Store result
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            logger.debug(
                f"Task {task.task_id} completed successfully "
                f"in {(task.completed_at - task.started_at).total_seconds():.2f}s"
            )
            
            # Learn from successful execution
            await self.decision_engine.learn_from_outcome(
                decision=None,  # Would need to track decision that led to this task
                outcome={
                    'success': True,
                    'task_type': task.task_type.value,
                    'service': task.parameters.get('service')
                }
            )
            
        except Exception as e:
            logger.error(
                f"Task {task.task_id} failed: {e}",
                exc_info=True
            )
            
            task.error = str(e)
            task.retry_count += 1
            
            # Retry logic
            if task.retry_count < task.max_retries:
                logger.info(
                    f"Retrying task {task.task_id} "
                    f"(attempt {task.retry_count + 1}/{task.max_retries})"
                )
                task.status = TaskStatus.PENDING
                
                # Exponential backoff
                backoff = min(2 ** task.retry_count, 30)
                await asyncio.sleep(backoff)
                
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                
                # Learn from failure
                await self.decision_engine.learn_from_outcome(
                    decision=None,
                    outcome={
                        'success': False,
                        'task_type': task.task_type.value,
                        'error': str(e)
                    }
                )
    
    def _build_task_context(self, workflow: Workflow, task: Task) -> Dict[str, Any]:
        """Build execution context for a task"""
        
        # Gather results from dependency tasks
        dependency_results = {}
        for dep_id in task.dependencies:
            dep_task = next(
                (t for t in workflow.tasks if t.task_id == dep_id),
                None
            )
            if dep_task and dep_task.result:
                dependency_results[dep_task.task_type.value] = dep_task.result
        
        return {
            'workflow_id': workflow.workflow_id,
            'target_email': workflow.target_email,
            'dependency_results': dependency_results,
            'workflow_metadata': workflow.metadata,
            'config': self.config
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        tasks_by_status = {}
        for status in TaskStatus:
            count = sum(1 for t in workflow.tasks if t.status == status)
            if count > 0:
                tasks_by_status[status.value] = count
        
        return {
            'workflow_id': workflow_id,
            'target_email': workflow.target_email,
            'status': workflow.status.value,
            'tasks_by_status': tasks_by_status,
            'created_at': workflow.created_at.isoformat(),
            'completed_at': (
                workflow.completed_at.isoformat() 
                if workflow.completed_at else None
            )
        }
    
    def cancel_workflow(self, workflow_id: str):
        """Cancel a running workflow"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        workflow.status = TaskStatus.CANCELLED
        
        # Cancel all pending tasks
        for task in workflow.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                task.status = TaskStatus.CANCELLED
        
        logger.info(f"Cancelled workflow {workflow_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            'active_workflows': len(self.active_workflows),
            'workflows_completed': self.workflows_completed,
            'workflows_failed': self.workflows_failed,
            'registered_handlers': len(self.workflow_handlers)
        }
