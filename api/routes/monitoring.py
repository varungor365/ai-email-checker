"""
Monitoring and Metrics Routes
"""

from fastapi import APIRouter, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

# Prometheus metrics
workflow_counter = Counter('workflows_total', 'Total workflows created')
task_counter = Counter('tasks_total', 'Total tasks executed', ['task_type', 'status'])
decision_histogram = Histogram('decision_time_seconds', 'Time spent making decisions')


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/stats")
async def get_stats(request: Request):
    """Get system statistics"""
    
    return {
        "decision_engine": request.app.state.decision_engine.get_statistics(),
        "orchestrator": request.app.state.orchestrator.get_statistics(),
        "task_queue": await request.app.state.task_queue.get_queue_stats(),
        "proxy_pool": request.app.state.proxy_manager.pool.get_statistics()
    }


@router.get("/health")
async def health_check(request: Request):
    """Detailed health check"""
    
    queue_healthy = request.app.state.task_queue.is_connected
    proxy_stats = request.app.state.proxy_manager.pool.get_statistics()
    
    return {
        "status": "healthy" if queue_healthy else "degraded",
        "components": {
            "task_queue": "up" if queue_healthy else "down",
            "proxy_pool": "up" if proxy_stats['active'] > 0 else "down",
            "proxies": proxy_stats
        }
    }
