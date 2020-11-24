"""
使用itsdangrous模块封装加密和解密接口
"""
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class SecretOauth(object):

    def __init__(self):
        # 初始化一个TimedJSONWebSignatureSerializer对象，用于加密和解密
        self.serializer = Serializer(
            secret_key=settings.SECRET_KEY,
            expires_in=24 * 15 * 60 # 秒
        )

    # 加密
    def dumps(self, content_dict):
        """
        功能：加密content_dict数据
        :param content_dict: 字典数据 {"openid": "89gtj78978gjtkrbngjkt"}
        :return: 加密后的数据
        """
        result = self.serializer.dumps(content_dict) # b"gregrtwretgtrhyt5hy"
        return result.decode() # "gregrtwretgtrhyt5hy"

    # 解密
    def loads(self, content):
        """
        解密数据
        :param content: 加密之后的字符串密文 "gregrtwretgtrhyt5hy"
        :return: 解密后的字典 {"openid": "89gtj78978gjtkrbngjkt"}
        """
        try:
            result = self.serializer.loads(content) # {"openid": "89gtj78978gjtkrbngjkt"}
        except Exception as e:
            # 解密失败
            return None
        return result
