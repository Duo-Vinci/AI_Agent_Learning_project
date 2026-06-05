"""
API 速率限制和流量控制
支持多种限流策略：令牌桶、滑动窗口等
"""

import time
import redis
from typing import Optional, Callable, Any
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class RateLimiter:
    """速率限制器基类"""

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        raise NotImplementedError

    def get_remaining(self, key: str) -> int:
        """获取剩余配额"""
        raise NotImplementedError


class TokenBucketLimiter(RateLimiter):
    """
    令牌桶算法限流器

    特点：
    - 平滑突发流量
    - 允许短时间内的突发请求
    """

    def __init__(self, rate: int, capacity: int):
        """
        Args:
            rate: 每秒补充的令牌数
            capacity: 桶容量（最大突发请求数）
        """
        self.rate = rate
        self.capacity = capacity
        self.buckets = {}
        self.lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        with self.lock:
            now = time.time()

            if key not in self.buckets:
                self.buckets[key] = {
                    'tokens': self.capacity,
                    'last_update': now
                }

            bucket = self.buckets[key]

            # 补充令牌
            elapsed = now - bucket['last_update']
            bucket['tokens'] = min(
                self.capacity,
                bucket['tokens'] + elapsed * self.rate
            )
            bucket['last_update'] = now

            # 尝试消费令牌
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                return True

            return False

    def get_remaining(self, key: str) -> int:
        """获取剩余令牌数"""
        if key in self.buckets:
            return int(self.buckets[key]['tokens'])
        return self.capacity


class SlidingWindowLimiter(RateLimiter):
    """
    滑动窗口算法限流器

    特点：
    - 精确控制时间窗口内的请求数
    - 更平滑的限流效果
    """

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds

            # 清理过期记录
            self.requests[key] = [
                t for t in self.requests[key] if t > cutoff
            ]

            # 检查是否超限
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True

            return False

    def get_remaining(self, key: str) -> int:
        """获取剩余配额"""
        now = time.time()
        cutoff = now - self.window_seconds

        recent_requests = [
            t for t in self.requests.get(key, []) if t > cutoff
        ]

        return max(0, self.max_requests - len(recent_requests))


class RedisRateLimiter(RateLimiter):
    """
    基于 Redis 的分布式限流器

    特点：
    - 支持分布式环境
    - 高性能
    - 适合生产环境
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int,
        window_seconds: int,
        prefix: str = "rate_limit"
    ):
        """
        Args:
            redis_client: Redis 客户端
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小（秒）
            prefix: Redis 键前缀
        """
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求（使用 Redis Lua 脚本保证原子性）"""
        redis_key = f"{self.prefix}:{key}"
        now = time.time()

        # Lua 脚本实现滑动窗口
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])

        -- 清理过期记录
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

        -- 获取当前计数
        local current = redis.call('ZCARD', key)

        if current < limit then
            -- 添加新记录
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window)
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(
            lua_script,
            1,
            redis_key,
            now,
            self.window_seconds,
            self.max_requests
        )

        return bool(result)

    def get_remaining(self, key: str) -> int:
        """获取剩余配额"""
        redis_key = f"{self.prefix}:{key}"
        now = time.time()
        cutoff = now - self.window_seconds

        # 清理过期记录
        self.redis.zremrangebyscore(redis_key, 0, cutoff)

        # 获取当前计数
        current = self.redis.zcard(redis_key)

        return max(0, self.max_requests - current)


class AdaptiveRateLimiter:
    """
    自适应限流器

    特点：
    - 根据系统负载动态调整限流阈值
    - 自动平衡性能和稳定性
    """

    def __init__(
        self,
        base_rate: int,
        min_rate: int,
        max_rate: int,
        target_cpu_percent: float = 70.0
    ):
        """
        Args:
            base_rate: 基础速率
            min_rate: 最小速率
            max_rate: 最大速率
            target_cpu_percent: 目标 CPU 使用率
        """
        self.base_rate = base_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.target_cpu = target_cpu_percent
        self.current_rate = base_rate
        self.limiter = TokenBucketLimiter(base_rate, base_rate * 2)

    def adjust_rate(self, cpu_percent: float):
        """根据 CPU 使用率调整限流速率"""
        if cpu_percent > self.target_cpu:
            # CPU 过高，降低速率
            self.current_rate = max(
                self.min_rate,
                self.current_rate * 0.9
            )
        elif cpu_percent < self.target_cpu * 0.8:
            # CPU 较低，提高速率
            self.current_rate = min(
                self.max_rate,
                self.current_rate * 1.1
            )

        # 更新限流器
        self.limiter.rate = self.current_rate

    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        return self.limiter.is_allowed(key)


# 装饰器：应用速率限制
def rate_limit(
    limiter: RateLimiter,
    key_func: Optional[Callable] = None
):
    """
    速率限制装饰器

    用法:
        limiter = TokenBucketLimiter(rate=10, capacity=20)

        @rate_limit(limiter, key_func=lambda request: request.user_id)
        def api_endpoint(request):
            return "OK"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成限流键
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "global"

            # 检查限流
            if not limiter.is_allowed(key):
                raise Exception(f"Rate limit exceeded for key: {key}")

            return func(*args, **kwargs)

        return wrapper
    return decorator


# FastAPI 中间件示例
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# 创建限流器
limiter = RedisRateLimiter(
    redis_client=redis.Redis(host='localhost', port=6379),
    max_requests=100,
    window_seconds=60
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 使用 IP 地址作为限流键
    client_ip = request.client.host

    if not limiter.is_allowed(client_ip):
        remaining = limiter.get_remaining(client_ip)
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "remaining": remaining
            }
        )

    response = await call_next(request)

    # 添加限流头
    response.headers["X-RateLimit-Remaining"] = str(
        limiter.get_remaining(client_ip)
    )

    return response
"""


# 使用示例
if __name__ == "__main__":
    print("=== 速率限制示例 ===\n")

    # 1. 令牌桶限流器
    print("1. 令牌桶限流器 (10 req/s, 容量 20)")
    tb_limiter = TokenBucketLimiter(rate=10, capacity=20)

    # 模拟请求
    allowed_count = 0
    for i in range(30):
        if tb_limiter.is_allowed("user_1"):
            allowed_count += 1

    print(f"   允许: {allowed_count}/30 请求")
    print(f"   剩余令牌: {tb_limiter.get_remaining('user_1')}\n")

    # 2. 滑动窗口限流器
    print("2. 滑动窗口限流器 (5 req/10s)")
    sw_limiter = SlidingWindowLimiter(max_requests=5, window_seconds=10)

    allowed_count = 0
    for i in range(10):
        if sw_limiter.is_allowed("user_2"):
            allowed_count += 1

    print(f"   允许: {allowed_count}/10 请求")
    print(f"   剩余配额: {sw_limiter.get_remaining('user_2')}\n")

    # 3. 自适应限流器
    print("3. 自适应限流器")
    adaptive = AdaptiveRateLimiter(
        base_rate=50,
        min_rate=10,
        max_rate=100,
        target_cpu_percent=70
    )

    # 模拟 CPU 变化
    print(f"   初始速率: {adaptive.current_rate}")

    adaptive.adjust_rate(cpu_percent=85)  # 高负载
    print(f"   CPU 85% 后: {adaptive.current_rate}")

    adaptive.adjust_rate(cpu_percent=50)  # 低负载
    print(f"   CPU 50% 后: {adaptive.current_rate}")

    print("\n限流示例完成！")
