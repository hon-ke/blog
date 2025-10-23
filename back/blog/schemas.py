from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# 基础模型
class PostBase(BaseModel):
    content: str
    title: Optional[str] = ""
    excerpt: Optional[str] = "随便写点内容当描述..."
    tag: Optional[str] = ""
    category: Optional[str] = ""
    cover: Optional[str] = ""
    is_top: Optional[bool]  = False
    is_locked: Optional[bool]  = False
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('内容不能为空')
        return v.strip()

# 创建请求模型
class PostCreate(PostBase):
    pass

# 更新请求模型
class PostUpdate(BaseModel):
    content: Optional[str] = ""
    title: Optional[str] = ""
    excerpt: Optional[str] = "随便写点内容当描述..."
    tag: Optional[str] = ""
    category: Optional[str] = ""
    cover: Optional[str] = ""
    is_top: Optional[bool] = False
    is_locked: Optional[bool] = False

# 响应模型
class PostResponse(PostBase):
    id: int
    like: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 列表响应模型
class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    total_page: int
    current_page: int
    size: int

# 基础模型
class PageBase(BaseModel):
    title: str = ""
    description: Optional[str] = ""
    icon: Optional[str]  = ""
    is_active: Optional[bool]  = ""
    order: Optional[int] = ""
    
# 创建请求模型
class PageCreate(PageBase):
    content: str = ""

# 更新请求模型
class PageUpdate(PageBase):
    title: Optional[str] = ""
    description: Optional[str] = ""
    icon: Optional[str] = ""
    content: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = ""

# 完整响应模型（包含内容）
class PageResponse(PageBase):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 导航页面响应模型（不包含内容）
class NavPageResponse(BaseModel):
    title: str
    description: Optional[str]
    icon: str
    order: int
    
    class Config:
        from_attributes = True

# 公开页面基本信息响应模型（不包含内容）
class PublicPageInfoResponse(BaseModel):
    title: str
    description: Optional[str]
    icon: str
    order: int
    
    class Config:
        from_attributes = True

# 公开页面完整响应模型（包含内容）
class PublicPageDetailResponse(BaseModel):
    title: str
    description: Optional[str]
    icon: str
    content: str
    order: int
    is_active:bool
    class Config:
        from_attributes = True

# 列表响应模型
class PageListResponse(BaseModel):
    pages: List[PageResponse]
    total: int