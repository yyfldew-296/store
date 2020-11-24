
# 商品列表
from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet

from goods.models import *
from meiduo_admin.paginations import MyPage
from meiduo_admin.serializers.sku_serializers import *


# 获取商品列表
class SKUGoodsView(ModelViewSet):

    queryset = SKU.objects.all()

    serializer_class = SKUModelSerializer

    pagination_class = MyPage

    def get_queryset(self):
        keywork = self.request.query_params.get('keywork')

        if keywork:
            return self.queryset.filter(name__contains=keywork)

        return self.queryset.all()


class SKUCategorieView(ListAPIView):

    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCateSimpleSerializer

class SPUSimpleView(ListAPIView):
    queryset = SPU.objects.all()
    serializer_class = SPUSimpleSerializer



class SPUSpecView(ListAPIView):

    queryset =  SPUSpecification.objects.all()
    serializer_class = SpecSimpleSerializer


    def get_queryset(self):

        spu_id = self.kwargs.get('pk')

        return self.queryset.filter(spu_id=spu_id)






