"""
CSV数据处理模块

负责读取、验证和处理CSV格式的人员证件数据。
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import date

from ..utils.date_utils import DateUtils
from ..utils.logger import get_logger


@dataclass
class PersonDocument:
    """人员证件信息数据类"""
    person_name: str        # 姓名
    document_type: str      # 证件类型
    start_date: Optional[date] = None     # 有效期起始日期
    expiry_date: Optional[date] = None    # 有效期截止日期  
    remarks: str = ""       # 备注信息
    
    # 计算字段
    days_left: Optional[int] = None         # 剩余天数（计算得出）
    status: Optional[str] = None            # 状态（计算得出）
    needs_reminder: Optional[bool] = None   # 是否需要提醒（计算得出）


class CSVProcessor:
    """CSV数据处理器"""
    
    # CSV文件必需的列
    REQUIRED_COLUMNS = ['person_name', 'document_type', 'expiry_date']
    
    # CSV文件可选的列
    OPTIONAL_COLUMNS = ['start_date', 'remarks']
    
    # 所有支持的列
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    def __init__(self, logger=None):
        """
        初始化CSV处理器
        
        Args:
            logger: 日志记录器，如果为None则创建默认记录器
        """
        self.logger = logger or get_logger(__name__)
    
    def read_csv_file(self, file_path: str, encoding: str = 'utf-8') -> List[PersonDocument]:
        """
        读取CSV文件并转换为PersonDocument对象列表
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码，默认为utf-8
            
        Returns:
            PersonDocument对象列表
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 数据格式错误
            UnicodeDecodeError: 编码错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV文件不存在: {file_path}")
        
        self.logger.info(f"开始读取CSV文件: {file_path}")
        
        # 尝试不同编码读取文件
        encodings_to_try = [encoding, 'utf-8', 'gbk', 'gb2312']
        df = None
        used_encoding = None
        
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                used_encoding = enc
                self.logger.info(f"成功使用编码 {enc} 读取文件")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise UnicodeDecodeError(f"无法使用任何编码读取文件: {file_path}")
        
        # 验证数据格式
        self._validate_dataframe(df, file_path)
        
        # 转换为PersonDocument对象列表
        documents = self._dataframe_to_documents(df)
        
        self.logger.info(f"成功读取 {len(documents)} 条人员证件记录")
        return documents
    
    def _validate_dataframe(self, df: pd.DataFrame, file_path: str) -> None:
        """
        验证DataFrame的格式和内容
        
        Args:
            df: 要验证的DataFrame
            file_path: 文件路径（用于错误提示）
            
        Raises:
            ValueError: 数据格式错误
        """
        # 检查是否为空
        if df.empty:
            raise ValueError(f"CSV文件为空: {file_path}")
        
        # 检查必需列是否存在
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV文件缺少必需列: {missing_columns}, 文件: {file_path}")
        
        # 检查数据完整性
        for idx, row in df.iterrows():
            # 检查必需字段是否为空
            for col in self.REQUIRED_COLUMNS:
                if pd.isna(row[col]) or str(row[col]).strip() == '':
                    raise ValueError(f"第{idx+2}行的'{col}'字段不能为空")
            
            # 验证日期格式
            if 'expiry_date' in row and not pd.isna(row['expiry_date']):
                if not DateUtils.is_valid_date(str(row['expiry_date'])):
                    raise ValueError(f"第{idx+2}行的到期日期格式无效: {row['expiry_date']}")
            
            if 'start_date' in row and not pd.isna(row['start_date']):
                if not DateUtils.is_valid_date(str(row['start_date'])):
                    raise ValueError(f"第{idx+2}行的开始日期格式无效: {row['start_date']}")
        
        self.logger.info(f"CSV数据验证通过，共 {len(df)} 行数据")
    
    def _dataframe_to_documents(self, df: pd.DataFrame) -> List[PersonDocument]:
        """
        将DataFrame转换为PersonDocument对象列表
        
        Args:
            df: 要转换的DataFrame
            
        Returns:
            PersonDocument对象列表
        """
        documents = []
        
        for idx, row in df.iterrows():
            try:
                # 解析日期
                start_date = None
                expiry_date = None
                
                if 'start_date' in row and not pd.isna(row['start_date']):
                    start_date = DateUtils.parse_date(str(row['start_date']))
                
                if 'expiry_date' in row and not pd.isna(row['expiry_date']):
                    expiry_date = DateUtils.parse_date(str(row['expiry_date']))
                
                # 创建PersonDocument对象
                doc = PersonDocument(
                    person_name=str(row['person_name']).strip(),
                    document_type=str(row['document_type']).strip(),
                    start_date=start_date,
                    expiry_date=expiry_date,
                    remarks=str(row.get('remarks', '')).strip() if not pd.isna(row.get('remarks', '')) else ""
                )
                
                documents.append(doc)
                
            except Exception as e:
                self.logger.error(f"处理第{idx+2}行数据时出错: {e}")
                raise ValueError(f"处理第{idx+2}行数据时出错: {e}")
        
        return documents
    
    def write_csv_file(self, documents: List[PersonDocument], file_path: str, 
                      include_calculated_fields: bool = True, encoding: str = 'utf-8') -> None:
        """
        将PersonDocument对象列表写入CSV文件
        
        Args:
            documents: PersonDocument对象列表
            file_path: 输出文件路径
            include_calculated_fields: 是否包含计算字段（days_left、status等）
            encoding: 文件编码
        """
        if not documents:
            raise ValueError("没有数据可写入")
        
        # 准备数据
        data_rows = []
        for doc in documents:
            row = {
                'person_name': doc.person_name,
                'document_type': doc.document_type,
                'start_date': DateUtils.format_date(doc.start_date) if doc.start_date else '',
                'expiry_date': DateUtils.format_date(doc.expiry_date) if doc.expiry_date else '',
                'remarks': doc.remarks
            }
            
            # 添加计算字段
            if include_calculated_fields:
                row.update({
                    'days_left': doc.days_left if doc.days_left is not None else '',
                    'status': doc.status if doc.status else '',
                    'needs_reminder': '是' if doc.needs_reminder else '否' if doc.needs_reminder is not None else ''
                })
            
            data_rows.append(row)
        
        # 创建DataFrame并保存
        df = pd.DataFrame(data_rows)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        df.to_csv(file_path, index=False, encoding=encoding)
        self.logger.info(f"成功写入CSV文件: {file_path}, 共 {len(documents)} 条记录")
    
    def create_sample_csv(self, file_path: str = "sample_data/人员证件信息.csv") -> None:
        """
        创建示例CSV文件
        
        Args:
            file_path: 输出文件路径
        """
        from datetime import datetime, timedelta
        
        # 准备示例数据
        today = date.today()
        sample_data = [
            {
                'person_name': '张三',
                'document_type': '身份证',
                'start_date': DateUtils.format_date(today - timedelta(days=3650)),
                'expiry_date': DateUtils.format_date(today + timedelta(days=365)),
                'remarks': '研发部'
            },
            {
                'person_name': '李四',
                'document_type': '护照',
                'start_date': DateUtils.format_date(today - timedelta(days=1825)),
                'expiry_date': DateUtils.format_date(today + timedelta(days=30)),
                'remarks': '市场部'
            },
            {
                'person_name': '王五',
                'document_type': '驾驶证',
                'start_date': DateUtils.format_date(today - timedelta(days=2190)),
                'expiry_date': DateUtils.format_date(today + timedelta(days=7)),
                'remarks': '行政部'
            },
            {
                'person_name': '赵六',
                'document_type': '工作许可证',
                'start_date': DateUtils.format_date(today - timedelta(days=365)),
                'expiry_date': DateUtils.format_date(today - timedelta(days=5)),
                'remarks': '技术部'
            },
            {
                'person_name': '钱七',
                'document_type': '健康证',
                'start_date': DateUtils.format_date(today - timedelta(days=300)),
                'expiry_date': DateUtils.format_date(today + timedelta(days=60)),
                'remarks': '食堂'
            }
        ]
        
        # 创建DataFrame并保存
        df = pd.DataFrame(sample_data)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        df.to_csv(file_path, index=False, encoding='utf-8')
        self.logger.info(f"成功创建示例CSV文件: {file_path}")
    
    def validate_documents(self, documents: List[PersonDocument]) -> List[str]:
        """
        验证PersonDocument对象列表的有效性
        
        Args:
            documents: 要验证的文档列表
            
        Returns:
            验证错误列表，空列表表示验证通过
        """
        errors = []
        
        if not documents:
            errors.append("没有任何证件数据")
            return errors
        
        for i, doc in enumerate(documents):
            # 验证必需字段
            if not doc.person_name or not doc.person_name.strip():
                errors.append(f"第{i+1}条记录：姓名不能为空")
            
            if not doc.document_type or not doc.document_type.strip():
                errors.append(f"第{i+1}条记录：证件类型不能为空")
            
            if not doc.expiry_date:
                errors.append(f"第{i+1}条记录：到期日期不能为空")
            
            # 验证日期逻辑
            if doc.start_date and doc.expiry_date:
                if doc.start_date >= doc.expiry_date:
                    errors.append(f"第{i+1}条记录：开始日期不能晚于或等于到期日期")
        
        return errors 