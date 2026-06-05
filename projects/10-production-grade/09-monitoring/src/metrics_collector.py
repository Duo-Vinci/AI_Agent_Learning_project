"""
监控指标收集
基于Prometheus的指标系统
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from typing import Dict, Any, Optional
import time
import logging
from functools import wraps


logger = logging.getLogger(__name__)


# ========== Prometheus指标定义 ==========

# 请求计数器
agent_requests_total = Counter(
    'agent_requests_total',
    'Total number of agent requests',
    ['agent_id', 'status']
)

# 请求延迟直方图
agent_request_duration_seconds = Histogram(
    'agent_request_duration_seconds',
    'Agent request duration in seconds',
    ['agent_id'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# LLM Token使用计数器
llm_tokens_used_total = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: prompt or completion
)

# 缓存命中率
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_level']  # L1, L2
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses'
)

# 当前活跃请求数
active_requests = Gauge(
    'active_requests',
    'Current number of active requests',
    ['agent_id']
)

# 错误计数器
errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'agent_id']
)

# 系统资源指标
memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)


# ========== 指标收集器类 ==========

class MetricsCollector:
    """
    指标收集器
    提供统一的指标收集接口
    """

    def __init__(self):
        """初始化指标收集器"""
        self.start_time = time.time()

    def record_request(self, agent_id: str, status: str):
        """
        记录请求

        Args:
            agent_id: Agent标识
            status: 状态（success/error）
        """
        agent_requests_total.labels(agent_id=agent_id, status=status).inc()

    def record_duration(self, agent_id: str, duration: float):
        """
        记录请求延迟

        Args:
            agent_id: Agent标识
            duration: 延迟时间（秒）
        """
        agent_request_duration_seconds.labels(agent_id=agent_id).observe(duration)

    def record_llm_tokens(self, model: str, prompt_tokens: int, completion_tokens: int):
        """
        记录LLM Token使用

        Args:
            model: 模型名称
            prompt_tokens: 提示词Token数
            completion_tokens: 完成Token数
        """
        llm_tokens_used_total.labels(model=model, type='prompt').inc(prompt_tokens)
        llm_tokens_used_total.labels(model=model, type='completion').inc(completion_tokens)

    def record_cache_hit(self, cache_level: str = 'L1'):
        """
        记录缓存命中

        Args:
            cache_level: 缓存层级（L1/L2）
        """
        cache_hits_total.labels(cache_level=cache_level).inc()

    def record_cache_miss(self):
        """记录缓存未命中"""
        cache_misses_total.inc()

    def record_error(self, error_type: str, agent_id: str = 'unknown'):
        """
        记录错误

        Args:
            error_type: 错误类型
            agent_id: Agent标识
        """
        errors_total.labels(error_type=error_type, agent_id=agent_id).inc()

    def set_active_requests(self, agent_id: str, count: int):
        """
        设置活跃请求数

        Args:
            agent_id: Agent标识
            count: 请求数量
        """
        active_requests.labels(agent_id=agent_id).set(count)

    def update_system_metrics(self):
        """更新系统资源指标"""
        try:
            import psutil

            # 内存使用
            memory = psutil.Process().memory_info().rss
            memory_usage_bytes.set(memory)

            # CPU使用率
            cpu = psutil.Process().cpu_percent(interval=0.1)
            cpu_usage_percent.set(cpu)

        except ImportError:
            logger.warning("psutil未安装，无法收集系统指标")
        except Exception as e:
            logger.error(f"更新系统指标失败: {e}")

    def get_uptime(self) -> float:
        """
        获取服务运行时间

        Returns:
            运行时间（秒）
        """
        return time.time() - self.start_time

    def export_metrics(self) -> str:
        """
        导出Prometheus格式的指标

        Returns:
            指标文本
        """
        return generate_latest(REGISTRY).decode('utf-8')


# 全局指标收集器实例
metrics = MetricsCollector()


# ========== 装饰器 ==========

def track_request(agent_id: Optional[str] = None):
    """
    请求追踪装饰器

    Args:
        agent_id: Agent标识（可选）

    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 获取agent_id
            _agent_id = agent_id or kwargs.get('agent_id', 'unknown')

            # 增加活跃请求计数
            metrics.set_active_requests(_agent_id, 1)

            start_time = time.time()
            status = 'success'

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                metrics.record_error(type(e).__name__, _agent_id)
                raise
            finally:
                # 记录指标
                duration = time.time() - start_time
                metrics.record_request(_agent_id, status)
                metrics.record_duration(_agent_id, duration)

                # 减少活跃请求计数
                metrics.set_active_requests(_agent_id, 0)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            _agent_id = agent_id or kwargs.get('agent_id', 'unknown')
            metrics.set_active_requests(_agent_id, 1)

            start_time = time.time()
            status = 'success'

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                metrics.record_error(type(e).__name__, _agent_id)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(_agent_id, status)
                metrics.record_duration(_agent_id, duration)
                metrics.set_active_requests(_agent_id, 0)

        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ========== 指标端点 ==========

def create_metrics_endpoint():
    """
    创建Prometheus指标端点
    适用于FastAPI等Web框架
    """
    from fastapi import Response

    async def metrics_endpoint():
        """指标端点"""
        metrics.update_system_metrics()
        return Response(
            content=metrics.export_metrics(),
            media_type="text/plain"
        )

    return metrics_endpoint


# ========== 使用示例 ==========

if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    print("=" * 50)
    print("监控指标收集示例")
    print("=" * 50)

    # 1. 基础指标记录
    print("\n1. 基础指标记录:")
    metrics.record_request('research-agent', 'success')
    metrics.record_request('research-agent', 'success')
    metrics.record_request('research-agent', 'error')
    metrics.record_duration('research-agent', 1.5)
    print("   ✓ 已记录请求和延迟指标")

    # 2. LLM Token记录
    print("\n2. LLM Token使用记录:")
    metrics.record_llm_tokens('gpt-4', prompt_tokens=100, completion_tokens=200)
    metrics.record_llm_tokens('gpt-4', prompt_tokens=150, completion_tokens=250)
    print("   ✓ 已记录Token使用")

    # 3. 缓存指标
    print("\n3. 缓存指标:")
    metrics.record_cache_hit('L1')
    metrics.record_cache_hit('L1')
    metrics.record_cache_hit('L2')
    metrics.record_cache_miss()
    print("   ✓ 已记录缓存命中和未命中")

    # 4. 错误记录
    print("\n4. 错误记录:")
    metrics.record_error('ValueError', 'writer-agent')
    metrics.record_error('TimeoutError', 'writer-agent')
    print("   ✓ 已记录错误")

    # 5. 系统指标
    print("\n5. 系统资源指标:")
    metrics.update_system_metrics()
    print("   ✓ 已更新系统指标")

    # 6. 使用装饰器
    print("\n6. 使用装饰器追踪请求:")

    @track_request(agent_id='test-agent')
    async def test_operation():
        """测试操作"""
        await asyncio.sleep(0.1)
        return "成功"

    asyncio.run(test_operation())
    print("   ✓ 装饰器已自动记录指标")

    # 7. 导出指标
    print("\n7. 导出Prometheus指标:")
    print("-" * 50)
    metrics_output = metrics.export_metrics()
    # 只显示前几行
    lines = metrics_output.split('\n')[:20]
    for line in lines:
        if line and not line.startswith('#'):
            print(f"   {line}")
    print(f"   ... (共 {len(metrics_output.split(chr(10)))} 行)")
    print("-" * 50)

    # 8. 运行时间
    print(f"\n8. 服务运行时间: {metrics.get_uptime():.2f} 秒")

    print("\n" + "=" * 50)
    print("提示:")
    print("  - 可以通过 /metrics 端点暴露指标给Prometheus")
    print("  - 配置Prometheus抓取: http://your-service:8000/metrics")
    print("  - 使用Grafana可视化这些指标")
    print("=" * 50)
