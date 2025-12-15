"""
OpenBullet Config API Routes
FastAPI endpoints for config upload and management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
from pathlib import Path
import logging

from checkers.openbullet.importer import ConfigImporter, ConfigAPI
from core.brain.orchestrator import CheckResult

logger = logging.getLogger(__name__)

# Initialize importer
config_importer = ConfigImporter(storage_dir="configs/openbullet")
config_api = ConfigAPI(config_importer)

# Create router
router = APIRouter(prefix="/api/v1/configs", tags=["OpenBullet Configs"])


@router.post("/upload")
async def upload_config(
    file: UploadFile = File(...),
    mode: str = Form('auto')
):
    """
    Upload an OpenBullet config file
    
    Supports:
    - .loli (LoliScript)
    - .anom (Anomaly C#)
    - .xml (Legacy OpenBullet)
    
    Args:
        file: Config file upload
        mode: Import mode ('auto', 'convert', 'execute')
    
    Returns:
        Import result with config details
    """
    
    try:
        # Validate file extension
        filename = file.filename
        if not any(filename.endswith(ext) for ext in ['.loli', '.anom', '.xml']):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be .loli, .anom, or .xml"
            )
        
        # Read file content
        content = await file.read()
        
        # Import config
        result = await config_api.upload_config(content, filename, mode)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Import failed')
            )
        
        return {
            'success': True,
            'message': f"Config '{result['metadata']['name']}' imported successfully",
            'config_hash': result['config_hash'],
            'mode': result['mode'],
            'metadata': result['metadata']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/bulk")
async def upload_configs_bulk(
    files: List[UploadFile] = File(...),
    mode: str = Form('auto')
):
    """
    Upload multiple OpenBullet config files at once
    
    Args:
        files: List of config files
        mode: Import mode for all files
    
    Returns:
        Summary of imports
    """
    
    try:
        # Read all files
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((file.filename, content))
        
        # Bulk import
        result = await config_api.bulk_upload(file_data, mode)
        
        return {
            'success': True,
            'total': result['total'],
            'successful': result['successful'],
            'failed': result['failed'],
            'results': result['results']
        }
    
    except Exception as e:
        logger.error(f"Bulk upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_configs(category: Optional[str] = None):
    """
    List all imported configs
    
    Args:
        category: Filter by category (optional)
    
    Returns:
        List of config details
    """
    
    try:
        configs = config_importer.list_configs(category)
        
        return {
            'total': len(configs),
            'configs': configs
        }
    
    except Exception as e:
        logger.error(f"List error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """
    Get list of all config categories
    
    Returns:
        List of category names
    """
    
    try:
        categories = config_importer.get_categories()
        
        return {
            'categories': categories
        }
    
    except Exception as e:
        logger.error(f"Categories error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_hash}")
async def get_config(config_hash: str):
    """
    Get details of a specific config
    
    Args:
        config_hash: Config identifier
    
    Returns:
        Config details
    """
    
    try:
        config = config_importer.get_config(config_hash)
        
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        
        return config
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get config error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{config_hash}")
async def delete_config(config_hash: str):
    """
    Delete an imported config
    
    Args:
        config_hash: Config identifier
    
    Returns:
        Deletion status
    """
    
    try:
        deleted = await config_importer.delete_config(config_hash)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Config not found")
        
        return {
            'success': True,
            'message': 'Config deleted successfully'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{config_hash}/test")
async def test_config(
    config_hash: str,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Test a config with credentials
    
    Args:
        config_hash: Config identifier
        email: Email to test
        password: Password to test
    
    Returns:
        Check result
    """
    
    try:
        result = await config_importer.execute_config(
            config_hash,
            email,
            password
        )
        
        return {
            'success': True,
            'result': {
                'status': result.status.value,
                'email': result.email,
                'message': result.message,
                'response_time': result.response_time
            }
        }
    
    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_stats():
    """
    Get statistics about imported configs
    
    Returns:
        Config statistics
    """
    
    try:
        stats = config_importer.export_stats()
        
        return stats
    
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Integration with existing checker system

@router.post("/{config_hash}/add-to-workflow")
async def add_config_to_workflow(
    config_hash: str,
    workflow_id: str = Form(...)
):
    """
    Add an OpenBullet config as a task in an existing workflow
    
    Args:
        config_hash: Config identifier
        workflow_id: Workflow to add to
    
    Returns:
        Updated workflow
    """
    
    try:
        config = config_importer.get_config(config_hash)
        
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        
        # This would integrate with the orchestrator
        # For now, return placeholder
        return {
            'success': True,
            'message': f"Config '{config['name']}' added to workflow {workflow_id}",
            'config': config,
            'workflow_id': workflow_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow add error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
