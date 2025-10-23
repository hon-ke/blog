from tortoise import fields, models
from core.base import BaseModelManager


class MetaModel(models.Model):
    id = fields.IntField(pk=True)
    # website
    website_url = fields.CharField(max_length=50)
    website_name = fields.CharField(max_length=50)

    # root用户相关
    name = fields.CharField(max_length=50)
    nickname = fields.CharField(null=True,max_length=128)
    email = fields.CharField(max_length=100,null=True)
    password = fields.CharField(max_length=128)
    des = fields.TextField(null=True)
    avatar = fields.CharField(max_length=200, null=True)
    ip = fields.CharField(max_length=50, null=True)

    key = fields.CharField(max_length=512)
    
    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    api_key = fields.CharField(
        max_length=128,
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        table = "meta"

class MetaModelManager(BaseModelManager[MetaModel]):
    def __init__(self):
        super().__init__(MetaModel)

website_manager = MetaModelManager()
