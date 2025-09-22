"""
业务逻辑模块

负责证件状态计算、提醒规则匹配等核心业务逻辑。
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from ..data.csv_processor import PersonDocument
from ..utils.date_utils import DateUtils
from ..utils.logger import get_logger


class ReminderLogic:
    """提醒业务逻辑类"""
    
    def __init__(self, logger=None):
        """
        初始化提醒业务逻辑
        
        Args:
            logger: 日志记录器，如果为None则创建默认记录器
        """
        self.logger = logger or get_logger(__name__)
    
    def calculate_document_status(self, documents: List[PersonDocument], 
                                days_until_expiring_threshold: int = 30) -> List[PersonDocument]:
        """
        计算所有证件的状态信息（剩余天数、状态）
        
        Args:
            documents: 证件文档列表
            days_until_expiring_threshold: 即将过期的天数阈值
            
        Returns:
            更新了状态信息的证件文档列表
        """
        self.logger.info(f"开始计算 {len(documents)} 个证件的状态信息")
        
        for doc in documents:
            if doc.expiry_date:
                # 计算剩余天数
                doc.days_left = DateUtils.calculate_days_left(doc.expiry_date)
                
                # 判断证件状态
                doc.status = self._get_document_status(doc.days_left, days_until_expiring_threshold)
            else:
                doc.days_left = None
                doc.status = "未知"
        
        # 统计状态信息
        status_counts = self._count_status_distribution(documents)
        self.logger.info(f"状态统计: {status_counts}")
        
        return documents
    
    def filter_reminder_documents(self, documents: List[PersonDocument], 
                                 reminder_days: List[int]) -> List[PersonDocument]:
        """
        筛选需要提醒的证件
        
        Args:
            documents: 所有证件文档列表
            reminder_days: 提醒天数列表（如[60, 30, 7, 1]）
            
        Returns:
            需要提醒的证件文档列表
        """
        self.logger.info(f"筛选需要提醒的证件，提醒节点: {reminder_days}")
        
        reminder_documents = []
        
        for doc in documents:
            if doc.days_left is not None:
                # 检查备注字段，如果是"已办理"，则不需要提醒
                if doc.remarks and doc.remarks.strip() == "已办理":
                    doc.needs_reminder = False
                    self.logger.debug(f"{doc.person_name}的{doc.document_type}备注为'已办理'，跳过提醒")
                else:
                    # 判断是否需要提醒
                    doc.needs_reminder = self._needs_reminder(doc.days_left, reminder_days)
                
                if doc.needs_reminder:
                    reminder_documents.append(doc)
            else:
                doc.needs_reminder = False
        
        self.logger.info(f"共有 {len(reminder_documents)} 个证件需要提醒")
        
        # 按剩余天数排序（已过期的在前面，天数越少越靠前）
        reminder_documents.sort(key=lambda x: x.days_left if x.days_left is not None else -999)
        
        return reminder_documents
    
    def generate_reminder_summary(self, reminder_documents: List[PersonDocument]) -> Dict[str, Any]:
        """
        生成提醒汇总信息
        
        Args:
            reminder_documents: 需要提醒的证件文档列表
            
        Returns:
            提醒汇总信息字典
        """
        if not reminder_documents:
            return {
                'total_count': 0,
                'expired_count': 0,
                'expiring_count': 0,
                'by_days_left': {},
                'by_person': {},
                'by_document_type': {}
            }
        
        # 按剩余天数分类统计
        by_days_left = {}
        expired_count = 0
        expiring_count = 0
        
        for doc in reminder_documents:
            days_left = doc.days_left
            if days_left is not None:
                if days_left < 0:
                    expired_count += 1
                else:
                    expiring_count += 1
                
                days_key = f"{days_left}天" if days_left >= 0 else f"已过期{abs(days_left)}天"
                if days_key not in by_days_left:
                    by_days_left[days_key] = []
                by_days_left[days_key].append(doc)
        
        # 按人员分类统计
        by_person = {}
        for doc in reminder_documents:
            person_name = doc.person_name
            if person_name not in by_person:
                by_person[person_name] = []
            by_person[person_name].append(doc)
        
        # 按证件类型分类统计
        by_document_type = {}
        for doc in reminder_documents:
            doc_type = doc.document_type
            if doc_type not in by_document_type:
                by_document_type[doc_type] = []
            by_document_type[doc_type].append(doc)
        
        summary = {
            'total_count': len(reminder_documents),
            'expired_count': expired_count,
            'expiring_count': expiring_count,
            'by_days_left': by_days_left,
            'by_person': by_person,
            'by_document_type': by_document_type
        }
        
        self.logger.info(f"生成提醒汇总: 总计{summary['total_count']}个，"
                        f"已过期{expired_count}个，即将过期{expiring_count}个")
        
        return summary
    
    def generate_status_report_data(self, documents: List[PersonDocument]) -> List[Dict[str, Any]]:
        """
        生成状态报告数据
        
        Args:
            documents: 证件文档列表
            
        Returns:
            用于生成报告的数据列表
        """
        report_data = []
        
        for doc in documents:
            row_data = {
                'person_name': doc.person_name,
                'document_type': doc.document_type,
                'start_date': DateUtils.format_date(doc.start_date) if doc.start_date else '',
                'expiry_date': DateUtils.format_date(doc.expiry_date) if doc.expiry_date else '',
                'days_left': doc.days_left if doc.days_left is not None else '',
                'status': doc.status or '',
                'remarks': doc.remarks
            }
            report_data.append(row_data)
        
        # 按状态和剩余天数排序
        report_data.sort(key=lambda x: (
            0 if x['status'] == '已过期' else (1 if x['status'] == '即将过期' else 2),
            x['days_left'] if isinstance(x['days_left'], int) else 999
        ))
        
        return report_data
    
    def _get_document_status(self, days_left: int, threshold: int) -> str:
        """
        获取证件状态
        
        Args:
            days_left: 剩余天数
            threshold: 即将过期阈值
            
        Returns:
            证件状态字符串
        """
        if days_left < 0:
            return "已过期"
        elif days_left <= threshold:
            return "即将过期"  
        else:
            return "有效"
    
    def _needs_reminder(self, days_left: int, reminder_days: List[int]) -> bool:
        """
        判断是否需要发送提醒
        
        Args:
            days_left: 剩余天数
            reminder_days: 提醒天数列表
            
        Returns:
            是否需要提醒
        """
        # 已过期的证件需要提醒
        if days_left < 0:
            return True
        
        # 如果没有设置提醒天数，则不提醒
        if not reminder_days:
            return False
        
        # 剩余天数小于等于最大提醒天数的证件需要提醒
        max_reminder_days = max(reminder_days)
        return days_left <= max_reminder_days
    
    def _count_status_distribution(self, documents: List[PersonDocument]) -> Dict[str, int]:
        """
        统计状态分布
        
        Args:
            documents: 证件文档列表
            
        Returns:
            状态分布统计
        """
        status_counts = {}
        for doc in documents:
            status = doc.status or "未知"
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def get_priority_level(self, days_left: Optional[int]) -> int:
        """
        获取证件的优先级等级（用于排序和显示）
        
        Args:
            days_left: 剩余天数
            
        Returns:
            优先级等级（数字越小优先级越高）
        """
        if days_left is None:
            return 999  # 最低优先级
        
        if days_left < 0:
            return 0    # 已过期，最高优先级
        elif days_left <= 1:
            return 1    # 1天内到期
        elif days_left <= 7:
            return 2    # 7天内到期
        elif days_left <= 30:
            return 3    # 30天内到期
        else:
            return 4    # 其他情况
    
    def get_display_color(self, days_left: Optional[int]) -> str:
        """
        根据剩余天数获取显示颜色（用于HTML邮件）
        
        Args:
            days_left: 剩余天数
            
        Returns:
            CSS颜色值
        """
        if days_left is None:
            return "#666666"  # 灰色
        
        if days_left < 0:
            return "#dc3545"  # 红色 - 已过期
        elif days_left <= 1:
            return "#dc3545"  # 红色 - 紧急
        elif days_left <= 7:
            return "#fd7e14"  # 橙色 - 警告
        elif days_left <= 30:
            return "#ffc107"  # 黄色 - 注意
        else:
            return "#28a745"  # 绿色 - 正常 