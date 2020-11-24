from rest_framework import serializers
from goods.models import SKU, SKUSpecification, GoodsCategory, SPU, SPUSpecification, SpecificationOption


# 自定义选项序列化器
class OptModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = [
            'id',
            'value'
        ]


# 自定义规格序列化器
class SpecSimpleSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    options = OptModelSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = [
            # 固有字段
            'id',
            'name',

            # 主表字段(单一)
            'spu',
            'spu_id',

            # 从表字段(多个)
            # options隐藏字段，记录当前规格关联的多个SpecificationOption模型类对象
            'options'
        ]


# 自定义SPU序列化器
class SPUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = [
            'id',
            'name'
        ]


# 自定义序列化三级分类序列化器
class GoodsCateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = [
            'id',
            'name'
        ]


# 自定义SKU关联从表SKUSpecification对象序列化器
class SKUSpecModelSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = [
            'spec_id',
            'option_id'
        ]


class SKUModelSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    # 自定义specs字段的序列化器
    specs = SKUSpecModelSerializer(many=True)

    class Meta:
        model = SKU
        fields = [
            # 固有字段
            'id',
            'name',
            'caption',
            'price',
            'cost_price',
            'market_price',
            'stock',
            'sales',
            'is_launched',

            # 关联字段(主表数据)
            'spu',
            'spu_id',
            'category',
            'category_id',

            # 关联字段(从表数据)
            # 记录的数据是于SKU对象，关联的"多个"关联从表"SKUSpecification"对象
            # 理解为：序列化specs字段，等于序列化多个SKUSpecification模型类对象数据
            'specs',
        ]

    def create(self, validated_data):
        """
        重写create方法，来手动插入中间表(SKUSpecification)数据记录新增sku拥有的规格和选项信息
        :param validated_data:有效数据
        :return:新建的SKU对象
        """
        # specs记录的是中间表数据，无法用于新建SKU，所以先从有效数据中移除
        # specs = [{spec_id:1, option_id:2}, {...}...]
        specs = validated_data.pop('specs')
        # 1、新建SKU对象——主表
        sku = SKU.objects.create(**validated_data)
        # 2、新建SKUSpecification对象 —— 记录SKU的规格和选项信息 —— 从表
        for temp in specs:
            # temp = {spec_id:1, option_id:2}
            temp['sku_id'] = sku.id  # {sku_id:8, spec_id:1, option_id:2}
            SKUSpecification.objects.create(**temp)

        return sku

    def update(self, instance, validated_data):
        specs = validated_data.pop('specs')
        # 1、更新主表数据
        instance = super().update(instance, validated_data)
        # 2、更新中间表数据 —— 原有的规格和选项删除，然后插入新的规格和选项
        # 2.1、删除旧规格选项
        SKUSpecification.objects.filter(sku_id=instance.id).delete()
        # 2.2、插入新规格选项
        for temp in specs:
            temp['sku_id'] = instance.id
            SKUSpecification.objects.create(**temp)

        return instance



















