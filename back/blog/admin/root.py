from fastapi import APIRouter, HTTPException,UploadFile,File
from fastapi.responses import JSONResponse,FileResponse
from tortoise.transactions import in_transaction
from blog.models import PostModel, CommentModel, PageModel
from core.config import settings
from datetime import datetime
from pathlib import Path
import zipfile
import tempfile
import json
import os


router = APIRouter()

@router.get("/root/export/data")
async def export_dump():
    """
    导出所有数据为JSON格式
    """
    try:
        # 获取所有帖子数据
        posts = await PostModel.all()
        posts_data = []
        
        for post in posts:
            # 获取该帖子的所有评论
            comments = await CommentModel.filter(post_id=post.id).all()
            
            post_data = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "excerpt": post.excerpt,
                "tag": post.tag,
                "category": post.category,
                "cover": post.cover,
                "is_top": post.is_top,
                "is_locked": post.is_locked,
                "like": post.like,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
                "comments": [
                    {
                        "id": comment.id,
                        "author_name": comment.author_name,
                        "author_email": comment.author_email,
                        "author_website": comment.author_website,
                        "content": comment.content,
                        "is_anonymous": comment.is_anonymous,
                        "is_superuser": comment.is_superuser,
                        "is_approved": comment.is_approved,
                        "ip_address": comment.ip_address,
                        "user_agent": comment.user_agent,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                        "updated_at": comment.updated_at.isoformat() if comment.updated_at else None
                    }
                    for comment in comments
                ]
            }
            posts_data.append(post_data)
        
        # 获取所有页面数据
        pages = await PageModel.all()
        pages_data = [
            {
                "id": page.id,
                "title": page.title,
                "description": page.description,
                "link": page.link,
                "icon": page.icon,
                "content": page.content,
                "is_active": page.is_active,
                "order": page.order,
                "created_at": page.created_at.isoformat() if page.created_at else None,
                "updated_at": page.updated_at.isoformat() if page.updated_at else None
            }
            for page in pages
        ]
        
        # 构建完整的数据结构
        export_data = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "version": "1.0",
                "total_posts": len(posts_data),
                "total_pages": len(pages_data),
                "total_comments": sum(len(post["comments"]) for post in posts_data)
            },
            "posts": posts_data,
            "pages": pages_data
        }
        
        # 返回JSON响应，设置下载头
        return JSONResponse(
            content=export_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出数据时发生错误: {str(e)}")
    

@router.post("/root/import/data")
async def import_dump(file: UploadFile = File(...)):
    """
    导入JSON格式的数据
    """
    # 检查文件类型
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持JSON格式文件")
    
    try:
        # 读取文件内容
        content = await file.read()
        data = json.loads(content)
        
        # 验证数据结构
        if not isinstance(data, dict) or 'posts' not in data or 'pages' not in data:
            raise HTTPException(status_code=400, detail="无效的数据格式")
        
        # 使用事务确保数据一致性
        async with in_transaction():
            # 导入页面数据
            pages_imported = 0
            for page_data in data.get('pages', []):
                page_id = page_data.get('id')
                
                # 检查是否已存在
                existing_page = await PageModel.filter(id=page_id).first()
                
                page_fields = {
                    "title": page_data.get('title'),
                    "description": page_data.get('description'),
                    "link": page_data.get('link'),
                    "icon": page_data.get('icon', 'czs-circle'),
                    "content": page_data.get('content', ''),
                    "is_active": page_data.get('is_active', True),
                    "order": page_data.get('order', 10)
                }
                
                if existing_page:
                    # 更新现有页面
                    await PageModel.filter(id=page_id).update(**page_fields)
                else:
                    # 创建新页面
                    await PageModel.create(id=page_id, **page_fields)
                
                pages_imported += 1
            
            # 导入帖子数据
            posts_imported = 0
            comments_imported = 0
            
            for post_data in data.get('posts', []):
                post_id = post_data.get('id')
                
                # 检查是否已存在
                existing_post = await PostModel.filter(id=post_id).first()
                
                post_fields = {
                    "title": post_data.get('title'),
                    "content": post_data.get('content'),
                    "excerpt": post_data.get('excerpt'),
                    "tag": post_data.get('tag', ''),
                    "category": post_data.get('category', '默认'),
                    "cover": post_data.get('cover', ''),
                    "is_top": post_data.get('is_top', False),
                    "is_locked": post_data.get('is_locked', False),
                    "like": post_data.get('like', 0)
                }
                
                if existing_post:
                    # 更新现有帖子
                    await PostModel.filter(id=post_id).update(**post_fields)
                    post = existing_post
                else:
                    # 创建新帖子
                    post = await PostModel.create(id=post_id, **post_fields)
                
                posts_imported += 1
                
                # 导入该帖子的评论
                for comment_data in post_data.get('comments', []):
                    comment_id = comment_data.get('id')
                    
                    # 检查是否已存在
                    existing_comment = await CommentModel.filter(id=comment_id).first()
                    
                    comment_fields = {
                        "post_id": post.id,
                        "author_name": comment_data.get('author_name'),
                        "author_email": comment_data.get('author_email'),
                        "author_website": comment_data.get('author_website'),
                        "content": comment_data.get('content'),
                        "is_anonymous": comment_data.get('is_anonymous', False),
                        "is_superuser": comment_data.get('is_superuser', False),
                        "is_approved": comment_data.get('is_approved', True),
                        "ip_address": comment_data.get('ip_address'),
                        "user_agent": comment_data.get('user_agent')
                    }
                    
                    if existing_comment:
                        # 更新现有评论
                        await CommentModel.filter(id=comment_id).update(**comment_fields)
                    else:
                        # 创建新评论
                        await CommentModel.create(id=comment_id, **comment_fields)
                    
                    comments_imported += 1
        
        return {
            "message": "数据导入成功",
            "summary": {
                "pages_imported": pages_imported,
                "posts_imported": posts_imported,
                "comments_imported": comments_imported,
                "imported_at": datetime.now().isoformat()
            }
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入数据时发生错误: {str(e)}")


@router.post("/root/validate")
async def validate_import_file(file: UploadFile = File(...)):
    """
    验证导入文件格式是否正确
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持JSON格式文件")
    
    try:
        content = await file.read()
        data = json.loads(content)
        
        # 基本结构验证
        if not isinstance(data, dict):
            return {"valid": False, "error": "根元素必须是对象"}
        
        if 'posts' not in data or 'pages' not in data:
            return {"valid": False, "error": "缺少必要的posts或pages字段"}
        
        if not isinstance(data['posts'], list) or not isinstance(data['pages'], list):
            return {"valid": False, "error": "posts和pages必须是数组"}
        
        # 验证帖子数据结构
        for i, post in enumerate(data['posts']):
            if not isinstance(post, dict):
                return {"valid": False, "error": f"帖子数据 {i} 必须是对象"}
            
            required_fields = ['id', 'title', 'content']
            for field in required_fields:
                if field not in post:
                    return {"valid": False, "error": f"帖子 {i} 缺少必要字段: {field}"}
            
            # 验证评论数据
            if 'comments' in post and isinstance(post['comments'], list):
                for j, comment in enumerate(post['comments']):
                    if not isinstance(comment, dict):
                        return {"valid": False, "error": f"帖子 {i} 的评论 {j} 必须是对象"}
                    
                    comment_required = ['id', 'author_name', 'author_email', 'content']
                    for field in comment_required:
                        if field not in comment:
                            return {"valid": False, "error": f"帖子 {i} 的评论 {j} 缺少必要字段: {field}"}
        
        # 验证页面数据结构
        for i, page in enumerate(data['pages']):
            if not isinstance(page, dict):
                return {"valid": False, "error": f"页面数据 {i} 必须是对象"}
            
            page_required = ['id', 'title', 'link']
            for field in page_required:
                if field not in page:
                    return {"valid": False, "error": f"页面 {i} 缺少必要字段: {field}"}
        
        return {
            "valid": True,
            "summary": {
                "posts_count": len(data['posts']),
                "pages_count": len(data['pages']),
                "comments_count": sum(len(post.get('comments', [])) for post in data['posts'])
            }
        }
        
    except json.JSONDecodeError:
        return {"valid": False, "error": "无效的JSON格式"}
    except Exception as e:
        return {"valid": False, "error": f"验证文件时发生错误: {str(e)}"}
    

@router.get("/root/export/static")
async def export_static_files():
    """
    将静态文件目录打包成ZIP文件并下载
    """
    static_dir = settings.STATIC_DIR  # 静态文件目录
    
    try:
        static_path = Path(static_dir)
        
        # 检查目录是否存在
        if not static_path.exists():
            raise HTTPException(status_code=404, detail=f"静态文件目录 '{static_dir}' 不存在")
        
        # 创建临时ZIP文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"static_files_{timestamp}.zip"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name
        
        # 创建ZIP文件
        files_added = 0
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in static_path.rglob('*'):
                if file_path.is_file():
                    # 计算在ZIP中的相对路径
                    arcname = file_path.relative_to(static_path)
                    zipf.write(file_path, arcname)
                    files_added += 1
        
        # 如果没有找到任何文件
        if files_added == 0:
            os.unlink(zip_path)  # 删除临时文件
            raise HTTPException(status_code=404, detail="静态文件目录中没有找到任何文件")
        
        # 返回ZIP文件
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{zip_filename}"'
            }
        )
        
    except Exception as e:
        # 清理临时文件（如果存在）
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.unlink(zip_path)
        raise HTTPException(status_code=500, detail=f"导出静态文件时发生错误: {str(e)}")
    




@router.post("/root/import/static")
async def import_static_files(file: UploadFile = File(...)):
    """
    导入ZIP格式的静态文件，解压到静态文件目录
    """
    # 检查文件类型
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="只支持ZIP格式文件")
    
    static_dir = settings.STATIC_DIR  # 静态文件目录
    static_path = Path(static_dir)
    
    try:
        # 确保静态文件目录存在
        static_path.mkdir(parents=True, exist_ok=True)
        
        # 创建临时目录存放上传的ZIP文件
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_file_path = temp_path / file.filename
            
            # 保存上传的ZIP文件
            content = await file.read()
            with open(zip_file_path, 'wb') as f:
                f.write(content)
            
            # 解压ZIP文件
            files_extracted = 0
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # 获取ZIP文件中的所有文件列表
                file_list = zip_ref.namelist()
                
                # 解压所有文件到静态文件目录
                zip_ref.extractall(static_path)
                files_extracted = len(file_list)
            
            # 记录解压的文件信息
            extracted_files = []
            for file_name in file_list:
                extracted_files.append({
                    "name": file_name,
                    "path": str(static_path / file_name)
                })
        
        return {
            "message": "静态文件导入成功",
            "summary": {
                "files_extracted": files_extracted,
                "target_directory": str(static_path),
                "imported_at": datetime.now().isoformat()
            },
            "files": extracted_files
        }
        
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="无效的ZIP文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入静态文件时发生错误: {str(e)}")