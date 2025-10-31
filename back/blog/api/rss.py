from fastapi import APIRouter, Response
from tortoise.expressions import Q
from datetime import datetime
import markdown
import re

from blog.models import PostModel

router = APIRouter()

# 博客配置信息 - 请根据实际情况修改
BLOG_CONFIG = {
    "title": "你的博客名称",
    "link": "https://yourblog.com",  # 你的博客域名
    "description": "你的博客描述"
}

def markdown_to_html(md_text: str) -> str:
    """
    将 Markdown 转换为 HTML，支持完整功能
    包括代码高亮 (hljs)、表格、目录等
    """
    if not md_text:
        return ""

    # 配置 Markdown 扩展
    extensions = [
        'markdown.extensions.extra',      # 包含表格、缩写等
        'markdown.extensions.codehilite', # 代码高亮
        # 'markdown.extensions.toc',        # 目录生成
        'markdown.extensions.smarty',     # 智能标点
        'markdown.extensions.nl2br',      # 换行转 <br>
        'markdown.extensions.sane_lists', # 更合理的列表
        'markdown.extensions.fenced_code', # 围栏代码块
    ]

    extension_configs = {
        'codehilite': {
            'css_class': 'hljs',
            'use_pygments': False,  # 使用 hljs 而不是 pygments
            'guess_lang': True,
        },
        'toc': {
            'permalink': True,
        }
    }

    html = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs=extension_configs
    )

    return html

def escape_xml_text(text: str) -> str:
    """
    转义 XML 文本中的特殊字符
    """
    if not text:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def generate_rss_xml(posts, title: str, link: str, description: str, category: str = None) -> str:
    """
    生成完整的 RSS XML - 手动构建确保格式正确
    """
    # 构建 XML 字符串
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">')
    xml_parts.append('<channel>')

    # 频道信息
    channel_title = escape_xml_text(f"{title} - {category}" if category else title)
    channel_link = escape_xml_text(f"{link}/category/{category}" if category else link)
    channel_description = escape_xml_text(f"{description} - {category}分类" if category else description)

    xml_parts.append(f'<title>{channel_title}</title>')
    xml_parts.append(f'<link>{channel_link}</link>')
    xml_parts.append(f'<description>{channel_description}</description>')
    xml_parts.append('<language>zh-CN</language>')
    xml_parts.append(f'<lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>')
    xml_parts.append('<generator>FastAPI Blog RSS</generator>')

    # 文章项
    for post in posts:
        post_link = escape_xml_text(f"{link}/posts/{post.id}")
        description_text = post.excerpt or (post.content[:200] + "..." if len(post.content) > 200 else post.content)
        description_text = re.sub(r'[#*`\[\]]', '', description_text)
        description_text = escape_xml_text(description_text)
        content_html = markdown_to_html(post.content)

        post_title = escape_xml_text(post.title or "无标题")
        post_category = escape_xml_text(post.category) if post.category else None

        xml_parts.append('<item>')
        xml_parts.append(f'<title>{post_title}</title>')
        xml_parts.append(f'<link>{post_link}</link>')
        xml_parts.append(f'<description>{description_text}</description>')
        xml_parts.append(f'<pubDate>{post.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>')
        xml_parts.append(f'<guid>{post_link}</guid>')

        if post_category:
            xml_parts.append(f'<category>{post_category}</category>')

        if content_html:
            # 直接嵌入 HTML，不进行额外转义
            xml_parts.append(f'<content:encoded><![CDATA[{content_html}]]></content:encoded>')

        xml_parts.append('</item>')

    xml_parts.append('</channel>')
    xml_parts.append('</rss>')

    return '\n'.join(xml_parts)

@router.get("/rss.xml")
async def get_main_rss_feed():
    """
    主 RSS Feed - 所有公开文章
    """
    # 获取所有公开文章
    posts = await PostModel.filter(is_locked=False)\
        .order_by('-is_top', '-created_at')\
        .exclude(category = "笔记")\
        .limit(20)\
        .all()

    # 生成 RSS XML
    xml_content = generate_rss_xml(
        posts=posts,
        title=BLOG_CONFIG["title"],
        link=BLOG_CONFIG["link"],
        description=BLOG_CONFIG["description"]
    )

    return Response(
        content=xml_content,
        media_type="application/rss+xml; charset=utf-8",
        headers={
            "Cache-Control": "public, max-age=3600"  # 缓存1小时
        }
    )

@router.get("/rss/{category}.xml")
async def get_category_rss_feed(category: str):
    """
    分类 RSS Feed - 指定分类的公开文章
    """
    # 获取指定分类的公开文章
    posts = await PostModel.filter(
        is_locked=False,
        category=category
    ).order_by('-is_top', '-created_at')\
     .limit(20)\
     .all()

    # 如果该分类没有文章，返回空 RSS
    if not posts:
        # 创建空的 RSS 结构
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">')
        xml_parts.append('<channel>')

        channel_title = escape_xml_text(f"{BLOG_CONFIG['title']} - {category}")
        channel_link = escape_xml_text(f"{BLOG_CONFIG['link']}/category/{category}")
        channel_description = escape_xml_text(f"{BLOG_CONFIG['description']} - {category}分类")

        xml_parts.append(f'<title>{channel_title}</title>')
        xml_parts.append(f'<link>{channel_link}</link>')
        xml_parts.append(f'<description>{channel_description}</description>')
        xml_parts.append('<language>zh-CN</language>')
        xml_parts.append(f'<lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>')
        xml_parts.append('<generator>FastAPI Blog RSS</generator>')
        xml_parts.append('</channel>')
        xml_parts.append('</rss>')

        xml_content = '\n'.join(xml_parts)
    else:
        # 生成分类 RSS XML
        xml_content = generate_rss_xml(
            posts=posts,
            title=BLOG_CONFIG["title"],
            link=BLOG_CONFIG["link"],
            description=BLOG_CONFIG["description"],
            category=category
        )

    return Response(
        content=xml_content,
        media_type="application/rss+xml; charset=utf-8",
        headers={
            "Cache-Control": "public, max-age=3600"
        }
    )
