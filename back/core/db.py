# core/db.py
import os
from tortoise import Tortoise
from core.security import hash_password
from config import settings
from core.meta import MetaModel
from blog.preset import preset_blogdata
from pathlib import Path
import json

def get_tortoise_config():
    """生成 Tortoise ORM 配置"""
    if not settings.DEBUG:
        # PostgreSQL 配置
        return {
            'connections': {
                'default': {
                    'engine': 'tortoise.backends.asyncpg',
                    'credentials': {
                        'host':'localhost',
                        'port': 5432,
                        'user': 'admin',
                        'password': 'admin',
                        'database': 'blog',
                        'minsize': 1,
                        'maxsize': 10,
                    }
                }
            },
            'apps': {
                'models': {
                    'models': ['core.meta', 'blog.models'],
                    'default_connection': 'default',
                }
            }
        };
    else:
        base_dir = Path(__file__).parent.parent
        db_path = base_dir / "db.sqlite3"

        config = {
            'connections': {
                'default': {
                    'engine': 'tortoise.backends.sqlite',
                    'credentials': {
                        'file_path': str(db_path),
                    }
                }
            },
            'apps': {
                'models': {
                    'models': ['core.meta', 'blog.models'],
                    'default_connection': 'default',
                }
            }
        }
        return config

def auto_load_modules():
    """自动加载模型模块"""
    return {
        'models': [
            'core.meta',
            'blog.models'
        ]
    }

async def init_db():
    """
    初始化数据库连接 - 使用事务确保只初始化一次
    """
    from tortoise.transactions import in_transaction

    tortoise_config = get_tortoise_config()
    await Tortoise.init(config=tortoise_config)

    # 生成数据库表结构（这个可以安全多次执行）
    await Tortoise.generate_schemas()

    # 使用数据库事务确保数据初始化只执行一次
    try:
        async with in_transaction("default"):
            # 检查是否已有数据
            existing_meta = await MetaModel.all().first()

            if existing_meta:
                return

            await meta_data()
            await preset_blogdata()

    except Exception as e:
        # 如果发生异常（如其他worker已经完成初始化），静默处理
        print(f"数据初始化可能已被其他进程完成: {e}")





async def close_db():
    """
    关闭数据库连接
    """
    await Tortoise.close_connections()

async def meta_data():
    """
    加载默认数据，如创建初始用户组及根用户。
    """
    meta = await MetaModel.create(
        website_url=settings.WEBSITE_URL,
        website_name=settings.WEBSITE_NAME,
        name=settings.ROOT_NAME,
        nickname=settings.ROOT_NICKNAME,
        email=settings.ROOT_EMAIL,  # 注意：这里应该是 email 而不是 emial
        password=hash_password(settings.ROOT_PASSWORD),
        key=settings.ROOT_KEY,
        des=settings.ROOT_DES,
        avatar=settings.ROOT_AVATAR,
        api_key=settings.ROOT_API_KEY
    )
