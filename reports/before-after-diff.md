# 漏洞整改前后对比说明 (before-after-diff.md)

以下展示了本项目中 `main.py` 在针对**日志泄漏风险**进行本轮安全加固前后的核心代码块变化对比：

### 1. 异常状态与非预期响应输出对比
* **整改前（高危：可能泄漏第三方 API 回显的 Headers）**：
  ```python
  elif response.status_code == 400:
      print(f"处于冷却中。响应: {response.text}")
  else:
      print(f"异常状态码: {response.status_code}, 响应: {response.text}")
  ```
* **整改后（安全：仅提取状态语义，绝不打印原文）**：
  ```python
  elif response.status_code == 400:
      # 仅提取结构化的特定字段，杜绝直接打印整段 response.text 全文
      err_msg = res_json.get("message", "冷却中/已达到上限")
      safe_print(f"处于冷却中。接口返回信息: {err_msg}")
  else:
      safe_print(f"网络异常，请求收到非预期状态码: {response.status_code}")
  ```

---

### 2. 网络异常（Exception）捕获对比
* **整改前（高危：堆栈报错直接输出到标准输出可能夹带 Cookie）**：
  ```python
  except Exception as e:
      print(f"运行出错: {e}")
  ```
* **整改后（安全：经清洗、净化后，仅输出安全类名提示）**：
  ```python
  except Exception as e:
      # 利用包装器拦截原生报错，进行敏感词模糊遮掩与堆栈深度脱敏
      safe_print(safe_format_exception(e))
  ```

---

### 3. 日志打印入口对比
* **整改前（高危：使用不加防备的原生 print）**：
  ```python
  print("正在执行AlphaGen签到")
  ```
* **整改后（安全：全部流经防泄露脱敏漏斗）**：
  ```python
  safe_print("正在执行AlphaGen签到")
  ```
