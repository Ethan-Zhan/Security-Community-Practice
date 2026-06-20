from django.http import JsonResponse
from bind.models import BindInfo
from utils.yxms import start_login_thread, monitor_result_queue
from utils.security import current_user, server_error_response
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import threading
import queue
import urllib.parse


@login_required
def unbound(request, device_id):
    try:
        if not (request.method == 'DELETE'):
            return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
        user_info_instance = current_user(request)
        bind_info_instance = BindInfo.objects.filter(user=user_info_instance, device_id=device_id).first()
        if not bind_info_instance:
            return JsonResponse({"status": "failed", "message": "Device not found"}, status=404)
        bind_info_instance.delete()
        return JsonResponse({"status": "success", "message": "Device unbound successfully"}, status=200)
    except Exception as e:
        return server_error_response(e, "unbound")


@login_required
def login(request, device_id):
    """
    ip_manager最有含金量的部分
    先302重定向到yxms.byr.ink，然后再用线程去请求yxms.byr.ink/api/login
    实现了自动重定向 发包 返回改数据库的过程 全程只需要点击确定
    :param request:
    :param device_id:
    :return:
    """
    try:
        if request.method != 'GET':
            return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
        user_info_instance = current_user(request)
        bind_info_instance = BindInfo.objects.filter(user=user_info_instance, device_id=device_id).first()
        if not bind_info_instance:
            return JsonResponse({"status": "failed", "message": "Device not found"}, status=404)
        if bind_info_instance.logged_in:
            return JsonResponse({"status": "failed", "message": "Already logged in"}, status=200)
        username = user_info_instance.name
        user_ip = bind_info_instance.ip
        result_queue = queue.Queue()
        start_login_thread(username, user_ip, result_queue)
        monitor_thread = threading.Thread(target=monitor_result_queue, args=(result_queue,))
        monitor_thread.daemon = True
        monitor_thread.start()
        return redirect("http://10.117.251.67/?" + urllib.parse.urlencode({"username": username}))
    except Exception as e:
        return server_error_response(e, "device_login")
    pass
# todo: 偶尔会有显示两次请求的情况 但是不影响功能


@login_required
def logout(request, device_id):
    try:
        if not (request.method == 'POST'):
            return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
        user_info_instance = current_user(request)
        bind_info_instance = BindInfo.objects.filter(user=user_info_instance, device_id=device_id).first()
        if not bind_info_instance:
            return JsonResponse({"status": "failed", "message": "Device not found"}, status=404)
        bind_info_instance.logged_in = False
        bind_info_instance.save()
        return JsonResponse({"status": "success",
                             "message": "Device logged out successfully"
                             }, status=200)
    except Exception as e:
        return server_error_response(e, "device_logout")


@login_required
def devices(request):
    try:
        if not (request.method == 'GET'):
            return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
        user_info_instance = current_user(request)
        bind_info_instances = BindInfo.objects.filter(user=user_info_instance)
        devices_list = []
        for bind_info in bind_info_instances:
            devices_list.append({
                "id": bind_info.device_id,
                "ip": bind_info.ip,
                "logged_in": bind_info.logged_in
            })

        return JsonResponse({"status": "success",
                             "devices": devices_list}, status=200)
    except Exception as e:
        return server_error_response(e, "devices")

