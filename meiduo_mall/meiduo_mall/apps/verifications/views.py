from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse
# get_redis_connection("verify_code")
# 功能：获取一个redis的连接对象
# 参数：django缓存配置选项
# 返回值：连接对象
from django_redis import get_redis_connection

from verifications.libs.captcha.captcha import captcha
# from verifications.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import ccp_send_sms_code
import re,random
# Create your views here.

# 获取图形验证码接口
class ImageCodeView(View):

    def get(self, request, uuid):
        # 1、提取参数
        # 2、校验参数
        # 3、业务数据处理
        # 3.1、调用captcha生成验证码图片
        # text: 验证码，类型是字符串
        # image: 图片数据，类型是字节
        text, image = captcha.generate_captcha()
        # 3.2、验证码text存入redis(以uuid作为key)
        # set img_<uuid> <text>
        # 获取django缓存配置项"verify_code"
        try:
            conn = get_redis_connection('verify_code') # 2号库
            # conn.set("键", "值")
            # conn.set("img_%s"%uuid, text)
            conn.setex("img_%s"%uuid, 300, text)
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 400,
                'errmsg': 'redis写入图形验证码失败'
            }, status=500)

        # 3.3、返回图片image
        # 4、构建响应
        return HttpResponse(image, content_type='image/jpeg')


# 发送短信验证码接口
class SMSCodeView(View):

    def get(self, request, mobile):
        # 1、提取参数
        # sms_codes/18588269037/?image_code=BHGJ&image_code_id=gerg-gtrhy-hybgby-yt6hhu
        image_code = request.GET.get('image_code') # 用户填写的图片验证码
        uuid = request.GET.get('image_code_id') # 用户图形验证码的uuid
        # 2、校验参数
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必要参数'})
        if not re.match(r'^[a-zA-Z0-9]{4}$', image_code):
            return JsonResponse({'code': 400, 'errmsg': '图形验证码格式有误'})
        if not re.match(r'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$', uuid):
            return JsonResponse({'code': 400, 'errmsg': 'uuid格式有误'})

        # 图形验证码校验 —— 根据uuid获取redis中的图形验证码，和用户填写的比对
        conn = get_redis_connection('verify_code') # 2号
        text = conn.get('img_%s'%uuid) # b"TYUP", redis客户端读取返回的数据统一是"字节"类型
        # TODO: 为了保证图片验证码之后被使用一次，只需要读一次立刻删除
        conn.delete('img_%s'%uuid)
        if not text:
            # 如果图形验证码过期，text返回为空
            return JsonResponse({'code': 400, 'errmsg': '图形验证码过期或已被使用过，请刷新'})
        #  b"YUPO".decode() --> "YUPO"
        if image_code.lower() != text.decode().lower(): # 统一转化小写对比，意味着忽略大小写
            return JsonResponse({'code': 400, 'errmsg': '图形验证码错误！'})

        # 3、业务数据处理 —— 发送短信
        # TODO: 发送短信之前校验标志信息存在否与
        flag = conn.get('send_flag_%s'%mobile)
        if flag:
            # flag存在则说明60秒之内发送过短信
            return JsonResponse({'code': 400, 'errmsg': '请勿频繁发送短信'})

        # 生成固定6位数长度的0-9字符组成的验证码
        sms_code = "%06d" % random.randrange(0, 999999)
        print('短信：', sms_code)
        # 3.1、把短信验证码写入redis
        """
        conn.setex('sms_%s'%mobile, 300, sms_code)
        # TODO: 成功发送短信之后，需要写入标志信息
        conn.setex('send_flag_%s' % mobile, 60, 1)
        """
        # TODO: 使用redis的pipeline功能，把多个redis指令打包批量发送并执行
        # (1)、获取redis的pipeline对象
        p = conn.pipeline()
        # (2)、使用pipeline对象方法实现调用指令
        p.setex('sms_%s' % mobile, 300, sms_code) # 此处不会通信，而是把setex指令放入管道中(加入队列)
        p.setex('send_flag_%s' % mobile, 60, 1)
        # (3)、提交pipeline把指令通过一次网络通信发送给redis执行
        p.execute() # 此处会真正发生网络通信，一次性把所有队列中的指令发送给redis服务器

        # 3.2、发送短信
        # ccp = CCP()
        # ccp.send_template_sms(
        #     mobile,
        #     [sms_code, 5],
        #     1
        # )
        # TODO: 使用异步方式发送短信
        ccp_send_sms_code.delay(mobile, sms_code)

        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})








