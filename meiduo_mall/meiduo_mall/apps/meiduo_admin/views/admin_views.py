from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.admin_serializers import *
from meiduo_admin.paginations import MyPage

from rest_framework.generics import ListAPIView


class AdminGroupListView(ListAPIView):

    queryset = Group.objects.all()

    serializer_class = AdminGroupModelSerializer



class AdminUserViewSet(ModelViewSet):

    queryset = User.objects.all()

    serializer_class = AdminUserModelSerializer

    pagination_class = MyPage
