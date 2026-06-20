# Prompt 记录

## 用户原始任务

```text
类似于origin/詹冲-匹配接口安全加固 根据/root/homework/Security-Community-Practice/期末作业.pdf 对/root/homework/Security-Community-Practice/成员代码/朱瑜杰-BYR-IP-Manager进行安全加固 你需要新建一个branch 然后在这个分支里完成期末作业里要求的工作
```

## 关键约束 Prompt

```text
背景：目标项目是 Django 编写的 BYR-IP-Manager，包含飞书 OAuth 登录、设备绑定、设备列表、设备解绑、设备登录/登出、JWT token 验证等功能。

任务范围：只修改成员代码/朱瑜杰-BYR-IP-Manager，并在该项目目录下新增期末作业要求的 docs/ 与 reports/ 过程材料。

安全约束：
1. 已登录接口必须以 request.user 作为唯一授权主体。
2. 不得信任客户端提交的 open_id 来决定查询、绑定、解绑或登录哪一个用户的设备。
3. token 验证必须检查 token 所属 open_id 与当前登录用户一致。
4. 状态变更接口不得使用 csrf_exempt 绕过 CSRF。
5. JSON 请求体必须安全解析，非法 JSON 返回 400。
6. 禁止 shell=True 和字符串拼接命令。
7. 生产密钥、DEBUG、Host 白名单必须从环境变量读取。
8. 异常不能在生产模式下原样返回给客户端。

禁止行为：
1. 不新增真实凭据。
2. 不扩大修改到其他成员项目。
3. 不只写注释，必须落实到代码逻辑和测试。
```

## AI 生成结果中的安全关键片段

```python
user_info_instance = current_user(request)
```

用于替代从请求体或 query string 读取 `open_id` 后查询用户的旧逻辑。

```python
if bind_user_info.get('open_id') != user_info_instance.open_id:
    return error_response("Token owner mismatch", status=403)
```

用于阻止当前登录用户拿其他用户的绑定 token 完成设备验证。

```python
response = requests.post(
    "http://localhost/api/login",
    json={"username": username, "ip": user_ip},
    timeout=5,
)
response.raise_for_status()
```

用于替换 `shell=True` 管道命令。

## 发现偏差后的修正记录

1. 初始审查发现 `callback` 新用户首次登录时保存表单后仍使用旧的 `user_info_instance` 变量，可能为 `None`，已改为接收 `user_info_form.save()` 返回值后再登录。
2. 发现绑定 token 刷新逻辑中使用错误字段名 `openid`，已修正为 `open_id`，并在找不到绑定记录时返回无效 token。
3. 发现静态扫描中 `demjson3` 只剩依赖文件引用，业务代码不再使用后从 `requirements.txt` 移除。
4. 发现语法编译会生成 `__pycache__`，已清理生成物，避免污染提交。
