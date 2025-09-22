# 人员证件有效期管控系统 - 虚拟环境激活脚本

Write-Host "正在激活人员证件有效期管控系统虚拟环境..." -ForegroundColor Green

# 激活虚拟环境
& "$PSScriptRoot\..\venv\Scripts\Activate.ps1"

Write-Host "虚拟环境已激活！" -ForegroundColor Green
Write-Host ""
Write-Host "可用命令:" -ForegroundColor Yellow
Write-Host "  python main.py          - 运行主程序" -ForegroundColor Cyan
Write-Host "  pip list                - 查看已安装的包" -ForegroundColor Cyan
Write-Host "  deactivate              - 退出虚拟环境" -ForegroundColor Cyan
Write-Host ""
Write-Host "当前已安装的依赖库:" -ForegroundColor Yellow
pip list 