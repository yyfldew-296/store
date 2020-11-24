"""
定义主页数据统计的接口视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from users.models import User
from orders.models import OrderInfo

from datetime import timedelta
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.home_serializers import *

from django.utils import timezone

# 用户总数
class UserTotalCountView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        # 1、统计出用户的数量
        count = User.objects.count()
        print('测试',count)
        cur_time = timezone.localtime() # 年月日时时分秒
        # 2、构建响应返回
        return Response({
            'count': count,
            'date': cur_time.date() # 年月日
        })


# 日增用户
class UserDayCountView(APIView):

    def get(self,request):

        cur_time = timezone.localtime()
        cur_0_time = cur_time.replace(hour=0,minute=0,second=0)
        count = User.objects.filter(
            date_joined__gte=cur_0_time
        ).count()

        return Response({
            'count':count,
            'date':cur_0_time.date()
        })


# 日活跃用户
class UserActiveCountView(APIView):

    def get(self,request):

        cur_time = timezone.localtime()
        cur_0_time = cur_time.replace(hour=0,second=0,minute=0)

        count = User.objects.filter(
            last_login__gte=cur_0_time
        ).count()

        return Response({
            'count':count,
            'date':cur_0_time
        })



# 日下单用户
class UserOrderCountView(APIView):

    def get(self, request):

        cur_time = timezone.localtime()
        cur_0_time = cur_time.replace(hour=0,minute=0,second=0)


        orders = OrderInfo.objects.filter(
            create_time__gte=cur_0_time
        )

        user_set=set()

        for order in orders:
            user_set.add(order.user)

        count = len(user_set)
        # users = User.objects.filter(
        #     orders__create_time__gte=cur_0_time
        # )
        #
        # count = len(set(users))
        # print('测试２',users)

        return Response({
            'count':count,
            'date':cur_0_time.date()
        })


# 月增用户
class UserMonthCountView(APIView):

    def get(self,request):

        end_0_time = timezone.localtime().replace(hour=0,second=0,minute=0)

        start_0_time = end_0_time - timedelta(days=29)

        ret_data = [ ]

        for index in range(30):
            #某一天的时间点
            calc_0_time= start_0_time + timedelta(days=index)

            next_0_time =calc_0_time  + timedelta(days=1)

            count = User.objects.filter(
                date_joined__gte=calc_0_time,
                date_joined__lt=next_0_time
            ).count()

            ret_data.append({
                'count':count,
                'date':calc_0_time.date()
            })

        return Response(ret_data)



# 分类商品访问量
class GoodsDayView(ListAPIView):
    queryset = GoodsVisitCount.objects.all()
    serializer_class = GoodsVisitCountModelSerializer


    def get_queryset(self):

        cur_0_time = timezone.localtime().replace(hour=0,second=0,minute=0)

        return self.queryset.filter(
            create_time__gte=cur_0_time
        )




























