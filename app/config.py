from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str = "training"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    allowed_origins: list[str] = ["http://localhost:4200"]
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
