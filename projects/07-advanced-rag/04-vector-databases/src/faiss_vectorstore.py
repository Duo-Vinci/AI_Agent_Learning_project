"""
FAISS向量数据库
使用FAISS进行高效的向量检索
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS向量数据库管理类"""

    def __init__(
        self,
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5",
        index_path: Optional[str] = None
    ):
        """
        初始化FAISS向量存储

        Args:
            embedding_model_name: Embedding模型名称
            index_path: 索引保存路径
        """
        self.embedding_model_name = embedding_model_name
        self.index_path = index_path
        self.vectorstore = None

        # 初始化Embedding模型
        logger.info(f"初始化Embedding模型: {embedding_model_name}")
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("Embedding模型加载成功")
        except Exception as e:
            logger.error(f"Embedding模型加载失败: {e}")
            raise

    def create_index(self, documents: List[Document]) -> FAISS:
        """
        创建FAISS索引

        Args:
            documents: 文档列表

        Returns:
            FAISS向量存储对象
        """
        try:
            logger.info(f"创建FAISS索引，文档数量: {len(documents)}")

            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )

            logger.info("FAISS索引创建成功")
            return self.vectorstore

        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            raise

    def add_documents(self, documents: List[Document]):
        """
        向现有索引添加文档

        Args:
            documents: 要添加的文档列表
        """
        if self.vectorstore is None:
            logger.warning("索引不存在，将创建新索引")
            self.create_index(documents)
        else:
            try:
                logger.info(f"添加 {len(documents)} 个文档到索引")
                self.vectorstore.add_documents(documents)
                logger.info("文档添加成功")
            except Exception as e:
                logger.error(f"添加文档失败: {str(e)}")
                raise

    def save_index(self, path: Optional[str] = None):
        """
        保存索引到磁盘

        Args:
            path: 保存路径，None则使用初始化时的路径
        """
        if self.vectorstore is None:
            raise ValueError("索引不存在，无法保存")

        save_path = path or self.index_path
        if save_path is None:
            raise ValueError("未指定保存路径")

        try:
            # 确保目录存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"保存索引到: {save_path}")
            self.vectorstore.save_local(save_path)
            logger.info("索引保存成功")

        except Exception as e:
            logger.error(f"保存索引失败: {str(e)}")
            raise

    def load_index(self, path: Optional[str] = None):
        """
        从磁盘加载索引

        Args:
            path: 加载路径，None则使用初始化时的路径
        """
        load_path = path or self.index_path
        if load_path is None:
            raise ValueError("未指定加载路径")

        try:
            logger.info(f"从 {load_path} 加载索引")
            self.vectorstore = FAISS.load_local(
                load_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("索引加载成功")

        except Exception as e:
            logger.error(f"加载索引失败: {str(e)}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 分数阈值，只返回超过此阈值的结果

        Returns:
            相关文档列表
        """
        if self.vectorstore is None:
            raise ValueError("索引不存在")

        try:
            if score_threshold is not None:
                # 带分数的搜索
                docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
                # 过滤低分结果
                docs = [doc for doc, score in docs_with_scores if score >= score_threshold]
            else:
                docs = self.vectorstore.similarity_search(query, k=k)

            logger.info(f"搜索完成，返回 {len(docs)} 个结果")
            return docs

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4
    ) -> List[tuple]:
        """
        带分数的相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            (文档, 分数)元组列表
        """
        if self.vectorstore is None:
            raise ValueError("索引不存在")

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise

    def max_marginal_relevance_search(
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
            lambda_mult: 多样性参数 (0=最大多样性, 1=最大相关性)

        Returns:
            文档列表
        """
        if self.vectorstore is None:
            raise ValueError("索引不存在")

        try:
            docs = self.vectorstore.max_marginal_relevance_search(
                query=query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult
            )
            logger.info(f"MMR搜索完成，返回 {len(docs)} 个结果")
            return docs

        except Exception as e:
            logger.error(f"MMR搜索失败: {str(e)}")
            raise

    def get_statistics(self) -> dict:
        """
        获取索引统计信息

        Returns:
            统计信息字典
        """
        if self.vectorstore is None:
            return {"error": "索引不存在"}

        try:
            # FAISS索引信息
            index = self.vectorstore.index
            stats = {
                "文档数量": index.ntotal,
                "向量维度": index.d,
                "索引类型": type(index).__name__,
            }
            return stats

        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {"error": str(e)}


def demo():
    """演示FAISS向量数据库"""
    print("=== FAISS向量数据库演示 ===\n")

    # 创建示例文档
    documents = [
        Document(page_content="深度学习是机器学习的一个分支，使用多层神经网络。", metadata={"source": "doc1", "topic": "深度学习"}),
        Document(page_content="自然语言处理让计算机理解和生成人类语言。", metadata={"source": "doc2", "topic": "NLP"}),
        Document(page_content="卷积神经网络（CNN）主要用于图像识别任务。", metadata={"source": "doc3", "topic": "计算机视觉"}),
        Document(page_content="循环神经网络（RNN）适合处理序列数据。", metadata={"source": "doc4", "topic": "深度学习"}),
        Document(page_content="Transformer架构彻底改变了NLP领域。", metadata={"source": "doc5", "topic": "NLP"}),
        Document(page_content="BERT是一种预训练语言模型，在多个任务上表现出色。", metadata={"source": "doc6", "topic": "NLP"}),
        Document(page_content="强化学习让智能体通过与环境交互来学习。", metadata={"source": "doc7", "topic": "强化学习"}),
        Document(page_content="RAG系统结合检索和生成，提高答案准确性。", metadata={"source": "doc8", "topic": "RAG"}),
    ]

    # 索引保存路径
    index_path = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/04-vector-databases/data/faiss_index"

    print("注意: 首次运行会下载BGE模型（约400MB），需要等待...\n")

    try:
        # 创建FAISS向量存储
        print("=== 步骤1: 创建索引 ===")
        faiss_store = FAISSVectorStore(
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            index_path=index_path
        )

        # 创建索引
        faiss_store.create_index(documents)
        print("索引创建成功!\n")

        # 获取统计信息
        print("=== 步骤2: 索引统计信息 ===")
        stats = faiss_store.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")

        # 相似度搜索
        print("\n=== 步骤3: 相似度搜索 ===")
        query = "什么是NLP？"
        print(f"查询: {query}\n")

        results = faiss_store.similarity_search(query, k=3)
        for i, doc in enumerate(results):
            print(f"结果 {i+1}:")
            print(f"  内容: {doc.page_content}")
            print(f"  元数据: {doc.metadata}\n")

        # 带分数的搜索
        print("=== 步骤4: 带分数的搜索 ===")
        results_with_scores = faiss_store.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(results_with_scores):
            print(f"结果 {i+1} (分数: {score:.4f}):")
            print(f"  内容: {doc.page_content}\n")

        # MMR搜索
        print("=== 步骤5: MMR搜索（提高多样性） ===")
        mmr_results = faiss_store.max_marginal_relevance_search(
            query=query,
            k=3,
            fetch_k=6,
            lambda_mult=0.5
        )
        for i, doc in enumerate(mmr_results):
            print(f"结果 {i+1}:")
            print(f"  内容: {doc.page_content}")
            print(f"  主题: {doc.metadata.get('topic')}\n")

        # 保存索引
        print("=== 步骤6: 保存索引 ===")
        faiss_store.save_index()
        print(f"索引已保存到: {index_path}\n")

        # 加载索引
        print("=== 步骤7: 加载已保存的索引 ===")
        new_store = FAISSVectorStore(
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            index_path=index_path
        )
        new_store.load_index()
        print("索引加载成功!\n")

        # 验证加载的索引
        test_results = new_store.similarity_search("深度学习", k=2)
        print("验证搜索:")
        for i, doc in enumerate(test_results):
            print(f"  {i+1}. {doc.page_content}")

        # 添加新文档
        print("\n=== 步骤8: 添加新文档 ===")
        new_docs = [
            Document(page_content="GPT是一种自回归语言模型。", metadata={"source": "doc9", "topic": "NLP"}),
            Document(page_content="向量数据库用于存储和检索高维向量。", metadata={"source": "doc10", "topic": "向量数据库"}),
        ]
        faiss_store.add_documents(new_docs)
        print(f"已添加 {len(new_docs)} 个新文档\n")

        # 更新统计信息
        new_stats = faiss_store.get_statistics()
        print("更新后的统计信息:")
        for key, value in new_stats.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("\n提示:")
        print("1. 确保已安装: pip install faiss-cpu sentence-transformers")
        print("2. 首次运行需要下载模型，请确保网络连接正常")
        print("3. 如果下载失败，可以尝试使用国内镜像或手动下载模型")


if __name__ == "__main__":
    demo()
