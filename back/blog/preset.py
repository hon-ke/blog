# 预定义的要加入到数据库的数据
from blog.models import PostModel,PageModel

# 不要删除，这里的数据是前端也定义好了的特殊页面，如果这数据删除，需要在前端的Aside页面手动加入
preset_page = [
    # order越大越在前，默认是10
    {"description": "友链页面", "title": "友链", "icon": "czs-Google","order":80},
    {"description": "关于页面", "title": "关于", "icon": "czs-circle","order":10},
    {"description": "文章归档", "title": "归档", "icon": "czs-box-l","order":11},
]

async def preset_blogdata():
    # 只要有数据就不创建了
    page =await PageModel.filter().first()
    if page:
        return
    
    for page in preset_page:
        await PageModel.create(**page)
    