@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   证件管理系统 - Windows定时任务设置
echo ========================================
echo.
echo 正在设置每天21:00自动运行的Windows定时任务...
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 检测到管理员权限，继续执行...
) else (
    echo ❌ 需要管理员权限来创建定时任务
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo.
echo 🚀 正在创建Windows定时任务...

REM 运行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "%~dp0setup_windows_task.ps1"

if %errorlevel% equ 0 (
    echo.
    echo ✅ Windows定时任务设置完成！
    echo.
    echo 📅 任务将在每天21:00自动运行证件检查
    echo 📧 如有证件过期将自动发送邮件提醒
    echo.
    echo 💡 您可以在"任务计划程序"中查看和管理此任务
    echo    (Win+R 输入 taskschd.msc 打开任务计划程序)
) else (
    echo.
    echo ❌ 设置失败，请检查错误信息
)

echo.
pause 