# 人员证件有效期管控系统 - 需求与设计文档
## Requirements & Design Document

> **文档目标**: 为AI助手提供完整的项目理解上下文，包含业务需求、系统设计和技术实现细节。

## 📋 项目概览

### 核心问题
企业和个人需要管理大量人员的各类证件（身份证、护照、驾驶证、健康证、工作许可证等），证件过期会带来合规风险和业务中断。传统的人工管理方式容易遗漏，缺乏系统性的提醒和状态跟踪机制。

### 解决方案
开发一个基于Python的自动化证件有效期管理系统，通过CSV批量导入、智能邮件提醒和状态报告，实现证件生命周期的全自动化管控。

### 目标用户
- **企业HR部门**: 管理员工证件有效期
- **个人用户**: 管理家庭成员证件
- **合规部门**: 监控证件状态，避免合规风险

## 🎯 核心功能需求

### 1. 数据管理功能
- **批量导入**: 通过CSV文件批量导入人员证件信息
- **数据验证**: 自动验证数据格式的完整性和正确性
- **增量更新**: 支持新增、修改现有人员证件信息

### 2. 智能提醒功能
- **多节点提醒**: 支持在证件到期前的多个时间点发送提醒（如60天、30天、7天、1天前）
- **汇总邮件**: 将当日所有需要提醒的证件汇总成一封HTML格式的邮件，避免邮件轰炸
- **自定义模板**: 支持完全自定义的HTML邮件模板
- **定时执行**: 配合系统定时任务实现每日自动扫描和提醒

### 3. 状态报告功能
- **全局状态报告**: 一键生成包含所有人员证件当前状态的综合CSV报告
- **状态分类**: 自动计算并标注证件状态（有效、即将过期、已过期）
- **剩余天数计算**: 精确计算每个证件的剩余有效天数

### 4. 系统管理功能
- **配置管理**: 通过YAML配置文件管理邮箱、提醒规则等设置
- **日志记录**: 详细记录程序运行状态、邮件发送结果等信息
- **错误处理**: 完善的异常处理和错误恢复机制

## 🏗️ 系统架构设计

### 数据流程图
```
CSV数据文件 → 数据读取与验证 → 日期计算与状态判断 → 提醒规则匹配 → 邮件生成与发送
                     ↓
               状态报告生成 ← 全局数据分析 ← 用户触发报告请求
```

### 核心模块设计

#### 1. 数据处理模块 (Data Processing)
- **功能**: CSV文件读写、数据验证、格式转换
- **核心库**: Pandas
- **关键逻辑**: 
  - 支持UTF-8编码的CSV文件
  - 必填字段验证（姓名、证件类型、到期日期）
  - 日期格式统一处理（YYYYMMDD）

#### 2. 业务逻辑模块 (Business Logic)
- **功能**: 证件状态计算、提醒规则匹配
- **核心算法**:
  ```python
  剩余天数 = (到期日期 - 当前日期).days
  是否需要提醒 = 剩余天数 in 提醒节点列表
  证件状态 = "有效" if 剩余天数 > 阈值 else ("即将过期" if 剩余天数 > 0 else "已过期")
  ```

#### 3. 邮件系统模块 (Email System)
- **功能**: SMTP邮件发送、HTML模板渲染
- **核心库**: SMTPlib, email模块
- **关键特性**:
  - 支持SSL/TLS加密
  - HTML表格格式的邮件内容
  - 多收件人支持
  - 邮件发送状态记录

#### 4. 配置管理模块 (Configuration)
- **功能**: YAML配置文件解析、运行时配置管理
- **核心库**: PyYAML
- **配置分类**: 邮件服务器、提醒规则、报告设置、邮件模板

#### 5. 日志管理模块 (Logging)
- **功能**: 运行日志记录、错误追踪
- **核心库**: Python logging
- **日志级别**: INFO（正常运行）、WARNING（警告）、ERROR（错误）

## 📊 数据模型设计

### CSV输入数据结构
```csv
字段名,数据类型,是否必填,格式说明,示例
person_name,string,必填,人员姓名,张三
document_type,string,必填,证件类型,护照
start_date,string,可选,YYYYMMDD格式,20200101  
expiry_date,string,必填,YYYYMMDD格式,20300101
remarks,string,可选,备注信息,研发部
```

### 内部数据处理结构
```python
class PersonDocument:
    person_name: str        # 姓名
    document_type: str      # 证件类型
    start_date: datetime    # 有效期起始日期
    expiry_date: datetime   # 有效期截止日期  
    remarks: str           # 备注信息
    days_left: int         # 剩余天数（计算得出）
    status: str            # 状态（计算得出）
    needs_reminder: bool   # 是否需要提醒（计算得出）
```

### 状态报告输出结构
```csv
字段名,说明,示例
person_name,姓名,张三
document_type,证件类型,护照
start_date,有效期起,2020-01-01
expiry_date,有效期止,2030-01-01
days_left,剩余天数,2156
status,证件状态,有效
remarks,备注,研发部
```

## ⚙️ 配置文件设计

### YAML配置结构
```yaml
# 邮件服务器配置
email:
  smtp_server: string      # SMTP服务器地址
  smtp_port: int          # SMTP端口
  smtp_user: string       # 邮箱账号
  smtp_password: string   # 邮箱密码/授权码
  sender_name: string     # 发件人显示名称
  receiver_email: string  # 收件人邮箱（逗号分隔多个）

# 提醒规则配置  
reminder:
  days_before_expiry: list[int]  # 提醒节点，如[60, 30, 7, 1]

# 报告配置
report:
  output_filename: string              # 报告文件名
  days_until_expiring_threshold: int   # 即将过期阈值

# 邮件模板配置
mail_template:
  subject: string     # 邮件主题模板
  body_html: string   # HTML邮件正文模板
  table_row_html: string  # 表格行HTML模板
```

### 模板变量设计
- **邮件主题模板变量**:
  - `{count}`: 当日提醒条目数量
  - `{today_date}`: 当前日期

- **邮件正文模板变量**:
  - `{table_rows}`: 动态生成的表格行HTML

- **表格行模板变量**:
  - `{person_name}`: 姓名
  - `{document_type}`: 证件类型
  - `{expiry_date}`: 到期日期
  - `{days_left}`: 剩余天数
  - `{remarks}`: 备注

## 🔄 核心业务流程

### 1. 邮件提醒流程
```
启动程序 → 加载配置文件 → 读取CSV数据 → 数据验证
    ↓
计算每个证件的剩余天数 → 根据提醒规则筛选需要提醒的证件
    ↓
生成HTML邮件内容 → 发送汇总邮件 → 记录发送结果 → 程序结束
```

### 2. 状态报告生成流程
```
启动程序(--report参数) → 加载配置文件 → 读取CSV数据 → 数据验证
    ↓
计算每个证件的剩余天数和状态 → 生成完整状态报告CSV → 保存文件 → 程序结束
```

### 3. 关键算法实现

#### 日期计算算法
```python
def calculate_days_left(expiry_date_str: str) -> int:
    """计算证件剩余有效天数"""
    today = datetime.now().date()
    expiry_date = datetime.strptime(expiry_date_str, '%Y%m%d').date()
    return (expiry_date - today).days
```

#### 提醒规则匹配算法  
```python
def needs_reminder(days_left: int, reminder_days: list) -> bool:
    """判断是否需要发送提醒"""
    return days_left in reminder_days and days_left >= 0
```

#### 状态判断算法
```python
def get_document_status(days_left: int, threshold: int) -> str:
    """获取证件状态"""
    if days_left < 0:
        return "已过期"
    elif days_left <= threshold:
        return "即将过期"  
    else:
        return "有效"
```

## 🛠️ 技术实现要点

### 开发环境要求
- **Python版本**: 3.10+（使用现代Python特性）
- **核心依赖包**:
  - `pandas>=2.0.0`: 高性能数据处理
  - `PyYAML>=6.0`: YAML配置文件解析
  - `python-dateutil>=2.8.0`: 日期时间处理增强

### 代码组织结构
```
licence_management/
├── main.py                 # 主程序入口
├── config/
│   ├── __init__.py
│   └── config_manager.py   # 配置管理模块
├── data/
│   ├── __init__.py  
│   └── csv_processor.py    # CSV数据处理模块
├── business/
│   ├── __init__.py
│   └── reminder_logic.py   # 业务逻辑模块
├── email/
│   ├── __init__.py
│   └── email_sender.py     # 邮件发送模块
├── utils/
│   ├── __init__.py
│   ├── logger.py          # 日志工具
│   └── date_utils.py      # 日期工具
└── templates/
    └── email_template.html # 邮件模板
```

### 异常处理策略
- **配置文件错误**: 提供详细的错误信息和修复建议
- **CSV格式错误**: 指出具体的数据格式问题
- **SMTP连接错误**: 提供网络和认证排查指引  
- **日期格式错误**: 自动尝试多种日期格式解析

### 性能优化考虑
- **批量处理**: 使用Pandas批量处理CSV数据
- **内存管理**: 大文件分块读取，避免内存溢出
- **邮件发送**: 单次连接发送所有邮件，减少SMTP握手开销

## 🔍 测试用例设计

### 单元测试覆盖
1. **日期计算测试**: 各种边界情况的剩余天数计算
2. **状态判断测试**: 不同剩余天数对应的状态判断
3. **提醒规则测试**: 多种提醒节点的匹配逻辑
4. **数据验证测试**: CSV格式校验的各种场景
5. **邮件模板测试**: HTML模板变量替换功能

### 集成测试场景  
1. **完整流程测试**: 从CSV读取到邮件发送的端到端测试
2. **配置文件测试**: 各种配置项的正确性验证
3. **错误处理测试**: 各种异常情况的处理验证

## 📝 扩展功能设计

### 可能的功能扩展点
1. **多语言支持**: 邮件模板和界面的国际化
2. **Web界面**: 提供Web管理界面替代命令行
3. **数据库存储**: 使用数据库替代CSV文件存储
4. **微信/短信通知**: 除邮件外的其他通知方式
5. **批量操作API**: 提供HTTP API接口
6. **证件图片管理**: 支持证件扫描件的存储和管理

### 架构扩展考虑
- 采用插件化架构，方便功能模块的独立开发和测试
- 使用配置驱动的设计，减少硬编码
- 预留接口，方便与其他系统集成

---

**注意**: 本文档应与代码实现保持同步更新，确保AI助手始终能够准确理解项目的最新状态。 