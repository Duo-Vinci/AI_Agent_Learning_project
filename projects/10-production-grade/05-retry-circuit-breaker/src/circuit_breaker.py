"""
熔断器模式
防止系统持续调用失败的服务
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict
from functools import wraps
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"          # 正常状态，请求可以通过
    OPEN = "open"              # 熔断状态，请求直接失败
    HALF_OPEN = "half_open"    # 半开状态，允许少量请求测试服务是否恢复


class CircuitBreakerException(Exception):
    """熔断器异常"""
    pass


class CircuitBreaker:
    """
    熔断器

    当失败次数超过阈值时，打开熔断器，一段时间内拒绝所有请求
    经过恢复时间后进入半开状态，允许少量请求测试服务是否恢复
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        success_threshold: int = 2
    ):
        """
        初始化熔断器

        Args:
            name: 熔断器名称
            failure_threshold: 失败阈值（连续失败多少次后打开熔断器）
            recovery_timeout: 恢复超时时间（秒）
            expected_exception: 预期的异常类型
            success_threshold: 半开状态下成功多少次后关闭熔断器
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        # 状态
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change_time = time.time()

        # 统计
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器调用函数

        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            CircuitBreakerException: 熔断器打开时抛出
        """
        self.total_calls += 1

        # 检查熔断器状态
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"熔断器 [{self.name}] 进入半开状态")
                self._set_state(CircuitState.HALF_OPEN)
            else:
                self.rejected_calls += 1
                raise CircuitBreakerException(
                    f"熔断器 [{self.name}] 已打开，请求被拒绝"
                )

        try:
            # 执行函数
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """成功回调"""
        self.successful_calls += 1
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"熔断器 [{self.name}] 半开状态测试成功 "
                f"({self.success_count}/{self.success_threshold})"
            )

            if self.success_count >= self.success_threshold:
                logger.info(f"熔断器 [{self.name}] 关闭")
                self._set_state(CircuitState.CLOSED)
                self.success_count = 0

    def _on_failure(self):
        """失败回调"""
        self.failed_calls += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        logger.warning(
            f"熔断器 [{self.name}] 检测到失败 "
            f"({self.failure_count}/{self.failure_threshold})"
        )

        if self.state == CircuitState.HALF_OPEN:
            # 半开状态下失败，立即重新打开熔断器
            logger.warning(f"熔断器 [{self.name}] 半开状态测试失败，重新打开")
            self._set_state(CircuitState.OPEN)
            self.success_count = 0

        elif self.failure_count >= self.failure_threshold:
            # 失败次数达到阈值，打开熔断器
            logger.error(f"熔断器 [{self.name}] 打开")
            self._set_state(CircuitState.OPEN)

    def _should_attempt_reset(self) -> bool:
        """
        判断是否应该尝试恢复

        Returns:
            是否应该尝试恢复
        """
        if self.last_failure_time is None:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def _set_state(self, new_state: CircuitState):
        """
        设置熔断器状态

        Args:
            new_state: 新状态
        """
        old_state = self.state
        self.state = new_state
        self.last_state_change_time = time.time()

        logger.info(
            f"熔断器 [{self.name}] 状态变更: {old_state.value} -> {new_state.value}"
        )

        if new_state == CircuitState.CLOSED:
            self.failure_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_threshold": self.failure_threshold,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "success_rate": (
                self.successful_calls / self.total_calls
                if self.total_calls > 0 else 0
            ),
            "last_state_change": datetime.fromtimestamp(
                self.last_state_change_time
            ).isoformat()
        }

    def reset(self):
        """重置熔断器"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info(f"熔断器 [{self.name}] 已重置")


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """
    熔断器装饰器

    Args:
        name: 熔断器名称
        failure_threshold: 失败阈值
        recovery_timeout: 恢复超时时间
        expected_exception: 预期的异常类型

    Returns:
        装饰器函数
    """
    breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception
    )

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        # 将熔断器实例附加到函数上
        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 50)
    print("熔断器模式示例")
    print("=" * 50)

    # 1. 基础熔断器
    print("\n1. 基础熔断器:")

    breaker = CircuitBreaker(
        name="api-service",
        failure_threshold=3,
        recovery_timeout=5
    )

    def unreliable_service(should_fail: bool = True):
        """模拟不可靠的服务"""
        if should_fail:
            raise ConnectionError("服务不可用")
        return "成功"

    # 触发多次失败
    for i in range(5):
        try:
            result = breaker.call(unreliable_service, should_fail=True)
            print(f"   调用 {i+1}: {result}")
        except (ConnectionError, CircuitBreakerException) as e:
            print(f"   调用 {i+1}: 失败 - {type(e).__name__}")

        # 查看熔断器状态
        stats = breaker.get_stats()
        print(f"   状态: {stats['state']}, 失败计数: {stats['failure_count']}")

    # 2. 熔断器装饰器
    print("\n2. 熔断器装饰器:")

    call_count = 0

    @circuit_breaker(
        name="database",
        failure_threshold=3,
        recovery_timeout=3
    )
    def database_query():
        """模拟数据库查询"""
        global call_count
        call_count += 1

        if call_count <= 3:
            raise ConnectionError("数据库连接失败")

        return {"data": "查询结果"}

    # 触发失败
    for i in range(6):
        try:
            result = database_query()
            print(f"   查询 {i+1}: {result}")
        except (ConnectionError, CircuitBreakerException) as e:
            print(f"   查询 {i+1}: {type(e).__name__}")

        time.sleep(0.5)

    # 3. 熔断器恢复测试
    print("\n3. 熔断器恢复测试:")

    breaker2 = CircuitBreaker(
        name="external-api",
        failure_threshold=2,
        recovery_timeout=2,
        success_threshold=2
    )

    request_count = 0

    def external_api_call():
        """模拟外部API调用"""
        global request_count
        request_count += 1

        # 前2次失败
        if request_count <= 2:
            raise TimeoutError("API超时")

        # 后续成功
        return {"status": "ok"}

    print("   触发失败...")
    for i in range(3):
        try:
            result = breaker2.call(external_api_call)
            print(f"   请求 {i+1}: {result}")
        except (TimeoutError, CircuitBreakerException) as e:
            print(f"   请求 {i+1}: {type(e).__name__}")

    print(f"   熔断器状态: {breaker2.state.value}")
    print(f"   等待 {breaker2.recovery_timeout} 秒...")
    time.sleep(breaker2.recovery_timeout)

    print("   尝试恢复...")
    for i in range(3):
        try:
            result = breaker2.call(external_api_call)
            print(f"   恢复请求 {i+1}: {result}")
        except (TimeoutError, CircuitBreakerException) as e:
            print(f"   恢复请求 {i+1}: {type(e).__name__}")

    print(f"   最终状态: {breaker2.state.value}")

    # 4. 统计信息
    print("\n4. 熔断器统计信息:")
    stats = breaker2.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
