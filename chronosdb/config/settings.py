from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration"""

    #Database
    database_url: str = "postgresql+asyncpg://neondb_owner:npg_Hi4bdNPXxt3a@ep-bitter-math-am2upr46-pooler.c-5.us-east-1.aws.neon.tech/neondb?ssl=require"

    #REDIS
    redis_url: str = ""

    #RabbitMQ 
    rabbitmq_url: str = ""

    # Application
    env: str = "development"
    log_level: str = "INFO"
    
    # Retry defaults
    max_retries: int = 3
    retry_backoff_multiplier: int = 2
    retry_backoff_max: int = 3600  # 1 hour
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()