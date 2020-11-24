from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.order_serializers import *

from meiduo_admin.paginations import MyPage




class OrderViewSet(ModelViewSet):

    queryset = OrderInfo.objects.all()

    serializer_class = OrderSimpleModelSerializer

    pagination_class = MyPage


    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')

        if keyword:
            return self.queryset.filter(order_id__contains=keyword)

        return self.queryset.all()

    def get_serializer_class(self):

        if self.action=='list':
            return OrderSimpleModelSerializer

        elif self.action=='retrieve':
            return OrderDetaiModelSerializer
        elif self.action=='partial_update':
            return OrderDetaiModelSerializer

        else:
            return self.serializer_class