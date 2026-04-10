from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.conf import settings
from utils.feishu_token import call_app_access_token, call_user_access_token, get_user_info
import urllib.parse
from .forms import UserInfoForm
from .models import UserInfo
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import uuid


@csrf_exempt
def feishu_redirect(request):
    try:
        if request.method == 'GET':
            state = str(uuid.uuid4())
            request.session['oauth_state'] = state
            base_url = "https://open.feishu.cn/open-apis/authen/v1/index"
            params = {
                "app_id": settings.FEISHU_APP_ID,
                "redirect_uri": settings.FEISHU_REDIRECT_URI,
                "state": state
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            return redirect(url)
        else:
            return JsonResponse({"msg": "Method not allowed"}, status=405)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)


@csrf_exempt
def callback(request):
    try:
        if request.method == 'GET':
            code = request.GET.get('code')
            state = request.GET.get('state')
            saved_state = request.session.get('oauth_state')
            if state == saved_state:
                if code:
                    app_access_token = call_app_access_token()
                    user_data_json = call_user_access_token(app_access_token, code)
                    user_access_token = user_data_json.get("access_token")
                    if user_access_token:
                        refresh_token = user_data_json.get("refresh_token")
                        user_info = get_user_info(user_access_token)
                        open_id = user_info.get("open_id")
                        if open_id:
                            user_info_instance = UserInfo.objects.filter(open_id=open_id).first()
                            if user_info_instance:
                                user_info_form = UserInfoForm(user_info, instance=user_info_instance)
                            else:
                                user_info_form = UserInfoForm(user_info)

                            if user_info_form.is_valid():
                                user_info_form.save()
                                login(request, user_info_instance)
                            else:
                                return JsonResponse({"msg": "Invalid user info"}, status=400)
                        return JsonResponse({"message": "Login successful",
                                             "user_info": user_info,
                                             "user_access_token": user_access_token})
                    else:
                        return JsonResponse({"msg": "Invalid user access token"}, status=400)
                else:
                    return JsonResponse({"msg": "Missing code parameter"}, status=400)
            else:
                return JsonResponse({"msg": "Invalid state parameter"}, status=400)
        else:
            return JsonResponse({"msg": "Method not allowed"}, status=405)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)


@login_required
@csrf_exempt
def feishu_logout(request):
    try:
        if request.method == 'GET':
            logout(request)
            return JsonResponse({"message": "Logout successful"})
        else:
            return JsonResponse({"msg": "Method not allowed"}, status=405)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)
