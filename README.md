# 人员证件有效期管控系统 v1.2

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🎯 **自动化的人员证件有效期管理解决方案**
> 
> 通过CSV批量导入、智能邮件提醒和全局状态报告，帮助企业和个人高效管理各类证件的有效期。

## ✨ 核心功能

- 📧 **智能邮件提醒** - 将当日所有到期提醒汇总为一封HTML邮件，避免邮件轰炸
- 📊 **一键状态报告** - 随时生成包含所有证件状态的综合CSV报告  
- 🔄 **灵活提醒规则** - 支持多节点自定义提醒（如：60、30、7、1天前）
- 📁 **CSV批量管理** - 支持大批量人员证件信息的导入和更新
- 🤖 **完全自动化** - 配合定时任务实现无人值守运行

## 🚀 快速开始

### 1. 安装依赖

```bash
# 确保Python版本为3.10+
python --version

# 安装依赖包
pip install pandas PyYAML
```

### 2. 配置设置

```bash
# 复制配置文件模板
cp config.example.yaml config.yaml

# 编辑配置文件，重要：请务必修改邮箱配置
notepad config.yaml  # Windows
nano config.yaml     # Linux/macOS
```

### 3. 准备数据

创建 `data.csv` 文件，包含以下字段：

```csv
person_name,document_type,start_date,expiry_date,remarks
张三,护照,20200101,20300101,研发部
李四,身份证,20150315,20250315,市场部负责人
```

### 4. 运行程序

```bash
# 发送邮件提醒
python main.py

# 生成状态报告
python main.py --report
```

## ⚙️ 基础配置

编辑 `config.yaml` 文件中的关键配置项：

```yaml
# 邮件服务器配置
email:
  smtp_server: "smtp.qq.com"           # 邮箱服务器
  smtp_port: 465                       # 端口
  smtp_user: "your_email@qq.com"       # 邮箱账号
  smtp_password: "your_auth_code"      # 邮箱授权码
  receiver_email: "manager@company.com" # 接收提醒的邮箱

# 提醒规则
reminder:
  days_before_expiry:
    - 60  # 提前60天提醒
    - 30  # 提前30天提醒
    - 7   # 提前7天提醒
    - 1   # 提前1天提醒
```

### 📧 常用邮箱配置

| 邮箱 | SMTP服务器 | 端口 | 备注 |
|------|------------|------|------|
| QQ邮箱 | smtp.qq.com | 465 | 需开启SMTP服务，使用授权码 |
| 163邮箱 | smtp.163.com | 465 | 需开启SMTP服务，使用授权码 |
| Gmail | smtp.gmail.com | 465 | 需开启两步验证，使用应用密码 |

## 📊 数据格式

CSV文件必须包含以下字段：

| 字段名 | 说明 | 是否必填 | 格式 | 示例 |
|--------|------|----------|------|------|
| person_name | 姓名 | ✅ | 文本 | 张三 |
| document_type | 证件类型 | ✅ | 文本 | 护照 |
| start_date | 有效期起 | ❌ | YYYYMMDD | 20200101 |
| expiry_date | 有效期止 | ✅ | YYYYMMDD | 20300101 |
| remarks | 备注 | ❌ | 文本 | 研发部 |

## 🤖 自动化运行

### Windows 任务计划程序
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发时间：每天上午9点
4. 操作：运行 `python /path/to/main.py`

### Linux/macOS Crontab
```bash
# 编辑定时任务
crontab -e

# 添加：每天上午9点执行
0 9 * * * cd /path/to/licence-management && python main.py
```

## ❓ 常见问题

**Q: 邮件发送失败？**
- 检查SMTP配置是否正确
- 确认使用授权码而非登录密码
- 检查网络连接和防火墙设置

**Q: CSV格式错误？**
- 确保文件保存为UTF-8编码
- 检查列名是否与要求一致
- 日期格式必须为YYYYMMDD

**Q: 程序运行无反应？**
- 查看 `logs/app.log` 日志文件
- 确认 `config.yaml` 和 `data.csv` 文件存在
- 检查Python版本是否为3.10+

## 📝 更多文档

- [需求与设计文档](REQUIREMENTS.md) - 详细的项目技术文档
- [配置文件完整示例](config.example.yaml) - 所有配置选项说明

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个Star支持一下！⭐**

</div>