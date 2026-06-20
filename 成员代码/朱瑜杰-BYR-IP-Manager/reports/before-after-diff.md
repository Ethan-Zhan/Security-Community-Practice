# 整改前后对比说明

## 改动主题

BYR-IP-Manager 设备绑定、设备管理、OAuth 回调和安全配置加固。

## 整改前逻辑

1. 登录态接口仍从客户端读取 `open_id`。
2. `/devices` 等接口可通过伪造 `open_id` 查询或操作他人设备。
3. `/verify` 只验证 token 内容和 IP，不校验 token 所属用户是否为当前登录用户。
4. 多个接口使用 `@csrf_exempt`。
5. 外部登录调用通过 `shell=True` 执行 `jo | curl | jq` 管道。
6. `SECRET_KEY` 硬编码，`DEBUG=True`。
7. OAuth 回调响应包含 `user_access_token`。

## 整改后逻辑

1. 设备和绑定接口统一使用 `request.user`。
2. 客户端提交的 `open_id` 不再参与设备所有权判断。
3. `/verify` 校验 token `open_id` 与当前登录用户一致。
4. 目标接口移除 CSRF 豁免。
5. 外部登录调用改为 `requests.post(..., json=..., timeout=5)`。
6. 密钥、DEBUG 和 Host 白名单改为环境变量配置。
7. OAuth 回调不再返回 `user_access_token`。
8. 数据库唯一约束改为 `user+device_id` 和 `user+ip`。

## 关键 diff 摘要

### 授权主体从请求参数改为当前用户

```diff
- body = demjson3.decode(request.body)
- open_id = body["open_id"]
- user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
+ user_info_instance = current_user(request)
```

### token 所属用户校验

```diff
  bind_user_info = bind_get_user_info(token)
+ user_info_instance = current_user(request)
+ if bind_user_info.get('open_id') != user_info_instance.open_id:
+     return error_response("Token owner mismatch", status=403)
```

### 移除 shell 管道调用

```diff
- command = f'jo username={username} ip={user_ip} | curl -s http://localhost/api/login -d "@-" | jq'
- result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
+ response = requests.post(
+     "http://localhost/api/login",
+     json={"username": username, "ip": user_ip},
+     timeout=5,
+ )
```

### 安全配置环境变量化

```diff
- SECRET_KEY = "django-insecure--aio!pbm5!y#@h42)-$2ka#jdzzku-22423y@ge88o=&13izm_"
- DEBUG = True
+ SECRET_KEY = env.str("DJANGO_SECRET_KEY", "django-insecure-change-me-in-env")
+ DEBUG = env.bool("DJANGO_DEBUG", False)
```

## 安全收益

| 对比项 | 整改前 | 整改后 |
| --- | --- | --- |
| 伪造 open_id | 可能越权操作设备 | 忽略客户端身份字段 |
| token 复用 | 他人 token 存在被验证风险 | token 必须属于当前用户 |
| CSRF | 多个接口豁免 | 恢复 Django CSRF 保护 |
| 命令执行 | `shell=True` 管道 | 结构化 HTTP 请求 |
| 密钥配置 | 硬编码 | 环境变量 |
| 错误响应 | 可能泄露异常 | 生产模式通用错误 |
| 重复绑定 | 依赖应用层检查 | 应用层检查 + 数据库唯一约束 |
