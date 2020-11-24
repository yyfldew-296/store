from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache

from .models import Area
# Create your views here.

# 获取省级行政区
class ProvinceAreasView(View):

    def get(self, request):
        # 1、提取参数
        # 2、校验参数
        # 3、业务数据处理 —— 查询省级行政区，并且转化成列表套字典
        # provinces是一个查询集

        # ========(1)、通读策略之"先读缓存，读到则直接构建响应"========
        province_list = cache.get('province_list') # 如果缓存数据存在返回列表，否则返回None
        if province_list:
            return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'province_list': province_list
        })

        # ========(2)、通读策略之"读mysql"========
        try:
            provinces = Area.objects.filter(
                parent=None
            )
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库错误'})

        province_list = []
        for province in provinces:
            province_list.append({
                'id': province.id,
                'name': province.name
            })

        # ========(3)、通读策略之"缓存回填"========
        # 缓存时间设置为3600秒，目的：一定程度上可以实现"缓存弱一致"
        cache.set('province_list', province_list, 3600)

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'province_list': province_list
        })


# 获取市、区信息
class SubAreasView(View):

    def get(self, request, pk):
        # 1、提取参数
        # 2、校验参数
        # 3、业务数据处理 —— 根据路径pk主键值，过滤出子级行政区数据

        # ========(1)、通读策略之"读缓存，命中直接构建响应返回"=========
        sub_data = cache.get('sub_area_'+pk)
        if sub_data:
            return JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'sub_data': sub_data
            })

        # ========(2)、通读策略之"读mysql"=========
        try:
            parent_area = Area.objects.get(pk=pk)
            # sub_areas = Area.objects.filter(parent=parent_area)
            sub_areas = Area.objects.filter(parent_id=pk)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库错误'})

        sub_list = []
        for sub in sub_areas:
            # sub：子级行政区对象
            sub_list.append({
                'id': sub.id,
                'name': sub.name
            })

        # 缓存数据
        sub_data = {
                'id': parent_area.id,
                'name': parent_area.name,
                'subs': sub_list
        }

        # ========(3)、通读策略之"回填缓存"=========
        # 需要记录的数据是：某一个父级行政区，对应的子级行政区数据
        cache.set('sub_area_'+pk, sub_data, 3600)

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'sub_data': sub_data
        })






