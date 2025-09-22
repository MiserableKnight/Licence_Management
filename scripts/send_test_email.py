#!/usr/bin/env python3
"""
使用项目配置发送测试邮件
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from licence_management.config.config_manager import ConfigManager
from licence_management.email.email_sender import EmailSender
from licence_management.utils.logger import get_logger


def send_test_email():
    """发送测试邮件"""
    print("🚀 证件管理系统 - Gmail邮件测试")
    print("=" * 50)
    
    try:
        # 加载配置
        print("📋 加载配置文件...")
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        
        print(f"✅ 配置加载成功")
        print(f"📤 发送邮箱: {config.email.smtp_user}")
        print(f"📨 接收邮箱: {config.email.receiver_email}")
        print(f"🌐 SMTP服务器: {config.email.smtp_server}:{config.email.smtp_port}")
        
        # 验证配置
        errors = config_manager.validate_config()
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ 配置验证通过")
        
        # 创建邮件发送器
        logger = get_logger("gmail_test")
        email_sender = EmailSender(
            email_config=config.email,
            template_config=config.mail_template,
            logger=logger
        )
        
        # 发送测试邮件
        print("\n📧 发送Gmail测试邮件...")
        test_subject = f"Gmail邮件测试 - 证件管理系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success = email_sender.send_test_email(test_subject)
        
        if success:
            print("🎉 Gmail测试邮件发送成功！")
            print(f"📬 请检查QQ邮箱: {config.email.receiver_email}")
            print("💡 如果收件箱没有邮件，请检查垃圾邮件文件夹")
            print("\n✅ Gmail邮件配置完全正常，可以使用证件管理系统了！")
            return True
        else:
            print("❌ Gmail测试邮件发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False


def main():
    """主函数"""
    success = send_test_email()
    
    if success:
        print(f"\n🎯 下一步:")
        print("1. 检查QQ邮箱是否收到测试邮件")
        print("2. 运行完整的证件管理系统")
        print("3. 系统会自动发送证件到期提醒")
    else:
        print(f"\n🔧 如果测试失败，请检查:")
        print("1. Gmail应用专用密码是否正确")
        print("2. 网络连接是否正常")
        print("3. Gmail两步验证是否已启用")


if __name__ == "__main__":
    main() 