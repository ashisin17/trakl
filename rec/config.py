from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/trakl"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    
    # Redis (optional caching)
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Content Discovery
    max_search_results: int = 50
    content_cache_ttl: int = 3600  # 1 hour
    
    # Recommendation Engine
    similarity_threshold: float = 0.7
    max_recommendations: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()
