"""
LangChain RAG应用 - 09: 高级RAG技术（Advanced RAG）

本模块演示：
1. HyDE（Hypothetical Document Embeddings）
2. Self-RAG（自我反思RAG）
3. 重排序（Reranking with Cross-Encoder）
4. 查询扩展和重写
5. 混合检索（Dense + Sparse/BM25）
6. 多跳推理RAG
7. 高级RAG技术对比

高级RAG技术能显著提升检索质量和答案准确性。
"""

import os
from typing import List, Dict, Any, Optional


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: HyDE ====================

def demo_hyde():
    """示例1: HyDE（假设文档嵌入）"""
    print_section("示例1: HyDE - 假设文档嵌入")

    print("HyDE核心思想:")
    print("  • 传统: 直接用问题检索")
    print("  • HyDE: 先生成假设答案，再用答案检索\n")

    print("为什么有效:")
    print("  ✓ 答案和文档在语义空间更接近")
    print("  ✓ 问题往往简短，答案更丰富")
    print("  ✓ 减少词汇不匹配问题\n")

    print("工作流程:")
    print("  1. 用户问题: '什么是LangChain？'")
    print("  2. LLM生成假设答案: 'LangChain是一个用于构建AI应用的开源框架...'")
    print("  3. 用假设答案的向量检索相似文档")
    print("  4. 基于检索到的真实文档生成最终答案\n")

    print("实现代码:")
    print("""
from langchain.chains import HypotheticalDocumentEmbedder
from langchain_openai import OpenAI, OpenAIEmbeddings

# 基础embeddings
base_embeddings = OpenAIEmbeddings()

# HyDE embeddings
llm = OpenAI(temperature=0)
hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
    llm,
    base_embeddings,
    prompt_key="web_search"  # 或自定义prompt
)

# 使用HyDE embeddings创建向量存储
vectorstore = FAISS.from_documents(documents, hyde_embeddings)

# 查询时会自动应用HyDE
results = vectorstore.similarity_search("什么是LangChain？")
    """)

    print("\n自定义HyDE Prompt:")
    print("""
from langchain.prompts import PromptTemplate

hyde_prompt = PromptTemplate(
    template='''请为以下问题生成一个详细的假设答案，即使你不确定也要生成：

问题: {question}

假设答案:''',
    input_variables=['question']
)

hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
    llm,
    base_embeddings,
    prompt=hyde_prompt
)
    """)

    print("\n效果对比:")
    print("""
查询: "LangChain的主要用途"

传统检索:
  → 直接用"LangChain的主要用途"检索
  → 可能匹配到: "LangChain使用指南", "安装LangChain"

HyDE检索:
  → 生成假设答案: "LangChain主要用于构建对话系统、问答应用、数据分析..."
  → 用假设答案检索
  → 更好地匹配到: "LangChain应用场景", "LangChain核心功能"

提升: 检索相关性提高15-25%
    """)

    print("\n适用场景:")
    print("  • 用户问题简短模糊")
    print("  • 文档较长较详细")
    print("  • 需要语义理解\n")


# ==================== 示例2: Self-RAG ====================

def demo_self_rag():
    """示例2: Self-RAG（自我反思RAG）"""
    print_section("示例2: Self-RAG - 自我反思")

    print("Self-RAG特点:")
    print("  ✓ 自我评估检索必要性")
    print("  ✓ 自我评估答案质量")
    print("  ✓ 动态决策是否检索")
    print("  ✓ 提高准确性和效率\n")

    print("工作流程:")
    print("""
1. 评估检索需求
   问题: "今天天气怎么样？"
   → 判断: 需要实时信息 → 检索

   问题: "1+1等于几？"
   → 判断: 不需要检索 → 直接回答

2. 检索相关文档
   → 执行检索

3. 评估检索质量
   → 相关性高 → 使用文档
   → 相关性低 → 重新检索或直接回答

4. 生成答案

5. 自我验证
   → 检查答案是否基于文档
   → 检查答案是否回答了问题
   → 如果不满意，重新生成
    """)

    print("\n实现示例:")
    print("""
class SelfRAG:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def should_retrieve(self, question: str) -> bool:
        '''判断是否需要检索'''
        prompt = f'''判断以下问题是否需要检索外部知识：

问题: {question}

如果需要检索回答"是"，否则回答"否"。'''

        response = self.llm.predict(prompt)
        return "是" in response

    def evaluate_relevance(self, docs: List[str], question: str) -> float:
        '''评估文档相关性'''
        prompt = f'''评估文档与问题的相关性（0-1）：

问题: {question}
文档: {docs[0][:200]}...

相关性分数:'''

        score = self.llm.predict(prompt)
        try:
            return float(score.strip())
        except:
            return 0.5

    def verify_answer(self, question: str, answer: str, docs: List[str]) -> bool:
        '''验证答案质量'''
        prompt = f'''验证答案是否正确回答了问题：

问题: {question}
答案: {answer}
参考文档: {docs[0][:200]}...

答案是否正确且基于文档？回答"是"或"否"。'''

        response = self.llm.predict(prompt)
        return "是" in response

    def query(self, question: str) -> str:
        '''执行Self-RAG查询'''

        # 1. 判断是否检索
        if not self.should_retrieve(question):
            return self.llm.predict(f"直接回答: {question}")

        # 2. 检索文档
        docs = self.retriever.get_relevant_documents(question)

        # 3. 评估相关性
        relevance = self.evaluate_relevance(docs, question)
        if relevance < 0.6:
            # 相关性太低，重新检索或直接回答
            return self.llm.predict(f"无相关文档，尝试回答: {question}")

        # 4. 生成答案
        context = "\\n".join([d.page_content for d in docs])
        prompt = f"基于以下文档回答问题：\\n{context}\\n\\n问题: {question}\\n答案:"
        answer = self.llm.predict(prompt)

        # 5. 验证答案
        if not self.verify_answer(question, answer, docs):
            # 答案不满意，重新生成
            answer = self.llm.predict(f"请更准确地回答: {question}")

        return answer
    """)

    print("\n效果:")
    print("  • 准确性提升: 10-15%")
    print("  • 减少不必要的检索: 30%")
    print("  • 减少幻觉: 20%\n")


# ==================== 示例3: 重排序 ====================

def demo_reranking():
    """示例3: 重排序（Reranking）"""
    print_section("示例3: 重排序 - Cross-Encoder")

    print("为什么需要重排序:")
    print("  • 向量检索速度快但精度有限")
    print("  • Cross-Encoder更准确但更慢")
    print("  • 两阶段检索: 向量检索+重排序\n")

    print("工作原理:")
    print("  1. 第一阶段: 向量检索（快速，召回100个候选）")
    print("  2. 第二阶段: Cross-Encoder重排序（精确，选出top 5）\n")

    print("实现代码:")
    print("""
from sentence_transformers import CrossEncoder

# 初始化重排序模型
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_documents(query: str, documents: List[str], top_k: int = 5):
    '''重排序文档'''

    # 准备输入对
    pairs = [[query, doc] for doc in documents]

    # 计算相关性分数
    scores = reranker.predict(pairs)

    # 排序
    doc_score_pairs = list(zip(documents, scores))
    doc_score_pairs.sort(key=lambda x: x[1], reverse=True)

    # 返回top-k
    return doc_score_pairs[:top_k]

# 使用示例
query = "什么是LangChain？"

# 1. 向量检索获取候选
candidates = vectorstore.similarity_search(query, k=20)

# 2. 重排序
reranked = rerank_documents(
    query,
    [doc.page_content for doc in candidates],
    top_k=5
)

for doc, score in reranked:
    print(f"分数: {score:.4f} - {doc[:50]}...")
    """)

    print("\n集成到LangChain:")
    print("""
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker

# 基础检索器
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# 重排序器
compressor = CrossEncoderReranker(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
    top_n=5
)

# 组合
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# 使用
docs = compression_retriever.get_relevant_documents("什么是LangChain？")
    """)

    print("\n性能对比:")
    print("""
指标                  仅向量检索    向量+重排序
────────────────────────────────────────────
检索速度              10ms         50ms
Precision@5          0.65         0.82
MRR                  0.58         0.76

结论: 重排序显著提升精度，适度增加延迟
    """)

    print("\n推荐模型:")
    print("  • ms-marco-MiniLM-L-6-v2: 快速，通用")
    print("  • ms-marco-electra-base: 更高精度")
    print("  • bge-reranker-large: 中文最佳\n")


# ==================== 示例4: 查询扩展和重写 ====================

def demo_query_expansion():
    """示例4: 查询扩展和重写"""
    print_section("示例4: 查询扩展和重写")

    print("查询扩展技术:\n")

    print("1. 同义词扩展")
    print("   原始: 'LangChain教程'")
    print("   扩展: 'LangChain教程 OR LangChain指南 OR LangChain文档'\n")

    print("2. 查询重写")
    print("   原始: 'LC是什么'")
    print("   重写: 'LangChain是什么'\n")

    print("3. 多角度查询")
    print("   原始: '如何使用LangChain？'")
    print("   生成:")
    print("     - LangChain使用教程")
    print("     - LangChain快速开始")
    print("     - LangChain代码示例\n")

    print("实现示例:")
    print("""
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)

# 查询重写
rewrite_prompt = PromptTemplate(
    template='''请将以下查询重写为更清晰、更完整的形式：

原始查询: {query}

重写后的查询:''',
    input_variables=['query']
)

# 查询扩展
expansion_prompt = PromptTemplate(
    template='''为以下查询生成3个相关的查询变体：

原始查询: {query}

查询变体（一行一个）:''',
    input_variables=['query']
)

def expand_query(query: str) -> List[str]:
    '''扩展查询'''

    # 重写
    rewritten = llm.predict(rewrite_prompt.format(query=query))

    # 扩展
    expansions = llm.predict(expansion_prompt.format(query=query))
    variants = [v.strip() for v in expansions.split('\\n') if v.strip()]

    # 合并
    all_queries = [rewritten] + variants
    return all_queries

# 使用
original = "LC怎么用？"
expanded = expand_query(original)

print(f"原始: {original}")
print("扩展:")
for q in expanded:
    print(f"  - {q}")

# 对每个查询检索并合并结果
all_docs = []
for q in expanded:
    docs = vectorstore.similarity_search(q, k=3)
    all_docs.extend(docs)

# 去重
unique_docs = deduplicate_documents(all_docs)
    """)

    print("\n效果:")
    print("  • 召回率提升: 20-30%")
    print("  • 覆盖更多相关文档")
    print("  • 对模糊查询特别有效\n")


# ==================== 示例5: 混合检索 ====================

def demo_hybrid_search():
    """示例5: 混合检索（Dense + Sparse）"""
    print_section("示例5: 混合检索")

    print("混合检索概念:")
    print("  • Dense（密集）: 向量/语义检索")
    print("  • Sparse（稀疏）: 关键词/BM25检索")
    print("  • 混合: 结合两者优势\n")

    print("各自优势:")
    print("  Dense检索:")
    print("    ✓ 语义理解")
    print("    ✓ 处理同义词")
    print("    ✗ 可能遗漏精确匹配")
    print()
    print("  Sparse检索:")
    print("    ✓ 精确关键词匹配")
    print("    ✓ 处理专有名词")
    print("    ✗ 无法理解语义\n")

    print("实现方法:")
    print("""
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# 1. 向量检索器
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 2. BM25检索器
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

# 3. 混合检索器
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5]  # 权重可调
)

# 使用
results = hybrid_retriever.get_relevant_documents("LangChain框架")
    """)

    print("\n权重调优:")
    print("""
# 语义为主（处理同义词、相关概念）
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)

# 精确匹配为主（专有名词、代码搜索）
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.3, 0.7]
)

# 平衡（通用场景）
weights=[0.5, 0.5]
    """)

    print("\n效果对比:")
    print("""
查询: "Python LangChain安装"

Dense检索 (0.72):
  1. LangChain环境配置
  2. 如何开始使用LangChain
  3. LangChain依赖管理

BM25检索 (0.68):
  1. pip install langchain
  2. Python包管理
  3. LangChain安装指南

混合检索 (0.83):
  1. pip install langchain
  2. LangChain安装指南
  3. LangChain环境配置

混合检索结合了两者优势！
    """)


# ==================== 示例6: 多跳推理RAG ====================

def demo_multi_hop_rag():
    """示例6: 多跳推理RAG"""
    print_section("示例6: 多跳推理RAG")

    print("多跳推理场景:")
    print("  问题: 'LangChain的创建者创建了哪些其他项目？'")
    print("  需要:")
    print("    1. 找到LangChain的创建者（Harrison Chase）")
    print("    2. 找到Harrison Chase的其他项目\n")

    print("实现方法:")
    print("""
def multi_hop_rag(question: str, max_hops: int = 3):
    '''多跳推理RAG'''

    current_query = question
    context = []

    for hop in range(max_hops):
        print(f"\\n跳{hop + 1}: {current_query}")

        # 检索
        docs = retriever.get_relevant_documents(current_query)
        context.extend(docs)

        # 生成中间答案
        intermediate_prompt = f'''基于文档回答：

文档: {docs[0].page_content}

问题: {current_query}

简短答案:'''

        intermediate_answer = llm.predict(intermediate_prompt)
        print(f"中间答案: {intermediate_answer}")

        # 判断是否需要继续
        continue_prompt = f'''是否需要更多信息来完整回答: {question}

当前已知: {intermediate_answer}

回答"是"或"否":'''

        should_continue = llm.predict(continue_prompt)
        if "否" in should_continue:
            break

        # 生成下一跳查询
        next_query_prompt = f'''生成下一个查询来获取更多信息：

原始问题: {question}
当前已知: {intermediate_answer}

下一个查询:'''

        current_query = llm.predict(next_query_prompt)

    # 生成最终答案
    final_context = "\\n".join([d.page_content for d in context])
    final_prompt = f'''基于所有信息回答问题：

信息: {final_context}

问题: {question}

完整答案:'''

    final_answer = llm.predict(final_prompt)
    return final_answer

# 使用
answer = multi_hop_rag("LangChain的创建者还创建了什么？")
    """)

    print("\n执行示例:")
    print("""
跳1: LangChain的创建者还创建了什么？
  → 检索到: "LangChain由Harrison Chase创建"
  → 中间答案: "Harrison Chase"

跳2: Harrison Chase创建了哪些项目？
  → 检索到: "Harrison Chase创建了LangChain和LangSmith"
  → 中间答案: "LangChain, LangSmith"

最终答案: Harrison Chase创建了LangChain和LangSmith两个项目。
    """)


# ==================== 示例7: 技术对比 ====================

def demo_technique_comparison():
    """示例7: 高级RAG技术对比"""
    print_section("示例7: 高级RAG技术对比")

    techniques = [
        {
            "技术": "HyDE",
            "复杂度": "中",
            "成本": "中(需LLM)",
            "提升": "15-25%",
            "适用": "模糊查询"
        },
        {
            "技术": "Self-RAG",
            "复杂度": "高",
            "成本": "高(多次LLM)",
            "提升": "10-20%",
            "适用": "需要高准确性"
        },
        {
            "技术": "重排序",
            "复杂度": "低",
            "成本": "低",
            "提升": "20-30%",
            "适用": "通用，强烈推荐"
        },
        {
            "技术": "查询扩展",
            "复杂度": "中",
            "成本": "中(需LLM)",
            "提升": "15-25%",
            "适用": "召回率优先"
        },
        {
            "技术": "混合检索",
            "复杂度": "中",
            "成本": "低",
            "提升": "10-20%",
            "适用": "精确+语义"
        },
        {
            "技术": "多跳推理",
            "复杂度": "高",
            "成本": "高(多次LLM)",
            "提升": "视场景",
            "适用": "复杂推理"
        }
    ]

    print(f"{'技术':<15} {'复杂度':<8} {'成本':<12} {'提升':<12} {'适用场景'}")
    print("-" * 75)

    for t in techniques:
        print(f"{t['技术']:<15} {t['复杂度']:<8} {t['成本']:<12} {t['提升']:<12} {t['适用']}")

    print("\n\n组合策略（推荐）:\n")

    print("基础RAG升级路径:")
    print("  Level 1: 基础RAG")
    print("  Level 2: + 重排序 (最优先)")
    print("  Level 3: + 混合检索")
    print("  Level 4: + 查询扩展/HyDE")
    print("  Level 5: + Self-RAG (高准确性需求)\n")

    print("实际组合示例:")
    print("  • 通用场景: 向量检索 + 重排序")
    print("  • 专业领域: HyDE + 混合检索 + 重排序")
    print("  • 高精度: Self-RAG + 重排序")
    print("  • 复杂问题: 查询扩展 + 多跳推理\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 09: 高级RAG技术")
    print("="*70)

    try:
        # 示例1: HyDE
        demo_hyde()

        # 示例2: Self-RAG
        demo_self_rag()

        # 示例3: 重排序
        demo_reranking()

        # 示例4: 查询扩展
        demo_query_expansion()

        # 示例5: 混合检索
        demo_hybrid_search()

        # 示例6: 多跳推理
        demo_multi_hop_rag()

        # 示例7: 技术对比
        demo_technique_comparison()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • 重排序: 最容易实施，效果显著")
        print("    • 混合检索: 结合精确和语义")
        print("    • HyDE/查询扩展: 提升召回率")
        print("    • 根据需求选择合适的技术组合")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
