"""
配置文件
应用配置管理
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "AI Agent API"
    version: str = "1.0.0"
    env: str = "production"
    debug: bool = False
    log_level: str = "INFO"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None

    # 数据库配置
    database_url: Optional[str] = None
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis 配置
    redis_url: Optional[str] = None
    redis_password: Optional[str] = None
    redis_max_connections: int = 50

    # 安全配置
    secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 监控配置
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True

    # 云服务配置
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # 功能开关
    enable_cache: bool = True
    enable_rate_limit: bool = True
    rate_limit_per_minute: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
