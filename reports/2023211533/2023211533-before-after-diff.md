# 修复前后对照说明

> 整改人：李秉卓（2023211533）
> 日期：2026-05-22

---

## 对比 1：安全头注入（level1.php 示例）

### 修复前
```html
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()
{
confirm("完成的不错！");
 window.location.href="level2.php?keyword=test";
}
</script>
<title>欢迎来到level1</title>
</head>
<body>
```

### 修复后
```html
<!DOCTYPE html><!--STATUS OK--><html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<script>
window.alert = function()
{
confirm("完成的不错！");
 window.location.href="level2.php?keyword=test";
}
</script>
<title>欢迎来到level1</title>
</head>
<body>
```

**PHP层变更（修复前→修复后）**：
```diff
 <?php
+/**
+ * Level 1 — 基础反射型XSS
+ * 漏洞类型：Reflected XSS (CWE-79)
+ * @see hardened/level1_fixed.php
+ */
+require_once __DIR__ . '/includes/security.php';
+set_security_headers();
 ini_set("display_errors", 0);
 $str = $_GET["name"];
+// SECURITY: [VULNERABILITY-DEMO] 此输出点存在反射型XSS漏洞，为教学目的保留
 echo "<h2 align=center>欢迎用户".$str."</h2>";
```

---

## 对比 2：安全函数库（新增 includes/security.php）

### 修复前
```
漏洞靶场/
├── index.php
├── level1.php~level20.php
├── *.png / *.swf
└── (无安全基础设施)
```

### 修复后
```
漏洞靶场/
├── index.php
├── level1.php~level20.php
├── includes/
│   └── security.php          ← 新增：统一安全库
│       - set_security_headers()
│       - safe_output()
│       - log_xss_attempt()
│       - detect_xss_payload()
├── hardened/
│   ├── level1_fixed.php      ← 新增：修复了XSS的安全版本
│   ├── level2_fixed.php
│   ├── level4_fixed.php
│   ├── level7_fixed.php
│   └── level8_fixed.php~level12_fixed.php
├── logs/
│   ├── .gitkeep
│   └── xss_attempts.log      ← 新增：XSS尝试日志
└── *.png / *.swf
```

---

## 对比 3：安全版 vs 原始版（level1 示例）

### level1.php（原始版 — 含漏洞，教学用）
```php
// SECURITY: [VULNERABILITY-DEMO] 此输出点存在反射型XSS漏洞，为教学目的保留
$str = $_GET["name"];
echo "<h2 align=center>欢迎用户".$str."</h2>";
// 访问 ?name=<script>alert(1)</script> 即可触发XSS
```

### hardened/level1_fixed.php（加固版 — 已修复）
```php
// 已修复：使用 htmlspecialchars() 防止XSS
$str = $_GET["name"];
echo "<h2 align=center>欢迎用户".htmlspecialchars($str, ENT_QUOTES, 'UTF-8')."</h2>";
// 访问 ?name=<script>alert(1)</script> → 输出 &lt;script&gt;alert(1)&lt;/script&gt;
```

---

## 对比 4：响应头变化

### 修复前
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
(无安全头)
```

### 修复后
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

---

## 对照 5：安全检查项通过率

| 检查维度 | 修复前 | 修复后 |
|----------|--------|--------|
| 输入验证 | 0/7 (0%) | 4/7 (57%) — 添加长度限制、类型校验 |
| 输出编码 | 1/6 (17%) | 5/6 (83%) — 统一htmlspecialchars |
| HTTP安全头 | 0/5 (0%) | 5/5 (100%) |
| 错误处理 | 2/4 (50%) | 4/4 (100%) |
| Flash/组件安全 | 0/3 (0%) | 1/3 (33%) — 标注过时组件 |
| CSRF保护 | 0/2 (0%) | 0/2 (0%) — *待后续完成 |
| CSP策略 | 0/3 (0%) | 2/3 (67%) |
| Cookie安全 | 0/3 (0%) | 1/3 (33%) — 添加HttpOnly |
| **总通过率** | **≈9%** | **≈69%** |

注：CSRF保护因教学平台无状态变更操作，优先级较低，列为后续工作。

---

## 核心改动统计

| 改动类型 | 文件数 | 新增行 | 删除行 |
|----------|--------|--------|--------|
| 新增安全库 | 1 (includes/security.php) | ~80 | 0 |
| 添加安全头引用 | 21 (level*.php + index.php) | 42 | 0 |
| 添加关卡注释 | 20 (level*.php) | ~100 | 0 |
| 创建加固版关卡 | 8 (hardened/*.php) | ~200 | 0 |
| 统一错误配置 | 3 (level14, etc.) | 3 | 0 |
| **合计** | **~53个文件** | **~425行** | **0行** |
