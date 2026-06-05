"""
ChromaDB向量数据库
使用ChromaDB进行持久化向量存储
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """ChromaDB向量数据库管理类"""

    def __init__(
        self,
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5",
        persist_directory: Optional[str] = None,
        collection_name: str = "default_collection"
    ):
        """
        初始化ChromaDB向量存储

        Args:
            embedding_model_name: Embedding模型名称
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        self.embedding_model_name = embedding_model_name
        self.persist_directory = persist_directory
        self.collection_name = collection_name
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

    def create_collection(self, documents: List[Document]) -> Chroma:
        """
        创建ChromaDB集合

        Args:
            documents: 文档列表

        Returns:
            Chroma向量存储对象
        """
        try:
            logger.info(f"创建ChromaDB集合: {self.collection_name}，文档数量: {len(documents)}")

            # 确保持久化目录存在
            if self.persist_directory:
                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )

            logger.info("ChromaDB集合创建成功")
            return self.vectorstore

        except Exception as e:
            logger.error(f"创建集合失败: {str(e)}")
            raise

    def load_collection(self) -> Chroma:
        """
        加载现有集合

        Returns:
            Chroma向量存储对象
        """
        if self.persist_directory is None:
            raise ValueError("未指定持久化目录")

        try:
            logger.info(f"加载ChromaDB集合: {self.collection_name}")

            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )

            logger.info("集合加载成功")
            return self.vectorstore

        except Exception as e:
            logger.error(f"加载集合失败: {str(e)}")
            raise

    def add_documents(self, documents: List[Document]):
        """
        向集合添加文档

        Args:
            documents: 要添加的文档列表
        """
        if self.vectorstore is None:
            logger.warning("集合不存在，将创建新集合")
            self.create_collection(documents)
        else:
            try:
                logger.info(f"添加 {len(documents)} 个文档到集合")
                self.vectorstore.add_documents(documents)
                logger.info("文档添加成功")
            except Exception as e:
                logger.error(f"添加文档失败: {str(e)}")
                raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            相关文档列表
        """
        if self.vectorstore is None:
            raise ValueError("集合不存在")

        try:
            docs = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
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
            raise ValueError("集合不存在")

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise

    def delete_collection(self):
        """删除集合"""
        if self.vectorstore is None:
            logger.warning("集合不存在")
            return

        try:
            logger.info(f"删除集合: {self.collection_name}")
            self.vectorstore.delete_collection()
            self.vectorstore = None
            logger.info("集合删除成功")

        except Exception as e:
            logger.error(f"删除集合失败: {str(e)}")
            raise

    def get_statistics(self) -> dict:
        """
        获取集合统计信息

        Returns:
            统计信息字典
        """
        if self.vectorstore is None:
            return {"error": "集合不存在"}

        try:
            collection = self.vectorstore._collection
            stats = {
                "集合名称": self.collection_name,
                "文档数量": collection.count(),
                "持久化目录": self.persist_directory,
            }
            return stats

        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {"error": str(e)}


def demo():
    """演示ChromaDB向量数据库"""
    print("=== ChromaDB向量数据库演示 ===\n")

    # 创建示例文档
    documents = [
        Document(page_content="Python是一种高级编程语言。", metadata={"source": "doc1", "category": "编程"}),
        Document(page_content="机器学习是人工智能的一个分支。", metadata={"source": "doc2", "category": "AI"}),
        Document(page_content="深度学习使用神经网络进行学习。", metadata={"source": "doc3", "category": "AI"}),
        Document(page_content="JavaScript是前端开发的主要语言。", metadata={"source": "doc4", "category": "编程"}),
        Document(page_content="数据库用于存储和管理数据。", metadata={"source": "doc5", "category": "数据库"}),
        Document(page_content="向量数据库专门用于存储向量。", metadata={"source": "doc6", "category": "数据库"}),
    ]

    # 持久化目录
    persist_dir = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/04-vector-databases/data/chroma_db"

    print("注意: 首次运行会下载BGE模型（约400MB），需要等待...\n")

    try:
        # 创建ChromaDB向量存储
        print("=== 步骤1: 创建集合 ===")
        chroma_store = ChromaVectorStore(
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            persist_directory=persist_dir,
            collection_name="demo_collection"
        )

        # 创建集合
        chroma_store.create_collection(documents)
        print("集合创建成功!\n")

        # 获取统计信息
        print("=== 步骤2: 集合统计信息 ===")
        stats = chroma_store.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")

        # 相似度搜索
        print("\n=== 步骤3: 相似度搜索 ===")
        query = "什么是机器学习？"
        print(f"查询: {query}\n")

        results = chroma_store.similarity_search(query, k=3)
        for i, doc in enumerate(results):
            print(f"结果 {i+1}:")
            print(f"  内容: {doc.page_content}")
            print(f"  元数据: {doc.metadata}\n")

        # 元数据过滤搜索
        print("=== 步骤4: 带过滤条件的搜索 ===")
        print("过滤条件: category = 'AI'\n")

        filtered_results = chroma_store.similarity_search(
            query=query,
            k=3,
            filter={"category": "AI"}
        )
        for i, doc in enumerate(filtered_results):
            print(f"结果 {i+1}:")
            print(f"  内容: {doc.page_content}")
            print(f"  分类: {doc.metadata.get('category')}\n")

        # 带分数的搜索
        print("=== 步骤5: 带分数的搜索 ===")
        results_with_scores = chroma_store.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(results_with_scores):
            print(f"结果 {i+1} (距离: {score:.4f}):")
            print(f"  内容: {doc.page_content}\n")

        # 添加新文档
        print("=== 步骤6: 添加新文档 ===")
        new_docs = [
            Document(page_content="神经网络是深度学习的基础。", metadata={"source": "doc7", "category": "AI"}),
            Document(page_content="SQL用于查询关系数据库。", metadata={"source": "doc8", "category": "数据库"}),
        ]
        chroma_store.add_documents(new_docs)
        print(f"已添加 {len(new_docs)} 个新文档\n")

        # 更新统计信息
        new_stats = chroma_store.get_statistics()
        print("更新后的统计信息:")
        for key, value in new_stats.items():
            print(f"  {key}: {value}")

        # 测试持久化
        print("\n=== 步骤7: 测试持久化 ===")
        print("重新加载集合...\n")

        new_store = ChromaVectorStore(
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            persist_directory=persist_dir,
            collection_name="demo_collection"
        )
        new_store.load_collection()

        # 验证加载的集合
        test_results = new_store.similarity_search("编程语言", k=2)
        print("验证搜索:")
        for i, doc in enumerate(test_results):
            print(f"  {i+1}. {doc.page_content}")

        print("\n提示: 数据已持久化到磁盘，下次运行可以直接加载")

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("\n提示:")
        print("1. 确保已安装: pip install chromadb sentence-transformers")
        print("2. 首次运行需要下载模型，请确保网络连接正常")


if __name__ == "__main__":
    demo()
