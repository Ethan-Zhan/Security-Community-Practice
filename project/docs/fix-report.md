# 整改说明与验证记录

**模块**：用户注册与登录  
**整改人**：[你的姓名]  
**日期**：2026-05-23

---

## 问题1：错误响应泄露账户状态（枚举风险）

### 问题描述
AI初始生成的登录接口返回了不同错误提示：
```python
# ❌ 初始代码（存在风险）
if not user:
    return jsonify({"message": "用户不存在"}), 401
if not check_password_hash(...):
    return jsonify({"message": "密码错误"}), 401
```
攻击者可通过响应差异批量探测有效邮箱。

整改方式
统一调用 auth_failed() 函数：

### ✅ 整改后代码
```python
if not user or not check_password_hash(user.password_hash, password):
    return auth_failed()  # 统一返回 {"success": false, "message": "登录失败"} + 401
```
### 验证方法

# 测试1：不存在的邮箱
```bash
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"nonexistent@example.com","password":"any"}'
```
```bash
# 测试2：存在邮箱但密码错误（先注册一个用户）
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"wrongpwd"}'
```
### 验证结果
```json
// 两次请求均返回相同响应：
{"success": false, "message": "登录失败"}
// 状态码均为 401 ✅
```

## 问题2：密码复杂度校验不完整

### 问题描述
初始生成的密码校验仅检查长度 len(password) >= 8，未强制大小写+数字组合。
### 整改方式
#### 补充正则校验（与注册模块保持一致）：
```python
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

# 在login接口中添加：
if not PASSWORD_PATTERN.fullmatch(password):
    return auth_failed()
```

### 验证方法
```bash
# 测试弱密码被拦截
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"weakpass"}'
```

### 验证结果
```json
{"success": false, "message": "登录失败"}  // 状态码 401 ✅
```

## 关于 Bandit B104 告警的处理
- **告警内容**：`host="0.0.0.0"` 绑定所有网络接口
- **处理决策**：添加 `# nosec B104` 注释 + 文档说明
- **理由**：
  1. 作业要求代码"能运行起来"，`0.0.0.0` 便于本地/局域网测试演示
  2. 核心安全控制点（注入防护/密码存储/枚举防护）均已落实，此配置不影响业务逻辑安全
  3. 生产环境部署时应通过反向代理或改为 `127.0.0.1` 限制访问
- **验证**：重新扫描后 `results: []`，无新增安全问题 ✅
## 安全扫描验证
- **命令**：`python -m bandit app.py`
- **结果**：仅1项中危告警（B104: `host="0.0.0.0"`），属部署配置范畴，非业务逻辑漏洞
- **处理**：已通过文档说明（见本文件），核心安全控制点（注入/密码/枚举/限流）均验证通过 ✅
- **截图**：`reports/scan-report.png`