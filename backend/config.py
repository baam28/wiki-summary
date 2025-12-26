# Configuration management
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    max_summary_words: int = Field(default=300, ge=50, le=1000, description="Maximum words in summary")
    max_input_tokens: int = Field(default=6000, ge=1000, le=16000, description="Maximum input tokens")
    max_output_tokens: int = Field(default=500, ge=100, le=2000, description="Maximum output tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    
    # API Configuration
    api_title: str = Field(default="Wiki Summary API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=10, ge=1, le=100, description="Requests per minute")
    
    # Caching
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl_seconds: int = Field(default=3600, ge=60, description="Cache TTL in seconds")
    
    # Backend URL (for frontend)
    backend_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
        
    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if v and not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format. Must start with 'sk-'")
        return v
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()

