## 本次PR说明

- 负责的环节：整改 / 安全加固 / 过程文档整理
- 涉及的模块：`成员代码/朱瑜杰-BYR-IP-Manager`

## 识别的主要安全风险

1. 已登录接口仍信任客户端传入的 `open_id`，攻击者可能伪造他人身份查看、绑定、解绑或登录他人设备。
2. 设备登录外部调用使用 `shell=True` 拼接命令，存在命令注入和外部依赖不可控风险。

## 安全约束如何进入AI交互

本次开发前先整理了 `成员代码/朱瑜杰-BYR-IP-Manager/docs/constraint-doc.md`，明确要求：

- 已登录接口必须以 `request.user` 作为唯一授权主体。
- 不得信任客户端提交的 `open_id` 决定操作对象。
- token 所属用户必须与当前登录用户一致。
- 禁止 `csrf_exempt`、`shell=True`、硬编码生产密钥和异常直出。

关键 Prompt 与修正记录见 `成员代码/朱瑜杰-BYR-IP-Manager/docs/prompt-records.md`。

## 审查发现的问题与处置

- 将 `/bind`、`/verify`、`/devices`、`/devices/<device_id>`、`/devices/<device_id>/login`、`/devices/<device_id>/logout` 改为使用当前登录用户。
- `/verify` 新增 token 所属用户校验，用户不匹配返回 403。
- 移除目标接口 `csrf_exempt`。
- 将 shell 管道调用改为 `requests.post(..., json=..., timeout=5)`。
- 将 `SECRET_KEY`、`JWT_KEY`、`DEBUG`、`ALLOWED_HOSTS` 改为环境变量配置。
- 新增数据库唯一约束和越权场景测试。

## 相关过程材料位置

- `成员代码/朱瑜杰-BYR-IP-Manager/docs/risk-analysis.md`
- `成员代码/朱瑜杰-BYR-IP-Manager/docs/constraint-doc.md`
- `成员代码/朱瑜杰-BYR-IP-Manager/docs/prompt-records.md`
- `成员代码/朱瑜杰-BYR-IP-Manager/docs/security-checklist.md`
- `成员代码/朱瑜杰-BYR-IP-Manager/docs/fix-report.md`
- `成员代码/朱瑜杰-BYR-IP-Manager/reports/scan-report.md`
- `成员代码/朱瑜杰-BYR-IP-Manager/reports/before-after-diff.md`
