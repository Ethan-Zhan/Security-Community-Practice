# 扫描与验证报告

## 基本信息

- 日期：2026-06-02
- 项目：校园失物招领平台
- 验证对象：`backend/app.py`
- 目标函数：`volunteer_link_items`
- 目标接口：`POST /api/volunteer/link`

## 本次关注的风险项

| 风险项 | 整改前状态 | 整改后状态 |
| --- | --- | --- |
| 普通用户可能越权确认匹配 | 后端只确认用户存在，角色限制不足 | 已增加“志愿者/管理员”角色校验 |
| 缺少必要参数 | 可能进入数据库逻辑或异常路径 | 已返回 400 |
| 非对象 JSON 或异常字段类型 | 缺少明确格式校验 | 已返回 400 |
| 物品类型错误 | 可能传入非 Lost/Found 成对物品 | 已校验 Lost/Found 类型 |
| 物品状态错误 | 可能重复操作非“未找到”物品 | 已限制两个物品都必须为“未找到” |

## 验证命令与结果

### 1. Python 语法检查

命令：

```powershell
python -m py_compile '成员代码\詹冲-校园失物招领平台\backend\app.py'
```

结果：通过，无错误输出。

### 2. diff 范围检查

命令：

```powershell
git diff -- '成员代码\詹冲-校园失物招领平台\backend\app.py'
```

结果：通过。代码 diff 集中在 `volunteer_link_items`，未修改前端、数据库结构或其他成员项目。

### 3. whitespace 检查

命令：

```powershell
git diff --check -- '成员代码\詹冲-校园失物招领平台\backend\app.py'
```

结果：通过。命令只出现 Git 的 LF/CRLF 提示，没有 whitespace error。

### 4. diff 统计

命令：

```powershell
git diff --stat
```

结果摘要：

```text
backend/app.py | 36 ++++++++++++++++++++++++++----------
1 file changed, 26 insertions(+), 10 deletions(-)
```

### 5. Flask test client 接口行为测试

验证方式：使用 Flask test client 调用 `POST /api/volunteer/link`，并用可控测试数据模拟不同用户角色、物品类型、物品状态和事务提交情况。

结果摘要：

```text
missing_operator: status=400, success=False, message=缺少必要参数, commits=False
invalid_user: status=403, success=False, message=无效的用户ID或未登录, commits=False
normal_user_forbidden: status=403, success=False, message=仅志愿者或管理员可以执行匹配操作, commits=False
wrong_item_type: status=400, success=False, message=物品类型不匹配，必须由失物和拾物组成, commits=False
wrong_item_status: status=409, success=False, message=只能匹配未找到状态的物品, commits=False
valid_volunteer_success: status=200, success=True, message=匹配成功，已通知双方用户, commits=True
```

测试结论：

1. 缺少必要参数时不会进入事务提交。
2. 无效用户和普通用户均会被后端拒绝。
3. 物品类型错误和状态错误均会在更新前被拒绝。
4. 合法志愿者匹配合法失物和拾物时可以成功提交。

## 人工审查结论

1. 角色校验发生在物品查询和数据库更新之前。
2. 普通用户会在进入更新逻辑前被 403 拒绝。
3. 物品类型和状态校验发生在更新 `Items` 表之前。
4. SQL 查询仍使用参数化绑定。
5. 异常分支仍执行 `rollback()` 并返回通用错误。

## 测试范围说明

当前已完成 Flask test client 行为测试。测试覆盖了缺参、无效用户、普通用户、错误物品类型、错误物品状态和合法志愿者成功路径，能够验证本次新增的服务端权限校验、输入校验、类型校验和状态校验是否按预期生效。
