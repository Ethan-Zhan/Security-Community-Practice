import requests
from datetime import datetime
from bind.models import BindInfo


def fetch_status_code():
    log_file_path = "/root/IP_manager/utils/cron.log"
    bind_info_instances = BindInfo.objects.all()
    ip_list = [instance.ip for instance in bind_info_instances]

    for ip in ip_list:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{datetime.now()}: Task started {ip}\n")

        url = "http://127.0.0.1/index"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Real-IP": ip
        }

        try:
            response = requests.get(url, headers=headers)
            with open(log_file_path, "a") as log_file:
                log_file.write(f"{datetime.now()}: Status Code: {response.status_code}\n")
        except requests.exceptions.RequestException as e:
            with open(log_file_path, "a") as log_file:
                log_file.write(f"{datetime.now()}: Error occurred: {e}\n")
