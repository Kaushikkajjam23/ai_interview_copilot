# app/config.py
import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "b25e2d5d15676cb7ee1894ec9a60683ff05aa0581813dca7511f2d7ade04a8e77d46bf26ed16f994e6ccb1dd6b9b0a2d4f0fdd26e2e9ee558cbf8fc804b3489be1727d218b00d1a9391bdb8d9bef507197900a871509ad63cfb6840f55e2f51a8e1fa035a4b5c172a62bd1538e068f242ac202e8c209c8f9d5e6cb0dd76732a84310ffd83d696fa2cd3f99dede343a79814ab73ba903a8e680c0236789988aaef67e82d7a5cba65cab2d2731f62ae32e2fc669d6a4b5d4cd9b52283a77933e64c7a91d78e5b9a03ccc3f1ae86a6860b0a12be6eb133ad92c92cd1e45cc27755b7a1d249ce99bf7653171a60200450e7a7119d02de368fe8ceb70a356fda75d1f")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Email
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Create a settings instance
settings = Settings()