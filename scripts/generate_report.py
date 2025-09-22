#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
证件状态报告自动生成脚本

这个脚本可以自动生成证件状态报告，并提供多种输出选项。
可以单独运行，也可以通过任务调度器定时执行。

使用方法:
    python scripts/generate_report.py                    # 生成默认报告
    python scripts/generate_report.py --output custom.csv # 指定输出文件
    python scripts/generate_report.py --open             # 生成后自动打开报告
    python scripts/generate_report.py --summary          # 只显示摘要信息
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径，以便导入licence_management模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from licence_management.main import LicenceManagementApp


def print_banner():
    """打印脚本标题横幅"""
    print("=" * 60)
    print("           证件状态报告自动生成脚本")
    print("=" * 60)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def print_summary(report_file):
    """
    打印报告摘要信息
    
    Args:
        report_file: 报告文件路径
    """
    try:
        import pandas as pd
        
        # 读取报告文件
        df = pd.read_csv(report_file)
        
        print("\n📊 证件状态摘要:")
        print("-" * 40)
        
        # 统计各状态数量
        status_counts = df['status'].value_counts()
        total_count = len(df)
        
        print(f"📋 总计证件数: {total_count}个")
        
        for status, count in status_counts.items():
            percentage = (count / total_count) * 100
            icon = "🔴" if status == "已过期" else "🟡" if status == "即将过期" else "🟢"
            print(f"{icon} {status}: {count}个 ({percentage:.1f}%)")
        
        # 显示最紧急的证件
        if '已过期' in status_counts:
            expired_docs = df[df['status'] == '已过期'].sort_values('days_left')
            print(f"\n🚨 已过期证件 (共{len(expired_docs)}个):")
            for _, row in expired_docs.head(5).iterrows():
                days = abs(row['days_left']) if pd.notna(row['days_left']) else 0
                print(f"   • {row['person_name']} - {row['document_type']} (过期{days}天)")
        
        # 显示即将过期的证件
        expiring_docs = df[df['status'] == '即将过期'].sort_values('days_left')
        if len(expiring_docs) > 0:
            print(f"\n⚠️  即将过期证件 (前5个最紧急):")
            for _, row in expiring_docs.head(5).iterrows():
                days = row['days_left'] if pd.notna(row['days_left']) else 0
                print(f"   • {row['person_name']} - {row['document_type']} (还有{days}天)")
        
        print("-" * 40)
        
    except ImportError:
        print("\n💡 提示: 安装pandas可以显示详细摘要信息")
        print("   pip install pandas")
    except Exception as e:
        print(f"\n⚠️  读取报告摘要时出错: {e}")


def open_file(file_path):
    """
    使用系统默认程序打开文件
    
    Args:
        file_path: 文件路径
    """
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
        print(f"✅ 已使用默认程序打开报告: {file_path}")
    except Exception as e:
        print(f"⚠️  无法自动打开文件: {e}")
        print(f"   请手动打开: {file_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="证件状态报告自动生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/generate_report.py                    # 生成默认报告
  python scripts/generate_report.py --output custom.csv # 指定输出文件
  python scripts/generate_report.py --open             # 生成后自动打开报告
  python scripts/generate_report.py --summary          # 只显示摘要信息
  python scripts/generate_report.py --quiet            # 静默模式（适合定时任务）
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='输出文件路径 (默认使用配置文件中的格式)'
    )
    
    parser.add_argument(
        '--open',
        action='store_true',
        help='生成报告后自动打开文件'
    )
    
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='显示详细的报告摘要信息'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式，减少输出信息（适合定时任务）'
    )
    
    args = parser.parse_args()
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    if not args.quiet:
        print_banner()
    
    try:
        # 创建应用实例
        app = LicenceManagementApp(args.config)
        
        # 初始化应用
        if not app.initialize():
            print("❌ 应用初始化失败，请检查配置文件。")
            return 1
        
        if not args.quiet:
            print("🚀 开始生成证件状态报告...")
        
        # 生成报告
        success = app.run_report(args.output)
        
        if not success:
            print("❌ 报告生成失败，请检查日志文件。")
            return 1
        
        # 获取生成的报告文件路径
        if args.output:
            report_file = args.output
        else:
            from licence_management.utils.date_utils import DateUtils
            today = DateUtils.get_today_str('%Y%m%d')
            report_file = f"证件状态报告_{today}.csv"
        
        if not args.quiet:
            print(f"\n✅ 报告生成成功！")
            print(f"📄 报告文件: {report_file}")
            print(f"📍 文件位置: {os.path.abspath(report_file)}")
        
        # 显示摘要信息
        if args.summary and not args.quiet:
            print_summary(report_file)
        
        # 自动打开文件
        if args.open:
            open_file(os.path.abspath(report_file))
        
        if not args.quiet:
            print(f"\n🎉 任务完成！报告已保存至: {report_file}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        return 1
    finally:
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    sys.exit(main()) 