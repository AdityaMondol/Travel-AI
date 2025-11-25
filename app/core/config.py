import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    LLM_PROVIDER: str = Field("nvidia", env="LLM_PROVIDER")
    
    OPENROUTER_API_KEY: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = Field("meta-llama/llama-3.1-70b-instruct", env="OPENROUTER_MODEL")
    
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    GOOGLE_MODEL: str = Field("gemini-2.0-flash", env="GOOGLE_MODEL")
    
    NVIDIA_API_KEY: Optional[str] = Field(None, env="NVIDIA_API_KEY")
    NVIDIA_BASE_URL: str = Field("https://integrate.api.nvidia.com/v1", env="NVIDIA_BASE_URL")
    NVIDIA_MODEL: str = Field("meta/llama-3.1-405b-instruct", env="NVIDIA_MODEL")
    
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
        "llama-3.1-405b": "meta/llama-3.1-405b-instruct",
        "llama-3.1-70b": "meta/llama-3.1-70b-instruct",
        "llama-3.1-8b": "meta/llama-3.1-8b-instruct",
        "llama-3.2-90b-vision": "meta/llama-3.2-90b-vision-instruct",
        "llama-3.2-11b-vision": "meta/llama-3.2-11b-vision-instruct",
        "llama-3.2-3b": "meta/llama-3.2-3b-instruct",
        "llama-3.2-1b": "meta/llama-3.2-1b-instruct",
        "mistral-large-2": "mistralai/mistral-large-2-instruct",
        "mistral-nemo-12b": "mistralai/mistral-nemo-12b-instruct",
        "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct-v0.1",
        "mixtral-8x22b": "mistralai/mixtral-8x22b-instruct-v0.1",
        "codestral-22b": "mistralai/codestral-22b-instruct-v0.1",
        "nemotron-4-340b": "nvidia/nemotron-4-340b-instruct",
        "nemotron-70b": "nvidia/llama-3.1-nemotron-70b-instruct",
        "arctic": "snowflake/arctic",
        "phi-3-medium": "microsoft/phi-3-medium-128k-instruct",
        "phi-3-small": "microsoft/phi-3-small-128k-instruct",
        "granite-34b": "ibm/granite-34b-code-instruct",
        "granite-8b": "ibm/granite-8b-code-instruct",
        "deepseek-coder-33b": "deepseek-ai/deepseek-coder-33b-instruct",
        "yi-large": "01-ai/yi-large",
        "qwen-2.5-72b": "qwen/qwen2.5-72b-instruct",
        "qwen-2.5-coder-32b": "qwen/qwen2.5-coder-32b-instruct",
        "gemma-2-27b": "google/gemma-2-27b-it",
        "gemma-2-9b": "google/gemma-2-9b-it",
        "gemma-2-2b": "google/gemma-2-2b-it"
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
        """Validate configuration"""
        try:
            provider = self.LLM_PROVIDER.lower()
            
            if provider == "openrouter" and not self.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY required for OpenRouter provider")
            if provider == "google" and not self.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY required for Google provider")
            if provider == "nvidia" and not self.NVIDIA_API_KEY:
                raise ValueError("NVIDIA_API_KEY required for NVIDIA provider")
            
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)
            os.makedirs(self.CACHE_DIR, exist_ok=True)
        except Exception as e:
            import logging
            logging.warning(f"Config validation warning: {e}")

settings = Settings()
Config = settings
