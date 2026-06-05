"""
多级缓存系统
支持内存缓存、Redis缓存和缓存策略
"""

import hashlib
import json
import time
import logging
from typing import Any, Optional, Dict, Callable
from functools import wraps
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """缓存后端接口"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        pass

    @abstractmethod
    def delete(self, key: str):
        """删除缓存"""
        pass

    @abstractmethod
    def clear(self):
        """清空缓存"""
        pass


class MemoryCache(CacheBackend):
    """
    内存缓存
    使用字典存储，支持TTL
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        初始化内存缓存

        Args:
            default_ttl: 默认过期时间（秒）
            max_size: 最大缓存条目数
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        expires_at = entry.get("expires_at")

        # 检查是否过期
        if expires_at and time.time() > expires_at:
            self.delete(key)
            return None

        # 更新访问时间
        self._access_times[key] = time.time()

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        # 如果缓存已满，删除最久未使用的条目
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_lru()

        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl if ttl > 0 else None

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time()
        }
        self._access_times[key] = time.time()

    def delete(self, key: str):
        """删除缓存"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)

    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._access_times.clear()

    def _evict_lru(self):
        """驱逐最久未使用的条目（LRU）"""
        if not self._access_times:
            return

        # 找到最久未访问的键
        lru_key = min(self._access_times, key=self._access_times.get)
        self.delete(lru_key)
        logger.debug(f"LRU驱逐: {lru_key}")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "usage": len(self._cache) / self.max_size if self.max_size > 0 else 0
        }


class RedisCache(CacheBackend):
    """
    Redis缓存
    需要redis-py库
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600,
        key_prefix: str = "cache:"
    ):
        """
        初始化Redis缓存

        Args:
            host: Redis主机
            port: Redis端口
            db: 数据库编号
            password: 密码
            default_ttl: 默认过期时间（秒）
            key_prefix: 键前缀
        """
        try:
            import redis
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            self.default_ttl = default_ttl
            self.key_prefix = key_prefix
        except ImportError:
            logger.error("Redis缓存需要安装redis库: pip install redis")
            raise

    def _make_key(self, key: str) -> str:
        """生成完整的键名"""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            full_key = self._make_key(key)
            value = self.redis_client.get(full_key)

            if value is None:
                return None

            # 反序列化
            return json.loads(value)

        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        try:
            full_key = self._make_key(key)
            ttl = ttl if ttl is not None else self.default_ttl

            # 序列化
            serialized_value = json.dumps(value, ensure_ascii=False)

            if ttl > 0:
                self.redis_client.setex(full_key, ttl, serialized_value)
            else:
                self.redis_client.set(full_key, serialized_value)

        except Exception as e:
            logger.error(f"Redis设置失败: {e}")

    def delete(self, key: str):
        """删除缓存"""
        try:
            full_key = self._make_key(key)
            self.redis_client.delete(full_key)
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")

    def clear(self):
        """清空缓存（清空所有带前缀的键）"""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis清空失败: {e}")


class MultiLevelCache:
    """
    多级缓存
    L1: 内存缓存（快速）
    L2: Redis缓存（持久化）
    """

    def __init__(
        self,
        l1_cache: Optional[CacheBackend] = None,
        l2_cache: Optional[CacheBackend] = None
    ):
        """
        初始化多级缓存

        Args:
            l1_cache: L1缓存（内存）
            l2_cache: L2缓存（Redis）
        """
        self.l1_cache = l1_cache or MemoryCache()
        self.l2_cache = l2_cache

        # 统计
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """获取缓存（先查L1，再查L2）"""
        # 尝试L1缓存
        value = self.l1_cache.get(key)
        if value is not None:
            self.l1_hits += 1
            logger.debug(f"L1缓存命中: {key}")
            return value

        # 尝试L2缓存
        if self.l2_cache:
            value = self.l2_cache.get(key)
            if value is not None:
                self.l2_hits += 1
                logger.debug(f"L2缓存命中: {key}")

                # 回写到L1缓存
                self.l1_cache.set(key, value)
                return value

        # 缓存未命中
        self.misses += 1
        logger.debug(f"缓存未命中: {key}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存（同时写入L1和L2）"""
        self.l1_cache.set(key, value, ttl)

        if self.l2_cache:
            self.l2_cache.set(key, value, ttl)

    def delete(self, key: str):
        """删除缓存（同时删除L1和L2）"""
        self.l1_cache.delete(key)

        if self.l2_cache:
            self.l2_cache.delete(key)

    def clear(self):
        """清空所有缓存"""
        self.l1_cache.clear()

        if self.l2_cache:
            self.l2_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.l1_hits + self.l2_hits + self.misses

        return {
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": (
                (self.l1_hits + self.l2_hits) / total_requests
                if total_requests > 0 else 0
            ),
            "l1_cache": self.l1_cache.get_stats() if hasattr(self.l1_cache, 'get_stats') else {}
        }


def make_cache_key(*args, **kwargs) -> str:
    """
    生成缓存键

    Args:
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        缓存键
    """
    # 将参数转换为字符串
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

    # 生成哈希
    key_str = "|".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(cache: CacheBackend, ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    缓存装饰器

    Args:
        cache: 缓存后端
        ttl: 过期时间（秒）
        key_func: 自定义键生成函数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{make_cache_key(*args, **kwargs)}"

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, ttl)
            logger.debug(f"缓存设置: {cache_key}")

            return result

        return wrapper
    return decorator


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 50)
    print("多级缓存系统示例")
    print("=" * 50)

    # 1. 内存缓存
    print("\n1. 内存缓存:")
    mem_cache = MemoryCache(default_ttl=5, max_size=3)

    mem_cache.set("user:1", {"name": "Alice", "age": 30})
    mem_cache.set("user:2", {"name": "Bob", "age": 25})

    print(f"   获取 user:1: {mem_cache.get('user:1')}")
    print(f"   获取 user:2: {mem_cache.get('user:2')}")
    print(f"   缓存统计: {mem_cache.get_stats()}")

    # 2. 缓存过期
    print("\n2. 缓存过期测试:")
    mem_cache.set("temp", "临时数据", ttl=1)
    print(f"   立即获取: {mem_cache.get('temp')}")
    time.sleep(1.5)
    print(f"   过期后获取: {mem_cache.get('temp')}")

    # 3. LRU驱逐
    print("\n3. LRU驱逐测试:")
    mem_cache.clear()
    for i in range(5):
        mem_cache.set(f"key:{i}", f"value:{i}")
        stats = mem_cache.get_stats()
        print(f"   设置 key:{i}, 当前大小: {stats['size']}/{stats['max_size']}")

    # 4. 多级缓存
    print("\n4. 多级缓存:")
    multi_cache = MultiLevelCache(
        l1_cache=MemoryCache(max_size=100),
        l2_cache=None  # 可以替换为RedisCache
    )

    multi_cache.set("product:1", {"name": "Laptop", "price": 999})
    print(f"   第1次获取: {multi_cache.get('product:1')}")
    print(f"   第2次获取: {multi_cache.get('product:1')}")
    print(f"   未缓存的获取: {multi_cache.get('product:999')}")

    stats = multi_cache.get_stats()
    print(f"   缓存统计: {stats}")

    # 5. 缓存装饰器
    print("\n5. 缓存装饰器:")

    cache_backend = MemoryCache()

    call_count = 0

    @cached(cache_backend, ttl=60)
    def expensive_computation(x: int, y: int) -> int:
        """模拟耗时计算"""
        global call_count
        call_count += 1
        print(f"   执行计算 (调用次数: {call_count})")
        time.sleep(0.1)  # 模拟耗时
        return x + y

    print(f"   结果1: {expensive_computation(10, 20)}")
    print(f"   结果2 (缓存): {expensive_computation(10, 20)}")
    print(f"   结果3 (不同参数): {expensive_computation(15, 25)}")
    print(f"   结果4 (缓存): {expensive_computation(15, 25)}")

    # 6. 自定义缓存键
    print("\n6. 自定义缓存键:")

    def custom_key_func(user_id: int, **kwargs) -> str:
        return f"user_profile:{user_id}"

    @cached(cache_backend, ttl=30, key_func=custom_key_func)
    def get_user_profile(user_id: int, include_details: bool = False):
        """获取用户资料"""
        print(f"   从数据库加载用户 {user_id}")
        return {"id": user_id, "name": f"User{user_id}"}

    print(f"   用户1: {get_user_profile(1)}")
    print(f"   用户1 (缓存): {get_user_profile(1, include_details=True)}")
