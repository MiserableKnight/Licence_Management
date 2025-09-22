@echo off
REM 证件管理系统 - 每日自动提醒任务
REM 运行时间：每天21:00

echo ======================================
echo 证件管理系统 - 每日自动检查
echo 开始时间: %date% %time%
echo ======================================

REM 切换到项目目录
cd /d "D:\Code\Licence_Management"

REM 激活虚拟环境（如果使用的话）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 运行证件提醒程序
echo 开始执行证件过期检查...
python -m licence_management

REM 检查执行结果
if %errorlevel% equ 0 (
    echo ✅ 证件检查任务执行成功
) else (
    echo ❌ 证件检查任务执行失败，错误代码: %errorlevel%
)

echo ======================================
echo 任务完成时间: %date% %time%
echo ======================================

REM 将日志追加到文件
echo [%date% %time%] 每日证件检查任务执行完成 >> logs\daily_task.log 