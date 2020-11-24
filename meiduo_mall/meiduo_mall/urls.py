"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include,register_converter
from meiduo_mall.utils.converters import *

register_converter(UsernameConverter, 'username')
register_converter(MobileConverter, 'mobile')

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'', include('users.urls')),
    re_path(r'', include('verifications.urls')),
    re_path(r'', include('oauth.urls')),
    re_path(r'', include('areas.urls')),
    # re_path(r'', include('contents.urls')),
    re_path(r'', include('goods.urls')),
    re_path(r'', include('carts.urls')),
    re_path(r'', include('orders.urls')),
    re_path(r'', include('payment.urls')),
    re_path(r'meiduo_admin/', include('meiduo_admin.urls')),
]
