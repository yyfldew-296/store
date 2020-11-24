"""
一个任务包里面的固定名称的模块tasks.py，是当前定义任务的地方
"""
from celery_tasks.main import celery_app
from celery_tasks.yuntongxun.ccp_sms import CCP

# 定义一个发送短信的任务(任务就是函数)
@celery_app.task(name='ccp_send_sms_code') # 只有被task装饰器装饰的函数才能"异步"执行；
def ccp_send_sms_code(mobile, sms_code):
    """
    功能：发送短信
    参数：mobile手机号；sms_code短信验证码
    返回值：0表示发送成功；-1表示发送失败
    """
    ccp = CCP()
    # result: 0表示成功，-1表示失败
    result = ccp.send_template_sms(
        mobile,
        [sms_code, 5],
        1
    )
    return result