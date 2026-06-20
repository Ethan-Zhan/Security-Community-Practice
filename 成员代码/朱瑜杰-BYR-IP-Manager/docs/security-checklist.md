# 安全审查清单

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 是否有实质性安全改动 | 通过 | 修改认证授权、CSRF、错误响应、外部调用和安全配置 |
| 是否只依赖注释声明安全 | 通过 | 授权主体改为 `request.user`，并新增测试 |
| 是否继续信任客户端 `open_id` | 通过 | 设备和绑定接口不再使用客户端 `open_id` 决定用户 |
| token 是否绑定当前登录用户 | 通过 | `/verify` 校验 token `open_id` 与 `request.user.open_id` |
| 状态变更接口是否绕过 CSRF | 通过 | 移除目标视图中的 `csrf_exempt` |
| JSON 输入是否安全解析 | 通过 | 新增 `parse_json_body()`，非法 JSON 返回 400 |
| 是否存在 shell 命令注入面 | 通过 | 移除 `shell=True`，改用 `requests.post` |
| 是否有数据库唯一约束 | 通过 | 增加 `user+device_id` 与 `user+ip` 唯一约束迁移 |
| 是否有硬编码生产密钥 | 通过 | `SECRET_KEY`、`JWT_KEY` 改为环境变量读取 |
| DEBUG 是否默认关闭 | 通过 | `DJANGO_DEBUG` 默认 `False` |
| 错误响应是否泄露异常 | 通过 | 生产模式返回通用错误，详细异常写日志 |
| OAuth token 是否回显给客户端 | 通过 | 回调响应移除 `user_access_token` |
| 是否新增回归测试 | 通过 | 新增绑定 token、token 越权、设备列表和解绑越权测试 |
| 是否完成验证 | 部分通过 | 语法编译和静态模式扫描通过；Django 测试因环境缺少 Django/pip 未执行 |

## 人工审查结论

本次改动落实了“认证用户只能管理自己的设备”这一核心安全边界。主要权限判断已从客户端传入身份切换到服务端登录态，越权攻击面明显缩小。

剩余风险：

1. 需要在安装依赖的环境中运行完整 Django 测试和迁移检查。
2. 外部网关 `http://localhost/api/login` 仍是明文本地 HTTP，若部署拓扑变化，需要重新评估传输安全。
3. 前端或调用方需要适配不再提交 `open_id` 的接口约定，以及 CSRF token 要求。
