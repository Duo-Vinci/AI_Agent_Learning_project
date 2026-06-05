"""
简单的单元测试示例
用于 CI/CD 流水线
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Welcome to AI Agent API"


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-agent-api"


def test_api_status():
    """测试 API 状态端点"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "v1"
    assert data["status"] == "operational"
    assert "endpoints" in data


def test_agent_endpoint():
    """测试 Agent 处理端点"""
    payload = {"query": "Hello, AI Agent"}
    response = client.post("/api/v1/agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["query"] == "Hello, AI Agent"
    assert "response" in data


def test_agent_endpoint_empty_query():
    """测试空查询"""
    payload = {}
    response = client.post("/api/v1/agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.parametrize("endpoint", [
    "/",
    "/health",
    "/api/v1/status"
])
def test_endpoints_accessible(endpoint):
    """测试所有端点可访问"""
    response = client.get(endpoint)
    assert response.status_code == 200


def test_cors_headers():
    """测试 CORS 头"""
    response = client.get("/health")
    assert "access-control-allow-origin" in response.headers


def test_invalid_endpoint():
    """测试无效端点"""
    response = client.get("/invalid/endpoint")
    assert response.status_code == 404
