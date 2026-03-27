from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration"""

    #Database
    database_url: str = ""

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
