from django.test import TestCase

import unittest


class MyClassTestCase(TestCase):

    @classmethod


    def setUpClass(cls):

        print('setUpClass在所有测试用例执行之前调用')

    @classmethod


    def tearDownClass(cls):

        print('tearDownClass在所有测试用例执行之后调用')


    def setUp(self):

        print('setUP在每一个测试方法执行之前被调用')

    def tearDown(self):
        print('tearDown在每一个测试方法执行之前被调用')


    def test_1(self):
        print('test_1')

    def test_2(self):
        print('test_2')


