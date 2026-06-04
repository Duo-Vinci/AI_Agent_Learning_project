# RAG（检索增强生成）教程

## 一、项目概述

本项目演示如何使用 LangChain 实现 RAG（Retrieval-Augmented Generation），让 AI 能够基于自定义文档进行问答。

**项目位置**：`projects/04-langchain-rag/`

**学习目标**：
- 理解 RAG 的概念和原理
- 学习如何构建向量数据库
- 掌握文档检索和问答的流程

---

## 二、核心概念

### 2.1 什么是 RAG

RAG 是一种增强大语言模型能力的技术：
1. **检索**：从文档库中检索相关信息
2. **生成**：基于检索到的信息生成回答

### 2.2 向量数据库

向量数据库用于存储文档的向量表示，便于快速检索相似内容。

---

## 三、RAG 流程示意图

```
┌─────────────────────────────────────────────────────────────────┐
│ 步骤1: 文档准备                                                 │
│  将文档分割成小块，转换为向量存储到向量数据库                        │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 步骤2: 用户提问                                                  │
│  用户问："LangChain 的主要功能是什么？"                            │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 步骤3: 向量检索                                                 │
│  将用户问题转换为向量，在向量数据库中查找相似文档                     │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 步骤4: 生成回答                                                  │
│  将检索到的文档作为上下文，让 LLM 生成基于文档的回答                 │
└─────────────────────────────────────────────────────────────────┘
```

### 详细流程

```
文档库                              用户问题
   ↓                                    ↓
文档分割 → 向量化 → 向量数据库      问题向量化
                           ↘        ↓
                            向量相似度匹配
                                 ↓
                          检索相关文档
                                 ↓
                    将文档作为上下文传给 LLM
                                 ↓
                          生成基于文档的回答
```

---

## 四、代码解析

### 4.1 加载和分割文档

```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

loader = TextLoader("documents/knowledge.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)
```

**作用**：将文档加载并分割成小块。

### 4.2 创建向量数据库

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
db = FAISS.from_documents(docs, embeddings)
```

**作用**：创建向量数据库并存储文档向量。

### 4.3 创建检索问答链

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="deepseek-v4-flash", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(),
    return_source_documents=True
)
```

**作用**：创建检索问答链。

### 4.4 执行问答

```python
result = qa_chain({"query": "LangChain 的主要功能是什么？"})
print(result["result"])
```

**作用**：执行检索并生成回答。

---

## 五、运行步骤

```bash
# 1. 安装依赖
pip install langchain langchain-openai python-dotenv faiss-cpu

# 2. 创建 .env 文件
cd projects/04-langchain-rag
copy .env.example .env
# 编辑 .env 添加您的 API Key

# 3. 创建文档目录并添加文档
mkdir documents
# 在 documents 目录下创建 knowledge.txt 文件

# 4. 运行脚本
python src/simple_rag.py
```

---

## 六、关键概念

### 6.1 文档分割策略

- **chunk_size**：每个文档块的大小
- **chunk_overlap**：文档块之间的重叠部分

### 6.2 向量数据库选择

常用的向量数据库：
- FAISS（Facebook，适合本地开发）
- Pinecone（云服务）
- Chroma（轻量级）

### 6.3 Chain Type

常用的链类型：
- `stuff`：将所有文档塞进提示词
- `map_reduce`：分别处理每个文档再汇总
- `refine`：逐步优化回答

---

## 七、注意事项

1. **文档质量**：文档质量直接影响回答质量
2. **向量模型选择**：选择合适的嵌入模型
3. **检索效果**：调整检索参数优化结果

---

## 八、进阶扩展

可以尝试：
1. 使用更多类型的文档加载器
2. 尝试不同的向量数据库
3. 添加文档更新功能
4. 实现多轮对话的 RAG