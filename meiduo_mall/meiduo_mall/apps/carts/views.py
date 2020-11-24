from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection
import json
from meiduo_mall.utils.cookiesecret import CookieSecret
from goods.models import SKU
# Create your views here.

class CartsView(View):

    # 添加购物车
    def post(self, request):
        # 1、提取参数
        user = request.user # 登陆用户 或 匿名用户
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id') # 1
        count = data.get('count')
        selected = data.get('selected', True)
        # 2、校验参数
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})

        # 3、业务数据处理 —— 记录用户登陆或未登陆购物车数据
        if user.is_authenticated:
            # 3.1、用户已登陆
            conn = get_redis_connection('carts') # 5号
            # (1)、提取原有redis购物车数据
            # redis_carts = {b"1": b"5", b"2": b"10"}
            redis_carts = conn.hgetall('carts_%s'%user.id)
            # redis_selected = [b"1", b"2"] 表示1和2商品被选中
            redis_selected = conn.smembers('selected_%s'%user.id)
            # (2)、构建最新的购物车数据 —— 存在则count累加，选中状态以最新为准
            # (3)、把新的购物车数据写入redis
            if str(sku_id).encode() in redis_carts:
                #  sku_id = 1
                #  str(sku_id) = '1'
                #  str(sku_id).encode() = b'1'
                # 当前sku_id商品在redis购物车中
                #  str(sku_id).encode() = b'1'
                #  redis_carts[b'1'] = b"5"
                #  int(redis_carts[str(sku_id).encode()]) = int(b"5") = 5
                count = count + int(redis_carts[str(sku_id).encode()])
                conn.hset('carts_%s'%user.id, sku_id, count)
            else:
                conn.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                # 被选中，需要把sku_id加入集合中
                conn.sadd('selected_%s'%user.id, sku_id)
            else:
                # 被取消选中，需要把sku_id从集合中去除
                conn.srem('selected_%s'%user.id, sku_id)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            # 3.2、用户未登陆 —— 存储cookie购物车
            # (1)、提取原有cookie购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 原有cookie购物车数据存在,解码
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
            # (2)、构建最新的购物车数据 ——  判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
            if sku_id in cart_dict:
                # 如果当前sku_id商品在原有购物车中，则count累加;选中状态selected以最新的为准
                cart_dict[sku_id]['count'] += count
                cart_dict[sku_id]['selected'] = selected
            else:
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            # (3)、把最新的购物车字典数据写入cookie中
            cart_str = CookieSecret.dumps(cart_dict)
            # 4、构建响应
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', cart_str, max_age=24 * 30 * 3600)
            return response

    # 展示购物车
    def get(self, request):
        # 1、提取参数
        user = request.user
        # 2、校验参数
        # 3、业务数据处理 —— 读取购物车数据，在从mysql读取详细信息
        # cart_dict = {1: {"count": 5, "selected": True}}
        cart_dict = {} # 准备一个空字典来保存购物车数据
        if user.is_authenticated:
            # 登陆
            conn = get_redis_connection('carts')
            # redis_carts = {b'1': b'5'}
            redis_carts = conn.hgetall('carts_%s'%user.id)
            # redis_selected = [b'1']
            redis_selected = conn.smembers('selected_%s'%user.id)
            for k,v in redis_carts.items():
                # k = b'1'; v = b'5'
                sku_id = int(k)
                count = int(v)
                cart_dict[sku_id] = {
                    "count": count,
                    "selected": k in redis_selected # b'1' in [b'1']
                }
        else:
            # 未登陆 —— 从cookie中读取购物车字典数据
            cart_str = request.COOKIES.get('carts') # 'HNJBHBHBHUBRRGEbhjgbrbBHBGHYUbg'
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)

        # 4、构建响应
        # cart_dict = {1: {"count": 5, "selected": True}}
        cart_skus = []
        sku_ids = cart_dict.keys() # [1]
        for sku_id in sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'count': cart_dict[sku_id]['count'],
                'selected': cart_dict[sku_id]['selected']
            })

        return JsonResponse({'code': 0,'errmsg': 'ok', 'cart_skus': cart_skus})

    # 修改购物车
    def put(self, request):
        # 1、提取参数
        user = request.user  # 登陆用户 或 匿名用户
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)
        # 2、校验参数
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})

        # 3、业务数据处理 —— 更新redis或cookie购物车数据
        if user.is_authenticated:
            # 登陆，更新redis
            conn = get_redis_connection('carts')
            # (1)、更新redis购物车的商品数量
            conn.hset('carts_%s'%user.id, sku_id, count)
            # (2)、更新redis购物车的选中状态
            if selected:
                conn.sadd('selected_%s'%user.id, sku_id)
            else:
                conn.srem('selected_%s'%user.id, sku_id)
            sku = SKU.objects.get(pk=sku_id)
            # 4、构建响应
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'cart_sku': {
                    'id': sku.id,
                    'count': count,
                    'selected': selected,
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': sku.price,
                    'amount': sku.price * count
                }
            })
            return response
        else:
            # 未登陆，更新cookie
            # (1)、读取cookie购物车字典数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
            # (2)、更新覆盖原有数据
            if sku_id in cart_dict:
                cart_dict[sku_id]['count'] = count
                cart_dict[sku_id]['selected'] = selected

            # (3)、最新数据写入cookie
            cart_str = CookieSecret.dumps(cart_dict)
            sku = SKU.objects.get(pk=sku_id)
            # 4、构建响应
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'cart_sku': {
                    'id': sku.id,
                    'count': cart_dict[sku_id]['count'],
                    'selected': cart_dict[sku_id]['selected'],
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': sku.price,
                    'amount': sku.price * cart_dict[sku_id]['count']
                }
            })
            response.set_cookie('carts', cart_str, max_age=24 * 3600 * 30)
            return response

    # 删除购物车
    def delete(self, request):
        # 1、提取参数
        user = request.user
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        # 2、校验参数
        if not sku_id:
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        # 3、业务数据处理 —— 删除redis或cookie购物车
        if user.is_authenticated:
            # 登陆，删除redis购物车商品
            conn = get_redis_connection('carts')
            # (1)、删除商品和数量
            conn.hdel('carts_%s'%user.id, sku_id)
            # (2)、删除选中状态
            conn.srem('selected_%s'%user.id, sku_id)
            # 4、构建响应
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            # 未登陆，删除cookie购物车商品 —— 删除购物车中的某一个商品
            # (1)、读取cookie购物车字典
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
            # (2)、删除购物车字典中的sku_id
            if sku_id in cart_dict:
                cart_dict.pop(sku_id)

            # (3)、把新的购物车字典数据加密写入cookie
            cart_str = CookieSecret.dumps(cart_dict)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', cart_str, max_age=24 * 3600 * 30)
            return response


# 全选或取消全选接口
class CartsSelectAllView(View):

    def put(self, request):
        # 1、提取参数
        user = request.user
        data = json.loads(request.body.decode())
        selected = data.get('selected') # None
        # 2、校验参数
        if not isinstance(selected, bool): # 布尔类型对象，只有2个值：True 或 False
            return JsonResponse({'code': 400, 'errmsg': '参数有误'})

        # 3、业务数据处理 —— 登陆，把redis购物车设置全选或取消；未登陆把Cookie购物车设置全选或取消；
        if user.is_authenticated:
            conn = get_redis_connection('carts')
            # (1)、获取redis购物车商品数据
            # redis_carts = {b'1': b'5', b'2' : b'15'}
            redis_carts = conn.hgetall('carts_%s'%user.id)
            # (2)、把全部sku_id加入集合或从集合中去除
            sku_ids = redis_carts.keys() # [b'1', b'2']
            if selected:
                # 全部sku_id加入集合
                conn.sadd('selected_%s'%user.id, *sku_ids) # sadd('selected_%s'%user.id, b'1', b'2')
            else:
                # 全部从集合中去除
                conn.srem('selected_%s'%user.id, *sku_ids)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            return response
        else:
            # (1)、提取cookie购物车字典数据
            cart_str = request.COOKIES.get('carts')
            # cart_dict = {1:{"count":5, "selected":True}}
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
            # (2)、设置全选或取消
            sku_ids = cart_dict.keys()
            for sku_id in sku_ids:
                cart_dict[sku_id]['selected'] = selected
            # (3)、把新购物车字典写入cookie
            cart_str = CookieSecret.dumps(cart_dict)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', cart_str, max_age=30 * 24 * 3600)
            return response



# 主页购物车简图
class CartsSimpleView(View):

    def get(self, request):
        # 业务数据处理
        user = request.user
        # 先定义一个字典，用于记录后续redis购物车数据或cookie购物车数据
        cart_dict = {} # {1: {"count": 5, "selected": True}}
        if user.is_authenticated:
            # 读取redis
            conn = get_redis_connection('carts')
            # redis_cart = {b'1': b'5', b'2': b''10'}
            redis_cart = conn.hgetall('carts_%s'%user.id)
            # redis_selected = [b'1', b'2']
            redis_selected = conn.smembers('selected_%s'%user.id)
            for sku_id in redis_selected:
                # sku_id = b'1'
                cart_dict[int(sku_id)] = {
                    'count': int(redis_cart[sku_id]),
                    'selected': sku_id in redis_selected
                }
        else:
            # 读取cookie
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}

            new_cart_dict = {} # 存储已勾选的商品
            sku_ids = cart_dict.keys() # [1,2,3,4,5]
            for sku_id in sku_ids:
                if cart_dict[sku_id]['selected']:
                    new_cart_dict[sku_id] = {
                        'count': cart_dict[sku_id]['count'],
                        'selected': cart_dict[sku_id]['selected']
                    }
            cart_dict = new_cart_dict


        # 根据cart_dict，去读取mysql商品详细信息，构建响应
        sku_ids = cart_dict.keys()
        cart_skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict[sku_id]['count'],
                'default_image_url': sku.default_image.url
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})


