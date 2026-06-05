"""
性能测试和负载测试
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self):
        self.response_times: List[float] = []
        self.errors: List[Exception] = []

    def record_response_time(self, duration: float):
        """记录响应时间"""
        self.response_times.append(duration)

    def record_error(self, error: Exception):
        """记录错误"""
        self.errors.append(error)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.response_times:
            return {
                "count": 0,
                "errors": len(self.errors),
                "error_rate": 1.0 if self.errors else 0.0
            }

        return {
            "count": len(self.response_times),
            "errors": len(self.errors),
            "error_rate": len(self.errors) / (len(self.response_times) + len(self.errors)),
            "min": min(self.response_times),
            "max": max(self.response_times),
            "mean": statistics.mean(self.response_times),
            "median": statistics.median(self.response_times),
            "p95": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else max(self.response_times),
            "p99": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else max(self.response_times),
        }


class MockAgent:
    """模拟Agent用于性能测试"""

    def __init__(self, latency: float = 0.1, error_rate: float = 0.0):
        """
        初始化Mock Agent

        Args:
            latency: 模拟延迟（秒）
            error_rate: 错误率（0.0-1.0）
        """
        self.latency = latency
        self.error_rate = error_rate
        self.call_count = 0

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        self.call_count += 1

        # 模拟延迟
        await asyncio.sleep(self.latency)

        # 模拟错误
        import random
        if random.random() < self.error_rate:
            raise Exception("模拟错误")

        return {
            "status": "success",
            "data": f"处理结果 #{self.call_count}"
        }


@pytest.mark.performance
class TestPerformance:
    """性能测试"""

    @pytest.mark.asyncio
    async def test_response_time(self):
        """测试响应时间"""
        agent = MockAgent(latency=0.05)
        metrics = PerformanceMetrics()

        # 执行100次请求
        for _ in range(100):
            start_time = time.time()
            try:
                await agent.execute({"query": "test"})
                duration = time.time() - start_time
                metrics.record_response_time(duration)
            except Exception as e:
                metrics.record_error(e)

        stats = metrics.get_stats()
        print(f"\n性能统计:")
        print(f"  请求数: {stats['count']}")
        print(f"  平均响应时间: {stats['mean']*1000:.2f}ms")
        print(f"  中位数: {stats['median']*1000:.2f}ms")
        print(f"  P95: {stats['p95']*1000:.2f}ms")
        print(f"  最小值: {stats['min']*1000:.2f}ms")
        print(f"  最大值: {stats['max']*1000:.2f}ms")

        # 验证性能要求
        assert stats['mean'] < 0.1  # 平均响应时间小于100ms
        assert stats['p95'] < 0.15  # P95小于150ms

    @pytest.mark.asyncio
    async def test_throughput(self):
        """测试吞吐量"""
        agent = MockAgent(latency=0.01)
        duration = 5  # 测试5秒

        start_time = time.time()
        completed = 0

        while time.time() - start_time < duration:
            try:
                await agent.execute({"query": "throughput test"})
                completed += 1
            except Exception:
                pass

        elapsed = time.time() - start_time
        throughput = completed / elapsed

        print(f"\n吞吐量测试:")
        print(f"  总请求数: {completed}")
        print(f"  测试时长: {elapsed:.2f}秒")
        print(f"  吞吐量: {throughput:.2f} req/s")

        # 验证吞吐量要求
        assert throughput > 50  # 至少每秒50个请求

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求"""
        agent = MockAgent(latency=0.1)
        concurrency_levels = [10, 50, 100]

        for concurrency in concurrency_levels:
            metrics = PerformanceMetrics()

            # 创建并发任务
            tasks = [agent.execute({"query": f"req{i}"}) for i in range(concurrency)]

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time

            # 统计结果
            for result in results:
                if isinstance(result, Exception):
                    metrics.record_error(result)
                else:
                    metrics.record_response_time(0.1)  # 估计值

            stats = metrics.get_stats()
            print(f"\n并发度 {concurrency}:")
            print(f"  总耗时: {total_time:.2f}秒")
            print(f"  成功数: {stats['count']}")
            print(f"  失败数: {stats['errors']}")


@pytest.mark.load
class TestLoad:
    """负载测试"""

    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """测试持续负载"""
        agent = MockAgent(latency=0.05, error_rate=0.01)
        metrics = PerformanceMetrics()

        duration = 10  # 10秒持续负载
        start_time = time.time()

        while time.time() - start_time < duration:
            request_start = time.time()
            try:
                await agent.execute({"query": "sustained load"})
                request_duration = time.time() - request_start
                metrics.record_response_time(request_duration)
            except Exception as e:
                metrics.record_error(e)

        stats = metrics.get_stats()
        print(f"\n持续负载测试 ({duration}秒):")
        print(f"  总请求数: {stats['count'] + stats['errors']}")
        print(f"  成功数: {stats['count']}")
        print(f"  失败数: {stats['errors']}")
        print(f"  错误率: {stats['error_rate']*100:.2f}%")
        print(f"  平均响应时间: {stats['mean']*1000:.2f}ms")

        # 验证稳定性
        assert stats['error_rate'] < 0.05  # 错误率应小于5%
        assert stats['mean'] < 0.1  # 平均响应时间应保持在100ms以下

    @pytest.mark.asyncio
    async def test_spike_load(self):
        """测试突发负载"""
        agent = MockAgent(latency=0.05)
        metrics = PerformanceMetrics()

        # 突然发送大量并发请求
        spike_size = 200
        tasks = [agent.execute({"query": f"spike{i}"}) for i in range(spike_size)]

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        spike_duration = time.time() - start_time

        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = spike_size - successful

        print(f"\n突发负载测试:")
        print(f"  突发请求数: {spike_size}")
        print(f"  处理时长: {spike_duration:.2f}秒")
        print(f"  成功数: {successful}")
        print(f"  失败数: {failed}")
        print(f"  成功率: {successful/spike_size*100:.2f}%")

        # 系统应该能处理突发负载
        assert successful / spike_size > 0.9  # 至少90%成功率

    @pytest.mark.asyncio
    async def test_gradual_ramp_up(self):
        """测试逐步增加负载"""
        agent = MockAgent(latency=0.05)

        ramp_stages = [10, 30, 50, 100]
        results = {}

        for stage_concurrency in ramp_stages:
            metrics = PerformanceMetrics()

            tasks = [
                agent.execute({"query": f"ramp{i}"})
                for i in range(stage_concurrency)
            ]

            start_time = time.time()
            stage_results = await asyncio.gather(*tasks, return_exceptions=True)
            stage_duration = time.time() - start_time

            successful = sum(1 for r in stage_results if not isinstance(r, Exception))

            results[stage_concurrency] = {
                "duration": stage_duration,
                "successful": successful,
                "total": stage_concurrency
            }

        print(f"\n逐步增加负载测试:")
        for concurrency, result in results.items():
            success_rate = result['successful'] / result['total'] * 100
            print(f"  并发度 {concurrency}: {result['successful']}/{result['total']} "
                  f"({success_rate:.1f}%) - {result['duration']:.2f}秒")

        # 验证系统能够扩展
        for result in results.values():
            assert result['successful'] / result['total'] > 0.95


@pytest.mark.stress
class TestStress:
    """压力测试"""

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """测试内存使用"""
        import tracemalloc

        tracemalloc.start()
        agent = MockAgent(latency=0.01)

        # 执行大量请求
        for _ in range(1000):
            await agent.execute({"query": "memory test"})

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\n内存使用:")
        print(f"  当前: {current / 1024 / 1024:.2f} MB")
        print(f"  峰值: {peak / 1024 / 1024:.2f} MB")

        # 验证内存使用合理
        assert peak / 1024 / 1024 < 100  # 峰值应小于100MB

    @pytest.mark.asyncio
    async def test_error_rate_under_load(self):
        """测试负载下的错误率"""
        agent = MockAgent(latency=0.05, error_rate=0.02)
        metrics = PerformanceMetrics()

        # 高并发请求
        tasks = [agent.execute({"query": f"error{i}"}) for i in range(500)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                metrics.record_error(result)
            else:
                metrics.record_response_time(0.05)

        stats = metrics.get_stats()
        print(f"\n错误率测试:")
        print(f"  总请求: {stats['count'] + stats['errors']}")
        print(f"  成功: {stats['count']}")
        print(f"  失败: {stats['errors']}")
        print(f"  错误率: {stats['error_rate']*100:.2f}%")

        # 验证错误率在可接受范围内
        assert stats['error_rate'] < 0.05  # 错误率应小于5%


if __name__ == "__main__":
    print("=" * 50)
    print("性能和负载测试")
    print("=" * 50)
    print("\n使用命令运行测试:")
    print("  性能测试: pytest test_performance.py -v -m performance")
    print("  负载测试: pytest test_performance.py -v -m load")
    print("  压力测试: pytest test_performance.py -v -m stress")
    print("  全部测试: pytest test_performance.py -v")

    pytest.main([__file__, "-v", "-s"])
