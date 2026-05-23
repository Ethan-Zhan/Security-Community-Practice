# Flask 用户注册/登录系统

## 项目简介

这是一个基于 Flask 的安全用户认证系统示例项目。

项目包含：

- 用户注册
- 用户登录
- SQLite 数据库
- 前后端交互
- 登录认证
- 接口限流
- 密码哈希
- 基础安全防护

适合作为：

- Flask 登录系统模板
- Web 安全课程实验
- 小型后台项目基础认证模块
- 用户系统开发参考

---

# 项目结构

```text
project/
│
├── app.py
├── requirements.txt
├── users.db
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── app.js
│
└── instance/
```

---

# 环境要求

推荐 Python 版本：

```text
Python 3.10+
```

---

# 安装依赖

```bash
pip install -r requirements.txt
```

---

# 启动项目

```bash
python app.py
```

---

# 访问项目

```text
http://127.0.0.1:5000
```

---

# 数据库说明

项目使用：

```text
SQLite
```

首次启动时会自动创建数据库。

数据库文件：

```text
users.db
```

数据表：

```text
users
```

包含字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 用户ID |
| username | VARCHAR(20) | 用户名 |
| email | VARCHAR(255) | 邮箱 |
| password_hash | VARCHAR(255) | 密码哈希 |

---

# 用户侧使用要求

## 用户名要求

- 长度必须为 6~20 位
- 仅允许：
  - 大小写字母
  - 数字
  - 下划线 `_`

合法示例：

```text
test123
user_name
Admin001
```

非法示例：

```text
ab
用户名123
test-123
admin!
```

---

## 邮箱要求

- 必须符合标准邮箱格式
- 邮箱不可重复注册
- 系统会自动转换为小写存储

合法示例：

```text
test@example.com
admin123@gmail.com
```

非法示例：

```text
test
abc@
@test.com
```

---

## 密码要求

密码必须：

- 至少 8 位
- 包含：
  - 大写字母
  - 小写字母
  - 数字

合法示例：

```text
StrongPass123
Hello2025
```

非法示例：

```text
12345678
password
PASSWORD123
Pass12
```

---

# 接口说明

## 注册接口

```text
POST /register
```

请求格式：

```json
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "StrongPass123"
}
```

---

## 登录接口

```text
POST /login
```

请求格式：

```json
{
  "email": "test@example.com",
  "password": "StrongPass123"
}
```

---

# 已实现安全特性

- 参数化查询
- 密码哈希存储
- 邮箱去重
- 登录认证
- 登录限流
- 注册限流
- 防用户枚举
- 统一错误响应
- 基础安全响应头
- 无敏感日志
- 无动态执行
- 前后端分离接口
- 前端 Token 保存

---

# 后续推荐增强

生产环境建议增加：

- Redis 限流
- JWT
- Refresh Token
- HTTPS
- HttpOnly Cookie
- CSRF 防护
- 邮箱验证码
- MFA 双因素认证
- 登录失败锁定
- 图形验证码
- 审计日志
- Nginx 反向代理
- Gunicorn / uWSGI

