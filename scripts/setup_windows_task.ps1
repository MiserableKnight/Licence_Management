# Windows任务计划程序设置脚本
# 创建两个任务（默认）：
# 1) 每天21:00 正常执行  scripts\scheduled_runner.py run
# 2) 每天10:30 补偿执行  scripts\scheduled_runner.py catchup

param(
    [string]$ProjectPath = "D:\Code\Licence_Management",
    [switch]$OnlyCatchup
)

Write-Host "🚀 正在设置Windows定时任务..." -ForegroundColor Green
Write-Host "📁 项目路径: $ProjectPath" -ForegroundColor Yellow

if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ 错误: 项目路径不存在: $ProjectPath" -ForegroundColor Red
    exit 1
}

$TaskMain  = "证件管理系统-每日提醒"
$TaskCatch = "证件管理系统-补偿执行"

# 通用设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

if ($OnlyCatchup) {
    # 仅创建补偿任务，不影响现有的21:00任务
    Get-ScheduledTask -TaskName $TaskCatch -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
    $ActionCatch = New-ScheduledTaskAction -Execute "python" -Argument "scripts/scheduled_runner.py catchup" -WorkingDirectory $ProjectPath
    $TriggerCatch = New-ScheduledTaskTrigger -Daily -At "10:30"
    Register-ScheduledTask -TaskName $TaskCatch -Action $ActionCatch -Trigger $TriggerCatch -Settings $Settings -Principal $Principal -Description "若前一日21:00未执行，则10:30补偿运行一次"

    Write-Host "✅ 已创建计划任务：$TaskCatch (每天 10:30)" -ForegroundColor Green
    return
}

# 默认：创建/更新两个任务
Get-ScheduledTask -TaskName $TaskMain  -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
Get-ScheduledTask -TaskName $TaskCatch -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

# 主任务 21:00
$ActionMain = New-ScheduledTaskAction -Execute "python" -Argument "scripts/scheduled_runner.py run" -WorkingDirectory $ProjectPath
$TriggerMain = New-ScheduledTaskTrigger -Daily -At "21:00"
Register-ScheduledTask -TaskName $TaskMain -Action $ActionMain -Trigger $TriggerMain -Settings $Settings -Principal $Principal -Description "每天21:00自动检查证件并发邮件"

# 补偿任务 10:30
$ActionCatch = New-ScheduledTaskAction -Execute "python" -Argument "scripts/scheduled_runner.py catchup" -WorkingDirectory $ProjectPath
$TriggerCatch = New-ScheduledTaskTrigger -Daily -At "10:30"
Register-ScheduledTask -TaskName $TaskCatch -Action $ActionCatch -Trigger $TriggerCatch -Settings $Settings -Principal $Principal -Description "若前一日21:00未执行，则10:30补偿运行一次"

Write-Host "✅ 已创建两个计划任务：" -ForegroundColor Green
Write-Host "  - $TaskMain   (每天 21:00)" -ForegroundColor White
Write-Host "  - $TaskCatch  (每天 10:30)" -ForegroundColor White 