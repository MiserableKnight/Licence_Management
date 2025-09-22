# 项目脚本总览（scripts/）

此目录包含人员证件有效期管控系统的辅助脚本：报告生成、定时任务、环境激活与邮件测试。本文档按用途分组说明每个脚本的作用与用法。

---

## 📌 快速索引
- `generate_report.py`：生成证件状态报告（CLI 主脚本）
- `generate_report.bat` / `generate_report.ps1`：报告生成的 Windows 便捷入口
- `scheduled_runner.py`：定时任务执行器（支持正常运行与补偿运行）
- `setup_task.bat` / `setup_windows_task.ps1`：一键创建 Windows 计划任务
- `daily_reminder_task.bat`：手动/简易每日运行脚本（兼容保留）
- `activate_env.bat` / `activate_env.ps1`：激活 Python 虚拟环境
- `send_test_email.py`：发送测试邮件，验证邮箱配置

---

## 📊 报告生成

### generate_report.py（推荐直接调用）
Python 脚本，用于生成证件状态报告，支持静默模式、摘要展示与自动打开文件。

使用示例：
```bash
# 基本用法（使用配置中的默认输出模板）
python scripts/generate_report.py

# 指定输出文件名
python scripts/generate_report.py --output "my_report.csv"

# 显示摘要并自动打开生成的报告
python scripts/generate_report.py --summary --open

# 静默模式（适合定时任务）
python scripts/generate_report.py --quiet
```

功能特性：
- 自动计算证件状态（已过期、即将过期、有效）
- 可选显示统计摘要（需安装 pandas）
- 支持自定义输出文件名与自动打开文件
- 静默模式适配定时任务

### generate_report.bat / generate_report.ps1
Windows 下的便捷入口，封装了环境检查与友好提示。

- 批处理：双击 `scripts/generate_report.bat` 或命令行执行 `scripts\generate_report.bat`
- PowerShell：`.\scripts\generate_report.ps1 -Output custom.csv -Summary -Open -Quiet`

---

## 🕘 定时任务相关

### scheduled_runner.py（定时执行器）
统一的调度包装脚本，用于由计划任务调用系统主流程，并提供“补偿执行”。

用法：
```bash
# 立即执行一次（成功则写入成功时间）
python scripts/scheduled_runner.py run

# 补偿执行：若发现前一日 21:00 未成功执行，则在当前时刻补跑一次
python scripts/scheduled_runner.py catchup
```

行为说明：
- 成功状态记录：`logs/last_success_iso.txt`
- 运行日志：`logs/scheduled_runner.log`（超过 1MB 自动轮转归档）
- 实际执行命令：`python -m licence_management`（在项目根目录）

建议：
- Windows 计划任务在 21:00 触发 `run`
- 早上 10:30 触发一次 `catchup`，确保前日晚任务缺失时自动补跑

### setup_task.bat / setup_windows_task.ps1（一键创建计划任务）
用于在 Windows“任务计划程序”中创建/更新计划任务。

- `setup_task.bat`：右键“以管理员身份运行”，内部调用 PowerShell 创建两个任务：
  - 每天 21:00 运行：`python scripts/scheduled_runner.py run`
  - 每天 10:30 补偿：`python scripts/scheduled_runner.py catchup`

- `setup_windows_task.ps1` 参数：
  - `-ProjectPath`：项目根目录，默认 `D:\Code\Licence_Management`
  - `-OnlyCatchup`：只创建/更新补偿任务（不影响现有 21:00 任务）

示例：
```powershell
# 以管理员 PowerShell 执行（如当前策略受限可先临时放开执行策略）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_windows_task.ps1 -ProjectPath "D:\Code\Licence_Management"
.\scripts\setup_windows_task.ps1 -OnlyCatchup
```

### daily_reminder_task.bat（简易版/兼容）
历史保留的每日运行脚本：切到项目根目录、可选激活虚拟环境、运行 `python -m licence_management` 并追加简要日志。

建议优先使用 `scheduled_runner.py` + 计划任务，以获得成功状态记录与日志轮转能力。

---

## 🔧 虚拟环境

- `activate_env.bat`
```batch
cd D:\Code\Licence_Management
scripts\activate_env.bat
```

- `activate_env.ps1`
```powershell
cd D:\Code\Licence_Management
.\scripts\activate_env.ps1
```

---

## 📧 邮件测试

- `send_test_email.py`
```bash
python scripts/send_test_email.py
```
用途：读取 `config.yaml`，验证 SMTP 账户、授权码与收件人配置是否正确，便于在正式开启定时任务前做连通性检查。

---

## 💡 常见问题与提示
- 请在“项目根目录”执行脚本（脚本内部也会尝试切换到根目录）
- 确保存在并正确配置 `config.yaml`（可用 `python -m licence_management --init-config` 生成模板）
- 若 PowerShell 限制执行脚本，可临时放开：`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- Windows 计划任务的“起始于(开始于)”应设置为项目根目录
- 日志目录：`logs/`，报告默认命名形如 `证件状态报告_YYYYMMDD.csv`

---

## 🔁 典型场景
- 手动生成并查看报告：
  ```bash
  python scripts/generate_report.py --summary --open
  ```
- 首次部署并测试邮件：
  ```bash
  python -m licence_management --init-config
  python scripts/send_test_email.py
  ```
- 设置 Windows 定时任务（管理员权限）：
  ```batch
  scripts\setup_task.bat
  ```
- 临时补偿执行一次（若错过昨日 21:00）：
  ```bash
  python scripts/scheduled_runner.py catchup
  ``` 