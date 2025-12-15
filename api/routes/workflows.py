"""
Workflow Management Routes
"""

from fastapi import APIRouter, Request
from typing import Optional

router = APIRouter()


@router.get("/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    request: Request
):
    """Get detailed workflow status"""
    
    orchestrator = request.app.state.orchestrator
    status = orchestrator.get_workflow_status(workflow_id)
    
    if not status:
        return {"error": "Workflow not found"}
    
    return status


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    request: Request
):
    """Cancel a running workflow"""
    
    orchestrator = request.app.state.orchestrator
    orchestrator.cancel_workflow(workflow_id)
    
    return {"workflow_id": workflow_id, "status": "cancelled"}
