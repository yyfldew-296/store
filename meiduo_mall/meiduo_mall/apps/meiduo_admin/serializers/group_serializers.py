from rest_framework import serializers
from django.contrib.auth.models import Group,Permission



class GroupPermSimpleSerializer(serializers.ModelSerializer):

    class Meta:

        model = Permission

        fields = [
            'id',
            'name'
        ]


class GroupModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = Group

        fields = [
            'id',
            'name',
            'permissions'
        ]