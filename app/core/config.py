"""Configuration management with environment validation"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Config(BaseSettings):
    """Production configuration with strict validation"""
    
    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    
    # NVIDIA NIM
    nvidia_api_key: str = Field(default="", env="NVIDIA_API_KEY")
    nvidia_api_base: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        env="NVIDIA_API_BASE"
    )
    nim_model: str = Field(default="meta/llama-3.1-405b-instruct", env="NIM_MODEL")
    nim_vision_model: str = Field(
        default="nvidia/llama-3.2-90b-vision-instruct",
        env="NIM_VISION_MODEL"
    )
    
    # Database
    database_url: str = Field(default="postgresql://user:pass@localhost/leonore", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Vector DB
    vector_db_type: str = Field(default="milvus", env="VECTOR_DB_TYPE")  # milvus, weaviate, pinecone
    milvus_host: str = Field(default="localhost", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    pinecone_api_key: str = Field(default="", env="PINECONE_API_KEY")
    pinecone_index: str = Field(default="leonore", env="PINECONE_INDEX")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-prod", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Safety & Governance
    enable_content_filter: bool = Field(default=True, env="ENABLE_CONTENT_FILTER")
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    enable_human_approval: bool = Field(default=False, env="ENABLE_HUMAN_APPROVAL")
    compliance_mode: bool = Field(default=False, env="COMPLIANCE_MODE")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, env="RATE_LIMIT_WINDOW_SECONDS")
    
    # Resource limits
    max_agent_memory_mb: int = Field(default=512, env="MAX_AGENT_MEMORY_MB")
    max_execution_time_seconds: int = Field(default=300, env="MAX_EXECUTION_TIME_SECONDS")
    max_concurrent_agents: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    
    # GPU/Cost limits
    gpu_memory_limit_gb: float = Field(default=24.0, env="GPU_MEMORY_LIMIT_GB")
    monthly_cost_limit_usd: float = Field(default=1000.0, env="MONTHLY_COST_LIMIT_USD")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    
    # Monitoring
    enable_prometheus: bool = Field(default=True, env="ENABLE_PROMETHEUS")
    enable_jaeger: bool = Field(default=False, env="ENABLE_JAEGER")
    jaeger_host: str = Field(default="localhost", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("environment must be development, staging, or production")
        return v
    
    @validator("vector_db_type")
    def validate_vector_db(cls, v):
        if v not in ["milvus", "weaviate", "pinecone"]:
            raise ValueError("vector_db_type must be milvus, weaviate, or pinecone")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


def get_config() -> Config:
    """Get singleton config instance"""
    return Config()
