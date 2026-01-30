# -*- coding: utf-8 -*-
"""
MediaCrawler Skill - 社交媒体数据采集和分析

这个 skill 允许 Claude Agent 采集和分析中国主流社交媒体平台的公开数据。

支持的平台:
- 小红书 (xhs)
- 抖音 (dy)
- 快手 (ks)
- B站 (bili)
- 微博 (wb)
- 贴吧 (tieba)
- 知乎 (zhihu)

使用方法:
    from skills.mediacrawler import MediaCrawlerSkill, analyze_data

    async with MediaCrawlerSkill() as skill:
        result = await skill.crawl(
            platform="xhs",
            mode="search",
            keywords="AI工具",
            max_items=10
        )
"""

try:
    from .skill_wrapper import (
        MediaCrawlerSkill,
        SkillError,
        APINotAvailableError,
        LoginRequiredError,
        TaskTimeoutError,
        InvalidParameterError,
    )
    from .skill_analyzer import DataAnalyzer, analyze_data
    from .skill_config import (
        SUPPORTED_PLATFORMS,
        SUPPORTED_MODES,
        get_platform_config,
        validate_platform,
        validate_mode,
    )

    __all__ = [
        # 核心类
        "MediaCrawlerSkill",
        "DataAnalyzer",
        # 分析函数
        "analyze_data",
        # 异常类
        "SkillError",
        "APINotAvailableError",
        "LoginRequiredError",
        "TaskTimeoutError",
        "InvalidParameterError",
        # 配置
        "SUPPORTED_PLATFORMS",
        "SUPPORTED_MODES",
        "get_platform_config",
        "validate_platform",
        "validate_mode",
    ]

    __version__ = "1.0.0"
    __author__ = "MediaCrawler Team"
    __description__ = "采集和分析中国主流社交媒体平台的公开数据"

except ImportError as e:
    # 如果依赖未安装，提供友好的错误提示
    import sys
    print(f"⚠️  MediaCrawler Skill 依赖未安装: {e}", file=sys.stderr)
    print("请运行: uv pip install httpx aiofiles", file=sys.stderr)
    raise
