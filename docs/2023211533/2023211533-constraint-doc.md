# 项目安全约束文档

> 适用项目：漏洞靶场 XSS 平台安全加固
> 作者：李秉卓（2023211533）
> 每次与AI开启新对话时，请将此文档完整粘贴给AI

---

## 一、背景说明

当前仓库中的 `漏洞靶场/` 目录是一个 XSS 挑战教学平台，包含20个关卡（level1.php ~ level20.php）。
本项目将对其进行安全加固，在不破坏教学功能的前提下：
- 添加安全响应头（CSP、X-Frame-Options等）
- 统一输入处理框架
- 修复实际可被利用的反射型XSS漏洞
- 为每关添加安全注释

## 二、任务范围

1. 创建 `includes/security.php` 安全函数库
2. 为每个 `level*.php` 添加安全头引入
3. 修复无过滤/弱过滤关卡的XSS漏洞
4. 创建 `hardened/` 目录存放安全版关卡
5. 为每关添加漏洞说明和安全注释

## 三、强制约束条件

### C1 — 输出转义
- 所有用户输入（`$_GET`, `$_POST`, `$_COOKIE`, `$_SERVER`）输出到HTML前必须经过 `htmlspecialchars($data, ENT_QUOTES, 'UTF-8')`
- **例外**：教学关卡中故意保留的漏洞点不需要修复，但必须在代码注释中标注 `[VULNERABILITY-DEMO]`

### C2 — 不使用危险函数
- **禁止使用**：`eval()`, `system()`, `exec()`, `shell_exec()`, `passthru()`, `popen()`, `proc_open()`, `assert()`
- 文件包含必须使用白名单校验，禁止直接使用 `include $_GET['file']`

### C3 — 安全响应头
每个PHP页面必须在输出HTML前设置以下响应头：
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

### C4 — 错误信息不泄露
- 所有页面设置 `ini_set("display_errors", "0")`
- 错误日志写入文件而非输出到页面
- 数据库连接失败不暴露密码或连接信息

### C5 — 输入验证
- 所有用户输入必须验证类型和格式
- 使用白名单验证优于黑名单过滤
- 对限制长度的输入（如关卡输入）设置最大长度 `max_input_length=5000`

### C6 — 会话安全
- Session cookie 设置 `HttpOnly` 和 `Secure` 标志
- 使用 `session_regenerate_id()` 防止会话固定攻击

### C7 — 日志记录
- 检测到XSS payload尝试时记录到日志
- 日志记录包含：时间戳、来源IP、关卡编号、payload摘要
- 日志文件不能包含可执行的PHP代码

## 四、禁止行为

1. 禁止在代码中硬编码密码、密钥、令牌
2. 禁止信任 `$_SERVER['HTTP_REFERER']` 做权限校验
3. 禁止信任客户端传入的角色/权限字段（如 `$_GET['role']`, `$_POST['is_admin']`）
4. 禁止在生产环境注释中保留调试信息
5. 禁止使用 `str_replace` 做XSS过滤（绕过方式太多）
6. 禁止使用不安全的哈希算法（MD5、SHA1）存储密码

## 五、质量要求

1. 所有新增代码使用4空格缩进
2. 函数名称使用 snake_case
3. 类名使用 PascalCase
4. 所有公共函数添加 PHPDoc 注释
5. 安全相关代码必须有 `// SECURITY:` 前缀的注释说明
