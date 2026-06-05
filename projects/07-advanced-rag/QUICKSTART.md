# 快速开始指南

本指南帮助你快速上手高级RAG系统项目。

## 环境准备

### 1. 安装依赖

```bash
cd projects/07-advanced-rag
pip install -r requirements.txt
```

主要依赖包：
- `langchain` - RAG框架
- `faiss-cpu` - 向量数据库
- `sentence-transformers` - Embedding模型
- `chromadb` - 向量数据库
- `rank-bm25` - BM25检索

### 2. 首次运行注意事项

**首次运行会自动下载BGE中文Embedding模型（约400MB），需要：**
- 稳定的网络连接
- 约5-10分钟下载时间
- 约1GB磁盘空间

如果下载失败，可以：
1. 使用国内镜像源
2. 手动下载模型到 `~/.cache/huggingface/`
3. 使用更小的模型如 `BAAI/bge-small-zh-v1.5`

## 5分钟快速体验

### 运行完整示例

```bash
# 综合示例 - 完整工作流
python demo_complete_workflow.py
```

这个脚本会演示：
- 文档准备和分块
- 向量存储创建
- 多种检索策略
- 混合检索
- 索引保存

### 运行单个模块

```bash
# 1. 文档加载
python 01-document-loaders/src/markdown_loader.py

# 2. 分块策略对比
python 02-chunking-strategies/src/compare_strategies.py

# 3. FAISS向量存储
python 04-vector-databases/src/faiss_vectorstore.py

# 4. 检索策略
python 05-retrieval-strategies/src/retrieval_methods.py

# 5. 混合检索
python 07-hybrid-search/src/hybrid_retrieval.py

# 6. 生产级系统
python 08-production-rag/src/complete_system.py
```

## 基础使用示例

### 示例1: 简单的RAG检索

```python
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. 准备文档
documents = [
    Document(page_content="深度学习是机器学习的一个分支。"),
    Document(page_content="RAG系统结合检索和生成。"),
    Document(page_content="向量数据库用于存储向量。"),
]

# 2. 创建Embedding
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={'device': 'cpu'}
)

# 3. 创建向量存储
vectorstore = FAISS.from_documents(documents, embeddings)

# 4. 检索
query = "什么是RAG？"
results = vectorstore.similarity_search(query, k=2)

for doc in results:
    print(doc.page_content)
```

### 示例2: 使用生产级系统

```python
from complete_system import ProductionRAGSystem, RAGConfig
from langchain.schema import Document

# 1. 创建配置
config = RAGConfig(
    chunk_size=500,
    retrieval_k=4,
    use_hybrid_search=True
)

# 2. 初始化系统
rag_system = ProductionRAGSystem(config)

# 3. 加载文档
documents = [
    Document(page_content="你的文档内容..."),
    # 更多文档...
]
rag_system.load_documents(documents)

# 4. 构建索引
rag_system.build_index()

# 5. 检索
results = rag_system.retrieve_only("你的查询", k=3)

# 6. 保存索引（下次可直接加载）
rag_system.save_index("./my_index")
```

### 示例3: 混合检索

```python
from hybrid_retrieval import HybridSearchRetriever

# 创建混合检索器
retriever = HybridSearchRetriever(
    documents=documents,
    dense_weight=0.6,  # 向量检索权重
    sparse_weight=0.4  # BM25检索权重
)

# 执行检索
results = retriever.search("查询", k=4)
```

## 常见使用场景

### 场景1: 技术文档问答

```python
# 1. 加载技术文档
from universal_loader import UniversalDocumentLoader

loader = UniversalDocumentLoader()
docs = loader.load_directory("./docs", file_types=['.md', '.pdf'])

# 2. 使用较大的chunk_size
from recursive_chunking import RecursiveChunker

chunker = RecursiveChunker(chunk_size=800, chunk_overlap=100)
chunks = chunker.split_documents(docs)

# 3. 使用向量检索为主
from hybrid_retrieval import HybridSearchRetriever

retriever = HybridSearchRetriever(
    documents=chunks,
    dense_weight=0.7,
    sparse_weight=0.3
)
```

### 场景2: 新闻文章检索

```python
# 1. 较小的chunk_size
chunker = RecursiveChunker(chunk_size=400, chunk_overlap=50)

# 2. 平衡的混合检索
retriever = HybridSearchRetriever(
    documents=chunks,
    dense_weight=0.5,
    sparse_weight=0.5
)
```

### 场景3: 法律文本检索

```python
# 1. 精确匹配为主
retriever = HybridSearchRetriever(
    documents=chunks,
    dense_weight=0.4,
    sparse_weight=0.6  # BM25为主
)

# 2. 使用元数据过滤
from chroma_vectorstore import ChromaVectorStore

store = ChromaVectorStore()
results = store.similarity_search(
    query="查询",
    filter={"category": "合同法"}
)
```

## 进阶技巧

### 1. 提高检索质量

```python
# 使用MMR提高结果多样性
results = vectorstore.max_marginal_relevance_search(
    query="查询",
    k=4,
    fetch_k=20,
    lambda_mult=0.5  # 0=最大多样性, 1=最大相关性
)
```

### 2. 评估系统性能

```python
from rag_evaluation import RAGEvaluator

evaluator = RAGEvaluator()
metrics = evaluator.evaluate_retrieval(
    retrieved_docs=retrieved_docs,
    relevant_docs=ground_truth_docs,
    k=4
)
print(f"Precision: {metrics['Precision@4']:.2%}")
print(f"Recall: {metrics['Recall@4']:.2%}")
```

### 3. 使用缓存加速

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str):
    return vectorstore.similarity_search(query, k=4)
```

## 故障排除

### 问题1: 模型下载失败

**解决方案**：
```python
# 使用国内镜像
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 或使用更小的模型
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5"  # 更小的模型
)
```

### 问题2: 内存不足

**解决方案**：
```python
# 1. 批量处理文档
for i in range(0, len(documents), 100):
    batch = documents[i:i+100]
    vectorstore.add_documents(batch)

# 2. 使用量化压缩
# 3. 减少chunk_size
```

### 问题3: 检索结果不准确

**解决方案**：
1. 调整chunk_size和overlap
2. 使用混合检索
3. 尝试不同的Embedding模型
4. 添加元数据过滤
5. 使用查询改写

## 下一步

1. **学习各模块**: 查看每个子目录的代码和注释
2. **自定义配置**: 根据你的数据调整参数
3. **集成LLM**: 添加OpenAI或其他LLM进行问答生成
4. **生产部署**: 参考 `08-production-rag` 的完整实现
5. **性能优化**: 使用缓存、批量处理、索引优化

## 获取帮助

- 查看代码中的详细注释
- 运行各模块的demo函数
- 参考 `docs/05-最佳实践/02-RAG系统优化.md`
- 参考 `docs/02-教程/07-高级RAG教程.md`

---

**开始构建你的RAG系统吧！** 🚀
