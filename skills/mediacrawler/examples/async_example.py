"""
MediaCrawler Skill - 异步模式示例

演示如何使用异步模式进行大量数据采集
"""

import asyncio
from skills.mediacrawler import MediaCrawlerSkill


async def async_example():
    """异步模式示例"""
    print("=== MediaCrawler Skill - 异步模式示例 ===\n")

    async with MediaCrawlerSkill() as skill:
        # 示例 1: 启动异步任务
        print("1. 启动异步任务")
        print("-" * 50)

        try:
            task_id = await skill.crawl_async(
                platform="xhs",
                mode="search",
                keywords="Python编程",
                max_items=50,  # 大量数据
                enable_comments=True,
            )

            print(f"✅ 任务已启动!")
            print(f"   任务ID: {task_id}")
            print(f"   正在后台采集数据...\n")

            # 示例 2: 轮询任务状态
            print("2. 监控任务进度")
            print("-" * 50)

            while True:
                status = await skill.check_status(task_id)

                print(f"   状态: {status['status']}")
                print(f"   平台: {status['platform']}")
                print(f"   已运行: {status['elapsed_time']:.1f} 秒")

                if status["status"] == "idle":
                    print(f"\n✅ 任务完成!")
                    break

                if status["status"] == "error":
                    print(f"\n❌ 任务失败!")
                    return

                # 等待 3 秒后再次检查
                await asyncio.sleep(3)
                print()  # 换行

            # 示例 3: 获取结果
            print("\n3. 获取任务结果")
            print("-" * 50)

            result = await skill.get_result(task_id)

            summary = result["summary"]
            print(f"   总帖子数: {summary['total_posts']}")
            print(f"   总评论数: {summary['total_comments']}")
            print(f"   平均点赞: {summary['avg_likes']:.1f}")
            print(f"   最热帖子: {summary['top_post']['title']}")

            # 示例 4: 深度分析
            print("\n4. 数据分析")
            print("-" * 50)

            from skills.mediacrawler import analyze_data
            import json

            with open(result["data_files"]["contents"], "r", encoding="utf-8") as f:
                data = json.load(f)

            # 趋势分析
            trending = analyze_data(data, "xhs", "trending")

            print("   热门作者 TOP 3:")
            for i, author in enumerate(trending["rising_authors"][:3], 1):
                print(f"   {i}. {author['author']}")
                print(f"      - 帖子数: {author['post_count']}")
                print(f"      - 总点赞: {author['total_likes']}")
                print(f"      - 平均点赞: {author['avg_likes']}")

            print(f"\n   发布高峰时段: {', '.join(trending['peak_times'])}")

        except Exception as e:
            print(f"❌ 错误: {e}")


async def parallel_example():
    """并行采集多个平台"""
    print("\n\n=== 并行采集示例 ===\n")

    async with MediaCrawlerSkill() as skill:
        print("同时采集小红书和抖音数据")
        print("-" * 50)

        try:
            # 启动多个异步任务
            xhs_task = await skill.crawl_async(
                platform="xhs",
                mode="search",
                keywords="AI工具",
                max_items=20,
            )

            dy_task = await skill.crawl_async(
                platform="dy",
                mode="search",
                keywords="AI工具",
                max_items=20,
            )

            print(f"✅ 小红书任务: {xhs_task}")
            print(f"✅ 抖音任务: {dy_task}")
            print("\n正在并行采集...\n")

            # 等待所有任务完成
            tasks = [xhs_task, dy_task]
            completed = []

            while len(completed) < len(tasks):
                for task_id in tasks:
                    if task_id in completed:
                        continue

                    status = await skill.check_status(task_id)
                    if status["status"] == "idle":
                        completed.append(task_id)
                        print(f"✅ {status['platform']} 采集完成!")

                if len(completed) < len(tasks):
                    await asyncio.sleep(3)

            print("\n所有任务完成! 🎉")

        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(async_example())

    # 运行并行示例
    # asyncio.run(parallel_example())
