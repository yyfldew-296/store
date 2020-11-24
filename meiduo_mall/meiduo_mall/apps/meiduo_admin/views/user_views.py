from rest_framework.generics import ListAPIView,CreateAPIView

from rest_framework.viewsets import ModelViewSet

from rest_framework.response import Response

from goods.models import SKU
from meiduo_admin.serializers.user_serializers import *

from meiduo_admin.paginations import MyPage
from meiduo_admin.serializers.sku_serializers import *

#获取用户列表
class UserView(ListAPIView,CreateAPIView):
    queryset = User.objects.all()
    serializer_class =  UserModelSerializer

    pagination_class = MyPage


    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')

        if keyword:
            return self.queryset.filter(
                username__contains=keyword
            )

        return self.queryset.all()



