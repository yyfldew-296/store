from django.test import TestCase

# Create your tests here.

"""
0. 导包， import unittest
1. 定义类，继承unittest.TestCase
2. 是一个fixture, 有前置后置方法
3. 有test开头的测试用例，结果用断言判断
4. 运行测试
"""
import unittest
from HTMLTestRunner.HTMLTestRunner import HTMLTestRunner


class MyTest(unittest.TestCase):
    def setUp(self) -> None:
        print('setUp')

    def tearDown(self) -> None:
        print("tearDown")

    @classmethod
    def setUpClass(cls) -> None:
        print('setUpClass')

    @classmethod
    def tearDownClass(cls) -> None:
        print('tearDownClass')

    def test_1_add(self):
        num = 1 + 2
        print('test_add')
        self.assertEqual(num, 3, msg='加法错误')

    def test_2_sub(self):
        num = 1 - 1
        print('test_sub')
        self.assertEqual(num, 0, msg='减法错误')


if __name__ == '__main__':
    # 1. 把测试用例添加到suite容器中
    suite = unittest.defaultTestLoader.discover('./', 'test_1_html.py')

    # 2. 打开文件，是一个文件对象
    with open('./HTMLTestRunner.html', 'w', encoding='utf-8') as f:
        # 3. HTMLTestRunner()创建一个runner对象
        runner = HTMLTestRunner(
            stream=f,  # 测试报告需要写入到的文件
            verbosity=2,  # 控制台输出信息的详细程度, 默认为1
            title='这是报告标题',  # 测试报告的标题
            description='这是一个测试报告'  # 测试报告的描述
        )
        # 4. runner把容器中测试用例运行
        runner.run(suite)