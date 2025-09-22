# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    证件状态报告自动生成脚本 (PowerShell版本)

.DESCRIPTION
    这个脚本可以自动生成证件状态报告，并提供多种输出选项。
    支持生成报告、显示摘要、自动打开文件等功能。

.PARAMETER Output
    指定输出文件路径

.PARAMETER Open
    生成报告后自动打开文件

.PARAMETER Summary
    显示详细的报告摘要信息

.PARAMETER Quiet
    静默模式，减少输出信息（适合定时任务）

.EXAMPLE
    .\scripts\generate_report.ps1
    生成默认报告

.EXAMPLE
    .\scripts\generate_report.ps1 -Output "custom_report.csv" -Open -Summary
    生成自定义文件名的报告，显示摘要并自动打开
#>

param(
    [string]$Config = "config.yaml",
    [string]$Output = "",
    [switch]$Open,
    [switch]$Summary,
    [switch]$Quiet
)

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 设置窗口标题
$Host.UI.RawUI.WindowTitle = "证件状态报告生成器"

function Write-Banner {
    if (-not $Quiet) {
        Write-Host "=" * 60 -ForegroundColor Cyan
        Write-Host "           证件状态报告自动生成脚本" -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Cyan
        Write-Host "执行时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
        Write-Host ""
    }
}

function Test-PythonAvailable {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        return $true
    }
    catch {
        Write-Host "❌ 错误: 未找到Python，请确保已安装Python并添加到PATH环境变量" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 提示: 您可以从 https://www.python.org/ 下载安装Python" -ForegroundColor Yellow
        return $false
    }
}

function Test-ConfigFile {
    param([string]$ConfigPath)
    
    if (-not (Test-Path $ConfigPath)) {
        Write-Host "⚠️  警告: 未找到配置文件 $ConfigPath" -ForegroundColor Yellow
        Write-Host "正在创建默认配置文件..." -ForegroundColor Cyan
        
        $result = python -m licence_management --init-config
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 创建配置文件失败" -ForegroundColor Red
            return $false
        }
        
        Write-Host ""
        Write-Host "✅ 配置文件模板已创建，请编辑 $ConfigPath 文件后重新运行此脚本" -ForegroundColor Green
        return $false
    }
    return $true
}

function Invoke-ReportGeneration {
    param(
        [string]$ConfigFile,
        [string]$OutputFile,
        [bool]$ShowSummary,
        [bool]$OpenFile,
        [bool]$QuietMode
    )
    
    # 构建命令行参数
    $args = @("scripts/generate_report.py")
    
    if ($ConfigFile -ne "config.yaml") {
        $args += "--config", $ConfigFile
    }
    
    if ($OutputFile) {
        $args += "--output", $OutputFile
    }
    
    if ($ShowSummary) {
        $args += "--summary"
    }
    
    if ($OpenFile) {
        $args += "--open"
    }
    
    if ($QuietMode) {
        $args += "--quiet"
    }
    
    if (-not $QuietMode) {
        Write-Host "🚀 正在生成证件状态报告..." -ForegroundColor Cyan
        Write-Host ""
    }
    
    # 执行Python脚本
    $result = python @args
    
    return $LASTEXITCODE -eq 0
}

# 主程序逻辑
try {
    # 切换到项目根目录
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptDir
    Set-Location $projectRoot
    
    Write-Banner
    
    # 检查Python环境
    if (-not (Test-PythonAvailable)) {
        if (-not $Quiet) {
            Write-Host ""
            Write-Host "按任意键退出..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        exit 1
    }
    
    # 检查配置文件
    if (-not (Test-ConfigFile $Config)) {
        if (-not $Quiet) {
            Write-Host ""
            Write-Host "按任意键退出..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        exit 0
    }
    
    # 生成报告
    $success = Invoke-ReportGeneration -ConfigFile $Config -OutputFile $Output -ShowSummary $Summary -OpenFile $Open -QuietMode $Quiet
    
    if ($success) {
        if (-not $Quiet) {
            Write-Host ""
            Write-Host "✅ 报告生成完成！" -ForegroundColor Green
        }
        $exitCode = 0
    }
    else {
        if (-not $Quiet) {
            Write-Host ""
            Write-Host "❌ 报告生成失败，请检查错误信息" -ForegroundColor Red
            Write-Host ""
            Write-Host "💡 故障排除建议:" -ForegroundColor Yellow
            Write-Host "   1. 检查 config.yaml 配置文件是否正确" -ForegroundColor Gray
            Write-Host "   2. 检查数据文件路径是否存在" -ForegroundColor Gray
            Write-Host "   3. 查看日志文件了解详细错误信息" -ForegroundColor Gray
        }
        $exitCode = 1
    }
}
catch {
    Write-Host "❌ 执行过程中出现错误: $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}
finally {
    if (-not $Quiet) {
        Write-Host ""
        Write-Host "按任意键退出..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

exit $exitCode 