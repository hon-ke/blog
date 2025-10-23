from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import secrets

from core.meta import MetaModel
from core.security import pwd_condes ,api_key_auth # 请替换为您的实际密码工具模块

router = APIRouter(prefix="/meta", tags=["Meta"])
root_router = APIRouter(prefix="/root/meta")


# Pydantic 模型
class MetaUpdate(BaseModel):
    website_url: Optional[str] = None
    website_name: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    des: Optional[str] = None
    avatar: Optional[str] = None
    ip: Optional[str] = None
    key: Optional[str] = None

class MetaResponse(BaseModel):
    id: int
    website_url: str
    website_name: str
    nickname: Optional[str] = None
    des: Optional[str] = None
    avatar: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    name: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    api_key: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None

class APIKeyResponse(BaseModel):
    success: bool
    api_key: str

# 生成安全的 API Key
def generate_api_key():
    return secrets.token_urlsafe(32)

# 验证密码（使用您的工具函数）
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码与哈希是否匹配"""
    return pwd_condes.verify(plain_password, hashed_password)

@router.get("", response_model=MetaResponse)
async def get_website_meta():
    """
    获取网站元数据
    """
    meta = await MetaModel.first()
    if not meta:
        raise HTTPException(status_code=404, detail="网站元数据未配置")
    
    return meta

@root_router.put("", response_model=MetaResponse)
async def update_website_meta(
    update_data: MetaUpdate,
    current_meta: MetaModel = Depends(api_key_auth)
):
    """
    更新网站元数据（需要 API Key 认证）
    """
    update_dict = update_data.dict(exclude_unset=True)
    
    # 智能更新 - 只更新提供的字段
    await MetaModel.filter(id=current_meta.id).update(**update_dict)
    
    # 获取更新后的数据
    updated_meta = await MetaModel.get(id=current_meta.id)
    return updated_meta

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, request: Request):
    """
    用户登录，成功则返回 API Key
    """
    # 查找用户
    meta = await MetaModel.filter(name=login_data.name).first()
    if not meta:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not verify_password(login_data.password, meta.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 生成新的 API Key（如果不存在）
    if not meta.api_key:
        meta.api_key = generate_api_key()
        await meta.save()
    
    # 更新最后登录时间和 IP
    client_ip = request.client.host if request.client else "unknown"
    await MetaModel.filter(id=meta.id).update(
        last_login=datetime.now(),
        ip=client_ip
    )
    
    # 重新获取更新后的数据
    updated_meta = await MetaModel.get(id=meta.id)
    
    return LoginResponse(
        success=True,
        message="登录成功",
        api_key=updated_meta.api_key,
        user_info={
            "id": updated_meta.id,
            "name": updated_meta.name,
            "nickname": updated_meta.nickname,
            "email": updated_meta.email,
            "last_login": updated_meta.last_login
        }
    )


@router.post("/refresh-api-key", response_model=APIKeyResponse)
async def refresh_api_key(current_meta: MetaModel = Depends(api_key_auth)):
    """
    刷新 API Key（需要现有 API Key 认证）
    """
    new_api_key = generate_api_key()
    await MetaModel.filter(id=current_meta.id).update(api_key=new_api_key)
    
    return APIKeyResponse(
        success=True,
        api_key=new_api_key
    )

@router.get("/verify-api-key")
async def verify_api_key_endpoint(current_meta: MetaModel = Depends(api_key_auth)):
    """
    验证 API Key 有效性
    """
    return {
        "success": True,
        "message": "API Key 有效",
        "user_info": {
            "id": current_meta.id,
            "name": current_meta.name,
            "nickname": current_meta.nickname,
            "email": current_meta.email
        }
    }