"""
错误处理器
提供统一的错误处理和降级策略
"""

import logging
from typing import Callable, Any, Optional, Dict, Type
from functools import wraps
import traceback
from datetime import datetime


class ErrorHandler:
    """
    错误处理器
    提供统一的错误捕获、日志记录和降级处理
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化错误处理器

        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, Dict[str, Any]] = {}

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        notify: bool = True
    ) -> Dict[str, Any]:
        """
        处理错误

        Args:
            error: 异常对象
            context: 错误上下文信息
            notify: 是否发送通知

        Returns:
            错误信息字典
        """
        error_type = type(error).__name__
        error_message = str(error)
        context = context or {}

        # 记录错误计数
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # 记录最后错误
        self.last_errors[error_type] = {
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "count": self.error_counts[error_type]
        }

        # 记录日志
        self.logger.error(
            f"错误处理: {error_type}",
            extra={
                "error_type": error_type,
                "error_message": error_message,
                "context": context,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )

        # 发送通知（如果需要）
        if notify and self._should_notify(error_type):
            self._send_notification(error, context)

        # 返回错误信息
        return {
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _should_notify(self, error_type: str) -> bool:
        """
        判断是否应该发送通知

        Args:
            error_type: 错误类型

        Returns:
            是否发送通知
        """
        # 可以根据错误类型和频率决定是否通知
        # 例如：连续错误超过阈值时才通知
        count = self.error_counts.get(error_type, 0)
        return count <= 5  # 只通知前5次

    def _send_notification(self, error: Exception, context: Dict[str, Any]):
        """
        发送错误通知

        Args:
            error: 异常对象
            context: 错误上下文
        """
        # 这里可以集成Slack、钉钉、邮件等通知渠道
        self.logger.warning(f"[通知] 发生错误: {type(error).__name__} - {str(error)}")

    def get_error_stats(self) -> Dict[str, Any]:
        """
        获取错误统计信息

        Returns:
            错误统计字典
        """
        return {
            "error_counts": self.error_counts,
            "last_errors": self.last_errors,
            "total_errors": sum(self.error_counts.values())
        }

    def reset_stats(self):
        """重置错误统计"""
        self.error_counts.clear()
        self.last_errors.clear()


def with_error_handler(
    fallback: Optional[Callable] = None,
    reraise: bool = True,
    log_error: bool = True
):
    """
    错误处理装饰器

    Args:
        fallback: 降级处理函数
        reraise: 是否重新抛出异常
        log_error: 是否记录错误日志

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger = logging.getLogger(func.__module__)
                    logger.error(
                        f"函数 {func.__name__} 执行失败",
                        extra={
                            "function": func.__name__,
                            "error": str(e),
                            "error_type": type(e).__name__
                        },
                        exc_info=True
                    )

                if fallback:
                    return fallback(*args, **kwargs)

                if reraise:
                    raise

                return None

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger = logging.getLogger(func.__module__)
                    logger.error(
                        f"函数 {func.__name__} 执行失败",
                        extra={
                            "function": func.__name__,
                            "error": str(e),
                            "error_type": type(e).__name__
                        },
                        exc_info=True
                    )

                if fallback:
                    return fallback(*args, **kwargs)

                if reraise:
                    raise

                return None

        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def safe_execute(
    func: Callable,
    *args,
    default: Any = None,
    exceptions: tuple = (Exception,),
    **kwargs
) -> Any:
    """
    安全执行函数

    Args:
        func: 要执行的函数
        *args: 位置参数
        default: 发生异常时的默认返回值
        exceptions: 要捕获的异常类型元组
        **kwargs: 关键字参数

    Returns:
        函数返回值或默认值
    """
    try:
        return func(*args, **kwargs)
    except exceptions as e:
        logger = logging.getLogger(__name__)
        logger.warning(
            f"安全执行失败，返回默认值",
            extra={
                "function": func.__name__,
                "error": str(e),
                "default": default
            }
        )
        return default


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 50)
    print("错误处理器示例")
    print("=" * 50)

    # 1. 基础错误处理
    print("\n1. 基础错误处理:")
    handler = ErrorHandler()

    try:
        raise ValueError("测试错误")
    except Exception as e:
        error_info = handler.handle_error(
            e,
            context={"operation": "test", "input": "invalid"}
        )
        print(f"   错误信息: {error_info}")

    # 2. 错误统计
    print("\n2. 错误统计:")
    for i in range(3):
        try:
            raise ConnectionError("连接失败")
        except Exception as e:
            handler.handle_error(e, context={"attempt": i + 1})

    stats = handler.get_error_stats()
    print(f"   总错误数: {stats['total_errors']}")
    print(f"   错误计数: {stats['error_counts']}")

    # 3. 装饰器使用
    print("\n3. 错误处理装饰器:")

    def fallback_function(*args, **kwargs):
        return {"status": "fallback", "message": "使用降级逻辑"}

    @with_error_handler(fallback=fallback_function, reraise=False)
    def risky_operation():
        raise RuntimeError("操作失败")

    result = risky_operation()
    print(f"   降级结果: {result}")

    # 4. 安全执行
    print("\n4. 安全执行:")

    def divide(a, b):
        return a / b

    result1 = safe_execute(divide, 10, 2, default=0)
    print(f"   正常执行: 10 / 2 = {result1}")

    result2 = safe_execute(divide, 10, 0, default=0)
    print(f"   异常捕获: 10 / 0 = {result2} (使用默认值)")

    # 5. 异步函数错误处理
    print("\n5. 异步函数错误处理:")

    import asyncio

    @with_error_handler(reraise=False)
    async def async_operation():
        await asyncio.sleep(0.1)
        raise ValueError("异步操作失败")

    asyncio.run(async_operation())
    print("   异步错误已捕获并记录")
