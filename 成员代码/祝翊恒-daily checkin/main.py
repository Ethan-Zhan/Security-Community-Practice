import os
import requests
import time
import sys

def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h)}小时{int(m)}分{int(s)}秒"

def smart_sleep(delay_seconds):
    if delay_seconds <= 0:
        return True

    MAX_WAIT = 900

    if delay_seconds < MAX_WAIT:
        print(f"距离签到时间还差 {format_time(delay_seconds)},原地等待")
        time.sleep(delay_seconds + 5)
        return True
    else:
        print(f"距离签到时间还很长（{format_time(delay_seconds)}）,本次跳过")
        return False

def sign_in_alphagen():
    print("正在执行AlphaGen签到")

    alphagen_cookie = os.environ.get("ALPHAGEN_COOKIE", "").strip()
    if not alphagen_cookie:
        print("未在Secrets中找到ALPHAGEN_COOKIE")
        return

    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'cookie': alphagen_cookie,
        'origin': 'https://alphagen.ai',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36 Edg/144.0.0.0',
    }

    try:
        print("获取准确倒计时")
        acc_res = requests.get('https://alphagen.ai/api/account', headers=headers)
        acc_json = acc_res.json() if acc_res.status_code == 200 else {}

        user_data = acc_json.get("user", {})
        current_ts = user_data.get("date") or acc_json.get("date") or int(time.time() * 1000)
        next_ts = user_data.get("nextFreeGemsAt") or acc_json.get("nextFreeGemsAt")
        gems = user_data.get("gems", "none")

        if next_ts:
            wait_sec = (int(next_ts) - int(current_ts)) / 1000

            if wait_sec > 0:
                if smart_sleep(wait_sec):
                    print("结束等待,发起签到请求")
                else:
                    print("距离下次签到还有很久")
                    return
            else:
                print("时间已到，直接签到")
        else:
            print("无法从接口获取倒计时，尝试直接签到")

        response = requests.post('https://alphagen.ai/api/claim_free_gems', headers=headers, data='{}')
        res_json = response.json() if response.status_code == 200 else {}

        if response.status_code == 200:
            new_gems = res_json.get("user", {}).get("gems", "none")
            print(f"签到成功,当前积分: {new_gems}")
        elif response.status_code == 400:
            print(f"处于冷却中。响应: {response.text}")
        else:
            print(f"异常状态码: {response.status_code}, 响应: {response.text}")

    except Exception as e:
        print(f"运行出错: {e}")

def sign_in_creativehub():
    print("正在执行CreativeHub签到")

    auth_token = os.environ.get("CREATIVEHUB_AUTH", "").strip()
    if not auth_token:
        print("未在Secrets中找到 CREATIVEHUB_AUTH")
        return

    headers = {
        'accept': '*/*',
        'authorization': auth_token,
        'origin': 'https://creativehub.ai',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36 Edg/144.0.0.0',
    }

    try:
        response = requests.post('https://creativehub.ai/api/GetDailyFreeCredits', headers=headers)
        res_data = response.json() if response.status_code == 200 else {}

        if response.status_code == 200 and res_data.get("code") == 200:
            print("签到成功")
        elif "not in time" in str(response.text).lower():
            print("冷却中")
        else:
            print(f"其他状态: {response.status_code}, 内容: {response.text}")
    except Exception as e:
        print(f"请求错误: {e}")


if __name__ == "__main__":
    sign_in_alphagen()
    time.sleep(2)
    sign_in_creativehub()
