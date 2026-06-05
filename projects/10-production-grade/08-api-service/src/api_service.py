"""
FastAPI服务
提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import time
import uuid
from datetime import datetime
import logging

# 初始化FastAPI应用
app = FastAPI(
    title="AI Agent API",
    version="1.0.0",
    description="生产级AI Agent服务API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== 数据模型 ==========

class AgentRequest(BaseModel):
    """Agent执行请求"""
    agent_id: str = Field(..., description="Agent标识")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    timeout: Optional[int] = Field(30, description="超时时间（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "research-agent",
                "input_data": {"query": "什么是AI Agent？"},
                "timeout": 30
            }
        }


class AgentResponse(BaseModel):
    """Agent执行响应"""
    request_id: str = Field(..., description="请求ID")
    agent_id: str = Field(..., description="Agent标识")
    status: str = Field(..., description="执行状态")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间（秒）")
    timestamp: str = Field(..., description="时间戳")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    version: str
    uptime: float


# ========== 模拟的Agent注册表 ==========

class MockAgent:
    """模拟Agent"""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        # 模拟处理
        import asyncio
        await asyncio.sleep(0.1)

        query = input_data.get("query", "")
        return {
            "query": query,
            "response": f"这是对'{query}'的响应",
            "timestamp": datetime.utcnow().isoformat()
        }


# Agent注册表
agent_registry: Dict[str, MockAgent] = {
    "research-agent": MockAgent(),
    "writer-agent": MockAgent(),
    "reviewer-agent": MockAgent(),
}

# 服务启动时间
service_start_time = time.time()


# ========== 依赖注入 ==========

async def get_request_id(x_request_id: Optional[str] = Header(None)) -> str:
    """获取或生成请求ID"""
    return x_request_id or str(uuid.uuid4())


def get_agent(agent_id: str) -> MockAgent:
    """获取Agent实例"""
    agent = agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' 不存在"
        )
    return agent


# ========== 中间件 ==========

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()

    # 记录请求
    logger.info(
        f"请求开始",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None
        }
    )

    # 处理请求
    response = await call_next(request)

    # 记录响应
    duration = time.time() - start_time
    logger.info(
        f"请求完成",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "duration": duration
        }
    )

    # 添加响应头
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = str(duration)

    return response


# ========== API路由 ==========

@app.get("/", tags=["基础"])
async def root():
    """根路径"""
    return {
        "message": "AI Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["基础"])
async def health_check():
    """健康检查"""
    uptime = time.time() - service_start_time
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        uptime=uptime
    )


@app.get("/agents", tags=["Agent管理"])
async def list_agents():
    """列出所有可用的Agent"""
    return {
        "agents": list(agent_registry.keys()),
        "count": len(agent_registry)
    }


@app.get("/agents/{agent_id}", tags=["Agent管理"])
async def get_agent_info(agent_id: str):
    """获取Agent信息"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' 不存在")

    return {
        "agent_id": agent_id,
        "status": "active",
        "type": "mock"
    }


@app.post("/api/v1/agents/execute", response_model=AgentResponse, tags=["Agent执行"])
async def execute_agent(
    request: AgentRequest,
    request_id: str = Depends(get_request_id)
):
    """
    执行Agent任务

    - **agent_id**: Agent标识
    - **input_data**: 输入数据
    - **timeout**: 超时时间（可选）
    """
    start_time = time.time()

    try:
        logger.info(
            f"执行Agent: {request.agent_id}",
            extra={
                "request_id": request_id,
                "agent_id": request.agent_id
            }
        )

        # 获取Agent
        agent = get_agent(request.agent_id)

        # 执行任务
        result = await agent.execute(request.input_data)

        execution_time = time.time() - start_time

        logger.info(
            f"Agent执行成功",
            extra={
                "request_id": request_id,
                "agent_id": request.agent_id,
                "execution_time": execution_time
            }
        )

        return AgentResponse(
            request_id=request_id,
            agent_id=request.agent_id,
            status="success",
            result=result,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time

        logger.error(
            f"Agent执行失败: {str(e)}",
            extra={
                "request_id": request_id,
                "agent_id": request.agent_id,
                "error": str(e)
            },
            exc_info=True
        )

        return AgentResponse(
            request_id=request_id,
            agent_id=request.agent_id,
            status="error",
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )


@app.get("/api/v1/metrics", tags=["监控"])
async def get_metrics():
    """获取服务指标"""
    uptime = time.time() - service_start_time

    return {
        "service": {
            "uptime": uptime,
            "status": "running"
        },
        "agents": {
            "total": len(agent_registry),
            "active": len(agent_registry)
        }
    }


# ========== 异常处理 ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ========== 启动和关闭事件 ==========

@app.on_event("startup")
async def startup_event():
    """服务启动事件"""
    logger.info("AI Agent API 服务启动")


@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭事件"""
    logger.info("AI Agent API 服务关闭")


# ========== 运行服务 ==========

if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("启动 AI Agent API 服务")
    print("=" * 50)
    print("\n访问地址:")
    print("  API文档: http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
