"""
日志工具模块

提供统一的日志记录功能，支持不同级别的日志输出和文件记录。
"""

import logging
import os
from datetime import datetime
from typing import Optional


def get_logger(name: str = "licence_management", 
               log_level: str = "INFO",
               log_file: Optional[str] = None) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则只输出到控制台
        
    Returns:
        配置好的日志记录器对象
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 创建格式器
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_default_logger() -> logging.Logger:
    """
    设置默认日志记录器，包含自动文件名生成
    
    Returns:
        配置好的默认日志记录器
    """
    # 生成日志文件名（包含日期）
    today = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/licence_management_{today}.log"
    
    return get_logger(
        name="licence_management",
        log_level="INFO", 
        log_file=log_file
    ) 