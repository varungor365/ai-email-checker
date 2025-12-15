"""
Core Orchestration Engine
AI-Driven decision making, task queue management, and state tracking
"""

# Import only what exists to avoid errors
try:
    from .brain import DecisionEngine, TaskOrchestrator
except ImportError:
    DecisionEngine = None
    TaskOrchestrator = None

try:
    from .queue import TaskQueue, TaskPriority
except ImportError:
    TaskQueue = None
    TaskPriority = None

try:
    from .state import StateManager, OperationState
except ImportError:
    StateManager = None
    OperationState = None

try:
    from .workflow import WorkflowBuilder, WorkflowExecutor
except ImportError:
    WorkflowBuilder = None
    WorkflowExecutor = None

__all__ = [
    'DecisionEngine',
    'TaskOrchestrator', 
    'TaskQueue',
    'TaskPriority',
    'StateManager',
    'OperationState',
    'WorkflowBuilder',
    'WorkflowExecutor'
]
