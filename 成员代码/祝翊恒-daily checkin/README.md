
# signin robot

本项目是一个基于 Python 和 GitHub Actions 实现的自动签到程序，通过自动化脚本定时领取各平台的每日积分。

## 主要功能

1.  **多平台支持**：目前已集成 `AlphaGen` 和 `CreativeHub` 两个平台的签到逻辑。（出于隐私安全，已将真实网站名称替换）
2.  **完全自动化**：利用 GitHub Actions，无需部署服务器，按照预设的时间表自动运行。
3.  **易于扩展**：代码采用模块化设计，可以非常方便地添加新的网站签到逻辑。

## 设置与使用

### 1. 配置 Secrets
为了保护个人账号信息，脚本通过GitHub Secrets获取敏感数据。请在GitHub仓库中点击 `Settings` -> `Secrets and variables` -> `Actions`，添加以下环境变量：
- `ALPHAGEN_COOKIE`: 对应 AlphaGen 网站的 Cookie。
- `CREATIVEHUB_AUTH`: 对应 CreativeHub 网站的 Authorization Token。
*(注意：请确保 Secrets 的名称与 `.github/workflows/signin.yml` 及 `main.py` 中的调用名称一致)*

### 2. 定时任务配置
签到频率在 `.github/workflows/signin.yml` 中定义。
```yaml
on:
  schedule:
    - cron: '24 04,06,08,10 * * *' # 每天指定时间点自动运行
  # UTC时间，对应北京时间（UTC + 8）为 12:24, 14:24, 16:24 and 18:24
```
可以根据需求修改 `cron` 表达式来调整运行时间。

## 如何增加新网站 (代码复用)

本程序支持复用，若需增加新网站，仅需两步：

1.  **编写签到函数**：在 `main.py` 中参考 `sign_in_alphagen` 编写一个新的函数（使用 `requests` 模拟请求）。
2.  **主程序调用**：在 `if __name__ == "__main__":` 块中添加你的新函数即可。

```python
def sign_in_new_site():
    # 1. 从 os.environ 获取 Secret
    # 2. 发送请求
    print("新网站签到成功")

# 在末尾添加调用
if __name__ == "__main__":
    sign_in_alphagen()
    sign_in_creativehub()
    sign_in_new_site() # 新增网站
```

