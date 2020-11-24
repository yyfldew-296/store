from rest_framework import serializers


from django.contrib.auth.models import Permission,ContentType, Group


class ContentTypeModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = ContentType

        fields = [
            'id',
            'name'
        ]


class PermissionModelSerializer(serializers.ModelSerializer):



    class Meta:

        model = Permission
        fields = [
            'id',
            'name',
            'codename',
            'content_type'
        ]


