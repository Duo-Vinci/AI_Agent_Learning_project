"""
真实LLM API集成示例
==================

本模块演示如何集成真实的LLM API：
- OpenAI GPT
- Anthropic Claude
- 使用装饰器、异步、错误处理等技术
- 实际的AI Agent应用

运行此文件需要：
1. pip install openai anthropic python-dotenv
2. 设置环境变量 OPENAI_API_KEY 和/或 ANTHROPIC_API_KEY
"""

import os
import asyncio
import time
from typing import Optional, List, Dict, Literal
from functools import wraps
from contextlib import contextmanager

# 尝试导入第三方库
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠ OpenAI SDK未安装: pip install openai")

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠ Anthropic SDK未安装: pip install anthropic")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠ python-dotenv未安装: pip install python-dotenv")


# ============================================================================
# 装饰器：监控LLM调用
# ============================================================================

def monitor_llm_call(func):
    """监控LLM调用的装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        print(f"\n🤖 [{func.__name__}] 开始调用...")

        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start

            print(f"✓ 调用成功")
            print(f"⏱ 耗时: {elapsed:.2f}秒")

            return result

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ 调用失败: {e}")
            print(f"⏱ 耗时: {elapsed:.2f}秒")
            raise

    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait = delay * (2 ** attempt)
                        print(f"  ⚠ 第 {attempt + 1} 次尝试失败，{wait:.1f}秒后重试...")
                        await asyncio.sleep(wait)
                    else:
                        print(f"  ✗ 达到最大重试次数")
                        raise
        return wrapper
    return decorator


# ============================================================================
# OpenAI GPT 集成
# ============================================================================

class GPTClient:
    """OpenAI GPT客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("需要设置 OPENAI_API_KEY")

        if not OPENAI_AVAILABLE:
            raise ImportError("需要安装 openai: pip install openai")

        self.client = AsyncOpenAI(api_key=self.api_key)

    @monitor_llm_call
    @retry_on_failure(max_retries=3)
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7
    ) -> Dict:
        """生成文本"""
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )

        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "model": model
        }

    @monitor_llm_call
    async def stream_generate(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo"
    ):
        """流式生成"""
        stream = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content


# ============================================================================
# Anthropic Claude 集成
# ============================================================================

class ClaudeClient:
    """Anthropic Claude客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要设置 ANTHROPIC_API_KEY")

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("需要安装 anthropic: pip install anthropic")

        self.client = AsyncAnthropic(api_key=self.api_key)

    @monitor_llm_call
    @retry_on_failure(max_retries=3)
    async def generate(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7
    ) -> Dict:
        """生成文本"""
        response = await self.client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "content": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
            "model": model
        }


# ============================================================================
# 多模型Agent
# ============================================================================

class MultiModelAgent:
    """
    多模型Agent

    可以同时使用多个LLM模型
    """

    def __init__(self):
        self.clients = {}

        # 尝试初始化各个客户端
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.clients["gpt"] = GPTClient()
                print("✓ GPT客户端已初始化")
            except Exception as e:
                print(f"✗ GPT客户端初始化失败: {e}")

        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.clients["claude"] = ClaudeClient()
                print("✓ Claude客户端已初始化")
            except Exception as e:
                print(f"✗ Claude客户端初始化失败: {e}")

        if not self.clients:
            print("⚠ 没有可用的LLM客户端，将使用模拟模式")

    async def generate(
        self,
        prompt: str,
        provider: Literal["gpt", "claude", "all"] = "gpt"
    ) -> Dict:
        """
        生成文本

        Args:
            prompt: 提示词
            provider: 使用的提供者（gpt/claude/all）

        Returns:
            生成结果
        """
        if not self.clients:
            return await self._mock_generate(prompt)

        if provider == "all":
            # 并发调用所有模型
            tasks = [
                client.generate(prompt)
                for client in self.clients.values()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            return {
                "providers": list(self.clients.keys()),
                "results": results
            }

        elif provider in self.clients:
            return await self.clients[provider].generate(prompt)

        else:
            raise ValueError(f"不支持的提供者: {provider}")

    async def _mock_generate(self, prompt: str) -> Dict:
        """模拟生成（当没有真实API时）"""
        print(f"\n🤖 [模拟模式] 生成响应...")
        await asyncio.sleep(1)
        return {
            "content": f"[模拟响应] 这是对 '{prompt[:30]}...' 的回复",
            "tokens": 50,
            "model": "mock"
        }

    async def compare_models(self, prompt: str) -> None:
        """
        对比不同模型的响应

        实用场景：
        - A/B测试
        - 模型评估
        - 选择最佳响应
        """
        print(f"\n{'='*60}")
        print(f"对比模型响应")
        print(f"{'='*60}")
        print(f"提示词: {prompt}\n")

        if not self.clients:
            print("⚠ 没有可用的客户端，使用模拟模式")
            result = await self._mock_generate(prompt)
            print(f"[模拟] {result['content']}")
            return

        for name, client in self.clients.items():
            print(f"\n{name.upper()}:")
            print("-" * 60)
            try:
                result = await client.generate(prompt)
                print(f"响应: {result['content'][:200]}...")
                print(f"Token: {result['tokens']}")
            except Exception as e:
                print(f"✗ 调用失败: {e}")


# ============================================================================
# 示例应用
# ============================================================================

async def basic_usage_example():
    """基础使用示例"""
    print("\n" + "="*60)
    print("示例1: 基础使用")
    print("="*60)

    agent = MultiModelAgent()

    # 单个查询
    result = await agent.generate(
        "用一句话解释什么是人工智能",
        provider="gpt"
    )

    if "content" in result:
        print(f"\n响应: {result['content']}")
        print(f"Token: {result.get('tokens', 'N/A')}")


async def comparison_example():
    """模型对比示例"""
    print("\n" + "="*60)
    print("示例2: 模型对比")
    print("="*60)

    agent = MultiModelAgent()

    await agent.compare_models(
        "什么是量子计算？请用简单的语言解释。"
    )


async def concurrent_queries_example():
    """并发查询示例"""
    print("\n" + "="*60)
    print("示例3: 并发查询")
    print("="*60)

    agent = MultiModelAgent()

    queries = [
        "什么是机器学习？",
        "什么是深度学习？",
        "什么是强化学习？"
    ]

    print(f"\n并发执行 {len(queries)} 个查询...\n")

    start = time.time()

    tasks = [agent.generate(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.time() - start

    print(f"\n结果:")
    print("-" * 60)
    for i, (query, result) in enumerate(zip(queries, results), 1):
        print(f"\n{i}. {query}")
        if isinstance(result, Exception):
            print(f"   ✗ 失败: {result}")
        elif "content" in result:
            print(f"   {result['content'][:100]}...")

    print(f"\n总耗时: {elapsed:.2f}秒")


async def stream_example():
    """流式输出示例"""
    print("\n" + "="*60)
    print("示例4: 流式输出")
    print("="*60)

    if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 需要OpenAI API才能演示流式输出")
        return

    try:
        client = GPTClient()

        print("\n流式输出（类似ChatGPT）:\n")
        print("  ", end="", flush=True)

        async for chunk in client.stream_generate("讲一个关于AI的短故事"):
            print(chunk, end="", flush=True)
            await asyncio.sleep(0.03)  # 控制输出速度

        print("\n")

    except Exception as e:
        print(f"\n✗ 流式输出失败: {e}")


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """运行所有示例"""

    print("\n" + "="*60)
    print("真实LLM API集成示例")
    print("="*60)

    # 检查环境
    print("\n环境检查:")
    print("-" * 60)
    print(f"OpenAI SDK: {'✓ 已安装' if OPENAI_AVAILABLE else '✗ 未安装'}")
    print(f"Anthropic SDK: {'✓ 已安装' if ANTHROPIC_AVAILABLE else '✗ 未安装'}")
    print(f"OpenAI API Key: {'✓ 已设置' if os.getenv('OPENAI_API_KEY') else '✗ 未设置'}")
    print(f"Anthropic API Key: {'✓ 已设置' if os.getenv('ANTHROPIC_API_KEY') else '✗ 未设置'}")

    # 运行示例
    await basic_usage_example()
    await comparison_example()
    await concurrent_queries_example()
    await stream_example()

    print("\n" + "="*60)
    print("集成完成！")
    print("="*60)
    print("\n关键技术:")
    print("1. 装饰器 - 监控和重试")
    print("2. 异步编程 - 并发调用")
    print("3. 错误处理 - 优雅失败")
    print("4. 类型注解 - 代码清晰")
    print("5. 上下文管理 - 资源管理")
    print("\n这些技术的组合是构建生产级AI应用的基础！")


if __name__ == "__main__":
    asyncio.run(main())
