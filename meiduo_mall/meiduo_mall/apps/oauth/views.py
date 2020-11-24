from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login
from django_redis import get_redis_connection
from QQLoginTool.QQtool import OAuthQQ

import json,re

from meiduo_mall.utils.secret import SecretOauth
from .models import OAuthQQUser
from users.models import User
from carts.utils import merge_cart_cookie_to_redis
# Create your views here.


# 接口1：获取QQ扫码url
class QQURLView(View):

    def get(self, request):
        # 1、提取参数
        next = request.GET.get('next')
        # 2、校验参数
        # 3、业务数据处理 —— 获取扫码url
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next
        )
        login_url = oauth.get_qq_url()
        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'login_url': login_url
        })


class QQUserView(View):
    # 接口2：获取openid
    def get(self, request):
        # 1、提取参数
        code = request.GET.get('code')
        # 2、校验参数
        # 3、业务数据处理 —— 获取openid
        try:
            # 3.1、获取OAuth对象
            oauth = OAuthQQ(
                client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI,
                state="/"
            )
            # 3.2、获取access_token
            access_token = oauth.get_access_token(code)
            # 3.3、获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '用户qq身份验证失败！'})

        # TODO: 判断用户是否绑定QQ账号 —— 把用户的美多账号和QQ的账号绑定
        try:
            qq_user = OAuthQQUser.objects.get(
                openid=openid
            )
        except OAuthQQUser.DoesNotExist as e:
            # 构建响应(未绑定) —— 需要把openid加密返回给前端
            # 加密openid
            auth = SecretOauth()
            access_token = auth.dumps({'openid':  openid})
            return JsonResponse({
                'code': 300,
                'errmsg': 'ok',
                'access_token': access_token
                # 'access_token': <加密后的openid>
            })
        else:
            # 构建响应(绑定过)
            login(request, qq_user.user)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('username', qq_user.user.username, max_age=14*24*60)
            response = merge_cart_cookie_to_redis(request, response)
            return response

    # 接口3：绑定QQ
    def post(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')
        # 2、校验参数
        # 2.1、必要性校验
        if not all([mobile, password, sms_code, access_token]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        # 2.2、约束校验
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': 'mobile格式有误'})
        if not re.match(r'^[0-9a-zA-Z_]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': 'password格式有误'})
        if not re.match(r'^\d{6}$', sms_code):
            return JsonResponse({'code': 400, 'errmsg': 'sms_code格式有误'})
        # 2.3、业务性校验 —— 短信验证码
        conn = get_redis_connection('verify_code') # 2号
        sms_code_from_redis = conn.get('sms_%s'%mobile) # 返回验证码或None
        if not sms_code_from_redis:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码过期'})
        if sms_code != sms_code_from_redis.decode():
            return JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})

        # 3、业务数据处理 —— 绑定QQ(把用户美多账号和openid绑定)
        # 3.1、获取openid
        auth = SecretOauth()
        content_dict = auth.loads(access_token) # {"openid": "dfregtrgtrh"}
        if content_dict is None:
            return JsonResponse({'code': 400, 'errmsg': 'access_token无效！'})
        openid = content_dict.get('openid')
        # 3.2、根据手机号查找用户
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            # 根据手机号找不到 —— 用户未注册美多账号
            # 新建美多账号
            user = User.objects.create_user(
                username=mobile,
                mobile=mobile,
                password=password
            )
            # 绑定QQ
            OAuthQQUser.objects.create(
                user=user,  # 当前已注册的美多账号
                openid=openid  # 对应的QQ身份
            )
        else:
            # 根据手机号找到用户 —— 用户已注册美多账号
            # 验证用户密码
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '密码有误'})
            # 直接绑定QQ
            OAuthQQUser.objects.create(
                user=user, # 当前已注册的美多账号
                openid=openid # 对应的QQ身份
            )

        # 4、构建响应
        login(request, user)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=14*3600*24)
        response = merge_cart_cookie_to_redis(request, response)
        return response











