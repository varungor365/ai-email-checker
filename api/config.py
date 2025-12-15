"""
API Configuration and Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-this-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:changeme@localhost:5432/ai_email_checker"
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB: str = "ai_email_checker_results"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    QUEUE_NAME: str = "ai_email_checker"
    
    # AI Configuration
    AI_ENABLED: bool = True
    LLM_ENABLED: bool = True
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Component Configurations
    @property
    def DECISION_ENGINE_CONFIG(self) -> Dict[str, Any]:
        return {
            'learning_enabled': True,
            'max_retries': 3,
            'services': {
                'mega': {
                    'max_attempts': 5,
                    'proxy_type': 'residential'
                },
                'dropbox': {
                    'max_attempts': 3,
                    'proxy_type': 'residential'
                }
            }
        }
    
    @property
    def ORCHESTRATOR_CONFIG(self) -> Dict[str, Any]:
        return {
            'llm_enabled': self.LLM_ENABLED,
            'default_services': ['mega', 'dropbox', 'pcloud']
        }
    
    @property
    def PROXY_CONFIG(self) -> Dict[str, Any]:
        return {
            'min_proxies': int(os.getenv('MIN_PROXIES', '10')),
            'max_proxies': int(os.getenv('MAX_PROXIES', '100')),
            'auto_scale': os.getenv('AUTO_SCALE_PROXIES', 'true').lower() == 'true',
            'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '300')),
            'static_proxies': [],
            'services': {
                'mega': {'proxy_type': 'residential'},
                'dropbox': {'proxy_type': 'residential'}
            }
        }
    
    @property
    def FINGERPRINT_CONFIG(self) -> Dict[str, Any]:
        return {
            'randomize': True,
            'preferred_browsers': ['Chrome', 'Firefox', 'Edge']
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
