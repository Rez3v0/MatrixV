from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MatrixV"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://matrixv:password@localhost/matrixv"
    
    # Celery & Redis 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "db+postgresql://matrixv:password@localhost/matrixv"
    
    # MinIO 配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "password123"
    MINIO_SECURE: bool = False
    
    # LLM 配置
    OPENAI_API_KEY: str = "dummy-key-for-local"
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    
    # 外部 API 配置
    PEXELS_API_KEY: str = "dummy-pexels-key"
    
    class Config:
        env_file = ".env"

settings = Settings()
