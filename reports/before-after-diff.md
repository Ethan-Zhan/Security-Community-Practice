# 整改前后对比说明

## 改动主题

志愿者匹配确认接口 `/api/volunteer/link` 的权限与输入校验加固。

## 整改前逻辑

整改前，接口主要执行以下步骤：

1. 使用 `request.json` 读取请求体。
2. 从请求体中读取 `operatorID` 或 `volunteerID`。
3. 查询 `operatorID` 对应用户是否存在。
4. 查询 `lostItemID` 和 `foundItemID` 对应物品。
5. 判断两条物品是否由同一用户发布。
6. 更新两条物品为“正在联系中”。
7. 创建双方通知。

主要不足：

1. 没有明确限制操作者必须为“志愿者”或“管理员”。
2. 对空请求体、非对象 JSON、空字符串参数和数组/对象参数缺少统一格式校验。
3. 查询物品时没有取出并校验 `ItemType`。
4. 查询物品时没有取出并校验 `ItemStatus`。

## 整改后逻辑

整改后，接口新增以下控制点：

1. 使用 `get_json_body()` 安全读取请求体。
2. 非对象 JSON 返回 400。
3. 缺少 `operatorID`、`lostItemID`、`foundItemID` 或空字符串返回 400。
4. 字段值为对象或数组时返回 400。
5. 无效用户返回 403。
6. 用户角色不是“志愿者”或“管理员”时返回 403。
7. `lostItemID` 必须对应 `ItemType = Lost`。
8. `foundItemID` 必须对应 `ItemType = Found`。
9. 两个物品都必须处于“未找到”状态，否则返回 409。
10. 原有同一用户不能匹配、通知创建、事务提交和异常回滚逻辑保留。

## 关键 diff 摘要

### 请求体和必要参数校验

```diff
-    data = request.json
-    operator_id = data.get('operatorID') or data.get('volunteerID')
+    data = get_json_body()
+    if not isinstance(data, dict):
+        return error_response('请求参数格式错误', 400)
+
+    operator_id = data.get('operatorID')
     lost_item_id = data.get('lostItemID')
     found_item_id = data.get('foundItemID')
+
+    required_values = (operator_id, lost_item_id, found_item_id)
+    if any(value is None or (isinstance(value, str) and not value.strip()) for value in required_values):
+        return error_response('缺少必要参数', 400)
+    if any(isinstance(value, (dict, list)) for value in required_values):
+        return error_response('请求参数格式错误', 400)
```

### 操作者角色校验

```diff
         cursor.execute('SELECT "UserRole" FROM "Users" WHERE "UserID" = %s', (operator_id,))
         operator = cursor.fetchone()
         if not operator:
-            return jsonify({'success': False, 'message': '无效的用户ID或未登录'}), 403
+            return error_response('无效的用户ID或未登录', 403)
+        if operator[0] not in ('志愿者', '管理员'):
+            return error_response('仅志愿者或管理员可以执行匹配操作', 403)
```

### 物品类型和状态校验

```diff
-        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (lost_item_id,))
+        cursor.execute('SELECT "UserID", "ItemName", "ItemType", "ItemStatus" FROM "Items" WHERE "ItemID" = %s', (lost_item_id,))
         lost_item_data = cursor.fetchone()
-        cursor.execute('SELECT "UserID", "ItemName" FROM "Items" WHERE "ItemID" = %s', (found_item_id,))
+        cursor.execute('SELECT "UserID", "ItemName", "ItemType", "ItemStatus" FROM "Items" WHERE "ItemID" = %s', (found_item_id,))
         found_item_data = cursor.fetchone()
```

```diff
-        lost_user_id, lost_item_name = lost_item_data
-        found_user_id, found_item_name = found_item_data
+        lost_user_id, lost_item_name, lost_item_type, lost_item_status = lost_item_data
+        found_user_id, found_item_name, found_item_type, found_item_status = found_item_data
+
+        if lost_item_type != 'Lost' or found_item_type != 'Found':
+            return error_response('物品类型不匹配，必须由失物和拾物组成', 400)
+        if lost_item_status != '未找到' or found_item_status != '未找到':
+            return error_response('只能匹配未找到状态的物品', 409)
```

## 安全收益

| 对比项 | 整改前 | 整改后 |
| --- | --- | --- |
| 普通用户伪造请求 | 可能通过用户存在性检查 | 返回 403 |
| 无效或异常参数 | 校验不足 | 返回 400 |
| 同类型物品匹配 | 缺少明确阻断 | 返回 400 |
| 已完成或已删除物品重复匹配 | 缺少明确阻断 | 返回 409 |
| 数据库异常暴露 | 异常分支为通用错误 | 保持通用错误 |
| SQL 注入 | 使用参数化 SQL | 继续使用参数化 SQL |

