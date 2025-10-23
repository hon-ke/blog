from tortoise import fields, models

from core.base import BaseModelManager


class PostModel(models.Model):

    id = fields.IntField(pk=True)
    # 核心内容
    title = fields.CharField(unique=True,max_length=255,null=True)
    content = fields.TextField()
    excerpt = fields.TextField(null=True, default="随便写点内容当描述...",description="文章摘要")  # 新增摘要字段
    tag = fields.CharField(max_length=128, default="", null=True)
    category = fields.CharField(max_length=128,null=True,default="默认")

    # 删除了type字段
    # cover图片
    cover = fields.CharField(max_length=128, default="", null=True)
    # 置顶？
    is_top = fields.BooleanField(default=False,description="是否置顶")
    is_locked = fields.BooleanField(default=False,description="是否私密")

    # 浏览
    like = fields.IntField(default=0, description="点赞量")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "posts"
        ordering = ["-created_at"]

class CommentModel(models.Model):
    id = fields.IntField(pk=True)
    
    # 关联文章
    post = fields.ForeignKeyField('models.PostModel', related_name='comments')
    
    # 评论者信息
    author_name = fields.CharField(max_length=100, description="评论者昵称")
    author_email = fields.CharField(max_length=100, description="评论者邮箱")
    author_website = fields.CharField(max_length=200, null=True, description="评论者网站")
    
    # 评论内容
    content = fields.TextField(description="评论内容")
    
    # 状态管理
    is_anonymous = fields.BooleanField(default=False, description="是否匿名评论")
    is_superuser = fields.BooleanField(default=False, description="是否超级用户")
    is_approved = fields.BooleanField(default=True, description="是否审核通过")
    
    # IP和用户代理（用于反垃圾）
    ip_address = fields.CharField(max_length=45, null=True, description="评论者IP")
    user_agent = fields.TextField(null=True, description="用户代理")
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "comments"
        ordering = ["-created_at"]


class PageModel(models.Model):
    id = fields.IntField(pk=True)
    # 页面标题
    title = fields.CharField(max_length=255,  unique = True,description="页面标题", null=True)
    # 页面描述
    description = fields.CharField(max_length=500, null=True, description="页面描述")
    # 图标
    icon = fields.CharField(default = "czs-circle",max_length=100, description="图标类名", null=True)
    # 页面内容
    content = fields.TextField(default="", description="页面内容")
    # 是否启用
    is_active = fields.BooleanField(default=True, description="是否启用", null=True)
    # 排序权重
    order = fields.IntField(default=100, description="排序权重", null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "pages"
        ordering = ["-order"]

class PageModelManager(BaseModelManager[PageModel]):
    def __init__(self):
        super().__init__(PageModel)

page_manager = PageModelManager()

class CommentModelManager(BaseModelManager[CommentModel]):
    def __init__(self):
        super().__init__(CommentModel)

comment_manager = CommentModelManager()

class PostModelManager(BaseModelManager[PostModel]):
    def __init__(self):
        super().__init__(PostModel)

post_manager = PostModelManager()