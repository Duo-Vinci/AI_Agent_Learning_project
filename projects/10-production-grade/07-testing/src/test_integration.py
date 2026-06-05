"""
集成测试示例
测试完整的工作流
"""

import pytest
import asyncio
import time
from typing import Dict, Any


# 模拟的Agent类
class ResearchAgent:
    """研究Agent"""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行研究"""
        await asyncio.sleep(0.1)  # 模拟API调用
        query = input_data.get("query", "")
        return {
            "query": query,
            "findings": f"关于'{query}'的研究结果",
            "sources": ["source1", "source2"]
        }


class WriterAgent:
    """写作Agent"""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行写作"""
        await asyncio.sleep(0.1)  # 模拟API调用
        research_data = input_data.get("research_data", {})
        return {
            "content": f"基于研究的文章内容",
            "word_count": 500,
            "sources": research_data.get("sources", [])
        }


class ReviewerAgent:
    """审核Agent"""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行审核"""
        await asyncio.sleep(0.1)  # 模拟API调用
        content = input_data.get("content", "")
        return {
            "approved": True,
            "feedback": "内容质量良好",
            "score": 85
        }


@pytest.mark.integration
class TestAgentWorkflow:
    """测试Agent工作流"""

    @pytest.mark.asyncio
    async def test_research_to_writer_workflow(self):
        """测试研究->写作工作流"""
        # 1. 研究阶段
        researcher = ResearchAgent()
        research_result = await researcher.execute({
            "query": "AI Agent的应用场景"
        })

        assert research_result is not None
        assert "findings" in research_result
        assert len(research_result["sources"]) > 0

        # 2. 写作阶段
        writer = WriterAgent()
        article = await writer.execute({
            "research_data": research_result
        })

        assert article is not None
        assert "content" in article
        assert article["word_count"] > 0

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流：研究->写作->审核"""
        # 1. 研究
        researcher = ResearchAgent()
        research_result = await researcher.execute({
            "query": "生产级AI Agent开发"
        })

        # 2. 写作
        writer = WriterAgent()
        article = await writer.execute({
            "research_data": research_result
        })

        # 3. 审核
        reviewer = ReviewerAgent()
        review_result = await reviewer.execute({
            "content": article["content"]
        })

        # 验证完整流程
        assert research_result is not None
        assert article is not None
        assert review_result is not None
        assert review_result["approved"] is True

    @pytest.mark.asyncio
    async def test_parallel_research(self):
        """测试并行研究任务"""
        researcher = ResearchAgent()

        queries = [
            "AI Agent架构",
            "AI Agent测试策略",
            "AI Agent部署方案"
        ]

        # 并行执行多个研究任务
        tasks = [
            researcher.execute({"query": query})
            for query in queries
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == len(queries)
        for result in results:
            assert "findings" in result
            assert "sources" in result


@pytest.mark.integration
class TestSystemIntegration:
    """测试系统集成"""

    @pytest.mark.asyncio
    async def test_end_to_end_performance(self):
        """测试端到端性能"""
        start_time = time.time()

        # 执行完整工作流
        researcher = ResearchAgent()
        writer = WriterAgent()
        reviewer = ReviewerAgent()

        research = await researcher.execute({"query": "性能测试"})
        article = await writer.execute({"research_data": research})
        review = await reviewer.execute({"content": article["content"]})

        duration = time.time() - start_time

        # 验证性能要求
        assert duration < 5.0  # 整个流程应在5秒内完成
        assert review["approved"] is True

    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """测试错误恢复"""
        class FlakyAgent:
            """模拟不稳定的Agent"""

            def __init__(self):
                self.call_count = 0

            async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                self.call_count += 1

                # 第一次调用失败
                if self.call_count == 1:
                    raise Exception("临时错误")

                return {"status": "success"}

        agent = FlakyAgent()

        # 第一次调用应该失败
        with pytest.raises(Exception):
            await agent.execute({})

        # 第二次调用应该成功
        result = await agent.execute({})
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_data_flow(self):
        """测试数据流转"""
        researcher = ResearchAgent()
        writer = WriterAgent()

        # 验证数据在Agent之间正确流转
        research = await researcher.execute({"query": "数据流转测试"})
        assert "sources" in research

        article = await writer.execute({"research_data": research})
        assert article["sources"] == research["sources"]  # 数据应该正确传递


@pytest.mark.integration
@pytest.mark.slow
class TestLoadAndStress:
    """负载和压力测试"""

    @pytest.mark.asyncio
    async def test_high_concurrency(self):
        """测试高并发场景"""
        researcher = ResearchAgent()

        # 创建100个并发任务
        num_tasks = 100
        tasks = [
            researcher.execute({"query": f"查询{i}"})
            for i in range(num_tasks)
        ]

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time

        # 验证结果
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= num_tasks * 0.95  # 至少95%成功

        # 验证平均延迟
        avg_latency = duration / num_tasks
        assert avg_latency < 0.5  # 平均延迟应小于500ms

    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """测试持续负载"""
        researcher = ResearchAgent()
        writer = WriterAgent()

        # 执行30秒的持续负载
        duration = 5  # 为了测试速度，使用5秒
        start_time = time.time()
        completed_workflows = 0

        while time.time() - start_time < duration:
            try:
                research = await researcher.execute({"query": "持续负载测试"})
                article = await writer.execute({"research_data": research})
                completed_workflows += 1
            except Exception:
                pass

        throughput = completed_workflows / duration
        print(f"\n   吞吐量: {throughput:.2f} workflows/秒")

        assert completed_workflows > 0
        assert throughput > 1.0  # 应该至少每秒完成1个工作流


# Fixture配置
@pytest.fixture(scope="session")
def integration_test_setup():
    """集成测试环境设置"""
    print("\n设置集成测试环境...")
    # 这里可以设置数据库、Redis等
    yield
    print("\n清理集成测试环境...")


# 运行测试
if __name__ == "__main__":
    print("=" * 50)
    print("运行集成测试")
    print("=" * 50)
    print("\n使用命令运行测试:")
    print("  所有集成测试: pytest test_integration.py -v -m integration")
    print("  跳过慢速测试: pytest test_integration.py -v -m 'integration and not slow'")

    pytest.main([__file__, "-v", "-s", "-m", "integration"])
