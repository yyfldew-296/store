# 导入:
from django.db import models
from meiduo_mall.utils.models import BaseModel

# 定义QQ登录的模型类:
class OAuthQQUser(BaseModel):
    """QQ登录用户数据"""

    # user 是个外键, 关联对应的用户 —— 代表美多商城用户
    user = models.ForeignKey('users.User',  on_delete=models.CASCADE, verbose_name='用户')
    # qq 发布的用户身份id —— 代表用户的qq身份
    openid = models.CharField(max_length=64,  verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'