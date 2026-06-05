"""
错误处理基础
===========

本模块介绍Python错误处理的基础：
- 异常的基本概念
- try-except 语句
- 多个异常处理
- else 和 finally 子句
- 自定义异常
- 异常链

在AI开发中，良好的错误处理至关重要：
- LLM API调用可能失败
- 网络请求可能超时
- 数据格式可能错误
- 资源可能不足
"""

import time
from typing import Optional, Dict, Any


# ============================================================================
# 1. 基本异常处理
# ============================================================================

def basic_exception_example():
    """基本异常处理示例"""
    print("\n【示例1】基本异常处理")
    print("=" * 60)

    # 除零错误
    print("\n1. 除零错误:")
    try:
        result = 10 / 0
        print(f"结果: {result}")
    except ZeroDivisionError:
        print("  ✗ 错误: 不能除以零")

    # 类型错误
    print("\n2. 类型错误:")
    try:
        result = "hello" + 5
        print(f"结果: {result}")
    except TypeError as e:
        print(f"  ✗ 错误: {e}")

    # 索引错误
    print("\n3. 索引错误:")
    try:
        numbers = [1, 2, 3]
        value = numbers[10]
        print(f"值: {value}")
    except IndexError:
        print("  ✗ 错误: 索引超出范围")


def safe_divide(a: float, b: float) -> Optional[float]:
    """
    安全的除法

    捕获异常并返回 None
    """
    try:
        return a / b
    except ZeroDivisionError:
        print(f"  ⚠ 警告: 除数为零")
        return None


def safe_division_example():
    """安全除法示例"""
    print("\n【示例2】安全除法")
    print("=" * 60)

    print(f"\nsafe_divide(10, 2) = {safe_divide(10, 2)}")
    print(f"safe_divide(10, 0) = {safe_divide(10, 0)}")


# ============================================================================
# 2. 捕获多个异常
# ============================================================================

def parse_number(value: str) -> Optional[float]:
    """
    解析数字

    处理多种可能的异常
    """
    try:
        return float(value)
    except ValueError:
        print(f"  ✗ '{value}' 不是有效的数字")
        return None
    except TypeError:
        print(f"  ✗ 类型错误: {value}")
        return None


def process_data(data: Dict[str, Any]) -> bool:
    """
    处理数据

    使用元组捕获多个异常
    """
    try:
        name = data["name"]
        age = int(data["age"])
        print(f"  处理用户: {name}, {age}岁")
        return True
    except (KeyError, ValueError, TypeError) as e:
        print(f"  ✗ 数据处理失败: {e}")
        return False


def multiple_exceptions_example():
    """多个异常处理示例"""
    print("\n【示例3】捕获多个异常")
    print("=" * 60)

    # 解析数字
    print("\n1. 解析数字:")
    parse_number("42")
    parse_number("3.14")
    parse_number("invalid")

    # 处理数据
    print("\n2. 处理数据:")
    process_data({"name": "Alice", "age": "25"})
    process_data({"name": "Bob"})  # 缺少 age
    process_data({"name": "Charlie", "age": "invalid"})


# ============================================================================
# 3. else 和 finally 子句
# ============================================================================

def read_file_safe(filename: str) -> Optional[str]:
    """
    安全读取文件

    演示 else 和 finally 的使用
    """
    file = None
    try:
        print(f"  尝试打开文件: {filename}")
        file = open(filename, 'r', encoding='utf-8')
        content = file.read()
        print(f"  ✓ 文件读取成功")
        return content

    except FileNotFoundError:
        print(f"  ✗ 文件不存在: {filename}")
        return None

    except PermissionError:
        print(f"  ✗ 没有权限读取: {filename}")
        return None

    else:
        # 没有异常时执行
        print(f"  文件大小: {len(content)} 字符")

    finally:
        # 无论是否异常都执行
        if file:
            file.close()
            print(f"  文件已关闭")


def else_finally_example():
    """else 和 finally 示例"""
    print("\n【示例4】else 和 finally 子句")
    print("=" * 60)

    print("\n1. 读取存在的文件:")
    # 创建临时文件
    with open("temp_test.txt", "w", encoding='utf-8') as f:
        f.write("测试内容")

    read_file_safe("temp_test.txt")

    print("\n2. 读取不存在的文件:")
    read_file_safe("nonexistent.txt")

    # 清理
    import os
    try:
        os.remove("temp_test.txt")
    except:
        pass


# ============================================================================
# 4. 自定义异常
# ============================================================================

class LLMError(Exception):
    """LLM错误基类"""
    pass


class LLMAPIError(LLMError):
    """LLM API错误"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"LLM API错误 [{self.status_code}]: {self.message}"
        return f"LLM API错误: {self.message}"


class LLMTimeoutError(LLMError):
    """LLM超时错误"""

    def __init__(self, timeout: float):
        self.timeout = timeout
        super().__init__(f"LLM调用超时 ({timeout}秒)")


class LLMRateLimitError(LLMError):
    """LLM速率限制错误"""

    def __init__(self, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        message = "达到速率限制"
        if retry_after:
            message += f"，请在 {retry_after}秒 后重试"
        super().__init__(message)


class TokenLimitError(LLMError):
    """Token限制错误"""

    def __init__(self, used: int, limit: int):
        self.used = used
        self.limit = limit
        super().__init__(f"超出Token限制: 使用了 {used}/{limit}")


def call_llm_api(prompt: str, simulate_error: Optional[str] = None) -> str:
    """
    模拟LLM API调用

    可以模拟各种错误
    """
    if simulate_error == "timeout":
        raise LLMTimeoutError(timeout=30.0)

    if simulate_error == "rate_limit":
        raise LLMRateLimitError(retry_after=60.0)

    if simulate_error == "api_error":
        raise LLMAPIError("服务器错误", status_code=500)

    if simulate_error == "token_limit":
        raise TokenLimitError(used=5000, limit=4096)

    return f"响应: {prompt}"


def custom_exceptions_example():
    """自定义异常示例"""
    print("\n【示例5】自定义异常")
    print("=" * 60)

    errors = [
        ("正常调用", None),
        ("超时错误", "timeout"),
        ("速率限制", "rate_limit"),
        ("API错误", "api_error"),
        ("Token限制", "token_limit")
    ]

    for name, error_type in errors:
        print(f"\n{name}:")
        try:
            result = call_llm_api("测试提示", simulate_error=error_type)
            print(f"  ✓ {result}")
        except LLMTimeoutError as e:
            print(f"  ✗ {e} (超时: {e.timeout}秒)")
        except LLMRateLimitError as e:
            print(f"  ✗ {e}")
            if e.retry_after:
                print(f"    等待时间: {e.retry_after}秒")
        except LLMAPIError as e:
            print(f"  ✗ {e}")
        except TokenLimitError as e:
            print(f"  ✗ {e}")
            print(f"    使用: {e.used}, 限制: {e.limit}")
        except LLMError as e:
            print(f"  ✗ LLM错误: {e}")


# ============================================================================
# 5. 异常链（Exception Chaining）
# ============================================================================

class DataProcessingError(Exception):
    """数据处理错误"""
    pass


def parse_json_data(data_str: str) -> dict:
    """解析JSON数据"""
    import json

    try:
        return json.loads(data_str)
    except json.JSONDecodeError as e:
        # 使用 from 关键字链接原始异常
        raise DataProcessingError(
            f"JSON解析失败: {e.msg}"
        ) from e


def process_api_response(response_text: str) -> dict:
    """
    处理API响应

    演示异常链
    """
    try:
        data = parse_json_data(response_text)
        return data
    except DataProcessingError:
        # 原始异常信息会被保留
        print(f"  ✗ 处理API响应失败")
        raise


def exception_chaining_example():
    """异常链示例"""
    print("\n【示例6】异常链")
    print("=" * 60)

    print("\n1. 有效的JSON:")
    try:
        result = process_api_response('{"status": "ok"}')
        print(f"  ✓ 结果: {result}")
    except DataProcessingError as e:
        print(f"  ✗ 错误: {e}")
        if e.__cause__:
            print(f"  原因: {e.__cause__}")

    print("\n2. 无效的JSON:")
    try:
        result = process_api_response('invalid json')
        print(f"  结果: {result}")
    except DataProcessingError as e:
        print(f"  ✗ 错误: {e}")
        if e.__cause__:
            print(f"  原因: {type(e.__cause__).__name__}")


# ============================================================================
# 6. 异常的最佳实践
# ============================================================================

def bad_exception_handling():
    """不好的异常处理示例"""
    print("\n【反面教材】不好的异常处理")
    print("-" * 60)

    # 1. 捕获所有异常（不推荐）
    print("\n1. 捕获所有异常:")
    try:
        result = 10 / 0
    except:  # 不推荐：捕获所有异常
        print("  ✗ 发生了某个错误")

    # 2. 空的异常处理（不推荐）
    print("\n2. 空的异常处理:")
    try:
        result = int("invalid")
    except ValueError:
        pass  # 不推荐：忽略异常

    print("  程序继续运行...")

    # 3. 过于宽泛的异常（不推荐）
    print("\n3. 过于宽泛的异常:")
    try:
        data = {"key": "value"}
        value = data["missing_key"]
    except Exception as e:  # 不推荐：太宽泛
        print(f"  ✗ 错误: {e}")


def good_exception_handling():
    """好的异常处理示例"""
    print("\n【正面示例】好的异常处理")
    print("-" * 60)

    # 1. 捕获具体的异常
    print("\n1. 捕获具体的异常:")
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        print(f"  ✗ 除零错误: {e}")

    # 2. 记录异常信息
    print("\n2. 记录异常信息:")
    try:
        result = int("invalid")
    except ValueError as e:
        print(f"  ✗ 类型转换失败: {e}")
        print(f"  输入值: 'invalid'")

    # 3. 提供有用的错误消息
    print("\n3. 提供有用的错误消息:")
    try:
        data = {"key": "value"}
        value = data["missing_key"]
    except KeyError as e:
        print(f"  ✗ 键不存在: {e}")
        print(f"  可用的键: {list(data.keys())}")


def best_practices_example():
    """异常处理最佳实践"""
    print("\n【示例7】异常处理最佳实践")
    print("=" * 60)

    bad_exception_handling()
    good_exception_handling()


# ============================================================================
# 7. AI应用：完整的错误处理策略
# ============================================================================

class AgentError(Exception):
    """Agent错误基类"""
    pass


class AgentExecutionError(AgentError):
    """Agent执行错误"""
    pass


class Agent:
    """
    带完整错误处理的Agent

    演示AI应用中的错误处理最佳实践
    """

    def __init__(self, name: str, max_retries: int = 3):
        self.name = name
        self.max_retries = max_retries

    def execute(self, task: str) -> str:
        """
        执行任务（带重试）

        实现了完整的错误处理策略：
        1. 捕获具体的异常
        2. 重试机制
        3. 详细的日志
        4. 优雅的失败
        """
        print(f"\n  [{self.name}] 执行任务: {task}")

        for attempt in range(self.max_retries):
            try:
                # 模拟可能失败的操作
                result = self._call_llm(task)
                print(f"  ✓ 任务完成")
                return result

            except LLMTimeoutError as e:
                print(f"  ⚠ 第 {attempt + 1} 次尝试超时")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"  等待 {wait_time}秒 后重试...")
                    time.sleep(wait_time)
                else:
                    raise AgentExecutionError(
                        f"任务失败: 超过最大重试次数"
                    ) from e

            except LLMRateLimitError as e:
                print(f"  ⚠ 达到速率限制")
                if e.retry_after and attempt < self.max_retries - 1:
                    print(f"  等待 {e.retry_after}秒...")
                    time.sleep(min(e.retry_after, 5))  # 最多等待5秒
                else:
                    raise AgentExecutionError(
                        f"任务失败: 速率限制"
                    ) from e

            except LLMAPIError as e:
                # API错误通常不需要重试
                print(f"  ✗ API错误: {e}")
                raise AgentExecutionError(
                    f"任务失败: API错误"
                ) from e

            except Exception as e:
                # 未预期的错误
                print(f"  ✗ 未预期的错误: {type(e).__name__}: {e}")
                raise AgentExecutionError(
                    f"任务失败: 未知错误"
                ) from e

        raise AgentExecutionError(f"任务失败: 达到最大重试次数")

    def _call_llm(self, prompt: str) -> str:
        """
        内部方法：调用LLM

        模拟随机失败
        """
        import random

        rand = random.random()

        if rand < 0.2:  # 20% 超时
            raise LLMTimeoutError(30.0)
        elif rand < 0.3:  # 10% 速率限制
            raise LLMRateLimitError(retry_after=2.0)
        elif rand < 0.35:  # 5% API错误
            raise LLMAPIError("服务器错误", 500)

        # 成功
        return f"完成: {prompt}"


def ai_error_handling_example():
    """AI应用的错误处理示例"""
    print("\n【示例8】AI应用的完整错误处理")
    print("=" * 60)

    agent = Agent("智能助手", max_retries=3)

    tasks = [
        "分析市场趋势",
        "生成报告",
        "回答用户问题"
    ]

    successful = 0
    failed = 0

    for task in tasks:
        try:
            result = agent.execute(task)
            print(f"  结果: {result}")
            successful += 1
        except AgentExecutionError as e:
            print(f"  ✗ 最终失败: {e}")
            if e.__cause__:
                print(f"  原因: {type(e.__cause__).__name__}")
            failed += 1

    print(f"\n统计:")
    print(f"  成功: {successful}/{len(tasks)}")
    print(f"  失败: {failed}/{len(tasks)}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("Python 错误处理基础")
    print("=" * 60)

    basic_exception_example()
    safe_division_example()
    multiple_exceptions_example()
    else_finally_example()
    custom_exceptions_example()
    exception_chaining_example()
    best_practices_example()
    ai_error_handling_example()

    print("\n" + "=" * 60)
    print("错误处理总结")
    print("=" * 60)
    print("1. 使用 try-except 捕获异常")
    print("2. 捕获具体的异常类型，而不是 Exception")
    print("3. 使用 else 处理没有异常的情况")
    print("4. 使用 finally 清理资源")
    print("5. 创建自定义异常类继承自 Exception")
    print("6. 使用异常链保留原始错误信息")
    print("7. 提供清晰的错误消息")
    print("8. 在AI应用中实现重试机制")
    print("9. 不要忽略或隐藏异常")
    print("10. 记录异常信息便于调试")


if __name__ == "__main__":
    main()
