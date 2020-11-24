
from django.urls import re_path,path
from . import views


# 路由映射列表
urlpatterns = [
    # 路由映射指的就是，把一个请求(HTTP请求)和处理的视图函数(方法)一一对应起来(映射);
    # 路由映射公式：请求方式 + 请求路径 = 视图方法
    # GET + usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/ = UsernameCountView.get()
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),

    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view()),

    re_path(r'^register/$', views.RegisterView.as_view()),

    re_path(r'^login/$', views.LoginView.as_view()),

    re_path(r'^logout/$', views.LogoutView.as_view()),

    re_path(r'^info/$', views.UserInfoView.as_view()),

    re_path(r'^emails/$', views.EmailView.as_view()),

    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),

    re_path(r'^addresses/create/$', views.CreateAddressView.as_view()),

    re_path(r'^addresses/$', views.AddressView.as_view()),

    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),

    re_path(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),

    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),

    re_path(r'^password/$', views.ChangePasswordView.as_view()),

    re_path(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
]