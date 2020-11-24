"""
定义一个函数，来实现渲染完整的index.html静态化页面，并且部署到front_end_pc目录里面
"""
import os
from django.conf import settings
from django.template import loader
from .utils import get_categories
from contents.models import ContentCategory

# 需要定时执行该函数
def generate_static_index_html():
    # 1、构建模版参数 —— 动态数据
    categories = get_categories() # 用来渲染页面的三级分类的

    # 广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': categories,
        'contents': contents
    }
    # 2、页面渲染
    # 2.1、获取模版对象
    template = loader.get_template('index.html')
    # 2.2、传入动态数据，渲染出完整的页面数据
    html = template.render(context=context) # render函数返回渲染出来的html文件数据
    # 3、把完整的页面数据，保存成静态文件index.html，该文件存放在front_end_pc目录里
    # prefix = "/Users/weiwei/Desktop/meiduo_mall_sz40/front_end_pc"
    prefix = os.path.join(
        os.path.dirname(os.path.dirname(settings.BASE_DIR)),
        'front_end_pc'
    )
    file_path = os.path.join(prefix, "index.html")
    with open(file_path, 'w') as f:
        f.write(html)