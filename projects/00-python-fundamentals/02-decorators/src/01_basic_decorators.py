"""
装饰器基础
==========

本模块介绍Python装饰器的基础概念：
- 函数装饰器
- 带参数的装饰器
- 多个装饰器的叠加
- 装饰器的实际应用

装饰器是Python中最强大的特性之一，在AI开发中用于：
- 日志记录
- 性能监控
- 缓存
- 重试
- 权限检查
"""

import time
import functools
from typing import Callable, Any


# ============================================================================
# 1. 函数基础：函数是一等公民
# ============================================================================

def understand_functions():
    """
    理解Python中函数是一等公民

    函数可以：
    - 赋值给变量
    - 作为参数传递
    - 作为返回值返回
    - 存储在数据结构中
    """
    print("\n【基础】函数是一等公民")
    print("=" * 60)

    def greet(name: str) -> str:
        return f"Hello, {name}!"

    # 1. 函数可以赋值给变量
    say_hello = greet
    print(f"1. {say_hello('Alice')}")

    # 2. 函数可以作为参数
    def execute_function(func: Callable, arg: str) -> str:
        return func(arg)

    result = execute_function(greet, "Bob")
    print(f"2. {result}")

    # 3. 函数可以返回函数
    def create_greeter(prefix: str) -> Callable:
        def greeter(name: str) -> str:
            return f"{prefix}, {name}!"
        return greeter

    formal_greet = create_greeter("Good morning")
    print(f"3. {formal_greet('Charlie')}")


# ============================================================================
# 2. 最简单的装饰器
# ============================================================================

def simple_decorator(func: Callable) -> Callable:
    """
    最简单的装饰器

    装饰器本质是一个函数，它接收一个函数作为参数，
    返回一个新的函数
    """
    def wrapper(*args, **kwargs):
        print(f"  [装饰器] 函数 {func.__name__} 开始执行")
        result = func(*args, **kwargs)
        print(f"  [装饰器] 函数 {func.__name__} 执行完成")
        return result

    return wrapper


@simple_decorator
def say_hello(name: str) -> str:
    """简单的问候函数"""
    return f"Hello, {name}!"


def simple_decorator_example():
    """简单装饰器示例"""
    print("\n【示例1】简单装饰器")
    print("=" * 60)

    # 使用装饰器的函数
    result = say_hello("Alice")
    print(f"  返回值: {result}\n")

    # 等价写法：
    print("  等价于:")
    print("  say_hello = simple_decorator(say_hello)")


# ============================================================================
# 3. 计时装饰器
# ============================================================================

def timer(func: Callable) -> Callable:
    """
    计时装饰器

    记录函数执行时间
    在AI开发中用于性能分析
    """
    @functools.wraps(func)  # 保留原函数的元信息
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  ⏱ {func.__name__} 耗时: {elapsed:.4f}秒")
        return result

    return wrapper


@timer
def slow_function(n: int) -> int:
    """一个慢速函数"""
    time.sleep(n)
    return n * n


def timer_example():
    """计时装饰器示例"""
    print("\n【示例2】计时装饰器")
    print("=" * 60)

    result = slow_function(1)
    print(f"  结果: {result}")


# ============================================================================
# 4. 日志装饰器
# ============================================================================

def log(func: Callable) -> Callable:
    """
    日志装饰器

    记录函数的调用信息
    在AI开发中用于调试和监控
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 记录输入
        args_str = ', '.join(repr(arg) for arg in args)
        kwargs_str = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))

        print(f"  📝 调用 {func.__name__}({all_args})")

        # 执行函数
        result = func(*args, **kwargs)

        # 记录输出
        print(f"  📝 {func.__name__} 返回: {result!r}")

        return result

    return wrapper


@log
def add(a: int, b: int) -> int:
    """加法函数"""
    return a + b


@log
def greet(name: str, greeting: str = "Hello") -> str:
    """问候函数"""
    return f"{greeting}, {name}!"


def log_example():
    """日志装饰器示例"""
    print("\n【示例3】日志装饰器")
    print("=" * 60)

    add(3, 5)
    greet("Bob", greeting="Hi")


# ============================================================================
# 5. 带参数的装饰器
# ============================================================================

def repeat(times: int):
    """
    带参数的装饰器

    重复执行函数多次
    需要两层嵌套函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                print(f"  第 {i + 1} 次执行:")
                result = func(*args, **kwargs)
                results.append(result)
            return results

        return wrapper

    return decorator


@repeat(times=3)
def say_hi(name: str) -> str:
    """多次问候"""
    return f"Hi, {name}!"


def parameterized_decorator_example():
    """带参数的装饰器示例"""
    print("\n【示例4】带参数的装饰器")
    print("=" * 60)

    results = say_hi("Alice")
    print(f"  返回值: {results}")


# ============================================================================
# 6. 缓存装饰器
# ============================================================================

def cache(func: Callable) -> Callable:
    """
    缓存装饰器

    缓存函数的返回值，避免重复计算
    在AI开发中用于缓存LLM响应
    """
    cached_results = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 创建缓存键
        key = (args, tuple(sorted(kwargs.items())))

        if key in cached_results:
            print(f"  💾 从缓存获取 {func.__name__}{args}")
            return cached_results[key]

        # 计算结果
        print(f"  🔄 计算 {func.__name__}{args}")
        result = func(*args, **kwargs)

        # 存入缓存
        cached_results[key] = result
        return result

    return wrapper


@cache
def fibonacci(n: int) -> int:
    """斐波那契数列（递归实现）"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@cache
@timer
def expensive_computation(x: int) -> int:
    """模拟昂贵的计算"""
    time.sleep(1)
    return x * x


def cache_example():
    """缓存装饰器示例"""
    print("\n【示例5】缓存装饰器")
    print("=" * 60)

    print("\n1. 计算斐波那契数:")
    result = fibonacci(10)
    print(f"  结果: {result}")

    print("\n2. 测试缓存效果:")
    print("  首次计算:")
    expensive_computation(5)

    print("\n  第二次计算（使用缓存）:")
    expensive_computation(5)


# ============================================================================
# 7. 多个装饰器叠加
# ============================================================================

@log
@timer
def complex_function(n: int) -> int:
    """应用多个装饰器"""
    time.sleep(0.5)
    return n * 2


def multiple_decorators_example():
    """多个装饰器示例"""
    print("\n【示例6】多个装饰器叠加")
    print("=" * 60)

    print("\n装饰器从下到上应用:")
    print("  complex_function = log(timer(complex_function))")

    result = complex_function(10)
    print(f"\n  最终结果: {result}")


# ============================================================================
# 8. 保留函数元信息
# ============================================================================

def bad_decorator(func: Callable) -> Callable:
    """不使用 functools.wraps 的装饰器"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def good_decorator(func: Callable) -> Callable:
    """使用 functools.wraps 的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@bad_decorator
def func_with_bad_decorator():
    """这个函数的文档字符串会丢失"""
    pass


@good_decorator
def func_with_good_decorator():
    """这个函数的文档字符串会保留"""
    pass


def functools_wraps_example():
    """functools.wraps 的重要性"""
    print("\n【示例7】保留函数元信息")
    print("=" * 60)

    print("\n不使用 @functools.wraps:")
    print(f"  函数名: {func_with_bad_decorator.__name__}")
    print(f"  文档: {func_with_bad_decorator.__doc__}")

    print("\n使用 @functools.wraps:")
    print(f"  函数名: {func_with_good_decorator.__name__}")
    print(f"  文档: {func_with_good_decorator.__doc__}")


# ============================================================================
# 9. AI应用：LLM调用装饰器
# ============================================================================

def llm_call_decorator(func: Callable) -> Callable:
    """
    LLM调用装饰器

    记录LLM调用的详细信息：
    - 调用时间
    - 执行时长
    - Token使用
    - 成功/失败状态
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from datetime import datetime

        # 记录开始
        start_time = datetime.now()
        print(f"\n  🤖 [{start_time.strftime('%H:%M:%S')}] "
              f"LLM调用开始: {func.__name__}")

        try:
            # 执行函数
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            # 记录成功
            print(f"  ✓ LLM调用成功")
            print(f"  ⏱ 耗时: {elapsed:.2f}秒")

            # 如果返回值包含token信息，记录它
            if isinstance(result, dict) and 'tokens' in result:
                print(f"  📊 Token使用: {result['tokens']}")

            return result

        except Exception as e:
            # 记录失败
            print(f"  ✗ LLM调用失败: {e}")
            raise

    return wrapper


@llm_call_decorator
def call_llm(prompt: str) -> dict:
    """模拟LLM调用"""
    time.sleep(1.5)  # 模拟API延迟
    return {
        "response": "这是LLM的响应",
        "tokens": 150
    }


def ai_decorator_example():
    """AI应用装饰器示例"""
    print("\n【示例8】AI应用：LLM调用装饰器")
    print("=" * 60)

    result = call_llm("什么是人工智能?")
    print(f"\n  返回结果: {result['response']}")


# ============================================================================
# 10. 实用装饰器模板
# ============================================================================

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    重试装饰器

    自动重试失败的函数
    在AI开发中用于处理API调用失败
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"  ⚠ 第 {attempt + 1} 次尝试失败: {e}")
                        print(f"  等待 {delay}秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"  ✗ 达到最大重试次数")
                        raise

        return wrapper

    return decorator


@retry(max_attempts=3, delay=0.5)
def unstable_api_call():
    """不稳定的API调用"""
    import random
    if random.random() < 0.7:  # 70%失败率
        raise Exception("API调用失败")
    return "成功"


def retry_example():
    """重试装饰器示例"""
    print("\n【示例9】重试装饰器")
    print("=" * 60)

    try:
        result = unstable_api_call()
        print(f"  ✓ 最终结果: {result}")
    except Exception as e:
        print(f"  ✗ 最终失败: {e}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("Python 装饰器基础教程")
    print("=" * 60)

    # 基础概念
    understand_functions()

    # 各种装饰器示例
    simple_decorator_example()
    timer_example()
    log_example()
    parameterized_decorator_example()
    cache_example()
    multiple_decorators_example()
    functools_wraps_example()

    # AI应用
    ai_decorator_example()
    retry_example()

    print("\n" + "=" * 60)
    print("装饰器基础总结")
    print("=" * 60)
    print("1. 装饰器是一个返回函数的函数")
    print("2. 使用 @decorator 语法应用装饰器")
    print("3. 使用 @functools.wraps 保留函数元信息")
    print("4. 装饰器可以带参数（需要额外一层嵌套）")
    print("5. 多个装饰器从下到上应用")
    print("6. 常用场景：日志、计时、缓存、重试")
    print("7. 在AI开发中用于监控和优化LLM调用")


if __name__ == "__main__":
    main()
