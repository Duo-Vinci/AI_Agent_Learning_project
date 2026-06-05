# LangChain RAG 项目

完整的检索增强生成（RAG）系统实现，从文档加载到高级检索策略。

## 项目概述

RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术，让AI能够基于自定义知识库回答问题。

本项目包含：
- **quickstart.py**: 快速入门（5分钟上手RAG）
- **simple_rag.py**: 基础RAG实现

## 学习目标

- ✅ 理解RAG的原理和工作流程
- ✅ 掌握文档加载和预处理
- ✅ 学习文本分块策略
- ✅ 理解向量嵌入和相似度搜索
- ✅ 构建向量数据库（FAISS）
- ✅ 实现检索问答系统
- ✅ 优化检索质量

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 API Key
```

### 3. 运行快速入门

```bash
# 最快的RAG体验
python src/quickstart.py
```

## 核心概念

### RAG工作流程

```
1. 索引阶段（离线）:
   文档 → 分块 → 向量化 → 存储到向量数据库

2. 检索阶段（在线）:
   问题 → 向量化 → 相似度搜索 → 获取相关文档

3. 生成阶段:
   问题 + 检索到的文档 → LLM → 生成答案
```

### 关键组件

#### 1. 文档加载器
```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader

# 加载文本文件
loader = TextLoader("document.txt")
documents = loader.load()

# 加载PDF
pdf_loader = PyPDFLoader("document.pdf")
pdf_documents = pdf_loader.load()
```

#### 2. 文本分块
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块大小
    chunk_overlap=50,    # 块之间重叠
    separators=["\n\n", "\n", "。", " "]
)

chunks = splitter.split_documents(documents)
```

#### 3. 向量嵌入
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_BASE")
)
```

#### 4. 向量存储
```python
from langchain_community.vectorstores import FAISS

# 创建向量库
vectorstore = FAISS.from_documents(documents, embeddings)

# 保存
vectorstore.save_local("vectorstore")

# 加载
vectorstore = FAISS.load_local("vectorstore", embeddings)
```

#### 5. 检索问答
```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True
)

result = qa_chain.invoke({"query": "你的问题"})
```

## 使用示例

### 基础RAG示例
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

# 1. 准备文档
docs = [
    Document(page_content="LangChain是一个AI应用开发框架。"),
    Document(page_content="RAG结合了检索和生成技术。")
]

# 2. 创建向量存储
embeddings = OpenAIEmbeddings(api_key="your_key")
vectorstore = FAISS.from_documents(docs, embeddings)

# 3. 创建问答链
llm = ChatOpenAI(model="gpt-3.5-turbo")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

# 4. 提问
answer = qa.invoke({"query": "什么是LangChain？"})
print(answer['result'])
```

## 文本分块策略

### 1. 按字符分块
```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

### 2. 递归分块（推荐）
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)
```

### 3. 按Token分块
```python
from langchain.text_splitter import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=100,
    chunk_overlap=10
)
```

## 检索策略

### 1. 相似度搜索
```python
# 返回最相似的k个文档
docs = vectorstore.similarity_search("查询", k=3)
```

### 2. 带分数的相似度搜索
```python
# 返回文档和相似度分数
docs_with_scores = vectorstore.similarity_search_with_score("查询", k=3)
```

### 3. MMR检索（最大边际相关性）
```python
# 平衡相关性和多样性
docs = vectorstore.max_marginal_relevance_search("查询", k=3)
```

## 优化技巧

### 1. 文档质量
- 清理文档（去除无关内容）
- 保持格式一致性
- 添加元数据（标题、日期、来源）

### 2. 分块优化
- 根据文档类型调整chunk_size
- 设置合适的overlap避免信息丢失
- 保持语义完整性

### 3. 检索优化
- 调整k值（返回文档数量）
- 使用混合检索（向量+关键词）
- 添加重排序（Reranking）

### 4. 提示优化
```python
from langchain_core.prompts import PromptTemplate

template = """
基于以下上下文回答问题。如果无法从上下文中找到答案，请说"我不知道"。

上下文:
{context}

问题: {question}

答案:"""

prompt = PromptTemplate.from_template(template)
```

## 常见问题

### Q: RAG和微调的区别？
- **RAG**: 检索外部知识，无需训练，更新知识容易
- **微调**: 将知识注入模型，需要训练，更新成本高

### Q: 如何选择chunk_size？
- 太小：上下文不足，答案质量差
- 太大：检索精度低，token消耗多
- 推荐：200-1000字符，根据文档类型调整

### Q: 向量数据库怎么选？
- **FAISS**: 快速、本地、适合中小规模
- **Chroma**: 易用、支持持久化
- **Pinecone**: 云服务、适合大规模生产

### Q: 如何提高检索准确性？
1. 优化文档分块
2. 使用更好的嵌入模型
3. 增加检索数量k
4. 添加重排序步骤
5. 使用混合检索

## 注意事项

- ⚠️ 文档质量直接影响回答质量
- ⚠️ 注意选择合适的嵌入模型
- ⚠️ 控制返回文档数量（k值），避免超过上下文限制
- ⚠️ 敏感信息不要放入向量数据库
- ✅ 定期更新知识库
- ✅ 监控检索质量
- ✅ 添加引用来源

## 相关教程

- 对应教程：`docs/02-教程/04-RAG教程.md`
- LangChain RAG文档：https://python.langchain.com/docs/use_cases/question_answering/

## 下一步

完成本项目后，可以继续学习：
- **项目05**: Agent自主代理系统
- 高级RAG技术（HyDE、Self-Query等）
- 多模态RAG（图像、音频）

## 许可证

MIT License