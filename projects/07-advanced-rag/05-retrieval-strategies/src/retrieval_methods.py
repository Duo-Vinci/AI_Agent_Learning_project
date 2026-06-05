"""
检索策略实现
包括相似度搜索、MMR、混合检索等
"""

from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalStrategies:
    """检索策略类"""

    def __init__(
        self,
        documents: List[Document],
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5"
    ):
        """
        初始化检索策略

        Args:
            documents: 文档列表
            embedding_model_name: Embedding模型名称
        """
        self.documents = documents

        # 初始化Embedding
        logger.info("初始化Embedding模型...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 创建向量存储
        logger.info("创建向量存储...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        基本相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            文档列表
        """
        logger.info(f"执行相似度搜索: {query}")
        results = self.vectorstore.similarity_search(query, k=k)
        return results

    def similarity_search_with_threshold(
        self,
        query: str,
        k: int = 4,
        threshold: float = 0.5
    ) -> List[Document]:
        """
        带阈值的相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            threshold: 相似度阈值

        Returns:
            文档列表
        """
        logger.info(f"执行带阈值的相似度搜索: {query}, threshold={threshold}")
        results_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)

        # 过滤低于阈值的结果
        filtered_results = [
            doc for doc, score in results_with_scores
            if score >= threshold
        ]

        logger.info(f"过滤后返回 {len(filtered_results)} 个结果")
        return filtered_results

    def mmr_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Document]:
        """
        最大边际相关性搜索（MMR）- 提高结果多样性

        Args:
            query: 查询文本
            k: 返回结果数量
            fetch_k: 候选结果数量
            lambda_mult: 相关性与多样性的权衡 (0=最大多样性, 1=最大相关性)

        Returns:
            文档列表
        """
        logger.info(f"执行MMR搜索: {query}, lambda={lambda_mult}")
        results = self.vectorstore.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult
        )
        return results

    def hybrid_search(
        self,
        query: str,
        k: int = 4,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4
    ) -> List[Document]:
        """
        混合检索（向量检索 + BM25关键词检索）

        Args:
            query: 查询文本
            k: 返回结果数量
            vector_weight: 向量检索权重
            bm25_weight: BM25权重

        Returns:
            文档列表
        """
        logger.info(f"执行混合检索: {query}")

        # 向量检索器
        vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )

        # BM25关键词检索器
        bm25_retriever = BM25Retriever.from_documents(self.documents)
        bm25_retriever.k = k

        # 混合检索器
        ensemble_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[vector_weight, bm25_weight]
        )

        results = ensemble_retriever.get_relevant_documents(query)
        return results

    def multi_query_search(
        self,
        queries: List[str],
        k: int = 4
    ) -> List[Document]:
        """
        多查询检索（合并多个查询的结果）

        Args:
            queries: 查询列表
            k: 每个查询返回的结果数量

        Returns:
            合并后的文档列表
        """
        logger.info(f"执行多查询检索: {len(queries)} 个查询")

        all_results = []
        seen_contents = set()

        for query in queries:
            results = self.similarity_search(query, k=k)
            for doc in results:
                # 去重
                if doc.page_content not in seen_contents:
                    all_results.append(doc)
                    seen_contents.add(doc.page_content)

        logger.info(f"合并后返回 {len(all_results)} 个唯一结果")
        return all_results

    def contextual_compression_search(
        self,
        query: str,
        k: int = 4
    ) -> List[Document]:
        """
        上下文压缩检索（提取相关片段）
        注: 这里使用简化版本，实际应用可使用LLM进行压缩

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            文档列表
        """
        logger.info(f"执行上下文压缩检索: {query}")

        # 先进行相似度搜索
        results = self.similarity_search(query, k=k)

        # 简化版：只保留包含查询关键词的句子
        query_keywords = set(query.lower().split())
        compressed_results = []

        for doc in results:
            sentences = doc.page_content.split('。')
            relevant_sentences = [
                s for s in sentences
                if any(keyword in s.lower() for keyword in query_keywords)
            ]

            if relevant_sentences:
                compressed_doc = Document(
                    page_content='。'.join(relevant_sentences) + '。',
                    metadata=doc.metadata
                )
                compressed_results.append(compressed_doc)
            else:
                compressed_results.append(doc)

        return compressed_results


def demo():
    """演示不同的检索策略"""
    print("=== 检索策略演示 ===\n")

    # 创建示例文档
    documents = [
        Document(page_content="深度学习是机器学习的一个分支，使用多层神经网络进行学习。", metadata={"id": 1, "topic": "深度学习"}),
        Document(page_content="卷积神经网络（CNN）主要用于图像识别和计算机视觉任务。", metadata={"id": 2, "topic": "CNN"}),
        Document(page_content="循环神经网络（RNN）适合处理序列数据，如文本和时间序列。", metadata={"id": 3, "topic": "RNN"}),
        Document(page_content="Transformer架构使用自注意力机制，彻底改变了NLP领域。", metadata={"id": 4, "topic": "Transformer"}),
        Document(page_content="BERT是基于Transformer的预训练模型，在多个NLP任务上表现出色。", metadata={"id": 5, "topic": "BERT"}),
        Document(page_content="GPT系列模型是自回归语言模型，擅长文本生成任务。", metadata={"id": 6, "topic": "GPT"}),
        Document(page_content="强化学习让智能体通过与环境交互来学习最优策略。", metadata={"id": 7, "topic": "强化学习"}),
        Document(page_content="迁移学习利用预训练模型，在新任务上快速取得好效果。", metadata={"id": 8, "topic": "迁移学习"}),
    ]

    print("注意: 首次运行会下载模型，需要等待...\n")

    try:
        # 初始化检索策略
        retriever = RetrievalStrategies(
            documents=documents,
            embedding_model_name="BAAI/bge-small-zh-v1.5"
        )

        query = "什么是神经网络？"

        # 策略1: 基本相似度搜索
        print("=== 策略1: 基本相似度搜索 ===")
        print(f"查询: {query}\n")
        results = retriever.similarity_search(query, k=3)
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.page_content}")
        print()

        # 策略2: MMR搜索（提高多样性）
        print("=== 策略2: MMR搜索（提高多样性） ===")
        mmr_results = retriever.mmr_search(query, k=3, lambda_mult=0.3)
        for i, doc in enumerate(mmr_results):
            print(f"{i+1}. {doc.page_content}")
            print(f"   主题: {doc.metadata.get('topic')}")
        print()

        # 策略3: 混合检索
        print("=== 策略3: 混合检索（向量+BM25） ===")
        hybrid_results = retriever.hybrid_search(query, k=3)
        for i, doc in enumerate(hybrid_results):
            print(f"{i+1}. {doc.page_content}")
        print()

        # 策略4: 多查询检索
        print("=== 策略4: 多查询检索 ===")
        queries = [
            "神经网络是什么？",
            "深度学习模型有哪些？",
            "如何训练神经网络？"
        ]
        print(f"查询列表: {queries}\n")
        multi_results = retriever.multi_query_search(queries, k=2)
        for i, doc in enumerate(multi_results[:5]):  # 只显示前5个
            print(f"{i+1}. {doc.page_content}")
        print()

        # 策略5: 上下文压缩
        print("=== 策略5: 上下文压缩检索 ===")
        compressed_results = retriever.contextual_compression_search(query, k=3)
        for i, doc in enumerate(compressed_results):
            print(f"{i+1}. {doc.page_content}")
        print()

        # 对比不同lambda值的MMR结果
        print("=== MMR参数对比 ===")
        lambda_values = [0.0, 0.5, 1.0]
        for lambda_val in lambda_values:
            print(f"\nlambda = {lambda_val} ({'最大多样性' if lambda_val == 0 else '最大相关性' if lambda_val == 1 else '平衡'}):")
            results = retriever.mmr_search(query, k=3, lambda_mult=lambda_val)
            for i, doc in enumerate(results):
                print(f"  {i+1}. 主题: {doc.metadata.get('topic')}")

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("\n提示:")
        print("1. 确保已安装: pip install faiss-cpu sentence-transformers rank-bm25")
        print("2. 首次运行需要下载模型")


if __name__ == "__main__":
    demo()
