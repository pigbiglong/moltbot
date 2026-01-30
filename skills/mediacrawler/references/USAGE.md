# MediaCrawler Skill 使用指南

> 专为 Claude Code 设计的社交媒体数据采集 Skill

## 🎯 快速开始

### 第一步: 启动 API 服务

```bash
cd /Users/zyjk/Desktop/project/海外旅游/MediaCrawler
uv run uvicorn api.main:app --port 8080
```

### 第二步: 了解数据保存位置

**重要**：数据将自动保存到 Moltbot 工作空间：

```bash
# Moltbot 工作空间
/Users/zyjk/Desktop/project/moltbot/data/
├── xhs/json/       # 小红书
├── dy/json/        # 抖音
├── wb/json/        # 微博
└── ...
```

**文件命名规则**：
- `search_contents_{关键词}_{时间戳}.json` - 搜索的帖子
- `search_comments_{关键词}_{时间戳}.json` - 搜索的评论
- `detail_contents_{关键词}_{时间戳}.json` - 详情的帖子
- `detail_comments_{关键词}_{时间戳}.json` - 详情的评论

### 第二步: 完成平台登录（仅首次）

```bash
# 小红书登录
uv run python main.py --platform xhs --lt qrcode --type search --keywords "测试" --max_items 1
```

扫描二维码登录后，登录态会自动保存。

### 第三步: 开始使用

```python
from skills.mediacrawler import MediaCrawlerSkill

async with MediaCrawlerSkill() as skill:
    result = await skill.crawl(
        platform="xhs",
        mode="search",
        keywords="AI工具",
        max_items=10
    )
    print(result['summary'])
```

## 📖 核心功能

### 1. 数据采集

#### 搜索模式 - 关键词搜索

```python
result = await skill.crawl(
    platform="xhs",           # 平台: xhs/dy/ks/bili/wb/tieba/zhihu
    mode="search",            # 模式: search
    keywords="旅游攻略,旅行", # 关键词（逗号分隔）
    max_items=20,            # 最大采集数量
    enable_comments=True     # 是否采集评论
)
```

#### 详情模式 - 指定帖子

```python
result = await skill.crawl(
    platform="xhs",
    mode="detail",
    post_ids="post_id_1,post_id_2",  # 帖子ID（逗号分隔）
    enable_comments=True
)
```

#### 创作者模式 - 分析UP主/博主

```python
result = await skill.crawl(
    platform="bili",
    mode="creator",
    creator_ids="creator_id",  # 创作者ID
    max_items=30
)
```

### 2. 返回数据结构

```python
{
    "status": "success",
    "task_id": "xhs_search_1738051200",
    "summary": {
        "platform": "xhs",
        "platform_name": "小红书",
        "total_posts": 15,        # 总帖子数
        "total_comments": 230,    # 总评论数
        "avg_likes": 1250.5,      # 平均点赞数
        "max_likes": 5000,        # 最高点赞数
        "top_post": {             # 最热帖子
            "title": "...",
            "likes": 5000,
            "url": "...",
            "author": "..."
        }
    },
    "data_files": {
        "contents": "data/xhs/json/search_contents_20260128.json",
        "comments": "data/xhs/json/search_comments_20260128.json"
    }
}
```

### 3. 数据分析

```python
from skills.mediacrawler import analyze_data
import json

# 读取数据
with open(result['data_files']['contents'], 'r') as f:
    data = json.load(f)

# 摘要分析
summary = analyze_data(data, platform="xhs", analysis_type="summary")
# 返回: 互动指标、作者统计、时间分布、内容统计

# 趋势分析
trending = analyze_data(data, platform="xhs", analysis_type="trending")
# 返回: 热门帖子TOP10、活跃作者、互动趋势、发布高峰

# 情感分析（评论数据）
with open(result['data_files']['comments'], 'r') as f:
    comments = json.load(f)
sentiment = analyze_data(comments, platform="xhs", analysis_type="sentiment")
# 返回: 正面/负面/中性比例、情感得分
```

## 🚀 高级用法

### 异步模式（大量数据）

```python
# 启动异步任务
task_id = await skill.crawl_async(
    platform="xhs",
    mode="search",
    keywords="Python编程",
    max_items=100
)

# 继续其他工作...
print(f"任务 {task_id} 正在后台运行")

# 检查状态
while True:
    status = await skill.check_status(task_id)
    if status["status"] == "idle":
        break
    await asyncio.sleep(3)

# 获取结果
result = await skill.get_result(task_id)
```

### 多平台并行采集

```python
# 同时采集多个平台
xhs_task = await skill.crawl_async(platform="xhs", mode="search", keywords="AI工具", max_items=20)
dy_task = await skill.crawl_async(platform="dy", mode="search", keywords="AI工具", max_items=20)

# 等待所有任务完成
tasks = [xhs_task, dy_task]
for task_id in tasks:
    while (await skill.check_status(task_id))["status"] != "idle":
        await asyncio.sleep(3)
    result = await skill.get_result(task_id)
    print(f"{result['summary']['platform_name']}: {result['summary']['total_posts']} 条")
```

## 💡 实用场景

### 场景 1: 市场调研

**目标**: 了解"AI工具"市场的用户需求和热点

```python
async def market_research():
    async with MediaCrawlerSkill() as skill:
        # 采集小红书数据
        result = await skill.crawl(
            platform="xhs",
            mode="search",
            keywords="AI工具,AI助手,ChatGPT",
            max_items=50,
            enable_comments=True
        )

        # 分析趋势
        from skills.mediacrawler import analyze_data
        import json

        with open(result['data_files']['contents'], 'r') as f:
            data = json.load(f)

        trending = analyze_data(data, "xhs", "trending")

        print("=== 市场调研报告 ===")
        print(f"总帖子数: {result['summary']['total_posts']}")
        print(f"平均互动: {result['summary']['avg_likes']} 点赞")
        print(f"\n热门作者 TOP 5:")
        for i, author in enumerate(trending['rising_authors'][:5], 1):
            print(f"{i}. {author['author']} - {author['post_count']} 篇帖子")
        print(f"\n发布高峰时段: {', '.join(trending['peak_times'])}")
```

### 场景 2: 竞品分析

**目标**: 分析竞品的爆款内容和用户反馈

```python
async def competitor_analysis(post_ids: str):
    async with MediaCrawlerSkill() as skill:
        # 获取竞品帖子详情
        result = await skill.crawl(
            platform="xhs",
            mode="detail",
            post_ids=post_ids,
            enable_comments=True
        )

        # 分析评论情感
        from skills.mediacrawler import analyze_data
        import json

        with open(result['data_files']['comments'], 'r') as f:
            comments = json.load(f)

        sentiment = analyze_data(comments, "xhs", "sentiment")

        print("=== 竞品分析报告 ===")
        print(f"帖子数: {result['summary']['total_posts']}")
        print(f"总评论: {result['summary']['total_comments']}")
        print(f"平均点赞: {result['summary']['avg_likes']}")
        print(f"\n用户情感:")
        print(f"  正面: {sentiment['positive']['percentage']}%")
        print(f"  负面: {sentiment['negative']['percentage']}%")
        print(f"  情感得分: {sentiment['sentiment_score']}")
```

### 场景 3: 达人研究

**目标**: 分析头部创作者的内容策略

```python
async def creator_analysis(creator_id: str):
    async with MediaCrawlerSkill() as skill:
        # 采集创作者数据
        result = await skill.crawl(
            platform="bili",
            mode="creator",
            creator_ids=creator_id,
            max_items=30
        )

        # 分析内容策略
        from skills.mediacrawler import analyze_data
        import json

        with open(result['data_files']['contents'], 'r') as f:
            data = json.load(f)

        summary = analyze_data(data, "bili", "summary")

        print("=== 达人分析报告 ===")
        print(f"总视频数: {result['summary']['total_posts']}")
        print(f"平均播放: {result['summary']['avg_likes']}")
        print(f"最热视频: {result['summary']['top_post']['title']}")
        print(f"\n内容策略:")
        print(f"  发布频率: {summary['time_distribution']}")
        print(f"  最佳时段: {summary.get('peak_hours', 'N/A')}")
```

## ⚠️ 常见问题

### Q1: 如何处理 API 连接失败？

```python
from skills.mediacrawler import MediaCrawlerSkill, APINotAvailableError

try:
    async with MediaCrawlerSkill() as skill:
        result = await skill.crawl(...)
except APINotAvailableError:
    print("❌ API 服务未启动")
    print("请运行: uv run uvicorn api.main:app --port 8080")
```

### Q2: 如何处理登录态过期？

```python
from skills.mediacrawler import LoginRequiredError

try:
    result = await skill.crawl(platform="xhs", ...)
except LoginRequiredError:
    print("❌ 登录态已过期，请重新登录")
    print("运行: uv run python main.py --platform xhs --lt qrcode --type search --keywords '测试' --max_items 1")
```

### Q3: 如何处理任务超时？

```python
from skills.mediacrawler import TaskTimeoutError

try:
    result = await skill.crawl(
        platform="xhs",
        mode="search",
        keywords="test",
        max_items=10,      # 减少数量
        timeout=600        # 增加超时时间
    )
except TaskTimeoutError:
    print("❌ 任务超时，建议使用异步模式")
    task_id = await skill.crawl_async(...)  # 改用异步
```

### Q4: 如何获取帖子ID？

**小红书**:
- URL格式: `https://www.xiaohongshu.com/explore/65a1b2c3d4e5f6g7`
- 帖子ID: `65a1b2c3d4e5f6g7`

**抖音**:
- URL格式: `https://www.douyin.com/video/7123456789012345678`
- 视频ID: `7123456789012345678`

**B站**:
- URL格式: `https://www.bilibili.com/video/BV1xx411c7mD`
- 视频ID: `BV1xx411c7mD`

## 📊 性能建议

| 数据量 | 推荐模式 | 预期耗时 | max_items |
|--------|---------|----------|-----------|
| 测试 | 同步 | 30-60秒 | 5-10 |
| 小规模 | 同步 | 1-2分钟 | 10-20 |
| 中规模 | 同步/异步 | 3-5分钟 | 20-50 |
| 大规模 | 异步 | 5-10分钟 | 50-100 |
| 多平台 | 异步并行 | 视任务而定 | - |

## 🔒 注意事项

1. **合法使用**: 仅用于学习和研究，遵守平台规则
2. **频率控制**: 避免频繁采集，建议间隔至少30秒
3. **数据隐私**: 不要采集和传播用户隐私信息
4. **资源管理**: 大量采集会占用系统资源，注意监控
5. **登录管理**: 定期检查登录态，避免采集失败

## 📚 更多资源

- **完整文档**: `skills/mediacrawler/skill.md`
- **代码示例**: `skills/mediacrawler/examples/`
- **测试脚本**: `skills/mediacrawler/test_skill.py`
- **项目主页**: https://github.com/NanmiCoder/MediaCrawler

---

**版本**: 1.0.0
**更新日期**: 2026-01-28
**适用于**: Claude Code
