

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login,logout,authenticate
from django_redis import get_redis_connection
import json,re

from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verify_email_url
from .models import User,Address
from meiduo_mall.utils.secret import SecretOauth
from carts.utils import merge_cart_cookie_to_redis

from goods.models import GoodsVisitCount
# Create your views here.

# 判断用户名是否重复
class UsernameCountView(View):

    def get(self, request, username):
        # 1、提取参数
        # 2、校验参数
        # 3、业务数据处理 —— 根据用户名统计用户数量
        # 捕获一场的原则：针对数据库的写操作，尽可能捕获异常；读操作可以酌情判断需不需要捕获异常；
        try:
            count = User.objects.filter(
                username=username
            ).count()
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'errmsg': '数据库错误！'
            })

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count': count
        })


# 判断手机号是否重复
class MobileCountView(View):

    def get(self, request, mobile):
        # 1、提取参数
        # 2、校验参数
        # 3、业务数据处理
        count = User.objects.filter(
            mobile=mobile
        ).count()
        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count': count
        })


# 用户注册
class RegisterView(View):

    def post(self, request):
        # 1、提取参数
        # request.body # 请求体参数，类型是字节对象 b'{"username": xxx....}'
        data = json.loads(request.body.decode()) # 低版本的python中，loads函数需要传入字符串
        # data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')

        allow = data.get('allow', False)

        # 2、校验参数
        # 2.1、必要性校验
        if not all([username, password, password2, mobile, sms_code]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必要参数',
            }, status=400)
        # 2.2、约束条件校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg': '用户名格式有误',
            }, status=400)

        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误',
            }, status=400)
        # 2次输入密码是否一致
        if password != password2:
            return JsonResponse({
                'code': 400,
                'errmsg': '两次输入密码不一致',
            }, status=400)

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'code': 400,
                'errmsg': '手机号格式有误',
            }, status=400)

        if not re.match(r'^\d{6}$', sms_code):
            return JsonResponse({
                'code': 400,
                'errmsg': '短信验证码格式有误',
            }, status=400)

        if not isinstance(allow, bool):
            return JsonResponse({
                'code': 400,
                'errmsg': 'allow格式有误',
            }, status=400)
        if not allow:
            return JsonResponse({
                'code': 400,
                'errmsg': '请求勾选同意协议'
            })

        # 2.3、业务性校验(短信验证校验)
        # TODO: 此处填充短信验证码校验逻辑代码
        conn = get_redis_connection('verify_code') # 2号
        sms_code_from_redis = conn.get('sms_%s'%mobile) # b"123456"
        if not sms_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码过期'})
        if sms_code != sms_code_from_redis.decode():
            return JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})

        # 3、业务数据处理 —— 新建User模型类对象保存数据库
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '数据库写入失败'
            }, status=500)

        # TODO: 状态保持 —— 使用session机制，把用户数据写入redis
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # 4、构建响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # TODO: 设置cookie，来记录用户名
        response.set_cookie(
            'username',
            username,
            max_age=3600 * 24 * 14
        )
        return response


# 传统登陆
class LoginView(View):

    def post(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        # 2、校验参数
        # 2.1、必要性校验
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        # 2.2、约束校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg': '用户名格式有误',
            }, status=400)

        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误',
            }, status=400)

        # 3、业务数据处理 —— 根据username和password查找用户、校验密码

        # TODO: 修改默认认证后端ModelBackend过滤字段
        """
        if re.match(r'^1[3-9]\d{9}$', username):
            # (1)、如果传入的是手机号，按照mobile字段过滤
            User.USERNAME_FIELD = 'mobile'
        else:
            # (2)、如果传入的是用户名，按照username字段过滤
            User.USERNAME_FIELD = 'username'
        """

        # 功能：传统身份认证
        # 参数：request请求对象，username用户和password密码
        # 返回值：验证成功返回用户对象；失败返回None
        user = authenticate(request, username=username, password=password)
        if not user:
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码错误'})
        """
        # 3.1、根据username查找用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            return JsonResponse({'code': 400, 'errmsg': '用户名错误'})
        # 3.2、检查密码
        if not user.check_password(password):
            return JsonResponse({'code': 400, 'errmsg': '密码错误'})
        """

        # TODO: 状态保持
        login(request, user) # 默认状态保持记录用户数据有效期为2周
        # 需要根据remembered字段，来设置保存用户信息的有效期
        if remembered != True:
            # 关闭浏览器用户登陆状态失效
            request.session.set_expiry(0)
        else:
            # 按照默认的Django有效期2周
            request.session.set_expiry(None)

        # 4、构建响应
        response =  JsonResponse({'code': 0, 'errmsg': 'ok'})
        # TODO: 设置cookie，来记录用户名
        response.set_cookie(
            'username',
            username,
            max_age= 3600 * 24 * 14
        )
        response = merge_cart_cookie_to_redis(request, response)
        return response


# 退出登陆
class LogoutView(View):

    def delete(self, request):
        """
        退出登陆，删除用户登陆信息
        """
        # 1、确定用户身份(当前以登陆的用户)
        # request.user ---> 已登陆的用户模型类对象(User) 或 匿名用户对象(AnonymousUser)
        # 2、删除该用户的session登陆数据，清除该用户的登陆状态
        logout(request) # 通过request对象获取用户信息，然后在去清除session数据

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response

# LoginRequiredMixin视图拓展类——拓展视图功能
# from django.contrib.auth.mixins import LoginRequiredMixin
from meiduo_mall.utils.views import LoginRequiredJsonMixin
# 用户中心接口 —— 获取当前登陆用户信息
class UserInfoView(LoginRequiredJsonMixin, View):

    def get(self, request):
        # 1、获取已经"登陆"的用户
        user = request.user
        # 2、判断用户是否已经登陆，如果没有登陆(匿名用户)返回错误
        # user.is_authenticated，用户对象有一个属性is_authenticated；
        # (1)、如果该user是一个AnonymousUser匿名用户对象，则is_authenticated为False
        # (2)、如果该user是一个User用户对象，则is_authenticated为True
        # if not user.is_authenticated:
        #     return JsonResponse({'code': 400, 'errmsg': '未登陆！'})

        # 3、如果是User对象，构建响应，返回用户信息
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'info_data': {
                'username': user.username,
                'mobile': user.mobile,
                'email': user.email,
                'email_active': user.email_active
            }
        })

# 添加邮箱接口
class EmailView(LoginRequiredJsonMixin, View):

    def put(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        email = data.get('email')
        # 2、校验参数
        if not email:
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            return JsonResponse({'code': 400, 'errmsg': '邮箱格式有误'})
        # 3、业务数据处理 —— 修改email属性，和发送验证邮件
        user = request.user
        user.email = email
        user.save()
        # TODO: 发送验证邮件
        # verify_url分为2个部分：
        # (1)、固定的验证请求前缀：http://www.meiduo.site:8080/success_verify_email.html?token=
        # (2)、查询字符串参数： ?token=<是一个字符串，该字符串是加密后的用户数据>
        # 需要生成记录当前登陆用户信息的token，作为verify_url查询字符串的拼接
        verify_url = generate_verify_email_url(request)
        send_verify_email.delay(email, verify_url=verify_url)

        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

# 验证邮箱
class VerifyEmailView(View):

    def put(self, request):
        # 1、提取参数
        token = request.GET.get('token')
        # 2、校验参数
        if not token:
            return JsonResponse({'code': 400, 'errmsg': '缺少token'})
        # 3、业务数据处理 —— 解密token值(解密成功则验证邮箱成功；否则验证失败)
        # 3.1、验证token，获取用户信息
        auth = SecretOauth()
        # user_info = {"user_id": 11, "email": "2335490692@qq.com"}
        user_info = auth.loads(token)
        if user_info is None:
            return JsonResponse({'code': 400, 'errmsg': 'token无效'})
        user_id = user_info.get('user_id')
        email = user_info.get('email')
        # 3.2、激活邮件 —— 把email_active设置为True
        try:
            user = User.objects.get(pk=user_id)
            user.email_active = True
            user.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '激活失败'})
        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 新增用户收货地址
class CreateAddressView(LoginRequiredJsonMixin, View):

    def post(self, request):
        # TODO: 我们限制用户新建收货地址最多不超过20个
        user = request.user
        count = Address.objects.filter(
            user=user, is_deleted=False
        ).count()
        if count >= 20:
            return JsonResponse({'code': 400, 'errmsg': '最多可以创建20个收货地址'})

        # 1、提取参数
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2、校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^\w{1,20}$', receiver):
            return JsonResponse({'code': 400, 'errmsg': '参数receiver有误'})

        if not re.match(r'^\w{1,50}$', place):
            return JsonResponse({'code': 400, 'errmsg': '参数place有误'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^\w{1,20}$', tel):
                return JsonResponse({'code': 400, 'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
                return JsonResponse({'code': 400, 'errmsg': '参数email有误'})
            if len(email) > 30:
                return JsonResponse({'code': 400, 'errmsg': '邮箱长度有误'})

        # 3、业务数据处理 —— 新建Address模型类对象保存数据
        try:
            address = Address.objects.create(
                user=user, # 当前新增地址从属用户
                title=receiver, # 新增的时候把收件人名称作为默认地址标题
                receiver=receiver, # 收货人别名
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                # tel=tel if tel else ""
                tel=tel or "",
                email=email or ""
            )
            # TODO: 如果当前登陆用户没有设置默认地址，把当前新增的地址作为其默认地
            if not user.default_address:
                user.default_address = address
                user.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库写入错误'})

        # 4、构建响应
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name, # 省名称
            "city": address.city.name, # 市名称
            "district": address.district.name, # 区名称
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return JsonResponse({
            'code': 0,
            'errmsg': '新增地址成功',
            'address': address_dict
        })


# 展示用户收货地址
class AddressView(LoginRequiredJsonMixin, View):

    def get(self, request):
        # 1、提取参数
        user = request.user
        # 2、校验参数
        # 3、业务数据处理——获取用户的地址
        address_queryset = Address.objects.filter(
            user=user, is_deleted=False
        )
        addresses = []
        for address in address_queryset:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name, # 省名称
                "city": address.city.name, # 市名称
                "district": address.district.name, # 区名称
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            if address.id == user.default_address_id:
                # 当前地址是用户默认地址，需要把这个地址插入列表头
                addresses.insert(0, address_dict)
            else:
                addresses.append(address_dict)

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'default_address_id': user.default_address_id,
            'addresses': addresses
        })


class UpdateDestroyAddressView(LoginRequiredJsonMixin, View):

    # 修改用户收货地址
    def put(self, request, address_id):
        # 1、提取参数
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2、校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^\w{1,20}$', receiver):
            return JsonResponse({'code': 400, 'errmsg': '参数receiver有误'})

        if not re.match(r'^\w{1,50}$', place):
            return JsonResponse({'code': 400, 'errmsg': '参数place有误'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^\w{1,20}$', tel):
                return JsonResponse({'code': 400, 'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
                return JsonResponse({'code': 400, 'errmsg': '参数email有误'})
            if len(email) > 30:
                return JsonResponse({'code': 400, 'errmsg': '邮箱长度有误'})

        # 3、业务数据处理 —— 更新模型类数据
        try:
            address = Address.objects.get(pk=address_id)

            address.receiver = receiver
            address.province_id = province_id
            address.city_id = city_id
            address.district_id = district_id
            address.place = place
            address.mobile = mobile
            address.tel = tel or ""
            address.email = email or ""

            address.save()  # 写入数据库

        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '未找到地址'})

        # 4、构建响应
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': address_dict
        })

    # 逻辑删除用户地址
    def delete(self, request, address_id):
        # 1、提取参数
        user = request.user
        # 2、校验参数
        # 3、业务数据处理 —— 把当前地址的is_deleted属性设置True,表示逻辑删除
        try:
            address = Address.objects.get(pk=address_id)
            # 逻辑删除
            address.is_deleted = True
            address.save()
            # 如果删除的地址刚好是用户的默认地址，需要把用户默认地址设置为None
            if address.id == user.default_address_id:
                user.default_address = None
                user.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库错误'})

        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 设置默认地址
class DefaultAddressView(LoginRequiredJsonMixin, View):

    def put(self, request, address_id):
        # 1、提取参数
        user = request.user
        # 2、校验参数
        # 3、业务数据处理 —— 把用户的默认地址设置为address_id地址
        try:
            address = Address.objects.get(pk=address_id, is_deleted=False)
            user.default_address = address
            # user.default_address_id = address_id
            user.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库错误'})
        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 设置地址标题
class UpdateTitleAddressView(LoginRequiredJsonMixin, View):

    def put(self, request, address_id):
        # 1、提取参数
        user = request.user
        data = json.loads(request.body.decode())
        title = data.get('title')

        # 2、校验参数
        if not title:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        if len(title) > 20:
            return JsonResponse({'code': 400, 'errmsg': '参数有误'})

        # 3、业务数据处理 —— 更新地址的title字段
        try:
            address = Address.objects.get(pk=address_id, is_deleted=False)
            address.title = title
            address.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库错误'})

        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 修改密码
class ChangePasswordView(LoginRequiredJsonMixin, View):

    def put(self, request):
        # 1、提取参数
        user = request.user
        data = json.loads(request.body.decode())
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')
        # 2、校验参数
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})

        # 新密码格式是否一致
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code': 400,
                                      'errmsg': '密码最少8位,最长20位'})
        # 两次数据是否一致
        if new_password != new_password2:
            return JsonResponse({'code': 400,
                                      'errmsg': '两次输入密码不一致'})

        # TODO: 旧密码是否输入正确
        # old_password = "chaunzhi12345" ———> 明文
        if not user.check_password(old_password):
            return JsonResponse({'code': 400, 'errmsg': '密码输入有误！'})

        # 3、业务数据处理 —— 修改密码(重置密码)
        # user.password = new_password --> 不行，直接赋值是明文，所以不行！
        user.set_password(new_password)
        user.save()

        # TODO: 修改密码之后，需要清除一切状态保持数据
        logout(request)
        # 4、构建响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response


from goods.models import SKU


# 用户浏览历史记录
class UserBrowseHistory(LoginRequiredJsonMixin, View):
    # 用户浏览历史记录
    def post(self, request):
        # 1、提取参数
        user = request.user
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        # 2、校验参数
        try:
            sku = SKU.objects.get(pk=sku_id, is_launched=True)
        except Exception as e:
            # 如果sku商品不存在或以下架，则不记录历史
            return JsonResponse({'code': 0, 'errmsg': 'ok'})

        # 3、业务数据处理 —— 历史记录写redis
        # history_1 : [1,2,3,4,5]
        conn = get_redis_connection('history') # 3号
        p = conn.pipeline()
        # (1)、去重
        p.lrem('history_%s'%user.id, 0, sku_id)
        # (2)、左侧插入
        p.lpush('history_%s'%user.id, sku_id)
        # (3)、截断
        p.ltrim('history_%s'%user.id, 0, 4)
        p.execute()


        # TODO：记录该商品分类访问量
        category = sku.category

        cur_0_time = timezone.localtime().replace(hour=0,second=0,minute=0)

        try:
            cate_visit = GoodsVisitCount.objects.get(
                category=category,
                create_time__gte=cur_0_time
            )
        except GoodsVisitCount.DoesNotExist as e:

            cate_visit = GoodsVisitCount.objects.create(
                count = 1,
                category = category
            )
        else:
            cate_visit.count += 1
            cate_visit.save()

        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})






    # 查询历史记录
    def get(self, request):
        # 1、提取参数
        user = request.user
        # 2、校验参数
        # 3、业务处理 —— 从redis读历史记录，在从mysql读详细信息
        # 3.1、读取redis历史(访问的sku_id)
        conn = get_redis_connection('history') # 3号
        # data = [b'1', b'2', b'3'];注意：redis客户端读取的字符数据全部都是字节形式
        sku_ids = conn.lrange('history_%s'%user.id, 0, -1)
        # 3.2、读取mysql商品详细信息
        # django模型类根据主键过滤的时候，主键可以直接传递整数、字符或者字节
        skus = SKU.objects.filter(
            # 过滤出id，包含在sku_ids列表中的所有对象
            # id 在 [b'1', b'2', b'3'...]
            id__in=sku_ids
        )
        sku_list = []
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg':'ok', 'skus': sku_list})

















