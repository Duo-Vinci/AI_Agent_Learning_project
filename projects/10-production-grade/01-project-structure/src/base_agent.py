"""
Agent基类
提供标准化的Agent接口和性能指标收集
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import time


class AgentMetrics:
    """Agent性能指标收集器"""

    def __init__(self):
        """初始化指标"""
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_duration = 0.0
        self.min_duration = float('inf')
        self.max_duration = 0.0

    def record_success(self, duration: float):
        """记录成功执行"""
        self.total_executions += 1
        self.successful_executions += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)

    def record_failure(self):
        """记录失败执行"""
        self.total_executions += 1
        self.failed_executions += 1

    @property
    def avg_duration(self) -> float:
        """计算平均执行时间"""
        if self.total_executions == 0:
            return 0.0
        return self.total_duration / self.successful_executions if self.successful_executions > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "avg_duration": self.avg_duration,
            "min_duration": self.min_duration if self.min_duration != float('inf') else 0.0,
            "max_duration": self.max_duration
        }


class BaseAgent(ABC):
    """
    Agent基类

    所有Agent实现都应该继承此类，并实现execute方法
    提供统一的错误处理、日志记录和性能监控
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化Agent

        Args:
            agent_id: Agent唯一标识
            config: Agent配置
            logger: 日志记录器（可选）
        """
        self.agent_id = agent_id
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.metrics = AgentMetrics()

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务（子类必须实现）

        Args:
            input_data: 输入数据

        Returns:
            执行结果
        """
        pass

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行Agent（带错误处理和指标收集）

        Args:
            input_data: 输入数据

        Returns:
            执行结果

        Raises:
            Exception: 执行失败时抛出异常
        """
        start_time = time.time()

        try:
            # 记录开始执行
            self.logger.info(
                f"Agent {self.agent_id} 开始执行",
                extra={
                    "agent_id": self.agent_id,
                    "agent_type": self.__class__.__name__,
                    "input_keys": list(input_data.keys())
                }
            )

            # 执行任务
            result = await self.execute(input_data)

            # 记录成功指标
            duration = time.time() - start_time
            self.metrics.record_success(duration)

            self.logger.info(
                f"Agent {self.agent_id} 执行成功",
                extra={
                    "agent_id": self.agent_id,
                    "duration": duration,
                    "result_keys": list(result.keys()) if isinstance(result, dict) else None
                }
            )

            return result

        except Exception as e:
            # 记录失败指标
            duration = time.time() - start_time
            self.metrics.record_failure()

            self.logger.error(
                f"Agent {self.agent_id} 执行失败",
                extra={
                    "agent_id": self.agent_id,
                    "duration": duration,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )

            raise

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标

        Returns:
            指标字典
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            **self.metrics.to_dict()
        }

    def reset_metrics(self):
        """重置性能指标"""
        self.metrics = AgentMetrics()


class ResearchAgent(BaseAgent):
    """
    研究型Agent示例
    用于信息检索和分析
    """

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行研究任务

        Args:
            input_data: 包含query字段的字典

        Returns:
            研究结果
        """
        query = input_data.get("query", "")

        # 模拟研究过程
        self.logger.debug(f"开始研究: {query}")

        # 这里应该调用实际的LLM或搜索API
        result = {
            "query": query,
            "findings": f"关于 '{query}' 的研究结果",
            "sources": ["source1", "source2"],
            "timestamp": datetime.utcnow().isoformat()
        }

        return result


class WriterAgent(BaseAgent):
    """
    写作型Agent示例
    用于内容生成和编辑
    """

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行写作任务

        Args:
            input_data: 包含topic或research_data字段的字典

        Returns:
            写作结果
        """
        topic = input_data.get("topic", "")
        research_data = input_data.get("research_data", {})

        # 模拟写作过程
        self.logger.debug(f"开始写作: {topic}")

        # 这里应该调用实际的LLM API
        result = {
            "topic": topic,
            "content": f"关于 '{topic}' 的文章内容",
            "word_count": 500,
            "timestamp": datetime.utcnow().isoformat()
        }

        return result


# 使用示例
if __name__ == "__main__":
    import asyncio

    async def main():
        # 创建日志记录器
        logging.basicConfig(level=logging.INFO)

        # 创建研究Agent
        researcher = ResearchAgent(
            agent_id="researcher-001",
            config={"model": "gpt-4", "temperature": 0.3}
        )

        # 执行研究任务
        research_result = await researcher.run({
            "query": "AI Agent的最佳实践"
        })

        print("研究结果:", research_result)
        print("性能指标:", researcher.get_metrics())

        # 创建写作Agent
        writer = WriterAgent(
            agent_id="writer-001",
            config={"model": "gpt-4", "temperature": 0.7}
        )

        # 执行写作任务
        article = await writer.run({
            "topic": "AI Agent开发指南",
            "research_data": research_result
        })

        print("\n写作结果:", article)
        print("性能指标:", writer.get_metrics())

    asyncio.run(main())
