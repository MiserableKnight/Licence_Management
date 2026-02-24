# 人员证件有效期管控系统 v1.3

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🎯 **自动化的人员证件有效期管理解决方案**
>
> 通过CSV批量导入、智能邮件提醒和全局状态报告，帮助企业和个人高效管理各类证件的有效期。支持多邮件服务器自动切换，确保提醒邮件送达。

## ✨ 核心功能

- 📧 **智能邮件提醒** - 将当日所有到期提醒汇总为一封HTML邮件，避免邮件轰炸
- 🔄 **邮件服务器自动切换** - 主服务器失败时自动切换到备用服务器，最多重试3次
- 📊 **一键状态报告** - 随时生成包含所有证件状态的综合CSV报告
- 🎯 **灵活提醒规则** - 支持多节点自定义提醒（如：60、30、10、7、1天前）
- 📁 **CSV批量管理** - 支持大批量人员证件信息的导入和更新
- 🛡️ **增强日期验证** - 自动检测并过滤无效日期（如 99/99/9999），防止系统运行失败
- 🤖 **完全自动化** - 配合Windows任务计划程序实现无人值守运行
- 📝 **详细日志记录** - 记录所有操作和异常，便于问题排查

## 📋 系统要求

- **Python**: 3.10 或更高版本
- **操作系统**: Windows 10/11（推荐），或 Linux/macOS
- **邮箱**: 支持SMTP的邮箱服务（QQ邮箱、Gmail、163邮箱等）

## 🚀 快速开始

### 1. 克隆或下载项目

```bash
# 克隆项目
git clone <repository-url>
cd Licence_Management

# 或下载并解压ZIP文件后进入项目目录
```

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装所需依赖包
pip install -r requirements.txt

# 或手动安装
pip install pandas PyYAML python-dateutil
```

### 4. 生成配置文件

```bash
# 生成配置文件模板
python -m licence_management --init-config

# 会生成 config_templates/config_template.yaml
# 将其复制为 config.yaml 并修改配置
```

### 5. 配置系统

复制配置文件模板并根据实际情况修改：

```bash
# Windows
copy config_templates\config_template.yaml config.yaml
notepad config.yaml

# Linux/macOS
cp config_templates/config_template.yaml config.yaml
nano config.yaml
```

**重要配置项：**

```yaml
# 数据文件路径
data_file: sample_data/人员证件信息.csv

# 邮件服务器配置（支持多服务器自动切换）
email:
  primary_server:
    name: Gmail
    smtp_server: smtp.gmail.com
    smtp_port: 587
    smtp_user: your_email@gmail.com
    smtp_password: your_app_password  # 使用应用专用密码
    sender_name: 证件管理系统
    use_ssl: false
    use_tls: true

  backup_servers:  # 备用服务器列表
    - name: QQ邮箱
      smtp_server: smtp.qq.com
      smtp_port: 587
      smtp_user: your_email@qq.com
      smtp_password: your_qq_auth_code
      sender_name: 证件管理系统
      use_ssl: false
      use_tls: true

  receiver_email: recipient@example.com,another@example.com  # 多个收件人用逗号分隔

# 提醒规则
reminder:
  days_before_expiry:
    - 60  # 提前60天提醒
    - 30  # 提前30天提醒
    - 10  # 提前10天提醒
    - 7   # 提前7天提醒
    - 1   # 提前1天提醒

# 报告配置
report:
  days_until_expiring_threshold: 30  # 超过30天显示为"有效"
  output_filename: 证件状态报告_{date}.csv

# 日志配置
log_level: INFO
log_file: logs/licence_management_{date}.log
```

### 6. 准备数据文件

创建或编辑 `sample_data/人员证件信息.csv` 文件：

```csv
person_name,document_type,start_date,expiry_date,remarks
张三,护照,09/10/2025,15/03/2026,研发部
李四,身份证,05/09/2025,20/03/2026,市场部
王五,工作签,09/10/2025,03/03/2026,即将到期
```

**日期格式要求**: `DD/MM/YYYY`（日/月/年）

### 7. 运行测试

```bash
# 生成状态报告（不发送邮件）
python -m licence_management --report

# 发送测试邮件
python -m licence_management --test-email

# 执行完整的邮件提醒流程
python -m licence_management
```

## 📧 常用邮箱配置

| 邮箱 | SMTP服务器 | 端口 | SSL/TLS | 获取授权码方式 |
|------|------------|------|---------|----------------|
| QQ邮箱 | smtp.qq.com | 587 | TLS | 设置 -> 账户 -> 开启SMTP -> 生成授权码 |
| 163邮箱 | smtp.163.com | 465 | SSL | 设置 -> POP3/SMTP/IMAP -> 开启服务 |
| Gmail | smtp.gmail.com | 587 | TLS | Google账户 -> 安全 -> 两步验证 -> 应用密码 |

**⚠️ 注意事项:**
- **不要使用登录密码**，必须使用授权码（或应用专用密码）
- Gmail需要先开启两步验证才能生成应用密码
- QQ邮箱需要在设置中手动开启SMTP服务

## 🤖 设置自动化任务

### Windows 任务计划程序（推荐）

项目提供了自动化脚本，一键设置定时任务：

```powershell
# 以管理员身份运行 PowerShell
# 进入项目目录
cd D:\Code\Licence_Management

# 运行设置脚本
powershell -ExecutionPolicy Bypass -File scripts\setup_windows_task.ps1
```

**手动设置步骤：**

1. 打开"任务计划程序"（Win+R 输入 `taskschd.msc`）
2. 点击"创建基本任务"
3. 任务名称：`证件管理系统-每日提醒`
4. 触发器：每天 21:00
5. 操作：启动程序
   - 程序：`python`（或完整路径如 `C:\Python311\python.exe`）
   - 参数：`scripts\scheduled_runner.py run`
   - 起始于：`D:\Code\Licence_Management`（你的项目路径）

### Linux/macOS Crontab

```bash
# 编辑定时任务
crontab -e

# 添加以下行（每天晚上9点执行）
0 21 * * * cd /path/to/Licence_Management && /usr/bin/python3 -m licence_management

# 或使用补偿机制（先在9点执行，失败则在次日10:30补偿）
0 21 * * * cd /path/to/Licence_Management && /usr/bin/python3 scripts/scheduled_runner.py run
30 10 * * * cd /path/to/Licence_Management && /usr/bin/python3 scripts/scheduled_runner.py catchup
```

## 📊 数据格式说明

CSV文件必须包含以下字段：

| 字段名 | 说明 | 是否必填 | 格式 | 示例 |
|--------|------|----------|------|------|
| person_name | 姓名 | ✅ | 文本 | 张三 |
| document_type | 证件类型 | ✅ | 文本 | 护照/工作签/河内通行证 |
| start_date | 有效期起始 | ❌ | DD/MM/YYYY | 09/10/2025 |
| expiry_date | 有效期截止 | ✅ | DD/MM/YYYY | 15/03/2026 |
| remarks | 备注 | ❌ | 文本 | 研发部/已办理/办理中 |

**日期注意事项**：
- 日期格式必须为 `DD/MM/YYYY`（日/月/年）
- 年份应在合理范围内（1900-2100）
- 长期有效的证件建议使用 `31/12/2099`
- 无效日期的记录会被自动跳过并在日志中记录警告

**特殊备注值：**
- `已办理` - 标记为已办理，不会发送提醒
- `办理中` - 仅作记录，仍会发送提醒

## 🔧 命令行参数

```bash
# 默认：发送邮件提醒
python -m licence_management

# 生成状态报告
python -m licence_management --report
python -m licence_management -r

# 指定报告输出文件
python -m licence_management --report --output my_report.csv
python -m licence_management -r -o my_report.csv

# 发送测试邮件
python -m licence_management --test-email
python -m licence_management -t

# 创建示例数据文件
python -m licence_management --create-sample
python -m licence_management -s

# 生成配置文件模板
python -m licence_management --init-config
python -m licence_management -i

# 使用自定义配置文件
python -m licence_management --config my_config.yaml
python -m licence_management -c my_config.yaml

# 显示详细日志
python -m licence_management --verbose
python -m licence_management -v
```

## 📂 项目结构

```
Licence_Management/
├── licence_management/        # 核心代码模块
│   ├── __init__.py
│   ├── __main__.py           # 程序入口
│   ├── main.py               # 主应用类
│   ├── config/               # 配置管理
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── data/                 # 数据处理
│   │   ├── __init__.py
│   │   └── csv_processor.py
│   ├── business/             # 业务逻辑
│   │   ├── __init__.py
│   │   └── reminder_logic.py
│   ├── email/                # 邮件发送
│   │   ├── __init__.py
│   │   └── email_sender.py
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── date_utils.py
│       └── logger.py
├── scripts/                  # 自动化脚本
│   ├── scheduled_runner.py   # 调度包装脚本
│   ├── setup_windows_task.ps1  # Windows任务设置
│   ├── setup_task.bat        # Windows批处理
│   ├── generate_report.bat   # 生成报告快捷方式
│   └── activate_env.bat      # 激活虚拟环境
├── config_templates/         # 配置模板
│   └── config_template.yaml
├── sample_data/              # 数据文件目录
│   └── 人员证件信息.csv
├── logs/                     # 日志目录
│   ├── licence_management_*.log
│   └── scheduled_runner.log
├── config.yaml               # 主配置文件（需自行创建）
├── requirements.txt          # 项目依赖
├── README.md                 # 本文件
└── REQUIREMENTS.md           # 详细需求文档
```

## ❓ 常见问题

### 邮件发送失败

**问题**: 提示"邮件发送失败"或"认证失败"

**解决方案**:
1. 确认使用的是**授权码**而非登录密码
2. 检查SMTP服务是否已开启
3. 确认端口号正确（SSL通常用465，TLS通常用587）
4. 检查防火墙是否阻止了SMTP端口
5. 查看日志文件 `logs/licence_management_*.log` 获取详细错误信息

### 日期格式错误

**问题**: 提示"日期格式无效"

**解决方案**:
1. 确保日期格式为 `DD/MM/YYYY`（如 09/10/2025）
2. 不要使用 `YYYY-MM-DD` 或其他格式
3. 日期必须符合日历规则（如 99/99/9999 是无效的）
4. 系统会自动跳过无效日期的记录并在日志中记录警告
5. 建议使用合理的日期范围（1900-01-01 到 2100-12-31）

**长期有效证件的日期建议**：
- 对于长期或永久有效的证件，建议使用 `31/12/2099` 作为到期日期
- 避免使用明显无效的日期（如 9999年），否则该记录将被跳过

### 程序运行无反应

**问题**: 运行命令后没有任何输出

**解决方案**:
1. 使用 `--verbose` 参数查看详细日志
2. 检查 `config.yaml` 文件是否存在且格式正确
3. 确认数据文件路径正确
4. 查看日志文件 `logs/licence_management_*.log`
5. 确认Python版本为3.10或更高

### 定时任务未执行

**问题**: 设置了定时任务但没有收到邮件

**解决方案**:
1. Windows: 打开"任务计划程序"检查任务状态和历史记录
2. 手动运行任务验证是否正常
3. 确认Python路径正确（使用完整路径）
4. 检查日志文件 `logs/scheduled_runner.log`
5. 确认计算机在指定时间处于开机状态

### 收到了邮件但内容为空

**问题**: 收到提醒邮件但没有具体证件信息

**解决方案**:
1. 检查数据文件是否有符合提醒条件的证件
2. 使用 `--report` 参数生成状态报告查看详情
3. 确认 `reminder.days_before_expiry` 配置是否合理
4. 检查证件备注是否为"已办理"（如果是则不会提醒）

## 📝 更多信息

- [配置文件模板](config_templates/config_template.yaml) - 完整配置示例
- [日志文件位置](logs/) - 查看详细运行日志和错误信息

## 🆕 更新日志

### v1.3 (2026-02-24)
- ✅ **增强日期验证** - 添加日期合理性检查，防止无效日期（如 99/99/9999）导致系统失败
- ✅ **自动跳过无效记录** - 对无效日期记录跳过处理并记录警告日志
- ✅ **优化错误提示** - 在日志中明确标注无效日期的行号和具体值
- ✅ **更新文档** - 添加日期处理建议和最佳实践

### v1.2
- ✅ 添加邮件服务器自动切换功能
- ✅ 支持多个备用邮件服务器
- ✅ 优化邮件发送重试机制

### v1.1
- ✅ 添加定时任务补偿机制
- ✅ 支持一键状态报告生成
- ✅ 优化日志记录和错误处理

## 🔒 安全建议

1. **不要将包含密码的 config.yaml 提交到版本控制系统**
2. **将敏感邮箱信息添加到 .gitignore**
3. **定期更换邮箱授权码**
4. **使用应用专用密码而非登录密码**

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个Star支持一下！⭐**

**💡 遇到问题？欢迎提交 Issue 或 Pull Request**

</div>
