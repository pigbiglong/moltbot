# MediaCrawler Skill

一个强大的社交媒体数据采集和分析 Skill，让 Claude Agent 能够轻松采集和分析中国主流社交媒体平台的公开数据。

## 🌟 特性

- **7个平台支持**: 小红书、抖音、快手、B站、微博、贴吧、知乎
- **3种采集模式**: 关键词搜索、指定帖子详情、创作者主页数据
- **双执行模式**: 同步等待（适合小量数据）和异步后台（适合大量数据）
- **智能分析**: 自动生成数据摘要、趋势分析、情感分析
- **Markdown 导出**: 将 JSON 数据转换为易读的 Markdown 格式
- **简单易用**: 一行代码启动采集，自动处理登录态和数据解析

## 📦 安装

### 前置依赖

确保已安装以下依赖：

```bash
pip install httpx aiofiles
```

或使用 uv（推荐）：

```bash
uv pip install httpx aiofiles
```

### 文件结构

```
skills/mediacrawler/
├── skill.md                 # Skill 定义（Claude Code 入口）
├── __init__.py             # Python 包初始化
├── README.md               # 本文件 - 快速开始指南
├── USAGE.md                # 详细使用指南
├── skill_config.py         # 平台配置
├── skill_wrapper.py        # 核心包装器
├── skill_analyzer.py       # 数据分析器
├── test_skill.py           # 测试套件
└── examples/               # 使用示例
    ├── search_example.py
    ├── detail_example.py
    └── async_example.py
```

## 🚀 快速开始

### 1. 启动 API 服务

```bash
cd /Users/zyjk/Desktop/project/海外旅游/MediaCrawler
uv run uvicorn api.main:app --port 8080 --reload
```

### 2. 完成平台登录（首次使用）

```bash
# 小红书登录示例
uv run python main.py --platform xhs --lt qrcode --type search --keywords "测试" --max_items 1

# 扫码登录后，登录态会自动保存
```

### 3. 使用 Skill

```python
import asyncio
from skills.mediacrawler import MediaCrawlerSkill

async def main():
    async with MediaCrawlerSkill() as skill:
        # 搜索小红书上关于"AI工具"的帖子
        result = await skill.crawl(
            platform="xhs",
            mode="search",
            keywords="AI工具",
            max_items=10
        )

        print(f"采集了 {result['summary']['total_posts']} 条帖子")
        print(f"平均点赞: {result['summary']['avg_likes']}")

asyncio.run(main())
```

## 📖 使用示例

### 示例 1: 关键词搜索

```python
# 搜索小红书上的旅游攻略
result = await skill.crawl(
    platform="xhs",
    mode="search",
    keywords="旅游攻略,旅行推荐",
    max_items=20,
    enable_comments=True
)

# 查看摘要
summary = result['summary']
print(f"总帖子: {summary['total_posts']}")
print(f"总评论: {summary['total_comments']}")
print(f"最热帖子: {summary['top_post']['title']}")
```

### 示例 2: 指定帖子详情

```python
# 获取特定帖子的详细信息和评论
result = await skill.crawl(
    platform="xhs",
    mode="detail",
    post_ids="post_id_1,post_id_2",
    enable_comments=True
)

# 分析评论情感
from skills.mediacrawler import analyze_data
import json

with open(result['data_files']['comments'], 'r') as f:
    comments = json.load(f)

sentiment = analyze_data(comments, "xhs", "sentiment")
print(f"正面评论: {sentiment['positive']['percentage']}%")
print(f"情感得分: {sentiment['sentiment_score']}")
```

### 示例 3: 异步模式（大量数据）

```python
# 启动异步任务
task_id = await skill.crawl_async(
    platform="xhs",
    mode="search",
    keywords="Python编程",
    max_items=100
)

# 继续做其他事情...
print(f"任务 {task_id} 正在后台运行")

# 稍后检查状态
status = await skill.check_status(task_id)
if status['status'] == 'idle':
    result = await skill.get_result(task_id)
```

### 示例 4: 数据分析

```python
from tools.skill_analyzer import analyze_data
import json

# 读取采集的数据
with open(result['data_files']['contents'], 'r') as f:
    data = json.load(f)

# 趋势分析
trending = analyze_data(data, "xhs", "trending")
print("热门作者:", trending['rising_authors'][:3])
print("发布高峰:", trending['peak_times'])

# 摘要分析
summary = analyze_data(data, "xhs", "summary")
print("互动指标:", summary['engagement_metrics'])
print("作者统计:", summary['author_stats'])
```

## 🎯 支持的平台

| 平台代码 | 平台名称 | 支持模式 |
|---------|---------|---------|
| `xhs` | 小红书 | search, detail, creator |
| `dy` | 抖音 | search, detail, creator |
| `ks` | 快手 | search, detail, creator |
| `bili` | B站 | search, detail, creator |
| `wb` | 微博 | search, detail, creator |
| `tieba` | 贴吧 | search, detail, creator |
| `zhihu` | 知乎 | search, detail, creator |

### 示例 4: Markdown 导出

```python
from skills.mediacrawler import export_to_markdown

# 采集数据
result = await skill.crawl(
    platform="xhs",
    mode="search",
    keywords="AI工具",
    max_items=10
)

# 导出为 Markdown（便于 Agent 阅读）
md_file = export_to_markdown(
    json_file=result['data_files']['contents'],
    platform="xhs",
    data_type="contents",
    format_type="summary"  # 摘要格式，最适合 Agent
)

print(f"已导出 Markdown: {md_file}")

# Agent 可以直接使用 Read 工具读取 Markdown
# 比 JSON 更易于理解和分析
```

## 📊 数据分析功能

### 1. 摘要分析 (summary)

```python
analysis = analyze_data(data, platform, "summary")
```

返回：
- 互动指标（点赞、评论、分享统计）
- 作者统计（活跃作者、发帖数量）
- 时间分布（发布高峰时段）
- 内容统计（标题长度等）

### 2. 趋势分析 (trending)

```python
trending = analyze_data(data, platform, "trending")
```

返回：
- 热门帖子 TOP 10
- 活跃作者排行
- 互动趋势（增长/下降）
- 发布高峰时段

### 3. 情感分析 (sentiment)

```python
sentiment = analyze_data(comments, platform, "sentiment")
```

返回：
- 正面/负面/中性评论比例
- 情感得分 (-1 到 1)
- 评论总数统计

## ⚙️ 配置选项

### MediaCrawlerSkill 初始化参数

```python
skill = MediaCrawlerSkill(
    api_url="http://localhost:8080",  # API 服务地址
    project_root="/path/to/project",  # 项目根目录（可选）
    timeout=300                        # 请求超时时间（秒）
)
```

### crawl 方法参数

```python
result = await skill.crawl(
    platform="xhs",           # 必需：平台代码
    mode="search",            # 必需：爬取模式
    keywords="关键词",        # search 模式必需
    post_ids="id1,id2",      # detail 模式必需
    creator_ids="id1,id2",   # creator 模式必需
    max_items=20,            # 可选：最大采集数量
    enable_comments=True,    # 可选：是否采集评论
    timeout=600              # 可选：任务超时时间
)
```

## 🔧 故障排除

### 问题 1: APINotAvailableError

**原因**: API 服务未启动或地址错误

**解决**:
```bash
# 启动 API 服务
uv run uvicorn api.main:app --port 8080

# 验证服务
curl http://localhost:8080/api/health
```

### 问题 2: LoginRequiredError

**原因**: 平台登录态不存在或已过期

**解决**:
```bash
# 重新登录
uv run python main.py --platform xhs --lt qrcode --type search --keywords "测试" --max_items 1
```

### 问题 3: TaskTimeoutError

**原因**: 采集数据量过大，超过超时时间

**解决**:
- 减少 `max_items` 参数
- 增加 `timeout` 参数
- 使用异步模式 `crawl_async()`

### 问题 4: 导入错误

**原因**: 缺少依赖包

**解决**:
```bash
uv pip install httpx aiofiles
```

## 📝 完整文档

查看 `skill.md` 获取完整的 API 文档和高级用法。

## 🎓 学习资源

- **Skill 定义**: `skill.md` - Claude Code 主入口
- **使用指南**: `USAGE.md` - 快速参考和实用场景
- **示例代码**: `examples/` 目录
- **项目主页**: https://github.com/NanmiCoder/MediaCrawler

## ⚠️ 注意事项

1. **合法合规**: 仅用于学习和研究目的
2. **频率控制**: 避免频繁采集，遵守平台规则
3. **数据隐私**: 不要采集和传播用户隐私信息
4. **资源占用**: 大量采集会占用系统资源
5. **登录态管理**: 登录态可能过期，需定期更新

## 📄 许可证

本项目遵循 NON-COMMERCIAL LEARNING LICENSE 1.1 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ for Claude Agent**
