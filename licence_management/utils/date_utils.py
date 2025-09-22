"""
日期处理工具模块

提供日期格式转换、计算和验证功能。
"""

from datetime import datetime, date
from typing import Optional, Union
from dateutil.parser import parse as dateutil_parse


class DateUtils:
    """日期处理工具类"""
    
    # 支持的日期格式列表
    SUPPORTED_FORMATS = [
        '%Y%m%d',        # 20240101
        '%Y-%m-%d',      # 2024-01-01
        '%Y/%m/%d',      # 2024/01/01
        '%d/%m/%Y',      # 01/01/2024
        '%d-%m-%Y',      # 01-01-2024
        '%Y年%m月%d日',   # 2024年01月01日
    ]
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """
        解析日期字符串为date对象
        
        Args:
            date_str: 日期字符串
            
        Returns:
            解析成功返回date对象，失败返回None
        """
        if not date_str or not isinstance(date_str, str):
            return None
            
        date_str = date_str.strip()
        if not date_str:
            return None
        
        # 首先尝试预定义格式
        for fmt in DateUtils.SUPPORTED_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # 使用dateutil进行智能解析
        try:
            return dateutil_parse(date_str).date()
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def format_date(date_obj: Union[date, datetime], format_str: str = '%Y-%m-%d') -> str:
        """
        格式化日期对象为字符串
        
        Args:
            date_obj: 日期或日期时间对象
            format_str: 格式字符串
            
        Returns:
            格式化后的日期字符串
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        return date_obj.strftime(format_str)
    
    @staticmethod
    def calculate_days_left(expiry_date: Union[str, date, datetime]) -> int:
        """
        计算证件剩余有效天数
        
        Args:
            expiry_date: 到期日期（字符串、date对象或datetime对象）
            
        Returns:
            剩余天数（负数表示已过期）
            
        Raises:
            ValueError: 日期格式无效
        """
        if isinstance(expiry_date, str):
            parsed_date = DateUtils.parse_date(expiry_date)
            if parsed_date is None:
                raise ValueError(f"无效的日期格式: {expiry_date}")
            expiry_date = parsed_date
        elif isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        
        today = date.today()
        return (expiry_date - today).days
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """
        验证日期字符串是否有效
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否为有效日期格式
        """
        return DateUtils.parse_date(date_str) is not None
    
    @staticmethod
    def normalize_date_format(date_str: str, target_format: str = '%Y%m%d') -> Optional[str]:
        """
        将日期字符串标准化为指定格式
        
        Args:
            date_str: 输入日期字符串
            target_format: 目标格式
            
        Returns:
            标准化后的日期字符串，解析失败返回None
        """
        parsed_date = DateUtils.parse_date(date_str)
        if parsed_date is None:
            return None
        
        return DateUtils.format_date(parsed_date, target_format)
    
    @staticmethod
    def get_today() -> date:
        """
        获取今天的日期
        
        Returns:
            今天的date对象
        """
        return date.today()
    
    @staticmethod
    def get_today_str(format_str: str = '%Y%m%d') -> str:
        """
        获取今天的日期字符串
        
        Args:
            format_str: 格式字符串
            
        Returns:
            格式化的今天日期字符串
        """
        return DateUtils.format_date(DateUtils.get_today(), format_str) 