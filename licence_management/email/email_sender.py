"""
邮件发送模块

负责SMTP邮件发送和HTML模板渲染。
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config.config_manager import EmailConfig, MailTemplateConfig
from ..data.csv_processor import PersonDocument
from ..business.reminder_logic import ReminderLogic
from ..utils.date_utils import DateUtils
from ..utils.logger import get_logger


class EmailSender:
    """邮件发送器"""
    
    def __init__(self, email_config: EmailConfig, template_config: MailTemplateConfig, logger=None):
        """
        初始化邮件发送器
        
        Args:
            email_config: 邮件配置
            template_config: 邮件模板配置
            logger: 日志记录器，如果为None则创建默认记录器
        """
        self.email_config = email_config
        self.template_config = template_config
        self.logger = logger or get_logger(__name__)
        self.reminder_logic = ReminderLogic(logger)
    
    def send_reminder_email(self, reminder_documents: List[PersonDocument]) -> bool:
        """
        发送证件到期提醒邮件
        
        Args:
            reminder_documents: 需要提醒的证件文档列表
            
        Returns:
            是否发送成功
        """
        if not reminder_documents:
            self.logger.info("没有需要提醒的证件，跳过邮件发送")
            return True
        
        self.logger.info(f"开始发送提醒邮件，包含 {len(reminder_documents)} 个证件")
        
        try:
            # 生成邮件内容
            subject = self._generate_subject(reminder_documents)
            html_body = self._generate_html_body(reminder_documents)
            
            # 创建邮件对象
            message = self._create_email_message(subject, html_body)
            
            # 发送邮件
            success = self._send_email(message)
            
            if success:
                self.logger.info("提醒邮件发送成功")
            else:
                self.logger.error("提醒邮件发送失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"发送提醒邮件时发生错误: {e}")
            return False
    
    def send_test_email(self, test_subject: str = "证件管理系统 - 测试邮件") -> bool:
        """
        发送测试邮件（用于验证邮件配置）
        
        Args:
            test_subject: 测试邮件主题
            
        Returns:
            是否发送成功
        """
        self.logger.info("开始发送测试邮件")
        
        try:
            # 生成测试邮件内容
            html_body = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>测试邮件</title>
            </head>
            <body>
                <h2>证件管理系统测试邮件</h2>
                <p>这是一封测试邮件，用于验证邮件配置是否正确。</p>
                <p>如果您收到此邮件，说明邮件系统配置成功！</p>
                <br>
                <p><strong>发送时间：</strong>{send_time}</p>
                <p><strong>系统信息：</strong>人员证件有效期管控系统</p>
                <br>
                <p>此邮件由系统自动发送，请勿回复。</p>
            </body>
            </html>
            """.format(send_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 创建邮件对象
            message = self._create_email_message(test_subject, html_body)
            
            # 发送邮件
            success = self._send_email(message)
            
            if success:
                self.logger.info("测试邮件发送成功")
            else:
                self.logger.error("测试邮件发送失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"发送测试邮件时发生错误: {e}")
            return False
    
    def _generate_subject(self, reminder_documents: List[PersonDocument]) -> str:
        """
        生成邮件主题
        
        Args:
            reminder_documents: 需要提醒的证件文档列表
            
        Returns:
            邮件主题字符串
        """
        today_date = DateUtils.get_today_str('%Y-%m-%d')
        count = len(reminder_documents)
        
        subject = self.template_config.subject.format(
            count=count,
            today_date=today_date
        )
        
        return subject
    
    def _generate_html_body(self, reminder_documents: List[PersonDocument]) -> str:
        """
        生成HTML邮件正文
        
        Args:
            reminder_documents: 需要提醒的证件文档列表
            
        Returns:
            HTML邮件正文字符串
        """
        # 生成表格行
        table_rows = []
        for doc in reminder_documents:
            # 获取显示颜色
            color = self.reminder_logic.get_display_color(doc.days_left)
            
            # 格式化剩余天数显示
            days_left_display = self._format_days_left_display(doc.days_left)
            
            # 格式化到期日期
            expiry_date_display = DateUtils.format_date(doc.expiry_date) if doc.expiry_date else '未知'
            
            # 生成表格行HTML
            row_html = self.template_config.table_row_html.format(
                person_name=doc.person_name,
                document_type=doc.document_type,
                expiry_date=expiry_date_display,
                days_left=days_left_display,
                remarks=doc.remarks or '',
                color=color
            )
            table_rows.append(row_html)
        
        # 拼接所有表格行
        table_rows_html = '\n'.join(table_rows)
        
        # 生成完整的邮件正文
        html_body = self.template_config.body_html.format(
            table_rows=table_rows_html
        )
        
        return html_body
    
    def _format_days_left_display(self, days_left: Optional[int]) -> str:
        """
        格式化剩余天数的显示文本
        
        Args:
            days_left: 剩余天数
            
        Returns:
            格式化的显示文本
        """
        if days_left is None:
            return "未知"
        elif days_left < 0:
            return f"已过期 {abs(days_left)} 天"
        elif days_left == 0:
            return "今天到期"
        elif days_left == 1:
            return "明天到期"
        else:
            return f"{days_left} 天后到期"
    
    def _create_email_message(self, subject: str, html_body: str) -> MIMEMultipart:
        """
        创建邮件消息对象
        
        Args:
            subject: 邮件主题
            html_body: HTML邮件正文
            
        Returns:
            邮件消息对象
        """
        message = MIMEMultipart('alternative')
        
        # 设置邮件头信息
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = f"{self.email_config.sender_name} <{self.email_config.smtp_user}>"
        message['To'] = self.email_config.receiver_email
        
        # 创建HTML部分
        html_part = MIMEText(html_body, 'html', 'utf-8')
        message.attach(html_part)
        
        return message
    
    def _send_email(self, message: MIMEMultipart) -> bool:
        """
        发送邮件
        
        Args:
            message: 邮件消息对象
            
        Returns:
            是否发送成功
        """
        try:
            # 解析收件人（支持多个收件人，逗号分隔）
            receivers = [email.strip() for email in self.email_config.receiver_email.split(',')]
            
            self.logger.info(f"连接SMTP服务器: {self.email_config.smtp_server}:{self.email_config.smtp_port}")
            
            # 创建SMTP连接
            if self.email_config.use_ssl:
                # 使用SSL连接
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(
                    self.email_config.smtp_server, 
                    self.email_config.smtp_port, 
                    context=context
                )
            else:
                # 使用普通连接
                server = smtplib.SMTP(
                    self.email_config.smtp_server, 
                    self.email_config.smtp_port
                )
                
                # 如果配置了TLS，启用TLS
                if self.email_config.use_tls:
                    server.starttls(context=ssl.create_default_context())
            
            self.logger.info("SMTP服务器连接成功，开始认证")
            
            # 登录邮箱
            server.login(self.email_config.smtp_user, self.email_config.smtp_password)
            
            self.logger.info("SMTP认证成功，开始发送邮件")
            
            # 发送邮件
            text = message.as_string()
            server.sendmail(self.email_config.smtp_user, receivers, text)
            
            # 关闭连接
            server.quit()
            
            self.logger.info(f"邮件发送成功，收件人: {', '.join(receivers)}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP认证失败: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"收件人被拒绝: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error(f"SMTP服务器连接断开: {e}")
            return False
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送邮件时发生未知错误: {e}")
            return False
    
    def validate_email_config(self) -> List[str]:
        """
        验证邮件配置的有效性
        
        Returns:
            验证错误列表，空列表表示验证通过
        """
        errors = []
        
        # 验证必需字段
        if not self.email_config.smtp_server:
            errors.append("SMTP服务器地址不能为空")
        
        if not (1 <= self.email_config.smtp_port <= 65535):
            errors.append("SMTP端口必须在1-65535之间")
        
        if not self.email_config.smtp_user:
            errors.append("SMTP用户名不能为空")
        
        if not self.email_config.smtp_password:
            errors.append("SMTP密码不能为空")
        
        if not self.email_config.receiver_email:
            errors.append("收件人邮箱不能为空")
        else:
            # 简单验证邮箱格式
            receivers = [email.strip() for email in self.email_config.receiver_email.split(',')]
            for email in receivers:
                if '@' not in email or '.' not in email:
                    errors.append(f"邮箱格式无效: {email}")
        
        # 验证模板配置
        if not self.template_config.subject:
            errors.append("邮件主题模板不能为空")
        
        if not self.template_config.body_html:
            errors.append("邮件正文模板不能为空")
        elif '{table_rows}' not in self.template_config.body_html:
            errors.append("邮件正文模板必须包含{table_rows}占位符")
        
        if not self.template_config.table_row_html:
            errors.append("表格行模板不能为空")
        
        return errors 