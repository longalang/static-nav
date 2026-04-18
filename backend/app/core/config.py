from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "开发文档导航"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # 数据库配置 - 使用绝对路径
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/nav.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # 管理员默认账号
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
