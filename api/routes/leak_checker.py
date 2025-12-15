"""
FastAPI routes for Email Leak Checker
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
import asyncio
from datetime import datetime
import csv
import io

from core.checkers.email_leak_checker import EmailLeakChecker
from core.auth import get_current_user

router = APIRouter(prefix="/api/leak-check", tags=["Email Leak Detection"])


# ==================== REQUEST MODELS ====================

class EmailScanRequest(BaseModel):
    """Single email scan request"""
    email: EmailStr
    sources: Optional[List[str]] = None  # Specific sources to check, None = all
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "sources": ["hibp", "emailrep", "holehe"]
            }
        }


class BulkScanRequest(BaseModel):
    """Bulk email scan request"""
    emails: List[EmailStr]
    max_concurrent: int = 5
    
    @validator('emails')
    def validate_emails(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 emails per request')
        if len(v) == 0:
            raise ValueError('At least 1 email required')
        return v
    
    @validator('max_concurrent')
    def validate_concurrent(cls, v):
        if v < 1 or v > 10:
            raise ValueError('max_concurrent must be between 1 and 10')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    "email1@example.com",
                    "email2@example.com",
                    "email3@example.com"
                ],
                "max_concurrent": 5
            }
        }


class MonitorRequest(BaseModel):
    """Email monitoring request"""
    email: EmailStr
    check_interval_hours: int = 24
    notify_on_breach: bool = True
    notification_methods: List[str] = ["email"]
    
    @validator('check_interval_hours')
    def validate_interval(cls, v):
        if v < 1 or v > 168:  # Max 1 week
            raise ValueError('Interval must be between 1 and 168 hours')
        return v


# ==================== API ENDPOINTS ====================

@router.post("/scan", summary="Scan single email for leaks")
async def scan_email(
    request: EmailScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Scan a single email across 30+ leak detection sources
    
    Returns:
    - Risk score (0-100)
    - Risk level (LOW/MEDIUM/HIGH/CRITICAL)
    - Breach details
    - Security recommendations
    """
    try:
        config = {
            'HIBP_API_KEY': current_user.get('hibp_api_key'),
            'INTELX_API_KEY': current_user.get('intelx_api_key'),
            'SPYCLOUD_API_KEY': current_user.get('spycloud_api_key'),
        }
        
        async with EmailLeakChecker(config) as checker:
            result = await checker.check_all_sources(request.email)
            
            return JSONResponse(
                status_code=200,
                content={
                    'success': True,
                    'data': result,
                    'scanned_at': datetime.now().isoformat()
                }
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/bulk", summary="Bulk email scan")
async def bulk_scan(
    request: BulkScanRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Scan multiple emails in parallel
    
    For large batches, results are processed in background
    Returns job ID to check status
    """
    try:
        config = {
            'HIBP_API_KEY': current_user.get('hibp_api_key'),
            'INTELX_API_KEY': current_user.get('intelx_api_key'),
            'SPYCLOUD_API_KEY': current_user.get('spycloud_api_key'),
        }
        
        # For small batches, process immediately
        if len(request.emails) <= 10:
            async with EmailLeakChecker(config) as checker:
                results = await checker.bulk_check(
                    request.emails,
                    max_concurrent=request.max_concurrent
                )
                
                return JSONResponse(
                    status_code=200,
                    content={
                        'success': True,
                        'total': len(request.emails),
                        'processed': len(results),
                        'results': results,
                        'summary': {
                            'critical': sum(1 for r in results if r['risk_level'] == 'CRITICAL'),
                            'high': sum(1 for r in results if r['risk_level'] == 'HIGH'),
                            'medium': sum(1 for r in results if r['risk_level'] == 'MEDIUM'),
                            'low': sum(1 for r in results if r['risk_level'] == 'LOW'),
                        }
                    }
                )
        
        # For large batches, use background task
        else:
            job_id = f"bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user['id']}"
            
            async def process_bulk():
                async with EmailLeakChecker(config) as checker:
                    results = await checker.bulk_check(
                        request.emails,
                        max_concurrent=request.max_concurrent
                    )
                    # Save results to database or file
                    # TODO: Implement result storage
            
            background_tasks.add_task(process_bulk)
            
            return JSONResponse(
                status_code=202,
                content={
                    'success': True,
                    'job_id': job_id,
                    'status': 'processing',
                    'message': f'Processing {len(request.emails)} emails in background',
                    'check_status_url': f'/api/leak-check/status/{job_id}'
                }
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk scan failed: {str(e)}")


@router.get("/results/{email}", summary="Get scan results for email")
async def get_results(
    email: EmailStr,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve previous scan results for an email
    Returns cached results if available
    """
    try:
        config = {}
        async with EmailLeakChecker(config) as checker:
            # Check cache
            cache_key = f"email_{email}"
            if cache_key in checker.cache:
                cached = checker.cache[cache_key]
                return JSONResponse(
                    status_code=200,
                    content={
                        'success': True,
                        'data': cached['data'],
                        'cached': True,
                        'cached_at': cached['timestamp'].isoformat()
                    }
                )
            else:
                return JSONResponse(
                    status_code=404,
                    content={
                        'success': False,
                        'message': 'No cached results found. Run a scan first.'
                    }
                )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor", summary="Start email monitoring")
async def monitor_email(
    request: MonitorRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Set up continuous monitoring for an email
    Will check periodically and notify on new breaches
    """
    try:
        monitor_id = f"monitor_{request.email}_{current_user['id']}"
        
        async def monitoring_task():
            """Background task for continuous monitoring"""
            config = {
                'HIBP_API_KEY': current_user.get('hibp_api_key'),
            }
            
            while True:
                try:
                    async with EmailLeakChecker(config) as checker:
                        result = await checker.check_all_sources(request.email)
                        
                        # Check if new breaches found
                        if result['sources_found'] > 0 and request.notify_on_breach:
                            # Send notification
                            # TODO: Implement notification system
                            pass
                    
                    # Wait for next check
                    await asyncio.sleep(request.check_interval_hours * 3600)
                
                except Exception as e:
                    logger.error(f"Monitoring error for {request.email}: {e}")
                    await asyncio.sleep(3600)  # Retry in 1 hour
        
        background_tasks.add_task(monitoring_task)
        
        return JSONResponse(
            status_code=201,
            content={
                'success': True,
                'monitor_id': monitor_id,
                'email': request.email,
                'check_interval_hours': request.check_interval_hours,
                'message': 'Monitoring started successfully'
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.get("/export/{format}", summary="Export scan results")
async def export_results(
    format: str,
    emails: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Export scan results in various formats
    
    Supported formats: csv, json, pdf
    """
    if format not in ['csv', 'json', 'pdf']:
        raise HTTPException(status_code=400, detail="Unsupported format. Use csv, json, or pdf")
    
    try:
        # Get results from database or cache
        # For demo, using mock data
        results = []
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['email', 'risk_score', 'risk_level', 'breaches_found', 'checked_at']
            )
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'email': result['email'],
                    'risk_score': result['risk_score'],
                    'risk_level': result['risk_level'],
                    'breaches_found': len(result.get('breaches', [])),
                    'checked_at': result['checked_at']
                })
            
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=leak_scan_results.csv"}
            )
        
        elif format == 'json':
            return JSONResponse(
                status_code=200,
                content={
                    'success': True,
                    'results': results,
                    'exported_at': datetime.now().isoformat()
                }
            )
        
        elif format == 'pdf':
            # TODO: Implement PDF export
            raise HTTPException(status_code=501, detail="PDF export not yet implemented")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/stats", summary="Get leak detection statistics")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """
    Get statistics about email leak detection
    
    Returns:
    - Total scans performed
    - Risk level distribution
    - Most common breaches
    - Top leaked domains
    """
    try:
        # TODO: Implement stats from database
        stats = {
            'total_scans': 0,
            'total_emails': 0,
            'risk_distribution': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            },
            'top_breaches': [],
            'top_domains': [],
            'last_scan': None
        }
        
        return JSONResponse(
            status_code=200,
            content={
                'success': True,
                'stats': stats
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", summary="List all available sources")
async def list_sources():
    """
    Get list of all 30 leak detection sources
    
    Returns source names, descriptions, and availability
    """
    sources = {
        'web_apis': [
            {'id': 'hibp', 'name': 'Have I Been Pwned', 'requires_key': True, 'free': True},
            {'id': 'firefox_monitor', 'name': 'Firefox Monitor', 'requires_key': False, 'free': True},
            {'id': 'cybernews', 'name': 'Cybernews', 'requires_key': False, 'free': True},
            {'id': 'emailrep', 'name': 'EmailRep.io', 'requires_key': False, 'free': True},
            {'id': 'breach_directory', 'name': 'BreachDirectory', 'requires_key': False, 'free': True},
            {'id': 'intelx', 'name': 'IntelX', 'requires_key': True, 'free': False},
            {'id': 'ghostproject', 'name': 'GhostProject', 'requires_key': True, 'free': False},
            {'id': 'avast', 'name': 'Avast HackCheck', 'requires_key': False, 'free': True},
            {'id': 'hpi_ilc', 'name': 'HPI Identity Leak Checker', 'requires_key': False, 'free': True},
            {'id': 'leakpeek', 'name': 'LeakPeek', 'requires_key': False, 'free': True},
            {'id': 'leak_lookup', 'name': 'Leak-Lookup', 'requires_key': False, 'free': True},
            {'id': 'spycloud', 'name': 'SpyCloud', 'requires_key': True, 'free': False},
        ],
        'github_tools': [
            {'id': 'breach_parse', 'name': 'breach-parse', 'language': 'bash'},
            {'id': 'cr3dov3r', 'name': 'Cr3dOv3r', 'language': 'python'},
            {'id': 'holehe', 'name': 'holehe', 'language': 'python'},
            {'id': 'mosint', 'name': 'mosint', 'language': 'go'},
            {'id': 'buster', 'name': 'buster', 'language': 'python'},
            {'id': 'leaklooker', 'name': 'LeakLooker', 'language': 'python'},
            {'id': 'photon', 'name': 'Photon', 'language': 'python'},
            {'id': 'theharvester', 'name': 'theHarvester', 'language': 'python'},
            {'id': 'sherlock', 'name': 'sherlock', 'language': 'python'},
            {'id': 'phoneinfoga', 'name': 'phoneinfoga', 'language': 'go'},
            {'id': 'ghunt', 'name': 'GHunt', 'language': 'python'},
            {'id': 'h8mail', 'name': 'h8mail', 'language': 'python'},
            {'id': 'linkedint', 'name': 'LinkedInt', 'language': 'python'},
            {'id': 'infoga', 'name': 'Infoga', 'language': 'python'},
            {'id': 'pwnedornot', 'name': 'pwnedOrNot', 'language': 'python'},
            {'id': 'whatbreach', 'name': 'WhatBreach', 'language': 'python'},
            {'id': 'social_analyzer', 'name': 'social-analyzer', 'language': 'python'},
            {'id': 'whatsmyname', 'name': 'WhatsMyName', 'language': 'python'},
        ]
    }
    
    return JSONResponse(
        status_code=200,
        content={
            'success': True,
            'total_sources': len(sources['web_apis']) + len(sources['github_tools']),
            'sources': sources
        }
    )


@router.post("/install-tools", summary="Install GitHub OSINT tools")
async def install_tools(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Install all GitHub OSINT tools
    This is a one-time setup process
    """
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    async def install_task():
        config = {}
        async with EmailLeakChecker(config) as checker:
            await checker.install_github_tools()
    
    background_tasks.add_task(install_task)
    
    return JSONResponse(
        status_code=202,
        content={
            'success': True,
            'message': 'Tool installation started in background',
            'estimated_time': '10-15 minutes'
        }
    )
