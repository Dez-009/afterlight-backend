from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pydantic import field_validator

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AfterLight API"
    VERSION: str = "1.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    JWT_SECRET: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://afterlight.app,https://www.afterlight.app"
    
    # Trusted hosts for production
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,afterlight.app,www.afterlight.app"
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "afterlight"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    
    # Redis (for rate limiting and caching)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    
    # File upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,image/gif,image/webp"
    
    # Rate limiting
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS: int = 100  # requests per window
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # External services
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@afterlight.app"
    
    # Print services (for keepsakes)
    PRINTFUL_API_KEY: Optional[str] = None
    LOB_API_KEY: Optional[str] = None
    
    # Frontend configuration
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Development settings
    ENABLE_DEBUG_ROUTES: bool = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',') if origin.strip()]
        return self.ALLOWED_ORIGINS
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Convert ALLOWED_HOSTS string to list"""
        if isinstance(self.ALLOWED_HOSTS, str):
            return [host.strip() for host in self.ALLOWED_HOSTS.split(',') if host.strip()]
        return self.ALLOWED_HOSTS
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convert ALLOWED_FILE_TYPES string to list"""
        if isinstance(self.ALLOWED_FILE_TYPES, str):
            return [file_type.strip() for file_type in self.ALLOWED_FILE_TYPES.split(',') if file_type.strip()]
        return self.ALLOWED_FILE_TYPES

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Railway-specific environment handling
        if os.getenv('RAILWAY_ENVIRONMENT'):
            self.ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'development')
            self.DEBUG = self.ENVIRONMENT == "development"
        
        # Railway automatically provides PORT
        if os.getenv('PORT'):
            self.PORT = int(os.getenv('PORT'))
        
        # Build database URL if not provided
        if not self.DATABASE_URL:
            if self.DATABASE_PASSWORD:
                self.DATABASE_URL = f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            else:
                self.DATABASE_URL = f"postgresql://{self.DATABASE_USER}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        
        # Build Redis URL if not provided
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        
        # Set debug based on environment
        self.DEBUG = self.ENVIRONMENT == "development"

# Create settings instance
settings = Settings()

# Environment-specific overrides
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.ALLOWED_ORIGINS = [
        "https://afterlight.app",
        "https://www.afterlight.app"
    ]
elif settings.ENVIRONMENT == "staging":
    settings.ALLOWED_ORIGINS = [
        "https://staging.afterlight.app",
        "https://staging-www.afterlight.app"
    ]
