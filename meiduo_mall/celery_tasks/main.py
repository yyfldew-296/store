"""
异步程序的主脚本文件(主模块)
"""
import os
# 作用，设置一个环境变量DJANGO_SETTINGS_MODULE，记录django配置文件的导包路径
# =======第一种方式设置django配置文件路径=======
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')
# =======第二种方式设置django配置文件路径=======
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    # 如果没有该环境变量
    # os.environ = {'DJANGO_SETTINGS_MODULE': 'meiduo_mall.settings.dev'}
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

from celery import Celery

# 1、初始化一个Celery对象 —— 异步程序对象
celery_app = Celery()
# 2、加载配置文件
celery_app.config_from_object('celery_tasks.config') # 参数是配置文件导包路径
# 3、注册任务
celery_app.autodiscover_tasks([
    'celery_tasks.sms', # (1)、发送短信任务包的导包路径
    'celery_tasks.email', # (2)、发送验证邮件任务包的导包路径
])
