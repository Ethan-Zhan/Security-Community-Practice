import requests

def login_yxms(username, user_ip):
    url = "https://yxms.byr.ink/api/login"
    data = {
        "username": username,
        "ip": user_ip
    }
    response = requests.post(url, json=data)

    return response

login_yxms("pythok", "127.0.0.1")