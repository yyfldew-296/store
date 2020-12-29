# 定义 setUpClass: 用户登录
# 定义 tearDownClass: 用户退出
# 定义测试方法：获取用户信息、获取用户浏览器记录、获取用户地址列表

from django.test import TestCase
from requests import Session


class MyClassTestCase(TestCase):
    # 类属性
    session = None

    # 在所有测试用例执行之前调用
    @classmethod
    def setUpClass(cls):
        print('setUpClass')
        # 构造账号密码
        info = {
            "username": "mike123",
            "password": "chuanzhi12345",
            "remembered": True
        }

        # 实例化session对象，此为类属性
        cls.session = Session()

        # 登录
        resp = cls.session.post(
            'http://127.0.0.1:8000/login/',
            json=info
        )

        # 获取 json 响应
        result = resp.json()

        # 检查是否登录成功
        # 检查是否登录成功
        if result['code'] != 0:
            print('登录失败')

    # 在所有测试用例执行之后调用
    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')
        # 登出
        cls.session.delete('http://127.0.0.1:8000/logout/')

    # 获取登陆用户
    def test_1_info(self):
        # 查看用户状态
        resp = self.session.get('http://127.0.0.1:8000/info/')
        print(resp.json())

    # 获取用户浏览历史
    def test_2_history(self):
        resp = self.session.get('http://127.0.0.1:8000/browse_histories/')
        print(resp.json())

    def test_3_addresses(self):
        # 调用查看地址列表接口
        url = 'http://127.0.0.1:8000/addresses/'
        resp = self.session.get(url)
        print(resp.json())