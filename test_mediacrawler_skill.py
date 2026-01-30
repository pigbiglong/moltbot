import asyncio
import sys
import os

# Add the skills directory to path so we can import mediacrawler
sys.path.append('/Users/zyjk/Desktop/project/moltbot')

from skills.mediacrawler.scripts import MediaCrawlerSkill

async def test_search():
    async with MediaCrawlerSkill() as skill:
        print("--- Testing XiaoHongShu (xhs) ---")
        try:
            xhs_result = await skill.crawl(
                platform="xhs",
                mode="search",
                keywords="AI测试",
                max_items=5
            )
            print(f"XHS Summary: {xhs_result['summary']}")
            print(f"XHS Files: {xhs_result['data_files']}")
        except Exception as e:
            print(f"XHS Error: {e}")

        print("\n--- Testing Weibo (wb) ---")
        try:
            wb_result = await skill.crawl(
                platform="wb",
                mode="search",
                keywords="AI测试",
                max_items=5
            )
            print(f"WB Summary: {wb_result['summary']}")
            print(f"WB Files: {wb_result['data_files']}")
        except Exception as e:
            print(f"WB Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
