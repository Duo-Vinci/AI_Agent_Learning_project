"""
RAG系统评估
评估检索质量和生成质量
"""

from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """RAG系统评估器"""

    def __init__(self):
        self.metrics = {}

    def evaluate_retrieval(
        self,
        retrieved_docs: List[Document],
        relevant_docs: List[Document],
        k: int = None
    ) -> Dict[str, float]:
        """
        评估检索质量

        Args:
            retrieved_docs: 检索到的文档列表
            relevant_docs: 相关文档列表（ground truth）
            k: Top-K评估

        Returns:
            评估指标字典
        """
        if k is None:
            k = len(retrieved_docs)

        # 提取文档内容用于比较
        retrieved_contents = set([doc.page_content for doc in retrieved_docs[:k]])
        relevant_contents = set([doc.page_content for doc in relevant_docs])

        # 计算指标
        true_positives = len(retrieved_contents & relevant_contents)
        false_positives = len(retrieved_contents - relevant_contents)
        false_negatives = len(relevant_contents - retrieved_contents)

        # Precision: 检索到的相关文档占检索文档的比例
        precision = true_positives / len(retrieved_contents) if retrieved_contents else 0

        # Recall: 检索到的相关文档占所有相关文档的比例
        recall = true_positives / len(relevant_contents) if relevant_contents else 0

        # F1 Score: Precision和Recall的调和平均
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Mean Reciprocal Rank (MRR): 第一个相关文档的排名倒数
        mrr = 0
        for i, doc in enumerate(retrieved_docs[:k]):
            if doc.page_content in relevant_contents:
                mrr = 1 / (i + 1)
                break

        # NDCG (简化版): 归一化折扣累计增益
        dcg = 0
        idcg = 0
        for i in range(min(k, len(retrieved_docs))):
            relevance = 1 if retrieved_docs[i].page_content in relevant_contents else 0
            dcg += relevance / np.log2(i + 2)

        for i in range(min(k, len(relevant_contents))):
            idcg += 1 / np.log2(i + 2)

        ndcg = dcg / idcg if idcg > 0 else 0

        metrics = {
            f"Precision@{k}": precision,
            f"Recall@{k}": recall,
            f"F1@{k}": f1,
            "MRR": mrr,
            f"NDCG@{k}": ndcg,
            "Retrieved": len(retrieved_contents),
            "Relevant": len(relevant_contents),
            "True Positives": true_positives
        }

        logger.info(f"检索评估完成: Precision={precision:.2%}, Recall={recall:.2%}, F1={f1:.2%}")
        return metrics

    def evaluate_answer_relevance(
        self,
        answer: str,
        query: str,
        embeddings
    ) -> float:
        """
        评估答案与查询的相关性

        Args:
            answer: 生成的答案
            query: 原始查询
            embeddings: Embedding模型

        Returns:
            相关性分数 (0-1)
        """
        try:
            answer_emb = embeddings.embed_query(answer)
            query_emb = embeddings.embed_query(query)

            similarity = cosine_similarity([answer_emb], [query_emb])[0][0]
            logger.info(f"答案相关性: {similarity:.4f}")
            return float(similarity)

        except Exception as e:
            logger.error(f"评估答案相关性失败: {e}")
            return 0.0

    def evaluate_faithfulness(
        self,
        answer: str,
        context_docs: List[Document]
    ) -> float:
        """
        评估答案忠实度（答案是否基于上下文）
        简化版：检查答案中的关键词是否来自上下文

        Args:
            answer: 生成的答案
            context_docs: 上下文文档

        Returns:
            忠实度分数 (0-1)
        """
        # 提取答案中的关键词
        answer_words = set(answer.lower().split())

        # 提取上下文中的词
        context_text = " ".join([doc.page_content for doc in context_docs])
        context_words = set(context_text.lower().split())

        # 计算答案词汇在上下文中的覆盖率
        common_words = answer_words & context_words
        faithfulness = len(common_words) / len(answer_words) if answer_words else 0

        logger.info(f"答案忠实度: {faithfulness:.2%}")
        return faithfulness

    def evaluate_context_relevance(
        self,
        context_docs: List[Document],
        query: str,
        embeddings
    ) -> float:
        """
        评估上下文相关性

        Args:
            context_docs: 检索到的上下文文档
            query: 查询
            embeddings: Embedding模型

        Returns:
            平均相关性分数
        """
        try:
            query_emb = embeddings.embed_query(query)
            doc_embeddings = [embeddings.embed_query(doc.page_content) for doc in context_docs]

            similarities = [
                cosine_similarity([query_emb], [doc_emb])[0][0]
                for doc_emb in doc_embeddings
            ]

            avg_relevance = np.mean(similarities) if similarities else 0
            logger.info(f"上下文平均相关性: {avg_relevance:.4f}")
            return float(avg_relevance)

        except Exception as e:
            logger.error(f"评估上下文相关性失败: {e}")
            return 0.0

    def evaluate_comprehensive(
        self,
        query: str,
        retrieved_docs: List[Document],
        relevant_docs: List[Document],
        answer: str,
        embeddings,
        k: int = 4
    ) -> Dict[str, float]:
        """
        综合评估RAG系统

        Args:
            query: 查询
            retrieved_docs: 检索到的文档
            relevant_docs: 相关文档（ground truth）
            answer: 生成的答案
            embeddings: Embedding模型
            k: Top-K

        Returns:
            综合评估指标
        """
        logger.info("开始综合评估...")

        metrics = {}

        # 1. 检索质量
        retrieval_metrics = self.evaluate_retrieval(retrieved_docs, relevant_docs, k)
        metrics.update(retrieval_metrics)

        # 2. 答案相关性
        answer_relevance = self.evaluate_answer_relevance(answer, query, embeddings)
        metrics["Answer Relevance"] = answer_relevance

        # 3. 答案忠实度
        faithfulness = self.evaluate_faithfulness(answer, retrieved_docs[:k])
        metrics["Faithfulness"] = faithfulness

        # 4. 上下文相关性
        context_relevance = self.evaluate_context_relevance(retrieved_docs[:k], query, embeddings)
        metrics["Context Relevance"] = context_relevance

        logger.info("综合评估完成")
        return metrics


def demo():
    """演示RAG评估"""
    print("=== RAG系统评估演示 ===\n")

    # 模拟数据
    query = "什么是深度学习？"

    # 检索到的文档
    retrieved_docs = [
        Document(page_content="深度学习是机器学习的一个分支，使用多层神经网络。"),
        Document(page_content="卷积神经网络主要用于图像识别。"),
        Document(page_content="自然语言处理是AI的重要领域。"),
        Document(page_content="循环神经网络适合处理序列数据。"),
    ]

    # 真正相关的文档（ground truth）
    relevant_docs = [
        Document(page_content="深度学习是机器学习的一个分支，使用多层神经网络。"),
        Document(page_content="深度学习使用神经网络模拟人脑学习过程。"),
    ]

    # 生成的答案
    answer = "深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的表示。深度学习在图像识别、语音识别等领域取得了突破性进展。"

    # 创建评估器
    evaluator = RAGEvaluator()

    # 评估1: 检索质量
    print("=== 评估1: 检索质量 ===")
    retrieval_metrics = evaluator.evaluate_retrieval(
        retrieved_docs=retrieved_docs,
        relevant_docs=relevant_docs,
        k=4
    )

    for metric, value in retrieval_metrics.items():
        if isinstance(value, float):
            print(f"{metric}: {value:.4f}")
        else:
            print(f"{metric}: {value}")
    print()

    # 评估2: 答案忠实度（不需要Embedding）
    print("=== 评估2: 答案忠实度 ===")
    faithfulness = evaluator.evaluate_faithfulness(answer, retrieved_docs)
    print(f"Faithfulness: {faithfulness:.4f}")
    print(f"说明: {faithfulness*100:.1f}% 的答案词汇来自检索到的文档\n")

    # 评估3: 使用模拟Embedding进行完整评估
    print("=== 评估3: 综合评估（使用模拟Embedding） ===")
    print("注意: 实际使用时应加载真实Embedding模型\n")

    from langchain.embeddings.base import Embeddings

    class MockEmbeddings(Embeddings):
        """模拟Embedding"""
        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return [self.embed_query(text) for text in texts]

        def embed_query(self, text: str) -> List[float]:
            np.random.seed(hash(text) % (2**32))
            return np.random.randn(384).tolist()

    mock_embeddings = MockEmbeddings()

    comprehensive_metrics = evaluator.evaluate_comprehensive(
        query=query,
        retrieved_docs=retrieved_docs,
        relevant_docs=relevant_docs,
        answer=answer,
        embeddings=mock_embeddings,
        k=4
    )

    print("综合评估结果:")
    print("-" * 50)
    for metric, value in comprehensive_metrics.items():
        if isinstance(value, float):
            print(f"{metric:.<30} {value:.4f}")
        else:
            print(f"{metric:.<30} {value}")

    # 评估指南
    print("\n" + "=" * 60)
    print("评估指标说明")
    print("=" * 60)
    print("""
检索质量指标:
  - Precision: 检索到的相关文档占检索文档的比例（越高越好）
  - Recall: 检索到的相关文档占所有相关文档的比例（越高越好）
  - F1 Score: Precision和Recall的调和平均
  - MRR: 第一个相关文档的排名倒数
  - NDCG: 归一化折扣累计增益，考虑排序质量

生成质量指标:
  - Answer Relevance: 答案与查询的相关性（0-1）
  - Faithfulness: 答案是否基于检索文档（0-1）
  - Context Relevance: 检索文档与查询的相关性（0-1）

建议阈值:
  - Precision > 0.6
  - Recall > 0.5
  - Faithfulness > 0.7
  - Answer Relevance > 0.6
    """)

    print("\n使用真实Embedding模型的方法:")
    print("-" * 60)
    print("""
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={'device': 'cpu'}
)

metrics = evaluator.evaluate_comprehensive(
    query=query,
    retrieved_docs=retrieved_docs,
    relevant_docs=relevant_docs,
    answer=answer,
    embeddings=embeddings,
    k=4
)
    """)


if __name__ == "__main__":
    demo()
