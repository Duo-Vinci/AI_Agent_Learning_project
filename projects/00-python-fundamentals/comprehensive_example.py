"""
综合示例：AI Agent系统
====================

这个文件展示了如何将所有Python基础技术综合应用到一个完整的AI Agent系统中：

✅ 异步编程 - 并发处理多个任务
✅ 装饰器 - 监控、重试、缓存
✅ 类型注解 - 类型安全
✅ 错误处理 - 优雅失败和恢复
✅ 上下文管理器 - 资源管理

这是一个生产级AI系统的简化版本。
"""

import asyncio
import time
import json
from typing import List, Dict, Optional, Protocol, TypedDict, Literal, Generic, TypeVar
from dataclasses import dataclass
from contextlib import asynccontextmanager
from functools import wraps
from datetime import datetime


# ============================================================================
# 类型定义
# ============================================================================

Role = Literal["user", "assistant", "system"]


class Message(TypedDict):
    """消息类型"""
    role: Role
    content: str
    timestamp: Optional[str]


class AgentResponse(TypedDict):
    """Agent响应类型"""
    content: str
    tokens: int
    model: str
    elapsed: float


T = TypeVar('T')


# ============================================================================
# 自定义异常
# ============================================================================

class AgentError(Exception):
    """Agent错误基类"""
    pass


class AgentTimeoutError(AgentError):
    """超时错误"""
    def __init__(self, timeout: float):
        super().__init__(f"Agent执行超时: {timeout}秒")
        self.timeout = timeout


class AgentAPIError(AgentError):
    """API错误"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


# ============================================================================
# 装饰器：监控和增强
# ============================================================================

def monitor(func):
    """监控装饰器：记录执行时间和状态"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        func_name = func.__name__

        print(f"\n⏳ [{datetime.now().strftime('%H:%M:%S')}] {func_name} 开始...")

        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"✅ {func_name} 完成 (耗时: {elapsed:.2f}秒)")
            return result
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ {func_name} 失败: {e} (耗时: {elapsed:.2f}秒)")
            raise

    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器：失败时自动重试"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except AgentTimeoutError:
                    if attempt < max_attempts - 1:
                        wait = delay * (2 ** attempt)
                        print(f"   ⚠️  第 {attempt + 1} 次尝试失败，{wait:.1f}秒后重试...")
                        await asyncio.sleep(wait)
                    else:
                        print(f"   ❌ 达到最大重试次数")
                        raise
                except AgentAPIError as e:
                    # API错误通常不需要重试
                    print(f"   ❌ API错误: {e}")
                    raise
        return wrapper
    return decorator


class Cache(Generic[T]):
    """缓存装饰器类：带TTL的缓存"""

    def __init__(self, ttl: float = 300.0):
        self.ttl = ttl
        self.cache: Dict[str, tuple[T, float]] = {}

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 创建缓存键
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # 检查缓存
            if key in self.cache:
                result, timestamp = self.cache[key]
                age = time.time() - timestamp

                if age < self.ttl:
                    print(f"   💾 缓存命中 (年龄: {age:.1f}秒)")
                    return result
                else:
                    print(f"   ⏰ 缓存过期 (年龄: {age:.1f}秒)")
                    del self.cache[key]

            # 执行函数
            result = await func(*args, **kwargs)

            # 存入缓存
            self.cache[key] = (result, time.time())

            return result

        return wrapper


# ============================================================================
# 协议：定义接口
# ============================================================================

class LLMProvider(Protocol):
    """LLM提供者协议"""

    async def generate(self, messages: List[Message]) -> AgentResponse:
        """生成响应"""
        ...

    def get_model_name(self) -> str:
        """获取模型名称"""
        ...


# ============================================================================
# 上下文管理器：资源管理
# ============================================================================

@asynccontextmanager
async def agent_session(agent_name: str):
    """
    Agent会话上下文管理器

    管理Agent的生命周期和资源
    """
    print(f"\n{'='*60}")
    print(f"🚀 启动Agent会话: {agent_name}")
    print(f"{'='*60}")

    session_data = {
        "name": agent_name,
        "start_time": time.time(),
        "tasks_completed": 0,
        "tasks_failed": 0
    }

    try:
        yield session_data
    finally:
        elapsed = time.time() - session_data["start_time"]
        print(f"\n{'='*60}")
        print(f"📊 Agent会话统计: {agent_name}")
        print(f"{'='*60}")
        print(f"运行时间: {elapsed:.2f}秒")
        print(f"完成任务: {session_data['tasks_completed']}")
        print(f"失败任务: {session_data['tasks_failed']}")
        print(f"成功率: {session_data['tasks_completed'] / max(session_data['tasks_completed'] + session_data['tasks_failed'], 1) * 100:.1f}%")
        print(f"{'='*60}\n")


@asynccontextmanager
async def llm_connection(provider_name: str):
    """
    LLM连接上下文管理器

    管理LLM连接的建立和清理
    """
    print(f"   🔌 连接到 {provider_name}...")
    await asyncio.sleep(0.3)  # 模拟连接延迟

    connection = {
        "provider": provider_name,
        "connected": True,
        "requests": 0
    }

    try:
        print(f"   ✅ {provider_name} 连接成功")
        yield connection
    finally:
        print(f"   🔌 断开 {provider_name} 连接")
        print(f"   📊 总请求数: {connection['requests']}")


# ============================================================================
# 核心实现：LLM提供者
# ============================================================================

class MockLLMProvider:
    """
    模拟LLM提供者

    实现LLMProvider协议
    包含完整的错误处理和资源管理
    """

    def __init__(self, model: str, error_rate: float = 0.1):
        self.model = model
        self.error_rate = error_rate

    @monitor
    @retry(max_attempts=3, delay=0.5)
    async def generate(self, messages: List[Message]) -> AgentResponse:
        """生成响应"""
        import random

        # 模拟API延迟
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # 模拟随机错误
        if random.random() < self.error_rate:
            if random.random() < 0.5:
                raise AgentTimeoutError(timeout=5.0)
            else:
                raise AgentAPIError("服务暂时不可用", status_code=503)

        # 生成响应
        last_message = messages[-1] if messages else {"content": ""}

        return {
            "content": f"[{self.model}] 响应: {last_message['content']}",
            "tokens": random.randint(50, 200),
            "model": self.model,
            "elapsed": random.uniform(0.5, 1.5)
        }

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model


# ============================================================================
# AI Agent实现
# ============================================================================

@dataclass
class Agent:
    """
    AI Agent

    使用所有最佳实践：
    - 类型注解
    - 异步操作
    - 错误处理
    - 资源管理
    """

    name: str
    provider: LLMProvider
    system_prompt: Optional[str] = None

    def __post_init__(self):
        self.history: List[Message] = []
        if self.system_prompt:
            self.history.append({
                "role": "system",
                "content": self.system_prompt,
                "timestamp": datetime.now().isoformat()
            })

    @Cache(ttl=60.0)
    @monitor
    async def process(self, user_input: str) -> str:
        """
        处理用户输入

        完整的错误处理和资源管理
        """
        # 添加用户消息
        self.history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })

        try:
            # 调用LLM
            response = await self.provider.generate(self.history)

            # 添加助手消息
            self.history.append({
                "role": "assistant",
                "content": response["content"],
                "timestamp": datetime.now().isoformat()
            })

            return response["content"]

        except AgentError as e:
            error_msg = f"处理失败: {e}"
            print(f"   ❌ {error_msg}")

            # 记录错误到历史
            self.history.append({
                "role": "assistant",
                "content": f"[错误] {error_msg}",
                "timestamp": datetime.now().isoformat()
            })

            raise

    def get_history(self) -> List[Message]:
        """获取对话历史"""
        return self.history.copy()

    def clear_history(self) -> None:
        """清空历史（保留系统提示）"""
        if self.system_prompt:
            self.history = [self.history[0]]
        else:
            self.history = []


# ============================================================================
# 多Agent协作系统
# ============================================================================

class MultiAgentSystem:
    """
    多Agent协作系统

    展示异步并发和协作
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def add_agent(self, agent: Agent) -> None:
        """添加Agent"""
        self.agents[agent.name] = agent
        print(f"   ➕ 添加Agent: {agent.name}")

    @monitor
    async def parallel_process(self, task: str) -> Dict[str, str]:
        """
        并行处理任务

        所有Agent同时处理相同任务
        """
        print(f"\n📋 任务: {task}")
        print(f"👥 分配给 {len(self.agents)} 个Agent并行处理\n")

        # 并发执行
        tasks = {
            name: agent.process(task)
            for name, agent in self.agents.items()
        }

        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )

        # 整理结果
        output = {}
        for name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                output[name] = f"❌ 失败: {result}"
            else:
                output[name] = result

        return output

    @monitor
    async def sequential_process(self, tasks: List[str]) -> List[str]:
        """
        顺序处理任务

        使用第一个Agent按顺序处理多个任务
        """
        if not self.agents:
            raise ValueError("没有可用的Agent")

        agent = list(self.agents.values())[0]

        print(f"\n📋 顺序处理 {len(tasks)} 个任务")
        print(f"👤 使用Agent: {agent.name}\n")

        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n   [{i}/{len(tasks)}] {task}")
            try:
                result = await agent.process(task)
                results.append(result)
            except Exception as e:
                results.append(f"❌ 失败: {e}")

        return results


# ============================================================================
# 示例应用
# ============================================================================

async def example_1_basic_agent():
    """示例1: 基础Agent使用"""
    print("\n" + "="*60)
    print("示例1: 基础Agent使用")
    print("="*60)

    async with agent_session("基础Agent示例"):
        # 创建LLM提供者
        provider = MockLLMProvider("gpt-4", error_rate=0.1)

        # 创建Agent
        agent = Agent(
            name="智能助手",
            provider=provider,
            system_prompt="你是一个有用的AI助手"
        )

        # 处理任务
        questions = [
            "什么是Python?",
            "什么是异步编程?",
            "什么是装饰器?"
        ]

        async with llm_connection(provider.get_model_name()):
            for question in questions:
                try:
                    response = await agent.process(question)
                    print(f"\n💬 问: {question}")
                    print(f"🤖 答: {response[:100]}...")
                except Exception as e:
                    print(f"\n💬 问: {question}")
                    print(f"❌ 失败: {e}")


async def example_2_multi_agent():
    """示例2: 多Agent并行处理"""
    print("\n" + "="*60)
    print("示例2: 多Agent并行处理")
    print("="*60)

    async with agent_session("多Agent示例"):
        # 创建系统
        system = MultiAgentSystem()

        # 添加多个Agent
        agents_config = [
            ("研究员", "gpt-4", "你是一个研究专家"),
            ("分析师", "claude-3", "你是一个数据分析专家"),
            ("作家", "gemini-pro", "你是一个技术作家")
        ]

        for name, model, prompt in agents_config:
            provider = MockLLMProvider(model, error_rate=0.15)
            agent = Agent(name, provider, prompt)
            system.add_agent(agent)

        # 并行处理
        task = "分析AI Agent的发展趋势"
        results = await system.parallel_process(task)

        print(f"\n📊 结果汇总:")
        print("-" * 60)
        for name, result in results.items():
            print(f"\n{name}:")
            print(f"  {result[:80]}...")


async def example_3_error_handling():
    """示例3: 错误处理和重试"""
    print("\n" + "="*60)
    print("示例3: 错误处理和重试")
    print("="*60)

    async with agent_session("错误处理示例"):
        # 创建高错误率的提供者
        provider = MockLLMProvider("gpt-4", error_rate=0.5)
        agent = Agent("测试Agent", provider)

        tasks = [
            "任务1: 测试重试机制",
            "任务2: 测试错误恢复",
            "任务3: 测试优雅失败"
        ]

        for task in tasks:
            try:
                result = await agent.process(task)
                print(f"\n✅ {task}")
                print(f"   结果: {result[:60]}...")
            except Exception as e:
                print(f"\n❌ {task}")
                print(f"   错误: {e}")


async def example_4_caching():
    """示例4: 缓存机制"""
    print("\n" + "="*60)
    print("示例4: 缓存机制")
    print("="*60)

    async with agent_session("缓存示例"):
        provider = MockLLMProvider("gpt-4", error_rate=0.0)
        agent = Agent("缓存测试Agent", provider)

        query = "什么是机器学习?"

        # 第一次查询（未缓存）
        print(f"\n第1次查询: {query}")
        await agent.process(query)

        # 第二次查询（使用缓存）
        print(f"\n第2次查询: {query}")
        await agent.process(query)

        # 第三次查询（使用缓存）
        print(f"\n第3次查询: {query}")
        await agent.process(query)


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """运行所有示例"""

    print("\n" + "="*60)
    print("🎯 综合示例：AI Agent系统")
    print("="*60)
    print("\n这个系统展示了以下Python技术的综合应用:")
    print("  ✅ 异步编程 - 并发处理")
    print("  ✅ 装饰器 - 监控、重试、缓存")
    print("  ✅ 类型注解 - 类型安全")
    print("  ✅ 错误处理 - 优雅失败")
    print("  ✅ 上下文管理器 - 资源管理")

    # 运行示例
    await example_1_basic_agent()
    await example_2_multi_agent()
    await example_3_error_handling()
    await example_4_caching()

    print("\n" + "="*60)
    print("🎉 所有示例完成！")
    print("="*60)
    print("\n💡 关键要点:")
    print("  1. 异步使I/O操作高效并发")
    print("  2. 装饰器使代码模块化和可维护")
    print("  3. 类型注解提高代码质量")
    print("  4. 错误处理确保系统健壮")
    print("  5. 上下文管理器确保资源清理")
    print("\n🚀 这些技术是构建生产级AI系统的基础！\n")


if __name__ == "__main__":
    asyncio.run(main())
