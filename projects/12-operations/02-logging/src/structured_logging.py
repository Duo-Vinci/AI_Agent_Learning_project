"""
结构化日志工具
支持 JSON 格式输出，便于 ELK 收集和分析
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """JSON 格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """将日志记录格式化为 JSON"""

        # 基础日志信息
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加额外字段
        if hasattr(record, 'agent_id'):
            log_data['agent_id'] = record.agent_id

        if hasattr(record, 'task_id'):
            log_data['task_id'] = record.task_id

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration

        # LLM 调用信息
        if hasattr(record, 'llm_call'):
            log_data['llm_call'] = record.llm_call

        # 异常信息
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # 额外的上下文数据
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class AgentLogger:
    """AI Agent 专用日志器"""

    def __init__(
        self,
        name: str = "ai-agent",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        console_output: bool = True
    ):
        """
        初始化日志器

        Args:
            name: 日志器名称
            level: 日志级别
            log_file: 日志文件路径
            console_output: 是否输出到控制台
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # 清空已有处理器

        # JSON 格式化器
        json_formatter = JSONFormatter()

        # 控制台输出
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(json_formatter)
            self.logger.addHandler(console_handler)

        # 文件输出
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)

    def _log(
        self,
        level: int,
        message: str,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        duration: Optional[float] = None,
        llm_call: Optional[Dict] = None,
        extra_data: Optional[Dict] = None,
        exc_info: bool = False
    ):
        """内部日志方法"""
        extra = {}

        if agent_id:
            extra['agent_id'] = agent_id
        if task_id:
            extra['task_id'] = task_id
        if user_id:
            extra['user_id'] = user_id
        if duration is not None:
            extra['duration'] = duration
        if llm_call:
            extra['llm_call'] = llm_call
        if extra_data:
            extra['extra_data'] = extra_data

        self.logger.log(level, message, extra=extra, exc_info=exc_info)

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        kwargs['exc_info'] = kwargs.get('exc_info', True)
        self._log(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self._log(logging.DEBUG, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        kwargs['exc_info'] = kwargs.get('exc_info', True)
        self._log(logging.CRITICAL, message, **kwargs)

    def log_agent_request(
        self,
        agent_id: str,
        task_id: str,
        task_type: str,
        status: str,
        duration: float,
        user_id: Optional[str] = None
    ):
        """记录 Agent 请求"""
        self.info(
            f"Agent request completed: {status}",
            agent_id=agent_id,
            task_id=task_id,
            user_id=user_id,
            duration=duration,
            extra_data={
                'task_type': task_type,
                'status': status
            }
        )

    def log_llm_call(
        self,
        agent_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration: float,
        cost: float,
        task_id: Optional[str] = None
    ):
        """记录 LLM 调用"""
        llm_call_data = {
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'duration': duration,
            'cost': cost
        }

        self.info(
            f"LLM call completed: {model}",
            agent_id=agent_id,
            task_id=task_id,
            llm_call=llm_call_data
        )

    def log_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        duration: float,
        status: str,
        task_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """记录工具调用"""
        extra = {
            'tool_name': tool_name,
            'status': status
        }

        if error:
            extra['error'] = error

        self.info(
            f"Tool call: {tool_name} - {status}",
            agent_id=agent_id,
            task_id=task_id,
            duration=duration,
            extra_data=extra
        )


# 全局日志器实例
logger = AgentLogger(
    name="ai-agent",
    level=logging.INFO,
    log_file="/var/log/agent/app.log",
    console_output=True
)


# 使用示例
if __name__ == "__main__":
    # 基础日志
    logger.info("Application started")

    # Agent 请求日志
    logger.log_agent_request(
        agent_id="agent-123",
        task_id="task-456",
        task_type="data_analysis",
        status="success",
        duration=5.32,
        user_id="user-789"
    )

    # LLM 调用日志
    logger.log_llm_call(
        agent_id="agent-123",
        model="gpt-4",
        prompt_tokens=150,
        completion_tokens=80,
        duration=2.5,
        cost=0.014,
        task_id="task-456"
    )

    # 工具调用日志
    logger.log_tool_call(
        agent_id="agent-123",
        tool_name="web_search",
        duration=1.2,
        status="success",
        task_id="task-456"
    )

    # 错误日志
    try:
        raise ValueError("示例错误")
    except Exception as e:
        logger.error(
            "Error occurred during task execution",
            agent_id="agent-123",
            task_id="task-456",
            exc_info=True
        )

    print("\n日志已生成！检查输出和日志文件。")
