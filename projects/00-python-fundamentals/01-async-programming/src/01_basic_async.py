"""
异步编程基础
=============

本模块介绍Python异步编程的基础概念：
- 协程（Coroutine）
- async/await 关键字
- asyncio 事件循环
- 异步函数的定义和调用

在AI Agent开发中，异步编程是提高性能的关键技术。
"""

import asyncio
import time
from typing import List


# ============================================================================
# 1. 基础概念：协程（Coroutine）
# ============================================================================

async def simple_coroutine() -> str:
    """
    最简单的协程函数

    使用 async def 定义的函数就是协程函数
    调用协程函数不会立即执行，而是返回一个协程对象
    """
    print("协程开始执行")
    await asyncio.sleep(1)  # 模拟异步操作，暂停1秒
    print("协程执行完成")
    return "协程返回值"


async def fetch_data(source: str, delay: float = 1.0) -> str:
    """
    模拟异步获取数据

    Args:
        source: 数据源名称
        delay: 模拟延迟时间（秒）

    Returns:
        获取到的数据
    """
    print(f"[{source}] 开始获取数据...")
    await asyncio.sleep(delay)  # await 暂停当前协程，让其他协程执行
    print(f"[{source}] 数据获取完成")
    return f"来自 {source} 的数据"


# ============================================================================
# 2. 同步 vs 异步对比
# ============================================================================

def sync_fetch(source: str, delay: float = 1.0) -> str:
    """同步获取数据（阻塞式）"""
    print(f"[同步-{source}] 开始获取...")
    time.sleep(delay)  # 阻塞整个程序
    print(f"[同步-{source}] 完成")
    return f"同步数据: {source}"


async def compare_sync_vs_async():
    """
    对比同步和异步执行的性能差异

    在AI开发中，同步调用会导致等待时间累加
    异步调用可以并发执行，大幅提升效率
    """
    print("=" * 60)
    print("示例1: 同步执行（阻塞式）")
    print("=" * 60)

    start = time.time()
    # 同步：依次执行，总时间 = 1 + 1 + 1 = 3秒
    result1 = sync_fetch("API-1", 1.0)
    result2 = sync_fetch("API-2", 1.0)
    result3 = sync_fetch("API-3", 1.0)
    sync_time = time.time() - start

    print(f"同步执行总耗时: {sync_time:.2f}秒\n")

    print("=" * 60)
    print("示例2: 异步执行（并发式）")
    print("=" * 60)

    start = time.time()
    # 异步：并发执行，总时间 = max(1, 1, 1) ≈ 1秒
    results = await asyncio.gather(
        fetch_data("API-1", 1.0),
        fetch_data("API-2", 1.0),
        fetch_data("API-3", 1.0)
    )
    async_time = time.time() - start

    print(f"异步执行总耗时: {async_time:.2f}秒")
    print(f"性能提升: {sync_time / async_time:.2f}x\n")


# ============================================================================
# 3. 多个协程的执行方式
# ============================================================================

async def task_with_result(task_id: int, delay: float) -> dict:
    """
    执行一个任务并返回结果

    Args:
        task_id: 任务ID
        delay: 执行时间

    Returns:
        任务结果字典
    """
    print(f"  任务 {task_id} 开始执行")
    await asyncio.sleep(delay)
    result = {
        "task_id": task_id,
        "status": "completed",
        "delay": delay
    }
    print(f"  任务 {task_id} 执行完成")
    return result


async def sequential_execution():
    """
    顺序执行（串行）

    使用 await 依次等待每个任务完成
    适用场景：任务之间有依赖关系
    """
    print("\n方式1: 顺序执行")
    print("-" * 40)

    start = time.time()

    # 依次执行
    result1 = await task_with_result(1, 1.0)
    result2 = await task_with_result(2, 0.5)
    result3 = await task_with_result(3, 0.5)

    elapsed = time.time() - start
    print(f"  总耗时: {elapsed:.2f}秒 (1.0 + 0.5 + 0.5 = 2.0秒)")

    return [result1, result2, result3]


async def concurrent_execution():
    """
    并发执行（并行）

    使用 asyncio.gather() 同时执行多个任务
    适用场景：任务相互独立，可以同时执行
    """
    print("\n方式2: 并发执行")
    print("-" * 40)

    start = time.time()

    # 并发执行
    results = await asyncio.gather(
        task_with_result(1, 1.0),
        task_with_result(2, 0.5),
        task_with_result(3, 0.5)
    )

    elapsed = time.time() - start
    print(f"  总耗时: {elapsed:.2f}秒 (max(1.0, 0.5, 0.5) ≈ 1.0秒)")

    return results


async def task_creation_example():
    """
    使用 create_task 创建任务

    create_task 会立即启动任务的执行
    适用场景：需要立即开始任务，稍后等待结果
    """
    print("\n方式3: 使用 create_task")
    print("-" * 40)

    start = time.time()

    # 创建任务（立即开始执行）
    task1 = asyncio.create_task(task_with_result(1, 1.0))
    task2 = asyncio.create_task(task_with_result(2, 0.5))
    task3 = asyncio.create_task(task_with_result(3, 0.5))

    print("  所有任务已启动，可以做其他事情...")
    await asyncio.sleep(0.2)  # 模拟做其他工作
    print("  现在等待任务完成...")

    # 等待所有任务完成
    result1 = await task1
    result2 = await task2
    result3 = await task3

    elapsed = time.time() - start
    print(f"  总耗时: {elapsed:.2f}秒")

    return [result1, result2, result3]


# ============================================================================
# 4. AI场景示例：并发调用多个LLM
# ============================================================================

async def mock_llm_call(model: str, prompt: str, delay: float = 1.0) -> dict:
    """
    模拟LLM API调用

    在实际应用中，这里会调用真实的LLM API
    如 OpenAI GPT、Anthropic Claude、本地模型等

    Args:
        model: 模型名称
        prompt: 提示词
        delay: 模拟API响应时间

    Returns:
        LLM响应结果
    """
    print(f"  [{model}] 发送请求: {prompt[:30]}...")
    await asyncio.sleep(delay)  # 模拟网络延迟和推理时间

    response = {
        "model": model,
        "prompt": prompt,
        "response": f"来自 {model} 的响应",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }

    print(f"  [{model}] 收到响应")
    return response


async def parallel_llm_inference():
    """
    AI应用场景：并行推理

    场景1: 对同一个问题询问多个模型，对比结果
    场景2: 将复杂任务拆分，并行调用多个专家Agent
    场景3: 批量处理用户请求
    """
    print("\nAI应用示例: 并行LLM推理")
    print("=" * 60)

    prompt = "请解释什么是人工智能？"

    start = time.time()

    # 并行调用多个模型
    results = await asyncio.gather(
        mock_llm_call("gpt-4", prompt, 1.5),
        mock_llm_call("claude-3", prompt, 1.2),
        mock_llm_call("gemini-pro", prompt, 1.0)
    )

    elapsed = time.time() - start

    print(f"\n并行推理完成:")
    for result in results:
        print(f"  - {result['model']}: {result['response']}")

    print(f"\n总耗时: {elapsed:.2f}秒")
    print(f"如果串行执行需要: {1.5 + 1.2 + 1.0:.1f}秒")
    print(f"性能提升: {(1.5 + 1.2 + 1.0) / elapsed:.2f}x")


# ============================================================================
# 5. 运行示例
# ============================================================================

async def main():
    """主函数：演示所有基础异步编程概念"""

    print("\n" + "=" * 60)
    print("Python 异步编程基础教程")
    print("=" * 60)

    # 示例1: 最简单的协程
    print("\n【示例1】简单协程")
    print("-" * 60)
    result = await simple_coroutine()
    print(f"返回值: {result}")

    # 示例2: 同步 vs 异步对比
    await compare_sync_vs_async()

    # 示例3: 多种执行方式对比
    print("\n【示例3】执行方式对比")
    print("=" * 60)
    await sequential_execution()
    await concurrent_execution()
    await task_creation_example()

    # 示例4: AI实际应用
    await parallel_llm_inference()

    print("\n" + "=" * 60)
    print("教程完成！")
    print("=" * 60)
    print("\n关键要点:")
    print("1. async def 定义协程函数")
    print("2. await 等待协程执行并获取结果")
    print("3. asyncio.gather() 并发执行多个协程")
    print("4. asyncio.create_task() 立即启动任务")
    print("5. 异步编程大幅提升I/O密集型任务的性能")
    print("6. 在AI开发中，异步可以并行调用多个模型/API")


if __name__ == "__main__":
    # 运行异步主函数
    # asyncio.run() 是Python 3.7+ 推荐的运行方式
    asyncio.run(main())
