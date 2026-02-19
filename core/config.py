from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: SecretStr
    aws_region: str = "us-east-1"
    sqs_queue_url: str

    gemini_api_key: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()