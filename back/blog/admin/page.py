from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from blog.models import page_manager
from blog.schemas import PageResponse, PageCreate, PageUpdate, PageListResponse
from core.security import is_admin
from blog.tools import exclude_empty,radom_icons
# 管理路由
router = APIRouter(
    prefix="/admin/pages",
    tags=["admin - 页面管理"],
)

@router.post(
    "/",
    summary="创建页面",
    response_model=PageResponse,
)
async def create_page(page_data: PageCreate):
    """创建新页面"""
    try:
        # 检查页面标识是否已存在
        if await page_manager.exists(title=page_data.title):
            raise HTTPException(status_code=409, detail="页面标识已存在")
        
        # 设置随机icon
        # if page_data.icon in ["",None]:
        #     page_data.icon = radom_icons()
        create_data = exclude_empty(page_data.model_dump())
        new_page = await page_manager.create(**create_data)
        return new_page
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建页面失败: {str(e)}")

@router.get(
    "/",
    summary="获取页面列表",
    response_model=PageListResponse,
)
async def get_pages(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1,description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
):
    """获取所有页面（管理员）"""
    try:
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        
        # 获取总数
        total = await page_manager.filter(**filters).count()
        
        # 获取分页数据
        pages = await page_manager.filter(**filters)\
            .offset((page - 1) * size)\
            .limit(size)\
            .order_by("order", "-created_at")\
            .all()
        
        return PageListResponse(pages=pages, total=total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取页面列表失败: {str(e)}")

@router.get(
    "/{page_title}",
    summary="获取页面详情",
    response_model=PageResponse,
)
async def get_page(page_title:str):
    """获取页面详情（管理员）"""
    try:
        page = await page_manager.get_or_none(title=page_title)
        if not page:
            raise HTTPException(status_code=404, detail="页面不存在")
        return page
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取页面详情失败: {str(e)}")

@router.put(
        "/",
    response_model=PageResponse,
)
async def update_page(page_data: PageUpdate):
    """更新页面"""
    try:
        page = await page_manager.get_or_none(title=page_data.title)

        if not page:
            raise HTTPException(status_code=404, detail="页面不存在")
        
        if page.icon in ["",None]:
            page_data.icon = radom_icons()

        update_data = exclude_empty(page_data.model_dump())
        
        # 如果更新了name，检查是否重复
        await page.update_from_dict(update_data)
        await page.save()
        
        return page
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新页面失败: {str(e)}")

@router.delete(
    "/{title}",
    summary="删除页面",
)
async def delete_page(title:str):
    """删除页面"""
    try:
        page = await page_manager.get_or_none(title=title)
        if not page:
            raise HTTPException(status_code=404, detail="页面不存在")
        
        await page_manager.delete(page)
        
        return {"detail": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除页面失败: {str(e)}")

@router.patch(
    "/{page_name}/toggle",
    summary="切换页面状态",
    response_model=PageResponse,
)
async def toggle_page_status(title:str):
    """启用/禁用页面"""
    try:
        page = await page_manager.get_or_none(title=title)
        if not page:
            raise HTTPException(status_code=404, detail="页面不存在")
        
        page.is_active = not page.is_active
        await page.save()
        
        return page
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换页面状态失败: {str(e)}")