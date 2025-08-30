import os
from pydantic_settings import BaseSettings
from typing import List

# ENV=local py -m uvicorn index:app #command
if  os.getenv("ENV") == "local":
    # Only load .env in local development
    from dotenv import load_dotenv
    load_dotenv()

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_URL: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek/deepseek-r1:free")
    CHROMA_API_KEY: str = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT: str = os.getenv("CHROMA_TENANT")
    CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "vector")
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"

settings = Settings()
