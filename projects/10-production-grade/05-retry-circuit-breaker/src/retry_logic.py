"""
重试机制
支持指数退避、最大重试次数和异常过滤
"""

import asyncio
import time
import logging
from typing import Callable, Type, Tuple, Optional, Any
from functools import wraps


logger = logging.getLogger(__name__)


class RetryException(Exception):
    """重试失败异常"""
    pass


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    重试装饰器（支持同步和异步函数）

    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟时间（秒）
        backoff: 退避系数（每次重试延迟时间乘以此系数）
        exceptions: 需要重试的异常类型元组
        on_retry: 重试时的回调函数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            last_exception = None

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e

                    if attempt >= max_attempts:
                        logger.error(
                            f"重试失败: {func.__name__} 已达到最大重试次数",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "error": str(e)
                            }
                        )
                        raise RetryException(
                            f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败"
                        ) from e

                    logger.warning(
                        f"重试 {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "error": str(e),
                            "retry_delay": current_delay
                        }
                    )

                    # 执行重试回调
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.warning(f"重试回调执行失败: {callback_error}")

                    # 等待后重试
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # 理论上不会到达这里
            raise RetryException(
                f"函数 {func.__name__} 重试逻辑异常"
            ) from last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            last_exception = None

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e

                    if attempt >= max_attempts:
                        logger.error(
                            f"重试失败: {func.__name__} 已达到最大重试次数",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "error": str(e)
                            }
                        )
                        raise RetryException(
                            f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败"
                        ) from e

                    logger.warning(
                        f"重试 {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "error": str(e),
                            "retry_delay": current_delay
                        }
                    )

                    # 执行重试回调
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.warning(f"重试回调执行失败: {callback_error}")

                    # 等待后重试
                    time.sleep(current_delay)
                    current_delay *= backoff

            # 理论上不会到达这里
            raise RetryException(
                f"函数 {func.__name__} 重试逻辑异常"
            ) from last_exception

        # 根据函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class RetryConfig:
    """重试配置类"""

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = False
    ):
        """
        初始化重试配置

        Args:
            max_attempts: 最大尝试次数
            delay: 初始延迟时间（秒）
            backoff: 退避系数
            max_delay: 最大延迟时间（秒）
            jitter: 是否添加随机抖动
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.max_delay = max_delay
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """
        计算延迟时间

        Args:
            attempt: 当前尝试次数

        Returns:
            延迟时间（秒）
        """
        import random

        # 计算指数退避延迟
        delay = self.delay * (self.backoff ** (attempt - 1))

        # 限制最大延迟
        delay = min(delay, self.max_delay)

        # 添加随机抖动（避免惊群效应）
        if self.jitter:
            delay *= (0.5 + random.random())

        return delay


async def retry_async(
    func: Callable,
    config: RetryConfig,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    *args,
    **kwargs
) -> Any:
    """
    异步重试函数

    Args:
        func: 要执行的异步函数
        config: 重试配置
        exceptions: 需要重试的异常类型
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        函数返回值

    Raises:
        RetryException: 达到最大重试次数后仍失败
    """
    attempt = 0
    last_exception = None

    while attempt < config.max_attempts:
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            attempt += 1
            last_exception = e

            if attempt >= config.max_attempts:
                raise RetryException(
                    f"函数在 {config.max_attempts} 次尝试后仍然失败"
                ) from e

            delay = config.calculate_delay(attempt)
            logger.warning(
                f"重试 {func.__name__} (尝试 {attempt}/{config.max_attempts})",
                extra={"delay": delay, "error": str(e)}
            )

            await asyncio.sleep(delay)

    raise RetryException("重试逻辑异常") from last_exception


# 使用示例
if __name__ == "__main__":
    import random

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 50)
    print("重试机制示例")
    print("=" * 50)

    # 1. 基础重试装饰器
    print("\n1. 基础重试装饰器:")

    attempt_count = 0

    @retry(max_attempts=3, delay=0.5, backoff=2.0)
    def unstable_operation():
        """模拟不稳定的操作"""
        global attempt_count
        attempt_count += 1
        print(f"   执行尝试 #{attempt_count}")

        if attempt_count < 3:
            raise ConnectionError("连接失败")

        return "成功"

    try:
        result = unstable_operation()
        print(f"   最终结果: {result}")
    except RetryException as e:
        print(f"   重试失败: {e}")

    # 2. 异步重试
    print("\n2. 异步重试:")

    async_attempt_count = 0

    @retry(max_attempts=3, delay=0.3, backoff=1.5, exceptions=(ValueError, RuntimeError))
    async def unstable_async_operation():
        """模拟不稳定的异步操作"""
        global async_attempt_count
        async_attempt_count += 1
        print(f"   异步尝试 #{async_attempt_count}")

        if async_attempt_count < 2:
            raise ValueError("临时错误")

        return {"status": "success", "data": "异步结果"}

    async def test_async():
        result = await unstable_async_operation()
        print(f"   异步结果: {result}")

    asyncio.run(test_async())

    # 3. 重试回调
    print("\n3. 带回调的重试:")

    def retry_callback(attempt: int, error: Exception):
        """重试回调函数"""
        print(f"   [回调] 第 {attempt} 次重试，错误: {error}")

    callback_count = 0

    @retry(max_attempts=3, delay=0.2, on_retry=retry_callback)
    def operation_with_callback():
        global callback_count
        callback_count += 1
        if callback_count < 2:
            raise TimeoutError("操作超时")
        return "完成"

    result = operation_with_callback()
    print(f"   结果: {result}")

    # 4. 重试配置类
    print("\n4. 使用重试配置类:")

    config = RetryConfig(
        max_attempts=5,
        delay=0.5,
        backoff=2.0,
        max_delay=10.0,
        jitter=True
    )

    print(f"   重试延迟序列:")
    for i in range(1, 6):
        delay = config.calculate_delay(i)
        print(f"   尝试 {i}: {delay:.2f} 秒")

    # 5. 限制重试的异常类型
    print("\n5. 限制重试的异常类型:")

    retry_count = 0

    @retry(max_attempts=3, delay=0.2, exceptions=(ConnectionError, TimeoutError))
    def selective_retry():
        """只对特定异常重试"""
        global retry_count
        retry_count += 1

        if retry_count == 1:
            raise ConnectionError("连接错误（会重试）")
        elif retry_count == 2:
            return "成功"

    try:
        result = selective_retry()
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   失败: {e}")

    # 测试不会重试的异常
    print("\n   测试不会重试的异常:")

    @retry(max_attempts=3, delay=0.2, exceptions=(ConnectionError,))
    def no_retry_for_value_error():
        raise ValueError("值错误（不会重试）")

    try:
        no_retry_for_value_error()
    except ValueError as e:
        print(f"   捕获到未重试的异常: {e}")
