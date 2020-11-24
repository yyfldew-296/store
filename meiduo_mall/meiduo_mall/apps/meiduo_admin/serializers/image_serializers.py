from rest_framework import serializers
from goods.models import SKU,SKUImage


class SKUSimpleSerializer(serializers.ModelSerializer):

    class Meta:

        model = SKU

        fields = [
            'id',
            'name'
        ]


class ImageModelSerializer(serializers.ModelSerializer):

    class Meta:

        model =SKUImage

        fields = [
            'id',
            'sku',
            'image'
        ]