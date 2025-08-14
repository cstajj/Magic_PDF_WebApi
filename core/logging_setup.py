import sys
from pathlib import Path
from loguru import logger

from .config import config_manager

def setup_logging():
    """
    根据配置文件设置 Loguru 日志记录器。
    """
    log_config = config_manager.settings.logging
    
    logger.remove()

    logger.add(
        sys.stderr,
        level=log_config.level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>"
    )

    # 4. 如果配置文件中指定了 file_path，则添加一个文件处理器
    if log_config.file_path:
        # 确保日志目录存在
        log_file = Path(log_config.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            sink=log_file,
            level=log_config.level.upper(),
            rotation=log_config.rotation,
            retention=log_config.retention,
            compression=log_config.compression,
            serialize=log_config.serialize,  # 是否输出为 JSON
            enqueue=True,  # 使日志写入异步，提高性能
            backtrace=True, # 记录完整的堆栈跟踪
            diagnose=True   # 添加异常诊断信息
        )
    
    logger.info("日志记录器已成功配置。")