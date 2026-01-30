# -*- coding: utf-8 -*-
"""
MediaCrawler Skill Wrapper
提供简单易用的接口来调用 MediaCrawler 功能
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import httpx

# 兼容相对导入和直接运行
try:
    from .skill_config import (
        DEFAULT_CONFIG,
        PLATFORM_CONFIGS,
        SUMMARY_TEMPLATE,
        get_platform_config,
        get_field_value,
        validate_platform,
        validate_mode,
        get_platform_display_name,
    )
except ImportError:
    from skill_config import (
        DEFAULT_CONFIG,
        PLATFORM_CONFIGS,
        SUMMARY_TEMPLATE,
        get_platform_config,
        get_field_value,
        validate_platform,
        validate_mode,
        get_platform_display_name,
    )

# 环境变量配置键
ENV_MEDIACRAWLER_PATH = "MEDIACRAWLER_PATH"
ENV_MEDIACRAWLER_API_URL = "MEDIACRAWLER_API_URL"


class SkillError(Exception):
    """Skill 基础异常"""
    pass


class APINotAvailableError(SkillError):
    """API 服务不可用"""
    pass


class LoginRequiredError(SkillError):
    """需要登录"""
    pass


class TaskTimeoutError(SkillError):
    """任务超时"""
    pass


class InvalidParameterError(SkillError):
    """参数无效"""
    pass


class MediaCrawlerSkill:
    """
    MediaCrawler Skill 主类

    提供同步和异步两种模式来采集社交媒体数据

    支持通过以下方式配置：
    1. 环境变量 MEDIACRAWLER_PATH - MediaCrawler 项目路径
    2. 环境变量 MEDIACRAWLER_API_URL - API 服务地址
    3. 构造参数 - 优先级最高
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        project_root: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        初始化 MediaCrawler Skill

        Args:
            api_url: API 服务地址，默认从环境变量读取或使用 localhost:8080
            project_root: 项目根目录，默认从环境变量 MEDIACRAWLER_PATH 读取
            timeout: 请求超时时间（秒），默认 300
        """
        # 优先级：构造参数 > 环境变量 > 默认值
        self.api_url = api_url or os.environ.get(ENV_MEDIACRAWLER_API_URL) or DEFAULT_CONFIG["api_url"]
        self.project_root = project_root or os.environ.get(ENV_MEDIACRAWLER_PATH) or self._detect_project_root()
        self.timeout = timeout or 300.0

        # 创建 HTTP 客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=10.0),
            follow_redirects=True,
        )

        # 任务状态缓存
        self.tasks: Dict[str, Dict] = {}

    @classmethod
    def get_project_path(cls) -> Optional[str]:
        """获取当前配置的 MediaCrawler 项目路径"""
        return os.environ.get(ENV_MEDIACRAWLER_PATH)

    @classmethod
    def set_project_path(cls, path: str) -> None:
        """设置 MediaCrawler 项目路径（环境变量方式）"""
        os.environ[ENV_MEDIACRAWLER_PATH] = path

    @classmethod
    def get_api_url(cls) -> str:
        """获取当前配置的 API 地址"""
        return os.environ.get(ENV_MEDIACRAWLER_API_URL, DEFAULT_CONFIG["api_url"])

    @classmethod
    def set_api_url(cls, url: str) -> None:
        """设置 API 地址（环境变量方式）"""
        os.environ[ENV_MEDIACRAWLER_API_URL] = url

    def _detect_project_root(self) -> str:
        """自动检测项目根目录（兼容多种部署方式）"""
        # 优先检测环境变量配置
        env_path = os.environ.get(ENV_MEDIACRAWLER_PATH)
        if env_path and Path(env_path).exists():
            return env_path

        # 常见部署路径
        common_paths = [
            "/Users/zyjk/Desktop/project/海外旅游/MediaCrawler",
            "/Users/zyjk/Desktop/project/MediaCrawler",
            "/Users/zyjk/clawd/MediaCrawler",
            "/Users/zyjk/Desktop/project/moltbot/skills/mediacrawler/MediaCrawler",
        ]

        for path in common_paths:
            if Path(path).exists():
                return path

        # 降级方案：从当前文件向上查找
        current = Path(__file__).resolve()
        for parent in [current.parent.parent] + list(current.parents):
            if (parent / "main.py").exists():
                return str(parent)

        # 如果找不到，返回当前工作目录
        return os.getcwd()

    async def crawl(
        self,
        platform: str,
        mode: str,
        keywords: Optional[str] = None,
        post_ids: Optional[str] = None,
        creator_ids: Optional[str] = None,
        max_items: Optional[int] = None,
        enable_comments: bool = True,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        同步模式：启动爬虫任务并等待完成

        Args:
            platform: 平台代码 (xhs/dy/ks/bili/wb/tieba/zhihu)
            mode: 爬取模式 (search/detail/creator)
            keywords: 搜索关键词（search 模式必需）
            post_ids: 帖子ID列表，逗号分隔（detail 模式必需）
            creator_ids: 创作者ID列表，逗号分隔（creator 模式必需）
            max_items: 最大采集数量
            enable_comments: 是否采集评论
            timeout: 任务超时时间（秒）

        Returns:
            包含摘要和数据文件路径的字典

        Raises:
            InvalidParameterError: 参数无效
            APINotAvailableError: API 不可用
            TaskTimeoutError: 任务超时
        """
        # 1. 验证参数
        self._validate_params(platform, mode, keywords, post_ids, creator_ids)

        # 2. 启动爬虫
        task_id = await self._start_crawler(
            platform=platform,
            mode=mode,
            keywords=keywords,
            post_ids=post_ids,
            creator_ids=creator_ids,
            max_items=max_items,
            enable_comments=enable_comments,
        )

        # 3. 等待完成
        task_timeout = timeout or DEFAULT_CONFIG["timeout"]
        await self._wait_for_completion(task_id, timeout=task_timeout)

        # 4. 获取结果
        result = await self._get_result(task_id)

        return result

    async def crawl_async(
        self,
        platform: str,
        mode: str,
        keywords: Optional[str] = None,
        post_ids: Optional[str] = None,
        creator_ids: Optional[str] = None,
        max_items: Optional[int] = None,
        enable_comments: bool = True,
    ) -> str:
        """
        异步模式：启动爬虫任务并立即返回任务ID

        Args:
            platform: 平台代码
            mode: 爬取模式
            keywords: 搜索关键词
            post_ids: 帖子ID列表
            creator_ids: 创作者ID列表
            max_items: 最大采集数量
            enable_comments: 是否采集评论

        Returns:
            任务ID

        Raises:
            InvalidParameterError: 参数无效
            APINotAvailableError: API 不可用
        """
        # 验证参数
        self._validate_params(platform, mode, keywords, post_ids, creator_ids)

        # 启动爬虫
        task_id = await self._start_crawler(
            platform=platform,
            mode=mode,
            keywords=keywords,
            post_ids=post_ids,
            creator_ids=creator_ids,
            max_items=max_items,
            enable_comments=enable_comments,
        )

        return task_id

    async def check_status(self, task_id: str) -> Dict[str, Any]:
        """
        检查任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        try:
            response = await self.client.get(f"{self.api_url}/api/crawler/status")
            response.raise_for_status()
            status = response.json()

            # 获取任务信息
            task_info = self.tasks.get(task_id, {})

            return {
                "task_id": task_id,
                "status": status.get("status", "unknown"),
                "platform": status.get("platform") or task_info.get("platform"),
                "mode": task_info.get("mode"),
                "start_time": task_info.get("start_time"),
                "elapsed_time": time.time() - task_info.get("start_time", time.time()),
            }
        except httpx.HTTPError as e:
            raise APINotAvailableError(f"Failed to check status: {e}")

    async def get_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            包含摘要和数据文件的结果

        Raises:
            ValueError: 任务未完成
        """
        # 检查任务是否完成
        status = await self.check_status(task_id)

        if status["status"] != "idle":
            raise ValueError(
                f"Task {task_id} not completed yet. Current status: {status['status']}"
            )

        # 获取结果
        return await self._get_result(task_id)

    def _validate_params(
        self,
        platform: str,
        mode: str,
        keywords: Optional[str],
        post_ids: Optional[str],
        creator_ids: Optional[str],
    ) -> None:
        """验证参数"""
        # 验证平台
        if not validate_platform(platform):
            raise InvalidParameterError(
                f"Invalid platform: {platform}. "
                f"Supported: {', '.join(PLATFORM_CONFIGS.keys())}"
            )

        # 验证模式
        if not validate_mode(mode):
            raise InvalidParameterError(
                f"Invalid mode: {mode}. Supported: search, detail, creator"
            )

        # 验证必需参数
        if mode == "search" and not keywords:
            raise InvalidParameterError("keywords is required for search mode")

        if mode == "detail" and not post_ids:
            raise InvalidParameterError("post_ids is required for detail mode")

        if mode == "creator" and not creator_ids:
            raise InvalidParameterError("creator_ids is required for creator mode")

    async def _start_crawler(
        self,
        platform: str,
        mode: str,
        keywords: Optional[str] = None,
        post_ids: Optional[str] = None,
        creator_ids: Optional[str] = None,
        max_items: Optional[int] = None,
        enable_comments: bool = True,
    ) -> str:
        """启动爬虫任务"""
        # 生成任务时间戳
        task_timestamp = int(time.time())
        
        # 构建请求负载
        payload = {
            "platform": platform,
            "crawler_type": mode,
            "login_type": "cookie",  # 使用保存的登录态
            "save_option": DEFAULT_CONFIG["save_option"],
            "headless": DEFAULT_CONFIG["headless"],
            "enable_comments": enable_comments,
            "enable_sub_comments": DEFAULT_CONFIG["enable_sub_comments"],
            "start_page": 1,
        }

        # 根据模式设置参数
        if mode == "search":
            payload["keywords"] = keywords or ""
        elif mode == "detail":
            payload["specified_ids"] = post_ids or ""
        elif mode == "creator":
            payload["creator_ids"] = creator_ids or ""

        # 设置最大数量（通过 keywords 参数传递，API 会解析）
        # 注意：这里需要根据实际 API 实现调整

        try:
            # 发送启动请求
            response = await self.client.post(
                f"{self.api_url}/api/crawler/start",
                json=payload,
            )
            response.raise_for_status()

            # 生成任务ID
            task_id = f"{platform}_{mode}_{task_timestamp}"

            # 保存任务信息（包含时间戳和标识词）
            identifier = keywords or post_ids or creator_ids or "unknown"
            self.tasks[task_id] = {
                "platform": platform,
                "mode": mode,
                "start_time": task_timestamp,
                "timestamp": task_timestamp,
                "identifier": identifier,
                "keywords": keywords,
                "post_ids": post_ids,
                "creator_ids": creator_ids,
            }

            return task_id

        except httpx.HTTPError as e:
            raise APINotAvailableError(f"Failed to start crawler: {e}")

    async def _wait_for_completion(self, task_id: str, timeout: int = 600) -> None:
        """等待任务完成"""
        start_time = time.time()
        poll_interval = DEFAULT_CONFIG["poll_interval"]

        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TaskTimeoutError(
                    f"Task {task_id} timeout after {timeout} seconds"
                )

            # 检查状态
            status = await self.check_status(task_id)

            if status["status"] == "idle":
                # 任务完成
                break

            if status["status"] == "error":
                raise SkillError("Crawler task failed")

            # 等待后继续轮询
            await asyncio.sleep(poll_interval)

    async def _get_result(self, task_id: str) -> Dict[str, Any]:
        """获取任务结果"""
        task_info = self.tasks.get(task_id, {})
        platform = task_info.get("platform")

        if not platform:
            raise ValueError(f"Task {task_id} not found")

        # 获取数据文件（使用新的命名规则）
        data_files = await self._get_latest_data_files(platform, task_id)

        # 生成摘要
        summary = await self._generate_summary(platform, data_files)

        return {
            "status": "success",
            "task_id": task_id,
            "summary": summary,
            "data_files": data_files,
        }

    async def _get_latest_data_files(self, platform: str, task_id: str) -> Dict[str, str]:
        """获取最新的数据文件（适配 MediaCrawler 实际路径和各种命名规则）"""
        # 获取任务信息
        task_info = self.tasks.get(task_id, {})
        if not task_info:
            raise ValueError(f"Task {task_id} not found")

        platform = task_info.get("platform")
        mode = task_info.get("mode")
        
        # 平台代码到目录名的映射
        platform_map = {
            "xhs": "xhs",
            "dy": "douyin",
            "ks": "kuaishou",
            "bili": "bilibili",
            "wb": "weibo",
            "tieba": "tieba",
            "zhihu": "zhihu"
        }
        dir_name = platform_map.get(platform, platform)
        
        # 获取当前日期 (YYYY-MM-DD)
        current_date = time.strftime('%Y-%m-%d', time.localtime())

        # 构建前缀（MediaCrawler 默认命名规则：{type}_{item}_{date}）
        contents_prefix = f"{mode}_contents_{current_date}"
        comments_prefix = f"{mode}_comments_{current_date}"

        # 构建完整路径（保存到 MediaCrawler 项目的 data/ 下）
        data_dir = os.path.join(self.project_root, "data", dir_name, "json")
        
        if not os.path.exists(data_dir):
            return {}

        import glob
        
        # 查找匹配内容文件（处理带时间戳后缀的情况）
        contents_files = glob.glob(os.path.join(data_dir, f"{contents_prefix}*.json"))
        comments_files = glob.glob(os.path.join(data_dir, f"{comments_prefix}*.json"))

        result = {}
        if contents_files:
            # 取最新的一个
            result["contents"] = sorted(contents_files, key=os.path.getmtime)[-1]
        
        if comments_files:
            # 取最新的一个
            result["comments"] = sorted(comments_files, key=os.path.getmtime)[-1]

        return result

    async def _generate_summary(
        self, platform: str, data_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """生成数据摘要"""
        summary = SUMMARY_TEMPLATE.copy()
        summary["platform"] = platform
        summary["platform_name"] = get_platform_display_name(platform)

        # 读取内容文件
        if "contents" in data_files:
            try:
                contents = await self._read_json_file(data_files["contents"])

                if contents:
                    summary["total_posts"] = len(contents)

                    # 提取点赞数
                    likes = [
                        get_field_value(item, platform, "like_count_field", 0)
                        for item in contents
                    ]

                    if likes:
                        summary["avg_likes"] = sum(likes) / len(likes)
                        summary["max_likes"] = max(likes)
                        summary["min_likes"] = min(likes)
                        summary["engagement_stats"]["total_likes"] = sum(likes)

                    # 找到最热门的帖子
                    top_post = max(
                        contents,
                        key=lambda x: get_field_value(x, platform, "like_count_field", 0),
                    )

                    summary["top_post"] = {
                        "title": get_field_value(top_post, platform, "content_title_field", ""),
                        "likes": get_field_value(top_post, platform, "like_count_field", 0),
                        "url": get_field_value(top_post, platform, "content_url_field", ""),
                        "author": get_field_value(top_post, platform, "user_name_field", ""),
                    }

                    # 统计分享和收藏
                    shares = [
                        get_field_value(item, platform, "share_count_field", 0)
                        for item in contents
                    ]
                    collects = [
                        get_field_value(item, platform, "collect_count_field", 0)
                        for item in contents
                    ]

                    summary["engagement_stats"]["total_shares"] = sum(shares)
                    summary["engagement_stats"]["total_collects"] = sum(collects)

            except Exception as e:
                print(f"Warning: Failed to read contents file: {e}")

        # 读取评论文件
        if "comments" in data_files:
            try:
                comments = await self._read_json_file(data_files["comments"])
                summary["total_comments"] = len(comments)
            except Exception as e:
                print(f"Warning: Failed to read comments file: {e}")

        return summary

    async def _read_json_file(self, file_path: str) -> List[Dict]:
        """读取 JSON 文件"""
        # 构建完整路径
        if not os.path.isabs(file_path):
            full_path = os.path.join(self.project_root, file_path)
        else:
            full_path = file_path

        import aiofiles
        async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)

            # 确保返回列表
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                return []

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        await self.client.aclose()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
