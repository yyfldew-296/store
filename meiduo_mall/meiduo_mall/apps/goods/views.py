from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
# Paginator是一个分页器对象
# EmptyPage是一个异常表示空页
from django.core.paginator import Paginator, EmptyPage
from .models import SKU
from .utils import get_breadcrumb
# Create your views here.

# 商品列表信息返回
class ListView(View):

    def get(self, request, category_id):
        # 1、提取参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')
        # 2、校验参数
        # 3、业务数据处理 —— 根据分类过滤sku商品，排序分页返回
        # 3.1、过滤加排序
        skus = SKU.objects.filter(
            category_id=category_id
        ).order_by(ordering) # order_by("-create_time")
        # 3.2、分页
        # (1)、获取分页器对象
        # Paginator：第一个参数是被分页的查询集；第二个参数是每页几个划分
        paginator = Paginator(skus, page_size)
        # page_skus也是一个查询集，是分页之后取得的当前页数据查询集
        try:
            # (2)、找对象的方法获取所需的页数据
            page_skus = paginator.page(page)
        except EmptyPage as e:
            return JsonResponse({'code': 400, 'errmsg': '页面不存在'})
        # 4、构建响应
        data_list = []
        for sku in page_skus:
            data_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        # 分页器对象中属性num_pages，总页数
        total_page = paginator.num_pages
        breadcrumb = get_breadcrumb(category_id)

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'list': data_list,
            'count': total_page,
            'breadcrumb': breadcrumb
        })


# 热销前2数据返回
class HotGoodsView(View):

    def get(self, request, category_id):
        # 1、提取参数
        # 2、校验参数
        # 3、业务数据处理 —— 按照销量排序取前2
        skus = SKU.objects.filter(
            category_id=category_id,
            is_launched=True # 已上架
        ).order_by('-sales')
        # 取销量前2
        hot_skus_queryset = skus[:2]
        hot_skus = []
        for sku in hot_skus_queryset:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'hot_skus': hot_skus
        })


# from haystack.views import SearchView
# # 搜索sku商品
# class MySearchView(SearchView):
#     # 该视图中默认已经提供了一个get方法响应GET请求，并且已经实现了根据q参数检索数据
#     # 构建响应 —— 重写该函数构建一个JsonResponse响应
#     def create_response(self):
#         # 1、获取ES搜索的结果
#         context = self.get_context()
#         # object_list是一个列表，保存了Haystack查询的结果Result对象
#         results = context['page'].object_list
#         data_list = []
#         # 2、构建指定的响应参数
#         for result in results:
#             # 每一个Result对象
#             # result.object属性就是查询出来是SKU模型类对象
#             sku = result.object
#             data_list.append({
#                 'id': sku.id,
#                 'name': sku.name,
#                 'price': sku.price,
#                 'default_image_url': sku.default_image.url,
#                 # 用户搜索的关键词
#                 'searchkey': context.get('query'),
#                 # 页面总页数
#                 'page_size': context['page'].paginator.num_pages,
#                 # 查询的总数量
#                 'count': context['page'].paginator.count
#             })
#
#         # 3、构建一个JsonResponse响应返回
#         return JsonResponse(data_list, safe=False)
#




