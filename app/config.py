from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    # POSTGRES_PORT: int 
    # POSTGRES_SERVER: str 
    # POSTGRES_USER: str 
    # POSTGRES_PASSWORD: str 
    # POSTGRES_DB: str 
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
        )
    
settings = DatabaseSettings() # type: ignore