"""
MediaCrawler Skill - 搜索模式示例

演示如何使用 skill 搜索社交媒体平台的内容
"""

import asyncio
from skills.mediacrawler import MediaCrawlerSkill


async def search_example():
    """搜索模式示例"""
    print("=== MediaCrawler Skill - 搜索模式示例 ===\n")

    async with MediaCrawlerSkill() as skill:
        # 示例 1: 搜索小红书上关于"AI工具"的帖子
        print("1. 搜索小红书 - AI工具")
        print("-" * 50)

        try:
            result = await skill.crawl(
                platform="xhs",
                mode="search",
                keywords="AI工具",
                max_items=5,
                enable_comments=True,
            )

            # 打印摘要
            summary = result["summary"]
            print(f"✅ 采集成功!")
            print(f"   平台: {summary['platform_name']}")
            print(f"   总帖子数: {summary['total_posts']}")
            print(f"   总评论数: {summary['total_comments']}")
            print(f"   平均点赞: {summary['avg_likes']:.1f}")
            print(f"   最高点赞: {summary['max_likes']}")
            print(f"\n   最热帖子:")
            print(f"   - 标题: {summary['top_post']['title']}")
            print(f"   - 点赞: {summary['top_post']['likes']}")
            print(f"   - 作者: {summary['top_post']['author']}")
            print(f"   - 链接: {summary['top_post']['url']}")
            print(f"\n   数据文件:")
            for file_type, path in result["data_files"].items():
                print(f"   - {file_type}: {path}")

        except Exception as e:
            print(f"❌ 错误: {e}")

        print("\n" + "=" * 50 + "\n")

        # 示例 2: 搜索多个关键词
        print("2. 搜索小红书 - 多个关键词")
        print("-" * 50)

        try:
            result = await skill.crawl(
                platform="xhs",
                mode="search",
                keywords="旅游攻略,旅行推荐",
                max_items=10,
                enable_comments=False,  # 不采集评论，更快
            )

            summary = result["summary"]
            print(f"✅ 采集成功!")
            print(f"   总帖子数: {summary['total_posts']}")
            print(f"   平均点赞: {summary['avg_likes']:.1f}")
            print(f"   互动统计:")
            print(f"   - 总点赞: {summary['engagement_stats']['total_likes']}")
            print(f"   - 总分享: {summary['engagement_stats']['total_shares']}")
            print(f"   - 总收藏: {summary['engagement_stats']['total_collects']}")

        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(search_example())
