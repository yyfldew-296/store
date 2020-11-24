from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.spu_serializers import *

from meiduo_admin.paginations import MyPage




class SPUGoodsView(ModelViewSet):

    queryset = SPU.objects.all()
    serializer_class = SPUModelSerializer

    pagination_class = MyPage


    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return self.queryset.filter(
                name__contains=keyword
            )

        return self.queryset.all()



class SPUBrandView(ListAPIView):

    queryset = Brand.objects.all()
    serializer_class = BrandSimpleSerializer


class SPUCateView(ListAPIView):

    queryset = GoodsCategory.objects.all()
    serializer_class =  CateSimpleSerializer

    def get_queryset(self):

        parent_id = self.kwargs.get('pk')
        if parent_id:
            return self.queryset.filter(parent_id=parent_id)
        return self.queryset.filter(parent_id=None)