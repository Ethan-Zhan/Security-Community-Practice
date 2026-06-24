# AI 交互与 Prompt 过程记录 (prompt-records.md)

本文件记录了在进行自动签到脚本（`main.py`）安全重构时，将《项目安全约束文档》中的安全规则提炼为 Prompt 并与 AI 交互的过程。

---

## 1. 关键 Prompt 输入文本

为了使 AI 生成的代码能够完美过滤敏感 Secrets 并在报错时防止信息泄漏，我们在交互时使用了以下结构化 Prompt：

```text
【背景说明】
我正在为一个运行在 GitHub Actions 环境下的 Python 自动签到脚本进行代码安全加固。
此脚本在执行过程中，会从环境变量（Secrets）中读取敏感凭证（如 ALPHAGEN_COOKIE 和 CREATIVEHUB_AUTH）。

【任务范围】
对 main.py 脚本中所有的控制台打印逻辑（print）和异常捕获逻辑（Exception）进行重构，全面落实“防止日志敏感信息泄露（Log Leakage）”的要求。

【约束条件】
1. 禁止在代码中直接使用 Python 的原生 print() 打印第三方 API 返回的原文（response.text）。
2. 实现一个统一的安全打印模块/包装函数（如 safe_print），在输出到控制台之前，必须自动检测并屏蔽（替换为 [REDACTED_SECRET]）所有环境变量中已配置的敏感密钥。
3. 实现异常安全格式化器（如 safe_format_exception），拦截 requests 网络库等底层报错时可能意外携带请求报头（Header）而暴露 Cookie 的风险，杜绝直接 print(e)。
4. 严禁在代码、注释或配置文件中硬编码任何敏感明文凭证。

请基于这些安全限制，对我的 main.py 代码进行重构。
```

---

## 2. AI 交互过程截图凭证

以下是在本轮重构开发中，将上述安全约束输入 AI、并由 AI 给出加固代码的真实交互截图：

![AI 交互截图凭证](prompt-screenshot.png)

---

## 3. 核心安全过滤防御逻辑说明

经过 AI 协助，我们最终在代码中完美实现了以下两个核心安全防御逻辑：

### ① 统一安全日志打印函数 `safe_print`
* **原理**：将所有原生的 `print` 替换为安全函数拦截。在输出前，动态从运行期环境变量（Secrets）中实时提取密钥字符串，凡是匹配到该密钥的值，一律使用替换算法替换为 `[REDACTED_SECRET]`。

### ② 异常信息模糊净化器 `safe_format_exception`
* **原理**：网络请求异常时（例如 DNS 故障、服务端 500 等），异常堆栈经常会默认携带明文 Request Header 抛出。该净化器在抛出异常前强制过滤掉已知的密钥内容，且只返回清洗后的基础错误类型名（如 `[ConnectionError]`），阻断敏感信息随报错输出。
