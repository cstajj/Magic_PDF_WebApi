import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional

class DatabaseSettings(BaseModel):
    """数据库配置模型"""
    url: str
    pool_size: int = 10 
    echo_sql: bool = False

# --- 新增的日志配置模型 ---
class LoggingSettings(BaseModel):
    """Loguru 日志配置模型"""
    level: str = "INFO"
    file_path: Optional[str] = None  # 设为可选，以便禁用文件日志
    rotation: str = "10 MB"
    retention: str = "7 days"
    compression: Optional[str] = "zip"
    serialize: bool = False

class AppSettings(BaseModel):
    """应用主配置模型，聚合所有子配置"""
    database: DatabaseSettings
    logging: LoggingSettings
    app_secret_key: str
    expired_second: int

class ConfigManager:
    _instance = None
    _settings: AppSettings | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """私有方法，只在第一次实例化时调用"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        self._settings = AppSettings(**config_data)

    @property
    def settings(self) -> AppSettings:
        """提供一个只读属性来安全地访问配置"""
        if self._settings is None:
            self._load_config()
        return self._settings

config_manager = ConfigManager()