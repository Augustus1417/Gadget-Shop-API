from pydantic_settings import BaseSettings
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'

class Settings(BaseSettings):
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    DATABASE: str
    
    class Config:
        env_file = str(env_path)


settings = Settings()