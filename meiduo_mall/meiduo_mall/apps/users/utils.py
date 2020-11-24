"""
自定义认证后端，实现多账号登陆
"""

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from users.models import User

class UsernameMobileAuthBackend(ModelBackend):

    # 重写该方法，实现多账号验证
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        功能：根据身份信息验证用户身份
        参数：request请求对象；username前端传入的用户名或手机号等；password密码；
        返回值：返回用户对象或None
        """
        try:
            # 1、根据username、mobile去查找用户
            # select * from tb_users where username='18588269037' or mobile='18588269037';
            user = User.objects.get(
                Q(username=username) | Q(mobile=username) # username='18588269037' or mobile='18588269037'
            )
            # user = User.objects.get(username=username, mobile=username) # username=18588269037 and mobile=18588269037
        except User.DoesNotExist as e:
            return None

        # TODO:
        if request is None:
            if not user.is_staff: #dwa1
                return None


        # 2、检查密码
        if user.check_password(password):
            return user


from django.conf import settings
from meiduo_mall.utils.secret import SecretOauth
# 获取验证邮件完成的verify_url
def generate_verify_email_url(request):
    """
    :param request: 请求对象 —— 通过请求对象获取登陆的用户request.user
    :return: 完整的verify_url
    """
    # 1、获取当前登陆的用户
    user = request.user
    # 2、把用户数据加密成token值
    data_dict = {
        'user_id': user.id,
        'email': user.email
    }
    auth = SecretOauth()
    token = auth.dumps(data_dict)
    verify_url = settings.EMAIL_VERIFY_URL + token
    # 3、返回完成的验证url
    return verify_url



def jwt_response_payload_handler(token, user=None, request = None):

    return {
        'username':user.username,
        'user_id':user.id,
        'token':token
    }







