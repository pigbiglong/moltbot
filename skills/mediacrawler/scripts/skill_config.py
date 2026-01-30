# -*- coding: utf-8 -*-
"""
MediaCrawler Skill Configuration
平台配置和常量定义
"""

from typing import Dict, List

# 支持的平台列表
SUPPORTED_PLATFORMS = ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]

# 支持的爬取模式
SUPPORTED_MODES = ["search", "detail", "creator"]

# 支持的分析类型
SUPPORTED_ANALYSIS_TYPES = ["summary", "trending", "sentiment"]

# 平台配置映射
PLATFORM_CONFIGS: Dict[str, Dict] = {
    "xhs": {
        "name": "小红书",
        "display_name": "Xiaohongshu",
        "content_id_field": "note_id",
        "content_url_field": "note_url",
        "content_title_field": "title",
        "content_desc_field": "desc",
        "like_count_field": "liked_count",
        "comment_count_field": "comment_count",
        "share_count_field": "share_count",
        "collect_count_field": "collected_count",
        "user_id_field": "user_id",
        "user_name_field": "nickname",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "nickname",
        "creator_fans_field": "fans",
    },
    "dy": {
        "name": "抖音",
        "display_name": "Douyin",
        "content_id_field": "aweme_id",
        "content_url_field": "aweme_url",
        "content_title_field": "title",
        "content_desc_field": "desc",
        "like_count_field": "liked_count",
        "comment_count_field": "comment_count",
        "share_count_field": "share_count",
        "collect_count_field": "collected_count",
        "user_id_field": "user_id",
        "user_name_field": "nickname",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "nickname",
        "creator_fans_field": "fans",
    },
    "ks": {
        "name": "快手",
        "display_name": "Kuaishou",
        "content_id_field": "video_id",
        "content_url_field": "video_url",
        "content_title_field": "title",
        "content_desc_field": "desc",
        "like_count_field": "liked_count",
        "comment_count_field": "comment_count",
        "share_count_field": "share_count",
        "collect_count_field": "collected_count",
        "user_id_field": "user_id",
        "user_name_field": "nickname",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "nickname",
        "creator_fans_field": "fans",
    },
    "bili": {
        "name": "B站",
        "display_name": "Bilibili",
        "content_id_field": "video_id",
        "content_url_field": "video_url",
        "content_title_field": "title",
        "content_desc_field": "desc",
        "like_count_field": "liked_count",
        "comment_count_field": "video_comment",
        "share_count_field": "video_share_count",
        "collect_count_field": "video_favorite_count",
        "user_id_field": "user_id",
        "user_name_field": "nickname",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "nickname",
        "creator_fans_field": "total_fans",
    },
    "wb": {
        "name": "微博",
        "display_name": "Weibo",
        "content_id_field": "note_id",
        "content_url_field": "note_url",
        "content_title_field": "content",  # 微博没有单独的标题
        "content_desc_field": "content",
        "like_count_field": "liked_count",
        "comment_count_field": "comments_count",
        "share_count_field": "shared_count",
        "collect_count_field": "liked_count",  # 微博用点赞数
        "user_id_field": "user_id",
        "user_name_field": "nickname",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "nickname",
        "creator_fans_field": "fans",
    },
    "tieba": {
        "name": "贴吧",
        "display_name": "Tieba",
        "content_id_field": "post_id",
        "content_url_field": "post_url",
        "content_title_field": "title",
        "content_desc_field": "content",
        "like_count_field": "like_count",
        "comment_count_field": "comment_count",
        "share_count_field": "share_count",
        "collect_count_field": "collect_count",
        "user_id_field": "user_id",
        "user_name_field": "username",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "username",
        "creator_fans_field": "fans",
    },
    "zhihu": {
        "name": "知乎",
        "display_name": "Zhihu",
        "content_id_field": "content_id",
        "content_url_field": "content_url",
        "content_title_field": "title",
        "content_desc_field": "content",
        "like_count_field": "voteup_count",
        "comment_count_field": "comment_count",
        "share_count_field": "share_count",
        "collect_count_field": "collect_count",
        "user_id_field": "user_id",
        "user_name_field": "username",
        "user_avatar_field": "avatar",
        "comment_id_field": "comment_id",
        "comment_content_field": "content",
        "creator_id_field": "user_id",
        "creator_name_field": "username",
        "creator_fans_field": "follower_count",
    },
}

# 数据文件类型映射
DATA_FILE_TYPES = {
    "contents": "内容数据",
    "comments": "评论数据",
    "creators": "创作者数据",
}

# 默认配置
DEFAULT_CONFIG = {
    "api_url": "http://localhost:8080",
    "max_items": 20,
    "enable_comments": True,
    "enable_sub_comments": False,
    "headless": True,
    "save_option": "json",
    "timeout": 600,  # 10分钟超时
    "poll_interval": 2,  # 状态轮询间隔（秒）
}

# 数据摘要模板
SUMMARY_TEMPLATE = {
    "platform": "",
    "platform_name": "",
    "mode": "",
    "total_posts": 0,
    "total_comments": 0,
    "avg_likes": 0.0,
    "max_likes": 0,
    "min_likes": 0,
    "top_post": {
        "title": "",
        "likes": 0,
        "url": "",
        "author": "",
    },
    "time_range": {
        "earliest": "",
        "latest": "",
    },
    "engagement_stats": {
        "total_likes": 0,
        "total_shares": 0,
        "total_collects": 0,
    },
}


def get_platform_config(platform: str) -> Dict:
    """
    获取平台配置

    Args:
        platform: 平台代码

    Returns:
        平台配置字典

    Raises:
        ValueError: 如果平台不支持
    """
    if platform not in PLATFORM_CONFIGS:
        raise ValueError(
            f"Unsupported platform: {platform}. "
            f"Supported platforms: {', '.join(SUPPORTED_PLATFORMS)}"
        )
    return PLATFORM_CONFIGS[platform]


def get_field_value(data: Dict, platform: str, field_type: str, default=None):
    """
    从数据中获取字段值（处理平台差异和类型转换）

    Args:
        data: 数据字典
        platform: 平台代码
        field_type: 字段类型（如 'like_count_field'）
        default: 默认值

    Returns:
        字段值
    """
    config = get_platform_config(platform)
    field_name = config.get(field_type)

    if not field_name:
        return default

    value = data.get(field_name, default)
    
    # 针对数量字段尝试转换为数值
    if field_type in [
        "like_count_field", 
        "comment_count_field", 
        "share_count_field", 
        "collect_count_field",
        "creator_fans_field"
    ]:
        if value is None or value == "":
            return 0
        if isinstance(value, str):
            # 处理 "1.2k", "1万" 等格式（简单处理）
            try:
                if 'k' in value.lower():
                    return int(float(value.lower().replace('k', '')) * 1000)
                if 'w' in value.lower() or '万' in value:
                    return int(float(value.lower().replace('w', '').replace('万', '')) * 10000)
                return int(float(value))
            except (ValueError, TypeError):
                return 0
    
    return value


def validate_platform(platform: str) -> bool:
    """验证平台是否支持"""
    return platform in SUPPORTED_PLATFORMS


def validate_mode(mode: str) -> bool:
    """验证爬取模式是否支持"""
    return mode in SUPPORTED_MODES


def validate_analysis_type(analysis_type: str) -> bool:
    """验证分析类型是否支持"""
    return analysis_type in SUPPORTED_ANALYSIS_TYPES


def get_platform_display_name(platform: str) -> str:
    """获取平台显示名称"""
    config = get_platform_config(platform)
    return config.get("name", platform)
