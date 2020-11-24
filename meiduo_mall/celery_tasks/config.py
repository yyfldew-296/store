

# 任务队列的连接
# 采用redis作为任务队列，redis标准连接写法： redis://<ip>:<port>/<几号库>
broker_url = 'redis://192.168.203.153:6379/3'



# 如果使用别的作为中间人, 例如使用 rabbitmq
# 则 rabbitmq 配置如下:
# broker_url= 'amqp://用户名:密码@ip地址:5672'