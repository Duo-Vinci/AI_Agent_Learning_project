"""
FastAPI 应用中集成分布式追踪
"""

from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from distributed_tracing import TracingConfig, DistributedTracer
import uvicorn
import asyncio


# 初始化追踪
config = TracingConfig(
    service_name="ai-agent-api",
    service_version="1.0.0",
    jaeger_host="localhost",
    jaeger_port=6831
)
tracer_instance = DistributedTracer(config)

# 创建 FastAPI 应用
app = FastAPI(title="AI Agent API with Tracing")

# 自动仪表化 FastAPI
FastAPIInstrumentor.instrument_app(app)

# 自动仪表化日志
LoggingInstrumentor().instrument(set_logging_format=True)

# 获取 tracer
tracer = trace.get_tracer(__name__)


@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    """添加追踪上下文到请求"""
    # 这里可以从请求头提取 trace context（用于跨服务追踪）
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    """根路径"""
    with tracer.start_as_current_span("root_handler"):
        return {"message": "AI Agent API with Distributed Tracing"}


@app.post("/agent/execute")
async def execute_agent(task: dict):
    """执行 Agent 任务（带追踪）"""

    with tracer_instance.trace_agent_execution(
        agent_id="agent-api",
        task_id=task.get("task_id", "unknown"),
        task_type=task.get("type", "general")
    ) as span:

        # 添加任务详情
        span.set_attribute("task.priority", task.get("priority", "normal"))

        # 模拟 LLM 调用
        with tracer_instance.trace_llm_call(
            model="gpt-4",
            prompt_length=len(task.get("prompt", ""))
        ) as llm_span:
            await asyncio.sleep(0.5)  # 模拟 LLM 调用
            llm_span.set_attribute("llm.total_tokens", 250)

        # 模拟工具调用
        if task.get("use_tools"):
            with tracer_instance.trace_tool_call(
                tool_name=task.get("tool", "default_tool")
            ):
                await asyncio.sleep(0.2)

        return {
            "status": "success",
            "task_id": task.get("task_id"),
            "result": "Task completed"
        }


@app.get("/health")
async def health_check():
    """健康检查（不追踪）"""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("启动 AI Agent API (带分布式追踪)")
    print("访问 http://localhost:8000/docs 查看 API 文档")
    print("访问 http://localhost:16686 查看 Jaeger 追踪")

    uvicorn.run(app, host="0.0.0.0", port=8000)
