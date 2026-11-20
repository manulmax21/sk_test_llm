from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    model_name: str = "qwen3:1.7b"
    knowledge_base_path: str = "app/knowledge_base.txt"
    allowed_origins: list[str] = ["*"]

    model_config = {"env_prefix": "APP_"}


settings = Settings()
