"""
配置管理系统
支持多环境配置、环境变量覆盖和配置验证
"""

from typing import Any, Dict, Optional
import yaml
import os
from pathlib import Path
import json


class ConfigurationError(Exception):
    """配置错误异常"""
    pass


class Config:
    """
    配置管理器

    支持：
    1. 多环境配置（development, staging, production）
    2. 环境变量覆盖
    3. 配置验证
    4. 点号路径访问
    """

    def __init__(self, env: Optional[str] = None, config_dir: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            env: 环境名称，默认从ENV环境变量读取
            config_dir: 配置文件目录，默认为./config
        """
        self.env = env or os.getenv("ENV", "development")
        self.config_dir = Path(config_dir or "config")
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            # 1. 加载基础配置（如果存在）
            base_config_path = self.config_dir / "base.yaml"
            if base_config_path.exists():
                with open(base_config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
                    print(f"✓ 已加载基础配置: {base_config_path}")

            # 2. 加载环境特定配置
            env_config_path = self.config_dir / f"{self.env}.yaml"
            if env_config_path.exists():
                with open(env_config_path, 'r', encoding='utf-8') as f:
                    env_config = yaml.safe_load(f) or {}
                    self._deep_update(self._config, env_config)
                    print(f"✓ 已加载环境配置: {env_config_path}")
            else:
                print(f"⚠ 环境配置文件不存在: {env_config_path}")

            # 3. 环境变量覆盖
            self._load_env_overrides()

            print(f"✓ 配置加载完成 (环境: {self.env})")

        except Exception as e:
            raise ConfigurationError(f"配置加载失败: {str(e)}")

    def _deep_update(self, base: dict, update: dict):
        """
        深度更新字典

        Args:
            base: 基础字典
            update: 更新字典
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def _load_env_overrides(self):
        """
        从环境变量加载覆盖配置

        格式：APP_SECTION__KEY=value
        例如：APP_LLM__MODEL=gpt-4 -> config.llm.model = "gpt-4"
        """
        prefix = "APP_"
        override_count = 0

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 移除前缀并转换为小写
                config_path = key[len(prefix):].lower().split("__")

                # 尝试转换值类型
                parsed_value = self._parse_value(value)

                # 设置嵌套值
                self._set_nested(self._config, config_path, parsed_value)
                override_count += 1

        if override_count > 0:
            print(f"✓ 已应用 {override_count} 个环境变量覆盖")

    def _parse_value(self, value: str) -> Any:
        """
        解析字符串值为合适的类型

        Args:
            value: 字符串值

        Returns:
            解析后的值
        """
        # 尝试解析为JSON（支持数字、布尔值、列表、字典等）
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            # 如果不是有效的JSON，返回原始字符串
            return value

    def _set_nested(self, d: dict, keys: list, value: Any):
        """
        设置嵌套字典值

        Args:
            d: 字典
            keys: 键路径列表
            value: 要设置的值
        """
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号路径）

        Args:
            key: 配置键，支持点号分隔的路径，如 "llm.model"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_required(self, key: str) -> Any:
        """
        获取必需的配置值，如果不存在则抛出异常

        Args:
            key: 配置键

        Returns:
            配置值

        Raises:
            ConfigurationError: 配置不存在
        """
        value = self.get(key)
        if value is None:
            raise ConfigurationError(f"必需的配置项不存在: {key}")
        return value

    def set(self, key: str, value: Any):
        """
        设置配置值

        Args:
            key: 配置键，支持点号分隔的路径
            value: 配置值
        """
        keys = key.split(".")
        self._set_nested(self._config, keys, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        获取完整配置字典

        Returns:
            配置字典
        """
        return self._config.copy()

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        return self.get(key)

    def __getattr__(self, name: str) -> Any:
        """支持属性式访问"""
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return self.get(name)

    def validate(self, required_keys: list) -> bool:
        """
        验证必需的配置项是否存在

        Args:
            required_keys: 必需的配置键列表

        Returns:
            是否全部存在

        Raises:
            ConfigurationError: 有配置项缺失
        """
        missing_keys = []
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)

        if missing_keys:
            raise ConfigurationError(
                f"缺少必需的配置项: {', '.join(missing_keys)}"
            )

        return True

    def __repr__(self) -> str:
        return f"Config(env={self.env}, keys={list(self._config.keys())})"


# 全局配置实例
_global_config: Optional[Config] = None


def get_config(env: Optional[str] = None, config_dir: Optional[str] = None) -> Config:
    """
    获取全局配置实例（单例模式）

    Args:
        env: 环境名称
        config_dir: 配置目录

    Returns:
        配置实例
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(env=env, config_dir=config_dir)
    return _global_config


def reset_config():
    """重置全局配置（主要用于测试）"""
    global _global_config
    _global_config = None


# 使用示例
if __name__ == "__main__":
    # 创建示例配置文件
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # 基础配置
    base_config = {
        "app": {
            "name": "AI Agent Service",
            "version": "1.0.0",
            "debug": False
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30
        },
        "database": {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "pool_size": 10
        },
        "cache": {
            "type": "redis",
            "host": "localhost",
            "port": 6379,
            "ttl": 3600
        }
    }

    with open(config_dir / "base.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(base_config, f, allow_unicode=True)

    # 开发环境配置
    dev_config = {
        "app": {"debug": True},
        "llm": {"temperature": 0.9}
    }

    with open(config_dir / "development.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(dev_config, f, allow_unicode=True)

    # 生产环境配置
    prod_config = {
        "app": {"debug": False},
        "llm": {"temperature": 0.3},
        "database": {"pool_size": 50},
        "cache": {"ttl": 7200}
    }

    with open(config_dir / "production.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(prod_config, f, allow_unicode=True)

    print("=" * 50)
    print("配置管理系统示例")
    print("=" * 50)

    # 测试配置加载
    config = Config(env="development")

    print(f"\n1. 获取配置值:")
    print(f"   应用名称: {config.get('app.name')}")
    print(f"   LLM模型: {config.get('llm.model')}")
    print(f"   温度: {config.get('llm.temperature')}")
    print(f"   调试模式: {config.get('app.debug')}")

    print(f"\n2. 默认值:")
    print(f"   不存在的键: {config.get('nonexistent.key', 'default_value')}")

    print(f"\n3. 属性式访问:")
    print(f"   配置对象: {config}")

    print(f"\n4. 验证必需配置:")
    try:
        config.validate(['app.name', 'llm.model', 'database.host'])
        print("   ✓ 所有必需配置项都存在")
    except ConfigurationError as e:
        print(f"   ✗ 验证失败: {e}")

    print(f"\n5. 环境变量覆盖测试:")
    print("   设置环境变量: APP_LLM__MODEL=gpt-3.5-turbo")
    os.environ["APP_LLM__MODEL"] = "gpt-3.5-turbo"

    # 重新加载配置
    config2 = Config(env="development")
    print(f"   覆盖后的模型: {config2.get('llm.model')}")
