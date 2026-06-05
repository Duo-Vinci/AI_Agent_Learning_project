"""
类装饰器与高级装饰器
==================

本模块介绍装饰器的高级用法：
- 类装饰器
- 装饰器类（使用类实现装饰器）
- 装饰器工厂
- 异步装饰器
- 实用装饰器库

这些是构建生产级AI系统的关键技术。
"""

import time
import asyncio
import functools
from typing import Callable, Any, Optional
from datetime import datetime
import json


# ============================================================================
# 1. 类装饰器（装饰类）
# ============================================================================

def singleton(cls):
    """
    单例装饰器

    确保类只有一个实例
    在AI开发中用于：
    - LLM客户端（避免创建多个连接）
    - 配置管理器
    - 缓存管理器
    """
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class LLMClient:
    """LLM客户端（单例）"""

    def __init__(self, api_key: str):
        print(f"  初始化 LLMClient (api_key: {api_key[:8]}...)")
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        return f"响应: {prompt}"


def singleton_example():
    """单例装饰器示例"""
    print("\n【示例1】单例装饰器")
    print("=" * 60)

    print("\n创建第一个实例:")
    client1 = LLMClient("sk-1234567890")

    print("\n创建第二个实例（实际返回同一个）:")
    client2 = LLMClient("sk-9999999999")

    print(f"\nclient1 is client2: {client1 is client2}")
    print(f"ID相同: {id(client1) == id(client2)}")


def add_methods(cls):
    """
    为类添加方法的装饰器

    动态增强类的功能
    """
    def to_dict(self):
        """将对象转为字典"""
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith('_')}

    def from_dict(cls, data: dict):
        """从字典创建对象"""
        return cls(**data)

    cls.to_dict = to_dict
    cls.from_dict = classmethod(from_dict)

    return cls


@add_methods
class Agent:
    """AI Agent"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role


def add_methods_example():
    """动态添加方法示例"""
    print("\n【示例2】动态添加方法")
    print("=" * 60)

    agent = Agent("研究员", "信息收集")

    print(f"\n转为字典: {agent.to_dict()}")

    # 从字典创建
    data = {"name": "分析师", "role": "数据分析"}
    agent2 = Agent.from_dict(data)
    print(f"从字典创建: {agent2.to_dict()}")


# ============================================================================
# 2. 装饰器类（使用类实现装饰器）
# ============================================================================

class CountCalls:
    """
    计数装饰器（使用类实现）

    统计函数被调用的次数
    在AI开发中用于监控API调用频率
    """

    def __init__(self, func: Callable):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        """使对象可调用"""
        self.count += 1
        print(f"  调用次数: {self.count}")
        return self.func(*args, **kwargs)


@CountCalls
def process_data(data: str) -> str:
    """处理数据"""
    return f"处理: {data}"


def class_decorator_example():
    """装饰器类示例"""
    print("\n【示例3】装饰器类")
    print("=" * 60)

    process_data("数据1")
    process_data("数据2")
    process_data("数据3")

    print(f"\n总调用次数: {process_data.count}")


class RateLimiter:
    """
    限流装饰器类

    限制函数调用频率
    在AI开发中用于控制API调用速率
    """

    def __init__(self, max_calls: int, time_window: float):
        """
        Args:
            max_calls: 时间窗口内最大调用次数
            time_window: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # 清理过期的调用记录
            self.calls = [t for t in self.calls
                         if now - t < self.time_window]

            # 检查是否超过限制
            if len(self.calls) >= self.max_calls:
                wait_time = self.time_window - (now - self.calls[0])
                print(f"  ⚠ 达到速率限制，等待 {wait_time:.2f}秒...")
                time.sleep(wait_time)
                self.calls = []

            # 记录本次调用
            self.calls.append(time.time())

            return func(*args, **kwargs)

        return wrapper


@RateLimiter(max_calls=3, time_window=2.0)
def call_api(endpoint: str) -> str:
    """模拟API调用"""
    print(f"  → 调用API: {endpoint}")
    return f"响应: {endpoint}"


def rate_limiter_example():
    """限流装饰器示例"""
    print("\n【示例4】限流装饰器")
    print("=" * 60)
    print("限制: 2秒内最多3次调用\n")

    for i in range(5):
        call_api(f"/api/endpoint_{i + 1}")


# ============================================================================
# 3. 带状态的装饰器
# ============================================================================

class Cache:
    """
    缓存装饰器类（带过期时间）

    在AI开发中用于缓存LLM响应
    """

    def __init__(self, ttl: float = 60.0):
        """
        Args:
            ttl: 缓存过期时间（秒）
        """
        self.ttl = ttl
        self.cache = {}

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存键
            key = (args, tuple(sorted(kwargs.items())))

            # 检查缓存
            if key in self.cache:
                result, timestamp = self.cache[key]
                age = time.time() - timestamp

                if age < self.ttl:
                    print(f"  💾 缓存命中 (年龄: {age:.1f}秒)")
                    return result
                else:
                    print(f"  ⏰ 缓存过期 (年龄: {age:.1f}秒)")
                    del self.cache[key]

            # 执行函数
            print(f"  🔄 执行函数")
            result = func(*args, **kwargs)

            # 存入缓存
            self.cache[key] = (result, time.time())

            return result

        # 添加清理缓存的方法
        wrapper.clear_cache = lambda: self.cache.clear()
        wrapper.cache_size = lambda: len(self.cache)

        return wrapper


@Cache(ttl=3.0)
def expensive_llm_call(prompt: str) -> str:
    """模拟昂贵的LLM调用"""
    time.sleep(1)
    return f"LLM响应: {prompt}"


def stateful_decorator_example():
    """带状态的装饰器示例"""
    print("\n【示例5】带状态的装饰器（缓存）")
    print("=" * 60)
    print("TTL: 3秒\n")

    # 第一次调用
    print("第1次调用:")
    expensive_llm_call("什么是AI?")

    # 第二次调用（使用缓存）
    print("\n第2次调用（立即）:")
    expensive_llm_call("什么是AI?")

    # 等待缓存过期
    print("\n等待4秒...")
    time.sleep(4)

    # 第三次调用（缓存已过期）
    print("\n第3次调用（缓存过期）:")
    expensive_llm_call("什么是AI?")

    print(f"\n缓存大小: {expensive_llm_call.cache_size()}")


# ============================================================================
# 4. 异步装饰器
# ============================================================================

def async_timer(func: Callable) -> Callable:
    """
    异步函数的计时装饰器

    用于测量异步函数的执行时间
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  ⏱ {func.__name__} 耗时: {elapsed:.4f}秒")
        return result

    return wrapper


def async_retry(max_attempts: int = 3, delay: float = 1.0):
    """
    异步重试装饰器

    自动重试失败的异步函数
    在AI开发中用于处理异步API调用失败
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"  ⚠ 第 {attempt + 1} 次尝试失败: {e}")
                        print(f"  等待 {delay}秒后重试...")
                        await asyncio.sleep(delay)
                    else:
                        print(f"  ✗ 达到最大重试次数")
                        raise

        return wrapper

    return decorator


@async_timer
@async_retry(max_attempts=3, delay=0.5)
async def async_llm_call(prompt: str) -> str:
    """异步LLM调用"""
    await asyncio.sleep(1)

    # 模拟随机失败
    import random
    if random.random() < 0.3:
        raise Exception("API调用失败")

    return f"响应: {prompt}"


async def async_decorator_example():
    """异步装饰器示例"""
    print("\n【示例6】异步装饰器")
    print("=" * 60)

    try:
        result = await async_llm_call("什么是异步编程?")
        print(f"  ✓ 结果: {result}")
    except Exception as e:
        print(f"  ✗ 失败: {e}")


# ============================================================================
# 5. 装饰器工厂
# ============================================================================

def monitor(
    log_input: bool = True,
    log_output: bool = True,
    log_time: bool = True,
    log_errors: bool = True
):
    """
    监控装饰器工厂

    灵活配置监控选项
    在AI开发中用于全面监控LLM调用
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__

            # 记录输入
            if log_input:
                args_str = ', '.join(repr(arg) for arg in args)
                print(f"  📥 输入 {func_name}({args_str})")

            # 记录时间
            start = time.time() if log_time else None

            try:
                # 执行函数
                result = func(*args, **kwargs)

                # 记录时间
                if log_time:
                    elapsed = time.time() - start
                    print(f"  ⏱ 耗时: {elapsed:.4f}秒")

                # 记录输出
                if log_output:
                    print(f"  📤 输出: {result!r}")

                return result

            except Exception as e:
                # 记录错误
                if log_errors:
                    print(f"  ❌ 错误: {e}")
                raise

        return wrapper

    return decorator


@monitor(log_input=True, log_output=True, log_time=True)
def process_query(query: str) -> str:
    """处理查询"""
    time.sleep(0.5)
    return f"处理结果: {query}"


def decorator_factory_example():
    """装饰器工厂示例"""
    print("\n【示例7】装饰器工厂")
    print("=" * 60)

    process_query("用户查询1")


# ============================================================================
# 6. AI应用：完整的LLM调用监控
# ============================================================================

class LLMMonitor:
    """
    LLM调用监控装饰器

    完整监控LLM调用的所有方面：
    - 请求/响应
    - 执行时间
    - Token使用
    - 错误处理
    - 统计信息
    """

    def __init__(self):
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_time': 0.0,
            'total_tokens': 0
        }

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.stats['total_calls'] += 1

            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n  🤖 [{timestamp}] LLM调用开始")
            print(f"  函数: {func.__name__}")

            if args:
                print(f"  提示词: {args[0][:50]}...")

            start = time.time()

            try:
                result = func(*args, **kwargs)

                elapsed = time.time() - start
                self.stats['successful_calls'] += 1
                self.stats['total_time'] += elapsed

                print(f"  ✓ 调用成功")
                print(f"  ⏱ 耗时: {elapsed:.2f}秒")

                # 提取token信息
                if isinstance(result, dict) and 'tokens' in result:
                    tokens = result['tokens']
                    self.stats['total_tokens'] += tokens
                    print(f"  📊 Token使用: {tokens}")

                return result

            except Exception as e:
                elapsed = time.time() - start
                self.stats['failed_calls'] += 1
                self.stats['total_time'] += elapsed

                print(f"  ✗ 调用失败: {e}")
                print(f"  ⏱ 耗时: {elapsed:.2f}秒")
                raise

        return wrapper

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_time': 0.0,
            'total_tokens': 0
        }


# 创建全局监控器
llm_monitor = LLMMonitor()


@llm_monitor
def call_gpt(prompt: str) -> dict:
    """模拟GPT调用"""
    time.sleep(1.2)
    return {
        "response": f"响应: {prompt}",
        "tokens": 150
    }


@llm_monitor
def call_claude(prompt: str) -> dict:
    """模拟Claude调用"""
    time.sleep(0.8)
    return {
        "response": f"响应: {prompt}",
        "tokens": 120
    }


def ai_monitoring_example():
    """AI监控示例"""
    print("\n【示例8】AI应用：LLM调用监控")
    print("=" * 60)

    # 执行多次调用
    call_gpt("什么是机器学习?")
    call_claude("什么是深度学习?")
    call_gpt("什么是强化学习?")

    # 显示统计
    stats = llm_monitor.get_stats()
    print("\n" + "=" * 60)
    print("📊 统计信息")
    print("=" * 60)
    print(f"总调用次数: {stats['total_calls']}")
    print(f"成功: {stats['successful_calls']}")
    print(f"失败: {stats['failed_calls']}")
    print(f"总耗时: {stats['total_time']:.2f}秒")
    print(f"平均耗时: {stats['total_time'] / stats['total_calls']:.2f}秒")
    print(f"总Token: {stats['total_tokens']}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("Python 类装饰器与高级装饰器")
    print("=" * 60)

    # 类装饰器
    singleton_example()
    add_methods_example()

    # 装饰器类
    class_decorator_example()
    rate_limiter_example()
    stateful_decorator_example()

    # 异步装饰器
    asyncio.run(async_decorator_example())

    # 装饰器工厂
    decorator_factory_example()

    # AI应用
    ai_monitoring_example()

    print("\n" + "=" * 60)
    print("高级装饰器总结")
    print("=" * 60)
    print("1. 类装饰器 - 装饰整个类（如单例模式）")
    print("2. 装饰器类 - 使用类实现装饰器（带状态）")
    print("3. 异步装饰器 - 装饰异步函数")
    print("4. 装饰器工厂 - 灵活配置装饰器参数")
    print("5. 限流器 - 控制API调用频率")
    print("6. 监控器 - 全面监控LLM调用")
    print("7. 在生产环境中，这些是必备工具")


if __name__ == "__main__":
    main()
