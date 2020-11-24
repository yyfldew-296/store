from rest_framework import serializers

from goods.models import *



# 获取ｓｐｕ列表
class SPUModelSerializer(serializers.ModelSerializer):

    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()



    class Meta:

        model = SPU

        # fields =[
        #     'id',
        #     'name',
        #     'brand',
        #     'brand_id',
        #     'category1_id',
        #     'category2_id',
        #     'category3_id',
        #     'sales',
        #     'comments',
        #     'desc_detail',
        #     'desc_pack',
        #     'desc_service',
        # ]
        exclude = ['category1','category2','category3']



# SPU的品牌选择
class BrandSimpleSerializer(serializers.ModelSerializer):

    class Meta:

        model = Brand

        fields = [
            'id',
            'name'
        ]


# 获取一级／二级／三级分类

class CateSimpleSerializer(serializers.ModelSerializer):

    class Meta:

        model = GoodsCategory
        fields = [
            'id',
            'name'
        ]



