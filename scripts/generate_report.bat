@echo off
chcp 65001 >nul
title 证件状态报告生成器

echo ====================================================
echo            证件状态报告自动生成脚本
echo ====================================================
echo.

REM 切换到项目根目录
cd /d "%~dp0.."

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请确保已安装Python并添加到PATH环境变量
    echo.
    echo 💡 提示: 您可以从 https://www.python.org/ 下载安装Python
    pause
    exit /b 1
)

REM 检查配置文件是否存在
if not exist "config.yaml" (
    echo ⚠️  警告: 未找到配置文件 config.yaml
    echo 正在创建默认配置文件...
    python -m licence_management --init-config
    if errorlevel 1 (
        echo ❌ 创建配置文件失败
        pause
        exit /b 1
    )
    echo.
    echo ✅ 配置文件模板已创建，请编辑 config.yaml 文件后重新运行此脚本
    echo.
    pause
    exit /b 0
)

REM 运行报告生成脚本
echo 🚀 正在生成证件状态报告...
echo.

python scripts/generate_report.py --summary --open

if errorlevel 1 (
    echo.
    echo ❌ 报告生成失败，请检查错误信息
    echo.
    echo 💡 故障排除建议:
    echo    1. 检查 config.yaml 配置文件是否正确
    echo    2. 检查数据文件路径是否存在
    echo    3. 查看日志文件了解详细错误信息
) else (
    echo.
    echo ✅ 报告生成完成！
)

echo.
echo 按任意键退出...
pause >nul 