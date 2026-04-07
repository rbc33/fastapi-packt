from pydantic_settings import BaseSettings, SettingsConfigDict


_base_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
        )
class DatabaseSettings(BaseSettings):
    # POSTGRES_PORT: int 
    # POSTGRES_SERVER: str 
    # POSTGRES_USER: str 
    # POSTGRES_PASSWORD: str 
    # POSTGRES_DB: str 
    DATABASE_URL: str = ""

    model_config = _base_config

class SecuritySettings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = _base_config

db_settings = DatabaseSettings() # type: ignore
security_settings = SecuritySettings() # type: ignore