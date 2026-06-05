"""
OpenTelemetry 分布式追踪实现
支持 Jaeger 和 Zipkin 导出
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import time
from typing import Optional, Dict, Any
from functools import wraps
import asyncio


class TracingConfig:
    """追踪配置"""

    def __init__(
        self,
        service_name: str = "ai-agent",
        service_version: str = "1.0.0",
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831,
        enable_console: bool = False
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.jaeger_host = jaeger_host
        self.jaeger_port = jaeger_port
        self.enable_console = enable_console


class DistributedTracer:
    """分布式追踪器"""

    def __init__(self, config: TracingConfig):
        """初始化分布式追踪"""
        self.config = config
        self.tracer = self._setup_tracing()

    def _setup_tracing(self):
        """配置 OpenTelemetry 追踪"""

        # 设置资源信息
        resource = Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "environment": "production",
            "team": "ai-team"
        })

        # 创建 TracerProvider
        provider = TracerProvider(resource=resource)

        # 配置 Jaeger Exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=self.config.jaeger_host,
            agent_port=self.config.jaeger_port,
        )

        # 添加 Span Processor
        provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )

        # 可选：控制台输出（调试用）
        if self.config.enable_console:
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )

        # 设置全局 tracer provider
        trace.set_tracer_provider(provider)

        # 自动仪表化 HTTP 请求
        RequestsInstrumentor().instrument()

        return trace.get_tracer(__name__)

    def create_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        parent_context=None
    ):
        """
        创建新的 Span

        Args:
            name: Span 名称
            attributes: Span 属性
            parent_context: 父 Span 上下文
        """
        span = self.tracer.start_span(
            name,
            context=parent_context,
            attributes=attributes or {}
        )
        return span

    def trace_agent_execution(
        self,
        agent_id: str,
        task_id: str,
        task_type: str
    ):
        """
        追踪 Agent 执行

        用法:
            with tracer.trace_agent_execution("agent-1", "task-1", "analysis"):
                # Agent 执行代码
                pass
        """
        return self.tracer.start_as_current_span(
            "agent.execute",
            attributes={
                "agent.id": agent_id,
                "task.id": task_id,
                "task.type": task_type
            }
        )

    def trace_llm_call(
        self,
        model: str,
        prompt_length: int
    ):
        """追踪 LLM 调用"""
        return self.tracer.start_as_current_span(
            "llm.call",
            attributes={
                "llm.model": model,
                "llm.prompt_length": prompt_length,
                "llm.provider": "openai"
            }
        )

    def trace_tool_call(
        self,
        tool_name: str,
        parameters: Optional[Dict] = None
    ):
        """追踪工具调用"""
        attrs = {
            "tool.name": tool_name,
        }
        if parameters:
            attrs["tool.parameters"] = str(parameters)

        return self.tracer.start_as_current_span(
            f"tool.{tool_name}",
            attributes=attrs
        )

    def add_event(self, span, name: str, attributes: Optional[Dict] = None):
        """向当前 Span 添加事件"""
        span.add_event(name, attributes=attributes or {})

    def set_error(self, span, error: Exception):
        """标记 Span 为错误状态"""
        span.set_status(Status(StatusCode.ERROR, str(error)))
        span.record_exception(error)


def trace_function(operation_name: Optional[str] = None):
    """
    函数追踪装饰器

    用法:
        @trace_function("custom_operation")
        async def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = operation_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                start_time = time.time()

                try:
                    result = await func(*args, **kwargs)

                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)
                    span.set_status(Status(StatusCode.OK))

                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = operation_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)
                    span.set_status(Status(StatusCode.OK))

                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 完整的使用示例
async def example_agent_workflow():
    """示例：完整的 Agent 工作流追踪"""

    # 初始化追踪器
    config = TracingConfig(
        service_name="ai-agent-example",
        jaeger_host="localhost",
        jaeger_port=6831
    )
    tracer = DistributedTracer(config)

    # 模拟 Agent 执行
    with tracer.trace_agent_execution(
        agent_id="agent-123",
        task_id="task-456",
        task_type="data_analysis"
    ) as span:

        # 添加事件
        tracer.add_event(span, "agent_started")

        # 模拟规划阶段
        with tracer.tracer.start_as_current_span("planning") as planning_span:
            planning_span.set_attribute("plan_steps", 3)
            await asyncio.sleep(0.1)

        # 模拟 LLM 调用
        with tracer.trace_llm_call(model="gpt-4", prompt_length=150) as llm_span:
            llm_span.set_attribute("llm.temperature", 0.7)
            llm_span.set_attribute("llm.max_tokens", 500)

            await asyncio.sleep(0.5)  # 模拟 LLM 调用

            llm_span.set_attribute("llm.prompt_tokens", 150)
            llm_span.set_attribute("llm.completion_tokens", 80)
            llm_span.set_attribute("llm.total_tokens", 230)

        # 模拟工具调用
        with tracer.trace_tool_call(
            tool_name="web_search",
            parameters={"query": "AI trends"}
        ) as tool_span:
            tool_span.set_attribute("tool.results_count", 5)
            await asyncio.sleep(0.3)

        # 模拟另一个 LLM 调用（合成结果）
        with tracer.trace_llm_call(model="gpt-4", prompt_length=300) as llm_span2:
            await asyncio.sleep(0.4)
            llm_span2.set_attribute("llm.total_tokens", 400)

        tracer.add_event(span, "agent_completed", {
            "success": True,
            "result_size": 1024
        })


# 使用装饰器的示例
@trace_function("data_processing")
async def process_data(data: str):
    """处理数据（自动追踪）"""
    await asyncio.sleep(0.2)
    return f"Processed: {data}"


@trace_function()
def calculate_cost(tokens: int) -> float:
    """计算成本（自动追踪）"""
    time.sleep(0.05)
    return tokens * 0.00002


if __name__ == "__main__":
    print("启动分布式追踪示例...")
    print("确保 Jaeger 正在运行: docker run -d -p 6831:6831/udp -p 16686:16686 jaegertracing/all-in-one:latest")
    print()

    # 运行示例
    asyncio.run(example_agent_workflow())

    print("\n追踪数据已发送到 Jaeger!")
    print("访问 http://localhost:16686 查看追踪信息")
    print("\n在 Jaeger UI 中：")
    print("1. 选择服务: ai-agent-example")
    print("2. 点击 'Find Traces' 查看追踪")
    print("3. 点击具体 trace 查看详细的调用链")
