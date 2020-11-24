from rest_framework import serializers

from goods.models import *


class SpecOptModelSerializer(serializers.ModelSerializer):



    class Meta:

        model = SPUSpecification

        fields = [
            'id',
            'name'
        ]


class OptModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = SpecificationOption
        fields = '__all__'
