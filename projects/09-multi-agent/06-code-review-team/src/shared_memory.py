"""
共享记忆管理
实现多Agent共享状态和上下文
"""

import time
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from langchain_openai import ChatOpenAI


@dataclass
class Fact:
    """事实性知识"""
    key: str
    value: Any
    source: str
    timestamp: float
    confidence: float = 1.0  # 置信度 0-1

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class Decision:
    """决策记录"""
    decision_id: str
    description: str
    made_by: str
    rationale: str
    timestamp: float
    outcome: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


class SharedMemory:
    """共享记忆空间：多Agent共享的知识库"""

    def __init__(self):
        """初始化共享记忆"""
        self.facts: Dict[str, Fact] = {}  # 事实性知识
        self.context: List[str] = []  # 对话上下文
        self.decisions: List[Decision] = []  # 决策历史
        self.variables: Dict[str, Any] = {}  # 共享变量
        self.max_context_size = 50  # 最大上下文条数

    def add_fact(self, key: str, value: Any, source: str, confidence: float = 1.0):
        """
        添加或更新事实

        Args:
            key: 事实的键
            value: 事实的值
            source: 信息来源（Agent ID）
            confidence: 置信度 0-1
        """
        fact = Fact(
            key=key,
            value=value,
            source=source,
            timestamp=time.time(),
            confidence=confidence
        )
        self.facts[key] = fact
        print(f"✓ 添加事实: {key} = {value} (来源: {source}, 置信度: {confidence})")

    def get_fact(self, key: str) -> Optional[Any]:
        """
        获取事实

        Args:
            key: 事实的键

        Returns:
            事实的值，不存在返回None
        """
        fact = self.facts.get(key)
        return fact.value if fact else None

    def get_fact_with_metadata(self, key: str) -> Optional[Fact]:
        """
        获取事实及其元数据

        Args:
            key: 事实的键

        Returns:
            Fact对象
        """
        return self.facts.get(key)

    def update_fact(self, key: str, value: Any, source: str, confidence: float = 1.0):
        """
        更新已存在的事实

        Args:
            key: 事实的键
            value: 新值
            source: 更新来源
            confidence: 新置信度
        """
        if key in self.facts:
            old_fact = self.facts[key]
            print(f"⚠ 更新事实: {key}")
            print(f"  旧值: {old_fact.value} (来源: {old_fact.source}, 置信度: {old_fact.confidence})")
            print(f"  新值: {value} (来源: {source}, 置信度: {confidence})")

        self.add_fact(key, value, source, confidence)

    def add_context(self, context: str, agent_id: Optional[str] = None):
        """
        添加上下文

        Args:
            context: 上下文内容
            agent_id: Agent标识（可选）
        """
        timestamp = time.time()
        formatted_context = f"[{agent_id or 'System'}] {context}" if agent_id else context
        self.context.append(formatted_context)

        # 保持最近的N条上下文
        if len(self.context) > self.max_context_size:
            self.context = self.context[-self.max_context_size:]

    def get_context(self, last_n: Optional[int] = None) -> List[str]:
        """
        获取上下文

        Args:
            last_n: 获取最近的N条，None表示全部

        Returns:
            上下文列表
        """
        if last_n:
            return self.context[-last_n:]
        return self.context

    def get_relevant_context(self, query: str, top_k: int = 5) -> List[str]:
        """
        获取相关上下文（简单实现：返回最近的k条）

        Args:
            query: 查询内容
            top_k: 返回的上下文条数

        Returns:
            相关上下文列表
        """
        # 简单实现：返回最近的k条
        # 在实际应用中，可以使用向量相似度搜索
        return self.context[-top_k:]

    def record_decision(
        self,
        decision_id: str,
        description: str,
        made_by: str,
        rationale: str,
        outcome: Optional[str] = None
    ):
        """
        记录决策

        Args:
            decision_id: 决策唯一标识
            description: 决策描述
            made_by: 决策者
            rationale: 决策理由
            outcome: 决策结果（可选）
        """
        decision = Decision(
            decision_id=decision_id,
            description=description,
            made_by=made_by,
            rationale=rationale,
            timestamp=time.time(),
            outcome=outcome
        )
        self.decisions.append(decision)
        print(f"✓ 记录决策: {decision_id} (by {made_by})")

    def update_decision_outcome(self, decision_id: str, outcome: str):
        """
        更新决策结果

        Args:
            decision_id: 决策ID
            outcome: 结果描述
        """
        for decision in self.decisions:
            if decision.decision_id == decision_id:
                decision.outcome = outcome
                print(f"✓ 更新决策结果: {decision_id}")
                return
        print(f"⚠ 未找到决策: {decision_id}")

    def get_decisions(self, made_by: Optional[str] = None) -> List[Decision]:
        """
        获取决策历史

        Args:
            made_by: 筛选特定决策者的决策

        Returns:
            决策列表
        """
        if made_by:
            return [d for d in self.decisions if d.made_by == made_by]
        return self.decisions

    def set_variable(self, key: str, value: Any):
        """
        设置共享变量

        Args:
            key: 变量名
            value: 变量值
        """
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        获取共享变量

        Args:
            key: 变量名
            default: 默认值

        Returns:
            变量值
        """
        return self.variables.get(key, default)

    def clear_context(self):
        """清空上下文"""
        self.context.clear()
        print("✓ 已清空上下文")

    def export_state(self) -> dict:
        """
        导出当前状态

        Returns:
            状态字典
        """
        return {
            'facts': {k: v.to_dict() for k, v in self.facts.items()},
            'context': self.context,
            'decisions': [d.to_dict() for d in self.decisions],
            'variables': self.variables
        }

    def get_summary(self) -> dict:
        """
        获取记忆摘要

        Returns:
            摘要信息
        """
        return {
            'total_facts': len(self.facts),
            'total_context': len(self.context),
            'total_decisions': len(self.decisions),
            'total_variables': len(self.variables)
        }


class MemoryAwareAgent:
    """具有共享记忆能力的Agent"""

    def __init__(self, agent_id: str, shared_memory: SharedMemory, llm: Optional[ChatOpenAI] = None):
        """
        初始化记忆感知Agent

        Args:
            agent_id: Agent唯一标识
            shared_memory: 共享记忆实例
            llm: 语言模型实例
        """
        self.agent_id = agent_id
        self.memory = shared_memory
        self.llm = llm or ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    def execute_with_context(self, task: str) -> str:
        """
        使用共享上下文执行任务

        Args:
            task: 任务描述

        Returns:
            执行结果
        """
        # 获取相关上下文
        context = self.memory.get_relevant_context(task, top_k=5)

        # 构建提示
        context_str = "\n".join(context) if context else "无相关上下文"

        prompt = f"""你是 {self.agent_id}。

相关上下文：
{context_str}

当前任务：
{task}

请基于上下文完成任务。如果发现重要信息，可以记录到共享记忆中。

执行结果："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)

            # 更新上下文
            self.memory.add_context(f"执行任务: {task[:50]}... -> {result[:50]}...", self.agent_id)

            print(f"✓ [{self.agent_id}] 任务完成")
            return result
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            print(f"✗ [{self.agent_id}] {error_msg}")
            return error_msg

    def contribute_knowledge(self, key: str, value: Any, confidence: float = 1.0):
        """
        贡献知识到共享记忆

        Args:
            key: 知识键
            value: 知识值
            confidence: 置信度
        """
        self.memory.add_fact(key, value, self.agent_id, confidence)

    def query_knowledge(self, key: str) -> Optional[Any]:
        """
        查询共享知识

        Args:
            key: 知识键

        Returns:
            知识值
        """
        return self.memory.get_fact(key)

    def make_decision(self, decision_id: str, description: str, rationale: str):
        """
        做出决策并记录

        Args:
            decision_id: 决策ID
            description: 决策描述
            rationale: 决策理由
        """
        self.memory.record_decision(decision_id, description, self.agent_id, rationale)

    def review_decisions(self) -> List[Decision]:
        """
        查看自己做出的决策

        Returns:
            决策列表
        """
        return self.memory.get_decisions(made_by=self.agent_id)

    def collaborate_with_memory(self, task: str, use_facts: bool = True, use_decisions: bool = True) -> str:
        """
        使用完整的共享记忆进行协作

        Args:
            task: 任务描述
            use_facts: 是否使用事实性知识
            use_decisions: 是否使用决策历史

        Returns:
            执行结果
        """
        # 收集相关信息
        context_parts = []

        if use_facts and self.memory.facts:
            facts_str = "\n".join([f"- {k}: {v.value}" for k, v in self.memory.facts.items()])
            context_parts.append(f"已知事实：\n{facts_str}")

        if use_decisions and self.memory.decisions:
            recent_decisions = self.memory.decisions[-5:]  # 最近5个决策
            decisions_str = "\n".join([
                f"- {d.description} (by {d.made_by}): {d.rationale}"
                for d in recent_decisions
            ])
            context_parts.append(f"最近决策：\n{decisions_str}")

        # 获取上下文
        context = self.memory.get_relevant_context(task, top_k=3)
        if context:
            context_parts.append(f"对话上下文：\n" + "\n".join(context))

        # 构建提示
        full_context = "\n\n".join(context_parts) if context_parts else "无相关背景信息"

        prompt = f"""你是 {self.agent_id}。请基于以下共享记忆完成任务。

{full_context}

任务：
{task}

执行结果："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)

            # 更新上下文
            self.memory.add_context(f"{task[:30]}... -> {result[:30]}...", self.agent_id)

            print(f"✓ [{self.agent_id}] 协作任务完成")
            return result
        except Exception as e:
            error_msg = f"协作失败: {str(e)}"
            print(f"✗ [{self.agent_id}] {error_msg}")
            return error_msg
