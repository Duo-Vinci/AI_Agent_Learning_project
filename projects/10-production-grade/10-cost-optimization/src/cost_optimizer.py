"""
成本优化模块
Token计数、成本估算和优化策略
"""

import tiktoken
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


# ========== 定价信息 ==========

# OpenAI定价（每1000个Token的美元价格，2024年价格）
PRICING = {
    "gpt-4": {
        "prompt": 0.03,
        "completion": 0.06
    },
    "gpt-4-32k": {
        "prompt": 0.06,
        "completion": 0.12
    },
    "gpt-3.5-turbo": {
        "prompt": 0.0015,
        "completion": 0.002
    },
    "gpt-3.5-turbo-16k": {
        "prompt": 0.003,
        "completion": 0.004
    },
    "claude-3-opus": {
        "prompt": 0.015,
        "completion": 0.075
    },
    "claude-3-sonnet": {
        "prompt": 0.003,
        "completion": 0.015
    },
    "claude-3-haiku": {
        "prompt": 0.00025,
        "completion": 0.00125
    }
}


# ========== Token管理器 ==========

class TokenManager:
    """
    Token管理器
    计算Token数量、估算成本、控制Token使用
    """

    def __init__(self, model: str = "gpt-4"):
        """
        初始化Token管理器

        Args:
            model: 模型名称
        """
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"模型 {model} 不支持tiktoken，使用cl100k_base编码")
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        计算文本的Token数量

        Args:
            text: 文本内容

        Returns:
            Token数量
        """
        return len(self.encoding.encode(text))

    def truncate_to_limit(self, text: str, max_tokens: int) -> str:
        """
        截断文本到指定Token数

        Args:
            text: 文本内容
            max_tokens: 最大Token数

        Returns:
            截断后的文本
        """
        tokens = self.encoding.encode(text)

        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """
        估算API调用成本

        Args:
            prompt_tokens: 提示词Token数
            completion_tokens: 完成Token数
            model: 模型名称（可选，默认使用初始化时的模型）

        Returns:
            成本（美元）
        """
        model = model or self.model

        # 获取定价
        pricing = PRICING.get(model)
        if not pricing:
            logger.warning(f"模型 {model} 没有定价信息，使用gpt-4价格估算")
            pricing = PRICING["gpt-4"]

        # 计算成本
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]

        return prompt_cost + completion_cost

    def optimize_prompt(self, prompt: str, max_tokens: int) -> str:
        """
        优化提示词（移除多余空格、换行等）

        Args:
            prompt: 原始提示词
            max_tokens: 最大Token数

        Returns:
            优化后的提示词
        """
        # 移除多余的空白字符
        import re
        optimized = re.sub(r'\s+', ' ', prompt).strip()

        # 如果仍然超过限制，进行截断
        if self.count_tokens(optimized) > max_tokens:
            optimized = self.truncate_to_limit(optimized, max_tokens)

        return optimized


# ========== 成本追踪器 ==========

@dataclass
class CostRecord:
    """成本记录"""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    operation: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostTracker:
    """
    成本追踪器
    追踪和分析LLM使用成本
    """

    def __init__(self):
        """初始化成本追踪器"""
        self.records: List[CostRecord] = []
        self.total_cost = 0.0
        self.total_tokens = 0

    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        operation: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        记录使用情况

        Args:
            model: 模型名称
            prompt_tokens: 提示词Token数
            completion_tokens: 完成Token数
            operation: 操作类型
            metadata: 元数据
        """
        # 计算成本
        token_manager = TokenManager(model)
        cost = token_manager.estimate_cost(prompt_tokens, completion_tokens)

        # 创建记录
        record = CostRecord(
            timestamp=datetime.utcnow(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            operation=operation,
            metadata=metadata or {}
        )

        self.records.append(record)
        self.total_cost += cost
        self.total_tokens += prompt_tokens + completion_tokens

        logger.info(
            f"记录LLM使用",
            extra={
                "model": model,
                "tokens": prompt_tokens + completion_tokens,
                "cost": f"${cost:.6f}",
                "operation": operation
            }
        )

    def get_total_cost(self, since: Optional[datetime] = None) -> float:
        """
        获取总成本

        Args:
            since: 起始时间（可选）

        Returns:
            总成本（美元）
        """
        if since is None:
            return self.total_cost

        filtered_records = [r for r in self.records if r.timestamp >= since]
        return sum(r.cost for r in filtered_records)

    def get_cost_by_model(self, since: Optional[datetime] = None) -> Dict[str, float]:
        """
        按模型统计成本

        Args:
            since: 起始时间（可选）

        Returns:
            模型成本字典
        """
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]

        cost_by_model: Dict[str, float] = {}
        for record in records:
            cost_by_model[record.model] = cost_by_model.get(record.model, 0) + record.cost

        return cost_by_model

    def get_cost_by_operation(self, since: Optional[datetime] = None) -> Dict[str, float]:
        """
        按操作类型统计成本

        Args:
            since: 起始时间（可选）

        Returns:
            操作成本字典
        """
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]

        cost_by_operation: Dict[str, float] = {}
        for record in records:
            cost_by_operation[record.operation] = cost_by_operation.get(record.operation, 0) + record.cost

        return cost_by_operation

    def get_statistics(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取统计信息

        Args:
            since: 起始时间（可选）

        Returns:
            统计信息字典
        """
        records = self.records
        if since:
            records = [r for r in records if r.timestamp >= since]

        if not records:
            return {
                "total_cost": 0,
                "total_requests": 0,
                "total_tokens": 0,
                "avg_cost_per_request": 0,
                "avg_tokens_per_request": 0
            }

        total_cost = sum(r.cost for r in records)
        total_tokens = sum(r.prompt_tokens + r.completion_tokens for r in records)

        return {
            "total_cost": total_cost,
            "total_requests": len(records),
            "total_tokens": total_tokens,
            "avg_cost_per_request": total_cost / len(records),
            "avg_tokens_per_request": total_tokens / len(records),
            "cost_by_model": self.get_cost_by_model(since),
            "cost_by_operation": self.get_cost_by_operation(since)
        }

    def get_daily_cost(self, days: int = 7) -> Dict[str, float]:
        """
        获取每日成本

        Args:
            days: 天数

        Returns:
            日期到成本的映射
        """
        daily_cost: Dict[str, float] = {}
        start_date = datetime.utcnow() - timedelta(days=days)

        for record in self.records:
            if record.timestamp >= start_date:
                date_str = record.timestamp.strftime("%Y-%m-%d")
                daily_cost[date_str] = daily_cost.get(date_str, 0) + record.cost

        return daily_cost

    def get_cost_alert(self, threshold: float) -> Optional[Dict[str, Any]]:
        """
        检查成本是否超过阈值

        Args:
            threshold: 成本阈值（美元）

        Returns:
            如果超过阈值，返回告警信息
        """
        if self.total_cost >= threshold:
            return {
                "alert": "成本告警",
                "current_cost": self.total_cost,
                "threshold": threshold,
                "exceeded_by": self.total_cost - threshold,
                "timestamp": datetime.utcnow().isoformat()
            }
        return None


# ========== 优化策略 ==========

class CostOptimizer:
    """成本优化器"""

    @staticmethod
    def suggest_model_downgrade(current_model: str, task_complexity: str) -> Optional[str]:
        """
        建议降级模型

        Args:
            current_model: 当前模型
            task_complexity: 任务复杂度（simple/medium/complex）

        Returns:
            建议的模型（如果有）
        """
        # 模型等级（从高到低）
        model_tiers = {
            "complex": ["gpt-4", "claude-3-opus"],
            "medium": ["gpt-3.5-turbo", "claude-3-sonnet"],
            "simple": ["gpt-3.5-turbo", "claude-3-haiku"]
        }

        recommended_models = model_tiers.get(task_complexity, [])

        # 如果当前模型不在推荐列表中，建议切换
        if current_model not in recommended_models:
            return recommended_models[0] if recommended_models else None

        return None

    @staticmethod
    def calculate_savings(
        current_model: str,
        suggested_model: str,
        monthly_tokens: int
    ) -> Dict[str, Any]:
        """
        计算切换模型的节省

        Args:
            current_model: 当前模型
            suggested_model: 建议模型
            monthly_tokens: 每月Token数

        Returns:
            节省信息
        """
        current_pricing = PRICING.get(current_model, PRICING["gpt-4"])
        suggested_pricing = PRICING.get(suggested_model, PRICING["gpt-3.5-turbo"])

        # 假设prompt和completion各占50%
        current_cost = (monthly_tokens / 1000) * (
            (current_pricing["prompt"] + current_pricing["completion"]) / 2
        )

        suggested_cost = (monthly_tokens / 1000) * (
            (suggested_pricing["prompt"] + suggested_pricing["completion"]) / 2
        )

        savings = current_cost - suggested_cost
        savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0

        return {
            "current_model": current_model,
            "suggested_model": suggested_model,
            "current_monthly_cost": current_cost,
            "suggested_monthly_cost": suggested_cost,
            "monthly_savings": savings,
            "savings_percent": savings_percent
        }


# ========== 使用示例 ==========

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 50)
    print("成本优化示例")
    print("=" * 50)

    # 1. Token计数
    print("\n1. Token计数:")
    token_manager = TokenManager("gpt-4")

    text = "人工智能Agent是一种能够自主执行任务的智能系统。"
    token_count = token_manager.count_tokens(text)
    print(f"   文本: {text}")
    print(f"   Token数: {token_count}")

    # 2. 文本截断
    print("\n2. 文本截断:")
    long_text = "这是一段很长的文本。" * 100
    print(f"   原始Token数: {token_manager.count_tokens(long_text)}")

    truncated = token_manager.truncate_to_limit(long_text, 50)
    print(f"   截断后Token数: {token_manager.count_tokens(truncated)}")

    # 3. 成本估算
    print("\n3. 成本估算:")
    cost = token_manager.estimate_cost(prompt_tokens=1000, completion_tokens=500)
    print(f"   GPT-4 (1000 prompt + 500 completion tokens): ${cost:.4f}")

    cost_turbo = TokenManager("gpt-3.5-turbo").estimate_cost(1000, 500)
    print(f"   GPT-3.5-Turbo (同样Token数): ${cost_turbo:.4f}")
    print(f"   节省: ${cost - cost_turbo:.4f} ({(cost - cost_turbo)/cost*100:.1f}%)")

    # 4. 成本追踪
    print("\n4. 成本追踪:")
    tracker = CostTracker()

    # 模拟一些API调用
    tracker.record_usage("gpt-4", 1000, 500, "research")
    tracker.record_usage("gpt-4", 800, 400, "writing")
    tracker.record_usage("gpt-3.5-turbo", 500, 300, "summarization")
    tracker.record_usage("claude-3-sonnet", 600, 350, "analysis")

    print(f"   总成本: ${tracker.total_cost:.4f}")
    print(f"   总Token数: {tracker.total_tokens:,}")

    # 5. 统计信息
    print("\n5. 统计信息:")
    stats = tracker.get_statistics()
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   平均每请求成本: ${stats['avg_cost_per_request']:.6f}")
    print(f"   平均每请求Token数: {stats['avg_tokens_per_request']:.0f}")

    print("\n   按模型统计:")
    for model, cost in stats['cost_by_model'].items():
        print(f"     {model}: ${cost:.4f}")

    print("\n   按操作统计:")
    for operation, cost in stats['cost_by_operation'].items():
        print(f"     {operation}: ${cost:.4f}")

    # 6. 成本告警
    print("\n6. 成本告警:")
    alert = tracker.get_cost_alert(threshold=0.10)
    if alert:
        print(f"   ⚠ {alert['alert']}")
        print(f"   当前成本: ${alert['current_cost']:.4f}")
        print(f"   阈值: ${alert['threshold']:.4f}")
        print(f"   超出: ${alert['exceeded_by']:.4f}")
    else:
        print("   ✓ 成本在阈值范围内")

    # 7. 优化建议
    print("\n7. 优化建议:")
    optimizer = CostOptimizer()

    suggestion = optimizer.suggest_model_downgrade("gpt-4", "simple")
    if suggestion:
        print(f"   建议: 对于简单任务，考虑使用 {suggestion} 代替 gpt-4")

        savings = optimizer.calculate_savings("gpt-4", suggestion, monthly_tokens=1000000)
        print(f"   预计每月节省: ${savings['monthly_savings']:.2f} ({savings['savings_percent']:.1f}%)")

    print("\n" + "=" * 50)
    print("成本优化提示:")
    print("  - 根据任务复杂度选择合适的模型")
    print("  - 使用缓存减少重复API调用")
    print("  - 优化提示词减少Token使用")
    print("  - 设置Token限制避免意外高额费用")
    print("  - 定期审查成本报告")
    print("=" * 50)
