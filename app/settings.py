from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str
    gemini_api_key: SecretStr
    llm_model: str
    jwt_secret_key: SecretStr | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
