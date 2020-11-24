from rest_framework import serializers

from users.models import User

from django.contrib.auth.models import Group

from django.contrib.auth.hashers import make_password


class AdminGroupModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = Group

        fields = [
            'id',
            'name'
        ]


class AdminUserModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'email',
            'mobile',

            'password',
            'groups',
            'user_permissions',
        ]


        extra_kwargs = {
            'password': {'write_only':True}
        }


    def validate(self, attrs):

        password= attrs.get('password')

        attrs['password'] = make_password(password)

        attrs['is_staff'] = True

        return attrs