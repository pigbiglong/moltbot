# -*- coding: utf-8 -*-
"""
MediaCrawler Skill Analyzer
数据分析和统计功能
"""

import json
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any, Optional

from .skill_config import get_field_value, get_platform_config


class DataAnalyzer:
    """数据分析器"""

    def __init__(self, platform: str):
        """
        初始化分析器

        Args:
            platform: 平台代码
        """
        self.platform = platform
        self.config = get_platform_config(platform)

    def analyze_summary(self, data: List[Dict]) -> Dict[str, Any]:
        """
        生成摘要分析

        Args:
            data: 数据列表

        Returns:
            摘要分析结果
        """
        if not data:
            return {
                "total_items": 0,
                "message": "No data to analyze",
            }

        result = {
            "total_items": len(data),
            "engagement_metrics": self._analyze_engagement(data),
            "author_stats": self._analyze_authors(data),
            "time_distribution": self._analyze_time_distribution(data),
            "content_stats": self._analyze_content(data),
        }

        return result

    def analyze_trending(self, data: List[Dict]) -> Dict[str, Any]:
        """
        趋势分析

        Args:
            data: 数据列表

        Returns:
            趋势分析结果
        """
        if not data:
            return {"message": "No data to analyze"}

        # 按时间排序
        sorted_data = self._sort_by_time(data)

        # 分析趋势
        result = {
            "top_posts": self._get_top_posts(data, limit=10),
            "rising_authors": self._get_rising_authors(data),
            "engagement_trend": self._analyze_engagement_trend(sorted_data),
            "peak_times": self._analyze_peak_times(data),
        }

        return result

    def analyze_sentiment(self, comments: List[Dict]) -> Dict[str, Any]:
        """
        情感分析（简单版本）

        Args:
            comments: 评论数据列表

        Returns:
            情感分析结果
        """
        if not comments:
            return {"message": "No comments to analyze"}

        # 简单的关键词情感分析
        positive_keywords = ["好", "棒", "赞", "喜欢", "优秀", "完美", "厉害", "支持"]
        negative_keywords = ["差", "烂", "垃圾", "不好", "失望", "糟糕", "讨厌"]

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for comment in comments:
            content = get_field_value(
                comment, self.platform, "comment_content_field", ""
            )

            has_positive = any(kw in content for kw in positive_keywords)
            has_negative = any(kw in content for kw in negative_keywords)

            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(comments)

        return {
            "total_comments": total,
            "positive": {
                "count": positive_count,
                "percentage": round(positive_count / total * 100, 2) if total > 0 else 0,
            },
            "negative": {
                "count": negative_count,
                "percentage": round(negative_count / total * 100, 2) if total > 0 else 0,
            },
            "neutral": {
                "count": neutral_count,
                "percentage": round(neutral_count / total * 100, 2) if total > 0 else 0,
            },
            "sentiment_score": self._calculate_sentiment_score(
                positive_count, negative_count, total
            ),
        }

    def _analyze_engagement(self, data: List[Dict]) -> Dict[str, Any]:
        """分析互动指标"""
        likes = [get_field_value(item, self.platform, "like_count_field", 0) for item in data]
        comments = [get_field_value(item, self.platform, "comment_count_field", 0) for item in data]
        shares = [get_field_value(item, self.platform, "share_count_field", 0) for item in data]

        return {
            "likes": {
                "total": sum(likes),
                "average": round(sum(likes) / len(likes), 2) if likes else 0,
                "max": max(likes) if likes else 0,
                "min": min(likes) if likes else 0,
            },
            "comments": {
                "total": sum(comments),
                "average": round(sum(comments) / len(comments), 2) if comments else 0,
                "max": max(comments) if comments else 0,
            },
            "shares": {
                "total": sum(shares),
                "average": round(sum(shares) / len(shares), 2) if shares else 0,
                "max": max(shares) if shares else 0,
            },
            "engagement_rate": self._calculate_engagement_rate(likes, comments, shares),
        }

    def _analyze_authors(self, data: List[Dict]) -> Dict[str, Any]:
        """分析作者统计"""
        authors = [
            get_field_value(item, self.platform, "user_name_field", "Unknown")
            for item in data
        ]

        author_counter = Counter(authors)
        most_common = author_counter.most_common(10)

        return {
            "total_unique_authors": len(author_counter),
            "top_authors": [
                {"name": name, "post_count": count} for name, count in most_common
            ],
        }

    def _analyze_time_distribution(self, data: List[Dict]) -> Dict[str, Any]:
        """分析时间分布"""
        # 提取时间字段（不同平台字段名可能不同）
        times = []
        for item in data:
            # 尝试多个可能的时间字段
            time_value = item.get("time") or item.get("create_time") or item.get("publish_time")
            if time_value:
                times.append(time_value)

        if not times:
            return {"message": "No time data available"}

        # 按小时统计
        hour_distribution = Counter()
        for t in times:
            try:
                # 处理时间戳
                if isinstance(t, (int, float)):
                    dt = datetime.fromtimestamp(t)
                else:
                    dt = datetime.fromisoformat(str(t))

                hour_distribution[dt.hour] += 1
            except Exception:
                continue

        # 找出发布高峰时段
        peak_hours = hour_distribution.most_common(3)

        return {
            "hour_distribution": dict(hour_distribution),
            "peak_hours": [
                {"hour": f"{hour}:00", "count": count} for hour, count in peak_hours
            ],
        }

    def _analyze_content(self, data: List[Dict]) -> Dict[str, Any]:
        """分析内容统计"""
        titles = [
            get_field_value(item, self.platform, "content_title_field", "")
            for item in data
        ]

        # 计算平均标题长度
        title_lengths = [len(title) for title in titles if title]
        avg_title_length = (
            round(sum(title_lengths) / len(title_lengths), 2) if title_lengths else 0
        )

        return {
            "average_title_length": avg_title_length,
            "total_with_title": len([t for t in titles if t]),
        }

    def _get_top_posts(self, data: List[Dict], limit: int = 10) -> List[Dict]:
        """获取热门帖子"""
        # 按点赞数排序
        sorted_data = sorted(
            data,
            key=lambda x: get_field_value(x, self.platform, "like_count_field", 0),
            reverse=True,
        )

        top_posts = []
        for item in sorted_data[:limit]:
            top_posts.append({
                "title": get_field_value(item, self.platform, "content_title_field", ""),
                "author": get_field_value(item, self.platform, "user_name_field", ""),
                "likes": get_field_value(item, self.platform, "like_count_field", 0),
                "comments": get_field_value(item, self.platform, "comment_count_field", 0),
                "url": get_field_value(item, self.platform, "content_url_field", ""),
            })

        return top_posts

    def _get_rising_authors(self, data: List[Dict]) -> List[Dict]:
        """获取活跃作者"""
        author_stats = {}

        for item in data:
            author = get_field_value(item, self.platform, "user_name_field", "Unknown")
            likes = get_field_value(item, self.platform, "like_count_field", 0)

            if author not in author_stats:
                author_stats[author] = {"post_count": 0, "total_likes": 0}

            author_stats[author]["post_count"] += 1
            author_stats[author]["total_likes"] += likes

        # 按总点赞数排序
        sorted_authors = sorted(
            author_stats.items(),
            key=lambda x: x[1]["total_likes"],
            reverse=True,
        )

        return [
            {
                "author": author,
                "post_count": stats["post_count"],
                "total_likes": stats["total_likes"],
                "avg_likes": round(stats["total_likes"] / stats["post_count"], 2),
            }
            for author, stats in sorted_authors[:10]
        ]

    def _analyze_engagement_trend(self, sorted_data: List[Dict]) -> Dict[str, Any]:
        """分析互动趋势"""
        if len(sorted_data) < 2:
            return {"message": "Not enough data for trend analysis"}

        # 简单的趋势分析：比较前半部分和后半部分
        mid = len(sorted_data) // 2
        first_half = sorted_data[:mid]
        second_half = sorted_data[mid:]

        first_avg_likes = sum(
            get_field_value(item, self.platform, "like_count_field", 0)
            for item in first_half
        ) / len(first_half)

        second_avg_likes = sum(
            get_field_value(item, self.platform, "like_count_field", 0)
            for item in second_half
        ) / len(second_half)

        trend = "increasing" if second_avg_likes > first_avg_likes else "decreasing"
        change_rate = (
            ((second_avg_likes - first_avg_likes) / first_avg_likes * 100)
            if first_avg_likes > 0
            else 0
        )

        return {
            "trend": trend,
            "change_rate": round(change_rate, 2),
            "first_period_avg": round(first_avg_likes, 2),
            "second_period_avg": round(second_avg_likes, 2),
        }

    def _analyze_peak_times(self, data: List[Dict]) -> List[str]:
        """分析发布高峰时段"""
        times = []
        for item in data:
            time_value = item.get("time") or item.get("create_time")
            if time_value:
                times.append(time_value)

        if not times:
            return []

        hour_counter = Counter()
        for t in times:
            try:
                if isinstance(t, (int, float)):
                    dt = datetime.fromtimestamp(t)
                else:
                    dt = datetime.fromisoformat(str(t))

                hour_counter[dt.hour] += 1
            except Exception:
                continue

        peak_hours = hour_counter.most_common(3)
        return [f"{hour}:00-{hour+1}:00" for hour, _ in peak_hours]

    def _sort_by_time(self, data: List[Dict]) -> List[Dict]:
        """按时间排序"""
        def get_time(item):
            time_value = item.get("time") or item.get("create_time") or 0
            if isinstance(time_value, (int, float)):
                return time_value
            try:
                return datetime.fromisoformat(str(time_value)).timestamp()
            except Exception:
                return 0

        return sorted(data, key=get_time)

    def _calculate_engagement_rate(
        self, likes: List[int], comments: List[int], shares: List[int]
    ) -> float:
        """计算互动率"""
        total_engagement = sum(likes) + sum(comments) + sum(shares)
        total_posts = len(likes)

        if total_posts == 0:
            return 0.0

        return round(total_engagement / total_posts, 2)

    def _calculate_sentiment_score(
        self, positive: int, negative: int, total: int
    ) -> float:
        """
        计算情感得分 (-1 到 1)

        Args:
            positive: 正面评论数
            negative: 负面评论数
            total: 总评论数

        Returns:
            情感得分
        """
        if total == 0:
            return 0.0

        score = (positive - negative) / total
        return round(score, 3)


def analyze_data(
    data: List[Dict],
    platform: str,
    analysis_type: str = "summary",
) -> Dict[str, Any]:
    """
    分析数据的便捷函数

    Args:
        data: 数据列表
        platform: 平台代码
        analysis_type: 分析类型 (summary/trending/sentiment)

    Returns:
        分析结果
    """
    analyzer = DataAnalyzer(platform)

    if analysis_type == "summary":
        return analyzer.analyze_summary(data)
    elif analysis_type == "trending":
        return analyzer.analyze_trending(data)
    elif analysis_type == "sentiment":
        return analyzer.analyze_sentiment(data)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
