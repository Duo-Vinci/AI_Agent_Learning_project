"""
异步编程进阶模式
===============

本模块介绍常用的异步编程模式：
- 超时控制
- 错误处理
- 异步生成器
- 异步上下文管理器
- 信号量和限流

这些是AI Agent开发中必备的高级技术。
"""

import asyncio
import random
from typing import AsyncGenerator, List, Optional
from datetime import datetime


# ============================================================================
# 1. 超时控制
# ============================================================================

async def slow_operation(task_id: int) -> str:
    """模拟一个可能很慢的操作"""
    delay = random.uniform(1, 5)  # 随机延迟1-5秒
    print(f"  任务 {task_id} 需要 {delay:.1f}秒")
    await asyncio.sleep(delay)
    return f"任务 {task_id} 完成"


async def timeout_example():
    """
    使用 wait_for 设置超时

    在AI应用中，LLM API调用可能很慢或卡住
    设置超时可以避免无限等待
    """
    print("\n【示例1】超时控制")
    print("=" * 60)

    # 设置3秒超时
    timeout = 3.0

    for i in range(1, 4):
        try:
            print(f"\n任务 {i} (超时限制: {timeout}秒)")
            result = await asyncio.wait_for(
                slow_operation(i),
                timeout=timeout
            )
            print(f"  ✓ {result}")

        except asyncio.TimeoutError:
            print(f"  ✗ 任务 {i} 超时！")


async def timeout_with_default():
    """
    超时后返回默认值

    实际应用：LLM调用超时后使用缓存或默认响应
    """
    print("\n【示例2】超时后使用默认值")
    print("-" * 60)

    async def call_with_fallback(task_id: int, timeout: float = 2.0):
        """调用失败时返回默认值"""
        try:
            result = await asyncio.wait_for(
                slow_operation(task_id),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            print(f"  任务 {task_id} 超时，使用默认值")
            return f"任务 {task_id} 默认响应（来自缓存）"

    results = await asyncio.gather(
        call_with_fallback(1),
        call_with_fallback(2),
        call_with_fallback(3)
    )

    print("\n结果:")
    for result in results:
        print(f"  - {result}")


# ============================================================================
# 2. 错误处理
# ============================================================================

async def risky_operation(task_id: int, fail_rate: float = 0.3) -> str:
    """可能失败的操作"""
    await asyncio.sleep(0.5)

    if random.random() < fail_rate:
        raise ValueError(f"任务 {task_id} 失败!")

    return f"任务 {task_id} 成功"


async def error_handling_example():
    """
    异步函数的错误处理

    方式1: try-except 捕获单个任务的错误
    方式2: gather 的 return_exceptions 参数
    """
    print("\n【示例3】错误处理")
    print("=" * 60)

    print("\n方式1: 单个任务的错误处理")
    print("-" * 40)

    for i in range(1, 4):
        try:
            result = await risky_operation(i, fail_rate=0.5)
            print(f"  ✓ {result}")
        except ValueError as e:
            print(f"  ✗ 捕获错误: {e}")

    print("\n方式2: gather 批量错误处理")
    print("-" * 40)

    # return_exceptions=True: 将异常作为结果返回，而不是抛出
    results = await asyncio.gather(
        risky_operation(1, fail_rate=0.5),
        risky_operation(2, fail_rate=0.5),
        risky_operation(3, fail_rate=0.5),
        return_exceptions=True  # 关键参数
    )

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"  ✗ 任务 {i} 失败: {result}")
        else:
            print(f"  ✓ 任务 {i} 成功: {result}")


async def retry_with_backoff(
    operation,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Optional[str]:
    """
    带指数退避的重试机制

    AI应用场景：LLM API可能因为限流或临时故障失败
    使用重试机制可以提高成功率

    Args:
        operation: 要执行的协程
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）

    Returns:
        操作结果，失败返回None
    """
    for attempt in range(max_retries):
        try:
            result = await operation
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # 指数退避
                print(f"    第 {attempt + 1} 次尝试失败: {e}")
                print(f"    等待 {delay:.1f}秒后重试...")
                await asyncio.sleep(delay)
            else:
                print(f"    达到最大重试次数，放弃")
                return None


async def retry_example():
    """重试机制示例"""
    print("\n【示例4】重试机制（指数退避）")
    print("=" * 60)

    result = await retry_with_backoff(
        risky_operation(1, fail_rate=0.7),
        max_retries=3,
        base_delay=0.5
    )

    if result:
        print(f"\n✓ 最终成功: {result}")
    else:
        print(f"\n✗ 最终失败")


# ============================================================================
# 3. 异步生成器
# ============================================================================

async def async_data_stream(count: int) -> AsyncGenerator[dict, None]:
    """
    异步生成器：逐个产生数据

    使用 yield 关键字，每次产生一个值
    适用场景：
    - 流式输出（LLM streaming）
    - 大量数据的分批处理
    - 实时数据流
    """
    for i in range(1, count + 1):
        await asyncio.sleep(0.3)  # 模拟数据生成延迟

        data = {
            "index": i,
            "timestamp": datetime.now().isoformat(),
            "value": random.randint(1, 100)
        }

        yield data


async def stream_llm_response(prompt: str) -> AsyncGenerator[str, None]:
    """
    模拟LLM流式响应

    AI应用场景：
    - 像ChatGPT一样逐字输出
    - 降低首字延迟，提升用户体验
    - 可以提前展示部分结果
    """
    response_text = "这是一个模拟的LLM响应，将会逐词输出。异步生成器非常适合流式场景。"

    words = response_text.split()

    for word in words:
        await asyncio.sleep(0.1)  # 模拟生成延迟
        yield word + " "


async def async_generator_example():
    """异步生成器示例"""
    print("\n【示例5】异步生成器")
    print("=" * 60)

    print("\n场景1: 数据流处理")
    print("-" * 40)

    async for data in async_data_stream(5):
        print(f"  收到数据: index={data['index']}, value={data['value']}")

    print("\n场景2: LLM流式输出")
    print("-" * 40)
    print("  ", end="", flush=True)

    async for chunk in stream_llm_response("测试提示"):
        print(chunk, end="", flush=True)

    print("\n")


# ============================================================================
# 4. 异步上下文管理器
# ============================================================================

class AsyncResource:
    """
    异步资源管理

    使用 async with 自动管理资源的创建和清理
    类似于同步的 with 语句
    """

    def __init__(self, name: str):
        self.name = name
        self.connected = False

    async def __aenter__(self):
        """进入上下文时调用"""
        print(f"  [{self.name}] 正在连接...")
        await asyncio.sleep(0.5)  # 模拟连接延迟
        self.connected = True
        print(f"  [{self.name}] 连接成功")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时调用"""
        print(f"  [{self.name}] 正在关闭...")
        await asyncio.sleep(0.3)  # 模拟清理延迟
        self.connected = False
        print(f"  [{self.name}] 已关闭")

    async def query(self, data: str) -> str:
        """执行查询"""
        if not self.connected:
            raise RuntimeError("资源未连接")

        await asyncio.sleep(0.2)
        return f"[{self.name}] 查询结果: {data}"


async def async_context_manager_example():
    """
    异步上下文管理器示例

    AI应用场景：
    - 数据库连接管理
    - API会话管理
    - 文件和网络资源管理
    """
    print("\n【示例6】异步上下文管理器")
    print("=" * 60)

    # 自动管理资源的生命周期
    async with AsyncResource("数据库") as db:
        result = await db.query("SELECT * FROM users")
        print(f"  {result}")

    # 退出 async with 后，资源自动清理

    print("\n并发使用多个资源:")
    print("-" * 40)

    async with AsyncResource("Redis") as cache, \
               AsyncResource("PostgreSQL") as db:
        cache_result = await cache.query("GET user:1")
        db_result = await db.query("SELECT * FROM users WHERE id=1")
        print(f"  {cache_result}")
        print(f"  {db_result}")


# ============================================================================
# 5. 信号量和限流
# ============================================================================

async def rate_limited_task(
    task_id: int,
    semaphore: asyncio.Semaphore
) -> str:
    """
    使用信号量限制并发数

    semaphore 确保同时只有N个任务在执行
    """
    async with semaphore:  # 获取信号量
        print(f"  任务 {task_id} 开始执行")
        await asyncio.sleep(1)  # 模拟工作
        print(f"  任务 {task_id} 执行完成")
        return f"任务 {task_id} 结果"
    # 退出 async with 后，信号量自动释放


async def semaphore_example():
    """
    信号量限流示例

    AI应用场景：
    - 限制同时调用的LLM API数量（避免超出速率限制）
    - 控制数据库连接池大小
    - 限制并发请求数
    """
    print("\n【示例7】信号量限流")
    print("=" * 60)

    # 创建信号量：最多允许3个并发
    max_concurrent = 3
    semaphore = asyncio.Semaphore(max_concurrent)

    print(f"启动10个任务，但最多 {max_concurrent} 个并发执行")
    print("-" * 40)

    # 创建10个任务
    tasks = [
        rate_limited_task(i, semaphore)
        for i in range(1, 11)
    ]

    # 并发执行（但受信号量限制）
    results = await asyncio.gather(*tasks)

    print("\n所有任务完成")


async def api_rate_limiter(calls_per_second: int = 5):
    """
    API限流器

    实际应用：控制LLM API调用频率
    避免触发速率限制（rate limit）
    """
    print(f"\n【示例8】API限流器 (每秒{calls_per_second}次)")
    print("=" * 60)

    semaphore = asyncio.Semaphore(calls_per_second)
    interval = 1.0 / calls_per_second  # 每次调用的间隔

    async def limited_api_call(call_id: int):
        """受限的API调用"""
        async with semaphore:
            print(f"  [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                  f"API调用 {call_id}")
            await asyncio.sleep(interval)  # 限制调用频率
            return f"调用 {call_id} 完成"

    # 快速发起多个调用
    tasks = [limited_api_call(i) for i in range(1, 11)]
    await asyncio.gather(*tasks)


# ============================================================================
# 6. 综合示例：多Agent并发系统
# ============================================================================

class Agent:
    """简单的AI Agent"""

    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty

    async def process(self, task: str) -> dict:
        """处理任务"""
        print(f"  [{self.name}] 开始处理: {task}")

        # 模拟LLM推理时间（随机1-3秒）
        processing_time = random.uniform(1, 3)
        await asyncio.sleep(processing_time)

        result = {
            "agent": self.name,
            "specialty": self.specialty,
            "task": task,
            "result": f"{self.specialty}相关的分析结果",
            "processing_time": f"{processing_time:.2f}秒"
        }

        print(f"  [{self.name}] 处理完成")
        return result


async def multi_agent_system():
    """
    多Agent并发系统

    实际场景：
    - 研究Agent：收集信息
    - 分析Agent：分析数据
    - 写作Agent：生成内容
    - 审核Agent：质量检查
    """
    print("\n【示例9】多Agent并发系统")
    print("=" * 60)

    # 创建多个专家Agent
    agents = [
        Agent("研究员", "信息收集"),
        Agent("数据分析师", "数据分析"),
        Agent("内容作家", "内容创作"),
        Agent("质量审核员", "质量检查")
    ]

    task = "分析AI Agent市场趋势"

    print(f"\n任务: {task}")
    print("4个Agent并行工作...\n")

    start = asyncio.get_event_loop().time()

    # 并发执行所有Agent
    results = await asyncio.gather(
        *[agent.process(task) for agent in agents]
    )

    elapsed = asyncio.get_event_loop().time() - start

    print(f"\n所有Agent完成:")
    for result in results:
        print(f"  - {result['agent']}: {result['result']} "
              f"(耗时: {result['processing_time']})")

    print(f"\n总耗时: {elapsed:.2f}秒")
    total_sequential = sum(float(r['processing_time'].split('秒')[0])
                          for r in results)
    print(f"串行执行需要: {total_sequential:.2f}秒")
    print(f"并发加速比: {total_sequential / elapsed:.2f}x")


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """演示所有异步编程进阶模式"""

    print("\n" + "=" * 60)
    print("Python 异步编程进阶模式")
    print("=" * 60)

    # 1. 超时控制
    await timeout_example()
    await timeout_with_default()

    # 2. 错误处理
    await error_handling_example()
    await retry_example()

    # 3. 异步生成器
    await async_generator_example()

    # 4. 异步上下文管理器
    await async_context_manager_example()

    # 5. 信号量和限流
    await semaphore_example()
    await api_rate_limiter(calls_per_second=3)

    # 6. 综合示例
    await multi_agent_system()

    print("\n" + "=" * 60)
    print("进阶模式总结")
    print("=" * 60)
    print("1. wait_for() - 超时控制，避免无限等待")
    print("2. return_exceptions - 批量错误处理")
    print("3. 异步生成器 - 流式数据处理")
    print("4. 异步上下文管理器 - 自动资源管理")
    print("5. Semaphore - 限制并发数，控制资源使用")
    print("6. 重试机制 - 提高系统可靠性")
    print("7. 多Agent并发 - AI系统的核心架构模式")


if __name__ == "__main__":
    asyncio.run(main())
