from django.http import JsonResponse
from feishu_auth.models import UserInfo
from bind.models import BindInfo
from utils.ip import get_client_ip
from utils.token import bind_token_generate, bind_token_pass, bind_get_user_info
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import demjson3


@login_required
@csrf_exempt
def bind(request):
    try:
        if request.method == 'POST':
            body = demjson3.decode(request.body)
            open_id = body["open_id"]
            if open_id:
                user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
                if user_info_instance:
                    user_ip = get_client_ip(request)
                    db_ip = BindInfo.objects.filter(user=user_info_instance).values('ip')
                    db_ip_list = list(db_ip.values_list('ip', flat=True))
                    if user_ip in db_ip_list:
                        return JsonResponse({"status": "failed",
                                             "msg": "Device already bound."}, status=200)
                    last_device = BindInfo.objects.filter(user=user_info_instance).order_by('-device_id').first()
                    if last_device:
                        device_id = last_device.device_id + 1
                    else:
                        device_id = 1
                    bind_info = BindInfo(user=user_info_instance, ip=user_ip, device_id=device_id)
                    bind_token = bind_token_generate(bind_info)
                    return JsonResponse({"status": "success",
                                         "token": bind_token
                                         }, status=200)
                else:
                    return JsonResponse({"msg": "User not exists"}, status=404)
            else:
                return JsonResponse({"msg": "Missing open_id parameter"}, status=400)
        else:
            return JsonResponse({"msg": "Method not allowed"}, status=405)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)


@login_required
@csrf_exempt
def verify(request):
    try:
        if request.method == 'POST':
            body = demjson3.decode(request.body)
            token = body["token"]
            if token:
                token = bind_token_pass({"token": token})
                bind_user_info = bind_get_user_info(token)
                open_id = bind_user_info.get('open_id')
                if open_id:
                    user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
                    if user_info_instance:
                        given_user_ip = bind_user_info.get('ip')
                        user_ip = get_client_ip(request)
                        if given_user_ip == user_ip:
                            last_device = BindInfo.objects.filter(user=user_info_instance).order_by(
                                '-device_id').first()
                            db_ip = BindInfo.objects.filter(user=user_info_instance).values('ip')
                            db_ip_list = list(db_ip.values_list('ip', flat=True))
                            if user_ip in db_ip_list:
                                return JsonResponse({"status": "failed",
                                                     "msg": "Device already bound."}, status=200)
                            if last_device:
                                device_id = last_device.device_id + 1
                            else:
                                device_id = 1
                            BindInfo.objects.create(user=user_info_instance, ip=user_ip, device_id=device_id)
                            return JsonResponse({"status": "success",
                                                "msg": "Device bound successfully",
                                                 "device_id": device_id}, status=200)
                        else:
                            return JsonResponse({"msg": "Invalid device"}, status=401)
                    else:
                        return JsonResponse({"msg": "User not exists"}, status=404)
                else:
                    return JsonResponse({"msg": "Missing open_id parameter"}, status=400)

            else:
                return JsonResponse({"msg": "token not found"}, status=401)
        else:
            return JsonResponse({"msg": "Method not allowed"}, status=405)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)
