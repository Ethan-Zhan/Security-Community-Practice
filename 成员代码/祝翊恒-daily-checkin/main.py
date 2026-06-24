import os
import requests
import time
import sys
import re

# ================= 配置与常量定义 =================
# 默认请求头 User-Agent，避免在各签到函数中重复硬编码
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36 Edg/144.0.0.0'

# 原地等待时的额外缓冲时间（秒）
SLEEP_BUFFER = 5

# 两个签到任务之间的间隔时间（秒），防止请求过于频繁
TASK_INTERVAL = 2
# =================================================


# ================= 安全加固模块 (Log Masking & Sanitization) =================

def safe_print(msg):
    """
    安全控制台输出函数：
    在输出至标准输出控制台之前，动态检测并遮蔽可能存在于文本中的环境变量敏感 Secrets，
    同时预防第三方接口报错泄露 Request Headers（如 Cookie、Authorization 等）。
    """
    if not isinstance(msg, str):
        msg = str(msg)

    # 1. 动态加载环境变量中的敏感 Secrets 值，构建屏蔽黑名单
    alphagen_cookie = os.environ.get("ALPHAGEN_COOKIE", "").strip()
    creativehub_auth = os.environ.get("CREATIVEHUB_AUTH", "").strip()

    secrets_to_mask = []
    # 仅屏蔽长度合规的密钥，防止空字符串或极短字符引起误杀
    if len(alphagen_cookie) > 6:
        secrets_to_mask.append(alphagen_cookie)
    if len(creativehub_auth) > 6:
        secrets_to_mask.append(creativehub_auth)

    # 2. 对匹配到黑名单密钥的部分执行强制遮罩替换
    for secret in secrets_to_mask:
        msg = msg.replace(secret, "[REDACTED_SECRET]")

    # 3. 深度防御：利用正则表达式过滤日志中可能回显的 Cookie 和 Authorization 信息
    msg = re.sub(r'(cookie\s*[:=]\s*)[^;&\n\r\t]+', r'\1[REDACTED_COOKIE]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'(authorization\s*[:=]\s*)[^\s&\n\r\t]+', r'\1[REDACTED_AUTH]', msg, flags=re.IGNORECASE)

    # 4. 执行最终的安全输出
    print(msg)


def safe_format_exception(e):
    """
    安全异常格式化器：
    防止原生异常报错信息（如 requests 抛出的网络异常）回显并打印含有 Cookie/Token 的完整网络请求上下文。
    """
    err_str = str(e)
    # 剔除已知的环境变量敏感信息
    alphagen_cookie = os.environ.get("ALPHAGEN_COOKIE", "").strip()
    creativehub_auth = os.environ.get("CREATIVEHUB_AUTH", "").strip()
    
    if alphagen_cookie and alphagen_cookie in err_str:
        err_str = err_str.replace(alphagen_cookie, "[REDACTED_COOKIE]")
    if creativehub_auth and creativehub_auth in err_str:
        err_str = err_str.replace(creativehub_auth, "[REDACTED_AUTH]")

    # 仅提取异常类型与过滤后的核心错误，隐去详细连接请求头
    err_type = type(e).__name__
    return f"[{err_type}] 发生网络或运行时异常（详细上下文已执行安全脱敏）"

# =========================================================================


def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h)}小时{int(m)}分{int(s)}秒"

def smart_sleep(delay_seconds):
    if delay_seconds <= 0:
        return True

    MAX_WAIT = 900

    if delay_seconds < MAX_WAIT:
        safe_print(f"距离签到时间还差 {format_time(delay_seconds)},原地等待")
        time.sleep(delay_seconds + SLEEP_BUFFER) 
        return True
    else:
        safe_print(f"距离签到时间还很长（{format_time(delay_seconds)}）,本次跳过")
        return False

def sign_in_alphagen():
    safe_print("正在执行AlphaGen签到")

    alphagen_cookie = os.environ.get("ALPHAGEN_COOKIE", "").strip()
    if not alphagen_cookie:
        safe_print("未在Secrets中找到ALPHAGEN_COOKIE")
        return

    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'cookie': alphagen_cookie,
        'origin': 'https://alphagen.ai',
        'user-agent': DEFAULT_USER_AGENT, 
    }

    try:
        safe_print("获取准确倒计时")
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
                    safe_print("结束等待,发起签到请求")
                else:
                    safe_print("距离下次签到还有很久")
                    return
            else:
                safe_print("时间已到，直接签到")
        else:
            safe_print("无法从接口获取倒计时，尝试直接签到")

        response = requests.post('https://alphagen.ai/api/claim_free_gems', headers=headers, data='{}')
        res_json = response.json() if response.status_code == 200 else {}

        if response.status_code == 200:
            new_gems = res_json.get("user", {}).get("gems", "none")
            safe_print(f"签到成功,当前积分: {new_gems}")
        elif response.status_code == 400:
            # 安全优化：不直接打印 response.text 全文，只打印净化后的状态和结构化返回
            msg_summary = res_json.get("message", "Request limit reached")
            safe_print(f"处于冷却中。接口信息: {msg_summary}")
        else:
            safe_print(f"异常状态码: {response.status_code}，连接已重置或请求被拒")

    except Exception as e:
        # 安全优化：使用安全异常格式化器
        safe_print(safe_format_exception(e))

def sign_in_creativehub():
    safe_print("正在执行CreativeHub签到")

    auth_token = os.environ.get("CREATIVEHUB_AUTH", "").strip()
    if not auth_token:
        safe_print("未在Secrets中找到 CREATIVEHUB_AUTH")
        return

    headers = {
        'accept': '*/*',
        'authorization': auth_token,
        'origin': 'https://creativehub.ai',
        'user-agent': DEFAULT_USER_AGENT, 
    }

    try:
        response = requests.post('https://creativehub.ai/api/GetDailyFreeCredits', headers=headers)
        res_data = response.json() if response.status_code == 200 else {}

        if response.status_code == 200 and res_data.get("code") == 200:
            safe_print("签到成功")
        elif "not in time" in str(response.text).lower():
            safe_print("冷却中")
        else:
            # 安全优化：只输出状态码和解析后的 JSON Code，不输出可能回显 Headers 的全文
            err_code = res_data.get("code", "unknown")
            safe_print(f"其他状态码: {response.status_code}, 业务响应码: {err_code}")
    except Exception as e:
        # 安全优化：使用安全异常格式化器
        safe_print(safe_format_exception(e))

if __name__ == "__main__":
    sign_in_alphagen()
    time.sleep(TASK_INTERVAL) 
    sign_in_creativehub()
