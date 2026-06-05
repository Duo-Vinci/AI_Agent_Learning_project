"""
自定义异常类
提供结构化的异常层次和错误信息
"""

from typing import Dict, Any, Optional


class AgentException(Exception):
    """
    Agent异常基类
    所有自定义异常都应该继承此类
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        初始化异常

        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详情
            original_error: 原始异常（如果是包装其他异常）
        """
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            错误信息字典
        """
        error_dict = {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }

        if self.original_error:
            error_dict["original_error"] = str(self.original_error)

        return error_dict

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class LLMException(AgentException):
    """LLM调用异常"""
    pass


class LLMTimeoutException(LLMException):
    """LLM调用超时异常"""
    pass


class LLMRateLimitException(LLMException):
    """LLM速率限制异常"""
    pass


class LLMQuotaExceededException(LLMException):
    """LLM配额超限异常"""
    pass


class ToolException(AgentException):
    """工具执行异常"""
    pass


class ToolTimeoutException(ToolException):
    """工具执行超时异常"""
    pass


class ToolNotFoundException(ToolException):
    """工具不存在异常"""
    pass


class ValidationException(AgentException):
    """数据验证异常"""
    pass


class InvalidInputException(ValidationException):
    """无效输入异常"""
    pass


class InvalidOutputException(ValidationException):
    """无效输出异常"""
    pass


class RateLimitException(AgentException):
    """速率限制异常"""
    pass


class TimeoutException(AgentException):
    """超时异常"""
    pass


class ConfigurationException(AgentException):
    """配置异常"""
    pass


class DatabaseException(AgentException):
    """数据库异常"""
    pass


class CacheException(AgentException):
    """缓存异常"""
    pass


class AuthenticationException(AgentException):
    """认证异常"""
    pass


class AuthorizationException(AgentException):
    """授权异常"""
    pass


class ResourceNotFoundException(AgentException):
    """资源不存在异常"""
    pass


class ServiceUnavailableException(AgentException):
    """服务不可用异常"""
    pass


# 使用示例
if __name__ == "__main__":
    print("=" * 50)
    print("自定义异常示例")
    print("=" * 50)

    # 1. 基础异常
    print("\n1. 基础异常:")
    try:
        raise AgentException(
            message="Agent执行失败",
            code="AGENT_ERROR",
            details={"agent_id": "agent-001", "task": "research"}
        )
    except AgentException as e:
        print(f"   异常: {e}")
        print(f"   错误代码: {e.code}")
        print(f"   详情: {e.details}")
        print(f"   字典格式: {e.to_dict()}")

    # 2. LLM异常
    print("\n2. LLM异常:")
    try:
        raise LLMTimeoutException(
            message="LLM调用超时",
            details={"model": "gpt-4", "timeout": 30, "duration": 35}
        )
    except LLMException as e:
        print(f"   异常: {e}")
        print(f"   类型: {type(e).__name__}")

    # 3. 验证异常
    print("\n3. 验证异常:")
    try:
        raise InvalidInputException(
            message="输入数据格式错误",
            details={
                "field": "email",
                "value": "invalid-email",
                "expected": "valid email format"
            }
        )
    except ValidationException as e:
        print(f"   异常: {e}")
        print(f"   详情: {e.details}")

    # 4. 包装原始异常
    print("\n4. 包装原始异常:")
    try:
        try:
            result = 1 / 0
        except ZeroDivisionError as original_error:
            raise ToolException(
                message="工具执行失败",
                code="TOOL_EXECUTION_ERROR",
                details={"tool": "calculator", "operation": "divide"},
                original_error=original_error
            )
    except ToolException as e:
        print(f"   异常: {e}")
        print(f"   原始错误: {e.original_error}")
        print(f"   完整信息: {e.to_dict()}")

    # 5. 速率限制异常
    print("\n5. 速率限制异常:")
    try:
        raise RateLimitException(
            message="API调用速率超限",
            details={
                "limit": 100,
                "current": 105,
                "window": "1 minute",
                "retry_after": 45
            }
        )
    except RateLimitException as e:
        print(f"   异常: {e}")
        print(f"   详情: {e.details}")
        retry_after = e.details.get("retry_after", 0)
        print(f"   建议: 请在 {retry_after} 秒后重试")
