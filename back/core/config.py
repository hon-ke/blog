from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    """
    应用配置类
    """
    # 调试模式
    DEBUG: bool = True

    BASE_DIR: str = ""

    # SERVER
    SERVER: str = ""

    # 服务器配置
    BIND: str = "0.0.0.0:8000"

    WORKERS: int = 4

    LOG_LEVEL: str = "info"

    # CORS配置
    ALLOWED_HOSTS: str

    # STATIC file
    STATIC_DIR: str 

    # 数据库连接URL
    DATABASE_URL: str = "sqlite://./db.sqlite3"

    # JWT配置
    SECRET_KEY: str 
    ALGORITHM: str 

    # 前端URL
    FRONTEND_URL: str 

    # 客户端配置 - 存储原始字符串
    CLIENT: str
    # 预定义分类 - 存储原始字符串
    PRESET_CATEGORIES:List[str]

    # website相关
    WEBSITE_NAME: str 
    WEBSITE_URL: str 

    # 管理员配置
    ROOT_NAME: str
    ROOT_NICKNAME: str 
    ROOT_EMAIL: str
    ROOT_PASSWORD: str 
    ROOT_DES: str
    ROOT_AVATAR: str
    ROOT_API_KEY: str 
    ROOT_KEY: str


    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


# 创建全局配置实例
settings = Settings()