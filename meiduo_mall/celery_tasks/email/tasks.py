
from django.conf import settings
from django.core.mail import send_mail
from celery_tasks.main import celery_app

# 定义一个函数发送邮件
@celery_app.task(name='send_verify_email')
def send_verify_email(to_email, verify_url):
    """
    :param to_email: 目标邮箱地址
    :param verify_url:  嵌入邮件正文的验证链接 —— 用户点击发请求调用后续接口完成邮件验证
    :return:
    """
    # 标题
    subject = "美多商城邮箱验证"
    # 发送内容:
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    # 发送邮件
    result = send_mail(
        subject=subject,
        message="",
        from_email=settings.EMAIL_FROM,
        recipient_list=[to_email],
        html_message=html_message
    )

    return result