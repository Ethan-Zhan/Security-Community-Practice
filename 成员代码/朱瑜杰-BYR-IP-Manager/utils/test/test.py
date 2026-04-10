import requests

# 定义请求的 URL
url = "http://127.0.0.1/index"

# 定义请求头
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Real-IP": "10.117.251.66"
}

# 发送 GET 请求
response = requests.get(url, headers=headers)

# 输出响应内容
print(response.text)
