#!/usr/bin/env python3
"""
生产级项目演示脚本
运行所有模块的示例代码
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


async def demo_01_base_agent():
    """演示Agent基类"""
    print_section("01. Agent基类演示")

    sys.path.insert(0, str(project_root / "01-project-structure/src"))
    from base_agent import ResearchAgent, WriterAgent

    # 创建研究Agent
    researcher = ResearchAgent(agent_id="demo-researcher", config={})
    result = await researcher.run({"query": "AI Agent最佳实践"})
    print(f"研究结果: {result}")
    print(f"性能指标: {researcher.get_metrics()}")


def demo_02_config():
    """演示配置管理"""
    print_section("02. 配置管理演示")

    sys.path.insert(0, str(project_root / "02-config-management/src"))

    # 创建临时配置文件
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)

    import yaml
    base_config = {
        "app": {"name": "Demo Service", "debug": True},
        "llm": {"model": "gpt-4", "temperature": 0.7}
    }

    with open(config_dir / "base.yaml", 'w') as f:
        yaml.dump(base_config, f)

    from config_manager import Config
    config = Config(env="development", config_dir=str(config_dir))

    print(f"应用名称: {config.get('app.name')}")
    print(f"LLM模型: {config.get('llm.model')}")
    print(f"温度: {config.get('llm.temperature')}")


def demo_03_logging():
    """演示日志系统"""
    print_section("03. 结构化日志演示")

    sys.path.insert(0, str(project_root / "03-logging-system/src"))
    from structured_logger import StructuredLogger, set_request_context

    logger = StructuredLogger("demo", level="INFO", format_type="json")

    set_request_context(request_id="demo-001", user_id="demo-user")
    logger.info("演示日志记录", module="demo", action="test")
    logger.warning("这是一个警告", severity="medium")


def demo_04_error_handling():
    """演示错误处理"""
    print_section("04. 错误处理演示")

    sys.path.insert(0, str(project_root / "04-error-handling/src"))
    from exceptions import LLMException
    from error_handler import ErrorHandler

    handler = ErrorHandler()

    try:
        raise LLMException("模拟LLM错误", code="LLM_ERROR", details={"model": "gpt-4"})
    except Exception as e:
        error_info = handler.handle_error(e, context={"operation": "demo"})
        print(f"错误已处理: {error_info['error_type']}")


async def demo_05_retry():
    """演示重试机制"""
    print_section("05. 重试机制演示")

    sys.path.insert(0, str(project_root / "05-retry-circuit-breaker/src"))
    from retry_logic import retry

    attempt_count = 0

    @retry(max_attempts=3, delay=0.1, backoff=1.5)
    async def unstable_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"  尝试 #{attempt_count}")

        if attempt_count < 2:
            raise ConnectionError("连接失败")

        return "成功"

    result = await unstable_operation()
    print(f"最终结果: {result}")


def demo_06_cache():
    """演示缓存系统"""
    print_section("06. 缓存系统演示")

    sys.path.insert(0, str(project_root / "06-caching/src"))
    from cache_system import MemoryCache, MultiLevelCache

    cache = MultiLevelCache(l1_cache=MemoryCache(max_size=100))

    # 设置缓存
    cache.set("user:1", {"name": "Alice", "age": 30})

    # 获取缓存
    user = cache.get("user:1")
    print(f"缓存数据: {user}")

    # 统计信息
    stats = cache.get_stats()
    print(f"缓存统计: L1命中={stats['l1_hits']}, 未命中={stats['misses']}")


def demo_07_testing():
    """演示测试"""
    print_section("07. 测试演示")

    print("运行单元测试...")
    print("提示: 使用命令 'pytest 07-testing/src/test_agent.py -v' 运行完整测试")


def demo_08_api():
    """演示API服务"""
    print_section("08. API服务演示")

    print("API服务信息:")
    print("  启动命令: python 08-api-service/src/api_service.py")
    print("  API文档: http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/health")


def demo_09_monitoring():
    """演示监控指标"""
    print_section("09. 监控指标演示")

    sys.path.insert(0, str(project_root / "09-monitoring/src"))
    from metrics_collector import metrics

    # 记录指标
    metrics.record_request('demo-agent', 'success')
    metrics.record_duration('demo-agent', 1.5)
    metrics.record_llm_tokens('gpt-4', 100, 200)
    metrics.record_cache_hit('L1')

    print("指标已记录:")
    print("  - 请求: demo-agent (成功)")
    print("  - 延迟: 1.5秒")
    print("  - Token: 100 prompt + 200 completion")
    print("  - 缓存: L1命中")


def demo_10_cost():
    """演示成本优化"""
    print_section("10. 成本优化演示")

    sys.path.insert(0, str(project_root / "10-cost-optimization/src"))
    from cost_optimizer import TokenManager, CostTracker

    # Token计数
    token_manager = TokenManager("gpt-4")
    text = "这是一个测试文本，用于演示Token计数功能。"
    token_count = token_manager.count_tokens(text)
    print(f"文本: {text}")
    print(f"Token数: {token_count}")

    # 成本估算
    cost = token_manager.estimate_cost(prompt_tokens=1000, completion_tokens=500)
    print(f"\n成本估算:")
    print(f"  GPT-4 (1000+500 tokens): ${cost:.4f}")

    # 成本追踪
    tracker = CostTracker()
    tracker.record_usage("gpt-4", 1000, 500, "demo")
    stats = tracker.get_statistics()
    print(f"\n成本统计:")
    print(f"  总成本: ${stats['total_cost']:.4f}")
    print(f"  总Token: {stats['total_tokens']}")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  生产级AI Agent项目 - 完整演示")
    print("=" * 60)

    demos = [
        ("Agent基类", demo_01_base_agent),
        ("配置管理", demo_02_config),
        ("日志系统", demo_03_logging),
        ("错误处理", demo_04_error_handling),
        ("重试机制", demo_05_retry),
        ("缓存系统", demo_06_cache),
        ("测试", demo_07_testing),
        ("API服务", demo_08_api),
        ("监控指标", demo_09_monitoring),
        ("成本优化", demo_10_cost),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            if asyncio.iscoroutinefunction(demo_func):
                await demo_func()
            else:
                demo_func()
        except Exception as e:
            print(f"\n⚠ {name} 演示出错: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 查看 PROJECT_README.md 了解详细文档")
    print("  2. 运行 pytest 07-testing/src/ -v 执行测试")
    print("  3. 启动 API 服务: python 08-api-service/src/api_service.py")
    print("  4. 访问 http://localhost:8000/docs 查看API文档")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
