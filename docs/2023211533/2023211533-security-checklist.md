# 安全审查清单 — 漏洞靶场 XSS 平台

> 审查人：李秉卓（2023211533）
> 审查日期：2026-05-22
> 参考标准：OWASP Top 10:2021

---

## 检查维度 1：输入验证（A03:2021-Injection）

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 1.1 | GET参数长度限制 | ❌ 未通过 | 所有关卡无输入长度限制，可发送超长payload | 添加 `MAX_INPUT_LENGTH=5000` 常量并校验 |
| 1.2 | GET参数类型校验 | ❌ 未通过 | 未验证输入是否为预期类型（数字应传字符串等） | 添加 `validate_input_type()` 函数 |
| 1.3 | 输入中存在危险字符时拒绝 | ⚠️ 部分 | 部分关卡用str_replace做过滤，但可被绕过 | 改用转义而非删除过滤 |
| 1.4 | 白名单验证（URL/email等） | ❌ 未通过 | level8/level9的href输入无白名单 | 对href值做白名单：只允许http://和https:// |
| 1.5 | Referer头输入验证 | ❌ 未通过 | level11直接取HTTP_REFERER未验证 | 至少做htmlspecialchars处理 |
| 1.6 | User-Agent输入验证 | ❌ 未通过 | level12直接取HTTP_USER_AGENT未验证 | 至少做htmlspecialchars处理 |
| 1.7 | Cookie值输入验证 | ❌ 未通过 | level13直接取$_COOKIE["user"] | 至少做htmlspecialchars处理 |

## 检查维度 2：输出编码（A03:2021-Injection）

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 2.1 | HTML上下文输出编码 | ⚠️ 部分 | level1无编码，level2~13部分位置无编码 | 所有反射点使用htmlspecialchars |
| 2.2 | 属性上下文输出编码 | ⚠️ 部分 | 多处input value使用裸值或仅过滤`<>` | 属性值必须转义 `"` 和 `'` |
| 2.3 | JavaScript上下文输出编码 | ❌ 未通过 | alert重写函数内使用用户输入 | 对window.location.href中的用户输入编码 |
| 2.4 | URL上下文输出编码 | ❌ 未通过 | level8/9 href中直接使用用户输入 | URL白名单+urlencode |
| 2.5 | Flash参数编码 | ⚠️ 部分 | level17-20使用htmlspecialchars但Flash内部可能有二次解析 | 移除Flash依赖或用参数化API |
| 2.6 | ENT_QUOTES标志使用 | ❌ 未通过 | level3 `htmlspecialchars` 未指定ENT_QUOTES，单引号可能未转义 | 统一使用 `htmlspecialchars($data, ENT_QUOTES, 'UTF-8')` |

## 检查维度 3：HTTP安全头配置（A05:2021-Security Misconfiguration）

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 3.1 | Content-Security-Policy | ❌ 未通过 | 全部20关无CSP头 | 添加CSP：default-src 'self'; script-src 'self' 'unsafe-inline' |
| 3.2 | X-Frame-Options | ❌ 未通过 | 全部20关无XFO头，可被iframe嵌入 | 添加 X-Frame-Options: DENY |
| 3.3 | X-Content-Type-Options | ❌ 未通过 | 全部20关无XCTO头 | 添加 X-Content-Type-Options: nosniff |
| 3.4 | X-XSS-Protection | ❌ 未通过 | 全部20关无XXP头 | 添加 X-XSS-Protection: 1; mode=block |
| 3.5 | Referrer-Policy | ❌ 未通过 | 全部关无Referrer-Policy | 添加 Referrer-Policy: strict-origin-when-cross-origin |

## 检查维度 4：错误处理（A05:2021-Security Misconfiguration）

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 4.1 | display_errors关闭 | ⚠️ 部分 | 仅部分关卡关闭，level14等未设置 | 统一在每个文件设置 |
| 4.2 | 错误信息不泄露路径 | ✅ 通过 | PHP默认不输出路径 | — |
| 4.3 | 数据库连接错误不暴露 | ✅ 通过 | 当前无数据库 | — |
| 4.4 | 不暴露技术栈（PHP版本等） | ✅ 通过 | 无 `phpinfo()` 等危险泄露 | — |

## 检查维度 5：Flash/过时组件安全（A06:2021-Vulnerable Components）

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 5.1 | Flash SWF文件存在 | ❌ 未通过 | 4个SWF文件存在（xsf01~04），含ActionScript漏洞 | Flash已停止支持，建议移除或提供迁移方案 |
| 5.2 | AngularJS 1.x使用 | ❌ 未通过 | level15使用AngularJS 1.x（angular.min.js），存在模板注入 | AngularJS 1.x已停止维护，有已知CVE |
| 5.3 | 外部资源引用 | ⚠️ 注意 | level14引用外部iframe（exifviewer.org），依赖第三方 | 评估第三方安全性和可用性 |

## 检查维度 6：CSRF保护（A01:2021-Broken Access Control）

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 6.1 | 状态变更操作有Token | ❌ 未通过 | 无CSRF Token机制 | 添加CSRF Token |
| 6.2 | SameSite Cookie属性 | ❌ 未通过 | level13设置Cookie未指定SameSite | 添加 SameSite=Lax |

## 检查维度 7：CSP策略完整性

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 7.1 | script-src限制 | ❌ 未通过 | 当前无CSP | 添加script-src 'self' 'unsafe-inline' |
| 7.2 | object-src限制（Flash等） | ❌ 未通过 | Flash embed无object-src限制 | 添加 object-src 'none' 或移除Flash |
| 7.3 | base-uri限制 | ❌ 未通过 | 无base-uri限制 | 添加 base-uri 'self' |

## 检查维度 8：Cookie安全属性

| # | 检查项 | 状态 | 问题描述 | 修复建议 |
|---|--------|------|----------|----------|
| 8.1 | HttpOnly标志 | ❌ 未通过 | level13 setcookie未设HttpOnly | 添加 `httponly=true` 参数 |
| 8.2 | Secure标志 | ❌ 未通过 | 未设Secure标志 | 添加 `secure=true`（HTTPS环境） |
| 8.3 | SameSite属性 | ❌ 未通过 | 未设SameSite | 添加 `samesite=Lax` |

---

## 统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 通过 | 2 | 7.1% |
| ⚠️ 部分通过 | 4 | 14.3% |
| ❌ 未通过 | 22 | 78.6% |
| **总计** | **28** | **100%** |
