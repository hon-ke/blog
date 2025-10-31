from datetime import datetime, timedelta
from typing import Set
from typing import Optional
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status, Header,Request
from fastapi import Cookie,Query
from jose import JWTError, jwt
from config import settings
from core.meta import website_manager


# 密码哈希上下文
pwd_condes = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cookie认证方案
async def cookie_auth(request: Request, token: Optional[str] = Cookie(None, alias="token")):
    """验证Cookie中的token
    验证失败会直接返回400错误并记录WARNING级别日志
    成功返回用户对象并记录INFO级别日志
    """
    if not token:
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": True})
        name: str = payload.get("sub")
        if name:
            user = await website_manager.get_or_none(name=name)
            if user:
                # await db_log.auth.log(
                #     level="INFO",
                #     username=user.name,
                #     action="cookie_auth",
                #     ip_address=request.client.host,
                #     user_agent=request.headers.get("user-agent")
                # )
                return user
        else:
            raise JWTError

    except JWTError as e:
        # await db_log.auth.log(
        #     level="WARNING",
        #     username="unknown",
        #     action= "cookie_auth",
        #     ip_address=request.client.host,
        #     user_agent=request.headers.get("user-agent"),
        #     des=f"Token validation failed: {str(e)}"
        # )
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


async def api_key_auth(request: Request, api_key: Optional[str] = Query(None)):
    """验证API Key
    验证失败会直接返回400错误并记录WARNING级别日志
    成功返回用户对象并记录INFO级别日志
    """
    if not api_key:
        return
    try:

        user = await website_manager.get_or_none(api_key=api_key)
        if user:
            # await db_log.auth.log(
            #     level="INFO",
            #     username=user.name,
            #     action="api_key_auth",
            #     ip_address=request.client.host,
            #     user_agent=request.headers.get("user-agent")
            # )
            return user
        else:
            raise Exception
    except Exception as e:

        # await db_log.auth.log(
        #     level="WARNING",
        #     username="unknown",
        #     action="api_key_auth",
        #     ip_address=request.client.host,
        #     user_agent=request.headers.get("user-agent"),
        #     des="Invalid API key"
        # )
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


async def auth_required(
    user_from_api= Depends(api_key_auth),
    user_from_cookie= Depends(cookie_auth),
):
    """验证用户身份，如果没有认证信息则返回None"""
    # 优先使用API认证
    if user_from_api:
        return user_from_api

    # 其次使用Cookie认证
    if user_from_cookie:
        return user_from_cookie

    raise HTTPException(
        status_code=401,
        detail="未授权"
    )

def hash_password(password: str) -> str:
    return pwd_condes.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码与哈希是否匹配"""
    return pwd_condes.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    user= Depends(auth_required),
):
    return user

async def is_admin(admin= Depends(get_current_user)):
    if admin:
        return admin
    raise HTTPException(
            status_code=401,
            detail="需要管理员权限"
        )

async def is_root(root = Depends(get_current_user)):
    if root:
        return root

    raise HTTPException(
            status_code=401,
            detail="需要超级管理权限"
        )
