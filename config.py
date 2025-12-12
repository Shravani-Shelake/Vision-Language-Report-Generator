from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "Vision-Language Report Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    #GEMINI
    GEMINI_API_KEY : str 
    GEMINI_MODEL : str = "gemini-2.5-flash"
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/reportdb"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "reports_collection"
    
    # AWS S3 (or local mock)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "report-files-bucket"
    USE_LOCAL_STORAGE: bool = True  # Set to False for real S3
    LOCAL_STORAGE_PATH: str = "./storage"
    
    # Vision Model
    VISION_MODEL: str = "Salesforce/blip-image-captioning-base"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_CSV_EXTENSIONS: list = [".csv"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
