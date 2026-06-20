# 扫描与验证报告

## 扫描对象

`成员代码/朱瑜杰-BYR-IP-Manager`

## 静态模式扫描

命令：

```bash
rg "csrf_exempt|demjson3|shell=True|request\.GET\.get\(\"open_id\"\)|body\[\"open_id" -n 成员代码/朱瑜杰-BYR-IP-Manager
```

结果：

```text
无业务代码命中。
```

说明：

- `csrf_exempt` 已从目标视图移除。
- `demjson3` 已从业务代码和依赖文件移除。
- `shell=True` 已移除。
- 设备接口不再从 query string 或请求体读取 `open_id` 作为授权依据。

## open_id 使用复查

命令：

```bash
rg "open_id" -n 成员代码/朱瑜杰-BYR-IP-Manager/bind 成员代码/朱瑜杰-BYR-IP-Manager/devices 成员代码/朱瑜杰-BYR-IP-Manager/feishu_auth 成员代码/朱瑜杰-BYR-IP-Manager/utils
```

结论：

- `bind/views.py` 中仅用于校验 token `open_id` 与当前登录用户一致。
- `devices/views.py` 中不再使用 `open_id`。
- `feishu_auth/views.py` 中保留 OAuth 用户识别逻辑，属于登录流程必要字段。
- 测试中保留伪造 `open_id` 用例，用于验证越权请求被忽略或拒绝。

## 语法检查

命令：

```bash
python -m compileall .
```

结果：

```text
通过。
```

## Django 测试执行情况

命令：

```bash
python manage.py test bind devices
```

结果：

```text
ModuleNotFoundError: No module named 'django'
```

原因：

当前执行环境没有安装 Django，且 `python -m pip --version`、`python3 -m pip --version` 均显示系统 Python 没有 pip，无法在当前环境直接安装 `requirements.txt` 后运行测试。

## 新增测试覆盖

新增测试文件：

- `成员代码/朱瑜杰-BYR-IP-Manager/bind/tests.py`
- `成员代码/朱瑜杰-BYR-IP-Manager/devices/tests.py`

覆盖场景：

1. `/bind` 即使收到他人 `open_id`，也只为当前登录用户签发 token。
2. `/verify` 拒绝当前用户验证他人的绑定 token。
3. `/devices` 即使收到他人 `open_id`，也只返回当前用户设备。
4. `/devices/<device_id>` 不能通过伪造 `open_id` 删除他人设备。

## 剩余验证动作

在依赖完整环境中继续执行：

```bash
pip install -r requirements.txt
python manage.py test bind devices
python manage.py check --deploy
python manage.py migrate --check
```
