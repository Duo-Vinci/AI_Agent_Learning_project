# 高级 RAG 教程

## 一、项目概述

本项目深入讲解检索增强生成（RAG）的高级技术，从基础实现到生产级优化，帮助你构建高质量的知识问答系统。

**项目位置**：`projects/07-advanced-rag/`

**学习目标**：
- 掌握文档处理的最佳实践
- 理解不同的文本分块策略
- 学会选择和优化 Embedding 模型
- 掌握多种检索策略
- 学习 RAG 系统的评估方法
- 了解高级 RAG 技术

---

## 二、RAG 核心架构

### 2.1 RAG 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│ 离线阶段（构建知识库）                                        │
├─────────────────────────────────────────────────────────────┤
│ 1. 文档加载 → 2. 文本分块 → 3. Embedding → 4. 存入向量库     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 在线阶段（查询回答）                                          │
├─────────────────────────────────────────────────────────────┤
│ 1. 用户提问 → 2. Embedding → 3. 向量检索 →                  │
│ 4. 相关文档 → 5. 构建Prompt → 6. LLM生成 → 7. 返回答案      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 RAG vs 传统问答

| 特性 | 传统 LLM | RAG 系统 |
|------|----------|----------|
| 知识来源 | 训练数据 | 外部知识库 |
| 知识更新 | 需要重新训练 | 更新文档即可 |
| 答案准确性 | 可能产生幻觉 | 基于真实文档 |
| 可解释性 | 低 | 高（可追溯来源） |
| 成本 | 低 | 中等 |

---

## 三、文档加载与处理

### 3.1 支持的文档格式

```python
from langchain_community.document_loaders import (
    TextLoader,           # 纯文本
    PyPDFLoader,         # PDF
    Docx2txtLoader,      # Word
    UnstructuredMarkdownLoader,  # Markdown
    CSVLoader,           # CSV
    UnstructuredHTMLLoader,  # HTML
)

# PDF 加载示例
loader = PyPDFLoader("document.pdf")
documents = loader.load()

# Word 文档
loader = Docx2txtLoader("document.docx")
documents = loader.load()

# 网页内容
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://example.com")
documents = loader.load()
```

### 3.2 文档预处理

```python
def preprocess_documents(documents):
    """文档清洗和规范化"""
    processed = []
    
    for doc in documents:
        # 1. 清理空白字符
        text = doc.page_content.strip()
        
        # 2. 移除多余换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 3. 统一标点符号
        text = text.replace('，', ',').replace('。', '.')
        
        # 4. 移除特殊字符
        text = re.sub(r'[^\w\s一-鿿.,!?;:()（）]', '', text)
        
        doc.page_content = text
        processed.append(doc)
    
    return processed
```

---

## 四、文本分块策略

### 4.1 为什么要分块？

- **上下文窗口限制**：LLM 有输入长度限制
- **检索精度**：小块更容易匹配相关内容
- **成本控制**：减少不必要的 Token 消耗

### 4.2 分块策略对比

```python
from langchain.text_splitter import (
    CharacterTextSplitter,      # 按字符分割
    RecursiveCharacterTextSplitter,  # 递归分割（推荐）
    TokenTextSplitter,          # 按 Token 分割
    MarkdownHeaderTextSplitter, # 按 Markdown 标题分割
)

# 1. 递归字符分割器（最常用）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 块大小
    chunk_overlap=50,      # 重叠大小
    length_function=len,
    separators=["\n\n", "\n", "。", ".", " ", ""]  # 分割优先级
)

# 2. 语义分割（基于句子）
from langchain_experimental.text_splitter import SemanticChunker
text_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile"  # 语义相似度阈值
)

# 3. Markdown 结构化分割
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
)
```

### 4.3 分块参数选择指南

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| chunk_size | 300-1000 | 太小：上下文不足；太大：噪音增加 |
| chunk_overlap | 10-20% | 保持上下文连续性 |
| 技术文档 | 500-800 | 需要完整代码块 |
| 新闻文章 | 300-500 | 段落独立性强 |
| 学术论文 | 800-1000 | 需要完整逻辑 |

---

## 五、Embedding 模型

### 5.1 模型选择

```python
# 1. OpenAI Embeddings
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",  # 或 text-embedding-3-small
    api_key=api_key
)

# 2. 本地开源模型（推荐）
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5",  # 中文
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': True}
)

# 3. Sentence Transformers
from langchain_community.embeddings import SentenceTransformerEmbeddings
embeddings = SentenceTransformerEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
```

### 5.2 模型对比

| 模型 | 维度 | 语言 | 优点 | 缺点 |
|------|------|------|------|------|
| text-embedding-3-large | 3072 | 多语言 | 效果好 | 需要API调用 |
| text-embedding-3-small | 1536 | 多语言 | 成本低 | 效果略差 |
| bge-large-zh-v1.5 | 1024 | 中文 | 本地部署、免费 | 需要 GPU |
| m3e-base | 768 | 中文 | 轻量级 | 效果一般 |

---

## 六、向量数据库

### 6.1 常用向量数据库

```python
# 1. FAISS（本地、内存）
from langchain_community.vectorstores import FAISS
vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)
# 保存到磁盘
vectorstore.save_local("faiss_index")
# 加载
vectorstore = FAISS.load_local("faiss_index", embeddings)

# 2. Chroma（本地、持久化）
from langchain_community.vectorstores import Chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 3. Pinecone（云端、生产级）
from langchain_community.vectorstores import Pinecone
import pinecone
pinecone.init(api_key=api_key, environment="us-west1-gcp")
vectorstore = Pinecone.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name="my-index"
)
```

### 6.2 向量数据库选型

| 数据库 | 适用场景 | 优点 | 缺点 |
|--------|---------|------|------|
| FAISS | 原型开发、小规模 | 快速、免费 | 不支持增量更新 |
| Chroma | 中小型项目 | 易用、持久化 | 性能一般 |
| Pinecone | 生产环境 | 高性能、可扩展 | 需要付费 |
| Milvus | 大规模部署 | 功能强大 | 部署复杂 |

---

## 七、检索策略

### 7.1 基础检索

```python
# 相似度检索（默认）
results = vectorstore.similarity_search(
    query="什么是 RAG？",
    k=4  # 返回 top-4 结果
)

# 带分数的检索
results = vectorstore.similarity_search_with_score(
    query="什么是 RAG？",
    k=4
)
for doc, score in results:
    print(f"分数: {score}")
    print(f"内容: {doc.page_content[:100]}...")
```

### 7.2 MMR（最大边际相关性）

避免检索结果重复，提高多样性：

```python
results = vectorstore.max_marginal_relevance_search(
    query="什么是 RAG？",
    k=4,
    fetch_k=20,  # 先取 20 个候选
    lambda_mult=0.5  # 0=最大多样性，1=最大相关性
)
```

### 7.3 混合检索

结合关键词检索和向量检索：

```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# 1. 向量检索器
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 2. BM25 关键词检索器
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3

# 3. 混合检索器
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5]  # 权重分配
)

results = ensemble_retriever.get_relevant_documents("什么是 RAG？")
```

### 7.4 重排序（Reranking）

对检索结果重新排序，提高精度：

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# 使用 LLM 提取相关片段
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_retriever
)

compressed_docs = compression_retriever.get_relevant_documents(
    "什么是 RAG？"
)
```

---

## 八、高级 RAG 技术

### 8.1 HyDE（假设性文档 Embedding）

先生成假设性答案，再用它检索：

```python
from langchain.chains import HypotheticalDocumentEmbedder

# 1. 生成假设性文档
hyde_prompt = """根据问题生成一个详细的假设性答案：

问题：{question}

假设性答案："""

# 2. 用假设性答案做 Embedding 检索
hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
    llm=llm,
    base_embeddings=embeddings,
    prompt_key="question"
)
```

**原理**：假设性答案比问题本身更接近文档内容，检索效果更好。

### 8.2 Self-RAG（自我反思 RAG）

让模型判断是否需要检索以及检索结果是否相关：

```
1. 判断：这个问题需要检索外部知识吗？
   - 需要 → 执行检索
   - 不需要 → 直接回答

2. 检索后判断：检索到的文档相关吗？
   - 相关 → 使用文档生成答案
   - 不相关 → 重新检索或直接回答

3. 答案判断：答案是否得到文档支持？
   - 支持 → 返回答案
   - 不支持 → 标记为不确定
```

### 8.3 RAPTOR（递归摘要 RAG）

构建多层次的文档摘要树：

```
原始文档（底层）
    ↓ 聚类 + 摘要
段落摘要（中层）
    ↓ 聚类 + 摘要
章节摘要（高层）
    ↓
全文摘要（顶层）
```

**优势**：可以检索到不同粒度的信息。

---

## 九、RAG 评估

### 9.1 评估指标

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,        # 忠实度：答案是否基于文档
    answer_relevancy,    # 相关性：答案是否回答问题
    context_precision,   # 精确度：检索文档的准确性
    context_recall,      # 召回率：相关文档是否被检索到
)

# 评估数据集
eval_dataset = {
    'question': ["什么是 RAG？"],
    'answer': [生成的答案],
    'contexts': [检索到的文档列表],
    'ground_truth': [标准答案]
}

# 执行评估
result = evaluate(
    dataset=eval_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)

print(result)
```

### 9.2 人工评估清单

- [ ] 答案是否准确回答问题？
- [ ] 答案是否基于检索到的文档？
- [ ] 是否包含文档中不存在的信息（幻觉）？
- [ ] 检索到的文档是否相关？
- [ ] 答案是否完整？

---

## 十、优化技巧

### 10.1 分块优化

```python
# 添加元数据
for i, chunk in enumerate(chunks):
    chunk.metadata = {
        "source": "document.pdf",
        "page": chunk.metadata.get("page", 0),
        "chunk_id": i,
        "total_chunks": len(chunks)
    }
```

### 10.2 Prompt 优化

```python
prompt_template = """使用以下检索到的上下文回答问题。
如果上下文中没有相关信息，请说"根据提供的信息无法回答"。

上下文：
{context}

问题：{question}

要求：
1. 答案必须基于上下文
2. 如果答案不确定，请说明
3. 引用具体的段落或数字

答案："""
```

### 10.3 缓存策略

```python
from functools import lru_cache
import hashlib

# 缓存检索结果
@lru_cache(maxsize=100)
def cached_retrieve(query: str, k: int = 4):
    return vectorstore.similarity_search(query, k=k)

# 或使用 Redis
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def retrieve_with_cache(query: str):
    cache_key = hashlib.md5(query.encode()).hexdigest()
    
    # 检查缓存
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 检索
    results = vectorstore.similarity_search(query)
    
    # 存入缓存
    r.setex(cache_key, 3600, json.dumps(results))  # 1小时过期
    
    return results
```

---

## 十一、运行步骤

```bash
# 1. 安装依赖
pip install langchain langchain-openai langchain-community
pip install faiss-cpu  # 或 faiss-gpu
pip install pypdf  # PDF支持
pip install sentence-transformers  # 本地 Embedding

# 2. 进入项目目录
cd projects/07-advanced-rag

# 3. 配置环境变量
copy .env.example .env

# 4. 运行示例
python src/01-document-loaders/pdf_loader.py
python src/02-chunking-strategies/compare_strategies.py
python src/08-production-rag/complete_system.py
```

---

## 十二、生产环境检查清单

- [ ] 文档更新机制
- [ ] 向量库备份策略
- [ ] 检索性能监控
- [ ] 答案质量评估
- [ ] 错误处理和降级
- [ ] 成本控制（Token 使用）
- [ ] 用户反馈收集
- [ ] A/B 测试框架

---

## 十三、常见问题

### Q1: 检索到的文档不相关怎么办？

1. 优化分块策略（调整 chunk_size）
2. 改进查询（查询扩展、改写）
3. 使用混合检索
4. 尝试不同的 Embedding 模型

### Q2: 如何处理多语言文档？

1. 使用多语言 Embedding 模型
2. 分别建立不同语言的索引
3. 查询时检测语言并路由到对应索引

### Q3: 向量库数据如何更新？

```python
# 增量更新
new_chunks = load_and_chunk_new_documents()
vectorstore.add_documents(new_chunks)

# 定期重建
if should_rebuild():
    vectorstore = rebuild_vectorstore()
```

---

## 十四、相关资源

- [[知识图谱]] - 完整学习路径导航
- [[04-RAG教程]] - RAG 基础入门
- [[02-RAG系统优化]] - RAG 优化最佳实践
- [[01-Prompt设计模式]] - Prompt 工程技巧
- [[LangChain家族包详解]] - 包依赖关系

---

## 十五、参考资源

- [LangChain RAG 文档](https://python.langchain.com/docs/use_cases/question_answering/)
- [向量数据库对比](https://www.pinecone.io/learn/vector-database/)
- [RAG 评估框架 RAGAS](https://github.com/explodinggradients/ragas)

---

**构建智能的知识问答系统，从优化 RAG 开始！**
