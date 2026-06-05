"""
异步HTTP请求 - 实战示例
=====================

本模块演示如何在AI应用中进行异步HTTP请求：
- 使用 aiohttp 和 httpx 进行异步请求
- 并发调用多个API
- 真实的LLM API调用示例
- 错误处理和重试

这是AI Agent开发中最常用的技术。
"""

import asyncio
import os
from typing import List, Dict, Optional
from datetime import datetime
import json


# ============================================================================
# 1. 使用 httpx 进行异步HTTP请求
# ============================================================================

async def httpx_example():
    """
    使用 httpx 进行异步请求

    httpx 是一个现代化的HTTP客户端，API类似 requests
    但支持异步操作，非常适合AI应用
    """
    print("\n【示例1】使用 httpx 异步请求")
    print("=" * 60)

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 单个请求
            print("\n1. 单个请求:")
            response = await client.get("https://httpbin.org/delay/1")
            print(f"   状态码: {response.status_code}")
            print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")

            # 并发多个请求
            print("\n2. 并发请求:")
            urls = [
                "https://httpbin.org/delay/1",
                "https://httpbin.org/delay/2",
                "https://httpbin.org/delay/1"
            ]

            start = asyncio.get_event_loop().time()

            # 并发执行
            responses = await asyncio.gather(
                *[client.get(url) for url in urls]
            )

            elapsed = asyncio.get_event_loop().time() - start

            print(f"   完成 {len(responses)} 个请求")
            print(f"   总耗时: {elapsed:.2f}秒 (并发)")
            print(f"   如果串行: {1+2+1}秒")

    except ImportError:
        print("   ⚠ 需要安装 httpx: pip install httpx")
    except Exception as e:
        print(f"   错误: {e}")


# ============================================================================
# 2. 使用 aiohttp 进行异步请求
# ============================================================================

async def aiohttp_example():
    """
    使用 aiohttp 进行异步请求

    aiohttp 是另一个流行的异步HTTP库
    性能更高，但API稍复杂
    """
    print("\n【示例2】使用 aiohttp 异步请求")
    print("=" * 60)

    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            print("\n并发获取多个API:")

            urls = [
                "https://httpbin.org/uuid",
                "https://httpbin.org/uuid",
                "https://httpbin.org/uuid"
            ]

            async def fetch(url: str) -> dict:
                async with session.get(url) as response:
                    return await response.json()

            results = await asyncio.gather(*[fetch(url) for url in urls])

            for i, result in enumerate(results, 1):
                print(f"   请求 {i}: {result.get('uuid', 'N/A')}")

    except ImportError:
        print("   ⚠ 需要安装 aiohttp: pip install aiohttp")
    except Exception as e:
        print(f"   错误: {e}")


# ============================================================================
# 3. 模拟LLM API调用（无需真实API密钥）
# ============================================================================

class MockLLMClient:
    """
    模拟LLM客户端

    模拟真实的LLM API调用行为
    包括延迟、token计数等
    """

    def __init__(self, model: str = "gpt-4"):
        self.model = model

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict:
        """
        模拟聊天完成API

        Args:
            messages: 消息列表
            temperature: 温度参数

        Returns:
            API响应
        """
        # 模拟API延迟（1-3秒）
        import random
        delay = random.uniform(1.0, 3.0)
        await asyncio.sleep(delay)

        # 模拟响应
        prompt_tokens = sum(len(m["content"].split()) for m in messages)
        completion_tokens = random.randint(20, 100)

        return {
            "id": f"chatcmpl-{random.randint(1000, 9999)}",
            "model": self.model,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"这是来自 {self.model} 的模拟响应。"
                               f"处理时间: {delay:.2f}秒"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }

    async def stream_completion(
        self,
        messages: List[Dict[str, str]]
    ):
        """
        模拟流式响应

        逐块返回生成的内容
        """
        response_text = (
            f"这是来自 {self.model} 的流式响应。"
            "流式输出可以降低首字延迟，提升用户体验。"
            "在实际应用中，每个chunk都是模型实时生成的。"
        )

        for char in response_text:
            await asyncio.sleep(0.05)  # 模拟生成延迟
            yield {
                "choices": [{
                    "delta": {"content": char}
                }]
            }


async def mock_llm_example():
    """模拟LLM调用示例"""
    print("\n【示例3】模拟LLM API调用")
    print("=" * 60)

    client = MockLLMClient("gpt-4")

    # 单个调用
    print("\n1. 单个聊天完成:")
    messages = [{"role": "user", "content": "什么是AI Agent?"}]

    response = await client.chat_completion(messages)
    print(f"   模型: {response['model']}")
    print(f"   响应: {response['choices'][0]['message']['content']}")
    print(f"   Token使用: {response['usage']['total_tokens']}")

    # 并发多个调用
    print("\n2. 并发多个查询:")

    queries = [
        "什么是机器学习?",
        "什么是深度学习?",
        "什么是强化学习?"
    ]

    start = asyncio.get_event_loop().time()

    tasks = [
        client.chat_completion([{"role": "user", "content": q}])
        for q in queries
    ]

    responses = await asyncio.gather(*tasks)

    elapsed = asyncio.get_event_loop().time() - start

    for i, resp in enumerate(responses, 1):
        content = resp['choices'][0]['message']['content']
        tokens = resp['usage']['total_tokens']
        print(f"   查询 {i}: {queries[i-1][:20]}...")
        print(f"           响应: {content[:50]}...")
        print(f"           Tokens: {tokens}")

    print(f"\n   并发耗时: {elapsed:.2f}秒")

    # 流式输出
    print("\n3. 流式输出:")
    print("   ", end="", flush=True)

    async for chunk in client.stream_completion(messages):
        content = chunk['choices'][0]['delta'].get('content', '')
        print(content, end="", flush=True)

    print("\n")


# ============================================================================
# 4. 并发调用多个LLM模型
# ============================================================================

async def multi_model_comparison():
    """
    并发调用多个模型，对比结果

    实际场景：
    - A/B测试不同模型
    - 集成多个模型的响应
    - 选择最佳答案
    """
    print("\n【示例4】并发调用多个模型")
    print("=" * 60)

    models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]
    prompt = "解释什么是神经网络"

    print(f"\n问题: {prompt}")
    print("同时询问3个模型...\n")

    start = asyncio.get_event_loop().time()

    # 创建多个客户端
    tasks = [
        MockLLMClient(model).chat_completion([
            {"role": "user", "content": prompt}
        ])
        for model in models
    ]

    responses = await asyncio.gather(*tasks)

    elapsed = asyncio.get_event_loop().time() - start

    # 显示结果
    for i, (model, resp) in enumerate(zip(models, responses), 1):
        content = resp['choices'][0]['message']['content']
        tokens = resp['usage']['total_tokens']

        print(f"{i}. {model}:")
        print(f"   {content}")
        print(f"   (Tokens: {tokens})\n")

    print(f"总耗时: {elapsed:.2f}秒 (并发)")
    print("如果串行调用需要约 4-9 秒")


# ============================================================================
# 5. 带重试的API调用
# ============================================================================

class RetryableHTTPClient:
    """
    带重试机制的HTTP客户端

    实现指数退避重试策略
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[Dict]:
        """
        带重试的HTTP请求

        Args:
            method: HTTP方法 (GET, POST等)
            url: 请求URL
            **kwargs: 其他参数

        Returns:
            响应数据，失败返回None
        """
        for attempt in range(self.max_retries):
            try:
                # 这里使用模拟请求
                # 实际应用中替换为真实的HTTP库
                await asyncio.sleep(0.5)

                # 模拟30%失败率
                import random
                if random.random() < 0.3:
                    raise Exception("API调用失败")

                return {
                    "status": "success",
                    "data": "响应数据"
                }

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    print(f"   第 {attempt + 1} 次尝试失败: {e}")
                    print(f"   等待 {delay:.1f}秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    print(f"   达到最大重试次数，请求失败")
                    return None


async def retry_example():
    """重试机制示例"""
    print("\n【示例5】带重试的API调用")
    print("=" * 60)

    client = RetryableHTTPClient(max_retries=3, base_delay=0.5)

    print("\n执行可能失败的API调用:")
    result = await client.request_with_retry("POST", "https://api.example.com")

    if result:
        print(f"   ✓ 请求成功: {result}")
    else:
        print(f"   ✗ 请求最终失败")


# ============================================================================
# 6. 批量处理用户请求
# ============================================================================

async def process_user_request(
    user_id: str,
    request: str,
    semaphore: asyncio.Semaphore
) -> Dict:
    """
    处理单个用户请求

    使用信号量限制并发数
    """
    async with semaphore:
        print(f"   [用户 {user_id}] 开始处理请求")

        client = MockLLMClient()
        response = await client.chat_completion([
            {"role": "user", "content": request}
        ])

        print(f"   [用户 {user_id}] 处理完成")

        return {
            "user_id": user_id,
            "request": request,
            "response": response['choices'][0]['message']['content'],
            "tokens": response['usage']['total_tokens']
        }


async def batch_processing_example():
    """
    批量处理示例

    场景：Web服务器同时处理多个用户请求
    使用信号量限制并发，避免资源耗尽
    """
    print("\n【示例6】批量处理用户请求")
    print("=" * 60)

    # 模拟10个用户请求
    user_requests = [
        (f"user_{i}", f"请求 {i}: 告诉我关于AI的知识")
        for i in range(1, 11)
    ]

    # 限制最多5个并发
    max_concurrent = 5
    semaphore = asyncio.Semaphore(max_concurrent)

    print(f"\n处理 {len(user_requests)} 个请求")
    print(f"最大并发: {max_concurrent}\n")

    start = asyncio.get_event_loop().time()

    tasks = [
        process_user_request(user_id, request, semaphore)
        for user_id, request in user_requests
    ]

    results = await asyncio.gather(*tasks)

    elapsed = asyncio.get_event_loop().time() - start

    print(f"\n所有请求处理完成:")
    print(f"   总请求数: {len(results)}")
    print(f"   总耗时: {elapsed:.2f}秒")
    print(f"   平均耗时: {elapsed / len(results):.2f}秒/请求")

    total_tokens = sum(r['tokens'] for r in results)
    print(f"   总Token使用: {total_tokens}")


# ============================================================================
# 7. 真实API调用示例（需要API密钥）
# ============================================================================

async def real_openai_example():
    """
    真实的OpenAI API调用

    需要设置环境变量: OPENAI_API_KEY

    注意：这是演示代码，实际运行需要：
    1. pip install openai
    2. export OPENAI_API_KEY="your-key"
    """
    print("\n【示例7】真实OpenAI API调用")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("   ⚠ 未设置 OPENAI_API_KEY 环境变量")
        print("   这是示例代码，展示如何使用真实API:\n")
        print("   ```python")
        print("   from openai import AsyncOpenAI")
        print("")
        print("   client = AsyncOpenAI(api_key='your-key')")
        print("")
        print("   response = await client.chat.completions.create(")
        print("       model='gpt-4',")
        print("       messages=[{'role': 'user', 'content': 'Hello!'}]")
        print("   )")
        print("")
        print("   print(response.choices[0].message.content)")
        print("   ```")
        return

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)

        print("\n调用真实API...")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "用一句话解释什么是异步编程"}
            ]
        )

        print(f"   响应: {response.choices[0].message.content}")
        print(f"   Tokens: {response.usage.total_tokens}")

    except ImportError:
        print("   ⚠ 需要安装 OpenAI SDK: pip install openai")
    except Exception as e:
        print(f"   错误: {e}")


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("异步HTTP请求 - AI应用实战")
    print("=" * 60)

    # HTTP请求示例
    await httpx_example()
    await aiohttp_example()

    # LLM调用示例
    await mock_llm_example()
    await multi_model_comparison()

    # 高级模式
    await retry_example()
    await batch_processing_example()

    # 真实API（可选）
    await real_openai_example()

    print("\n" + "=" * 60)
    print("实战要点总结")
    print("=" * 60)
    print("1. 使用 httpx 或 aiohttp 进行异步HTTP请求")
    print("2. 并发调用多个LLM API，提升响应速度")
    print("3. 使用信号量限制并发数，避免速率限制")
    print("4. 实现重试机制，提高系统可靠性")
    print("5. 批量处理用户请求，提升吞吐量")
    print("6. 流式输出降低首字延迟，提升体验")
    print("\n推荐阅读:")
    print("- OpenAI API文档: https://platform.openai.com/docs")
    print("- httpx文档: https://www.python-httpx.org/")
    print("- aiohttp文档: https://docs.aiohttp.org/")


if __name__ == "__main__":
    asyncio.run(main())
