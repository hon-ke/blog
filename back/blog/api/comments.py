from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from blog.models import comment_manager, post_manager
from core.meta import website_manager
from datetime import datetime

router = APIRouter(prefix="/comments", tags=["comments"])

# Pydantic模型
class CommentCreate(BaseModel):
    post_id: int
    author_name: str
    author_email: str
    author_website: Optional[str] = None
    content: str
    is_anonymous: bool = False
    api_key: Optional[str] = None  # 新增 API Key 字段

class CommentResponse(BaseModel):
    id: int
    author_name:  Optional[str]
    author_website: Optional[str]
    content: str
    is_anonymous:  Optional[bool] = False
    is_superuser: Optional[bool] = False
    created_at: datetime
    
    class Config:
        from_attributes = True

# 获取文章评论
@router.get("/post/{post_id}", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: int,
    page: int = 1,
    page_size: int = 20
):
    """获取指定文章的评论列表"""
    # 检查文章是否存在
    post = await post_manager.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 获取已审核的评论
    comments = await comment_manager.filter(
        post_id=post_id,
        is_approved=True
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return comments

# 提交评论
@router.post("/", response_model=CommentResponse)
async def create_comment(comment_data: CommentCreate, request: Request):
    """提交新评论"""
    # 验证文章是否存在
    post = await post_manager.get_or_none(id=comment_data.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 验证评论内容
    if not comment_data.content.strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")
    
    if len(comment_data.content) > 500:
        raise HTTPException(status_code=400, detail="评论内容不能超过500字")
    
    # 检查 API Key 并设置 is_superuser
    is_superuser = False
    website_config = None
    
    if comment_data.api_key:
        # 从网站配置中获取 API Key 进行验证
        website_config = await website_manager.first()
        if website_config and website_config.api_key:
            if comment_data.api_key == website_config.api_key:
                is_superuser = True
    
    # 如果是超级用户，使用 meta 表中的数据
    if is_superuser and website_config:
        author_name = website_config.nickname or website_config.name
        author_email = website_config.email or ""
        author_website = website_config.website_url or ""
    else:
        author_name = comment_data.author_name.strip()
        author_email = comment_data.author_email.strip()
        author_website = comment_data.author_website.strip() if comment_data.author_website else None
    
    # 创建评论
    comment = await comment_manager.create(
        post_id=comment_data.post_id,
        author_name=author_name,
        author_email=author_email,
        author_website=author_website,
        content=comment_data.content.strip(),
        is_anonymous=comment_data.is_anonymous,
        is_superuser=is_superuser,  # 设置超级用户标志
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return comment

# 获取评论统计
@router.get("/post/{post_id}/count")
async def get_comment_count(post_id: int):
    """获取文章的评论数量"""
    count = await comment_manager.filter(
        post_id=post_id,
        is_approved=True
    ).count()
    
    return {"post_id": post_id, "comment_count": count}
