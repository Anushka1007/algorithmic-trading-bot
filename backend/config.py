from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    twelve_data_api_key: str = ""
    groq_api_key: str = ""
    ai_model: str = "llama-3.1-8b-instant"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
