from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from urllib.parse import unquote

from core.config import settings
from blog.models import PostModel, page_manager,post_manager

from datetime import datetime
from pathlib import Path
from typing import List
from PIL import Image
import mimetypes
import aiofiles
import magic
import os
import re
import io

router = APIRouter(prefix="/file", tags=["文件上传"])

class UploadConfig:
    """上传配置类"""
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 50MB
    UPLOAD_DIR = settings.STATIC_DIR

    # 允许的文件类型
    ALLOWED_TYPES = {
        'images': ["image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"],
        'videos': ["video/mp4", "video/avi", "video/mov", "video/webm", "video/quicktime"],
        'documents': [
            "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain", "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/zip", "application/x-rar-compressed"
        ]
    }

    # 图片压缩配置
    COMPRESS_ENABLED = True
    MAX_IMAGE_SIZE = (1920, 1080)
    QUALITY = {
        'jpeg': 85,
        'webp': 80
    }
    PNG_COMPRESS_LEVEL = 6

def ensure_directories():
    """确保上传目录存在"""
    os.makedirs(os.path.join(UploadConfig.UPLOAD_DIR, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(UploadConfig.UPLOAD_DIR, "compressed"), exist_ok=True)

def get_file_type(content: bytes, filename: str) -> str:
    """获取并验证文件类型"""
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(content)

        # 检查是否在允许的类型中
        allowed_types = (
            UploadConfig.ALLOWED_TYPES['images'] +
            UploadConfig.ALLOWED_TYPES['videos'] +
            UploadConfig.ALLOWED_TYPES['documents']
        )

        if mime_type in allowed_types:
            return mime_type
    except:
        pass

    # 通过文件扩展名判断
    ext_map = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.png': 'image/png', '.gif': 'image/gif',
        '.webp': 'image/webp', '.mp4': 'video/mp4',
        '.pdf': 'application/pdf'
    }

    ext = os.path.splitext(filename)[1].lower()
    return ext_map.get(ext, 'application/octet-stream')

def generate_filename(original_name: str, upload_dir: str) -> str:
    """生成唯一文件名"""
    base_name, ext = os.path.splitext(original_name)
    filename = original_name

    counter = 1
    while os.path.exists(os.path.join(upload_dir, filename)):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}_{counter}{ext}" if counter > 1 else f"{base_name}_{timestamp}{ext}"
        counter += 1

    return filename

def compress_image(content: bytes, mime_type: str) -> tuple[bytes, str]:
    """压缩图片"""
    try:
        image = Image.open(io.BytesIO(content))
        original_size = image.size

        # 调整尺寸
        if original_size[0] > UploadConfig.MAX_IMAGE_SIZE[0] or original_size[1] > UploadConfig.MAX_IMAGE_SIZE[1]:
            ratio = min(
                UploadConfig.MAX_IMAGE_SIZE[0] / original_size[0],
                UploadConfig.MAX_IMAGE_SIZE[1] / original_size[1]
            )
            new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # 转换为RGB模式
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # 保存压缩图片
        output = io.BytesIO()

        if mime_type == 'image/jpeg':
            image.save(output, 'JPEG', quality=UploadConfig.QUALITY['jpeg'], optimize=True)
            new_type = 'image/jpeg'
        elif mime_type == 'image/png':
            image.save(output, 'PNG', optimize=True, compress_level=UploadConfig.PNG_COMPRESS_LEVEL)
            new_type = 'image/png'
        elif mime_type == 'image/webp':
            image.save(output, 'WEBP', quality=UploadConfig.QUALITY['webp'], method=6)
            new_type = 'image/webp'
        else:
            image.save(output, 'WEBP', quality=UploadConfig.QUALITY['webp'], method=6)
            new_type = 'image/webp'

        return output.getvalue(), new_type

    except Exception as e:
        print(f"图片压缩失败: {str(e)}")
        return content, mime_type

def should_compress(mime_type: str, file_size: int) -> bool:
    """判断是否需要压缩"""
    return (UploadConfig.COMPRESS_ENABLED and
            mime_type.startswith('image/') and
            file_size > 100 * 1024)

def format_size(bytes_size: int) -> str:
    """格式化文件大小"""
    if bytes_size < 1024 * 1024:
        return f"{round(bytes_size / 1024, 1)}KB"
    return f"{round(bytes_size / (1024 * 1024), 1)}MB"

async def upload_file(file: UploadFile) -> dict:
    """处理单个文件上传"""
    content = await file.read()
    file_size = len(content)

    # 验证文件大小
    if file_size > UploadConfig.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制 ({UploadConfig.MAX_FILE_SIZE / 1024 / 1024}MB)"
        )

    # 验证文件类型
    mime_type = get_file_type(content, file.filename)
    if mime_type == 'application/octet-stream':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file.filename}"
        )

    # 保存原文件
    upload_dir = os.path.join(UploadConfig.UPLOAD_DIR, "uploads")
    filename = generate_filename(file.filename, upload_dir)
    file_path = os.path.join(upload_dir, filename)

    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    # 构建响应数据
    result = {
        "success": True,
        "filename": file.filename,
        "url": f"{settings.SERVER}/static/uploads/{filename}",
        "size": format_size(file_size),
        "mime_type": mime_type,
        "compressed": False
    }

    # 图片压缩处理
    if should_compress(mime_type, file_size):
        try:
            compressed_content, compressed_type = compress_image(content, mime_type)
            compressed_size = len(compressed_content)

            # 保存压缩文件
            compressed_dir = os.path.join(UploadConfig.UPLOAD_DIR, "compressed")
            compressed_path = os.path.join(compressed_dir, filename)

            async with aiofiles.open(compressed_path, 'wb') as f:
                await f.write(compressed_content)

            # 更新结果
            result.update({
                "compressed_url": f"{settings.SERVER}/static/compressed/{filename}",
                "compressed_size": format_size(compressed_size),
                "compressed_mime_type": compressed_type,
                "compressed": True,
                "compression_ratio": round((1 - compressed_size / file_size) * 100, 1)
            })

        except Exception as e:
            print(f"图片压缩失败: {str(e)}")

    return result

# 初始化目录
ensure_directories()

@router.post("/single", summary="单文件上传")
async def upload_single(file: UploadFile = File(...)):
    """单文件上传接口"""
    try:
        return await upload_file(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post("/multi", summary="多文件上传")
async def upload_multiple(files: List[UploadFile] = File(...)):
    """多文件上传接口"""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有接收到文件"
        )

    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="一次最多上传20个文件"
        )

    results = []
    for file in files:
        try:
            result = await upload_file(file)
            results.append(result)
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": e.detail
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"上传失败: {str(e)}"
            })

    success_count = len([r for r in results if r.get('success')])
    return {
        "success": True,
        "message": f"成功处理 {success_count} 个文件",
        "results": results
    }



# 确保静态目录存在
def get_safe_path(file_path: str) -> Path:
    """获取安全的文件路径，防止目录遍历攻击"""
    # 解码URL编码的路径
    decoded_path = unquote(file_path)

    static_path = Path(settings.STATIC_DIR).resolve()
    full_path = (static_path / decoded_path).resolve()

    # 确保文件在static目录内
    if not str(full_path).startswith(str(static_path)):
        raise HTTPException(status_code=400, detail="无效的文件路径")

    return full_path

@router.get("/{file_path:path}")
async def download_file(file_path: str, as_attachment: bool = True):
    """
    下载文件，支持子目录路径
    """
    try:
        full_path = get_safe_path(file_path)

        if not full_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")

        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="请求的路径不是文件")

        # 获取文件类型
        mime_type, _ = mimetypes.guess_type(str(full_path))

        # 获取文件名用于下载
        filename = Path(file_path).name

        return FileResponse(
            path=full_path,
            filename=filename if as_attachment else None,
            media_type=mime_type
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

def find_attachments(markdown_content:str) -> List[str]:
    """
    从 Markdown 内容中提取所有以 /static/ 开头的附件路径

    Args:
        markdown_content: Markdown 文本内容

    Returns:
        附件路径列表（去重后的）
    """
    # 匹配 Markdown 中常见的资源引用格式
    patterns = [
        # 图片: ![alt](/static/image.png) 或 ![alt](/static/image.png "title")
        r'!\[.*?\]\(\s*(/static/[^)\s]+)(?:\s+[^)]*)?\s*\)',
        # 链接: [text](/static/file.pdf) 或 [text](/static/file.pdf "title")
        r'\[.*?\]\(\s*(/static/[^)\s]+)(?:\s+[^)]*)?\s*\)',
        # HTML img 标签: <img src="/static/image.jpg">
        r'<img[^>]*src=["\'](/static/[^"\']+)["\'][^>]*>',
        # HTML a 标签: <a href="/static/file.pdf">
        r'<a[^>]*href=["\'](/static/[^"\']+)["\'][^>]*>',
        # 直接路径
        r'(?<!`)(/static/[^\s<>"\'\)]+)'
    ]

    attachments = []

    for pattern in patterns:
        matches = re.findall(pattern, markdown_content, re.IGNORECASE)
        for match in matches:
            # 清理路径，移除查询参数和可能的标题文本
            clean_path = match.split('?')[0].split('#')[0].strip()
            clean_path = clean_path.split('"')[0].strip()  # 移除标题文本

            if clean_path and clean_path.startswith('/static/'):
                attachments.append(clean_path)

    # 去重并返回
    return list(set(attachments))


def get_all_static_files(static_dir: str) -> List[str]:
    """
    递归获取 static 目录下的所有文件

    Args:
        static_dir: static 目录的路径

    Returns:
        所有文件的绝对路径列表
    """
    static_path = Path(static_dir)
    if not static_path.exists():
        return []

    all_files = []

    # 递归遍历所有文件和子目录
    for file_path in static_path.rglob("*"):
        if file_path.is_file():
            relative_path = str(file_path.relative_to(static_path))
            all_files.append(str(relative_path))

    return all_files

@router.delete("/clean")
async def clean():
    post_content = await post_manager.filter().values("cover","content")
    page_content = await page_manager.filter().values("content")

    # 正确的方式：使用列表推导式提取 content 字段
    post_list_from_content = [item["content"] for item in post_content]
    post_list_form_cover = [item["cover"] for item in post_content]
    print(post_list_form_cover)
    print(len(post_list_form_cover))
    page_content_list = [item["content"] for item in page_content]

    # 合并所有内容
    all_content = "".join( post_list_from_content+post_list_form_cover + page_content_list)

    # 压缩后的和未压缩的
    attach_list =  find_attachments(all_content)
    attach_list += [x.replace("compressed","uploads",1) for x in attach_list if "compressed" in x]
    attach_list = [x.replace("/static/","",1)for x in attach_list]

    # print(attach_list)

    static_files =  get_all_static_files(settings.STATIC_DIR)

    remove_list = set(static_files)-set(attach_list)

    # print(len(remove_list),len(static_files),len(attach_list))
    removed  = 0
    for index,x in enumerate(remove_list,1):
        os.remove(settings.STATIC_DIR+"/"+x)
        removed+=1

    # print({"Total":len(static_files),"Used":len(attach_list),"Removed":removed})

    return {"Total":len(static_files),"Used":len(attach_list),"Removed":removed}
