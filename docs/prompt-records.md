# AI 交互过程记录

## 交互日期

2026-06-02

## 使用方式

使用 AI 编程工具 Codex 对“校园失物招领平台”的志愿者匹配确认接口进行安全加固。交互方式为：先将安全约束文档提供给 AI，再在同一轮对话中明确目标接口、修改范围、禁止行为和验证要求。

## 本轮发送给 AI 的关键 Prompt

本轮实际发送给 AI 的 Prompt 包含两部分：

1. `docs/constraint-doc.md`
2. 本轮对话中的具体修改要求

其中 `docs/constraint-doc.md` 记录背景说明、任务范围、安全约束和禁止行为；具体修改要求如下：

```markdown
## 对话目标

请只改进“校园失物招领平台”的一个功能点：志愿者确认匹配接口 /api/volunteer/link 的权限与输入校验。不要修改其他功能，不要修改前端，不要修改数据库结构。

## 请先阅读

请先阅读以下文件和代码片段：

1. 成员代码/詹冲-校园失物招领平台/docs/risk-analysis.md
2. 成员代码/詹冲-校园失物招领平台/docs/constraint-doc.md
3. 成员代码/詹冲-校园失物招领平台/docs/security-checklist.md
4. 成员代码/詹冲-校园失物招领平台/backend/app.py 中的 volunteer_link_items

## 具体修改要求

请在 backend/app.py 的 volunteer_link_items 中完成以下改进：

1. 使用项目已有的安全 JSON 读取方式，避免请求体为空时异常。
2. 校验 operatorID、lostItemID、foundItemID 三个必要参数，缺失时返回 400。
3. 查询 operatorID 对应用户是否存在，不存在返回 403。
4. 查询 UserRole 后，仅允许“志愿者”或“管理员”继续执行匹配。
5. 普通用户调用时返回 403，不能执行后续物品更新。
6. 查询失物和拾物时，同时取出 ItemType 和 ItemStatus。
7. 校验 lostItemID 对应 ItemType = Lost，foundItemID 对应 ItemType = Found。
8. 校验两个物品都处于“未找到”状态，否则拒绝匹配。
9. 保留原有“同一用户发布的失物和拾物不能匹配”限制。
10. 继续使用参数化 SQL。
11. 不要把数据库异常原文返回给前端。

## 禁止修改

1. 不修改数据库建表 SQL。
2. 不修改前端 HTML/CSS/JS。
3. 不新增第三方依赖。
4. 不改其他接口。
5. 不硬编码密钥、账号或连接串。

## 修改后请输出

请在完成代码修改后输出：

1. 修改摘要。
2. 安全约束落实情况。
3. 建议运行的验证命令。
4. docs/security-checklist.md 应如何填写。
5. docs/prompt-records.md、docs/fix-report.md、reports/scan-report.md、reports/before-after-diff.md 后续应补充哪些内容。

## 建议验证命令

powershell
python -m py_compile '成员代码\詹冲-校园失物招领平台\backend\app.py'
git diff -- '成员代码\詹冲-校园失物招领平台\backend\app.py'


如本地依赖完整，可进一步使用 Flask test client 或测试数据库验证：

1. 普通用户调用 /api/volunteer/link 应返回 403。
2. 志愿者或管理员使用合法失物和拾物 ID 应成功匹配。
3. 同类型物品、已找回物品、已删除物品应被拒绝。
```

## Prompt 中的核心约束摘要

```text
只改进“校园失物招领平台”的一个功能点：志愿者确认匹配接口 /api/volunteer/link 的权限与输入校验。
不要修改其他功能，不要修改前端，不要修改数据库结构。
```

```text
1. 权限校验必须在后端完成。
2. operatorID 对应用户必须存在。
3. UserRole 必须是“志愿者”或“管理员”。
4. 普通用户、无效用户、未登录用户不得执行匹配确认操作。
5. lostItemID 必须对应 ItemType = Lost。
6. foundItemID 必须对应 ItemType = Found。
7. 两个物品都必须处于“未找到”状态。
8. SQL 必须继续参数化。
9. 错误响应不能泄露数据库异常、堆栈、连接串、密钥或环境变量。
```

## AI 返回结果

已完成，只改了 [backend/app.py](D:/桌面/Security-Community-Practice/成员代码/詹冲-校园失物招领平台/backend/app.py:1215) 里的 `volunteer_link_items`。

**修改摘要**
- 用 `get_json_body()` 替换 `request.json`，空请求体或非对象 JSON 返回 400。
- 强制校验 `operatorID`、`lostItemID`、`foundItemID`，缺失或空字符串返回 400。
- 查询 `operatorID` 的 `UserRole`，只允许 `志愿者`、`管理员`，普通用户返回 403。
- 查询物品时增加 `ItemType`、`ItemStatus`，校验 `Lost` / `Found` 类型和两个物品均为 `未找到`。
- 保留同一用户不能匹配、通知创建、两条物品更新、`commit()`、异常 `rollback()`。
- 错误响应继续用通用消息，没有把数据库异常原文返回给前端。

**已验证**
```powershell
python -m py_compile '成员代码\詹冲-校园失物招领平台\backend\app.py'
git diff -- '成员代码\詹冲-校园失物招领平台\backend\app.py'
git diff --check -- '成员代码\詹冲-校园失物招领平台\backend\app.py'
```
编译通过；diff 只涉及目标函数。`git diff --check` 只有 Git 的 LF/CRLF 提示，没有 whitespace error。

**security-checklist.md 建议填写**
- Prompt 对照检查各项可填“通过”：范围、空 JSON/缺失字段、操作者存在、角色校验、普通用户拒绝、物品类型、物品状态、同用户限制、成功响应兼容。
- 人工安全审查中“最小权限原则、服务端授权、参数化 SQL、数据状态一致性、错误响应、回滚逻辑、外部依赖、改动范围”可填“通过”。
- 补充说明：运行了 `py_compile` 和 `git diff`；数据库场景需用测试库人工验证。

**后续文档可补充**
- `docs/prompt-records.md`：记录本轮提示词、目标接口、禁止范围和执行命令。
- `docs/fix-report.md`：写明新增校验点、返回码、未改动内容和验证结果。
- `reports/scan-report.md`：记录风险项从“普通用户可越权/类型状态未校验”变为已修复。
- `reports/before-after-diff.md`：摘录本次 `git diff`，说明修改前后行为差异。

还需要人工用测试库补测：普通用户 403、无效用户 403、合法志愿者/管理员成功、同类型物品 400、非 `未找到` 状态 409。

## AI 生成结果中与安全约束相关的关键片段

### 安全读取和参数校验

```python
data = get_json_body()
if not isinstance(data, dict):
    return error_response('请求参数格式错误', 400)

operator_id = data.get('operatorID')
lost_item_id = data.get('lostItemID')
found_item_id = data.get('foundItemID')

required_values = (operator_id, lost_item_id, found_item_id)
if any(value is None or (isinstance(value, str) and not value.strip()) for value in required_values):
    return error_response('缺少必要参数', 400)
if any(isinstance(value, (dict, list)) for value in required_values):
    return error_response('请求参数格式错误', 400)
```

### 后端角色校验

```python
cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (operator_id,))
operator = cursor.fetchone()
if not operator:
    return error_response('无效的用户ID或未登录', 403)
if operator[0] not in ('志愿者', '管理员'):
    return error_response('仅志愿者或管理员可以执行匹配操作', 403)
```

### 物品类型和状态校验

```python
cursor.execute('SELECT "UserID", "ItemName", "ItemType", "ItemStatus" FROM "Items" WHERE "ItemID" = %s', (lost_item_id,))
lost_item_data = cursor.fetchone()
cursor.execute('SELECT "UserID", "ItemName", "ItemType", "ItemStatus" FROM "Items" WHERE "ItemID" = %s', (found_item_id,))
found_item_data = cursor.fetchone()

if lost_item_type != 'Lost' or found_item_type != 'Found':
    return error_response('物品类型不匹配，必须由失物和拾物组成', 400)
if lost_item_status != '未找到' or found_item_status != '未找到':
    return error_response('只能匹配未找到状态的物品', 409)
```

## 偏差或问题处理

本轮 AI 输出没有偏离任务范围。人工复查 `git diff` 后确认：

1. 代码改动集中在 `backend/app.py` 的 `volunteer_link_items`。
2. 未修改前端页面。
3. 未修改数据库结构。
4. 未新增第三方依赖。
5. 安全约束落实在后端逻辑中，而不是只写在注释里。

## 最终采纳情况

采纳本轮 AI 生成的改动，并补充完成 `docs/` 和 `reports/` 下的过程材料。
