import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from blog.models import post_manager
from blog.schemas import (
    PostResponse, PostCreate, PostUpdate, PostListResponse
)
from blog.tools import exclude_empty
# 管理路由（需要管理员权限）
router = APIRouter(
    prefix="/admin/posts",
    tags=["admin - 文章管理"],
)

@router.post(
    "/",
    summary="创建内容",
    response_model=PostResponse,
)
async def create_post(
    post_data: PostCreate,
):
    """创建新内容"""
    try:
        # 验证标题唯一性
        if post_data.title:
            if await post_manager.exists(title=post_data.title):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="文章标题已存在"
                )

        # 设置默认分类
        if not post_data.category:
            post_data.category = "默认"

        if post_data.is_top:
            toped_post =  await post_manager.filter(is_top=True)
            for x in toped_post:
                x.is_top = False
                await x.save()

        # 创建帖子
        if not post_data.title:
            post_data.title = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        create_data = exclude_empty(post_data.model_dump())
        new_post = await post_manager.create(
            **create_data
        )

        return new_post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建失败: {str(e)}"
        )

@router.get(
    "/{post_title}",
    summary="获取内容详情",
    response_model=PostResponse,
)
async def get_post(
    post_title: str,
):
    """获取内容详情（管理员可见私密内容）"""
    try:
        post = await post_manager.get_or_none(title=post_title)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在"
            )
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详情失败: {str(e)}"
        )

@router.put(
    "/{post_title}",
    summary="更新内容",
    response_model=PostResponse,
)
async def update_post(
    post_title: str,
    post_data: PostUpdate,
):
    """更新内容"""
    try:
        post = await post_manager.get_or_none(title=post_title)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在"
            )

        # 验证标题唯一性（标题有更新时）
        update_data = exclude_empty(post_data.model_dump())
        if "title" in update_data and update_data["title"]:
            existing = await post_manager.filter(
                title=update_data["title"]
            ).exclude(id=post.id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="文章标题已存在"
                )

        await post.update_from_dict(update_data)
        await post.save()

        return post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )

@router.delete(
    "/{title}",
    summary="删除内容",
)
async def delete_post(
    title: str,
):
    """删除内容"""
    try:
        post = await post_manager.get_or_none(title=title)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在"
            )

        await post_manager.delete(post)

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "删除成功",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )

@router.patch(
    "/{title}/top",
    summary="置顶/取消置顶",
    response_model=PostResponse,
)
async def toggle_top(
    title: str,
    is_top: bool = Query(..., description="是否置顶"),
):
    """置顶或取消置顶内容"""
    try:
        post = await post_manager.get_or_none(title=title)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在"
            )

        post.is_top = is_top
        await post.save()

        return post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )

@router.patch(
    "/{title}/lock",
    summary="锁定/解锁内容",
    response_model=PostResponse,
)
async def toggle_lock(
    title: str,
    is_locked: bool = Query(..., description="是否锁定"),
):
    """锁定或解锁内容（设为私密/公开）"""
    try:
        post = await post_manager.get_or_none(str=title)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在"
            )

        post.is_locked = is_locked
        await post.save()

        return post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )
