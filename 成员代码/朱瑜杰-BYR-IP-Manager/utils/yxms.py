from feishu_auth.models import UserInfo
from bind.models import BindInfo
import time
import threading
import queue
import requests
from utils.exception.exception import (
    InvalidException
)


def login_yxms(username, user_ip, result_queue):
    time.sleep(3)
    response = requests.post(
        "http://localhost/api/login",
        json={"username": username, "ip": user_ip},
        timeout=5,
    )
    response.raise_for_status()
    output_str = response.json()
    user_info_instance = UserInfo.objects.filter(name=username).first()
    bind_info_instance = BindInfo.objects.filter(user=user_info_instance, ip=user_ip).first()
    if not bind_info_instance:
        raise Exception(InvalidException)
    bind_info_instance.logged_in = output_str.get("success")
    bind_info_instance.save()


def start_login_thread(username, user_ip, result_queue):
    thread = threading.Thread(target=login_yxms, args=(username, user_ip, result_queue))
    thread.start()
    return thread


def monitor_result_queue(result_queue):
    while True:
        try:
            result = result_queue.get()
            break
        except queue.Empty:
            continue
