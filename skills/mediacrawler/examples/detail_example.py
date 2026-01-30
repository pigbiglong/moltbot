"""
MediaCrawler Skill - 详情模式示例

演示如何使用 skill 获取指定帖子的详细信息
"""

import asyncio
from skills.mediacrawler import MediaCrawlerSkill


async def detail_example():
    """详情模式示例"""
    print("=== MediaCrawler Skill - 详情模式示例 ===\n")

    async with MediaCrawlerSkill() as skill:
        # 示例: 获取指定小红书帖子的详情
        print("获取小红书帖子详情")
        print("-" * 50)

        # 注意: 这里需要替换为真实的帖子ID
        post_ids = "your_post_id_1,your_post_id_2"

        print(f"帖子ID: {post_ids}")
        print("提示: 请将 'your_post_id_1' 替换为真实的帖子ID\n")

        try:
            result = await skill.crawl(
                platform="xhs",
                mode="detail",
                post_ids=post_ids,
                enable_comments=True,
            )

            # 打印摘要
            summary = result["summary"]
            print(f"✅ 采集成功!")
            print(f"   平台: {summary['platform_name']}")
            print(f"   总帖子数: {summary['total_posts']}")
            print(f"   总评论数: {summary['total_comments']}")
            print(f"\n   详细信息:")
            print(f"   - 平均点赞: {summary['avg_likes']:.1f}")
            print(f"   - 最高点赞: {summary['max_likes']}")
            print(f"   - 最低点赞: {summary['min_likes']}")
            print(f"\n   数据文件:")
            for file_type, path in result["data_files"].items():
                print(f"   - {file_type}: {path}")

            # 如果有评论，可以进行情感分析
            if "comments" in result["data_files"]:
                print("\n   正在分析评论情感...")
                from skills.mediacrawler import analyze_data
                import json

                with open(result["data_files"]["comments"], "r", encoding="utf-8") as f:
                    comments = json.load(f)

                sentiment = analyze_data(comments, "xhs", "sentiment")
                print(f"   - 正面评论: {sentiment['positive']['percentage']}%")
                print(f"   - 负面评论: {sentiment['negative']['percentage']}%")
                print(f"   - 中性评论: {sentiment['neutral']['percentage']}%")
                print(f"   - 情感得分: {sentiment['sentiment_score']}")

        except Exception as e:
            print(f"❌ 错误: {e}")
            print("\n提示: 请确保:")
            print("1. 已将示例中的帖子ID替换为真实ID")
            print("2. API 服务正在运行")
            print("3. 已完成平台登录")


if __name__ == "__main__":
    asyncio.run(detail_example())
