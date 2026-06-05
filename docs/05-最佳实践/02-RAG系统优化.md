# RAG 系统优化最佳实践

## 一、概述

本文档总结 RAG（检索增强生成）系统的优化经验和最佳实践，帮助你构建高质量、高性能的知识问答系统。

---

## 二、文档处理优化

### 2.1 文档预处理

```python
import re
from typing import List

def preprocess_document(text: str) -> str:
    """文档预处理"""
    # 1. 统一换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. 移除多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # 3. 修复常见问题
    text = text.replace('�', '')  # 移除乱码字符
    
    # 4. 标准化标点符号
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()
```

### 2.2 智能分块策略

**推荐配置**：
- **技术文档**: chunk_size=800, overlap=100
- **新闻文章**: chunk_size=400, overlap=50
- **对话记录**: chunk_size=300, overlap=30
- **代码文件**: 按函数/类分块

```python
def smart_chunking(text: str, doc_type: str) -> List[str]:
    """根据文档类型智能分块"""
    
    configs = {
        'technical': {'size': 800, 'overlap': 100},
        'news': {'size': 400, 'overlap': 50},
        'conversation': {'size': 300, 'overlap': 30},
        'code': {'size': 1000, 'overlap': 50}
    }
    
    config = configs.get(doc_type, {'size': 500, 'overlap': 50})
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['size'],
        chunk_overlap=config['overlap'],
        separators=["\n\n", "\n", "。", ".", " ", ""]
    )
    
    return splitter.split_text(text)
```

---

## 三、检索优化

### 3.1 混合检索

结合向量检索和关键词检索：

```python
from langchain.retrievers import EnsembleRetriever

# 向量检索（语义相似）
vector_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# BM25 关键词检索
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 5

# 混合检索器
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4]  # 向量60%，关键词40%
)
```

### 3.2 重排序

使用 Cross-Encoder 重排序检索结果：

```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
    
    def rerank(self, query: str, documents: List[str], top_k: int = 3):
        """重排序文档"""
        # 计算相关性分数
        pairs = [[query, doc] for doc in documents]
        scores = self.model.predict(pairs)
        
        # 排序
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        
        return [documents[i] for i in ranked_indices]
```

### 3.3 查询优化

**查询扩展**：
```python
async def expand_query(query: str) -> List[str]:
    """查询扩展"""
    prompt = f"""生成3个与以下查询相关的变体问题：
    
原始查询：{query}

变体查询（每行一个）："""
    
    result = await llm.agenerate(prompt)
    variants = result.split('\n')
    
    return [query] + variants
```

**查询改写**：
```python
async def rewrite_query(query: str, context: str) -> str:
    """基于上下文改写查询"""
    prompt = f"""根据对话上下文，将用户查询改写为独立的完整问题。

上下文：{context}

用户查询：{query}

改写后的查询："""
    
    return await llm.agenerate(prompt)
```

---

## 四、Embedding 优化

### 4.1 模型选择

| 场景 | 推荐模型 | 说明 |
|------|---------|------|
| 中文通用 | BAAI/bge-large-zh-v1.5 | 效果好，免费 |
| 英文通用 | text-embedding-3-large | OpenAI 最新 |
| 多语言 | paraphrase-multilingual-MiniLM | 轻量级 |
| 代码检索 | Salesforce/codet5-base | 代码专用 |

### 4.2 Embedding 缓存

```python
import hashlib
from functools import lru_cache

class EmbeddingCache:
    def __init__(self, embeddings, cache_size: int = 10000):
        self.embeddings = embeddings
        self.cache = {}
        self.max_size = cache_size
    
    def embed_query(self, text: str):
        """带缓存的查询 Embedding"""
        key = hashlib.md5(text.encode()).hexdigest()
        
        if key in self.cache:
            return self.cache[key]
        
        embedding = self.embeddings.embed_query(text)
        
        if len(self.cache) < self.max_size:
            self.cache[key] = embedding
        
        return embedding
```

---

## 五、Prompt 优化

### 5.1 RAG Prompt 模板

```python
RAG_PROMPT = """根据以下上下文回答问题。

上下文信息：
{context}

回答要求：
1. 答案必须基于上下文
2. 如果上下文中没有相关信息，明确说"根据提供的信息无法回答"
3. 引用具体的段落或数据支持你的答案
4. 保持简洁准确

问题：{question}

答案："""
```

### 5.2 引用来源

```python
CITATION_PROMPT = """根据提供的文档回答问题，并标注信息来源。

文档：
{documents}

问题：{question}

请按以下格式回答：
答案：[你的答案]
来源：[文档1], [文档2]

回答："""
```

---

## 六、性能优化

### 6.1 批量处理

```python
async def batch_embed_documents(texts: List[str], batch_size: int = 32):
    """批量 Embedding"""
    embeddings_list = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = await embeddings.aembed_documents(batch)
        embeddings_list.extend(embeddings)
    
    return embeddings_list
```

### 6.2 异步检索

```python
async def parallel_retrieval(queries: List[str]):
    """并行检索多个查询"""
    tasks = [retriever.aget_relevant_documents(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

### 6.3 向量库优化

**FAISS 索引选择**：
- **小数据集(<10k)**: Flat (精确搜索)
- **中等数据集(10k-1M)**: IVF (倒排索引)
- **大数据集(>1M)**: HNSW (层次导航)

```python
import faiss

def create_optimized_index(dimension: int, num_vectors: int):
    """创建优化的 FAISS 索引"""
    if num_vectors < 10000:
        # Flat: 精确但慢
        index = faiss.IndexFlatL2(dimension)
    
    elif num_vectors < 1000000:
        # IVF: 平衡速度和精度
        nlist = int(np.sqrt(num_vectors))
        quantizer = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
    
    else:
        # HNSW: 快速近似
        index = faiss.IndexHNSWFlat(dimension, 32)
    
    return index
```

---

## 七、质量评估

### 7.1 评估指标

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,      # 答案是否基于文档
    answer_relevancy,  # 答案是否相关
    context_precision, # 检索精确度
    context_recall     # 检索召回率
)

def evaluate_rag_system(test_data):
    """评估 RAG 系统"""
    result = evaluate(
        dataset=test_data,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    )
    
    return result
```

### 7.2 A/B 测试

```python
class ABTester:
    """A/B 测试框架"""
    
    def __init__(self):
        self.variants = {}
        self.results = {'A': [], 'B': []}
    
    def add_variant(self, name: str, retriever):
        self.variants[name] = retriever
    
    async def test_query(self, query: str, ground_truth: str):
        """测试单个查询"""
        for name, retriever in self.variants.items():
            docs = await retriever.aget_relevant_documents(query)
            answer = await generate_answer(query, docs)
            
            score = calculate_similarity(answer, ground_truth)
            self.results[name].append(score)
    
    def get_winner(self):
        """获取胜出方案"""
        avg_scores = {
            name: np.mean(scores)
            for name, scores in self.results.items()
        }
        return max(avg_scores.items(), key=lambda x: x[1])
```

---

## 八、成本优化

### 8.1 缓存策略

```python
from functools import lru_cache
import redis

class RAGCache:
    """RAG 结果缓存"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1小时
    
    async def get_or_generate(self, query: str):
        """获取缓存或生成"""
        cache_key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
        
        # 检查缓存
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 生成答案
        answer = await rag_chain.ainvoke(query)
        
        # 缓存结果
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps(answer)
        )
        
        return answer
```

### 8.2 文档去重

```python
def deduplicate_chunks(chunks: List[str], threshold: float = 0.9):
    """去除相似重复的文档块"""
    unique_chunks = []
    embeddings_list = []
    
    for chunk in chunks:
        embedding = embeddings.embed_query(chunk)
        
        # 检查是否与已有块相似
        is_duplicate = False
        for existing_emb in embeddings_list:
            similarity = cosine_similarity([embedding], [existing_emb])[0][0]
            if similarity > threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_chunks.append(chunk)
            embeddings_list.append(embedding)
    
    return unique_chunks
```

---

## 九、监控和调试

### 9.1 检索质量监控

```python
class RetrievalMonitor:
    """检索质量监控"""
    
    def __init__(self):
        self.metrics = {
            'avg_relevance_score': [],
            'avg_num_docs': [],
            'cache_hit_rate': 0
        }
    
    def log_retrieval(self, query: str, docs: List, relevance_scores: List[float]):
        """记录检索"""
        self.metrics['avg_relevance_score'].append(np.mean(relevance_scores))
        self.metrics['avg_num_docs'].append(len(docs))
        
        # 检查质量
        if np.mean(relevance_scores) < 0.5:
            logger.warning(f"Low relevance for query: {query}")
    
    def get_report(self):
        """生成报告"""
        return {
            'avg_relevance': np.mean(self.metrics['avg_relevance_score']),
            'avg_docs_retrieved': np.mean(self.metrics['avg_num_docs'])
        }
```

---

## 十、常见问题解决方案

### 问题1：检索结果不相关

**原因**：
- 文档分块不当
- Embedding 模型不适合
- 查询表达不清

**解决方案**：
1. 调整分块策略
2. 尝试不同的 Embedding 模型
3. 使用查询改写
4. 添加混合检索

### 问题2：答案包含幻觉

**原因**：
- 检索文档不相关
- Prompt 设计不当
- 温度参数过高

**解决方案**：
1. 改进检索质量
2. 强调"仅基于上下文回答"
3. 降低 temperature
4. 使用答案验证

### 问题3：性能慢

**原因**：
- 向量库索引不优化
- 没有使用缓存
- 检索文档过多

**解决方案**：
1. 优化 FAISS 索引
2. 添加多层缓存
3. 减少 top_k 参数
4. 使用异步处理

---

## 十一、检查清单

**开发阶段**：
- [ ] 文档预处理完善
- [ ] 分块策略合理
- [ ] Embedding 模型选择恰当
- [ ] 检索策略优化
- [ ] Prompt 设计清晰

**测试阶段**：
- [ ] 评估指标达标
- [ ] A/B 测试完成
- [ ] 边界情况测试
- [ ] 性能测试通过

**上线阶段**：
- [ ] 缓存策略配置
- [ ] 监控告警设置
- [ ] 成本控制措施
- [ ] 降级方案准备

---

## 十二、相关资源

- [[知识图谱]] - 完整学习路径导航
- [[04-RAG教程]] - RAG 基础入门
- [[07-高级RAG教程]] - 高级检索策略
- [[01-Prompt设计模式]] - Prompt 工程技巧

---

**持续优化，构建高质量 RAG 系统！**
