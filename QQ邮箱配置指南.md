# QQ邮箱SMTP配置指南

## 为什么需要配置QQ邮箱？

Gmail在国内无法直接访问，因此建议配置QQ邮箱作为备用邮件服务器。系统会自动尝试主服务器，失败时自动切换到QQ邮箱。

## QQ邮箱授权码获取步骤

### 1. 开启SMTP服务

1. 登录QQ邮箱网页版：https://mail.qq.com
2. 点击上方的 **"设置"**
3. 选择 **"账户"**
4. 找到 **"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"** 部分
5. 点击 **"开启SMTP服务"**

### 2. 生成授权码

1. 在开启SMTP服务时，系统会要求验证身份（通常通过手机短信验证）
2. 验证成功后，系统会显示一个 **16位的授权码**（例如：`vrmyeigftiykqwqr`）
3. **重要**：请妥善保存这个授权码，它只会显示一次！

### 3. 配置到系统

打开 `config.yaml`，找到 `backup_servers` 部分，填写QQ邮箱信息：

```yaml
email:
  primary_server:
    name: Gmail
    smtp_server: smtp.gmail.com
    smtp_port: 587
    smtp_user: zhengqiao1208@gmail.com
    smtp_password: vrmyeigftiykqwqr
    sender_name: 证件管理系统
    use_ssl: false
    use_tls: true

  backup_servers:
    - name: QQ邮箱
      smtp_server: smtp.qq.com
      smtp_port: 587
      smtp_user: 970937197@qq.com        # 填写你的QQ邮箱
      smtp_password: your_qq_auth_code    # 填写上面获取的16位授权码
      sender_name: 证件管理系统
      use_ssl: false
      use_tls: true

  receiver_email: lei.xu@cdal.com.cn, wangzhenlong@comac.cc, 970937197@qq.com
  max_retry_attempts: 3
```

**关键配置说明：**
- `smtp_user`: 你的QQ邮箱地址
- `smtp_password`: **不是QQ密码**，是上面获取的16位授权码
- `smtp_port`: 587（使用TLS加密）或 465（使用SSL加密）

### 4. 验证配置

运行测试命令验证邮件配置：

```bash
# Windows (虚拟环境)
.\venv\Scripts\python.exe -m licence_management --test-email

# Linux/Mac
python3 -m licence_management --test-email
```

## 常见问题

### Q1: 授权码忘记了怎么办？
**A:** 需要重新生成。登录QQ邮箱 -> 设置 -> 账户 -> 点击"生成授权码"（之前生成的授权码不会显示，需要重新生成）

### Q2: 为什么不直接使用QQ密码？
**A:** QQ邮箱为了安全，要求使用授权码而非登录密码来通过SMTP发送邮件

### Q3: Gmail还能用吗？
**A:** 在国内环境无法直接访问。系统配置了自动切换机制，Gmail失败时会自动尝试QQ邮箱

### Q4: 可以只使用QQ邮箱吗？
**A:** 可以。在 `config.yaml` 中将QQ邮箱配置为 `primary_server`，删除或留空 `backup_servers`

### Q5: 其他邮箱怎么配置？
**A:** 参考以下常用邮箱配置：

#### 163邮箱
- SMTP服务器: `smtp.163.com`
- 端口: 465 (SSL) 或 994 (TLS)
- 需要开启SMTP服务并获取授权码

#### 126邮箱
- SMTP服务器: `smtp.126.com`
- 端口: 465 (SSL) 或 994 (TLS)
- 需要开启SMTP服务并获取授权码

#### 企业邮箱
- 根据邮件服务商提供的信息配置
- 通常使用标准的SMTP端口：25 (无加密), 587 (TLS), 465 (SSL)

## 系统自动切换机制

系统会按照以下顺序尝试发送邮件：

1. 首先尝试主服务器（Gmail）
2. 如果主服务器失败，自动切换到备用服务器1（QQ邮箱）
3. 如果备用服务器1也失败，继续尝试其他备用服务器
4. 所有服务器都失败时，记录详细的错误日志和解决建议

## 测试邮件功能

配置完成后，建议先发送测试邮件：

```bash
python -m licence_management --test-email
```

检查日志文件 `logs/licence_management_*.log` 可以看到：
- 服务器切换过程
- 详细的错误信息
- 针对性的解决建议

## 相关链接

- QQ邮箱帮助中心：https://service.mail.qq.com/
- SMTP配置文档：https://service.mail.qq.com/cgi-bin/help?subtype=1&id=28&no=1001256
