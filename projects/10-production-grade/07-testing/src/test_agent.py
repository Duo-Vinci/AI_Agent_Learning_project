"""
单元测试示例
测试Agent基础功能
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


# 假设我们的Agent类（简化版）
class SimpleAgent:
    """简化的Agent用于测试"""

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        query = input_data.get("query", "")

        if not query:
            raise ValueError("query不能为空")

        # 模拟LLM调用
        result = {
            "query": query,
            "response": f"处理结果: {query}",
            "agent_id": self.agent_id
        }

        return result


class TestSimpleAgent:
    """测试SimpleAgent类"""

    @pytest.fixture
    def agent(self):
        """创建测试用Agent实例"""
        config = {
            "model": "gpt-4",
            "temperature": 0.7
        }
        return SimpleAgent(agent_id="test-agent", config=config)

    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        """测试成功执行"""
        input_data = {"query": "什么是AI Agent？"}

        result = await agent.execute(input_data)

        assert result is not None
        assert "response" in result
        assert result["query"] == "什么是AI Agent？"
        assert result["agent_id"] == "test-agent"

    @pytest.mark.asyncio
    async def test_execute_empty_query(self, agent):
        """测试空查询"""
        input_data = {"query": ""}

        with pytest.raises(ValueError, match="query不能为空"):
            await agent.execute(input_data)

    @pytest.mark.asyncio
    async def test_execute_missing_query(self, agent):
        """测试缺少query字段"""
        input_data = {}

        with pytest.raises(ValueError):
            await agent.execute(input_data)


class TestAgentWithMock:
    """使用Mock测试Agent"""

    @pytest.fixture
    def mock_llm(self):
        """创建Mock LLM"""
        llm = AsyncMock()
        llm.agenerate.return_value = "这是Mock响应"
        return llm

    @pytest.mark.asyncio
    async def test_agent_with_mock_llm(self, mock_llm):
        """测试使用Mock LLM的Agent"""
        # 创建使用Mock LLM的Agent
        agent = SimpleAgent(agent_id="mock-agent", config={})

        # 执行任务
        result = await agent.execute({"query": "测试查询"})

        # 验证结果
        assert result is not None
        assert "response" in result


def test_agent_configuration():
    """测试Agent配置"""
    config = {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    }

    agent = SimpleAgent(agent_id="config-test", config=config)

    assert agent.agent_id == "config-test"
    assert agent.config["model"] == "gpt-4"
    assert agent.config["temperature"] == 0.7


class TestAgentErrorHandling:
    """测试错误处理"""

    @pytest.fixture
    def agent(self):
        return SimpleAgent(agent_id="error-test", config={})

    @pytest.mark.asyncio
    async def test_invalid_input_type(self, agent):
        """测试无效输入类型"""
        # 传入非字典类型应该引发错误
        with pytest.raises((TypeError, AttributeError)):
            await agent.execute("invalid input")

    @pytest.mark.asyncio
    async def test_large_query(self, agent):
        """测试超长查询"""
        # 创建一个很长的查询
        long_query = "x" * 10000

        result = await agent.execute({"query": long_query})

        # 应该能处理，但可能会截断
        assert result is not None


@pytest.mark.parametrize("query,expected_keyword", [
    ("什么是AI？", "AI"),
    ("Python编程", "Python"),
    ("机器学习基础", "机器学习"),
])
@pytest.mark.asyncio
async def test_agent_with_different_queries(query, expected_keyword):
    """参数化测试：测试不同的查询"""
    agent = SimpleAgent(agent_id="param-test", config={})

    result = await agent.execute({"query": query})

    assert expected_keyword in result["response"] or expected_keyword in result["query"]


class TestAsyncOperations:
    """测试异步操作"""

    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """测试并发执行多个Agent"""
        agents = [
            SimpleAgent(agent_id=f"agent-{i}", config={})
            for i in range(3)
        ]

        # 并发执行
        tasks = [
            agent.execute({"query": f"查询{i}"})
            for i, agent in enumerate(agents)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["query"] == f"查询{i}"


# 运行测试的主函数
if __name__ == "__main__":
    print("=" * 50)
    print("运行单元测试")
    print("=" * 50)
    print("\n使用命令运行测试: pytest test_agent.py -v")
    print("查看覆盖率: pytest test_agent.py --cov --cov-report=html")

    # 运行pytest
    pytest.main([__file__, "-v", "-s"])
