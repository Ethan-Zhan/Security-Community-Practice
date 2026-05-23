# Prompt记录与AI交互留痕 (docs/prompt-records.md)
**课程名称**: 信息安全管理  
**交互工具**: Antigravity (Advanced AI Coding Assistant)  
**记录日期**: 2026-05-23  

---

## 一、 结构化提示词 (Structured Prompt) 表达
为了确保 AI 严格实现安全边界，我们构建了以下包含“背景说明”、“任务范围”、“约束条件”和“禁止行为”的结构化 Prompt，并将其输入给 AI 辅助编程工具。

### 输入 Prompt 文本展示：
```text
【背景说明】
我正在进行一项信息安全管理课程的期末实践作业。现需要将我本地编写的一个基于 TensorFlow/CNN 的图像分类本地脚本 (imageClassification.py) 升级为一个可以通过外部客户端发送图片请求调用的 Flask Web API 推理服务。

【任务范围】
只允许在“王彦杰-Image Classification using CNN”的目录下进行编码。不要触碰其他同学的项目文件。

【安全约束条件】
1. 必须提供身份验证！调用预测接口 (/api/predict) 必须验证 Authorization Header 是否包含 Bearer BUPT_SEC_2026_TEST_KEY。
2. 必须防止路径遍历！使用 secure_filename 对用户上传的图片文件名进行彻底规范化。
3. 必须限制上传大小在 2MB 以内，拦截超大文件并返回 413，以防止 DoS 攻击。
4. 必须进行木马过滤！使用 Pillow 二进制流分析图片数据，调用 verify() 判断图片结构的合法性，拦截混入恶意外壳的 Webshell 脚本图片。
5. 必须防报错泄露！捕获全局内部错误，统一返回 Mask 错误信息，隐蔽后端物理盘符路径和 Traceback。
6. 必须高兼容！若 TensorFlow 库在本地环境导入失败，服务需要能自动降级至安全模拟演示模式（Mock Mode），使所有安全防御拦截依然 100% 真实执行，仅在最后一步推理采用仿真返回，保障零环境报错。

【禁止行为】
- 严禁使用无过滤的原始文件名写入文件。
- 严禁允许匿名调用此高敏感推理算力 API。
```

---

## 二、 AI 生成结果中与安全约束相关的关键片段
AI 接收到上述结构化约束 Prompt 后，生成了高度合规的代码片段。以下是落实了安全约束条件的关键代码片段摘录：

### 1. 落实 API Key 身份验证约束
```python
def check_authentication(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header:
        logger.warning("拦截未授权访问: 请求未携带 Authorization 头部")
        return False
    try:
        token_type, token = auth_header.split(" ")
        if token_type.lower() != "bearer" or token != API_KEY:
            logger.warning(f"拦截非法访问: API Key 校验不匹配 (传入的Token为: {token})")
            return False
        return True
    except ValueError:
        logger.warning(f"拦截非法访问: Authorization 头部格式错误")
        return False
```

### 2. 落实路径遍历防御与上传文件安检约束
```python
# 路径遍历漏洞防护
original_filename = file.filename
safe_filename = secure_filename(original_filename)
if original_filename != safe_filename:
    logger.warning(f"【路径遍历攻击防御】 检测到异常输入文件名: '{original_filename}'，已安全规范化为: '{safe_filename}'")

# 文件木马检验
try:
    img = Image.open(file.stream)
    img.verify()  # 检查图片底层二进制结构
    file.stream.seek(0)
except Exception as e:
    logger.error(f"【文件安检拦截】 检测到非法图片流！报错信息: {e}")
    return jsonify({
        "success": False,
        "error_type": "MALICIOUS_FILE_BLOCKED",
        "message": "安全防御拦截：您上传的文件数据不合法！"
    }), 400
```

### 3. 落实大文件 DoS 防护与异常信息泄露防护
```python
# 限制 2MB 最大限制
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

@app.errorhandler(413)
def request_entity_too_large(error):
    logger.warning("【拒绝服务DoS防御】 拦截到超大文件上传攻击，已自动予以切断。")
    return jsonify({
        "success": False,
        "error_type": "REQUEST_ENTITY_TOO_LARGE",
        "message": "安全防御拦截：上传的文件体积过大！"
    }), 413

# 统一全局异常返回，防物理路径泄露
except Exception as ex:
    logger.error(f"内部发生未知异常: {ex}")
    return jsonify({
        "success": False,
        "error_type": "INTERNAL_SERVER_ERROR",
        "message": "服务在处理请求时发生内部错误，出于安全机制，已隐蔽真实系统物理堆栈报错。"
    }), 500
```

---

## 三、 发现偏差或问题时的交互记录
在 AI 开发的早期，AI 试图仅通过上传文件的文件名扩展名后缀来进行安全性判断（即简单比对 `.png`）。
*   **交互偏差**: 人工审查指出：“仅仅校验文件名后缀无法防御隐藏在图片内部的恶意 Webshell（即图片马）”。
*   **安全纠正**: 人工命令 AI：“必须结合 `PIL.Image` 二进制流加载，在内存中强行解析并调用 `verify()`，如果是非图片数据必须报错并予以切断”。
*   **整改结果**: AI 迅速更新了逻辑，在代码中加入了完整的 Pillow 二进制流安检，并在 `secure_classification_api.py` 中完美实现。
