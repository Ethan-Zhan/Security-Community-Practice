from django.http import JsonResponse
from bind.models import BindInfo
from utils.token import bind_token_generate, bind_token_pass, bind_get_user_info
from utils.security import current_user, error_response, get_request_ip, parse_json_body, server_error_response
from django.contrib.auth.decorators import login_required


@login_required
def bind(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"msg": "Method not allowed"}, status=405)
        user_info_instance = current_user(request)
        user_ip = get_request_ip(request)
        if not user_ip:
            return error_response("Unable to determine client IP", status=400)
        if BindInfo.objects.filter(user=user_info_instance, ip=user_ip).exists():
            return JsonResponse({"status": "failed", "msg": "Device already bound."}, status=409)
        last_device = BindInfo.objects.filter(user=user_info_instance).order_by('-device_id').first()
        device_id = last_device.device_id + 1 if last_device else 1
        bind_info = BindInfo(user=user_info_instance, ip=user_ip, device_id=device_id)
        bind_token = bind_token_generate(bind_info)
        return JsonResponse({"status": "success", "token": bind_token}, status=200)
    except Exception as e:
        return server_error_response(e, "bind")


@login_required
def verify(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"msg": "Method not allowed"}, status=405)
        body = parse_json_body(request)
        if body is None:
            return error_response("Invalid JSON body", status=400)
        token = body.get("token")
        if not token:
            return JsonResponse({"msg": "token not found"}, status=401)
        token = bind_token_pass({"token": token})
        bind_user_info = bind_get_user_info(token)
        user_info_instance = current_user(request)
        if bind_user_info.get('open_id') != user_info_instance.open_id:
            return error_response("Token owner mismatch", status=403)
        given_user_ip = bind_user_info.get('ip')
        user_ip = get_request_ip(request)
        if given_user_ip != user_ip:
            return JsonResponse({"msg": "Invalid device"}, status=401)
        if BindInfo.objects.filter(user=user_info_instance, ip=user_ip).exists():
            return JsonResponse({"status": "failed", "msg": "Device already bound."}, status=409)
        last_device = BindInfo.objects.filter(user=user_info_instance).order_by('-device_id').first()
        device_id = last_device.device_id + 1 if last_device else 1
        BindInfo.objects.create(user=user_info_instance, ip=user_ip, device_id=device_id)
        return JsonResponse({"status": "success",
                             "msg": "Device bound successfully",
                             "device_id": device_id}, status=200)
    except Exception as e:
        return server_error_response(e, "verify")
