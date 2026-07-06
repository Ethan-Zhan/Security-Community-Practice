# 关键变更摘要
- if not user: return {"message": "用户不存在"}, 401
- if not check_password_hash(...): return {"message": "密码错误"}, 401
+ if not user or not check_password_hash(...): return auth_failed()  # 统一401

- if len(password) < 8: return auth_failed()
+ if not PASSWORD_PATTERN.fullmatch(password): return auth_failed()  # 强化校验

+ @app.after_request  # 新增全局安全头注入
+ def add_security_headers(response): ...
# 整改前后代码对比

**文件**：`app.py`  
**对比时间**：2026-05-23

---

## 关键变更 1：统一错误响应（防枚举）

### 整改前
```python
if not user:
    return jsonify({"message": "用户不存在"}), 401
if not check_password_hash(user.password_hash, password):
    return jsonify({"message": "密码错误"}), 401
```
### 整改后
```python
def auth_failed():
    return jsonify({"success": False, "message": "登录失败"}), 401

# 在login接口中：
if not user or not check_password_hash(user.password_hash, password):
    return auth_failed()
```
### 安全收益
#### ✅ 攻击者无法通过响应差异枚举有效邮箱
#### ✅ 符合最小信息泄露原则


## 关键变更 2：强化密码校验

### 整改前
```python
if len(password) < 8:
    return auth_failed()
```
### 整改后
```python
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

if not PASSWORD_PATTERN.fullmatch(password):
    return auth_failed()
```
### 安全收益
#### ✅ 强制密码复杂度，降低撞库成功率
#### ✅ 与注册模块策略一致，形成统一规范


## 关键变更 3：全局安全响应头

### 新增代码
```python
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Server"] = ""
    return response
```
### 安全收益
#### ✅ 防MIME类型混淆攻击
#### ✅ 防点击劫持（X-Frame-Options）
#### ✅ 减少Referer信息泄露
#### ✅ 隐藏服务器版本，缩小攻击面
