# MediaCrawler Skill - 更新日志

## v1.1.0 (2026-01-28) - Markdown 导出功能

### ✨ 新增功能

#### Markdown 导出器

添加了完整的 Markdown 导出功能，使采集的数据更易于 Agent 阅读和理解。

**新增文件**:
- `skill_markdown_exporter.py` - Markdown 导出核心模块 (13KB)
- `examples/markdown_export_example.py` - 完整使用示例 (7.6KB)
- `MARKDOWN_EXPORT.md` - 详细功能说明 (8.7KB)

**新增功能**:
1. **MarkdownExporter 类** - 核心导出器
2. **export_to_markdown()** - 便捷导出函数
3. **batch_export_to_markdown()** - 批量导出函数

**支持的格式**:

帖子内容:
- `detailed` - 详细格式（包含所有字段）
- `summary` - 摘要格式（关键信息）
- `table` - 表格格式（便于对比）

评论数据:
- `threaded` - 线程格式（按帖子分组）
- `flat` - 平铺格式（所有评论）
- `summary` - 摘要格式（高赞评论）

### 📝 使用示例

```python
from skills.mediacrawler import MediaCrawlerSkill, export_to_markdown

async with MediaCrawlerSkill() as skill:
    # 采集数据
    result = await skill.crawl(
        platform="xhs",
        mode="search",
        keywords="AI工具",
        max_items=10
    )

    # 导出为 Markdown
    md_file = export_to_markdown(
        json_file=result['data_files']['contents'],
        platform="xhs",
        data_type="contents",
        format_type="summary"  # 最适合 Agent
    )

    print(f"已导出: {md_file}")
```

### 🎯 优势

1. **易于阅读** - 结构化的 Markdown 格式
2. **Agent 友好** - 直接理解内容含义
3. **格式丰富** - 支持 emoji、表格、列表
4. **灵活导出** - 多种格式满足不同需求

### 📊 格式对比

| 格式 | 特点 | 适用场景 |
|------|------|---------|
| detailed | 完整信息 | 深度分析 |
| summary | 简洁列表 | 快速浏览 |
| table | 表格展示 | 数据对比 |

### 📚 文档更新

- ✅ 更新 `skill.md` - 添加 Markdown 导出 API 说明
- ✅ 更新 `README.md` - 添加使用示例
- ✅ 更新 `如何使用.md` - 添加功能介绍
- ✅ 更新 `__init__.py` - 导出新函数

### 🔧 技术细节

**依赖**: 无新增依赖，使用标准库

**兼容性**: 完全向后兼容，不影响现有功能

**性能**: Markdown 文件比 JSON 大约 20-30%

---

## v1.0.0 (2026-01-28) - 初始版本

### ✨ 核心功能

- ✅ 支持 7 个平台（小红书、抖音、快手、B站、微博、贴吧、知乎）
- ✅ 3 种采集模式（search、detail、creator）
- ✅ 2 种执行模式（同步、异步）
- ✅ 3 种数据分析（摘要、趋势、情感）

### 📦 文件结构

```
skills/mediacrawler/
├── skill.md                 # Skill 定义
├── __init__.py             # 包初始化
├── skill_config.py         # 平台配置
├── skill_wrapper.py        # 核心包装器
├── skill_analyzer.py       # 数据分析器
├── test_skill.py           # 测试套件
├── README.md               # 快速开始
├── USAGE.md                # 详细指南
├── PACKAGE_INFO.md         # 打包说明
└── examples/               # 使用示例
    ├── search_example.py
    ├── detail_example.py
    └── async_example.py
```

### 🎉 发布状态

- ✅ 所有测试通过 (5/5)
- ✅ 完整文档
- ✅ 使用示例
- ✅ 生产就绪

---

**维护者**: MediaCrawler Team
**许可证**: NON-COMMERCIAL LEARNING LICENSE 1.1
