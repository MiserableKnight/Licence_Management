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

from ..config.config_manager import EmailConfig, MailTemplateConfig, SmtpServerConfig
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
            
            # 创建邮件对象（使用主服务器配置）
            message = self._create_email_message(
                subject,
                html_body,
                self.email_config.primary_server
            )

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
            
            # 创建邮件对象（使用主服务器配置）
            message = self._create_email_message(
                test_subject,
                html_body,
                self.email_config.primary_server
            )

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
    
    def _create_email_message(self, subject: str, html_body: str, server_config: SmtpServerConfig) -> MIMEMultipart:
        """
        创建邮件消息对象

        Args:
            subject: 邮件主题
            html_body: HTML邮件正文
            server_config: SMTP服务器配置

        Returns:
            邮件消息对象
        """
        message = MIMEMultipart('alternative')

        # 设置邮件头信息
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = f"{server_config.sender_name} <{server_config.smtp_user}>"
        message['To'] = self.email_config.receiver_email

        # 创建HTML部分
        html_part = MIMEText(html_body, 'html', 'utf-8')
        message.attach(html_part)

        return message
    
    def _send_email(self, message: MIMEMultipart) -> bool:
        """
        发送邮件（支持多服务器自动切换）

        Args:
            message: 邮件消息对象

        Returns:
            是否发送成功
        """
        # 构建服务器列表（主服务器 + 备用服务器）
        servers = [self.email_config.primary_server] + self.email_config.backup_servers
        total_servers = len(servers)

        # 如果没有配置任何服务器，返回失败
        if total_servers == 0:
            self.logger.error("没有配置任何SMTP服务器")
            return False

        self.logger.info(f"开始尝试发送邮件，共配置 {total_servers} 个SMTP服务器")

        # 解析收件人（支持多个收件人，逗号分隔）
        receivers = [email.strip() for email in self.email_config.receiver_email.split(',')]

        # 依次尝试每个服务器
        for i, server_config in enumerate(servers):
            server_index = i + 1
            is_primary = (i == 0)

            try:
                self.logger.info(f"尝试使用服务器 [{server_config.name}] ({server_index}/{total_servers})")
                self.logger.info(f"  地址: {server_config.smtp_server}:{server_config.smtp_port}")
                self.logger.info(f"  用户: {server_config.smtp_user}")

                # 尝试发送邮件
                success = self._send_email_via_server(
                    server_config,
                    message,
                    receivers,
                    is_primary
                )

                if success:
                    self.logger.info(f"✓ 邮件通过服务器 [{server_config.name}] 发送成功")
                    return True
                else:
                    # 发送失败，继续尝试下一个服务器
                    if i < total_servers - 1:
                        self.logger.warning(f"✗ 服务器 [{server_config.name}] 发送失败，自动切换到下一个备用服务器...")
                    else:
                        self.logger.error("✗ 所有邮件服务器均发送失败")

            except Exception as e:
                self.logger.error(f"服务器 [{server_config.name}] 发送时发生异常: {e}")
                if i < total_servers - 1:
                    self.logger.info(f"自动切换到下一个备用服务器...")
                else:
                    self.logger.error("所有邮件服务器均尝试失败")

        # 所有服务器都尝试失败
        self._log_failure_suggestions(servers)
        return False

    def _send_email_via_server(
        self,
        server_config: SmtpServerConfig,
        message: MIMEMultipart,
        receivers: List[str],
        is_primary: bool
    ) -> bool:
        """
        通过指定服务器发送邮件

        Args:
            server_config: SMTP服务器配置
            message: 邮件消息对象
            receivers: 收件人列表
            is_primary: 是否为主服务器

        Returns:
            是否发送成功
        """
        server = None

        try:
            # 创建SMTP连接
            if server_config.use_ssl:
                # 使用SSL连接
                self.logger.debug(f"使用SSL连接到 {server_config.smtp_server}:{server_config.smtp_port}")
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(
                    server_config.smtp_server,
                    server_config.smtp_port,
                    context=context,
                    timeout=30
                )
            else:
                # 使用普通连接
                self.logger.debug(f"使用普通连接到 {server_config.smtp_server}:{server_config.smtp_port}")
                server = smtplib.SMTP(
                    server_config.smtp_server,
                    server_config.smtp_port,
                    timeout=30
                )

                # 如果配置了TLS，启用TLS
                if server_config.use_tls:
                    self.logger.debug("启用TLS加密")
                    server.starttls(context=ssl.create_default_context())

            self.logger.debug(f"服务器 [{server_config.name}] 连接成功，开始认证")

            # 登录邮箱
            server.login(server_config.smtp_user, server_config.smtp_password)

            self.logger.debug(f"服务器 [{server_config.name}] 认证成功，开始发送邮件")

            # 更新邮件的发件人信息（使用当前服务器的配置）
            # QQ邮箱等国内服务要求From头必须是纯邮箱地址
            if 'From' in message:
                del message['From']
            message['From'] = server_config.smtp_user

            # 发送邮件
            text = message.as_string()
            server.sendmail(server_config.smtp_user, receivers, text)

            self.logger.debug(f"服务器 [{server_config.name}] 邮件发送成功，收件人: {', '.join(receivers)}")

            # 关闭连接
            server.quit()

            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"服务器 [{server_config.name}] SMTP认证失败"
            suggestion = self._get_auth_error_suggestion(server_config, is_primary)
            self.logger.error(f"{error_msg}: {e}\n  建议解决方法: {suggestion}")
            return False

        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"服务器 [{server_config.name}] 收件人被拒绝: {e}")
            self.logger.error("  请检查收件人邮箱地址是否正确")
            return False

        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"服务器 [{server_config.name}] 连接断开"
            suggestion = self._get_connection_error_suggestion(server_config, is_primary)
            self.logger.error(f"{error_msg}: {e}\n  建议解决方法: {suggestion}")
            return False

        except smtplib.SMTPConnectError as e:
            error_msg = f"无法连接到服务器 [{server_config.name}]"
            suggestion = self._get_connection_error_suggestion(server_config, is_primary)
            self.logger.error(f"{error_msg}: {e}\n  建议解决方法: {suggestion}")
            return False

        except smtplib.SMTPException as e:
            self.logger.error(f"服务器 [{server_config.name}] SMTP错误: {e}")
            return False

        except OSError as e:
            error_msg = f"服务器 [{server_config.name}] 网络错误"
            suggestion = self._get_network_error_suggestion(server_config, is_primary)
            self.logger.error(f"{error_msg}: {e}\n  建议解决方法: {suggestion}")
            return False

        except Exception as e:
            self.logger.error(f"服务器 [{server_config.name}] 发送邮件时发生未知错误: {e}")
            import traceback
            self.logger.debug(f"错误堆栈:\n{traceback.format_exc()}")
            return False

        finally:
            # 确保连接被关闭
            if server is not None:
                try:
                    server.quit()
                except:
                    pass

    def _get_auth_error_suggestion(self, server_config: SmtpServerConfig, is_primary: bool) -> str:
        """获取认证错误的解决建议"""
        if 'gmail.com' in server_config.smtp_server.lower():
            return (
                "1. Gmail在国内可能无法访问，建议配置QQ邮箱等国内邮件服务作为备用服务器\n"
                "   2. 请确认使用的是应用专用密码，而非Google账户密码\n"
                "   3. 前往 Google账户设置 -> 安全性 -> 两步验证 -> 应用专用密码 生成密码"
            )
        elif 'qq.com' in server_config.smtp_server.lower():
            return (
                "1. 请确保已开启QQ邮箱SMTP服务\n"
                "   2. 登录QQ邮箱 -> 设置 -> 账户 -> SMTP服务\n"
                "   3. 使用授权码（而非登录密码）：\n"
                "      登录QQ邮箱 -> 设置 -> 账户 -> 生成授权码"
            )
        elif '163.com' in server_config.smtp_server.lower():
            return (
                "1. 请确保已开启163邮箱SMTP服务\n"
                "   2. 使用授权码（而非登录密码）\n"
                "   3. 检查是否因安全问题被暂时锁定"
            )
        else:
            return "请检查用户名和密码/授权码是否正确"

    def _get_connection_error_suggestion(self, server_config: SmtpServerConfig, is_primary: bool) -> str:
        """获取连接错误的解决建议"""
        if 'gmail.com' in server_config.smtp_server.lower():
            return (
                "1. Gmail在国内无法直接访问，建议使用QQ邮箱等国内邮件服务\n"
                "   2. 如果需要使用Gmail，请配置VPN或代理\n"
                "   3. 建议在config.yaml中将QQ邮箱配置为primary_server"
            )
        else:
            return (
                "1. 请检查网络连接是否正常\n"
                "   2. 检查防火墙设置\n"
                "   3. 确认SMTP服务器地址和端口配置正确\n"
                f"   4. 当前配置端口: {server_config.smtp_port}"
            )

    def _get_network_error_suggestion(self, server_config: SmtpServerConfig, is_primary: bool) -> str:
        """获取网络错误的解决建议"""
        return self._get_connection_error_suggestion(server_config, is_primary)

    def _log_failure_suggestions(self, servers: List[SmtpServerConfig]) -> None:
        """记录所有服务器尝试失败后的总结建议"""
        self.logger.error("=" * 70)
        self.logger.error("所有邮件服务器均发送失败，总结建议：")
        self.logger.error("=" * 70)

        for i, server in enumerate(servers):
            is_primary = (i == 0)
            server_type = "主服务器" if is_primary else f"备用服务器{i}"
            self.logger.error(f"\n{server_type}: [{server.name}]")

            if 'gmail.com' in server.smtp_server.lower():
                self.logger.error("  问题: Gmail在国内无法直接访问")
                self.logger.error("  建议: 请配置QQ邮箱、163邮箱等国内邮件服务")
            elif 'qq.com' in server.smtp_server.lower():
                self.logger.error("  问题: QQ邮箱认证失败或服务未开启")
                self.logger.error("  建议: ")
                self.logger.error("    1. 登录QQ邮箱 -> 设置 -> 账户 -> 开启SMTP服务")
                self.logger.error("    2. 生成授权码（非登录密码）")
                self.logger.error("    3. 在config.yaml中更新授权码")
            else:
                self.logger.error("  问题: 连接或认证失败")
                self.logger.error(f"  建议: 检查 {server.name} 的SMTP配置和网络连接")

        self.logger.error("\n" + "=" * 70)
        self.logger.error("如需帮助，请查看: https://github.com/your-repo/docs/email-troubleshooting.md")
        self.logger.error("=" * 70)
    
    def validate_email_config(self) -> List[str]:
        """
        验证邮件配置的有效性

        Returns:
            验证错误列表，空列表表示验证通过
        """
        errors = []

        # 验证主服务器配置
        primary = self.email_config.primary_server
        if not primary.smtp_server:
            errors.append("主SMTP服务器地址不能为空")

        if not (1 <= primary.smtp_port <= 65535):
            errors.append("主SMTP端口必须在1-65535之间")

        if not primary.smtp_user:
            errors.append("主SMTP用户名不能为空")

        if not primary.smtp_password:
            errors.append("主SMTP密码不能为空")

        # 验证备用服务器配置
        for i, backup in enumerate(self.email_config.backup_servers):
            if not backup.smtp_server:
                errors.append(f"备用服务器{i+1}的SMTP地址不能为空")

            if not (1 <= backup.smtp_port <= 65535):
                errors.append(f"备用服务器{i+1}的SMTP端口必须在1-65535之间")

            if not backup.smtp_user:
                errors.append(f"备用服务器{i+1}的SMTP用户名不能为空")

            if not backup.smtp_password:
                errors.append(f"备用服务器{i+1}的SMTP密码不能为空")

        # 验证收件人配置
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