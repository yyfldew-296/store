from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.option_serializers import *

from meiduo_admin.paginations import MyPage


class SpecSimpeListView(ListAPIView):

    queryset = SPUSpecification.objects.all()

    serializer_class = SpecOptModelSerializer


class OptViewSet(ModelViewSet):

    queryset = SpecificationOption.objects.all()
    serializer_class = OptModelSerializer

    pagination_class = MyPage
