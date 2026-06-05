"""
生产级RAG系统
包含完整的文档处理、检索、生成流程和错误处理
"""

import os
import logging
from typing import List, Optional, Dict
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """RAG系统配置"""
    # Embedding配置
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_device: str = "cpu"

    # 分块配置
    chunk_size: int = 500
    chunk_overlap: int = 50

    # 检索配置
    retrieval_k: int = 4
    use_hybrid_search: bool = True
    dense_weight: float = 0.6
    sparse_weight: float = 0.4

    # 生成配置
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.1
    max_tokens: int = 500

    # 存储配置
    vectorstore_path: str = "./vectorstore"
    enable_cache: bool = True


class ProductionRAGSystem:
    """生产级RAG系统"""

    def __init__(self, config: RAGConfig = None):
        """
        初始化RAG系统

        Args:
            config: RAG配置对象
        """
        self.config = config or RAGConfig()
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self.documents = []

        logger.info("初始化生产级RAG系统")
        self._initialize_components()

    def _initialize_components(self):
        """初始化系统组件"""
        try:
            # 初始化Embedding模型
            logger.info(f"加载Embedding模型: {self.config.embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config.embedding_model,
                model_kwargs={'device': self.config.embedding_device},
                encode_kwargs={'normalize_embeddings': True}
            )

            # 初始化文本分割器
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", "。", ".", " ", ""]
            )

            logger.info("系统组件初始化完成")

        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise

    def load_documents(self, documents: List[Document]) -> bool:
        """
        加载文档到系统

        Args:
            documents: 文档列表

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始加载 {len(documents)} 个文档")

            # 文档预处理
            processed_docs = self._preprocess_documents(documents)

            # 文档分块
            chunks = self.text_splitter.split_documents(processed_docs)
            logger.info(f"文档分块完成: {len(chunks)} 个块")

            self.documents = chunks
            return True

        except Exception as e:
            logger.error(f"文档加载失败: {e}")
            return False

    def _preprocess_documents(self, documents: List[Document]) -> List[Document]:
        """
        文档预处理

        Args:
            documents: 原始文档列表

        Returns:
            处理后的文档列表
        """
        import re

        processed = []
        for doc in documents:
            # 清理文本
            text = doc.page_content

            # 统一换行符
            text = text.replace('\r\n', '\n').replace('\r', '\n')

            # 移除多余空白
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' {2,}', ' ', text)

            # 移除特殊字符
            text = text.replace('�', '')

            doc.page_content = text.strip()
            processed.append(doc)

        return processed

    def build_index(self) -> bool:
        """
        构建向量索引

        Returns:
            是否成功
        """
        try:
            if not self.documents:
                logger.error("没有文档可索引")
                return False

            logger.info("开始构建向量索引")

            # 创建向量存储
            self.vectorstore = FAISS.from_documents(
                documents=self.documents,
                embedding=self.embeddings
            )

            # 创建检索器
            if self.config.use_hybrid_search:
                self._build_hybrid_retriever()
            else:
                self.retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": self.config.retrieval_k}
                )

            logger.info("向量索引构建完成")
            return True

        except Exception as e:
            logger.error(f"索引构建失败: {e}")
            return False

    def _build_hybrid_retriever(self):
        """构建混合检索器"""
        try:
            logger.info("构建混合检索器")

            # 向量检索器
            dense_retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": self.config.retrieval_k}
            )

            # BM25检索器
            sparse_retriever = BM25Retriever.from_documents(self.documents)
            sparse_retriever.k = self.config.retrieval_k

            # 混合检索器
            self.retriever = EnsembleRetriever(
                retrievers=[dense_retriever, sparse_retriever],
                weights=[self.config.dense_weight, self.config.sparse_weight]
            )

            logger.info("混合检索器构建完成")

        except Exception as e:
            logger.error(f"混合检索器构建失败: {e}")
            # 降级到单一向量检索
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": self.config.retrieval_k}
            )

    def initialize_qa_chain(self, openai_api_key: Optional[str] = None):
        """
        初始化问答链

        Args:
            openai_api_key: OpenAI API密钥
        """
        try:
            if self.retriever is None:
                raise ValueError("检索器未初始化，请先构建索引")

            logger.info("初始化问答链")

            # 初始化LLM
            llm = ChatOpenAI(
                model_name=self.config.llm_model,
                temperature=self.config.llm_temperature,
                max_tokens=self.config.max_tokens,
                api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
            )

            # 创建QA链
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True
            )

            logger.info("问答链初始化完成")

        except Exception as e:
            logger.error(f"问答链初始化失败: {e}")
            raise

    def query(self, question: str) -> Dict:
        """
        执行查询

        Args:
            question: 问题

        Returns:
            包含答案和来源的字典
        """
        try:
            logger.info(f"处理查询: {question}")

            if self.qa_chain is None:
                # 如果QA链未初始化，只返回检索结果
                logger.warning("QA链未初始化，只返回检索结果")
                docs = self.retriever.get_relevant_documents(question)
                return {
                    "question": question,
                    "answer": "问答链未初始化，无法生成答案",
                    "source_documents": docs,
                    "timestamp": datetime.now().isoformat()
                }

            # 执行问答
            result = self.qa_chain({"query": question})

            response = {
                "question": question,
                "answer": result["result"],
                "source_documents": result["source_documents"],
                "timestamp": datetime.now().isoformat()
            }

            logger.info("查询处理完成")
            return response

        except Exception as e:
            logger.error(f"查询处理失败: {e}")
            return {
                "question": question,
                "answer": f"处理查询时出错: {str(e)}",
                "source_documents": [],
                "timestamp": datetime.now().isoformat()
            }

    def retrieve_only(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        只执行检索，不生成答案

        Args:
            query: 查询
            k: 返回结果数量

        Returns:
            文档列表
        """
        try:
            if self.retriever is None:
                raise ValueError("检索器未初始化")

            if k is not None:
                # 临时修改k值
                old_k = self.config.retrieval_k
                self.config.retrieval_k = k

            docs = self.retriever.get_relevant_documents(query)

            if k is not None:
                self.config.retrieval_k = old_k

            logger.info(f"检索到 {len(docs)} 个文档")
            return docs

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def save_index(self, path: Optional[str] = None):
        """
        保存向量索引

        Args:
            path: 保存路径
        """
        try:
            if self.vectorstore is None:
                raise ValueError("向量存储未初始化")

            save_path = path or self.config.vectorstore_path
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"保存索引到: {save_path}")
            self.vectorstore.save_local(save_path)
            logger.info("索引保存成功")

        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            raise

    def load_index(self, path: Optional[str] = None):
        """
        加载向量索引

        Args:
            path: 加载路径
        """
        try:
            load_path = path or self.config.vectorstore_path

            logger.info(f"从 {load_path} 加载索引")
            self.vectorstore = FAISS.load_local(
                load_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            # 重建检索器
            if self.config.use_hybrid_search:
                logger.warning("混合检索需要重新加载文档")
                self.retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": self.config.retrieval_k}
                )
            else:
                self.retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": self.config.retrieval_k}
                )

            logger.info("索引加载成功")

        except Exception as e:
            logger.error(f"加载索引失败: {e}")
            raise

    def get_statistics(self) -> Dict:
        """
        获取系统统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "配置": {
                "Embedding模型": self.config.embedding_model,
                "分块大小": self.config.chunk_size,
                "检索数量": self.config.retrieval_k,
                "混合检索": self.config.use_hybrid_search,
            },
            "数据": {
                "文档块数": len(self.documents),
                "索引状态": "已构建" if self.vectorstore else "未构建",
            },
            "状态": {
                "检索器": "已初始化" if self.retriever else "未初始化",
                "问答链": "已初始化" if self.qa_chain else "未初始化",
            }
        }

        if self.vectorstore:
            try:
                stats["数据"]["向量数量"] = self.vectorstore.index.ntotal
                stats["数据"]["向量维度"] = self.vectorstore.index.d
            except:
                pass

        return stats


def demo():
    """演示生产级RAG系统"""
    print("=== 生产级RAG系统演示 ===\n")

    # 创建示例文档
    documents = [
        Document(
            page_content="""深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的层次化表示。
            深度学习在图像识别、语音识别和自然语言处理等领域取得了突破性进展。
            常见的深度学习模型包括卷积神经网络（CNN）、循环神经网络（RNN）和Transformer。""",
            metadata={"source": "AI教程", "chapter": "深度学习基础"}
        ),
        Document(
            page_content="""自然语言处理（NLP）是人工智能的一个重要分支，专注于让计算机理解和生成人类语言。
            NLP的应用包括机器翻译、情感分析、文本摘要、问答系统等。
            现代NLP主要基于深度学习技术，特别是Transformer架构。""",
            metadata={"source": "AI教程", "chapter": "NLP基础"}
        ),
        Document(
            page_content="""Transformer是一种基于自注意力机制的神经网络架构，由Google在2017年提出。
            它彻底改变了NLP领域，成为BERT、GPT等大语言模型的基础。
            Transformer的核心创新是自注意力机制，能够高效地捕捉序列中的长距离依赖关系。""",
            metadata={"source": "AI教程", "chapter": "Transformer"}
        ),
        Document(
            page_content="""RAG（检索增强生成）是一种结合信息检索和文本生成的技术。
            RAG系统首先从知识库中检索相关文档，然后基于这些文档生成答案。
            这种方法可以有效减少大语言模型的幻觉问题，提高答案的准确性和可靠性。""",
            metadata={"source": "AI教程", "chapter": "RAG系统"}
        ),
    ]

    try:
        # 创建自定义配置
        config = RAGConfig(
            embedding_model="BAAI/bge-small-zh-v1.5",
            chunk_size=300,
            chunk_overlap=30,
            retrieval_k=3,
            use_hybrid_search=True,
            dense_weight=0.6,
            sparse_weight=0.4
        )

        # 初始化系统
        print("=== 步骤1: 初始化RAG系统 ===")
        rag_system = ProductionRAGSystem(config)
        print("系统初始化完成!\n")

        # 加载文档
        print("=== 步骤2: 加载文档 ===")
        success = rag_system.load_documents(documents)
        if success:
            print(f"成功加载 {len(documents)} 个文档\n")

        # 构建索引
        print("=== 步骤3: 构建向量索引 ===")
        success = rag_system.build_index()
        if success:
            print("索引构建成功!\n")

        # 获取统计信息
        print("=== 步骤4: 系统统计信息 ===")
        stats = rag_system.get_statistics()
        for category, info in stats.items():
            print(f"\n{category}:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        # 测试检索
        print("\n\n=== 步骤5: 测试检索功能 ===")
        test_query = "什么是Transformer？"
        print(f"查询: {test_query}\n")

        retrieved_docs = rag_system.retrieve_only(test_query, k=2)
        for i, doc in enumerate(retrieved_docs):
            print(f"文档 {i+1}:")
            print(f"  内容: {doc.page_content[:150]}...")
            print(f"  来源: {doc.metadata}\n")

        # 保存索引
        print("=== 步骤6: 保存索引 ===")
        index_path = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/08-production-rag/data/production_index"
        rag_system.save_index(index_path)
        print(f"索引已保存到: {index_path}\n")

        # 测试加载索引
        print("=== 步骤7: 测试加载索引 ===")
        new_system = ProductionRAGSystem(config)
        new_system.load_index(index_path)
        print("索引加载成功!\n")

        # 验证加载的系统
        test_docs = new_system.retrieve_only("深度学习", k=2)
        print("验证检索:")
        for i, doc in enumerate(test_docs):
            print(f"  {i+1}. {doc.page_content[:80]}...")

        print("\n" + "=" * 70)
        print("注意: 完整的问答功能需要配置OpenAI API密钥")
        print("=" * 70)
        print("""
使用问答功能的方法:

1. 设置环境变量:
   export OPENAI_API_KEY='your-api-key'

2. 初始化问答链:
   rag_system.initialize_qa_chain()

3. 执行查询:
   result = rag_system.query("什么是深度学习？")
   print(result["answer"])
        """)

    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        print("\n提示:")
        print("1. 确保已安装所有依赖")
        print("2. 首次运行需要下载模型")


if __name__ == "__main__":
    demo()
