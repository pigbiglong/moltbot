# MediaCrawler Skill - 完整打包说明

## 📦 Skill 已完成打包

所有文件已整理到标准的 Claude Code skill 目录结构中。

### 📁 完整文件清单

```
skills/mediacrawler/
├── skill.md                 # ⭐ Claude Code 主入口（13KB）
├── __init__.py             # Python 包初始化（1.9KB）
├── README.md               # 快速开始指南（7.7KB）
├── USAGE.md                # 详细使用指南（9.8KB）
├── skill_config.py         # 平台配置模块（8.1KB）
├── skill_wrapper.py        # 核心包装器类（16KB）
├── skill_analyzer.py       # 数据分析器（13KB）
├── test_skill.py           # 测试套件（6.7KB）
└── examples/               # 使用示例
    ├── search_example.py   # 搜索模式示例（2.7KB）
    ├── detail_example.py   # 详情模式示例（2.7KB）
    └── async_example.py    # 异步模式示例（4.6KB）

总计: 9个文件 + 3个示例 = 12个文件
总大小: ~86KB
```

## 🎯 文件说明

### 核心文件

#### 1. skill.md ⭐
**用途**: Claude Code 的主要入口文件
- 包含完整的 Skill 定义（YAML frontmatter）
- 详细的 API 文档和参数说明
- 完整的使用示例和工作流程
- 错误处理指南和最佳实践

**适用场景**: Claude Code 自动加载和识别

#### 2. __init__.py
**用途**: Python 包初始化
- 导出所有核心类和函数
- 提供友好的错误提示
- 版本信息和包元数据

**导出内容**:
```python
from skills.mediacrawler import (
    MediaCrawlerSkill,      # 核心类
    DataAnalyzer,           # 分析器
    analyze_data,           # 分析函数
    # 异常类
    SkillError,
    APINotAvailableError,
    LoginRequiredError,
    TaskTimeoutError,
    InvalidParameterError,
    # 配置
    SUPPORTED_PLATFORMS,
    SUPPORTED_MODES,
    get_platform_config,
    validate_platform,
    validate_mode,
)
```

#### 3. skill_config.py
**用途**: 平台配置和字段映射
- 7个平台的完整配置
- 统一的字段访问接口
- 平台验证函数

**关键配置**:
```python
SUPPORTED_PLATFORMS = ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]
SUPPORTED_MODES = ["search", "detail", "creator"]

PLATFORM_CONFIGS = {
    "xhs": {
        "name": "小红书",
        "content_id_field": "note_id",
        "like_count_field": "liked_count",
        # ... 更多字段映射
    },
    # ... 其他6个平台
}
```

#### 4. skill_wrapper.py
**用途**: MediaCrawlerSkill 核心类
- HTTP 客户端封装
- 同步/异步执行模式
- 状态轮询和结果获取
- 数据摘要自动生成

**核心方法**:
```python
class MediaCrawlerSkill:
    async def crawl(...)              # 同步采集
    async def crawl_async(...)        # 异步采集
    async def check_status(...)       # 检查状态
    async def get_result(...)         # 获取结果
    async def _generate_summary(...)  # 生成摘要
```

#### 5. skill_analyzer.py
**用途**: 数据分析和统计
- DataAnalyzer 类实现
- 三种分析类型
- 统计计算和数据聚合

**分析功能**:
```python
class DataAnalyzer:
    def analyze_summary(data)    # 摘要分析
    def analyze_trending(data)   # 趋势分析
    def analyze_sentiment(data)  # 情感分析

def analyze_data(data, platform, analysis_type)  # 便捷函数
```

### 文档文件

#### 6. README.md
**用途**: 快速开始指南
- 安装说明
- 快速开始步骤
- 基础使用示例
- 故障排除

**适合**: 首次使用和快速参考

#### 7. USAGE.md
**用途**: 详细使用指南
- 核心功能详解
- 高级用法示例
- 实用场景演示
- 常见问题解答
- 性能建议

**适合**: 深入学习和日常使用

### 测试和示例

#### 8. test_skill.py
**用途**: 完整的测试套件
- 5个测试场景
- 自动验证所有核心功能
- 友好的测试报告

**运行方式**:
```bash
uv run python skills/mediacrawler/test_skill.py
```

#### 9-11. examples/
**用途**: 实际使用示例
- `search_example.py` - 搜索模式演示
- `detail_example.py` - 详情模式演示
- `async_example.py` - 异步模式演示

**运行方式**:
```bash
uv run python skills/mediacrawler/examples/search_example.py
```

## 🚀 在 Claude Code 中使用

### 方式 1: 自然语言调用（推荐）

直接告诉 Claude Code 你的需求：

```
"使用 mediacrawler skill 搜索小红书上关于'AI工具'的帖子，采集20条"
```

Claude Code 会自动：
1. 识别 skill.md 文件
2. 加载 skill 定义
3. 调用相应的功能
4. 返回结构化结果

### 方式 2: Python 代码调用

```python
from skills.mediacrawler import MediaCrawlerSkill

async with MediaCrawlerSkill() as skill:
    result = await skill.crawl(
        platform="xhs",
        mode="search",
        keywords="AI工具",
        max_items=20
    )
    print(result['summary'])
```

### 方式 3: 运行示例脚本

```bash
# 在项目根目录
uv run python skills/mediacrawler/examples/search_example.py
```

## ✅ 验证 Skill 安装

### 步骤 1: 测试导入

```python
# 测试 Python 包导入
python -c "from skills.mediacrawler import MediaCrawlerSkill; print('✅ 导入成功')"
```

### 步骤 2: 运行测试套件

```bash
uv run python skills/mediacrawler/test_skill.py
```

预期输出:
```
✅ 通过  模块导入
✅ 通过  配置功能
✅ 通过  Skill 初始化
✅ 通过  API 连接
✅ 通过  数据分析器

总计: 5/5 测试通过
```

### 步骤 3: 运行示例

```bash
uv run python skills/mediacrawler/examples/search_example.py
```

## 📋 使用前准备

### 1. 启动 API 服务

```bash
cd /Users/zyjk/Desktop/project/海外旅游/MediaCrawler
uv run uvicorn api.main:app --port 8080
```

### 2. 完成平台登录（首次使用）

```bash
# 小红书登录
uv run python main.py --platform xhs --lt qrcode --type search --keywords "测试" --max_items 1
```

扫描二维码登录后，登录态会自动保存到 `xhs_user_data_dir/`

### 3. 验证环境

```bash
# 检查 API 健康状态
curl http://localhost:8080/api/health

# 预期输出: {"status":"ok"}
```

## 🎯 核心功能速查

### 数据采集

```python
# 搜索模式
result = await skill.crawl(
    platform="xhs",
    mode="search",
    keywords="关键词",
    max_items=20
)

# 详情模式
result = await skill.crawl(
    platform="xhs",
    mode="detail",
    post_ids="id1,id2"
)

# 创作者模式
result = await skill.crawl(
    platform="bili",
    mode="creator",
    creator_ids="creator_id"
)
```

### 数据分析

```python
from skills.mediacrawler import analyze_data
import json

# 读取数据
with open(result['data_files']['contents'], 'r') as f:
    data = json.load(f)

# 摘要分析
summary = analyze_data(data, "xhs", "summary")

# 趋势分析
trending = analyze_data(data, "xhs", "trending")

# 情感分析
sentiment = analyze_data(comments, "xhs", "sentiment")
```

### 异步模式

```python
# 启动异步任务
task_id = await skill.crawl_async(
    platform="xhs",
    mode="search",
    keywords="关键词",
    max_items=100
)

# 检查状态
status = await skill.check_status(task_id)

# 获取结果
result = await skill.get_result(task_id)
```

## 📊 支持的平台和模式

| 平台 | 代码 | search | detail | creator |
|------|------|--------|--------|---------|
| 小红书 | xhs | ✅ | ✅ | ✅ |
| 抖音 | dy | ✅ | ✅ | ✅ |
| 快手 | ks | ✅ | ✅ | ✅ |
| B站 | bili | ✅ | ✅ | ✅ |
| 微博 | wb | ✅ | ✅ | ✅ |
| 贴吧 | tieba | ✅ | ✅ | ✅ |
| 知乎 | zhihu | ✅ | ✅ | ✅ |

## ⚠️ 重要提醒

1. **API 服务**: 必须先启动 API 服务才能使用 skill
2. **登录态**: 首次使用需要手动登录平台保存登录态
3. **导入路径**: 使用 `from skills.mediacrawler import ...`
4. **运行环境**: 使用 `uv run` 确保依赖正确加载
5. **合法使用**: 仅用于学习研究，遵守平台规则

## 🔧 故障排除

### 问题 1: 导入失败

```bash
# 错误: No module named 'skills.mediacrawler'
# 解决: 确保在项目根目录运行
cd /Users/zyjk/Desktop/project/海外旅游/MediaCrawler
python -c "from skills.mediacrawler import MediaCrawlerSkill"
```

### 问题 2: 依赖缺失

```bash
# 错误: No module named 'aiofiles'
# 解决: 使用 uv run
uv run python your_script.py
```

### 问题 3: API 连接失败

```bash
# 错误: APINotAvailableError
# 解决: 启动 API 服务
uv run uvicorn api.main:app --port 8080
```

## 📚 文档导航

- **快速开始**: 阅读 `README.md`
- **详细用法**: 阅读 `USAGE.md`
- **完整 API**: 阅读 `skill.md`
- **代码示例**: 查看 `examples/` 目录
- **测试验证**: 运行 `test_skill.py`

## 🎉 总结

MediaCrawler Skill 已完整打包，包含：

✅ **9个核心文件** - 完整的功能实现
✅ **3个示例脚本** - 实际使用演示
✅ **3份文档** - 从快速开始到深入使用
✅ **1个测试套件** - 自动验证功能
✅ **7个平台支持** - 覆盖主流社交媒体
✅ **3种采集模式** - 满足不同需求
✅ **2种执行模式** - 灵活的性能选择
✅ **3种分析功能** - 智能数据洞察

**现在就可以在 Claude Code 中使用了！** 🚀

---

**版本**: 1.0.0
**打包日期**: 2026-01-28
**状态**: ✅ 生产就绪
**位置**: `/Users/zyjk/Desktop/project/海外旅游/MediaCrawler/skills/mediacrawler/`
