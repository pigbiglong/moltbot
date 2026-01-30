#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaCrawler Skill - 快速测试脚本

用于验证 skill 的基本功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("测试 1: 模块导入")
    print("=" * 60)

    try:
        from tools.skill_wrapper import MediaCrawlerSkill
        from tools.skill_analyzer import DataAnalyzer, analyze_data
        from tools.skill_config import (
            SUPPORTED_PLATFORMS,
            SUPPORTED_MODES,
            get_platform_config,
        )

        print("✅ 所有模块导入成功!")
        print(f"   支持的平台: {', '.join(SUPPORTED_PLATFORMS)}")
        print(f"   支持的模式: {', '.join(SUPPORTED_MODES)}")
        return True

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("\n请确保已安装依赖:")
        print("  uv pip install httpx aiofiles")
        return False


async def test_config():
    """测试配置功能"""
    print("\n" + "=" * 60)
    print("测试 2: 配置功能")
    print("=" * 60)

    try:
        from tools.skill_config import (
            get_platform_config,
            validate_platform,
            validate_mode,
        )

        # 测试平台配置
        xhs_config = get_platform_config("xhs")
        print(f"✅ 小红书配置: {xhs_config['name']}")

        # 测试验证函数
        assert validate_platform("xhs") == True
        assert validate_platform("invalid") == False
        assert validate_mode("search") == True
        assert validate_mode("invalid") == False

        print("✅ 配置功能正常!")
        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


async def test_skill_initialization():
    """测试 Skill 初始化"""
    print("\n" + "=" * 60)
    print("测试 3: Skill 初始化")
    print("=" * 60)

    try:
        from tools.skill_wrapper import MediaCrawlerSkill

        # 测试初始化
        skill = MediaCrawlerSkill(
            api_url="http://localhost:8080",
            timeout=300,
        )

        print(f"✅ Skill 初始化成功!")
        print(f"   API URL: {skill.api_url}")
        print(f"   项目根目录: {skill.project_root}")
        print(f"   超时时间: {skill.timeout}s")

        await skill.close()
        return True

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


async def test_api_connection():
    """测试 API 连接"""
    print("\n" + "=" * 60)
    print("测试 4: API 连接")
    print("=" * 60)

    try:
        from tools.skill_wrapper import MediaCrawlerSkill
        import httpx

        async with MediaCrawlerSkill() as skill:
            # 尝试连接 API
            try:
                response = await skill.client.get(
                    f"{skill.api_url}/api/health",
                    timeout=5.0,
                )

                if response.status_code == 200:
                    print("✅ API 服务连接成功!")
                    print(f"   状态码: {response.status_code}")
                    return True
                else:
                    print(f"⚠️  API 返回异常状态码: {response.status_code}")
                    return False

            except httpx.ConnectError:
                print("❌ 无法连接到 API 服务")
                print("\n请确保 API 服务已启动:")
                print("  cd /Users/zyjk/Desktop/project/海外旅游/MediaCrawler")
                print("  uv run uvicorn api.main:app --port 8080")
                return False

            except Exception as e:
                print(f"❌ API 连接测试失败: {e}")
                return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_analyzer():
    """测试数据分析器"""
    print("\n" + "=" * 60)
    print("测试 5: 数据分析器")
    print("=" * 60)

    try:
        from tools.skill_analyzer import DataAnalyzer, analyze_data

        # 创建测试数据
        test_data = [
            {
                "note_id": "1",
                "title": "测试帖子1",
                "liked_count": 100,
                "comment_count": 10,
                "share_count": 5,
                "nickname": "用户A",
            },
            {
                "note_id": "2",
                "title": "测试帖子2",
                "liked_count": 200,
                "comment_count": 20,
                "share_count": 10,
                "nickname": "用户B",
            },
        ]

        # 测试分析功能
        analyzer = DataAnalyzer("xhs")
        summary = analyzer.analyze_summary(test_data)

        print("✅ 数据分析器工作正常!")
        print(f"   总条目: {summary['total_items']}")
        print(f"   平均点赞: {summary['engagement_metrics']['likes']['average']}")

        return True

    except Exception as e:
        print(f"❌ 分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MediaCrawler Skill 测试套件" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = []

    # 运行测试
    results.append(("模块导入", await test_imports()))
    results.append(("配置功能", await test_config()))
    results.append(("Skill 初始化", await test_skill_initialization()))
    results.append(("API 连接", await test_api_connection()))
    results.append(("数据分析器", await test_analyzer()))

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}  {name}")

    print("\n" + "-" * 60)
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过! Skill 已准备就绪!")
        print("\n下一步:")
        print("1. 确保 API 服务运行: uv run uvicorn api.main:app --port 8080")
        print("2. 完成平台登录: uv run python main.py --platform xhs --lt qrcode --type search --keywords '测试' --max_items 1")
        print("3. 运行示例: python tools/examples/search_example.py")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
