from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.perm_serializers import *

from meiduo_admin.paginations import MyPage


class ContenTypeListView(ListAPIView):

    queryset = ContentType.objects.all()

    serializer_class = ContentTypeModelSerializer


class PermissionViewSet(ModelViewSet):

    queryset = Permission.objects.all()

    serializer_class = PermissionModelSerializer

    pagination_class = MyPage

    def get_queryset(self):

        return self.queryset.order_by('pk')






