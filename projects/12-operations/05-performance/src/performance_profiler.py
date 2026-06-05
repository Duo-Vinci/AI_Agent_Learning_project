"""
性能分析和优化工具
支持 CPU、内存、I/O 等性能分析
"""

import cProfile
import pstats
import io
import time
import psutil
import tracemalloc
from typing import Callable, Any, Optional
from functools import wraps
from memory_profiler import profile as memory_profile
import sys


class PerformanceProfiler:
    """性能分析器"""

    def __init__(self):
        self.results = {}

    def profile_cpu(self, func: Callable) -> Callable:
        """
        CPU 性能分析装饰器

        用法:
            profiler = PerformanceProfiler()

            @profiler.profile_cpu
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.disable()

                # 生成报告
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s)
                ps.sort_stats('cumulative')
                ps.print_stats(30)  # 显示前 30 个最慢的函数

                print(f"\n{'='*60}")
                print(f"CPU 性能分析: {func.__name__}")
                print(f"{'='*60}")
                print(s.getvalue())

                # 保存结果
                self.results[func.__name__] = {
                    'type': 'cpu',
                    'stats': ps
                }

        return wrapper

    def profile_memory(self, func: Callable) -> Callable:
        """
        内存性能分析装饰器

        用法:
            @profiler.profile_memory
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracemalloc.start()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

                print(f"\n{'='*60}")
                print(f"内存分析: {func.__name__}")
                print(f"{'='*60}")
                print(f"当前内存使用: {current / 1024 / 1024:.2f} MB")
                print(f"峰值内存使用: {peak / 1024 / 1024:.2f} MB")
                print(f"进程内存增长: {end_memory - start_memory:.2f} MB")

                self.results[func.__name__] = {
                    'type': 'memory',
                    'current_mb': current / 1024 / 1024,
                    'peak_mb': peak / 1024 / 1024,
                    'delta_mb': end_memory - start_memory
                }

        return wrapper

    def profile_time(self, func: Callable) -> Callable:
        """
        时间性能分析装饰器（简单计时）

        用法:
            @profiler.profile_time
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time

                print(f"\n{'='*60}")
                print(f"执行时间: {func.__name__}")
                print(f"{'='*60}")
                print(f"耗时: {duration:.4f} 秒")

                self.results[func.__name__] = {
                    'type': 'time',
                    'duration_seconds': duration
                }

        return wrapper

    def get_system_metrics(self) -> dict:
        """获取系统性能指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total_gb': memory.total / (1024 ** 3),
                'available_gb': memory.available / (1024 ** 3),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': disk.total / (1024 ** 3),
                'used_gb': disk.used / (1024 ** 3),
                'free_gb': disk.free / (1024 ** 3),
                'percent': disk.percent
            }
        }

    def save_profile_data(self, filename: str, func_name: str):
        """保存性能分析数据到文件"""
        if func_name in self.results:
            result = self.results[func_name]
            if result['type'] == 'cpu' and 'stats' in result:
                result['stats'].dump_stats(filename)
                print(f"CPU 分析数据已保存到: {filename}")


class LLMOptimizer:
    """LLM 调用优化器"""

    def __init__(self, cache_enabled: bool = True, max_cache_size: int = 1000):
        self.cache_enabled = cache_enabled
        self.cache = {}
        self.max_cache_size = max_cache_size
        self.stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'total_tokens': 0,
            'saved_tokens': 0,
            'total_cost': 0.0,
            'saved_cost': 0.0
        }

    def _calculate_cost(self, model: str, tokens: int) -> float:
        """计算成本"""
        pricing = {
            'gpt-4': 0.03 / 1000,
            'gpt-3.5-turbo': 0.0015 / 1000,
            'claude-3-opus': 0.015 / 1000,
            'claude-3-sonnet': 0.003 / 1000,
            'deepseek-chat': 0.0001 / 1000
        }
        rate = pricing.get(model.lower(), pricing['gpt-4'])
        return tokens * rate

    def optimize_prompt(self, prompt: str) -> str:
        """
        优化 Prompt 以减少 Token 使用

        策略:
        1. 移除多余空白
        2. 使用缩写
        3. 简化表达
        """
        # 移除多余空白和换行
        optimized = ' '.join(prompt.split())

        # 常见缩写替换（谨慎使用，不要影响语义）
        replacements = {
            'please': 'pls',
            'information': 'info',
            'description': 'desc',
            'example': 'ex',
            'following': 'below'
        }

        for old, new in replacements.items():
            optimized = optimized.replace(f' {old} ', f' {new} ')

        return optimized

    def call_with_cache(
        self,
        model: str,
        prompt: str,
        llm_function: Callable,
        optimize_prompt: bool = True
    ) -> Any:
        """
        带缓存和优化的 LLM 调用

        Args:
            model: 模型名称
            prompt: 提示词
            llm_function: 实际的 LLM 调用函数
            optimize_prompt: 是否优化 prompt
        """
        self.stats['total_calls'] += 1

        # Prompt 优化
        if optimize_prompt:
            original_prompt = prompt
            prompt = self.optimize_prompt(prompt)
            saved_chars = len(original_prompt) - len(prompt)
            if saved_chars > 0:
                print(f"Prompt 优化: 节省了约 {saved_chars} 字符")

        # 缓存检查
        cache_key = hash(f"{model}:{prompt}")

        if self.cache_enabled and cache_key in self.cache:
            self.stats['cache_hits'] += 1
            cached_result = self.cache[cache_key]

            # 计算节省的成本
            saved_tokens = cached_result.get('tokens', 0)
            saved_cost = self._calculate_cost(model, saved_tokens)

            self.stats['saved_tokens'] += saved_tokens
            self.stats['saved_cost'] += saved_cost

            print(f"✓ 缓存命中! 节省 {saved_tokens} tokens (${saved_cost:.4f})")

            return cached_result['response']

        # 实际调用 LLM
        start_time = time.time()
        result = llm_function(model, prompt)
        duration = time.time() - start_time

        # 提取 token 信息
        tokens = result.get('usage', {}).get('total_tokens', 0)
        cost = self._calculate_cost(model, tokens)

        self.stats['total_tokens'] += tokens
        self.stats['total_cost'] += cost

        print(f"LLM 调用: {tokens} tokens, ${cost:.4f}, {duration:.2f}s")

        # 缓存结果
        if self.cache_enabled:
            # 限制缓存大小
            if len(self.cache) >= self.max_cache_size:
                # 删除最旧的缓存项
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]

            self.cache[cache_key] = {
                'response': result,
                'tokens': tokens,
                'timestamp': time.time()
            }

        return result

    def get_optimization_report(self) -> dict:
        """获取优化报告"""
        cache_hit_rate = (
            self.stats['cache_hits'] / max(self.stats['total_calls'], 1)
        )

        avg_tokens = (
            self.stats['total_tokens'] / max(self.stats['total_calls'], 1)
        )

        return {
            '总调用次数': self.stats['total_calls'],
            '缓存命中次数': self.stats['cache_hits'],
            '缓存命中率': f"{cache_hit_rate:.2%}",
            '总 Token 使用': self.stats['total_tokens'],
            '节省 Token': self.stats['saved_tokens'],
            '平均每次调用 Token': f"{avg_tokens:.0f}",
            '总成本': f"${self.stats['total_cost']:.4f}",
            '节省成本': f"${self.stats['saved_cost']:.4f}",
            '优化建议': self._get_recommendations()
        }

    def _get_recommendations(self) -> list:
        """生成优化建议"""
        recommendations = []

        cache_hit_rate = (
            self.stats['cache_hits'] / max(self.stats['total_calls'], 1)
        )

        if cache_hit_rate < 0.3:
            recommendations.append("缓存命中率较低，考虑增加缓存大小或优化缓存键")

        if self.stats['total_cost'] > 10:
            recommendations.append("成本较高，考虑使用更便宜的模型或减少调用频率")

        avg_tokens = (
            self.stats['total_tokens'] / max(self.stats['total_calls'], 1)
        )

        if avg_tokens > 2000:
            recommendations.append("平均 Token 使用量较高，建议优化 Prompt 长度")

        if not recommendations:
            recommendations.append("当前优化良好，继续保持")

        return recommendations


# 使用示例
if __name__ == "__main__":
    print("=== 性能分析示例 ===\n")

    profiler = PerformanceProfiler()

    # CPU 性能分析
    @profiler.profile_cpu
    def cpu_intensive_task():
        """CPU 密集型任务"""
        result = 0
        for i in range(1000000):
            result += i ** 2
        return result

    # 内存性能分析
    @profiler.profile_memory
    def memory_intensive_task():
        """内存密集型任务"""
        data = []
        for i in range(100000):
            data.append({'id': i, 'value': 'x' * 100})
        return data

    # 时间性能分析
    @profiler.profile_time
    def slow_task():
        """耗时任务"""
        time.sleep(0.5)
        return "完成"

    # 执行分析
    cpu_intensive_task()
    memory_intensive_task()
    slow_task()

    # 显示系统指标
    print("\n=== 系统性能指标 ===")
    metrics = profiler.get_system_metrics()
    print(f"CPU 使用率: {metrics['cpu']['percent']}%")
    print(f"内存使用率: {metrics['memory']['percent']}%")
    print(f"磁盘使用率: {metrics['disk']['percent']}%")

    # LLM 优化示例
    print("\n=== LLM 优化示例 ===")
    optimizer = LLMOptimizer(cache_enabled=True)

    def mock_llm_call(model: str, prompt: str):
        """模拟 LLM 调用"""
        time.sleep(0.1)
        return {
            'response': f"Response to: {prompt[:50]}...",
            'usage': {'total_tokens': len(prompt.split()) * 1.5}
        }

    # 模拟多次调用（包含重复）
    prompts = [
        "请分析这段代码的性能瓶颈",
        "请分析这段代码的性能瓶颈",  # 重复 - 应该命中缓存
        "生成一个 Python 函数来处理数据",
        "请分析这段代码的性能瓶颈",  # 再次重复
    ]

    for prompt in prompts:
        optimizer.call_with_cache(
            model="gpt-3.5-turbo",
            prompt=prompt,
            llm_function=mock_llm_call,
            optimize_prompt=True
        )
        print()

    # 显示优化报告
    print("=== 优化报告 ===")
    report = optimizer.get_optimization_report()
    for key, value in report.items():
        if key == '优化建议':
            print(f"\n{key}:")
            for rec in value:
                print(f"  - {rec}")
        else:
            print(f"{key}: {value}")
