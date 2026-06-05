"""
结构化日志系统
支持JSON格式输出、请求追踪和上下文管理
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import uuid


# 请求ID上下文变量
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)
user_id_var: ContextVar[str] = ContextVar('user_id', default=None)


class JSONFormatter(logging.Formatter):
    """
    JSON格式化器
    将日志记录格式化为JSON字符串，便于日志聚合平台处理
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录

        Args:
            record: 日志记录对象

        Returns:
            JSON格式的日志字符串
        """
        # 基础日志数据
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
        }

        # 添加请求追踪信息
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # 添加额外字段（从extra参数传入）
        if hasattr(record, '__dict__'):
            # 排除标准字段
            standard_fields = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                'getMessage', 'message'
            }

            for key, value in record.__dict__.items():
                if key not in standard_fields and not key.startswith('_'):
                    # 确保值可以JSON序列化
                    try:
                        json.dumps(value)
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)

        # 处理异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_data, ensure_ascii=False, default=str)


class StructuredLogger:
    """
    结构化日志记录器
    提供统一的日志记录接口，支持结构化字段
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        format_type: str = "json",
        handlers: Optional[list] = None
    ):
        """
        初始化日志记录器

        Args:
            name: 日志记录器名称
            level: 日志级别
            format_type: 格式类型（json或text）
            handlers: 自定义处理器列表
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # 避免重复添加处理器
        if not self.logger.handlers:
            if handlers:
                for handler in handlers:
                    self.logger.addHandler(handler)
            else:
                # 默认控制台处理器
                handler = logging.StreamHandler(sys.stdout)

                # 选择格式化器
                if format_type == "json":
                    handler.setFormatter(JSONFormatter())
                else:
                    handler.setFormatter(logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    ))

                self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs):
        """
        统一的日志记录方法

        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外的结构化字段
        """
        extra = kwargs.copy()
        getattr(self.logger, level.lower())(message, extra=extra)

    def debug(self, message: str, **kwargs):
        """记录DEBUG级别日志"""
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """记录INFO级别日志"""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """记录WARNING级别日志"""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """记录ERROR级别日志"""
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """记录CRITICAL级别日志"""
        self._log("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs):
        """记录异常日志（自动包含堆栈跟踪）"""
        self.logger.exception(message, extra=kwargs)


class RequestLogger:
    """
    带请求追踪的日志记录器
    自动为每条日志添加请求ID和用户ID
    """

    def __init__(self, logger: StructuredLogger):
        """
        初始化请求日志记录器

        Args:
            logger: 结构化日志记录器
        """
        self.logger = logger

    def _add_context(self, kwargs: dict) -> dict:
        """
        添加上下文信息

        Args:
            kwargs: 日志参数

        Returns:
            包含上下文的日志参数
        """
        request_id = request_id_var.get()
        if request_id:
            kwargs['request_id'] = request_id

        user_id = user_id_var.get()
        if user_id:
            kwargs['user_id'] = user_id

        return kwargs

    def debug(self, message: str, **kwargs):
        """记录DEBUG级别日志"""
        self.logger.debug(message, **self._add_context(kwargs))

    def info(self, message: str, **kwargs):
        """记录INFO级别日志"""
        self.logger.info(message, **self._add_context(kwargs))

    def warning(self, message: str, **kwargs):
        """记录WARNING级别日志"""
        self.logger.warning(message, **self._add_context(kwargs))

    def error(self, message: str, **kwargs):
        """记录ERROR级别日志"""
        self.logger.error(message, **self._add_context(kwargs))

    def critical(self, message: str, **kwargs):
        """记录CRITICAL级别日志"""
        self.logger.critical(message, **self._add_context(kwargs))

    def exception(self, message: str, **kwargs):
        """记录异常日志"""
        self.logger.exception(message, **self._add_context(kwargs))


def setup_logging(
    app_name: str,
    level: str = "INFO",
    format_type: str = "json"
) -> StructuredLogger:
    """
    设置应用日志系统

    Args:
        app_name: 应用名称
        level: 日志级别
        format_type: 格式类型

    Returns:
        日志记录器实例
    """
    return StructuredLogger(app_name, level=level, format_type=format_type)


def set_request_context(request_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    设置请求上下文

    Args:
        request_id: 请求ID（如果为None则自动生成）
        user_id: 用户ID
    """
    if request_id is None:
        request_id = str(uuid.uuid4())

    request_id_var.set(request_id)

    if user_id:
        user_id_var.set(user_id)


def clear_request_context():
    """清除请求上下文"""
    request_id_var.set(None)
    user_id_var.set(None)


# 使用示例
if __name__ == "__main__":
    print("=" * 50)
    print("结构化日志系统示例")
    print("=" * 50)

    # 1. 基础结构化日志
    print("\n1. 基础结构化日志（JSON格式）:")
    logger = StructuredLogger("ai-agent", level="DEBUG", format_type="json")

    logger.info("应用启动", version="1.0.0", port=8000)
    logger.debug("调试信息", module="main", action="init")
    logger.warning("警告信息", message="内存使用率较高", usage=85)
    logger.error("错误信息", error_code="ERR001", details="连接失败")

    # 2. 异常日志
    print("\n2. 异常日志（包含堆栈跟踪）:")
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("发生除零错误", operation="division", numerator=1, denominator=0)

    # 3. 请求追踪日志
    print("\n3. 请求追踪日志:")
    request_logger = RequestLogger(logger)

    # 模拟请求1
    set_request_context(request_id="req-001", user_id="user-123")
    request_logger.info("用户登录", method="POST", endpoint="/api/login")
    request_logger.info("查询用户信息", user_id="user-123")

    # 模拟请求2
    set_request_context(request_id="req-002", user_id="user-456")
    request_logger.info("执行AI任务", agent_id="agent-001", task="research")
    request_logger.warning("任务执行缓慢", duration=5.2, threshold=3.0)

    clear_request_context()

    # 4. 文本格式日志（便于开发环境查看）
    print("\n4. 文本格式日志:")
    text_logger = StructuredLogger("ai-agent-dev", level="INFO", format_type="text")
    text_logger.info("这是文本格式的日志")
    text_logger.warning("警告消息")

    # 5. 自定义处理器（同时输出到文件和控制台）
    print("\n5. 自定义处理器示例:")

    # 文件处理器
    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setFormatter(JSONFormatter())

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())

    multi_logger = StructuredLogger(
        "multi-output",
        level="INFO",
        handlers=[file_handler, console_handler]
    )

    multi_logger.info("此日志同时输出到文件和控制台", feature="multi-output")

    print("\n✓ 日志已保存到 app.log 文件")
