## 本次PR说明

- 负责的环节：整改
- 涉及的模块：校园失物招领平台后端志愿者匹配确认接口 `POST /api/volunteer/link`

## 识别的主要安全风险

1. 原接口主要校验 `operatorID` 是否对应存在用户，但“用户存在”不等于“用户有权限”，普通用户可能伪造请求越权确认匹配。
2. 原接口缺少对 `lostItemID`、`foundItemID` 的物品类型和状态校验，可能导致同类型物品、已找回物品或正在联系中的物品被错误关联。

## 安全约束如何进入AI交互

本次修改前，先把风险识别结果整理为 `docs/constraint-doc.md`，并在与 AI 交互时完整提供该约束文档，同时在对话中明确要求：

1. 权限校验必须在后端完成，不能只依赖前端页面限制。
2. 只有“志愿者”和“管理员”可以执行匹配确认。
3. `lostItemID` 必须对应 `ItemType = Lost`，`foundItemID` 必须对应 `ItemType = Found`。
4. 两条物品都必须处于“未找到”状态。
5. SQL 必须继续使用参数化查询。
6. 不修改前端、不修改数据库结构、不新增依赖、不扩大到其他接口。

## 审查发现的问题与处置

审查发现 `/api/volunteer/link` 属于会修改物品状态和创建通知的敏感写接口，原逻辑存在服务端角色校验不足、物品类型校验不足和状态校验不足的问题。

处置方式：

1. 使用 `get_json_body()` 处理请求体，缺少必要参数或参数格式错误时返回 400。
2. 查询 `operatorID` 对应用户角色，只允许“志愿者”和“管理员”继续执行，普通用户返回 403。
3. 查询物品时补充读取 `ItemType` 和 `ItemStatus`。
4. 在更新数据库前校验 Lost/Found 类型和“未找到”状态。
5. 保留原有同一用户不能自匹配、通知创建、事务提交和异常回滚逻辑。

验证情况：

1. `python -m py_compile` 通过。
2. `git diff` 显示代码改动集中在 `backend/app.py` 的 `volunteer_link_items`。
3. `git diff --check` 没有 whitespace error。
4. 已使用 Flask test client 做接口行为测试，覆盖缺参、无效用户、普通用户、错误物品类型、错误物品状态和合法志愿者成功路径，测试均符合预期。

## 相关过程材料位置

- `docs/risk-analysis.md`
- `docs/constraint-doc.md`
- `docs/prompt-records.md`
- `docs/security-checklist.md`
- `docs/fix-report.md`
- `reports/scan-report.md`
- `reports/before-after-diff.md`
