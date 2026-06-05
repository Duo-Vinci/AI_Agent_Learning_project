"""
Prometheus 指标收集器
提供完整的 AI Agent 监控指标收集功能
"""

from prometheus_client import Counter, Histogram, Gauge, Info, Summary
from prometheus_client import start_http_server, generate_latest
from prometheus_client import CollectorRegistry
import time
from typing import Dict, Optional
from functools import wraps
import asyncio


# 创建指标注册表
registry = CollectorRegistry()

# ============= 请求相关指标 =============

# 请求总数计数器
agent_requests_total = Counter(
    'agent_requests_total',
    'AI Agent 请求总数',
    ['agent_id', 'status', 'task_type'],  # status: success/error, task_type: 任务类型
    registry=registry
)

# 请求持续时间直方图
agent_request_duration_seconds = Histogram(
    'agent_request_duration_seconds',
    'Agent 请求处理时长（秒）',
    ['agent_id', 'task_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],  # 分桶：100ms 到 5分钟
    registry=registry
)

# 当前活跃 Agent 数量
active_agents = Gauge(
    'active_agents',
    '当前正在执行任务的 Agent 数量',
    registry=registry
)

# Agent 队列长度
agent_queue_length = Gauge(
    'agent_queue_length',
    'Agent 任务队列中等待处理的任务数',
    ['priority'],  # 按优先级分类
    registry=registry
)

# ============= LLM 相关指标 =============

# LLM Token 使用量
llm_tokens_total = Counter(
    'llm_tokens_total',
    'LLM Token 总使用量',
    ['model', 'type'],  # type: prompt/completion
    registry=registry
)

# LLM 调用次数
llm_calls_total = Counter(
    'llm_calls_total',
    'LLM API 调用总次数',
    ['model', 'status'],  # status: success/error/timeout
    registry=registry
)

# LLM 调用延迟
llm_call_duration_seconds = Histogram(
    'llm_call_duration_seconds',
    'LLM API 调用延迟（秒）',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0],
    registry=registry
)

# LLM 成本
llm_cost_total = Counter(
    'llm_cost_total',
    'LLM 使用总成本（美元）',
    ['model'],
    registry=registry
)

# ============= 工具调用指标 =============

# 工具调用次数
tool_calls_total = Counter(
    'tool_calls_total',
    'Agent 工具调用总次数',
    ['tool_name', 'status'],
    registry=registry
)

# 工具调用延迟
tool_call_duration_seconds = Histogram(
    'tool_call_duration_seconds',
    '工具调用延迟（秒）',
    ['tool_name'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
    registry=registry
)

# ============= 缓存相关指标 =============

# 缓存命中/未命中
cache_operations_total = Counter(
    'cache_operations_total',
    '缓存操作总数',
    ['operation', 'result'],  # operation: get/set, result: hit/miss/error
    registry=registry
)

# 缓存大小
cache_size_bytes = Gauge(
    'cache_size_bytes',
    '缓存占用大小（字节）',
    ['cache_type'],
    registry=registry
)

# ============= 系统资源指标 =============

# 内存使用
process_memory_bytes = Gauge(
    'process_memory_bytes',
    '进程内存使用（字节）',
    registry=registry
)

# CPU 使用率
process_cpu_percent = Gauge(
    'process_cpu_percent',
    '进程 CPU 使用率（百分比）',
    registry=registry
)

# Agent 信息
agent_info = Info(
    'agent_info',
    'Agent 系统信息',
    registry=registry
)


class MetricsCollector:
    """指标收集器"""

    def __init__(self, port: int = 8001):
        """
        初始化指标收集器

        Args:
            port: Prometheus metrics 暴露端口
        """
        self.port = port
        self.registry = registry
        self._server_started = False

    def start_server(self):
        """启动 Prometheus HTTP 服务器"""
        if not self._server_started:
            start_http_server(self.port, registry=self.registry)
            self._server_started = True
            print(f"Metrics server started on port {self.port}")

    def record_request(
        self,
        agent_id: str,
        status: str,
        duration: float,
        task_type: str = "general"
    ):
        """
        记录 Agent 请求

        Args:
            agent_id: Agent 标识符
            status: 请求状态 (success/error)
            duration: 请求处理时长（秒）
            task_type: 任务类型
        """
        agent_requests_total.labels(
            agent_id=agent_id,
            status=status,
            task_type=task_type
        ).inc()

        agent_request_duration_seconds.labels(
            agent_id=agent_id,
            task_type=task_type
        ).observe(duration)

    def record_llm_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration: float,
        status: str = "success"
    ):
        """
        记录 LLM 使用情况

        Args:
            model: 模型名称
            prompt_tokens: 提示词 Token 数
            completion_tokens: 完成 Token 数
            duration: 调用时长
            status: 调用状态
        """
        # 记录 Token 使用
        llm_tokens_total.labels(model=model, type='prompt').inc(prompt_tokens)
        llm_tokens_total.labels(model=model, type='completion').inc(completion_tokens)

        # 记录调用次数
        llm_calls_total.labels(model=model, status=status).inc()

        # 记录延迟
        llm_call_duration_seconds.labels(model=model).observe(duration)

        # 计算并记录成本
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        llm_cost_total.labels(model=model).inc(cost)

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        计算 LLM 调用成本

        价格表（每千 Token）：
        - GPT-4: $0.03 (prompt) / $0.06 (completion)
        - GPT-3.5-turbo: $0.0015 (prompt) / $0.002 (completion)
        - Claude-3-opus: $0.015 (prompt) / $0.075 (completion)
        - Claude-3-sonnet: $0.003 (prompt) / $0.015 (completion)
        - DeepSeek-chat: $0.0001 (prompt) / $0.0002 (completion)
        """
        pricing = {
            'gpt-4': {'prompt': 0.03/1000, 'completion': 0.06/1000},
            'gpt-4-turbo': {'prompt': 0.01/1000, 'completion': 0.03/1000},
            'gpt-3.5-turbo': {'prompt': 0.0015/1000, 'completion': 0.002/1000},
            'claude-3-opus': {'prompt': 0.015/1000, 'completion': 0.075/1000},
            'claude-3-sonnet': {'prompt': 0.003/1000, 'completion': 0.015/1000},
            'claude-3-haiku': {'prompt': 0.00025/1000, 'completion': 0.00125/1000},
            'deepseek-chat': {'prompt': 0.0001/1000, 'completion': 0.0002/1000},
        }

        # 默认使用 GPT-4 价格
        rates = pricing.get(model.lower(), pricing['gpt-4'])

        cost = (prompt_tokens * rates['prompt'] +
                completion_tokens * rates['completion'])

        return cost

    def record_tool_call(self, tool_name: str, duration: float, status: str = "success"):
        """记录工具调用"""
        tool_calls_total.labels(tool_name=tool_name, status=status).inc()
        tool_call_duration_seconds.labels(tool_name=tool_name).observe(duration)

    def record_cache_operation(self, operation: str, result: str):
        """
        记录缓存操作

        Args:
            operation: 操作类型 (get/set)
            result: 操作结果 (hit/miss/error)
        """
        cache_operations_total.labels(operation=operation, result=result).inc()

    def update_system_metrics(self):
        """更新系统资源指标"""
        import psutil

        process = psutil.Process()

        # 内存使用
        mem_info = process.memory_info()
        process_memory_bytes.set(mem_info.rss)

        # CPU 使用率
        cpu_percent = process.cpu_percent(interval=1)
        process_cpu_percent.set(cpu_percent)

    def set_agent_info(self, version: str, environment: str, **kwargs):
        """设置 Agent 信息"""
        info_dict = {
            'version': version,
            'environment': environment,
            **kwargs
        }
        agent_info.info(info_dict)

    def get_metrics(self) -> bytes:
        """获取所有指标（Prometheus 格式）"""
        return generate_latest(self.registry)


# 装饰器：自动记录请求指标
def track_agent_request(agent_id: str, task_type: str = "general"):
    """
    装饰器：自动追踪 Agent 请求

    用法：
        @track_agent_request("my_agent", "data_analysis")
        async def process_task(data):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            active_agents.inc()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                collector.record_request(agent_id, 'success', duration, task_type)

                return result

            except Exception as e:
                duration = time.time() - start_time
                collector.record_request(agent_id, 'error', duration, task_type)
                raise

            finally:
                active_agents.dec()

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            active_agents.inc()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                collector.record_request(agent_id, 'success', duration, task_type)

                return result

            except Exception as e:
                duration = time.time() - start_time
                collector.record_request(agent_id, 'error', duration, task_type)
                raise

            finally:
                active_agents.dec()

        # 根据函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 装饰器：自动记录 LLM 调用
def track_llm_call(model: str):
    """
    装饰器：自动追踪 LLM 调用

    用法：
        @track_llm_call("gpt-4")
        async def call_llm(prompt):
            ...
            return {"usage": {"prompt_tokens": 100, "completion_tokens": 50}}
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # 从结果中提取 Token 信息
                if isinstance(result, dict) and 'usage' in result:
                    usage = result['usage']
                    collector.record_llm_usage(
                        model=model,
                        prompt_tokens=usage.get('prompt_tokens', 0),
                        completion_tokens=usage.get('completion_tokens', 0),
                        duration=duration,
                        status='success'
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time
                llm_calls_total.labels(model=model, status='error').inc()
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if isinstance(result, dict) and 'usage' in result:
                    usage = result['usage']
                    collector.record_llm_usage(
                        model=model,
                        prompt_tokens=usage.get('prompt_tokens', 0),
                        completion_tokens=usage.get('completion_tokens', 0),
                        duration=duration,
                        status='success'
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time
                llm_calls_total.labels(model=model, status='error').inc()
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 全局指标收集器实例
collector = MetricsCollector(port=8001)


# 示例使用
if __name__ == "__main__":
    import random

    # 启动指标服务器
    collector.start_server()

    # 设置 Agent 信息
    collector.set_agent_info(
        version="1.0.0",
        environment="production",
        python_version="3.11"
    )

    print("模拟生成指标数据...")

    # 模拟一些指标数据
    agents = ["agent-1", "agent-2", "agent-3"]
    models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]

    for _ in range(100):
        agent_id = random.choice(agents)
        model = random.choice(models)

        # 模拟请求
        status = "success" if random.random() > 0.1 else "error"
        duration = random.uniform(0.5, 30.0)
        collector.record_request(agent_id, status, duration, "data_analysis")

        # 模拟 LLM 调用
        if status == "success":
            collector.record_llm_usage(
                model=model,
                prompt_tokens=random.randint(100, 2000),
                completion_tokens=random.randint(50, 1000),
                duration=random.uniform(1.0, 10.0)
            )

        time.sleep(0.1)

    # 更新系统指标
    collector.update_system_metrics()

    print(f"\n指标已生成！访问 http://localhost:8001 查看 Prometheus 指标")
    print("按 Ctrl+C 退出...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n服务已停止")
