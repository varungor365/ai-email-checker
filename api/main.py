"""
Main FastAPI Application
AI-Driven Autonomous Email Security Research Framework
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from .routes import operations, workflows, monitoring, openbullet
from .config import settings
from core.brain import DecisionEngine, TaskOrchestrator
from core.queue import TaskQueue
from identity.proxies import ProxyManager
from identity.fingerprints import FingerprintGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AI Email Checker Framework...")
    
    # Initialize core components
    app.state.decision_engine = DecisionEngine(config=settings.DECISION_ENGINE_CONFIG)
    app.state.orchestrator = TaskOrchestrator(
        decision_engine=app.state.decision_engine,
        config=settings.ORCHESTRATOR_CONFIG
    )
    app.state.task_queue = TaskQueue(
        redis_url=settings.REDIS_URL,
        queue_name=settings.QUEUE_NAME
    )
    
    # Connect to queue
    await app.state.task_queue.connect()
    
    # Initialize proxy manager
    app.state.proxy_manager = ProxyManager(config=settings.PROXY_CONFIG)
    await app.state.proxy_manager.initialize()
    
    # Initialize fingerprint generator
    app.state.fingerprint_gen = FingerprintGenerator(config=settings.FINGERPRINT_CONFIG)
    
    logger.info("Framework initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    await app.state.task_queue.disconnect()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AI-Driven Autonomous Email Security Research Framework",
    description="Distributed AI-powered security research platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(operations.router, prefix="/api/v1/operations", tags=["operations"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(openbullet.router, tags=["openbullet"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI-Driven Autonomous Email Security Research Framework",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    # Check queue connection
    queue_healthy = app.state.task_queue.is_connected
    
    # Check proxy pool
    proxy_stats = app.state.proxy_manager.pool.get_statistics()
    proxies_healthy = proxy_stats['active'] > 0
    
    healthy = queue_healthy and proxies_healthy
    
    return {
        "status": "healthy" if healthy else "degraded",
        "components": {
            "task_queue": "up" if queue_healthy else "down",
            "proxy_pool": "up" if proxies_healthy else "down",
            "active_proxies": proxy_stats['active']
        }
    }


@app.get("/stats")
async def get_statistics():
    """Get system statistics"""
    
    return {
        "decision_engine": app.state.decision_engine.get_statistics(),
        "orchestrator": app.state.orchestrator.get_statistics(),
        "task_queue": await app.state.task_queue.get_queue_stats(),
        "proxy_pool": app.state.proxy_manager.pool.get_statistics()
    }
