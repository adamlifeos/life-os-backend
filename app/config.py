from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./life_os.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

print("🔑 Loaded API Key:", settings.OPENAI_API_KEY)