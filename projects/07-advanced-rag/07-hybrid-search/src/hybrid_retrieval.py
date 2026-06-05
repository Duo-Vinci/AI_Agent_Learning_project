"""
混合搜索实现
结合密集检索（向量）和稀疏检索（BM25）
"""

from typing import List, Dict, Optional
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from rank_bm25 import BM25Okapi
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridSearchRetriever:
    """混合搜索检索器"""

    def __init__(
        self,
        documents: List[Document],
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5",
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4
    ):
        """
        初始化混合搜索

        Args:
            documents: 文档列表
            embedding_model_name: Embedding模型名称
            dense_weight: 密集检索权重
            sparse_weight: 稀疏检索权重
        """
        self.documents = documents
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

        logger.info("初始化混合搜索检索器...")

        # 初始化Embedding模型
        logger.info("加载Embedding模型...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 创建密集向量检索器
        logger.info("创建密集向量检索器...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.dense_retriever = self.vectorstore.as_retriever()

        # 创建稀疏BM25检索器
        logger.info("创建BM25稀疏检索器...")
        self.sparse_retriever = BM25Retriever.from_documents(documents)

        # 创建混合检索器
        self.hybrid_retriever = EnsembleRetriever(
            retrievers=[self.dense_retriever, self.sparse_retriever],
            weights=[dense_weight, sparse_weight]
        )

        logger.info("混合搜索检索器初始化完成")

    def search(self, query: str, k: int = 4) -> List[Document]:
        """
        执行混合搜索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            文档列表
        """
        self.dense_retriever.search_kwargs = {"k": k}
        self.sparse_retriever.k = k

        results = self.hybrid_retriever.get_relevant_documents(query)
        logger.info(f"混合搜索完成，返回 {len(results)} 个结果")
        return results[:k]

    def dense_search(self, query: str, k: int = 4) -> List[Document]:
        """
        只使用密集检索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            文档列表
        """
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info(f"密集检索完成，返回 {len(results)} 个结果")
        return results

    def sparse_search(self, query: str, k: int = 4) -> List[Document]:
        """
        只使用稀疏检索（BM25）

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            文档列表
        """
        self.sparse_retriever.k = k
        results = self.sparse_retriever.get_relevant_documents(query)
        logger.info(f"稀疏检索完成，返回 {len(results)} 个结果")
        return results[:k]

    def compare_methods(self, query: str, k: int = 4) -> Dict[str, List[Document]]:
        """
        对比三种检索方法的结果

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            三种方法的结果字典
        """
        results = {
            "密集检索（向量）": self.dense_search(query, k),
            "稀疏检索（BM25）": self.sparse_search(query, k),
            "混合检索": self.search(query, k)
        }
        return results

    def adjust_weights(self, dense_weight: float, sparse_weight: float):
        """
        调整检索权重

        Args:
            dense_weight: 密集检索权重
            sparse_weight: 稀疏检索权重
        """
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

        self.hybrid_retriever = EnsembleRetriever(
            retrievers=[self.dense_retriever, self.sparse_retriever],
            weights=[dense_weight, sparse_weight]
        )

        logger.info(f"权重已调整: 密集={dense_weight}, 稀疏={sparse_weight}")


class AdvancedHybridSearch:
    """高级混合搜索（带重排序）"""

    def __init__(
        self,
        documents: List[Document],
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5"
    ):
        """
        初始化高级混合搜索

        Args:
            documents: 文档列表
            embedding_model_name: Embedding模型名称
        """
        self.documents = documents
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 创建向量存储
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

        # 创建BM25索引
        tokenized_docs = [doc.page_content.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def search_with_reranking(
        self,
        query: str,
        k: int = 4,
        initial_k: int = 20
    ) -> List[Document]:
        """
        带重排序的混合搜索

        Args:
            query: 查询文本
            k: 最终返回结果数量
            initial_k: 初始检索数量

        Returns:
            重排序后的文档列表
        """
        logger.info(f"执行带重排序的混合搜索: {query}")

        # 第1步: 密集检索
        dense_docs = self.vectorstore.similarity_search_with_score(query, k=initial_k)

        # 第2步: 稀疏检索
        query_tokens = query.split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        sparse_indices = np.argsort(bm25_scores)[-initial_k:][::-1]

        # 第3步: 融合分数
        doc_scores = {}

        # 密集检索分数（归一化）
        dense_max = max([score for _, score in dense_docs]) if dense_docs else 1
        for doc, score in dense_docs:
            doc_id = doc.page_content
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (score / dense_max) * 0.6

        # 稀疏检索分数（归一化）
        sparse_max = max(bm25_scores) if max(bm25_scores) > 0 else 1
        for idx in sparse_indices:
            doc_id = self.documents[idx].page_content
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (bm25_scores[idx] / sparse_max) * 0.4

        # 第4步: 按融合分数排序
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        # 第5步: 返回Top-K
        result_docs = []
        for doc_content, score in sorted_docs[:k]:
            for doc in self.documents:
                if doc.page_content == doc_content:
                    result_docs.append(doc)
                    break

        logger.info(f"重排序完成，返回 {len(result_docs)} 个结果")
        return result_docs


def demo():
    """演示混合搜索"""
    print("=== 混合搜索演示 ===\n")

    # 创建示例文档
    documents = [
        Document(page_content="Python是一种高级编程语言，广泛用于数据科学和机器学习。", metadata={"id": 1}),
        Document(page_content="深度学习使用神经网络进行学习，是机器学习的一个分支。", metadata={"id": 2}),
        Document(page_content="自然语言处理（NLP）让计算机理解和生成人类语言。", metadata={"id": 3}),
        Document(page_content="Transformer架构彻底改变了NLP领域，使用自注意力机制。", metadata={"id": 4}),
        Document(page_content="BERT是基于Transformer的预训练模型，在多个任务上表现出色。", metadata={"id": 5}),
        Document(page_content="RAG系统结合检索和生成，提高了答案的准确性和可靠性。", metadata={"id": 6}),
        Document(page_content="向量数据库用于存储和检索高维向量，支持相似度搜索。", metadata={"id": 7}),
        Document(page_content="机器学习算法可以从数据中学习模式，无需显式编程。", metadata={"id": 8}),
    ]

    print("注意: 首次运行会下载模型，需要等待...\n")

    try:
        # 创建混合搜索检索器
        print("=== 初始化混合搜索检索器 ===")
        hybrid_retriever = HybridSearchRetriever(
            documents=documents,
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            dense_weight=0.6,
            sparse_weight=0.4
        )
        print("初始化完成!\n")

        # 测试查询
        query = "什么是自然语言处理？"
        print(f"查询: {query}\n")

        # 对比三种方法
        print("=== 对比三种检索方法 ===")
        comparison = hybrid_retriever.compare_methods(query, k=3)

        for method_name, results in comparison.items():
            print(f"\n{method_name}:")
            for i, doc in enumerate(results):
                print(f"  {i+1}. {doc.page_content}")

        # 测试不同权重
        print("\n\n=== 测试不同权重配置 ===")
        weight_configs = [
            (0.8, 0.2, "向量为主"),
            (0.5, 0.5, "平衡"),
            (0.2, 0.8, "BM25为主")
        ]

        for dense_w, sparse_w, desc in weight_configs:
            print(f"\n{desc} (密集={dense_w}, 稀疏={sparse_w}):")
            hybrid_retriever.adjust_weights(dense_w, sparse_w)
            results = hybrid_retriever.search(query, k=3)
            for i, doc in enumerate(results):
                print(f"  {i+1}. {doc.page_content[:60]}...")

        # 高级混合搜索（带重排序）
        print("\n\n=== 高级混合搜索（带重排序） ===")
        advanced_retriever = AdvancedHybridSearch(
            documents=documents,
            embedding_model_name="BAAI/bge-small-zh-v1.5"
        )

        reranked_results = advanced_retriever.search_with_reranking(query, k=3, initial_k=6)
        print(f"查询: {query}\n")
        for i, doc in enumerate(reranked_results):
            print(f"{i+1}. {doc.page_content}")

        # 对比不同类型的查询
        print("\n\n=== 不同类型查询的效果对比 ===")

        test_queries = [
            ("精确匹配查询", "Transformer架构"),
            ("语义查询", "如何处理文本数据？"),
            ("关键词查询", "机器学习 数据")
        ]

        for query_type, test_query in test_queries:
            print(f"\n{query_type}: {test_query}")
            results = hybrid_retriever.search(test_query, k=2)
            for i, doc in enumerate(results):
                print(f"  {i+1}. {doc.page_content[:60]}...")

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("\n提示:")
        print("1. 确保已安装: pip install faiss-cpu sentence-transformers rank-bm25")
        print("2. 首次运行需要下载模型")

    print("\n" + "=" * 70)
    print("混合搜索的优势")
    print("=" * 70)
    print("""
1. 密集检索（向量）:
   - 优势: 理解语义相似性，处理同义词和改写
   - 劣势: 对精确关键词匹配不敏感

2. 稀疏检索（BM25）:
   - 优势: 精确关键词匹配，对罕见词敏感
   - 劣势: 不理解语义，无法处理同义词

3. 混合检索:
   - 结合两者优势，提供更全面的检索结果
   - 可以根据应用场景调整权重

推荐权重配置:
  - 技术文档: 密集0.7, 稀疏0.3 (重语义)
  - 法律文本: 密集0.4, 稀疏0.6 (重精确匹配)
  - 通用问答: 密集0.6, 稀疏0.4 (平衡)
    """)


if __name__ == "__main__":
    demo()
