"""
AI Agent API 主应用
FastAPI 应用入口文件
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Agent API",
    description="AI Agent 部署示例应用",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每个请求的日志"""
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录日志
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s"
    )

    return response


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to AI Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "ai-agent-api",
        "version": "1.0.0"
    }


@app.get("/api/v1/status")
async def api_status():
    """API 状态检查"""
    return {
        "api_version": "v1",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "agent": "/api/v1/agent"
        }
    }


@app.post("/api/v1/agent")
async def agent_endpoint(request: dict):
    """AI Agent 处理端点"""
    logger.info("agent_request_received", query=request.get("query"))

    # 这里实现实际的 AI Agent 逻辑
    query = request.get("query", "")

    return {
        "status": "success",
        "query": query,
        "response": f"已处理查询: {query}",
        "model": "gpt-4",
        "timestamp": time.time()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
