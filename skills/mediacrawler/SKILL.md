---
name: mediacrawler
description: 采集和分析中国主流社交媒体平台的公开数据（小红书、抖音、快手、B站、微博、贴吧、知乎）
---

# MediaCrawler Skill

## 功能说明

这个 skill 允许 Claude Agent 采集和分析中国主流社交媒体平台的公开数据，支持：

- **7个平台**: 小红书(xhs)、抖音(dy)、快手(ks)、B站(bili)、微博(wb)、贴吧(tieba)、知乎(zhihu)
- **3种模式**: 关键词搜索、指定帖子详情、创作者主页数据
- **智能分析**: 自动生成数据摘要、趋势分析、情感分析
- **灵活执行**: 支持同步等待和异步后台两种模式

## 使用场景

1. **市场调研**: 搜索关键词了解市场趋势和用户需求
2. **竞品分析**: 分析特定帖子的表现和用户反馈
3. **达人研究**: 分析创作者的内容策略和粉丝互动
4. **舆情监控**: 追踪特定话题的讨论和情感倾向
5. **内容策划**: 发现热门话题和最佳发布时间

## 前置条件

### 1. 配置 MediaCrawler 项目路径

**方式一：环境变量（推荐）**
```bash
export MEDIACRAWLER_PATH="/Users/zyjk/Desktop/project/海外旅游/MediaCrawler"
export MEDIACRAWLER_API_URL="http://localhost:8080"
```

**方式二：在代码中配置**
```python
from tools.skill_wrapper import MediaCrawlerSkill

# 设置项目路径
MediaCrawlerSkill.set_project_path("/path/to/MediaCrawler")
MediaCrawlerSkill.set_api_url("http://localhost:8080")
```

### 2. 启动 API 服务

```bash
cd $MEDIACRAWLER_PATH
uv run uvicorn api.main:app --port 8080 --reload
```

### 3. 数据保存路径

**默认保存位置**: `{MEDIACRAWLER_PATH}/data/`

**自定义保存位置**: 可以通过脚本下载到指定目录

### 4. 最佳实践

**⚠️ 重要：避免数据覆盖问题**
MediaCrawler 默认会将每次采集写入同一文件，导致历史数据丢失。请使用以下脚本：

**脚本位置**: `/Users/zyjk/clawd/MediaCrawler/crawl_simple.py`

**特点**:
- 每次采集保存为独立文件（关键词_时间戳.json）
- 自动读取并合并缓存数据
- 保留所有历史数据，不会覆盖

**使用方法**:
```bash
cd /Users/zyjk/clawd/MediaCrawler

# 完整采集（50+关键词）
python3 crawl_simple.py

# 查看帮助
python3 crawl_simple.py --help
```

**输出目录**: `/Users/zyjk/Documents/Obsidian Vault/综合搜索/留学/2026-01-29/小红书/`

## 使用方法

### 方式 1: 通过 Python 代码调用

```python
import asyncio
from tools.skill_wrapper import MediaCrawlerSkill

async def main():
    # 初始化 skill（会自动读取环境变量）
    async with MediaCrawlerSkill() as skill:
        # 搜索小红书上关于"旅游攻略"的帖子
        result = await skill.crawl(
            platform="xhs",
            mode="search",
            keywords="旅游攻略",
            max_items=10,
            enable_comments=True
        )

        print(f"采集了 {result['summary']['total_posts']} 条帖子")
        print(f"平均点赞数: {result['summary']['avg_likes']}")
        print(f"数据文件: {result['data_files']}")

asyncio.run(main())
```

### 方式 2: 通过自然语言调用（推荐）

直接告诉 Claude Agent 你的需求，例如：

- "使用 mediacrawler skill 搜索小红书上关于'旅游攻略'的帖子"
- "帮我采集抖音上这个视频的详细数据和评论：[视频ID]"
- "分析B站UP主 [UP主ID] 的最近内容表现"

## 核心功能

### 1. crawl - 数据采集（同步模式）

启动爬虫任务并等待完成，适合小量数据（< 20条）。

**参数**:
- `platform` (必需): 平台代码
- `mode` (必需): 爬取模式
- `keywords` (search 模式必需): 搜索关键词
- `max_items` (可选): 最大采集数量，默认 20
- `enable_comments` (可选): 是否采集评论，默认 True

**返回值**:
```python
{
    "status": "success",
    "summary": {...},
    "data_files": {
        "contents": "/.../data/xhs/json/search_contents_2026-01-29.json",
        "comments": "/.../data/xhs/json/search_comments_2026-01-29.json"
    }
}
```

## 故障排除

### 微博平台返回 0 条数据
确保 API 服务的 `/api/data/files` 端点正确支持平台过滤。检查：
1. API 服务是否重启
2. 平台别名配置是否正确（wb/weibo/微博）

### 项目路径未正确识别
手动设置项目路径：
```python
MediaCrawlerSkill.set_project_path("/path/to/MediaCrawler")
```
