from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from blog.models import post_manager, comment_manager
from core.meta import MetaModel

router = APIRouter(prefix="/heatmap", tags=["heatmap"])

class HeatmapService:
    def __init__(self, post_manager, comment_manager):
        self.post_manager = post_manager
        self.comment_manager = comment_manager
        # 定义分类权重映射
        self.category_weights = {
            "post": 4,      # 文章
            "note": 1,      # 笔记
            "comment": 0.5  # 评论
        }
        # 分类显示名称映射
        self.category_display_names = {
            "post": "文章",
            "note": "笔记", 
            "comment": "评论"
        }
    
    def get_current_time(self):
        """获取当前时间（带时区）"""
        return datetime.now(timezone.utc)
    
    def generate_date_range_descending(self, days: int = 60) -> List[str]:
        """生成从今天到过去的日期范围列表（倒序排列）"""
        end_date = self.get_current_time()
        start_date = end_date - timedelta(days=days-1)
        
        date_list = []
        current_date = end_date
        
        while current_date >= start_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date -= timedelta(days=1)
        
        return date_list
    
    def calculate_heat_value(self, category_stats: Dict[str, int]) -> int:
        """计算热力值"""
        heat_value = 0
        for category, count in category_stats.items():
            weight = self.category_weights.get(category, 0)
            heat_value += count * weight
        return heat_value
    
    def is_note(self, post) -> bool:
        """判断一个post是否是笔记"""
        # 根据您的业务逻辑判断，这里假设category为"笔记"的就是笔记
        return post.category == "笔记"
    
    async def get_category_heatmap_data_descending(self, days: int = 60) -> List[Dict]:
        """获取最近N天的热力图数据"""
        all_dates_desc = self.generate_date_range_descending(days)
        
        end_date = self.get_current_time()
        start_date = end_date - timedelta(days=days-1)
        
        # 查询文章和笔记
        posts = await self.post_manager.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by("created_at")
        
        # 查询评论
        comments = await self.comment_manager.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            is_approved=True
        ).order_by("created_at")
        
        # 统计数据
        actual_data = {}
        
        # 统计文章和笔记
        for post in posts:
            # 确保日期是 naive datetime 用于格式化
            created_at = post.created_at
            if created_at.tzinfo is not None:
                created_at = created_at.replace(tzinfo=None)
            date_str = created_at.strftime("%Y-%m-%d")
            
            # 根据是否为笔记来分类
            if self.is_note(post):
                category = "note"
            else:
                category = "post"
            
            if date_str not in actual_data:
                actual_data[date_str] = {}
            
            if category not in actual_data[date_str]:
                actual_data[date_str][category] = 0
            actual_data[date_str][category] += 1
        
        # 统计评论
        for comment in comments:
            # 确保日期是 naive datetime 用于格式化
            created_at = comment.created_at
            if created_at.tzinfo is not None:
                created_at = created_at.replace(tzinfo=None)
            date_str = created_at.strftime("%Y-%m-%d")
            
            if date_str not in actual_data:
                actual_data[date_str] = {}
            
            if "comment" not in actual_data[date_str]:
                actual_data[date_str]["comment"] = 0
            actual_data[date_str]["comment"] += 1
        
        # 构建结果
        result = []
        for date_str in all_dates_desc:
            day_data = {
                "date": date_str,
                "note": 0,
                "post": 0, 
                "comment": 0,
                "heat": 0
            }
            
            if date_str in actual_data:
                for category, count in actual_data[date_str].items():
                    # 确保分类字段在允许的范围内
                    if category in ["note", "post", "comment"] and count > 0:
                        day_data[category] = count
                
                heat_value = self.calculate_heat_value(actual_data[date_str])
                day_data["heat"] = heat_value
            
            result.append(day_data)
        
        return result
    
    async def get_blog_statistics(self):
        """获取博客统计：总天数、笔记总数、文章总数"""
        try:
            # 获取网站创建时间
            website = await MetaModel.all().order_by("created_at").first()
            
            if not website:
                return {
                    "days": 0,
                    "notes": 0,
                    "posts": 0,
                    "comments": 0
                }
            
            # 处理时区问题
            current_time = self.get_current_time()
            earliest_date = website.created_at
            
            # 确保两个时间都有时区信息或都没有
            if earliest_date.tzinfo is not None and current_time.tzinfo is None:
                current_time = current_time.replace(tzinfo=timezone.utc)
            elif earliest_date.tzinfo is None and current_time.tzinfo is not None:
                current_time = current_time.replace(tzinfo=None)
            
            # 计算总天数
            total_days = (current_time - earliest_date).days + 1

            # 获取所有文章和笔记
            all_posts = await self.post_manager.filter().all()
            
            # 分别统计文章和笔记
            notes_count = 0
            posts_count = 0
            
            for post in all_posts:
                if self.is_note(post):
                    notes_count += 1
                else:
                    posts_count += 1

            # 统计评论数量
            comments_count = await self.comment_manager.filter().count()

            return {
                "days": total_days,
                "notes": notes_count,
                "posts": posts_count,
                "comments": comments_count
            }
            
        except Exception as e:
            print(f"Error in get_blog_statistics: {e}")
            return {
                "days": 0,
                "notes": 0, 
                "posts": 0,
                "comments": 0
            }

# 初始化服务
heatmap_service = HeatmapService(post_manager, comment_manager)

@router.get("/type-distribution")
async def get_category_distribution_heatmap_descending(days: Optional[int] = 60):
    """获取热力图数据"""
    try:
        if days <= 0 or days > 365:
            raise HTTPException(status_code=400, detail="天数必须在1-365之间")
        
        # 获取热力图数据
        heatmap_data = await heatmap_service.get_category_heatmap_data_descending(days)
        
        # 获取博客统计
        blog_stats = await heatmap_service.get_blog_statistics()
        
        # 构建返回数据
        return {
            "data": heatmap_data,
            "statistics": blog_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热力图数据失败: {str(e)}")