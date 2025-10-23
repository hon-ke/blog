from typing import TypeVar, Generic, Type, Any, List, Callable, Awaitable
from functools import wraps
from tortoise.transactions import in_transaction
from tortoise.models import Model
from tortoise.queryset import QuerySet
from tortoise.exceptions import DoesNotExist, IntegrityError
from fastapi import HTTPException, status

T = TypeVar('T', bound=Model)

class ManagerException(HTTPException):
    """基础Manager异常"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(status_code=status_code, detail=detail)

def handle_manager_errors(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Manager方法异常处理装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DoesNotExist as e:
            raise ManagerException(detail=f"{str(e)}", status_code=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            raise ManagerException(detail=f"{str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise ManagerException(detail=f"{str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

class BaseModelManager(Generic[T]):
    """基础Repository提供通用CRUD操作"""
    
    def __init__(self, model: Type[T]):
        self._model = model
        
    
    async def get(self, **kwargs) -> T | None:
        """获取单个对象"""
        return await self._model.get(**kwargs)
    
    
    async def get_or_none(self, **kwargs) -> T | None:
        """获取单个对象"""
        return await self._model.get_or_none(**kwargs)
    
    
    async def all(self, preload: List[str]|str = None, **filters) -> List[T]:
        """获取所有对象，并支持预加载关联关系"""
        if isinstance(preload,str):
            preload = [preload]
        if filters:
            query = await query.filter(**filters)
        
        # 如果指定了 preload，则预加载关联关系
        if preload:
            for relation in preload:
                query = await query.prefetch_related(relation)  # Tortoise ORM 的 prefetch_related
        
        return query

    async def create(self, **kwargs) -> T:
        """创建新对象（事务内执行）"""
        async with in_transaction():
            return await self._model.create(**kwargs)

    async def get_or_create(self, **kwargs) -> tuple[T, bool]:
        """
        获取对象，如果不存在则创建
        返回 (对象, 是否创建)
        """
        async with in_transaction():
            obj, created = await self._model.get_or_create(**kwargs)
            return obj, created

    async def update(self, obj: T, **kwargs) -> T:
        """更新对象的所有字段"""
        async with in_transaction():
            await obj.update_from_dict(kwargs).save()
            return obj

    async def update_partial(self, obj: T, **kwargs) -> T:
        """
        部分更新对象（仅更新传入的字段）
        不需要事务（由调用方控制）
        """
        await obj.update_from_dict(kwargs).save()
        return obj

    
    async def delete(self, obj: T):
        """删除对象（支持软删除）"""
        async with in_transaction():
            # if hasattr(obj, "is_active"):
            #     await obj.update_from_dict({"is_active": False}).save()
            # else:
            #     await obj.delete()
            await obj.delete()

    async def soft_delete(self, obj: T):
        """软删除对象（需确保模型有 is_active 字段）"""
        if not hasattr(obj, "is_active"):
            raise ManagerException(detail="模型不支持软删除", status_code=status.HTTP_400_BAD_REQUEST)
        await obj.update_from_dict({"is_active": False}).save()

    
    async def exists(self, **kwargs) -> bool:
        """检查对象是否存在（无需事务）"""
        return await self._model.filter(**kwargs).exists()

    
    # 可选：为常用 QuerySet 方法添加类型提示
    def filter(self, **kwargs) -> QuerySet:
        return self._model.filter(**kwargs)

    def exclude(self, **kwargs) -> QuerySet:
        return self._model.exclude(**kwargs)
    
    
    def last(self, **kwargs) -> QuerySet:
        return self._model.last()
    
    def first(self, **kwargs) -> QuerySet:
        return self._model.first()