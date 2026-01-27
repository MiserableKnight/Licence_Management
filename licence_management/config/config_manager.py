"""
配置管理模块

负责YAML配置文件的加载、验证和管理。
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SmtpServerConfig:
    """单个SMTP服务器配置类"""
    name: str
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    sender_name: str
    use_ssl: bool = True
    use_tls: bool = False


@dataclass
class EmailConfig:
    """邮件配置类"""
    primary_server: SmtpServerConfig
    backup_servers: List[SmtpServerConfig]
    receiver_email: str
    max_retry_attempts: int = 3


@dataclass
class ReminderConfig:
    """提醒规则配置类"""
    days_before_expiry: List[int] = field(default_factory=lambda: [60, 30, 7, 1])


@dataclass
class ReportConfig:
    """报告配置类"""
    output_filename: str = "证件状态报告_{date}.csv"
    days_until_expiring_threshold: int = 30


@dataclass
class MailTemplateConfig:
    """邮件模板配置类"""
    subject: str = "证件到期提醒 - {count}个证件需要关注 ({today_date})"
    body_html: str = ""
    table_row_html: str = ""


@dataclass
class AppConfig:
    """应用主配置类"""
    email: EmailConfig
    reminder: ReminderConfig
    report: ReportConfig
    mail_template: MailTemplateConfig
    
    # 数据文件路径
    data_file: str = "sample_data/人员证件信息.csv"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self._config: Optional[AppConfig] = None
    
    def load_config(self) -> AppConfig:
        """
        加载配置文件
        
        Returns:
            应用配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML格式错误
            ValueError: 配置验证失败
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 验证和构建配置对象
        self._config = self._build_config(config_data)
        return self._config
    
    def _build_config(self, config_data: Dict[str, Any]) -> AppConfig:
        """
        从字典数据构建配置对象
        
        Args:
            config_data: 配置字典数据
            
        Returns:
            应用配置对象
            
        Raises:
            ValueError: 配置项缺失或格式错误
        """
        # 验证必需的配置节点
        required_sections = ['email', 'reminder', 'report', 'mail_template']
        for section in required_sections:
            if section not in config_data:
                raise ValueError(f"缺少配置节点: {section}")
        
        # 构建邮件配置
        email_config = self._build_email_config(config_data['email'])
        
        # 构建提醒配置
        reminder_config = self._build_reminder_config(config_data['reminder'])
        
        # 构建报告配置
        report_config = self._build_report_config(config_data['report'])
        
        # 构建邮件模板配置
        template_config = self._build_template_config(config_data['mail_template'])
        
        # 构建主配置
        app_config = AppConfig(
            email=email_config,
            reminder=reminder_config,
            report=report_config,
            mail_template=template_config
        )
        
        # 可选配置项
        if 'data_file' in config_data:
            app_config.data_file = config_data['data_file']
        
        if 'log_level' in config_data:
            app_config.log_level = config_data['log_level']
        
        if 'log_file' in config_data:
            app_config.log_file = config_data['log_file']
        
        return app_config
    
    def _build_email_config(self, email_data: Dict[str, Any]) -> EmailConfig:
        """
        构建邮件配置

        支持新格式（primary_server + backup_servers）和旧格式（直接配置）
        自动将旧格式转换为新格式
        """
        # 检测配置格式
        if 'primary_server' in email_data:
            # 新格式：primary_server + backup_servers
            return self._build_email_config_new(email_data)
        else:
            # 旧格式：直接配置，自动转换为新格式
            return self._build_email_config_legacy(email_data)

    def _build_email_config_new(self, email_data: Dict[str, Any]) -> EmailConfig:
        """构建新格式的邮件配置"""
        # 验证必需字段
        if 'primary_server' not in email_data:
            raise ValueError("邮件配置缺少 primary_server 字段")

        if 'receiver_email' not in email_data:
            raise ValueError("邮件配置缺少 receiver_email 字段")

        # 构建主服务器配置
        primary_data = email_data['primary_server']
        primary_server = self._build_smtp_server_config(primary_data, "主服务器")

        # 构建备用服务器配置（如果有）
        backup_servers = []
        if 'backup_servers' in email_data and email_data['backup_servers']:
            for i, backup_data in enumerate(email_data['backup_servers']):
                server = self._build_smtp_server_config(
                    backup_data,
                    f"备用服务器{i+1}"
                )
                backup_servers.append(server)

        return EmailConfig(
            primary_server=primary_server,
            backup_servers=backup_servers,
            receiver_email=email_data['receiver_email'],
            max_retry_attempts=email_data.get('max_retry_attempts', 3)
        )

    def _build_email_config_legacy(self, email_data: Dict[str, Any]) -> EmailConfig:
        """
        构建旧格式的邮件配置（向后兼容）

        将旧格式自动转换为新格式，并打印警告
        """
        import warnings

        # 验证旧格式的必需字段
        required_fields = ['smtp_server', 'smtp_port', 'smtp_user', 'smtp_password',
                          'sender_name', 'receiver_email']

        for field in required_fields:
            if field not in email_data:
                raise ValueError(f"邮件配置缺少字段: {field}")

        # 打印警告信息
        warnings.warn(
            "邮件配置使用了旧格式，已自动转换为新格式。"
            "建议将配置文件更新为：primary_server + backup_servers 格式。"
            "参考：https://github.com/your-repo/docs/config-upgrade.md",
            DeprecationWarning,
            stacklevel=2
        )

        # 将旧格式转换为主服务器配置
        primary_server = SmtpServerConfig(
            name="默认服务器（旧格式转换）",
            smtp_server=email_data['smtp_server'],
            smtp_port=email_data['smtp_port'],
            smtp_user=email_data['smtp_user'],
            smtp_password=email_data['smtp_password'],
            sender_name=email_data['sender_name'],
            use_ssl=email_data.get('use_ssl', True),
            use_tls=email_data.get('use_tls', False)
        )

        return EmailConfig(
            primary_server=primary_server,
            backup_servers=[],
            receiver_email=email_data['receiver_email'],
            max_retry_attempts=email_data.get('max_retry_attempts', 3)
        )

    def _build_smtp_server_config(self, server_data: Dict[str, Any], server_name_hint: str) -> SmtpServerConfig:
        """
        构建单个SMTP服务器配置

        Args:
            server_data: 服务器配置数据
            server_name_hint: 服务器名称提示（用于错误信息）

        Returns:
            SMTP服务器配置对象
        """
        # 验证必需字段
        required_fields = ['smtp_server', 'smtp_port', 'smtp_user', 'smtp_password', 'sender_name']

        for field in required_fields:
            if field not in server_data:
                raise ValueError(f"{server_name_hint}配置缺少字段: {field}")

        return SmtpServerConfig(
            name=server_data.get('name', server_name_hint),
            smtp_server=server_data['smtp_server'],
            smtp_port=server_data['smtp_port'],
            smtp_user=server_data['smtp_user'],
            smtp_password=server_data['smtp_password'],
            sender_name=server_data['sender_name'],
            use_ssl=server_data.get('use_ssl', True),
            use_tls=server_data.get('use_tls', False)
        )
    
    def _build_reminder_config(self, reminder_data: Dict[str, Any]) -> ReminderConfig:
        """构建提醒配置"""
        days_before = reminder_data.get('days_before_expiry', [60, 30, 7, 1])
        
        if not isinstance(days_before, list) or not all(isinstance(x, int) for x in days_before):
            raise ValueError("days_before_expiry必须是整数列表")
        
        return ReminderConfig(days_before_expiry=days_before)
    
    def _build_report_config(self, report_data: Dict[str, Any]) -> ReportConfig:
        """构建报告配置"""
        return ReportConfig(
            output_filename=report_data.get('output_filename', "证件状态报告_{date}.csv"),
            days_until_expiring_threshold=report_data.get('days_until_expiring_threshold', 30)
        )
    
    def _build_template_config(self, template_data: Dict[str, Any]) -> MailTemplateConfig:
        """构建邮件模板配置"""
        return MailTemplateConfig(
            subject=template_data.get('subject', "证件到期提醒 - {count}个证件需要关注 ({today_date})"),
            body_html=template_data.get('body_html', ""),
            table_row_html=template_data.get('table_row_html', "")
        )
    
    @property
    def config(self) -> AppConfig:
        """
        获取当前配置
        
        Returns:
            应用配置对象
            
        Raises:
            RuntimeError: 配置未加载
        """
        if self._config is None:
            raise RuntimeError("配置尚未加载，请先调用load_config()")
        return self._config
    
    def validate_config(self) -> List[str]:
        """
        验证配置的有效性
        
        Returns:
            验证错误列表，空列表表示验证通过
        """
        if self._config is None:
            return ["配置尚未加载"]
        
        errors = []
        
        # 验证邮件配置
        email_config = self._config.email

        # 验证主服务器配置
        if not email_config.primary_server.smtp_server:
            errors.append("主SMTP服务器地址不能为空")

        if not (1 <= email_config.primary_server.smtp_port <= 65535):
            errors.append("主SMTP端口必须在1-65535之间")

        if not email_config.primary_server.smtp_user:
            errors.append("主SMTP用户名不能为空")

        if not email_config.primary_server.smtp_password:
            errors.append("主SMTP密码不能为空")

        # 验证备用服务器配置
        for i, backup_server in enumerate(email_config.backup_servers):
            if not backup_server.smtp_server:
                errors.append(f"备用服务器{i+1}的SMTP地址不能为空")

            if not (1 <= backup_server.smtp_port <= 65535):
                errors.append(f"备用服务器{i+1}的SMTP端口必须在1-65535之间")

            if not backup_server.smtp_user:
                errors.append(f"备用服务器{i+1}的SMTP用户名不能为空")

            if not backup_server.smtp_password:
                errors.append(f"备用服务器{i+1}的SMTP密码不能为空")

        if not email_config.receiver_email:
            errors.append("收件人邮箱不能为空")
        
        # 验证提醒配置
        reminder_config = self._config.reminder
        if not reminder_config.days_before_expiry:
            errors.append("提醒天数列表不能为空")
        
        if any(day < 0 for day in reminder_config.days_before_expiry):
            errors.append("提醒天数不能为负数")
        
        # 验证报告配置
        report_config = self._config.report
        if report_config.days_until_expiring_threshold < 0:
            errors.append("即将过期阈值不能为负数")
        
        return errors
    
    def save_default_config(self, output_file: str = "config_template.yaml") -> None:
        """
        生成默认配置文件模板

        Args:
            output_file: 输出文件路径
        """
        default_config = {
            'email': {
                'primary_server': {
                    'name': 'Gmail',
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'smtp_user': 'your_email@gmail.com',
                    'smtp_password': 'your_app_password',
                    'sender_name': '证件管理系统',
                    'use_ssl': False,
                    'use_tls': True
                },
                'backup_servers': [
                    {
                        'name': 'QQ邮箱',
                        'smtp_server': 'smtp.qq.com',
                        'smtp_port': 587,
                        'smtp_user': 'your_email@qq.com',
                        'smtp_password': 'your_qq_auth_code',
                        'sender_name': '证件管理系统',
                        'use_ssl': False,
                        'use_tls': True
                    }
                ],
                'receiver_email': 'recipient@example.com',
                'max_retry_attempts': 3
            },
            'reminder': {
                'days_before_expiry': [60, 30, 7, 1]
            },
            'report': {
                'output_filename': '证件状态报告_{date}.csv',
                'days_until_expiring_threshold': 30
            },
            'mail_template': {
                'subject': '证件到期提醒 - {count}个证件需要关注 ({today_date})',
                'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>证件到期提醒</title>
</head>
<body>
    <h2>证件到期提醒</h2>
    <p>以下证件即将到期或已过期，请及时处理：</p>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f2f2f2;">
            <th>姓名</th>
            <th>证件类型</th>
            <th>到期日期</th>
            <th>剩余天数</th>
            <th>备注</th>
        </tr>
        {table_rows}
    </table>
    <br>
    <p>此邮件由系统自动发送，请勿回复。</p>
</body>
</html>''',
                'table_row_html': '''<tr>
            <td>{person_name}</td>
            <td>{document_type}</td>
            <td>{expiry_date}</td>
            <td style="color: {color};">{days_left}</td>
            <td>{remarks}</td>
        </tr>'''
            },
            'data_file': 'sample_data/人员证件信息.csv',
            'log_level': 'INFO',
            'log_file': 'logs/licence_management_{date}.log'
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False, indent=2) 