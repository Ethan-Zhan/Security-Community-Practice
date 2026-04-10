from feishu_auth.models import UserInfo
from bind.models import BindInfo
import time
import threading
import queue
import http.client
import json
import subprocess
from utils.exception.exception import (
    InvalidException
)


def login_yxms(username, user_ip, result_queue):
    time.sleep(3)
    command = f'jo username={username} ip={user_ip} | curl -s http://localhost/api/login -d "@-" | jq'
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    output_str = json.loads(result.stdout)
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