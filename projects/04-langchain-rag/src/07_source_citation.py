"""
LangChain RAG应用 - 07: 来源引用（Source Citation）

本模块演示：
1. 答案溯源基础
2. 文档引用格式化
3. 置信度评分
4. 引用排序和过滤
5. 多文档引用合并
6. 引用展示优化

来源引用让RAG系统的答案可验证，增强用户信任。
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 基础答案溯源 ====================

def demo_basic_citation():
    """示例1: 基础答案溯源"""
    print_section("示例1: 基础答案溯源")

    print("答案溯源的重要性:")
    print("  ✓ 增强可信度")
    print("  ✓ 便于验证")
    print("  ✓ 发现错误来源")
    print("  ✓ 符合学术/法律要求\n")

    print("基础实现:")
    print("""
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True  # 关键参数
)

result = qa_chain({"query": "什么是LangChain？"})

print("答案:", result["result"])
print("\\n来源文档:")
for i, doc in enumerate(result["source_documents"], 1):
    print(f"{i}. {doc.page_content}")
    print(f"   来源: {doc.metadata.get('source', 'Unknown')}")
    """)

    print("\n示例输出:")
    print("""
答案: LangChain是一个用于构建LLM应用的开源框架。

来源文档:
1. LangChain是一个开源框架，用于构建基于大型语言模型的应用...
   来源: langchain_intro.pdf (页码: 1)

2. LangChain由Harrison Chase于2022年创建...
   来源: langchain_intro.pdf (页码: 2)

3. LangChain提供了丰富的组件和工具...
   来源: langchain_guide.md
    """)

    print("\n元数据最佳实践:")
    print("  • source: 文件名或URL")
    print("  • page: 页码")
    print("  • section: 章节")
    print("  • author: 作者")
    print("  • date: 日期")
    print("  • chunk_id: 块ID\n")


# ==================== 示例2: 引用格式化 ====================

def demo_citation_formatting():
    """示例2: 文档引用格式化"""
    print_section("示例2: 文档引用格式化")

    print("常见引用格式:\n")

    # 示例文档
    doc = Document(
        page_content="LangChain是一个强大的AI开发框架。",
        metadata={
            "source": "langchain_guide.pdf",
            "page": 5,
            "author": "Harrison Chase",
            "date": "2023-10-15"
        }
    )

    print("1. 简单格式:")
    print(f"   [{doc.metadata['source']}]")

    print("\n2. 标准格式:")
    print(f"   [{doc.metadata['source']}, p.{doc.metadata['page']}]")

    print("\n3. 学术格式 (APA风格):")
    print(f"   ({doc.metadata['author']}, {doc.metadata['date'][:4]}, p.{doc.metadata['page']})")

    print("\n4. 带链接格式:")
    print(f"   [参考文献{1}]({doc.metadata['source']})")

    print("\n5. 内联引用:")
    answer = "LangChain是一个强大的AI开发框架"
    citation = f"[{doc.metadata['source']}, p.{doc.metadata['page']}]"
    print(f"   {answer} {citation}")

    print("\n实现代码:")
    print("""
def format_citation(doc: Document, style: str = "standard") -> str:
    '''格式化文档引用'''
    if style == "simple":
        return f"[{doc.metadata.get('source', 'Unknown')}]"

    elif style == "standard":
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', '')
        if page:
            return f"[{source}, p.{page}]"
        return f"[{source}]"

    elif style == "apa":
        author = doc.metadata.get('author', 'Unknown')
        date = doc.metadata.get('date', 'n.d.')[:4]
        page = doc.metadata.get('page', '')
        if page:
            return f"({author}, {date}, p.{page})"
        return f"({author}, {date})"

    elif style == "inline":
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', '')
        return f"[{source}" + (f", p.{page}]" if page else "]")

# 使用
for doc in source_documents:
    citation = format_citation(doc, style="standard")
    print(citation)
    """)

    print("\n选择建议:")
    print("  • 技术文档: standard")
    print("  • 学术论文: apa")
    print("  • 在线内容: 带链接格式")
    print("  • 聊天机器人: inline\n")


# ==================== 示例3: 置信度评分 ====================

def demo_confidence_scoring():
    """示例3: 置信度评分"""
    print_section("示例3: 置信度评分")

    print("置信度评分的作用:")
    print("  ✓ 评估答案可靠性")
    print("  ✓ 过滤低质量引用")
    print("  ✓ 排序展示引用")
    print("  ✓ 提供不确定性提示\n")

    print("评分维度:\n")

    print("1. 相似度分数")
    print("   • 来自向量搜索")
    print("   • 范围: 0-1")
    print("   • 越高越相关\n")

    print("2. 内容覆盖度")
    print("   • 答案中有多少内容来自该文档")
    print("   • 计算关键词重叠\n")

    print("3. 文档质量")
    print("   • 文档新鲜度")
    print("   • 来源权威性")
    print("   • 文档完整性\n")

    print("综合评分示例:")
    print("""
def calculate_confidence(doc: Document, query: str,
                        answer: str, similarity_score: float) -> float:
    '''计算文档的置信度分数'''

    # 1. 相似度分数 (40%)
    sim_score = similarity_score * 0.4

    # 2. 覆盖度分数 (30%)
    answer_words = set(answer.lower().split())
    doc_words = set(doc.page_content.lower().split())
    overlap = len(answer_words & doc_words) / len(answer_words)
    coverage_score = overlap * 0.3

    # 3. 文档质量 (30%)
    quality_score = 0.3
    if 'date' in doc.metadata:
        # 新文档加分
        from datetime import datetime
        doc_date = datetime.strptime(doc.metadata['date'], '%Y-%m-%d')
        days_old = (datetime.now() - doc_date).days
        if days_old < 30:
            quality_score = 0.3
        elif days_old < 365:
            quality_score = 0.2
        else:
            quality_score = 0.1

    return sim_score + coverage_score + quality_score

# 使用
for doc, score in zip(source_documents, similarity_scores):
    confidence = calculate_confidence(doc, query, answer, score)
    print(f"置信度: {confidence:.2f} - {doc.page_content[:50]}...")
    """)

    print("\n置信度等级:")
    print("  • 0.8-1.0: 高置信度 ⭐⭐⭐")
    print("  • 0.6-0.8: 中置信度 ⭐⭐")
    print("  • 0.4-0.6: 低置信度 ⭐")
    print("  • 0.0-0.4: 不确定\n")

    print("应用示例:")
    results = [
        ("LangChain是一个AI框架...", 0.92, "⭐⭐⭐"),
        ("LangChain提供丰富的工具...", 0.75, "⭐⭐"),
        ("Python是编程语言...", 0.35, "不确定"),
    ]

    print(f"{'引用内容':<40} {'置信度':<8} {'等级'}")
    print("-" * 60)
    for content, conf, level in results:
        print(f"{content:<40} {conf:<8.2f} {level}")
    print()


# ==================== 示例4: 引用排序和过滤 ====================

def demo_citation_filtering():
    """示例4: 引用排序和过滤"""
    print_section("示例4: 引用排序和过滤")

    print("为什么需要排序和过滤:")
    print("  ✓ 突出最相关的引用")
    print("  ✓ 减少信息过载")
    print("  ✓ 提高用户体验\n")

    print("排序策略:\n")

    print("1. 按相似度排序")
    print("""
# 降序排列，最相关的在前
sorted_docs = sorted(
    zip(source_documents, similarity_scores),
    key=lambda x: x[1],
    reverse=True
)
    """)

    print("\n2. 按置信度排序")
    print("""
# 综合多个因素
sorted_docs = sorted(
    source_documents,
    key=lambda doc: calculate_confidence(doc),
    reverse=True
)
    """)

    print("\n3. 去重")
    print("""
def deduplicate_docs(documents: List[Document],
                     threshold: float = 0.9) -> List[Document]:
    '''去除内容高度相似的文档'''
    unique_docs = []
    for doc in documents:
        is_duplicate = False
        for unique_doc in unique_docs:
            similarity = calculate_text_similarity(
                doc.page_content,
                unique_doc.page_content
            )
            if similarity > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_docs.append(doc)
    return unique_docs
    """)

    print("\n过滤策略:\n")

    print("1. 阈值过滤")
    print("""
# 只保留高分引用
filtered_docs = [
    doc for doc, score in zip(documents, scores)
    if score > 0.7
]
    """)

    print("\n2. Top-K过滤")
    print("""
# 只保留前K个
top_k_docs = sorted_docs[:3]
    """)

    print("\n3. 多样性过滤")
    print("""
# 使用MMR确保多样性
from langchain.vectorstores import FAISS

docs = vectorstore.max_marginal_relevance_search(
    query,
    k=3,
    fetch_k=10,
    lambda_mult=0.5
)
    """)

    print("\n完整示例:")
    print("""
def filter_and_sort_citations(documents: List[Document],
                              scores: List[float],
                              min_score: float = 0.6,
                              max_citations: int = 3) -> List[Tuple[Document, float]]:
    '''过滤和排序引用'''

    # 1. 过滤低分
    filtered = [(doc, score) for doc, score in zip(documents, scores)
                if score >= min_score]

    # 2. 排序
    sorted_docs = sorted(filtered, key=lambda x: x[1], reverse=True)

    # 3. 限制数量
    top_docs = sorted_docs[:max_citations]

    # 4. 去重
    unique_docs = []
    seen_content = set()
    for doc, score in top_docs:
        content_hash = hash(doc.page_content[:100])
        if content_hash not in seen_content:
            unique_docs.append((doc, score))
            seen_content.add(content_hash)

    return unique_docs
    """)


# ==================== 示例5: 多文档引用合并 ====================

def demo_multi_doc_citation():
    """示例5: 多文档引用合并"""
    print_section("示例5: 多文档引用合并")

    print("合并场景:")
    print("  • 答案来自多个文档")
    print("  • 需要综合引用")
    print("  • 避免引用冗余\n")

    print("方法1: 列表式引用")
    print("""
答案: LangChain是一个强大的AI开发框架，提供了丰富的组件。

参考来源:
[1] langchain_intro.pdf, p.1
[2] langchain_guide.md, section 2.1
[3] official_docs.html
    """)

    print("\n方法2: 内联引用")
    print("""
答案: LangChain是一个强大的AI开发框架[1]，提供了丰富的组件[2]，
      支持多种向量数据库[3]。

参考文献:
[1] langchain_intro.pdf, p.1
[2] langchain_guide.md, section 2.1
[3] vector_stores.pdf, p.5
    """)

    print("\n方法3: 脚注式引用")
    print("""
答案: LangChain是一个强大的AI开发框架¹，提供了丰富的组件²。

¹ Harrison Chase (2022). "LangChain Introduction", p.1
² LangChain Documentation (2023). "Core Components"
    """)

    print("\n实现代码:")
    print("""
def format_answer_with_citations(answer: str,
                                source_documents: List[Document],
                                style: str = "list") -> str:
    '''生成带引用的答案'''

    if style == "list":
        result = f"答案: {answer}\\n\\n参考来源:\\n"
        for i, doc in enumerate(source_documents, 1):
            citation = format_citation(doc, style="standard")
            result += f"[{i}] {citation}\\n"
        return result

    elif style == "inline":
        # 在答案中插入引用标记
        result = answer
        references = "\\n\\n参考文献:\\n"
        for i, doc in enumerate(source_documents, 1):
            # 简化：在句末添加引用
            citation = format_citation(doc, style="standard")
            references += f"[{i}] {citation}\\n"
        return result + references

    elif style == "footnote":
        result = answer
        footnotes = "\\n\\n"
        for i, doc in enumerate(source_documents, 1):
            author = doc.metadata.get('author', 'Unknown')
            year = doc.metadata.get('date', 'n.d.')[:4]
            title = doc.metadata.get('title', doc.metadata.get('source'))
            footnotes += f"{'¹²³⁴⁵⁶⁷⁸⁹'[i-1]} {author} ({year}). \"{title}\"\\n"
        return result + footnotes
    """)


# ==================== 示例6: 引用展示优化 ====================

def demo_citation_display():
    """示例6: 引用展示优化"""
    print_section("示例6: 引用展示优化")

    print("展示优化原则:")
    print("  ✓ 清晰易读")
    print("  ✓ 层次分明")
    print("  ✓ 交互友好")
    print("  ✓ 适应不同场景\n")

    print("1. 命令行展示:")
    print("""
╔══════════════════════════════════════════════════════════════╗
║ 答案                                                         ║
╚══════════════════════════════════════════════════════════════╝

LangChain是一个用于构建LLM应用的开源框架。

┌──────────────────────────────────────────────────────────────┐
│ 📚 参考来源 (3个)                                            │
├──────────────────────────────────────────────────────────────┤
│ [1] langchain_intro.pdf, p.1              置信度: ⭐⭐⭐     │
│     LangChain是一个开源框架，用于构建...                     │
│                                                              │
│ [2] langchain_guide.md, section 2        置信度: ⭐⭐       │
│     LangChain提供了丰富的组件...                             │
│                                                              │
│ [3] official_docs.html                    置信度: ⭐⭐       │
│     Harrison Chase创建了LangChain...                         │
└──────────────────────────────────────────────────────────────┘
    """)

    print("\n2. Web界面展示 (HTML):")
    print("""
<div class="answer-container">
    <div class="answer">
        <h3>答案</h3>
        <p>LangChain是一个用于构建LLM应用的开源框架。</p>
    </div>

    <div class="sources">
        <h4>📚 参考来源</h4>
        <div class="source-item">
            <span class="source-number">[1]</span>
            <span class="source-citation">langchain_intro.pdf, p.1</span>
            <span class="confidence">⭐⭐⭐</span>
            <details>
                <summary>查看详情</summary>
                <p>LangChain是一个开源框架，用于构建...</p>
            </details>
        </div>
    </div>
</div>
    """)

    print("\n3. Markdown展示:")
    print("""
## 答案

LangChain是一个用于构建LLM应用的开源框架。

---

### 📚 参考来源

#### [1] langchain_intro.pdf, p.1 ⭐⭐⭐

> LangChain是一个开源框架，用于构建基于大型语言模型的应用...

#### [2] langchain_guide.md, section 2 ⭐⭐

> LangChain提供了丰富的组件和工具...

#### [3] official_docs.html ⭐⭐

> Harrison Chase于2022年创建了LangChain...
    """)

    print("\n4. 交互式展示:")
    print("""
答案: LangChain是一个用于构建LLM应用的开源框架。

参考来源: [展开/折叠]

  ▼ [1] langchain_intro.pdf, p.1 ⭐⭐⭐
      LangChain是一个开源框架...
      [📄 查看原文] [🔗 打开文件]

  ▶ [2] langchain_guide.md ⭐⭐
      [点击展开]

  ▶ [3] official_docs.html ⭐⭐
      [点击展开]
    """)

    print("\n实现建议:")
    print("  • CLI: 使用表格和分隔线")
    print("  • Web: 可折叠的引用卡片")
    print("  • 移动端: 精简展示，点击查看详情")
    print("  • API: JSON格式，客户端自定义展示\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 07: 来源引用")
    print("="*70)

    try:
        # 示例1: 基础溯源
        demo_basic_citation()

        # 示例2: 引用格式化
        demo_citation_formatting()

        # 示例3: 置信度评分
        demo_confidence_scoring()

        # 示例4: 排序和过滤
        demo_citation_filtering()

        # 示例5: 多文档引用
        demo_multi_doc_citation()

        # 示例6: 展示优化
        demo_citation_display()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • 始终返回源文档")
        print("    • 使用合适的引用格式")
        print("    • 提供置信度评分")
        print("    • 优化引用展示")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
