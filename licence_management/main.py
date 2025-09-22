"""
人员证件有效期管控系统 - 主程序入口

这是系统的主程序入口，提供命令行接口和核心业务流程控制。
"""

import sys
import argparse
from typing import List, Optional
from datetime import datetime

from .config.config_manager import ConfigManager
from .data.csv_processor import CSVProcessor, PersonDocument
from .business.reminder_logic import ReminderLogic
from .email.email_sender import EmailSender
from .utils.logger import get_logger, setup_default_logger
from .utils.date_utils import DateUtils


class LicenceManagementApp:
    """证件管理应用主类"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化应用
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.logger = None
        self.config_manager = None
        self.csv_processor = None
        self.reminder_logic = None
        self.email_sender = None
        
    def initialize(self) -> bool:
        """
        初始化应用组件
        
        Returns:
            是否初始化成功
        """
        try:
            # 初始化配置管理器
            self.config_manager = ConfigManager(self.config_file)
            config = self.config_manager.load_config()
            
            # 初始化日志记录器
            if config.log_file:
                log_file = config.log_file.format(date=DateUtils.get_today_str('%Y%m%d'))
                self.logger = get_logger("licence_management", config.log_level, log_file)
            else:
                self.logger = get_logger("licence_management", config.log_level)
            
            self.logger.info("=" * 60)
            self.logger.info("人员证件有效期管控系统启动")
            self.logger.info(f"配置文件: {self.config_file}")
            self.logger.info(f"数据文件: {config.data_file}")
            
            # 验证配置
            config_errors = self.config_manager.validate_config()
            if config_errors:
                self.logger.error("配置验证失败:")
                for error in config_errors:
                    self.logger.error(f"  - {error}")
                return False
            
            self.logger.info("配置验证通过")
            
            # 初始化其他组件
            self.csv_processor = CSVProcessor(self.logger)
            self.reminder_logic = ReminderLogic(self.logger)
            self.email_sender = EmailSender(config.email, config.mail_template, self.logger)
            
            # 验证邮件配置
            email_errors = self.email_sender.validate_email_config()
            if email_errors:
                self.logger.warning("邮件配置验证失败:")
                for error in email_errors:
                    self.logger.warning(f"  - {error}")
                self.logger.warning("邮件功能可能不可用")
            
            self.logger.info("应用初始化完成")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"应用初始化失败: {e}")
            else:
                print(f"应用初始化失败: {e}")
            return False
    
    def run_reminder(self) -> bool:
        """
        运行邮件提醒流程
        
        Returns:
            是否执行成功
        """
        self.logger.info("开始执行邮件提醒流程")
        
        try:
            config = self.config_manager.config
            
            # 读取CSV数据
            self.logger.info(f"读取CSV数据文件: {config.data_file}")
            documents = self.csv_processor.read_csv_file(config.data_file)
            
            if not documents:
                self.logger.warning("没有找到任何证件数据")
                return True
            
            # 计算证件状态
            documents = self.reminder_logic.calculate_document_status(
                documents, 
                config.report.days_until_expiring_threshold
            )
            
            # 筛选需要提醒的证件
            reminder_documents = self.reminder_logic.filter_reminder_documents(
                documents, 
                config.reminder.days_before_expiry
            )
            
            if not reminder_documents:
                self.logger.info("没有需要提醒的证件")
                return True
            
            # 生成提醒汇总
            summary = self.reminder_logic.generate_reminder_summary(reminder_documents)
            self.logger.info(f"提醒汇总: 总计{summary['total_count']}个证件，"
                           f"已过期{summary['expired_count']}个，"
                           f"即将过期{summary['expiring_count']}个")
            
            # 发送提醒邮件
            success = self.email_sender.send_reminder_email(reminder_documents)
            
            if success:
                self.logger.info("邮件提醒流程执行成功")
            else:
                self.logger.error("邮件发送失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"邮件提醒流程执行失败: {e}")
            return False
    
    def run_report(self, output_file: Optional[str] = None) -> bool:
        """
        运行状态报告生成流程
        
        Args:
            output_file: 输出文件路径，如果为None则使用配置中的文件名
            
        Returns:
            是否执行成功
        """
        self.logger.info("开始执行状态报告生成流程")
        
        try:
            config = self.config_manager.config
            
            # 读取CSV数据
            self.logger.info(f"读取CSV数据文件: {config.data_file}")
            documents = self.csv_processor.read_csv_file(config.data_file)
            
            if not documents:
                self.logger.warning("没有找到任何证件数据")
                return True
            
            # 计算证件状态
            documents = self.reminder_logic.calculate_document_status(
                documents, 
                config.report.days_until_expiring_threshold
            )
            
            # 生成输出文件名
            if output_file is None:
                today = DateUtils.get_today_str('%Y%m%d')
                output_file = config.report.output_filename.format(date=today)
            
            # 写入状态报告
            self.csv_processor.write_csv_file(
                documents, 
                output_file, 
                include_calculated_fields=True
            )
            
            # 统计报告
            status_counts = {}
            for doc in documents:
                status = doc.status or "未知"
                status_counts[status] = status_counts.get(status, 0) + 1
            
            self.logger.info(f"状态报告生成完成: {output_file}")
            self.logger.info(f"证件状态统计: {status_counts}")
            
            print(f"\n✅ 状态报告生成完成！")
            print(f"📄 报告文件: {output_file}")
            print(f"📊 证件状态统计:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}个")
            
            return True
            
        except Exception as e:
            self.logger.error(f"状态报告生成失败: {e}")
            return False
    
    def run_test_email(self) -> bool:
        """
        运行测试邮件发送
        
        Returns:
            是否执行成功
        """
        self.logger.info("开始发送测试邮件")
        
        try:
            success = self.email_sender.send_test_email()
            
            if success:
                self.logger.info("测试邮件发送成功")
                print("\n✅ 测试邮件发送成功！请检查您的邮箱。")
            else:
                self.logger.error("测试邮件发送失败")
                print("\n❌ 测试邮件发送失败，请检查邮件配置。")
            
            return success
            
        except Exception as e:
            self.logger.error(f"测试邮件发送失败: {e}")
            print(f"\n❌ 测试邮件发送失败: {e}")
            return False
    
    def create_sample_data(self) -> bool:
        """
        创建示例数据文件
        
        Returns:
            是否创建成功
        """
        self.logger.info("开始创建示例数据文件")
        
        try:
            config = self.config_manager.config
            self.csv_processor.create_sample_csv(config.data_file)
            
            print(f"\n✅ 示例数据文件创建完成！")
            print(f"📄 数据文件: {config.data_file}")
            print("🔍 您可以编辑此文件来添加实际的证件数据。")
            
            return True
            
        except Exception as e:
            self.logger.error(f"创建示例数据文件失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.logger:
            self.logger.info("应用执行完成")
            self.logger.info("=" * 60)


def create_default_config():
    """创建默认配置文件"""
    config_manager = ConfigManager()
    config_manager.save_default_config("config_templates/config_template.yaml")
    print("\n✅ 默认配置文件模板已创建！")
    print("📄 配置模板: config_templates/config_template.yaml")
    print("📝 请复制模板文件为 config.yaml 并修改其中的配置项。")


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="人员证件有效期管控系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m licence_management                    # 运行邮件提醒（默认）
  python -m licence_management --report          # 生成状态报告
  python -m licence_management --test-email      # 发送测试邮件
  python -m licence_management --create-sample   # 创建示例数据
  python -m licence_management --init-config     # 创建配置文件模板
  
配置文件:
  程序默认使用当前目录下的 config.yaml 文件作为配置文件。
  可以使用 --config 参数指定不同的配置文件路径。
        """
    )
    
    # 添加命令行参数
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='生成证件状态报告'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='状态报告输出文件路径'
    )
    
    parser.add_argument(
        '--test-email', '-t',
        action='store_true',
        help='发送测试邮件'
    )
    
    parser.add_argument(
        '--create-sample', '-s',
        action='store_true',
        help='创建示例数据文件'
    )
    
    parser.add_argument(
        '--init-config', '-i',
        action='store_true',
        help='创建默认配置文件模板'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    args = parser.parse_args()
    
    # 处理创建配置文件模板
    if args.init_config:
        create_default_config()
        return 0
    
    # 创建应用实例
    app = LicenceManagementApp(args.config)
    
    try:
        # 初始化应用
        if not app.initialize():
            print("❌ 应用初始化失败，请检查配置文件。")
            return 1
        
        # 执行不同的操作模式
        success = True
        
        if args.create_sample:
            success = app.create_sample_data()
        elif args.test_email:
            success = app.run_test_email()
        elif args.report:
            success = app.run_report(args.output)
        else:
            # 默认运行邮件提醒
            success = app.run_reminder()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        return 1
    finally:
        app.cleanup()


if __name__ == "__main__":
    sys.exit(main()) 