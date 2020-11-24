
from django.urls import re_path

from meiduo_admin.views.home_views import *
from meiduo_admin.views.sku_views import *
from meiduo_admin.views.user_views import *
from meiduo_admin.views.spu_views import *
from meiduo_admin.views.spec_views import *
from meiduo_admin.views.option_views import *
from meiduo_admin.views.image_views import *
from meiduo_admin.views.order_views import *
from meiduo_admin.views.perm_views import *
from meiduo_admin.views.group_views import *
from meiduo_admin.views.admin_views import *

from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    re_path(r'^authorizations/$', obtain_jwt_token),

    # 用户总数统计
    re_path(r'^statistical/total_count/$', UserTotalCountView.as_view()),
    # 当日新增用户
    re_path(r'^statistical/day_increment/$', UserDayCountView.as_view()),
    # 日活跃用户
    re_path(r'^statistical/day_active/$', UserActiveCountView.as_view()),
    # 日下单用户
    re_path(r'^statistical/day_orders/$', UserOrderCountView.as_view()),
    # 月增用户
    re_path(r'^statistical/month_increment/$', UserMonthCountView.as_view()),
    # 日分类商品访问
    re_path(r'^statistical/goods_day_views/$', GoodsDayView.as_view()),



    # 用户列表数据,新建用户单一数据
    # GET + /users/ = self.get --> ListAPIView
    # POST + /users/ = self.post --> CreateAPIView
    re_path(r'^users/$', UserView.as_view()),

    # SKU管理
    re_path(r'^skus/$', SKUGoodsView.as_view(actions={
        'get': 'list',
        'post': 'create'
    })),
    re_path(r'^skus/(?P<pk>\d+)/$', SKUGoodsView.as_view(actions={
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 新建sku可选三级分类
    re_path(r'^skus/categories/$', SKUCategorieView.as_view()),
    # 新建sku可选spu信息
    re_path(r'^goods/simple/$', SPUSimpleView.as_view()),
    # 新建sku选择的SPU可选的规格和选项信息
    re_path(r'^goods/(?P<pk>\d+)/specs/$', SPUSpecView.as_view()),


    re_path(r'^goods/$', SPUGoodsView.as_view(actions={
        'get':'list',
        'post':'create'

    })),

    re_path(r'^goods/$', SPUGoodsView.as_view(actions={
        'get': 'reteieve',
        'put': 'update',
        'delete':'destroy'
    })),


    re_path(r'^goods/brands/simple/$', SPUBrandView.as_view()),

    re_path(r'^goods/channel/categories/$', SPUCateView.as_view()),

    re_path(r'^goods/channel/categories/(?P<pk>\d+)/$', SPUCateView.as_view()),

    re_path(r'^goods/specs/$', SpecViewSet.as_view(actions={
        'get':'list',
        'post':'create'
    })),

    re_path(r'^goods/specs/(?P<pk>\d+)/$', SpecViewSet.as_view(actions={
        'get': 'retrieve',
        'put': 'update',
        'delete':'destroy'
    })),

    re_path(r'^goods/specs/simple/$', SpecSimpeListView.as_view()),


    re_path(r'^specs/options/$', OptViewSet.as_view(actions={
        'get':'list',
        'post':'create'
    })),

    re_path(r'^specs/options/$', OptViewSet.as_view(actions={
        'get': 'retrieve',
        'put': 'update',
        'delete':'destroy'
    })),

    # 图片管理
    re_path(r'^skus/images/$', ImageViewSet.as_view(actions={
        'get': 'list',
        'post': 'create'
    })),
    re_path(r'^skus/images/(?P<pk>\d+)/$', ImageViewSet.as_view(actions={
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),

    # 新建图片可选SKU
    re_path(r'^skus/simple/$', SKUSimpleListView.as_view()),

    re_path(r'^orders/$', OrderViewSet.as_view(actions={
        'get':'list'
    })),

    re_path(r'^orders/(?P<pk>\d+)/$', OrderViewSet.as_view(actions={
        'get': 'retrieve'
    })),

    re_path(r'^orders/(?P<pk>\d+)/status/$', OrderViewSet.as_view(actions={
        'patch': 'partial_update'
    })),

    re_path(r'^permission/content_types/$', ContenTypeListView.as_view()),

    re_path(r'^permission/perms/$', PermissionViewSet.as_view(actions={
        'get':'list',
        'post':'create'
    })),

    re_path(r'^permission/perms/(?P<pk>\d+)/$', PermissionViewSet.as_view(actions={
        'get':'retrieve',
        'put':'update',
        'delete':'destroy'
    })),


    re_path(r'^permission/groups/$', GroupViewSet.as_view(actions={
        'get':'list',
        'post':'create'
    })),

    re_path(r'^permission/groups/(?P<pk>\d+)/$', GroupViewSet.as_view(actions={
        'get':'retrieve',
        'put':'update',
        'delete':'destroy'
    })),

    re_path(r'^permission/simple/$', GroupPermListView.as_view()),

    re_path(r'^permission/admins/$', AdminUserViewSet.as_view(actions={
        'get':'list',
        'post':'create'
    })),

    re_path(r'^permission/admins/(?P<pk>\d+)/$', AdminUserViewSet.as_view(actions={
        'get':'retrieve',
        'put': 'update',
        'delete':'destroy'

    })),

    re_path(r'permission/groups/simple/$', AdminGroupListView.as_view()),


]
