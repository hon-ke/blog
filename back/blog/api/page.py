from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from blog.models import page_manager
from blog.schemas import PublicPageInfoResponse, PublicPageDetailResponse, PageListResponse



# 公开路由
router = APIRouter(prefix="/pages", tags=["public - 页面"])

@router.get(
    "/",
    summary="获取页面基本信息列表",
    response_model=List[PublicPageInfoResponse],
)

async def get_public_pages():
    """获取所有启用的页面基本信息（不包含内容）"""
    try:
        pages = await page_manager.filter(
            is_active=True
        ).all()

        if pages:
            return pages
        else:
            # 预设的页面
            return []
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"页面获取失败: {str(e)}")

@router.get("/all")
async def get_all_posts():
    pages = await page_manager.filter(is_active=True).values("title")
    if not pages:
        return []
    return set([x.get("title","") for x in pages])


@router.get(
    "/{title}",
    summary="获取页面完整详情",
    response_model=PublicPageDetailResponse,
)
async def get_public_page(title: str,):
    """根据页面标识获取页面完整详情（包含内容）"""
    try:
        page = await page_manager.get_or_none(title=title, is_active=True)

        if not page:
            raise HTTPException(status_code=404, detail=f"页面未找到")
        return page

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取页面详情失败: {str(e)}")

