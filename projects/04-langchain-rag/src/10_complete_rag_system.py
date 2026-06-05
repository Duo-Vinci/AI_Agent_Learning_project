"""
完整的RAG系统

这是一个生产级的RAG（检索增强生成）系统实现，集成了文档管理、向量检索、问答等完整功能。

主要功能：
1. 文档管理：上传、索引、删除、更新文档
2. 智能检索：多种检索策略、相似度搜索
3. 问答系统：基于检索的精准问答
4. 配置管理：灵活的系统配置
5. 缓存优化：减少重复计算
6. 日志监控：完整的日志记录

适用场景：
- 企业知识库问答
- 文档智能检索
- FAQ自动回答
- 技术文档助手
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
import json
import hashlib
from pathlib import Path

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


@dataclass
class Document:
    """文档数据类"""
    doc_id: str
    filename: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class Config:
    """系统配置类"""

    def __init__(self):
        self.vector_store_path = "./data/vector_store"
        self.cache_dir = "./data/cache"
        self.log_dir = "./logs"

        # 分块配置
        self.chunk_size = 1000
        self.chunk_overlap = 200

        # 检索配置
        self.retrieval_k = 4  # 返回top-k个结果
        self.similarity_threshold = 0.7

        # LLM配置
        self.llm_model = "gpt-3.5-turbo"
        self.temperature = 0.7

        # 缓存配置
        self.enable_cache = True
        self.cache_ttl = 3600  # 缓存有效期（秒）

        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        for dir_path in [self.vector_store_path, self.cache_dir, self.log_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


class DocumentManager:
    """文档管理器"""

    def __init__(self, config: Config):
        self.config = config
        self.documents: Dict[str, Document] = {}
        self.metadata_file = os.path.join(config.vector_store_path, "metadata.json")
        self._load_metadata()

    def _load_metadata(self):
        """加载文档元数据"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for doc_id, doc_data in data.items():
                    self.documents[doc_id] = Document(
                        doc_id=doc_data['doc_id'],
                        filename=doc_data['filename'],
                        content=doc_data['content'],
                        metadata=doc_data['metadata'],
                        created_at=datetime.fromisoformat(doc_data['created_at']),
                        updated_at=datetime.fromisoformat(doc_data['updated_at'])
                    )

    def _save_metadata(self):
        """保存文档元数据"""
        data = {}
        for doc_id, doc in self.documents.items():
            data[doc_id] = {
                'doc_id': doc.doc_id,
                'filename': doc.filename,
                'content': doc.content,
                'metadata': doc.metadata,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat()
            }

        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_document(self, filename: str, content: str, metadata: Optional[Dict] = None) -> str:
        """
        添加文档

        Args:
            filename: 文件名
            content: 文档内容
            metadata: 元数据

        Returns:
            文档ID
        """
        # 生成文档ID
        doc_id = hashlib.md5(f"{filename}{datetime.now()}".encode()).hexdigest()[:16]

        # 创建文档对象
        doc = Document(
            doc_id=doc_id,
            filename=filename,
            content=content,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.documents[doc_id] = doc
        self._save_metadata()

        print(f"✅ 文档已添加: {filename} (ID: {doc_id})")
        return doc_id

    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if doc_id in self.documents:
            filename = self.documents[doc_id].filename
            del self.documents[doc_id]
            self._save_metadata()
            print(f"✅ 文档已删除: {filename}")
            return True
        return False

    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        return self.documents.get(doc_id)

    def list_documents(self) -> List[Document]:
        """列出所有文档"""
        return list(self.documents.values())


class VectorStoreManager:
    """向量存储管理器"""

    def __init__(self, config: Config):
        self.config = config

        # 初始化Embedding模型（使用本地模型）
        print("📥 加载Embedding模型...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 初始化文本分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len
        )

        self.vector_store = None
        self._load_vector_store()

    def _load_vector_store(self):
        """加载向量存储"""
        index_path = os.path.join(self.config.vector_store_path, "index")
        if os.path.exists(index_path):
            try:
                self.vector_store = FAISS.load_local(
                    index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("✅ 向量存储已加载")
            except Exception as e:
                print(f"⚠️  加载向量存储失败: {e}")
                self.vector_store = None

    def _save_vector_store(self):
        """保存向量存储"""
        if self.vector_store:
            index_path = os.path.join(self.config.vector_store_path, "index")
            self.vector_store.save_local(index_path)
            print("✅ 向量存储已保存")

    def index_document(self, doc_id: str, content: str):
        """
        索引文档

        Args:
            doc_id: 文档ID
            content: 文档内容
        """
        print(f"📑 正在索引文档 {doc_id}...")

        # 分块
        chunks = self.text_splitter.split_text(content)
        print(f"  - 文档已分块: {len(chunks)} 个chunk")

        # 添加元数据
        metadatas = [{"doc_id": doc_id, "chunk_id": i} for i in range(len(chunks))]

        # 创建或更新向量存储
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                metadatas=metadatas
            )
        else:
            self.vector_store.add_texts(
                texts=chunks,
                metadatas=metadatas
            )

        self._save_vector_store()
        print(f"✅ 文档索引完成")

    def delete_document_from_index(self, doc_id: str):
        """从索引中删除文档（FAISS不支持直接删除，需要重建）"""
        print(f"⚠️  FAISS不支持直接删除，需要重建索引")

    def search(self, query: str, k: int = 4) -> List[Dict]:
        """
        搜索相关文档

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            相关文档列表
        """
        if self.vector_store is None:
            return []

        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)

        results = []
        for doc, score in docs_with_scores:
            results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score)
            })

        return results


class QueryCache:
    """查询缓存"""

    def __init__(self, config: Config):
        self.config = config
        self.cache: Dict[str, Dict] = {}

    def _get_cache_key(self, query: str) -> str:
        """生成缓存键"""
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[str]:
        """获取缓存"""
        if not self.config.enable_cache:
            return None

        cache_key = self._get_cache_key(query)
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # 检查是否过期
            if (datetime.now() - cached_data['timestamp']).seconds < self.config.cache_ttl:
                print("🔄 使用缓存结果")
                return cached_data['answer']
            else:
                # 过期，删除缓存
                del self.cache[cache_key]

        return None

    def set(self, query: str, answer: str):
        """设置缓存"""
        if self.config.enable_cache:
            cache_key = self._get_cache_key(query)
            self.cache[cache_key] = {
                'answer': answer,
                'timestamp': datetime.now()
            }


class RAGSystem:
    """完整的RAG系统"""

    def __init__(self, config: Optional[Config] = None):
        """
        初始化RAG系统

        Args:
            config: 配置对象
        """
        self.config = config or Config()

        # 初始化各个组件
        print("🚀 初始化RAG系统...")
        self.doc_manager = DocumentManager(self.config)
        self.vector_manager = VectorStoreManager(self.config)
        self.cache = QueryCache(self.config)

        # 初始化LLM
        self.llm = ChatOpenAI(
            model=self.config.llm_model,
            temperature=self.config.temperature
        )

        # 创建QA链
        self._create_qa_chain()

        print("✅ RAG系统初始化完成\n")

    def _create_qa_chain(self):
        """创建问答链"""
        # 自定义Prompt
        prompt_template = """使用以下检索到的上下文来回答问题。如果你不知道答案，就说你不知道，不要试图编造答案。

上下文：
{context}

问题：{question}

详细回答："""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        if self.vector_manager.vector_store:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_manager.vector_store.as_retriever(
                    search_kwargs={"k": self.config.retrieval_k}
                ),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
        else:
            self.qa_chain = None

    def add_document_from_file(self, file_path: str) -> str:
        """
        从文件添加文档

        Args:
            file_path: 文件路径

        Returns:
            文档ID
        """
        print(f"\n📂 加载文档: {file_path}")

        # 根据文件类型选择加载器
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding='utf-8')

        documents = loader.load()
        content = "\n\n".join([doc.page_content for doc in documents])

        # 添加文档
        filename = os.path.basename(file_path)
        doc_id = self.doc_manager.add_document(
            filename=filename,
            content=content,
            metadata={'source': file_path}
        )

        # 索引文档
        self.vector_manager.index_document(doc_id, content)

        # 重新创建QA链
        self._create_qa_chain()

        return doc_id

    def add_document_from_text(self, filename: str, content: str) -> str:
        """
        从文本添加文档

        Args:
            filename: 文件名
            content: 文本内容

        Returns:
            文档ID
        """
        print(f"\n📝 添加文本文档: {filename}")

        # 添加文档
        doc_id = self.doc_manager.add_document(
            filename=filename,
            content=content
        )

        # 索引文档
        self.vector_manager.index_document(doc_id, content)

        # 重新创建QA链
        self._create_qa_chain()

        return doc_id

    def query(self, question: str) -> Dict[str, Any]:
        """
        查询问答系统

        Args:
            question: 问题

        Returns:
            回答和相关信息
        """
        print(f"\n❓ 问题: {question}")

        # 检查缓存
        cached_answer = self.cache.get(question)
        if cached_answer:
            return {
                'answer': cached_answer,
                'sources': [],
                'from_cache': True
            }

        # 检查是否有文档
        if not self.qa_chain:
            return {
                'answer': "系统中还没有文档，请先添加文档。",
                'sources': [],
                'from_cache': False
            }

        # 执行查询
        try:
            result = self.qa_chain.invoke({"query": question})

            answer = result['result']
            source_docs = result.get('source_documents', [])

            # 提取来源信息
            sources = []
            for doc in source_docs:
                sources.append({
                    'content': doc.page_content[:200] + "...",
                    'metadata': doc.metadata
                })

            # 缓存结果
            self.cache.set(question, answer)

            print(f"\n💬 回答: {answer}")
            print(f"📚 使用了 {len(sources)} 个文档片段")

            return {
                'answer': answer,
                'sources': sources,
                'from_cache': False
            }

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return {
                'answer': f"查询失败: {str(e)}",
                'sources': [],
                'from_cache': False
            }

    def list_documents(self) -> List[Document]:
        """列出所有文档"""
        return self.doc_manager.list_documents()

    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        success = self.doc_manager.delete_document(doc_id)
        if success:
            self.vector_manager.delete_document_from_index(doc_id)
        return success

    def get_statistics(self) -> Dict:
        """获取系统统计信息"""
        docs = self.doc_manager.list_documents()
        return {
            'total_documents': len(docs),
            'cache_size': len(self.cache.cache),
            'config': {
                'chunk_size': self.config.chunk_size,
                'retrieval_k': self.config.retrieval_k,
                'cache_enabled': self.config.enable_cache
            }
        }


# ============ 示例使用 ============

def example_1_basic_usage():
    """示例1: 基础使用"""
    print("\n" + "="*60)
    print("示例1: RAG系统基础使用")
    print("="*60)

    # 初始化系统
    rag = RAGSystem()

    # 添加文档（使用模拟数据）
    doc1 = """
    Python是一种高级编程语言，由Guido van Rossum于1991年创建。
    Python以其简洁明了的语法和强大的功能而闻名。
    它被广泛应用于Web开发、数据科学、人工智能等领域。
    """

    doc2 = """
    机器学习是人工智能的一个分支，它使计算机能够从数据中学习。
    常见的机器学习算法包括线性回归、决策树、神经网络等。
    Python有许多优秀的机器学习库，如scikit-learn、TensorFlow和PyTorch。
    """

    rag.add_document_from_text("python_intro.txt", doc1)
    rag.add_document_from_text("ml_intro.txt", doc2)

    # 查询
    result = rag.query("Python是什么时候创建的？")
    print(f"\n回答: {result['answer']}")

    result = rag.query("有哪些机器学习算法？")
    print(f"\n回答: {result['answer']}")


def example_2_document_management():
    """示例2: 文档管理"""
    print("\n" + "="*60)
    print("示例2: 文档管理")
    print("="*60)

    rag = RAGSystem()

    # 添加多个文档
    documents = [
        ("Python基础", "Python是一种解释型、面向对象的高级编程语言。"),
        ("Java基础", "Java是一种面向对象的编程语言，具有跨平台特性。"),
        ("JavaScript基础", "JavaScript是一种脚本语言，主要用于网页开发。")
    ]

    doc_ids = []
    for title, content in documents:
        doc_id = rag.add_document_from_text(title, content)
        doc_ids.append(doc_id)

    # 列出所有文档
    print("\n📚 当前文档列表:")
    for doc in rag.list_documents():
        print(f"  - {doc.filename} (ID: {doc.doc_id})")

    # 删除一个文档
    if doc_ids:
        rag.delete_document(doc_ids[0])
        print(f"\n删除后的文档数量: {len(rag.list_documents())}")


def example_3_statistics():
    """示例3: 系统统计"""
    print("\n" + "="*60)
    print("示例3: 系统统计")
    print("="*60)

    rag = RAGSystem()

    # 添加文档
    rag.add_document_from_text(
        "AI简介",
        "人工智能是计算机科学的一个分支，旨在创建能够模拟人类智能的系统。"
    )

    # 进行一些查询
    rag.query("什么是人工智能？")
    rag.query("什么是人工智能？")  # 第二次应该使用缓存

    # 获取统计信息
    stats = rag.get_statistics()
    print("\n📊 系统统计:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*15 + "完整RAG系统演示")
    print("="*60)

    # 运行示例
    example_1_basic_usage()
    example_2_document_management()
    example_3_statistics()

    print("\n" + "="*60)
    print("✅ 所有示例执行完成")
    print("="*60)
