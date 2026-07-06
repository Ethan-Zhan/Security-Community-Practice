# 漏洞靶场 XSS 风险分析报告

> 作者：李秉卓（2023211533）
> 日期：2026-05-22
> 分析范围：漏洞靶场/ level1.php ~ level20.php

---

## 一、总体风险概述

| 指标 | 数值 |
|------|------|
| 总关卡数 | 20 |
| 存在XSS漏洞的关卡 | 19/20 |
| 高风险（无过滤/弱过滤） | 12关 |
| 中风险（部分过滤可绕过） | 7关 |
| 低风险（已有防护） | 1关（level3部分防护） |
| 涉及用户输入端 | `$_GET["name"]`, `$_GET["keyword"]`, `$_GET["t_sort"]`, `$_GET["arg01"]`, `$_GET["arg02"]`, `$_GET["src"]`, `$_SERVER['HTTP_REFERER']`, `$_SERVER['HTTP_USER_AGENT']`, `$_COOKIE["user"]` |
| 额外风险 | Flash SWF文件存在ActionScript注入、AngularJS模板注入、Cookie注入、HTTP头注入 |

---

## 二、逐关风险分析

### Level 1
- **文件**：`level1.php`
- **用户输入**：`$_GET["name"]`
- **输出位置**：`<h2 align=center>欢迎用户".$str."</h2>"`
- **过滤措施**：无
- **XSS类型**：反射型 XSS
- **攻击Payload**：`<script>alert(1)</script>`
- **风险等级**：**严重**

### Level 2
- **文件**：`level2.php`
- **用户输入**：`$_GET["keyword"]`
- **输出位置1**：`<h2>` 标签内 — `htmlspecialchars($str)` ✅ 已防护
- **输出位置2**：`<input name=keyword value="'.$str.'">` — 无过滤，且双引号包裹
- **过滤措施**：仅在h2中使用了htmlspecialchars，input value中未转义
- **XSS类型**：HTML 属性注入 XSS
- **攻击Payload**：`" onmouseover="alert(1)` 或 `"><script>alert(1)</script>`
- **风险等级**：**严重**

### Level 3
- **文件**：`level3.php`
- **用户输入**：`$_GET["keyword"]`
- **输出位置1**：`<h2>` 中 `htmlspecialchars($str)` ✅
- **输出位置2**：`<input name=keyword value='".htmlspecialchars($str)."'>` — 单引号包裹
- **过滤措施**：两处都用htmlspecialchars（但未指定ENT_QUOTES，单引号默认不转义）
- **XSS类型**：单引号属性注入 XSS（需php.ini配置配合绕过）
- **攻击Payload**：`' onclick='alert(1)`（利用单引号未转义）
- **风险等级**：**中（取决于PHP版本/htmlspecialchars配置）**

### Level 4
- **文件**：`level4.php`
- **用户输入**：`$_GET["keyword"]`
- **输出位置**：`<input name=keyword value="'.$str3.'">`
- **过滤措施**：`str_replace(">","",$str); str_replace("<","",$str2)` — 仅删除 `<>`
- **XSS类型**：事件处理器注入 XSS
- **绕过方式**：不使用`<>`，用事件属性 `" onfocus="alert(1)" autofocus="true`
- **风险等级**：**严重**

### Level 5
- **文件**：`level5.php`
- **用户输入**：`$_GET["keyword"]`
- **输出位置**：`<input name=keyword value="'.$str3.'">`
- **过滤措施**：
  - `strtolower()` 转小写
  - `str_replace("<script","<scr_ipt",...)` — 屏蔽`<script`标签
  - `str_replace("on","o_n",...)` — 屏蔽 `on*` 事件
- **绕过方式**：用 `<a href="javascript:alert(1)">click</a>` 或 `<img src=x onerror=...>` 需要绕过on，利用HTML实体/burp等
- **风险等级**：**高**

### Level 6
- **文件**：`level6.php`
- **过滤措施**（level5基础上增加）：
  - `str_replace("src","sr_c",...)`
  - `str_replace("data","da_ta",...)`
  - `str_replace("href","hr_ef",...)`
- **绕过方式**：大小写混用 `<a HrEf="javascript:alert(1)">` 或使用HTML实体
- **风险等级**：**高**

### Level 7
- **文件**：`level7.php`
- **过滤措施**：与level6类似，但使用 `str_replace("...","")` 空字符串替换
- **绕过方式**：双写绕过 `"><scrscriptipt>alert(1)</scrscriptipt>`、`oonnmouseover`
- **风险等级**：**高**

### Level 8
- **文件**：`level8.php`
- **输出位置**：`<a href="'.$str7.'">友情链接</a>` — href属性注入
- **过滤措施**：level7的5种替换 + `str_replace('"','&quot',...)`
- **绕过方式**：JavaScript伪协议 `javascript:alert(1)`（无需引号）
- **XSS类型**：DOM型（href伪协议）
- **风险等级**：**严重**

### Level 9
- **文件**：`level9.php`
- **过滤措施**：与level8相同，但增加了 `if(false===strpos($str7,'http://'))` 校验
- **绕过方式**：大小写 `hTtP://` 虽然会被strpos匹配，但可以在http前插入不合法内容让if失效，或用其他协议
- **XSS类型**：href伪协议 XSS
- **风险等级**：**高**

### Level 10
- **文件**：`level10.php`
- **输入参数**：`$_GET["keyword"]`、`$_GET["t_sort"]`
- **过滤措施**：`keyword`经htmlspecialchars；`t_sort`仅过滤`<>`
- **输出位置**：`<input name="t_sort" value="'.$str33.'" type="hidden">`
- **绕过方式**：`" onmouseover="alert(1)`
- **风险等级**：**高**

### Level 11
- **文件**：`level11.php`
- **输入来源**：`$_SERVER['HTTP_REFERER']`（Referer头注入）
- **过滤措施**：仅过滤`<>`
- **输出位置**：`<input name="t_ref" value="'.$str33.'" type="hidden">`
- **XSS类型**：HTTP Referer头注入 XSS
- **风险等级**：**严重**

### Level 12
- **文件**：`level12.php`
- **输入来源**：`$_SERVER['HTTP_USER_AGENT']`（User-Agent头注入）
- **过滤措施**：仅过滤`<>`
- **输出位置**：`<input name="t_ua" value="'.$str33.'" type="hidden">`
- **XSS类型**：HTTP User-Agent头注入 XSS
- **风险等级**：**严重**

### Level 13
- **文件**：`level13.php`
- **输入来源**：`$_COOKIE["user"]`（Cookie注入）
- **过滤措施**：仅过滤`<>`
- **输出位置**：`<input name="t_cook" value="'.$str33.'" type="hidden">`
- **XSS类型**：Cookie注入 XSS
- **风险等级**：**严重**

### Level 14
- **文件**：`level14.php`
- **漏洞类型**：iframe嵌入 + EXIF XSS
- **描述**：页面内嵌 exifviewer.org iframe，该网站可解析图片EXIF数据。通过上传包含XSS payload的图片EXIF元数据实现攻击
- **XSS类型**：DOM型 / EXIF注入 XSS
- **风险等级**：**中**

### Level 15
- **文件**：`level15.php`
- **输入参数**：`$_GET["src"]`
- **输出位置**：`<span class="ng-include:'.htmlspecialchars($str).'">`
- **过滤措施**：htmlspecialchars（但因AngularJS模板机制，可通过路径包含实现注入）
- **XSS类型**：AngularJS ng-include 模板注入
- **绕过方式**：`level15.php?src=1.gif` 其中1.gif实际为js代码
- **风险等级**：**高**

### Level 16
- **文件**：`level16.php`
- **过滤措施**：`str_replace` 替换 `script`→`&nbsp;`、空格→`&nbsp;`、`/`→`&nbsp;`、制表符→`&nbsp;`
- **绕过方式**：使用 `%0a`、`%0d`、`%0c` 等换行/换页字符替代空格
- **风险等级**：**高**

### Level 17
- **文件**：`level17.php`
- **输入参数**：`$_GET["arg01"]`、`$_GET["arg02"]`
- **输出位置**：`<embed src=index.png?arg01=arg02>`
- **过滤措施**：htmlspecialchars处理
- **XSS类型**：Flash参数注入（src参数可控，可引入外部恶意SWF）
- **风险等级**：**中**

### Level 18
- **文件**：`level18.php`
- **输入参数**：`$_GET["arg01"]`、`$_GET["arg02"]`
- **输出位置**：`<embed src=xsf02.swf?arg01=arg02>`
- **过滤措施**：htmlspecialchars处理
- **XSS类型**：Flash ActionScript注入（xsf02.swf中存在可被利用的ActionScript函数）
- **风险等级**：**高**

### Level 19
- **文件**：`level19.php`
- **输入参数**：`$_GET["arg01"]`、`$_GET["arg02"]`
- **输出位置**：`<embed src="xsf03.swf?arg01=arg02">`
- **过滤措施**：htmlspecialchars处理
- **XSS类型**：Flash ActionScript注入（xsf03.swf中存在可被利用的函数）
- **风险等级**：**高**

### Level 20
- **文件**：`level20.php`
- **输入参数**：`$_GET["arg01"]`、`$_GET["arg02"]`
- **输出位置**：`<embed src="xsf04.swf?arg01=arg02">`
- **过滤措施**：htmlspecialchars处理
- **XSS类型**：Flash ActionScript注入
- **风险等级**：**高**

---

## 三、风险汇总表

| 关卡 | 输入来源 | 过滤方式 | 可绕过 | XSS类型 | 风险等级 |
|------|----------|----------|--------|---------|----------|
| 1 | GET name | 无 | N/A | 反射型 | **严重** |
| 2 | GET keyword | 部分（h2已防护，input未防护） | `"`闭合 | 属性注入 | **严重** |
| 3 | GET keyword | htmlspecialchars(两处) | 单引号可能未转义 | 属性注入 | 中 |
| 4 | GET keyword | 删除`<>` | 事件处理器 | 属性注入 | **严重** |
| 5 | GET keyword | 替换`<script`/`on` | `javascript:`伪协议 | 属性/链接注入 | 高 |
| 6 | GET keyword | +替换`src`/`data`/`href` | 大小写绕过 | 属性注入 | 高 |
| 7 | GET keyword | 空字符串替换(双写绕过) | `scrscriptipt` | 属性注入 | 高 |
| 8 | GET keyword | +替换`"`→`&quot` | `javascript:`无需引号 | href注入 | **严重** |
| 9 | GET keyword | +校验`http://` | JS伪协议 | href注入 | 高 |
| 10 | GET keyword/t_sort | keyword已防护，t_sort仅过滤`<>` | 事件处理器 | 属性注入 | 高 |
| 11 | HTTP_REFERER | 过滤`<>` | 事件处理器 | Referer头注入 | **严重** |
| 12 | HTTP_USER_AGENT | 过滤`<>` | 事件处理器 | UA头注入 | **严重** |
| 13 | COOKIE | 过滤`<>` | 事件处理器 | Cookie注入 | **严重** |
| 14 | 外部iframe | 无 | EXIF注射 | EXIF/DOM XSS | 中 |
| 15 | GET src | htmlspecialchars | AngularJS ng-include | 模板注入 | 高 |
| 16 | GET keyword | 替换所有空格/`/` | `%0a`换行绕过 | 反射型 | 高 |
| 17 | GET arg01/arg02 | htmlspecialchars | Flash参数注入 | Flash XSS | 中 |
| 18 | GET arg01/arg02 | htmlspecialchars | xsf02.swf内部漏洞 | Flash XSS | 高 |
| 19 | GET arg01/arg02 | htmlspecialchars | xsf03.swf内部漏洞 | Flash XSS | 高 |
| 20 | GET arg01/arg02 | htmlspecialchars | xsf04.swf内部漏洞 | Flash XSS | 高 |

---

## 四、系统性风险问题

### 1. 缺少统一安全框架
- 每个关卡独立处理安全逻辑，没有共享的安全头设置、输入验证函数
- 部分关卡（level7, level16）使用替换而非转义作为"过滤"，存在编码绕过风险

### 2. 缺少安全响应头
- 全20关无 Content-Security-Policy
- 全20关无 X-Frame-Options
- 全20关无 X-Content-Type-Options
- 全20关无 X-XSS-Protection

### 3. 不一致的错误处理
- 部分关卡设置 `ini_set("display_errors", 0)`，部分未设置

### 4. Flash SWF 文件安全风险
- `xsf01.swf` ~ `xsf04.swf` 四个Flash文件可能存在ActionScript漏洞
- Flash Player已于2020年停止支持，这些文件属于过时技术风险

### 5. 无CSRF保护
- 关卡间跳转通过 `window.location.href` 实现，无Token验证
- 任何网站可通过iframe发起GET请求到任何关卡
