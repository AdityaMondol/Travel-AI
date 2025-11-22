import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    LLM_PROVIDER: str = Field("openrouter", env="LLM_PROVIDER")
    
    OPENROUTER_API_KEY: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = Field("meta-llama/llama-3.1-70b-instruct", env="OPENROUTER_MODEL")
    
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    GOOGLE_MODEL: str = Field("gemini-2.0-flash", env="GOOGLE_MODEL")
    
    NVIDIA_API_KEY: Optional[str] = Field(None, env="NVIDIA_API_KEY")
    NVIDIA_BASE_URL: str = Field("https://integrate.api.nvidia.com/v1", env="NVIDIA_BASE_URL")
    NVIDIA_MODEL: str = Field("meta/llama-3.1-70b-instruct", env="NVIDIA_MODEL")
    
    GOOGLE_CLIENT_ID: Optional[str] = Field(None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(None, env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = Field("http://localhost:8000/auth/callback", env="GOOGLE_REDIRECT_URI")

    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    CACHE_ENABLED: bool = Field(True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(3600, env="CACHE_TTL")
    
    OUTPUT_DIR: str = Field("output", env="OUTPUT_DIR")
    CACHE_DIR: str = Field(".cache", env="CACHE_DIR")
    
    AGENT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    ENABLE_TELEMETRY: bool = True
    ENABLE_ANALYTICS: bool = True

    OPENROUTER_MODELS: Dict[str, str] = {
        "deepseek-r1": "deepseek/deepseek-r1",
        "deepseek-chat": "alibaba/tongyi-deepresearch-30b-a3b:free",
        "llama-70b": "meta-llama/llama-3.1-70b-instruct",
        "llama-8b": "meta-llama/llama-3.1-8b-instruct",
        "gpt-4": "openai/gpt-4-turbo",
        "gpt-4o": "openai/gpt-4o",
        "claude-3-opus": "anthropic/claude-3-opus",
        "claude-3-sonnet": "anthropic/claude-3-sonnet",
        "mistral-large": "mistralai/mistral-large",
        "mistral-medium": "mistralai/mistral-medium",
        "qwen-max": "qwen/qwen-max",
        "qwen-plus": "qwen/qwen-plus",
        "yi-large": "01-ai/yi-large",
        "yi-medium": "01-ai/yi-medium",
        "neural-chat": "neuroapi/neural-chat-7b",
        "cohere-command": "cohere/command-r-plus",
        "perplexity": "perplexity/llama-3.1-sonar-large-128k-online"
    }

    GOOGLE_MODELS: Dict[str, str] = {
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash",
        "gemini-pro": "gemini-pro"
    }

    NVIDIA_MODELS: Dict[str, str] = {
        "llama-70b": "meta/llama-3.1-70b-instruct",
        "llama-8b": "meta/llama-3.1-8b-instruct",
        "mistral-large": "mistralai/mistral-large",
        "mistral-medium": "mistralai/mistral-medium",
        "nemotron": "nvidia/nemotron-4-340b-instruct",
        "openai": "docker-compose up --build"
    }
    
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "ja": "Japanese", "zh": "Chinese",
        "ko": "Korean", "hi": "Hindi", "ru": "Russian", "ar": "Arabic",
        "nl": "Dutch", "pl": "Polish", "tr": "Turkish"
    }

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def validate(self):
        provider = self.LLM_PROVIDER.lower()
        
        if provider == "openrouter" and not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY required for OpenRouter provider")
        if provider == "google" and not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY required for Google provider")
        if provider == "nvidia" and not self.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY required for NVIDIA provider")
        
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.CACHE_DIR, exist_ok=True)

settings = Settings()
Config = settings
