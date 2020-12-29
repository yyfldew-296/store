from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.image_serializers import *

from meiduo_admin.paginations import MyPage
from rest_framework.generics import ListAPIView

class SKUSimpleListView(ListAPIView):

    queryset = SKU.objects.all()
    serializer_class = SKUSimpleSerializer

class ImageViewSet(ModelViewSet):

    queryset = SKUImage.objects.all()

    serializer_class = ImageModelSerializer

    pagination_class = MyPage


