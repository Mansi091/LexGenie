from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    GROQ_API_KEY : str = Field("",validation_alias="groq_api_key")

    class Config:
        env_file=".env"
        env_file_encoding="utf-8"
        extra="ignore"

        
settings = Settings()