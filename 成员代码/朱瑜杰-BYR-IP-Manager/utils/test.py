import requests

# 目标URL
url = 'https://www.baidu.com'

# 可选：请求的头部信息
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Real-IP" : "10.117.251.66"
}

# 发起GET请求
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    # 输出响应内容（例如：json数据）
    print(response.text)
else:
    print(f"Request failed with status code {response.status_code}")