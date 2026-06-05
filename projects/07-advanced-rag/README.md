# 高级RAG系统 - 完整实现

本项目提供了从基础到生产级的完整RAG（检索增强生成）系统实现，包含8个子模块，覆盖RAG系统的所有核心组件。

## 项目结构

```
07-advanced-rag/
├── 01-document-loaders/        # 文档加载器
│   └── src/
│       ├── pdf_loader.py       # PDF加载
│       ├── word_loader.py      # Word文档加载
│       ├── markdown_loader.py  # Markdown加载
│       ├── html_loader.py      # HTML加载
│       └── universal_loader.py # 统一加载器
├── 02-chunking-strategies/     # 分块策略
│   └── src/
│       ├── fixed_size_chunking.py      # 固定大小分块
│       ├── semantic_chunking.py        # 语义分块
│       ├── recursive_chunking.py       # 递归分块
│       └── compare_strategies.py       # 策略对比
├── 03-embedding-comparison/    # Embedding对比
│   └── src/
│       └── compare_embeddings.py       # 模型对比
├── 04-vector-databases/        # 向量数据库
│   └── src/
│       ├── faiss_vectorstore.py        # FAISS
│       └── chroma_vectorstore.py       # ChromaDB
├── 05-retrieval-strategies/    # 检索策略
│   └── src/
│       └── retrieval_methods.py        # 多种检索方法
├── 06-evaluation/              # RAG评估
│   └── src/
│       └── rag_evaluation.py           # 评估指标
├── 07-hybrid-search/           # 混合检索
│   └── src/
│       └── hybrid_retrieval.py         # 混合搜索
└── 08-production-rag/          # 生产级系统
    └── src/
        └── complete_system.py          # 完整RAG系统
```

## 快速开始

### 1. 安装依赖

```bash
cd projects/07-advanced-rag
pip install -r requirements.txt
```

### 2. 运行示例

#### 文档加载
```bash
# PDF加载
python 01-document-loaders/src/pdf_loader.py

# 统一加载器（支持多种格式）
python 01-document-loaders/src/universal_loader.py
```

#### 分块策略
```bash
# 固定大小分块
python 02-chunking-strategies/src/fixed_size_chunking.py

# 对比不同策略
python 02-chunking-strategies/src/compare_strategies.py
```

#### 向量数据库
```bash
# FAISS向量存储
python 04-vector-databases/src/faiss_vectorstore.py

# ChromaDB向量存储
python 04-vector-databases/src/chroma_vectorstore.py
```

#### 检索策略
```bash
# 多种检索方法
python 05-retrieval-strategies/src/retrieval_methods.py

# 混合检索
python 07-hybrid-search/src/hybrid_retrieval.py
```

#### 完整RAG系统
```bash
# 生产级RAG系统
python 08-production-rag/src/complete_system.py
```

## 核心功能

### 1. 文档加载器 (01-document-loaders)

支持多种文档格式：
- **PDF**: PyPDFLoader，支持页面范围选择
- **Word**: Docx2txtLoader，提取文本内容
- **Markdown**: UnstructuredMarkdownLoader，保留结构
- **HTML**: UnstructuredHTMLLoader和WebBaseLoader，支持网页抓取
- **统一接口**: 自动识别文件类型

### 2. 分块策略 (02-chunking-strategies)

多种分块方法：
- **固定大小**: 按字符或Token数分割
- **递归分块**: 按文档结构递归分割（推荐）
- **语义分块**: 基于语义相似度智能分块
- **结构化分块**: Markdown标题、代码函数等

**推荐配置**：
- 技术文档: chunk_size=800, overlap=100
- 新闻文章: chunk_size=400, overlap=50
- 对话记录: chunk_size=300, overlap=30

### 3. Embedding模型 (03-embedding-comparison)

支持的模型：
- **BGE-Small-ZH**: 384维，快速，中文优化
- **BGE-Base-ZH**: 768维，平衡，推荐使用
- **BGE-Large-ZH**: 1024维，效果最好

### 4. 向量数据库 (04-vector-databases)

- **FAISS**: 快速、本地、适合原型开发
- **ChromaDB**: 持久化、易用、适合生产环境

### 5. 检索策略 (05-retrieval-strategies)

多种检索方法：
- 相似度搜索、MMR搜索、混合检索
- 多查询检索、上下文压缩

### 6. RAG评估 (06-evaluation)

评估指标：
- **检索质量**: Precision, Recall, F1, MRR, NDCG
- **答案相关性**: 答案与查询的语义相似度
- **答案忠实度**: 答案是否基于检索文档

### 7. 混合搜索 (07-hybrid-search)

结合密集检索（向量）和稀疏检索（BM25）

### 8. 生产级系统 (08-production-rag)

完整的端到端RAG系统，包含文档管理、索引构建、混合检索、错误处理等

## 最佳实践

### 分块策略选择
1. 选择合适大小（太小上下文不足，太大噪音增加）
2. 保持10-20%重叠保证连续性
3. 尊重文档结构，不在句子中间分割

### Embedding选择
1. 中文任务优先选择BGE系列
2. 性能要求高用Small，效果要求高用Large
3. 对常见查询使用缓存

### 检索优化
1. 使用混合检索结合向量和关键词
2. 根据任务调整k值和权重
3. 使用重排序提高精度

## 常见问题

**Q1: 检索结果不相关？**
- 调整chunk_size和overlap
- 使用混合检索
- 尝试不同的Embedding模型

**Q2: 答案产生幻觉？**
- 改进检索质量
- 在Prompt中强调"仅基于上下文"
- 降低LLM的temperature

**Q3: 系统响应慢？**
- 优化FAISS索引
- 使用Embedding缓存
- 减少retrieval_k值

## 参考资源

- [LangChain文档](https://python.langchain.com/)
- [FAISS文档](https://github.com/facebookresearch/faiss)
- [BGE模型](https://huggingface.co/BAAI/bge-large-zh-v1.5)

---

**构建高质量的RAG系统，从这里开始！**
