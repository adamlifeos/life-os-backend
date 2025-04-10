from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Get DATABASE_URL from environment or use SQLite as fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./life_os.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def get_database_url(self) -> str:
        # Handle SQLite URL specially
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        
        # For PostgreSQL, ensure SSL mode is required
        if self.DATABASE_URL.startswith("postgresql"):
            return f"{self.DATABASE_URL}?sslmode=require"
        
        return self.DATABASE_URL

settings = Settings()

print("🔑 Loaded API Key:", settings.OPENAI_API_KEY)