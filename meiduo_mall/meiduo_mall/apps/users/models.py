from django.db import models
from django.contrib.auth.models import AbstractUser
from meiduo_mall.utils.models import BaseModel
# Create your models here.

# 自定义用户模型类，由于需要使用django用户相关的功能，而这些功能，必须依赖AbstractUser基类，
# 所以，我们需要继承AbstractUser
class User(AbstractUser):

    # 新增字段mobile
    mobile = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='手机号'
    )
    # 新增 email_active 字段
    # 用于记录邮箱是否激活, 默认为 False: 未激活
    email_active = models.BooleanField(
        default=False,
        verbose_name='邮箱验证状态'
    )

    # 新增默认收货地址
    default_address = models.ForeignKey(
        'Address', related_name='users', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='默认地址'
    )

    class Meta:
        # 对应的mysql表名
        db_table = 'tb_users'
        # 以下2个字段定义django默认管理站点该模型类在html页面中的中文显示
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# User.is_authenticated: True表示经过身份认证(有身份)；False表示匿名用户(身份认证失败)；
# User.objects.create() # 新建用户模型类对象 —— 1、密码不加密；2、is_staff设置为False
# User.objects.create_user() # 新建用户模型类对象 —— 1、密码加密；2、is_staff设置为False
# User.objects.create_superuser() # 新建用户模型类对象 —— 1、密码加密；2、is_staff设置为True,is_superuser设置为True
# User.check_password() # 检查密码
# User.set_password() # 设置用户密码


class Address(BaseModel):
    """
    用户地址（收货地址）
    """
    # on_delete=models.CASCADE --> 主表数据(User)存在关联的从表数据(Address),主表数据删除，从表数据级联删除
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    # on_delete=models.PROTECT --> 主表数据存在关联从表数据，则主表数据不允许删除
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        # 设置默认 已更新时间降序 获取查询集数据
        ordering = ['-update_time']
