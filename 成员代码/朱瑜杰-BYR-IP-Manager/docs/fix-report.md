# 整改说明与验证记录

## 整改主题

BYR-IP-Manager 设备绑定与设备管理接口安全加固。

## 问题一：已登录接口仍信任客户端 open_id

整改前：

- `/bind`、`/devices`、`/devices/<device_id>`、`/devices/<device_id>/login`、`/devices/<device_id>/logout` 使用请求体或 query string 中的 `open_id` 查询用户。
- 攻击者可以登录自己的账号后伪造他人 `open_id`。

整改后：

- 所有目标接口统一使用 `request.user`。
- `/verify` 额外校验 token `open_id` 与当前登录用户一致。
- 新增测试覆盖伪造 `open_id` 无法查看或解绑他人设备。

应满足条件：

- 用户只能看到、解绑、登录、登出自己的设备。
- 他人 token 不能被当前用户验证成功。

## 问题二：CSRF 豁免与异常直出

整改前：

- 登录态状态变更接口使用 `@csrf_exempt`。
- 多处 `except Exception as e` 直接返回 `str(e)`。

整改后：

- 移除目标视图中的 `csrf_exempt`。
- 新增 `server_error_response()`，生产模式返回通用错误，详细异常写日志。

应满足条件：

- Session/Cookie 认证接口恢复 Django CSRF 中间件保护。
- 生产响应不暴露内部异常细节。

## 问题三：shell=True 命令执行

整改前：

```python
command = f'jo username={username} ip={user_ip} | curl -s http://localhost/api/login -d "@-" | jq'
subprocess.run(command, shell=True, ...)
```

整改后：

```python
requests.post(
    "http://localhost/api/login",
    json={"username": username, "ip": user_ip},
    timeout=5,
)
```

应满足条件：

- 业务参数不进入 shell 命令字符串。
- 外部调用有 timeout 和 HTTP 状态检查。

## 问题四：配置默认值不安全

整改前：

- `SECRET_KEY` 硬编码。
- `DEBUG=True` 默认开启。
- `JWT_KEY` 有固定默认值。

整改后：

- `DJANGO_SECRET_KEY`、`JWT_KEY`、`DJANGO_DEBUG`、`DJANGO_ALLOWED_HOSTS` 从环境变量读取。
- `DEBUG` 默认 `False`。
- 增加安全 Header 和 Cookie 配置。

应满足条件：

- 生产部署不需要修改代码即可注入安全配置。
- 仓库不保存真实密钥。

## 验证记录

已执行：

```bash
python -m compileall .
```

结果：通过，所有 Python 文件语法编译成功。

已执行：

```bash
rg "csrf_exempt|demjson3|shell=True|request\.GET\.get\(\"open_id\"\)|body\[\"open_id" -n 成员代码/朱瑜杰-BYR-IP-Manager
```

结果：业务代码未发现上述高风险模式。

尝试执行：

```bash
python manage.py test bind devices
python manage.py check --deploy
```

结果：当前环境缺少 Django，且系统 Python 没有 pip，命令未能运行。错误为 `ModuleNotFoundError: No module named 'django'`。

后续建议：

1. 在可安装依赖的环境中执行 `pip install -r requirements.txt`。
2. 运行 `python manage.py test bind devices`。
3. 运行 `python manage.py migrate --check` 和 `python manage.py check --deploy`。
