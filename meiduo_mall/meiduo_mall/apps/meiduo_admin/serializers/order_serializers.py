from rest_framework import serializers

from goods.models import SKU
from orders.models import *


# 订单简单序列化
class OrderSimpleModelSerializer(serializers.ModelSerializer):



    class Meta:

        model = OrderInfo

        fields = [
            'order_id',
            'create_time',
        ]




# 定义关联打ＳＫＵ模型类序列化器
class SKUSimpleModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = SKU
        fields = [
            'name',
            'default_image',
        ]





# 定义关联打OrderGoods模型类序列化器
class OrderGoodsModelSerializer(serializers.ModelSerializer):

    sku = SKUSimpleModelSerializer()


    class Meta:
        model = OrderGoods

        fields = [
            'count',
            'price',
            'sku',
        ]



# 订单详情序列化
class OrderDetaiModelSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()

    skus=OrderGoodsModelSerializer(many=True)



    class Meta:

        model = OrderInfo

        fields = [
            'order_id',
            'user',
            'total_count',
            'total_amount',
            'freight',
            'pay_method',
            'status',
            'create_time',


            'skus',
        ]























