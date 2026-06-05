"""
LangChain RAG应用 - 05: 检索策略（Retrieval Strategies）

本模块演示：
1. 相似度搜索（Similarity Search）
2. MMR（Maximum Marginal Relevance）- 最大边际相关性
3. 自查询检索器（Self-Query Retriever）
4. 多查询检索器（Multi-Query Retriever）
5. 父文档检索器（Parent Document Retriever）
6. 时间加权检索
7. 检索策略对比和适用场景
8. 检索参数优化

不同的检索策略适用于不同的应用场景，选择合适的策略能显著提升RAG效果。
"""

import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# 准备测试文档
SAMPLE_DOCUMENTS = [
    "LangChain是一个用于构建LLM应用的强大框架，提供了丰富的组件和工具。",
    "LangChain框架支持多种大型语言模型，包括OpenAI、Anthropic等。",
    "RAG技术通过检索相关文档来增强生成质量，减少幻觉问题。",
    "检索增强生成结合了信息检索和文本生成两种技术的优势。",
    "向量数据库用于存储和检索文档的向量表示，支持语义搜索。",
    "FAISS是Facebook开发的高效相似度搜索库，支持十亿级向量。",
    "Chroma是专为AI应用设计的向量数据库，使用简单。",
    "文本嵌入将文本转换为高维向量，是语义检索的基础。",
    "Transformer模型在自然语言处理领域取得了突破性进展。",
    "大型语言模型展示了强大的理解和生成能力，应用广泛。",
]


def get_vectorstore():
    """创建测试用的向量存储"""
    try:
        from langchain_community.vectorstores import FAISS
        from langchain.embeddings.fake import FakeEmbeddings

        embeddings = FakeEmbeddings(size=384)
        documents = [Document(page_content=text) for text in SAMPLE_DOCUMENTS]
        return FAISS.from_documents(documents, embeddings)
    except:
        return None


# ==================== 示例1: 相似度搜索（基础）====================

def demo_similarity_search():
    """示例1: 相似度搜索（Similarity Search）"""
    print_section("示例1: 相似度搜索（Similarity Search）")

    print("相似度搜索特点:")
    print("  ✓ 最基础的检索方法")
    print("  ✓ 返回与查询最相似的文档")
    print("  ✓ 速度快，实现简单")
    print("  ✗ 可能返回冗余结果")
    print("  ✗ 缺乏多样性\n")

    try:
        from langchain_community.vectorstores import FAISS
        from langchain.embeddings.fake import FakeEmbeddings

        embeddings = FakeEmbeddings(size=384)
        documents = [Document(page_content=text) for text in SAMPLE_DOCUMENTS]
        vectorstore = FAISS.from_documents(documents, embeddings)

        query = "什么是RAG技术？"
        print(f"查询: {query}\n")

        # 基础相似度搜索
        print("1. 基础搜索 (k=3):")
        results = vectorstore.similarity_search(query, k=3)
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content}")

        # 带分数的搜索
        print(f"\n2. 带分数搜索:")
        results_with_scores = vectorstore.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(results_with_scores, 1):
            print(f"   {i}. [分数: {score:.4f}] {doc.page_content[:60]}...")

        # 不同k值的影响
        print(f"\n3. k值影响:")
        for k in [1, 3, 5]:
            results = vectorstore.similarity_search(query, k=k)
            print(f"   k={k}: 返回 {len(results)} 个结果")

        print("\n适用场景:")
        print("  • 简单问答")
        print("  • 快速原型开发")
        print("  • 结果多样性不重要的场景\n")

    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例2: MMR（最大边际相关性）====================

def demo_mmr():
    """示例2: MMR（Maximum Marginal Relevance）"""
    print_section("示例2: MMR - 最大边际相关性")

    print("MMR特点:")
    print("  ✓ 平衡相关性和多样性")
    print("  ✓ 减少结果冗余")
    print("  ✓ 提供更全面的信息")
    print("  ✗ 计算复杂度稍高\n")

    print("MMR公式:")
    print("  MMR = λ * Sim(q, d) - (1-λ) * max Sim(d, d_i)")
    print("  • λ: 平衡参数 (0-1)")
    print("  • λ=1: 纯相关性（等同于相似度搜索）")
    print("  • λ=0: 纯多样性")
    print("  • λ=0.5: 平衡相关性和多样性\n")

    try:
        from langchain_community.vectorstores import FAISS
        from langchain.embeddings.fake import FakeEmbeddings

        embeddings = FakeEmbeddings(size=384)
        documents = [Document(page_content=text) for text in SAMPLE_DOCUMENTS]
        vectorstore = FAISS.from_documents(documents, embeddings)

        query = "LangChain框架"
        print(f"查询: {query}\n")

        # 标准相似度搜索
        print("1. 标准相似度搜索 (可能有冗余):")
        results = vectorstore.similarity_search(query, k=4)
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content[:65]}...")

        # MMR搜索
        print(f"\n2. MMR搜索 (lambda=0.5, 更多样化):")
        results = vectorstore.max_marginal_relevance_search(
            query,
            k=4,
            fetch_k=10,  # 先取10个候选，再选最多样的4个
            lambda_mult=0.5  # 平衡相关性和多样性
        )
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content[:65]}...")

        # 不同lambda值的影响
        print(f"\n3. 不同lambda值对比:")

        for lambda_val in [0.3, 0.5, 0.7, 1.0]:
            if lambda_val == 1.0:
                results = vectorstore.similarity_search(query, k=3)
                print(f"\n   lambda={lambda_val} (相似度搜索):")
            else:
                results = vectorstore.max_marginal_relevance_search(
                    query, k=3, fetch_k=10, lambda_mult=lambda_val
                )
                print(f"\n   lambda={lambda_val}:")

            for i, doc in enumerate(results, 1):
                print(f"     {i}. {doc.page_content[:60]}...")

        print("\n参数建议:")
        print("  • fetch_k: 通常设为k的2-3倍")
        print("  • lambda: 0.5是常用的平衡值")
        print("  • 多样性需求高时使用较小的lambda\n")

    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例3: 多查询检索器 ====================

def demo_multi_query_retriever():
    """示例3: 多查询检索器（Multi-Query Retriever）"""
    print_section("示例3: 多查询检索器")

    print("多查询检索器特点:")
    print("  ✓ 自动生成多个查询变体")
    print("  ✓ 从不同角度检索")
    print("  ✓ 提高召回率")
    print("  ✗ 需要LLM生成查询")
    print("  ✗ 成本和延迟增加\n")

    print("工作流程:")
    print("  1. 用户提出原始查询")
    print("  2. LLM生成多个查询变体")
    print("  3. 对每个变体执行检索")
    print("  4. 合并和去重结果\n")

    print("示例:")
    print("  原始查询: '如何使用LangChain构建RAG应用？'")
    print("\n  生成的查询变体:")
    print("    1. LangChain RAG应用开发步骤是什么？")
    print("    2. 使用LangChain实现检索增强生成的方法")
    print("    3. LangChain构建问答系统的最佳实践")
    print("\n  每个变体独立检索，结果合并后更全面\n")

    print("配置示例:")
    print("""
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm,
    num_queries=3  # 生成3个查询变体
)

results = retriever.get_relevant_documents("查询")
    """)

    print("\n适用场景:")
    print("  • 复杂问题需要多角度查询")
    print("  • 查询表达不够精确")
    print("  • 需要提高召回率\n")


# ==================== 示例4: 自查询检索器 ====================

def demo_self_query_retriever():
    """示例4: 自查询检索器（Self-Query Retriever）"""
    print_section("示例4: 自查询检索器")

    print("自查询检索器特点:")
    print("  ✓ 自动从查询中提取元数据过滤")
    print("  ✓ 分离语义查询和结构化过滤")
    print("  ✓ 提高检索精度")
    print("  ✗ 需要LLM解析查询")
    print("  ✗ 需要定义元数据结构\n")

    print("工作流程:")
    print("  1. 用户查询: '找出2023年关于Python的高级教程'")
    print("  2. LLM解析:")
    print("     - 语义查询: 'Python教程'")
    print("     - 元数据过滤: year=2023, level=advanced, topic=Python")
    print("  3. 执行过滤后的语义搜索\n")

    print("配置示例:")
    print("""
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever

# 定义元数据结构
metadata_field_info = [
    AttributeInfo(
        name="year",
        description="文档的发布年份",
        type="integer"
    ),
    AttributeInfo(
        name="level",
        description="难度级别: beginner, intermediate, advanced",
        type="string"
    ),
]

retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="技术教程文档",
    metadata_field_info=metadata_field_info
)
    """)

    print("\n查询示例:")
    examples = [
        ("找出初级的Python教程", "level='beginner' AND topic='Python'"),
        ("2023年发布的文章", "year=2023"),
        ("高级的机器学习内容", "level='advanced' AND topic='ML'"),
    ]

    print(f"{'用户查询':<30} {'提取的过滤条件'}")
    print("-" * 70)
    for query, filter_cond in examples:
        print(f"{query:<30} {filter_cond}")

    print("\n适用场景:")
    print("  • 查询包含结构化信息")
    print("  • 需要精确过滤")
    print("  • 多维度检索\n")


# ==================== 示例5: 父文档检索器 ====================

def demo_parent_document_retriever():
    """示例5: 父文档检索器（Parent Document Retriever）"""
    print_section("示例5: 父文档检索器")

    print("父文档检索器特点:")
    print("  ✓ 用小块检索，返回大块")
    print("  ✓ 平衡检索精度和上下文")
    print("  ✓ 避免上下文碎片化")
    print("  ✗ 实现较复杂\n")

    print("核心思想:")
    print("  • 索引: 存储小块文本的向量（精确匹配）")
    print("  • 检索: 返回小块所属的大块（完整上下文）")
    print("  • 优势: 结合了小块的精确性和大块的完整性\n")

    print("示例:")

    # 演示文档结构
    parent_doc = """
第一章：LangChain简介

LangChain是一个强大的框架，用于构建基于大型语言模型的应用。
它提供了丰富的组件，包括提示模板、链、代理等。

1.1 核心概念
LangChain的核心是链（Chain），它将多个组件连接起来。

1.2 应用场景
LangChain适用于问答系统、聊天机器人、文档分析等场景。
    """

    small_chunks = [
        "LangChain是一个强大的框架",
        "它提供了丰富的组件",
        "LangChain的核心是链",
        "适用于问答系统、聊天机器人"
    ]

    print("父文档（大块）:")
    print(parent_doc)
    print("\n子文档（小块，用于索引）:")
    for i, chunk in enumerate(small_chunks, 1):
        print(f"  {i}. {chunk}")

    print("\n检索过程:")
    print("  1. 查询: 'LangChain的组件'")
    print("  2. 匹配小块: '它提供了丰富的组件'")
    print("  3. 返回: 整个父文档（包含完整上下文）\n")

    print("配置示例:")
    print("""
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 父文档分割器（大块）
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
# 子文档分割器（小块）
child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

# 存储父文档
store = InMemoryStore()

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

retriever.add_documents(documents)
    """)

    print("\n适用场景:")
    print("  • 需要精确检索但保留完整上下文")
    print("  • 长文档分析")
    print("  • 学术论文、技术文档\n")


# ==================== 示例6: 时间加权检索 ====================

def demo_time_weighted_retrieval():
    """示例6: 时间加权检索"""
    print_section("示例6: 时间加权检索")

    print("时间加权检索特点:")
    print("  ✓ 考虑文档新鲜度")
    print("  ✓ 优先返回最近的文档")
    print("  ✓ 适合时效性强的内容")
    print("  ✗ 可能忽略旧但相关的文档\n")

    print("评分公式:")
    print("  score = semantic_similarity * (1 - decay_rate)^hours_passed")
    print("  • decay_rate: 衰减率，控制时间影响")
    print("  • hours_passed: 距离现在的小时数\n")

    print("示例:")

    documents_with_time = [
        {"content": "LangChain v0.1发布", "date": "2024-01-01", "similarity": 0.95},
        {"content": "LangChain v0.2发布", "date": "2024-06-01", "similarity": 0.90},
        {"content": "LangChain v0.3发布", "date": "2024-12-01", "similarity": 0.85},
    ]

    print(f"{'文档':<25} {'日期':<15} {'语义相似度':<12} {'时间加权后'}")
    print("-" * 70)

    decay_rate = 0.01  # 每小时衰减1%
    current_date = datetime(2024, 12, 15)

    for doc in documents_with_time:
        doc_date = datetime.strptime(doc["date"], "%Y-%m-%d")
        hours_passed = (current_date - doc_date).total_seconds() / 3600
        time_weight = (1 - decay_rate) ** hours_passed
        final_score = doc["similarity"] * time_weight

        print(f"{doc['content']:<25} {doc['date']:<15} {doc['similarity']:<12.2f} {final_score:.4f}")

    print("\n配置示例:")
    print("""
from langchain.retrievers import TimeWeightedVectorStoreRetriever

retriever = TimeWeightedVectorStoreRetriever(
    vectorstore=vectorstore,
    decay_rate=0.01,  # 每小时衰减1%
    k=4
)

# 添加文档时自动记录时间
retriever.add_documents(documents)
    """)

    print("\n适用场景:")
    print("  • 新闻、博客文章")
    print("  • 软件文档（版本更新）")
    print("  • 实时信息流\n")


# ==================== 示例7: 检索策略对比 ====================

def demo_strategy_comparison():
    """示例7: 检索策略对比和适用场景"""
    print_section("示例7: 检索策略对比")

    strategies = [
        {
            "策略": "相似度搜索",
            "速度": "快",
            "质量": "中",
            "复杂度": "低",
            "成本": "低",
            "适用场景": "通用，快速原型"
        },
        {
            "策略": "MMR",
            "速度": "中",
            "质量": "高",
            "复杂度": "中",
            "成本": "低",
            "适用场景": "需要多样性"
        },
        {
            "策略": "多查询",
            "速度": "慢",
            "质量": "高",
            "复杂度": "中",
            "成本": "高(需LLM)",
            "适用场景": "复杂查询"
        },
        {
            "策略": "自查询",
            "速度": "中",
            "质量": "高",
            "复杂度": "高",
            "成本": "高(需LLM)",
            "适用场景": "结构化过滤"
        },
        {
            "策略": "父文档",
            "速度": "中",
            "质量": "高",
            "复杂度": "高",
            "成本": "中",
            "适用场景": "长文档"
        },
        {
            "策略": "时间加权",
            "速度": "快",
            "质量": "中",
            "复杂度": "中",
            "成本": "低",
            "适用场景": "时效性内容"
        },
    ]

    print(f"{'策略':<12} {'速度':<6} {'质量':<6} {'复杂度':<8} {'成本':<12} {'适用场景'}")
    print("-" * 80)

    for s in strategies:
        print(f"{s['策略']:<12} {s['速度']:<6} {s['质量']:<6} {s['复杂度']:<8} {s['成本']:<12} {s['适用场景']}")

    print("\n组合策略:")
    print("  实际应用中，常常组合使用多种策略:\n")

    combinations = [
        "MMR + 元数据过滤: 在特定类别中获取多样化结果",
        "多查询 + 父文档: 多角度检索 + 完整上下文",
        "时间加权 + 相似度: 平衡新鲜度和相关性",
    ]

    for combo in combinations:
        print(f"  • {combo}")

    print("\n选择建议:")
    print("  1. 从简单策略开始（相似度搜索）")
    print("  2. 根据实际问题选择优化方向")
    print("  3. 通过评估指标验证效果")
    print("  4. 权衡性能、成本和质量\n")


# ==================== 示例8: 检索参数优化 ====================

def demo_parameter_optimization():
    """示例8: 检索参数优化"""
    print_section("示例8: 检索参数优化")

    print("关键参数及其影响:\n")

    print("1. k (检索数量)")
    print("   • 过小: 可能遗漏重要信息")
    print("   • 过大: 引入噪音，增加成本")
    print("   • 推荐: 3-5个用于问答，10-20个用于摘要\n")

    print("2. score_threshold (分数阈值)")
    print("   • 只返回分数高于阈值的结果")
    print("   • 避免低质量匹配")
    print("   • 推荐: 0.7-0.8（需要实验确定）\n")

    print("3. fetch_k (MMR候选数)")
    print("   • MMR的初始候选集大小")
    print("   • 推荐: k的2-3倍")
    print("   • 权衡: 更大的fetch_k提供更多多样性但更慢\n")

    print("4. lambda (MMR平衡参数)")
    print("   • 控制相关性vs多样性")
    print("   • lambda=1.0: 纯相关性")
    print("   • lambda=0.5: 平衡")
    print("   • lambda=0.0: 纯多样性\n")

    print("参数调优流程:\n")

    steps = [
        "1. 建立评估数据集（查询-期望结果对）",
        "2. 定义评估指标（准确率、召回率、MRR等）",
        "3. 网格搜索或贝叶斯优化",
        "4. 交叉验证",
        "5. 选择最佳参数组合",
    ]

    for step in steps:
        print(f"  {step}")

    print("\n示例: k值优化")
    print("""
# 评估不同k值
results = {}
for k in [1, 3, 5, 7, 10]:
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    # 计算评估指标
    metrics = evaluate(retriever, test_queries)
    results[k] = metrics

# 选择最佳k
best_k = max(results, key=lambda k: results[k]['f1_score'])
print(f"最佳k值: {best_k}")
    """)

    print("\n监控指标:")
    print("  • 检索延迟: 确保用户体验")
    print("  • 命中率: 查询找到相关文档的比例")
    print("  • 平均排名: 相关文档的平均位置")
    print("  • 用户满意度: 最终目标\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 05: 检索策略")
    print("="*70)

    try:
        # 示例1: 相似度搜索
        demo_similarity_search()

        # 示例2: MMR
        demo_mmr()

        # 示例3: 多查询检索器
        demo_multi_query_retriever()

        # 示例4: 自查询检索器
        demo_self_query_retriever()

        # 示例5: 父文档检索器
        demo_parent_document_retriever()

        # 示例6: 时间加权检索
        demo_time_weighted_retrieval()

        # 示例7: 策略对比
        demo_strategy_comparison()

        # 示例8: 参数优化
        demo_parameter_optimization()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • 相似度搜索: 最基础，适合快速开始")
        print("    • MMR: 提供多样性，推荐使用")
        print("    • 多查询/自查询: 复杂场景，需要LLM")
        print("    • 根据场景选择合适的策略")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
