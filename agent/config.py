from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/trakl"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # External Services
    rec_service_url: str = "http://localhost:8001"
    
    # Google Calendar Integration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8002/api/calendar/callback"
    
    # Session Management
    default_session_duration: int = 30  # minutes
    max_sessions_per_day: int = 8
    
    # Progress Tracking
    progress_update_interval: int = 24  # hours
    
    class Config:
        env_file = ".env"

settings = Settings()
