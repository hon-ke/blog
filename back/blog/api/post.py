from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from blog.models import post_manager,PostModel
from blog.schemas import PostResponse, PostListResponse
from tortoise.expressions import Q
from core.config import settings
import re
import math

# 公开路由（无需权限）
router = APIRouter(
    prefix="/posts",
    tags=["public - 内容浏览"],
)

@router.get(
    "/",
    summary="获取公开内容列表",
    response_model=PostListResponse,
)
async def get_public_posts(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, description="每页数量"),
    category: Optional[str] = Query(None, description="分类"),
    tag: Optional[str] = Query(None, description="标签"),
):
    """获取公开内容列表（不包含私密内容）"""
    try:
        # 构建查询条件 - 只查询非私密内容
        filters = {"is_locked": False}
        if category:
            filters["category"] = category
        if tag:
            filters["tag"] = tag
        
        # 获取总数
        total = await post_manager.filter(**filters).count()
        
        # 计算总页数
        total_page = math.ceil(total / size) if total > 0 else 1
        
        # 获取分页数据
        posts = await post_manager.filter(**filters)\
            .offset((page - 1) * size)\
            .limit(size)\
            .order_by("-is_top", "-created_at")\
            .all()
        
        return PostListResponse(
            posts=posts,
            total=total,
            total_page=total_page,
            current_page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取列表失败: {str(e)}"
        )

@router.get(
    "/exists",
)
async def is_exists(title: str):
    """检查文章是否存在"""
    if not title:
        return {"error": "请输入文章标题"}
    
    try:
        post = await post_manager.get_or_none(title=title)
        if not post:
            return {"is_exists": False}

        return {"is_exists": True}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查失败: {str(e)}"
        )

@router.get(
    "/like",
    summary="点赞文章",
)
async def like(post_id: int = Query(..., description="文章ID")):
    post = await post_manager.get_or_none(id=post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    post.like += 1
    await post.save()
    
    return {
        "status": 200,
        "message": "点赞成功",
        "like_count": post.like
    }

@router.get(
    "/categories",
)
async def get_all_categories():
    categories = await post_manager.filter().values("category")
    if not categories:
        # 如果没有分类，默认加载预设的分类
        if settings.PRESET_CATEGORIES:
            return settings.PRESET_CATEGORIES
        return []
    
    return set([x.get("category","") for x in categories] + settings.PRESET_CATEGORIES)

@router.get(
    "/all",
)
async def get_all_posts():
    posts = await post_manager.filter().values("title")
    if not posts:
        return []
    return set([x.get("title","") for x in posts])

@router.get(
    "/archive",
    summary="文章归档",
    response_model=List[dict],
)
async def get_posts_archive():
    """按照年份归档文章"""
    try:
        # 获取所有公开文章，按创建时间降序排列
        posts = await post_manager.filter(is_locked=False)\
            .order_by("-created_at")\
            .all().exclude(category="笔记")
        
        # 按年份分组
        archive_dict = {}
        for post in posts:
            # 提取年份
            year = post.created_at.year
            
            # 初始化年份分组
            if year not in archive_dict:
                archive_dict[year] = []
            
            # 添加文章信息
            archive_dict[year].append({
                "time": post.created_at.strftime("%Y-%m-%d"),
                "title": post.title,
                "id": post.id
            })
        
        # 转换为要求的格式并按年份倒序排列
        result = []
        for year in sorted(archive_dict.keys(), reverse=True):
            result.append({
                "date": str(year),  # 年份作为字符串
                "data": archive_dict[year]
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取归档失败: {str(e)}"
        )

def highlight_keyword(text: str, keyword: str, context_length: int = 100) -> str:
    """
    高亮显示关键词，并截取前后文本
    """
    if not text or not keyword:
        return text
    
    # 转义正则特殊字符
    escaped_keyword = re.escape(keyword)
    
    # 查找所有匹配位置
    matches = list(re.finditer(escaped_keyword, text, re.IGNORECASE))
    
    if not matches:
        # 如果没有匹配，返回前context_length个字符
        return text[:context_length] + "..." if len(text) > context_length else text
    
    # 取第一个匹配位置
    first_match = matches[0]
    start_pos = first_match.start()
    end_pos = first_match.end()
    
    # 计算截取范围
    context_start = max(0, start_pos - context_length)
    context_end = min(len(text), end_pos + context_length)
    
    # 截取文本
    excerpt = text[context_start:context_end]
    
    # 添加省略号
    prefix = "..." if context_start > 0 else ""
    suffix = "..." if context_end < len(text) else ""
    
    # 高亮关键词
    highlighted_excerpt = re.sub(
        escaped_keyword, 
        lambda m: f'<span style="color: #ff0000; font-weight: bold;">{m.group()}</span>', 
        excerpt, 
        flags=re.IGNORECASE
    )
    
    return f"{prefix}{highlighted_excerpt}{suffix}"



@router.get("/search")
async def search_posts(q: str = Query(...)):
    """
    使用Model方法的简单搜索
    """
    if not q or not q.strip():
        return []
    
    keyword = q.strip()
    
    try:
        # 使用Model的filter方法进行模糊匹配
        posts = await PostModel.filter(
            content__icontains=keyword
        ).order_by("-is_top", "-created_at")
        
        # 转换为字典列表
        posts_data = []
        for post in posts:
            post_data = {
                "id": post.id,
                "title": post.title,
                "content": highlight_keyword(post.content,keyword),
                "category":post.category,
            }
            posts_data.append(post_data)
        
        return posts_data
        
    except Exception as e:
        print(f"搜索错误: {e}")
        return []

@router.get(
    "/title/{title}",
    summary="获取公开内容详情",
    response_model=PostResponse,
)
async def get_public_post(
    title: str,
):
    """获取公开内容详情（无法查看私密内容）"""
    try:
        post = await post_manager.get_or_none(title=title, is_locked=False)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在或无权访问"
            )
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详情失败: {str(e)}"
        )

@router.get(
    "/{id}",
    summary="获取公开内容详情",
    response_model=PostResponse,
)
async def get_public_post(
    id: int,
):
    """获取公开内容详情（无法查看私密内容）"""
    try:
        post = await post_manager.get_or_none(id=id, is_locked=False)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在或无权访问"
            )
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取详情失败: {str(e)}"
        )
    


