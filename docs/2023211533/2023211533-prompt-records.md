# AI交互 Prompt 记录

> 作者：李秉卓（2023211533）
> AI工具：Claude (via opencode CLI)
> 项目：漏洞靶场 XSS 平台安全加固

---

## 对话说明

以下为完成本作业所使用的全部关键Prompt。每个Prompt在AI工具中独立发起，
每次新对话开始时均粘贴了 `constraint-doc.md` 的安全约束内容。

---

### Prompt 1：创建安全基础库

**目的**：生成 `includes/security.php`，包含安全函数库。

```
【背景】你是一个PHP安全专家。请为以下项目创建安全函数库。

当前项目是一个XSS挑战教学平台，在 /漏洞靶场/ 目录下有20个关卡（level1.php ~ level20.php）。
每个关卡通过 $_GET 接收用户输入并输出到HTML页面，部分关卡缺少安全防护。

【约束条件（完整粘贴constraint-doc.md内容）】

请生成 /漏洞靶场/includes/security.php 文件，包含：

1. 函数 set_security_headers()
   - 设置 X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP 安全头
   - CSP策略：default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'

2. 函数 safe_output($data)
   - 封装 htmlspecialchars($data, ENT_QUOTES, 'UTF-8')
   - 如果输入是数组，递归处理每个元素

3. 函数 log_xss_attempt($level, $payload)
   - 将检测到的XSS payload尝试记录到 ../logs/xss_attempts.log
   - 格式：[时间戳] Level N | IP: xxx | Payload: xxx（截断至200字符）

4. 函数 detect_xss_payload($input)
   - 检测输入是否包含常见XSS模式（<script>, onerror=, javascript: 等）
   - 返回 bool

5. 常量定义：
   - MAX_INPUT_LENGTH = 5000
   - SESSION_TIMEOUT = 3600

【禁止行为】
- 不要使用 eval()、system()、exec()
- 不要硬编码任何密码或密钥
- 日志文件不能包含可执行PHP代码

请只输出PHP代码，不要输出解释。
```

**AI输出**：见 `漏洞靶场/includes/security.php`

---

### Prompt 2：为所有关卡添加安全头引入

**目的**：批量修改每个 level*.php，在文件头添加安全头函数调用。

```
【背景+约束文档完整粘贴】

当前 /漏洞靶场/ 目录下有20个 level*.php 文件。每个文件在 <?php 标记后缺少安全头设置。
我需要你为每个文件执行以下操作：

对 level1.php ~ level20.php（以及 index.php）：

1. 在 <?php 或 <?php ini_set(...) 之后第一行添加：
<?php
require_once __DIR__ . '/includes/security.php';
set_security_headers();

2. 确保每个文件都包含 ini_set("display_errors", 0)（如果缺失则添加）

3. 检查是否有 GET/POST/COOKIE 参数直接拼接到HTML输出的情况，
   在漏洞点添加注释：// SECURITY: [VULNERABILITY-DEMO] 此输出点存在反射型XSS漏洞，为教学目的保留

【注意事项】
- 不要修改关卡的XSS漏洞逻辑本身（这是教学平台，需要保留挑战性）
- 只添加安全头、错误配置、注释
- 输出完整修改后的文件内容
```

**AI输出**：修改后的 level1.php ~ level20.php 内容

---

### Prompt 3：创建安全加固版关卡（hardened版本）

**目的**：创建修复了XSS漏洞的关卡版本，放在 `hardened/` 目录。

```
【背景+约束文档完整粘贴】

请为以下关卡生成安全加固版本。加固版放在 /漏洞靶场/hardened/ 目录下，
原关卡保持不变。每关的加固方式如下：

【level1加固版】
- 原始漏洞：$_GET["name"] 无过滤直接输出到 <h2>
- 加固方式：使用 htmlspecialchars($name, ENT_QUOTES, 'UTF-8') 转义输出
- 代码注释标注原漏洞及修复方式

【level2加固版】
- 原始漏洞：$_GET["keyword"] 未经转义直接写入 <input value="...">（双引号属性注入）
- 加固方式：input value 中使用 htmlspecialchars($keyword, ENT_QUOTES, 'UTF-8')
- 同时修复 form action 也应使用 htmlspecialchars

【level4加固版】
- 原始漏洞：str_replace(">","")和str_replace("<","")作为XSS过滤 — 可通过事件属性绕过
- 加固方式：不使用str_replace过滤，改用htmlspecialchars转义输出
- 添加注释说明为什么str_replace不可靠

【level7加固版】
- 原始漏洞：str_replace的字符串删除策略导致双写绕过（scrscriptipt -> script）
- 加固方式：改用htmlspecialchars，添加注释说明删除式过滤的绕过风险

【level8加固版】
- 原始漏洞：<a href="...">中允许javascript:伪协议
- 加固方式：校验href值，白名单只允许http://和https://开头的URL，禁止javascript:和data:

【level10加固版】
- 原始漏洞：t_sort参数仅过滤<>后写入hidden input
- 加固方式：对所有表单隐藏域使用htmlspecialchars

【level11加固版】
- 原始漏洞：HTTP_REFERER头注入到隐藏域
- 加固方式：使用htmlspecialchars处理HTTP_REFERER

【level12加固版】
- 原始漏洞：HTTP_USER_AGENT头注入到隐藏域
- 加固方式：使用htmlspecialchars处理User-Agent

输出每个hardened版本的完整代码。
```

**AI输出**：`hardened/level1_fixed.php` ~ `hardened/level20_fixed.php`

---

### Prompt 4：安全注释和文档补充

**目的**：为每个关卡文件添加说明性的安全注释。

```
【背景+约束文档完整粘贴】

请分析当前 /漏洞靶场/ 中的每个 level*.php 文件，在文件顶部添加注释块：

```
/**
 * Level N — [关卡名称]
 * 漏洞类型：反射型XSS / 属性注入XSS / HTTP头注入XSS / Flash注入 / AngularJS模板注入
 * 攻击向量：[简述如何触发]
 * 绕过方式：[简述过滤绕过方法]
 * 防御措施：[简述正确修复方式]
 * @see hardened/levelN_fixed.php — 安全加固版本
 */
```

请为 level1.php ~ level20.php 分别生成对应的顶部注释块。
根据每个文件的过滤逻辑判断漏洞类型。

输出格式：每个文件对应的注释块。
```

**AI输出**：各关卡的顶部注释

---

### Prompt 5：生成安全审查清单

**目的**：基于OWASP Top 10和本项目实际情况，生成安全检查清单并填写。

```
【背景+约束文档完整粘贴】

请基于以下标准生成 XSS 教学平台的安全审查清单：

检查维度（来自OWASP Top 10和通用安全最佳实践）：

1. 输入验证（A03:2021-Injection）
2. 输出编码（A03:2021-Injection）
3. HTTP安全头配置（A05:2021-Security Misconfiguration）
4. 错误处理（A05:2021-Security Misconfiguration）
5. Flash/ActiveX安全（A06:2021-Vulnerable Components）
6. 敏感信息泄露（A01:2021-Broken Access Control）
7. CSP策略完整性
8. Cookie安全属性

对照当前漏洞靶场代码，为每个检查项填写：
- 检查项名称
- 当前状态（通过/未通过/部分通过）
- 发现的具体问题
- 建议修复方案

输出格式为Markdown表格。
```

**AI输出**：安全审查清单（填入 security-checklist.md）

---

### Prompt 6：整改报告

**目的**：汇总所有发现的问题和修复措施。

```
请根据前面的风险分析和安全审查结果，生成整改报告：

包含以下部分：

1. 发现的问题清单（按严重程度排序）
2. 每项问题的修复措施
3. 修复前后对比（关键关卡）
4. 未修复项说明（哪些漏洞因教学目的保留）
5. 验证方法（如何确认修复有效）
6. 残余风险评估

输出格式为Markdown。
```

**AI输出**：更新后的 fix-report.md
