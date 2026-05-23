
# 安全审查清单：注册与登录模块

**审查人**：[你的姓名]  
**审查日期**：2026-05-23  
**审查范围**：`/register` + `/login` 接口 + 全局安全配置

---

## 第一层检查：对照Prompt约束

| 检查项 | Prompt要求 | 代码实现位置 | 是否落实 | 备注 |
|--------|-----------|-------------|---------|------|
| ORM参数化查询 | ✅ 禁止字符串拼接 | `User.query.filter_by()` | ✅ | SQLAlchemy自动预编译 |
| 密码哈希算法 | ✅ pbkdf2:sha256 + salt≥16 | `generate_password_hash(..., salt_length=16)` | ✅ | 符合约束 |
| 恒定时间比对 | ✅ check_password_hash | `if not check_password_hash(...)` | ✅ | 内部使用 `hmac.compare_digest` |
| 错误响应脱敏 | ✅ 统一"注册失败"/"登录失败" | `register_failed()` / `auth_failed()` | ✅ | 不暴露字段状态 |
| 速率限制 | ✅ 注册5/min, 登录10/min | `@limiter.limit(...)` | ✅ | 装饰器+429处理器 |
| 输入正则校验 | ✅ 用户名/邮箱/密码三重校验 | `USERNAME_PATTERN` 等 | ✅ | `fullmatch` 严格匹配 |
| Token生成安全 | ✅ secrets.token_hex | `token = secrets.token_hex(32)` | ✅ | 加密安全随机源 |
| 安全响应头 | ✅ X-Frame-Options等 | `@app.after_request` | ✅ | 全局注入 |
| 生产配置 | ✅ debug=False | `app.run(debug=False)` | ✅ | 关闭交互式调试 |

---

## 第二层检查：人工业务逻辑审查

| 检查项 | 审查要点 | 审查结果 | 状态 |
|--------|---------|---------|------|
| 认证授权分层 | 注册/登录是否独立接口，权限是否最小化 | ✅ 接口职责单一，无越权 | ✅ |
| 最小权限原则 | 数据库连接是否仅必要权限 | ✅ SQLite文件级权限，无提权风险 | ✅ |
| 错误处理完整性 | 是否覆盖 `IntegrityError` / 通用 `Exception` | ✅ 双重 `try-except` + rollback | ✅ |
| 敏感信息流转 | 密码是否仅在哈希/比对时短暂内存存在 | ✅ 无日志打印/响应返回明文 | ✅ |
| 限流绕过风险 | 是否考虑 `X-Forwarded-For` 代理IP | ⚠️ 本次使用 `get_remote_address`，生产建议增强 | ⚠️ 已记录待办 |

---

## 审查结论
- ✅ 所有强制约束均在代码逻辑中落实（非仅注释）
- ✅ 人工审查未发现高危/中危业务逻辑漏洞
- ⚠️ 限流基于直连IP，若部署在代理后需调整 `key_func`（本次作业范围外）

**审查通过**：✅ 可合并至主分支