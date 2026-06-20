# BYR-IP-Manager 风险分析

## 选定项目

- 项目名称：BYR-IP-Manager
- 项目路径：`成员代码/朱瑜杰-BYR-IP-Manager`
- 本次改进主题：设备绑定与设备管理接口安全加固
- 涉及接口：`/bind`、`/verify`、`/devices`、`/devices/<device_id>`、`/devices/<device_id>/login`、`/devices/<device_id>/logout`、飞书 OAuth 登录/登出接口

## 选择该模块的原因

该模块涉及飞书 OAuth 登录、设备 IP 绑定、设备登录/登出状态修改和 JWT token 验证，属于明确包含身份认证、权限判断、输入处理和数据存取的业务模块，符合期末作业“对现有模块进行实质性安全修改”的要求。

## 当前逻辑观察

整改前，多个已登录接口仍从请求体或查询参数读取 `open_id`，再用该 `open_id` 查询用户和设备。例如：

1. `/bind` 从 JSON body 读取 `open_id` 后为该用户生成绑定 token。
2. `/devices` 从 GET 请求体读取 `open_id` 后返回设备列表。
3. `/devices/<device_id>` 从请求体读取 `open_id` 后删除设备。
4. `/devices/<device_id>/login` 从 query string 读取 `open_id` 后触发设备登录流程。

这些接口已经使用 `login_required`，但没有把“当前登录用户”作为唯一授权主体。

## 敏感操作

| 操作 | 涉及数据 | 风险说明 |
| --- | --- | --- |
| 设备绑定 | `BindInfo.user`、`BindInfo.ip`、JWT token | 绑定关系决定后续设备管理权限 |
| 设备解绑 | `BindInfo` 删除 | 越权删除会影响他人设备使用 |
| 设备登录/登出 | `BindInfo.logged_in` | 会改变校园网设备状态 |
| 飞书 OAuth 回调 | 用户登录态、OAuth token | 处理不当可能泄露 token 或产生状态重放 |
| 外部命令调用 | `username`、`ip` | 拼接 shell 命令可能引入命令注入 |

## 主要安全风险

### 风险一：伪造 open_id 越权管理他人设备

接口虽然要求登录，但仍信任客户端传入的 `open_id`。攻击者登录自己的账号后，可以把请求体或 query string 中的 `open_id` 改成其他用户，从而尝试查看、绑定、解绑或登录他人的设备。

可能影响：

- 查看他人设备 IP 和登录状态。
- 删除他人的设备绑定。
- 用他人的绑定 token 完成设备验证。
- 触发他人设备登录流程。

### 风险二：状态变更接口豁免 CSRF

多个登录态接口使用 `@csrf_exempt`。当接口依赖 Cookie/Session 识别用户时，状态变更请求缺少 CSRF 保护会增加跨站请求伪造风险。

可能影响：

- 用户登录状态下访问恶意页面，被动触发绑定、解绑或登出请求。
- 攻击链可与 open_id 越权风险叠加。

### 风险三：命令注入与外部调用不可控

`utils/yxms.py` 使用字符串拼接构造 shell 管道，并以 `shell=True` 调用。`username` 和 `ip` 来自业务数据，一旦数据源被污染，可能影响命令执行边界。

可能影响：

- 注入额外 shell 命令。
- 依赖 `jo`、`curl`、`jq` 等外部程序，错误处理不可控。

### 风险四：敏感配置和错误响应不安全

`SECRET_KEY` 硬编码，`DEBUG=True` 默认开启，异常信息直接返回给客户端。生产环境下容易泄露内部错误、配置细节或 token 相关状态。

可能影响：

- 密钥被提交到仓库后难以轮换。
- 调试错误页面或异常文本暴露内部路径与实现细节。

## 本次整改目标

1. 已登录接口统一使用 `request.user` 作为授权主体，不再信任客户端传入的 `open_id`。
2. `/verify` 校验 token 中的 `open_id` 必须等于当前登录用户。
3. 移除状态变更接口的 `csrf_exempt`，恢复 Django CSRF 中间件保护。
4. 使用标准 `json.loads` 解析请求体，拒绝非法 JSON 和非对象 JSON。
5. 把 `shell=True` 管道调用替换为 `requests.post(..., json=...)`。
6. `SECRET_KEY`、`JWT_KEY`、`DEBUG`、`ALLOWED_HOSTS` 改为环境变量配置。
7. 异常写入日志，生产模式下返回通用错误信息。
8. 数据库增加同一用户下 `device_id` 和 `ip` 的唯一约束。

## 不在本次范围内的事项

1. 不重构完整前端交互。
2. 不替换飞书 OAuth 提供方。
3. 不设计新的角色体系。
4. 不修改外部校园网网关服务协议。
5. 不处理仓库中其他成员项目的安全问题。
