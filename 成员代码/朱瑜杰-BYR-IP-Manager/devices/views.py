from django.http import JsonResponse, HttpResponse
from feishu_auth.models import UserInfo
from bind.models import BindInfo
from django.views.decorators.csrf import csrf_exempt
from utils.yxms import start_login_thread, monitor_result_queue
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import demjson3
import threading
import queue
import subprocess


@login_required
@csrf_exempt
def unbound(request, device_id):
    try:
        if not (request.method == 'DELETE'):
            return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
        body = demjson3.decode(request.body)
        open_id = body["open_id"]
        if not open_id:
            return JsonResponse({"msg": "Missing open_id parameter"}, status=400)
        user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
        if not user_info_instance:
            return JsonResponse({"msg": "User not exists"}, status=404)
        bind_info_instance = BindInfo.objects.filter(user=user_info_instance, device_id=device_id).first()
        if not bind_info_instance:
            return JsonResponse({"status": "failed", "message": "Device not found"}, status=404)
        bind_info_instance.delete()
        return JsonResponse({"status": "success", "message": "Device unbound successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "failed", "message": str(e)}, status=500)


@login_required
@csrf_exempt
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
        open_id = request.GET.get("open_id")
        if not open_id:
            return JsonResponse({"status": "failed", "message": "Missing openid"}, status=400)
        user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
        if not user_info_instance:
            return JsonResponse({"msg": "User not exists"}, status=404)
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
        return redirect("http://10.117.251.67/?username="+username)
    except Exception as e:
        return JsonResponse({"status": "failed", "message": str(e)}, status=500)
    pass
# todo: 偶尔会有显示两次请求的情况 但是不影响功能


@login_required
@csrf_exempt
def logout(request, device_id):
    if not (request.method == 'POST'):
        return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
    body = demjson3.decode(request.body)
    open_id = body["open_id"]
    if not open_id:
        return JsonResponse({"msg": "Missing open_id parameter"}, status=400)
    user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
    if not user_info_instance:
        return JsonResponse({"msg": "User not exists"}, status=404)
    bind_info_instance = BindInfo.objects.filter(user=user_info_instance, device_id=device_id).first()
    if not bind_info_instance:
        return JsonResponse({"status": "failed", "message": "Device not found"}, status=404)
    bind_info_instance.logged_in = False
    bind_info_instance.save()
    return JsonResponse({"status": "success",
                         "message": "Device logged out successfully"
                         }, status=200)


@login_required
@csrf_exempt
def devices(request):
    if not (request.method == 'GET'):
        return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=405)
    body = demjson3.decode(request.body)
    open_id = body["open_id"]
    if not open_id:
        return JsonResponse({"msg": "Missing open_id parameter"}, status=400)
    user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
    if not user_info_instance:
        return JsonResponse({"msg": "User not exists"}, status=404)
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

