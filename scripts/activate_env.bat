@echo off
echo 正在激活人员证件有效期管控系统虚拟环境...
call ..\venv\Scripts\activate.bat
echo 虚拟环境已激活！
echo.
echo 可用命令:
echo   python main.py          - 运行主程序
echo   pip list                - 查看已安装的包
echo   deactivate              - 退出虚拟环境
echo.
cmd /k 