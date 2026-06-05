"""
记忆系统实现
包含工作记忆、情节记忆和语义记忆

记忆类型：
1. 工作记忆（Working Memory）：短期、当前上下文
2. 情节记忆（Episodic Memory）：对话历史、事件序列
3. 语义记忆（Semantic Memory）：长期知识、向量存储
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from dotenv import load_dotenv

from langchain.schema import BaseMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

load_dotenv()


# ============ 记忆条目数据类 ============

@dataclass
class MemoryEntry:
    """
    记忆条目

    属性:
        content: 记忆内容
        timestamp: 时间戳
        importance: 重要性分数 (0-1)
        access_count: 访问次数
        memory_type: 记忆类型
        metadata: 元数据
    """
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    access_count: int = 0
    memory_type: str = "episodic"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def access(self):
        """记录访问"""
        self.access_count += 1

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.content} (重要性: {self.importance:.2f})"


# ============ 工作记忆 ============

class WorkingMemory:
    """
    工作记忆（短期记忆）
    保存最近的对话和当前任务的上下文

    特性：
    - 容量有限（通常5-7条）
    - 快速访问
    - 自动清理旧内容
    """

    def __init__(self, capacity: int = 5):
        """
        初始化工作记忆

        参数:
            capacity: 最大容量
        """
        self.capacity = capacity
        self.items: List[MemoryEntry] = []

    def add(self, content: str, importance: float = 0.5, metadata: Dict = None):
        """
        添加记忆

        参数:
            content: 内容
            importance: 重要性
            metadata: 元数据
        """
        entry = MemoryEntry(
            content=content,
            importance=importance,
            memory_type="working",
            metadata=metadata or {}
        )

        self.items.append(entry)

        # 如果超过容量，移除最旧的
        if len(self.items) > self.capacity:
            removed = self.items.pop(0)
            print(f"📤 [工作记忆] 移出: {removed.content[:50]}...")

    def get_all(self) -> List[MemoryEntry]:
        """获取所有记忆"""
        return self.items

    def get_recent(self, n: int = 3) -> List[MemoryEntry]:
        """获取最近的N条记忆"""
        return self.items[-n:]

    def clear(self):
        """清空工作记忆"""
        self.items = []

    def __str__(self):
        return f"工作记忆 ({len(self.items)}/{self.capacity}条)"


# ============ 情节记忆 ============

class EpisodicMemory:
    """
    情节记忆（对话历史）
    存储完整的对话历史和事件序列

    特性：
    - 按时间顺序存储
    - 可以搜索和回溯
    - 支持摘要压缩
    """

    def __init__(self, max_size: int = 100):
        """
        初始化情节记忆

        参数:
            max_size: 最大存储条数
        """
        self.max_size = max_size
        self.episodes: List[MemoryEntry] = []

    def add(self, content: str, importance: float = 0.5, metadata: Dict = None):
        """
        添加情节

        参数:
            content: 内容
            importance: 重要性
            metadata: 元数据
        """
        entry = MemoryEntry(
            content=content,
            importance=importance,
            memory_type="episodic",
            metadata=metadata or {}
        )

        self.episodes.append(entry)

        # 超过最大容量时，压缩或删除旧的
        if len(self.episodes) > self.max_size:
            self._compress_old_episodes()

    def _compress_old_episodes(self):
        """压缩旧的情节记忆"""
        # 保留最近的一半
        keep_count = self.max_size // 2
        self.episodes = self.episodes[-keep_count:]
        print(f"📦 [情节记忆] 已压缩，保留最近 {keep_count} 条")

    def search_by_time(self, start_time: datetime, end_time: datetime) -> List[MemoryEntry]:
        """
        按时间范围搜索

        参数:
            start_time: 开始时间
            end_time: 结束时间

        返回:
            符合条件的记忆列表
        """
        return [ep for ep in self.episodes
                if start_time <= ep.timestamp <= end_time]

    def search_by_keyword(self, keyword: str) -> List[MemoryEntry]:
        """
        按关键词搜索

        参数:
            keyword: 关键词

        返回:
            包含关键词的记忆列表
        """
        return [ep for ep in self.episodes if keyword.lower() in ep.content.lower()]

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """获取最近的N条情节"""
        return self.episodes[-n:]

    def get_important(self, threshold: float = 0.7) -> List[MemoryEntry]:
        """
        获取重要的情节

        参数:
            threshold: 重要性阈值

        返回:
            重要性高于阈值的记忆
        """
        return [ep for ep in self.episodes if ep.importance >= threshold]

    def __str__(self):
        return f"情节记忆 ({len(self.episodes)}条)"


# ============ 语义记忆 ============

class SemanticMemory:
    """
    语义记忆（长期知识）
    使用向量存储来保存和检索知识

    特性：
    - 基于相似度检索
    - 持久化存储
    - 支持大规模知识库
    """

    def __init__(self, persist_directory: str = "./semantic_memory"):
        """
        初始化语义记忆

        参数:
            persist_directory: 持久化目录
        """
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        self.vectorstore: Optional[FAISS] = None
        self.knowledge_base: Dict[str, MemoryEntry] = {}

        # 尝试加载已有的向量存储
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """初始化向量存储"""
        try:
            if os.path.exists(self.persist_directory):
                # 加载已有的向量存储
                self.vectorstore = FAISS.load_local(
                    self.persist_directory,
                    self.embeddings
                )
                print(f"✅ [语义记忆] 已加载 {self.vectorstore.index.ntotal} 条知识")
            else:
                # 创建新的向量存储
                self.vectorstore = FAISS.from_texts(
                    ["初始化语义记忆"],
                    self.embeddings
                )
                print("✅ [语义记忆] 已创建新的知识库")
        except Exception as e:
            print(f"⚠️  [语义记忆] 初始化失败: {str(e)}")
            # 创建空的向量存储
            self.vectorstore = FAISS.from_texts(
                ["初始化语义记忆"],
                self.embeddings
            )

    def add_knowledge(self, content: str, importance: float = 0.5, metadata: Dict = None):
        """
        添加知识

        参数:
            content: 知识内容
            importance: 重要性
            metadata: 元数据
        """
        entry = MemoryEntry(
            content=content,
            importance=importance,
            memory_type="semantic",
            metadata=metadata or {}
        )

        # 生成唯一ID
        entry_id = f"sem_{len(self.knowledge_base)}_{datetime.now().timestamp()}"
        self.knowledge_base[entry_id] = entry

        # 添加到向量存储
        if self.vectorstore:
            self.vectorstore.add_texts(
                [content],
                metadatas=[{"id": entry_id, "importance": importance}]
            )

        print(f"📚 [语义记忆] 已添加知识: {content[:50]}...")

    def retrieve(self, query: str, k: int = 3) -> List[MemoryEntry]:
        """
        检索相关知识

        参数:
            query: 查询内容
            k: 返回数量

        返回:
            相关的记忆列表
        """
        if not self.vectorstore:
            return []

        try:
            # 相似度搜索
            docs = self.vectorstore.similarity_search(query, k=k)

            results = []
            for doc in docs:
                # 从知识库中获取完整的记忆条目
                entry_id = doc.metadata.get("id")
                if entry_id in self.knowledge_base:
                    entry = self.knowledge_base[entry_id]
                    entry.access()  # 记录访问
                    results.append(entry)

            return results

        except Exception as e:
            print(f"⚠️  [语义记忆] 检索失败: {str(e)}")
            return []

    def save(self):
        """保存向量存储到磁盘"""
        if self.vectorstore:
            try:
                os.makedirs(self.persist_directory, exist_ok=True)
                self.vectorstore.save_local(self.persist_directory)
                print(f"💾 [语义记忆] 已保存到 {self.persist_directory}")
            except Exception as e:
                print(f"⚠️  [语义记忆] 保存失败: {str(e)}")

    def __str__(self):
        count = len(self.knowledge_base)
        return f"语义记忆 ({count}条知识)"


# ============ 统一记忆系统 ============

class UnifiedMemorySystem(BaseMemory):
    """
    统一记忆系统
    整合工作记忆、情节记忆和语义记忆

    特性：
    - 自动管理三种记忆
    - 智能检索相关信息
    - 记忆重要性评估
    """

    def __init__(
        self,
        working_capacity: int = 5,
        episodic_max_size: int = 100,
        semantic_persist_dir: str = "./semantic_memory"
    ):
        """
        初始化统一记忆系统

        参数:
            working_capacity: 工作记忆容量
            episodic_max_size: 情节记忆最大容量
            semantic_persist_dir: 语义记忆持久化目录
        """
        self.working_memory = WorkingMemory(capacity=working_capacity)
        self.episodic_memory = EpisodicMemory(max_size=episodic_max_size)
        self.semantic_memory = SemanticMemory(persist_directory=semantic_persist_dir)

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    @property
    def memory_variables(self) -> List[str]:
        """返回记忆变量名"""
        return ["working_context", "relevant_history", "relevant_knowledge"]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        加载相关记忆

        参数:
            inputs: 输入字典，包含当前查询

        返回:
            记忆变量字典
        """
        query = inputs.get("input", "")

        # 1. 获取工作记忆（最近的上下文）
        working_items = self.working_memory.get_recent(3)
        working_context = "\n".join([item.content for item in working_items])

        # 2. 从情节记忆中检索相关历史
        relevant_episodes = self.episodic_memory.search_by_keyword(query)
        if not relevant_episodes:
            relevant_episodes = self.episodic_memory.get_recent(3)
        relevant_history = "\n".join([ep.content for ep in relevant_episodes[:3]])

        # 3. 从语义记忆中检索相关知识
        relevant_knowledge_items = self.semantic_memory.retrieve(query, k=2)
        relevant_knowledge = "\n".join([item.content for item in relevant_knowledge_items])

        return {
            "working_context": working_context or "无",
            "relevant_history": relevant_history or "无",
            "relevant_knowledge": relevant_knowledge or "无"
        }

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]):
        """
        保存上下文到记忆

        参数:
            inputs: 输入字典
            outputs: 输出字典
        """
        user_input = inputs.get("input", "")
        agent_output = outputs.get("output", "")

        # 组合输入输出
        context = f"用户: {user_input}\n助手: {agent_output}"

        # 评估重要性
        importance = self._evaluate_importance(context)

        # 保存到工作记忆
        self.working_memory.add(context, importance=importance)

        # 保存到情节记忆
        self.episodic_memory.add(context, importance=importance)

        # 如果非常重要，保存到语义记忆
        if importance > 0.7:
            self.semantic_memory.add_knowledge(context, importance=importance)

    def _evaluate_importance(self, content: str) -> float:
        """
        评估内容的重要性

        参数:
            content: 内容

        返回:
            重要性分数 (0-1)
        """
        # 简单的启发式规则
        importance = 0.5

        # 包含关键词提高重要性
        keywords = ["重要", "关键", "必须", "记住", "注意"]
        if any(kw in content for kw in keywords):
            importance += 0.2

        # 内容较长提高重要性
        if len(content) > 100:
            importance += 0.1

        # 限制在 0-1 范围
        return min(1.0, max(0.0, importance))

    def clear(self):
        """清空所有记忆"""
        self.working_memory.clear()
        print("🗑️  已清空所有记忆")

    def summary(self):
        """打印记忆系统摘要"""
        print("\n" + "="*60)
        print("记忆系统状态")
        print("="*60)
        print(f"📋 {self.working_memory}")
        print(f"📖 {self.episodic_memory}")
        print(f"📚 {self.semantic_memory}")
        print("="*60 + "\n")


# ============ 测试示例 ============

def run_examples():
    """运行示例"""

    print("="*80)
    print("记忆系统示例")
    print("="*80)

    # 创建记忆系统
    memory_system = UnifiedMemorySystem(
        working_capacity=5,
        episodic_max_size=50,
        semantic_persist_dir="./test_semantic_memory"
    )

    # 示例1：添加对话到记忆
    print("\n【示例1】添加对话到记忆")
    print("-"*80)

    conversations = [
        {"input": "Python是什么？", "output": "Python是一种高级编程语言"},
        {"input": "如何学习Python？", "output": "可以通过在线教程、书籍和实践项目学习"},
        {"input": "Python有什么优势？", "output": "Python语法简洁、生态丰富、应用广泛"}
    ]

    for conv in conversations:
        memory_system.save_context({"input": conv["input"]}, {"output": conv["output"]})

    memory_system.summary()

    # 示例2：检索相关记忆
    print("\n【示例2】检索相关记忆")
    print("-"*80)

    query = "Python学习"
    memories = memory_system.load_memory_variables({"input": query})

    print(f"查询: {query}\n")
    print("工作记忆:")
    print(memories["working_context"])
    print("\n相关历史:")
    print(memories["relevant_history"])
    print("\n相关知识:")
    print(memories["relevant_knowledge"])

    # 示例3：添加重要知识
    print("\n\n【示例3】添加重要知识到语义记忆")
    print("-"*80)

    important_facts = [
        "Python由Guido van Rossum于1991年创建",
        "Python支持多种编程范式：面向对象、函数式、过程式",
        "Python的哲学是'优雅'、'明确'、'简单'"
    ]

    for fact in important_facts:
        memory_system.semantic_memory.add_knowledge(fact, importance=0.9)

    # 检索知识
    query = "Python的历史"
    results = memory_system.semantic_memory.retrieve(query, k=2)
    print(f"\n检索 '{query}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.content}")

    # 保存语义记忆
    memory_system.semantic_memory.save()

    # 示例4：情节记忆搜索
    print("\n\n【示例4】情节记忆搜索")
    print("-"*80)

    episodes = memory_system.episodic_memory.search_by_keyword("学习")
    print(f"包含'学习'的情节 ({len(episodes)}条):")
    for ep in episodes:
        print(f"  - {ep}")


if __name__ == "__main__":
    run_examples()
