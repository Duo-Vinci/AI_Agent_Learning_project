"""
LangChain RAG应用 - 06: QA链（Question Answering Chain）

本模块演示：
1. RetrievalQA链基础
2. ConversationalRetrievalChain（带记忆）
3. 不同chain_type对比（stuff, map_reduce, refine, map_rerank）
4. 自定义提示词的QA
5. 流式QA输出
6. QA链的参数优化
7. 多文档源QA

QA链将检索器和语言模型结合，实现基于文档的问答功能。
"""

import os
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# 准备知识库文档
KNOWLEDGE_BASE = [
    "LangChain是一个开源框架，用于构建基于大型语言模型的应用程序。它由Harrison Chase于2022年创建。",
    "LangChain的核心组件包括：提示模板、LLM、链、代理、记忆、回调等。",
    "RAG（检索增强生成）是LangChain的重要应用场景，它通过检索相关文档来增强LLM的回答质量。",
    "LangChain支持多种向量数据库，包括FAISS、Chroma、Pinecone、Weaviate等。",
    "LangChain提供了多种文档加载器，可以处理PDF、Word、CSV、JSON、HTML等格式。",
    "Chain是LangChain的核心概念，它将多个组件连接成一个完整的工作流。",
    "Agent是LangChain中的智能体，可以根据输入动态选择使用哪些工具。",
    "LangChain的Memory组件用于维护对话历史，支持多种记忆类型。",
]


def get_test_vectorstore():
    """创建测试用的向量存储"""
    try:
        from langchain_community.vectorstores import FAISS
        from langchain.embeddings.fake import FakeEmbeddings

        embeddings = FakeEmbeddings(size=384)
        documents = [Document(page_content=text) for text in KNOWLEDGE_BASE]
        return FAISS.from_documents(documents, embeddings)
    except:
        return None


def get_test_llm():
    """获取测试用的LLM（模拟）"""
    from langchain.llms.fake import FakeListLLM

    # 预定义一些回答
    responses = [
        "LangChain是一个用于构建LLM应用的开源框架，由Harrison Chase创建。",
        "LangChain的核心组件包括提示模板、链、代理、记忆等。",
        "RAG通过检索相关文档来增强回答质量，是LangChain的重要应用。",
        "LangChain支持FAISS、Chroma、Pinecone等多种向量数据库。",
    ]
    return FakeListLLM(responses=responses)


# ==================== 示例1: RetrievalQA基础 ====================

def demo_retrieval_qa_basic():
    """示例1: RetrievalQA链基础用法"""
    print_section("示例1: RetrievalQA链基础用法")

    print("RetrievalQA特点:")
    print("  ✓ 结合检索和生成")
    print("  ✓ 基于文档回答问题")
    print("  ✓ 可溯源")
    print("  ✗ 无对话记忆\n")

    print("基本配置示例:")
    print("""
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

result = qa_chain({"query": "什么是LangChain？"})
print(result["result"])
print(result["source_documents"])
    """)

    print("\n工作流程:")
    print("  1. 用户提出问题")
    print("  2. 检索器找到相关文档")
    print("  3. 将文档和问题组合成提示")
    print("  4. LLM生成答案")
    print("  5. 返回答案和源文档\n")

    try:
        from langchain.chains import RetrievalQA

        vectorstore = get_test_vectorstore()
        llm = get_test_llm()

        if vectorstore:
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )

            query = "什么是LangChain？"
            print(f"问题: {query}\n")

            result = qa_chain({"query": query})

            print(f"答案: {result['result']}\n")
            print(f"源文档数量: {len(result['source_documents'])}")
            print("\n源文档:")
            for i, doc in enumerate(result['source_documents'], 1):
                print(f"  {i}. {doc.page_content[:60]}...")
            print()

    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例2: chain_type对比 ====================

def demo_chain_types():
    """示例2: 不同chain_type对比"""
    print_section("示例2: 不同chain_type对比")

    chain_types = {
        "stuff": {
            "描述": "将所有文档合并到一个提示中",
            "优点": "简单直接，只需一次LLM调用",
            "缺点": "文档过多时超出上下文限制",
            "适用": "文档少（<4个），文档短"
        },
        "map_reduce": {
            "描述": "分别处理每个文档，然后合并结果",
            "优点": "可处理任意数量文档",
            "缺点": "多次LLM调用，成本高",
            "适用": "文档多，需要独立分析"
        },
        "refine": {
            "描述": "迭代式处理，逐步精炼答案",
            "优点": "答案质量高，考虑所有文档",
            "缺点": "串行处理，速度慢",
            "适用": "需要综合多个文档信息"
        },
        "map_rerank": {
            "描述": "为每个文档生成答案和分数，选择最高分",
            "优点": "可并行处理，找出最佳答案",
            "缺点": "可能忽略其他有用信息",
            "适用": "寻找单一最佳答案"
        }
    }

    print(f"{'类型':<15} {'描述':<30} {'优点':<25} {'缺点':<25} {'适用场景'}")
    print("-" * 120)

    for chain_type, info in chain_types.items():
        print(f"{chain_type:<15} {info['描述']:<30} {info['优点']:<25} {info['缺点']:<25} {info['适用']}")

    print("\n\n详细说明:\n")

    print("1. STUFF (最常用)")
    print("   流程: [Doc1, Doc2, Doc3] -> 合并 -> LLM -> 答案")
    print("   提示模板: '根据以下文档回答问题:\\n{documents}\\n问题:{question}'")
    print("   LLM调用: 1次\n")

    print("2. MAP_REDUCE")
    print("   流程: Doc1 -> LLM -> 答案1")
    print("         Doc2 -> LLM -> 答案2")
    print("         Doc3 -> LLM -> 答案3")
    print("         [答案1, 答案2, 答案3] -> LLM -> 最终答案")
    print("   LLM调用: n+1次（n是文档数）\n")

    print("3. REFINE")
    print("   流程: Doc1 -> LLM -> 初步答案")
    print("         (初步答案 + Doc2) -> LLM -> 精炼答案1")
    print("         (精炼答案1 + Doc3) -> LLM -> 精炼答案2")
    print("   LLM调用: n次\n")

    print("4. MAP_RERANK")
    print("   流程: Doc1 -> LLM -> (答案1, 分数1)")
    print("         Doc2 -> LLM -> (答案2, 分数2)")
    print("         Doc3 -> LLM -> (答案3, 分数3)")
    print("         选择最高分的答案")
    print("   LLM调用: n次\n")

    print("选择建议:")
    print("  • 默认使用 stuff（最简单高效）")
    print("  • 文档超过4-5个时使用 map_reduce")
    print("  • 需要高质量综合答案时使用 refine")
    print("  • 寻找单一最佳答案时使用 map_rerank\n")


# ==================== 示例3: ConversationalRetrievalChain ====================

def demo_conversational_retrieval():
    """示例3: ConversationalRetrievalChain（带记忆）"""
    print_section("示例3: ConversationalRetrievalChain - 对话式检索")

    print("ConversationalRetrievalChain特点:")
    print("  ✓ 支持多轮对话")
    print("  ✓ 维护对话历史")
    print("  ✓ 理解上下文引用")
    print("  ✓ 自然的对话体验\n")

    print("与RetrievalQA的区别:")
    print("  • RetrievalQA: 每个问题独立处理")
    print("  • ConversationalRetrievalChain: 考虑对话历史\n")

    print("配置示例:")
    print("""
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)

# 第一轮对话
result1 = qa_chain({"question": "什么是LangChain？"})

# 第二轮对话（可以引用上文）
result2 = qa_chain({"question": "它有哪些核心组件？"})
    """)

    print("\n对话示例:\n")

    conversation = [
        {
            "turn": 1,
            "user": "什么是LangChain？",
            "assistant": "LangChain是一个开源框架，用于构建基于大型语言模型的应用程序。"
        },
        {
            "turn": 2,
            "user": "它是谁创建的？",
            "assistant": "LangChain由Harrison Chase于2022年创建。",
            "note": "理解'它'指的是LangChain"
        },
        {
            "turn": 3,
            "user": "有哪些核心组件？",
            "assistant": "核心组件包括提示模板、LLM、链、代理、记忆、回调等。",
            "note": "继续上下文，知道问的是LangChain的组件"
        }
    ]

    for turn_data in conversation:
        print(f"轮次{turn_data['turn']}:")
        print(f"  用户: {turn_data['user']}")
        print(f"  助手: {turn_data['assistant']}")
        if 'note' in turn_data:
            print(f"  注: {turn_data['note']}")
        print()

    print("记忆类型选择:")
    print("  • ConversationBufferMemory: 保存所有历史")
    print("  • ConversationBufferWindowMemory: 保存最近k轮")
    print("  • ConversationSummaryMemory: 总结历史")
    print("  • ConversationTokenBufferMemory: 基于token限制\n")


# ==================== 示例4: 自定义提示词 ====================

def demo_custom_prompts():
    """示例4: 自定义提示词的QA"""
    print_section("示例4: 自定义提示词")

    print("为什么需要自定义提示词:")
    print("  ✓ 控制输出格式")
    print("  ✓ 添加特定指令")
    print("  ✓ 优化回答质量")
    print("  ✓ 适配特定领域\n")

    print("默认提示词（简化版）:")
    print("""
使用以下文档回答问题。如果无法从文档中找到答案，请说"我不知道"。

文档:
{context}

问题: {question}
答案:
    """)

    print("\n自定义提示词示例:\n")

    print("1. 专业领域（技术文档）:")
    print("""
你是一个专业的技术文档助手。请基于以下文档准确回答技术问题。

要求:
- 使用准确的技术术语
- 提供代码示例（如果适用）
- 说明版本信息（如果相关）
- 如果文档中没有信息，明确说明

文档:
{context}

问题: {question}
技术回答:
    """)

    print("\n2. 客户服务:")
    print("""
你是一个友好的客户服务助手。请基于我们的知识库为客户提供帮助。

要求:
- 使用友好、礼貌的语气
- 提供清晰的步骤说明
- 如果需要人工协助，引导客户联系支持团队
- 始终从客户角度考虑

知识库:
{context}

客户问题: {question}
回答:
    """)

    print("\n3. 学术研究:")
    print("""
你是一个学术助手。请基于提供的研究文献回答问题。

要求:
- 引用具体的文献来源
- 使用学术语言
- 指出不同观点（如果存在）
- 说明研究的局限性

文献:
{context}

研究问题: {question}
学术回答:
    """)

    print("\n实现代码:")
    print("""
from langchain.prompts import PromptTemplate

template = '''你是一个专业助手。基于以下文档回答问题。

文档:
{context}

问题: {question}

请提供详细、准确的答案:'''

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt}
)
    """)

    print("\n提示词优化建议:")
    print("  1. 明确角色定位")
    print("  2. 清晰的输出要求")
    print("  3. 适当的示例")
    print("  4. 边界条件说明")
    print("  5. 通过测试迭代优化\n")


# ==================== 示例5: 流式输出 ====================

def demo_streaming():
    """示例5: 流式QA输出"""
    print_section("示例5: 流式QA输出")

    print("流式输出的优势:")
    print("  ✓ 降低首字延迟")
    print("  ✓ 改善用户体验")
    print("  ✓ 实时反馈")
    print("  ✓ 适合长答案\n")

    print("配置示例:")
    print("""
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI

# 启用流式输出的LLM
llm = ChatOpenAI(
    temperature=0,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# 查询时会实时输出答案
result = qa_chain({"query": "解释RAG技术"})
    """)

    print("\n自定义流式回调:")
    print("""
from langchain.callbacks.base import BaseCallbackHandler

class CustomStreamHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        # 自定义处理每个新token
        print(token, end="", flush=True)

    def on_llm_end(self, response, **kwargs):
        # LLM完成时的处理
        print("\\n[生成完成]")

handler = CustomStreamHandler()
llm = ChatOpenAI(streaming=True, callbacks=[handler])
    """)

    print("\n流式输出示例效果:")
    print("  用户: 什么是RAG？")
    print("  助手: ", end="")

    # 模拟流式输出
    answer = "RAG（检索增强生成）是一种结合信息检索和文本生成的技术..."
    import time
    for char in answer:
        print(char, end="", flush=True)
        time.sleep(0.02)
    print("\n")

    print("应用场景:")
    print("  • 聊天机器人")
    print("  • 长文本生成")
    print("  • 实时问答系统\n")


# ==================== 示例6: QA链参数优化 ====================

def demo_qa_optimization():
    """示例6: QA链参数优化"""
    print_section("示例6: QA链参数优化")

    print("关键参数:\n")

    print("1. temperature (LLM参数)")
    print("   • 0.0: 确定性输出，适合事实性问答")
    print("   • 0.7: 平衡创造性和准确性")
    print("   • 1.0+: 更有创造性，适合生成任务\n")

    print("2. k (检索数量)")
    print("   • 1-2: 精确但可能信息不足")
    print("   • 3-5: 推荐范围，平衡性能和质量")
    print("   • 10+: 信息丰富但可能引入噪音\n")

    print("3. return_source_documents")
    print("   • True: 返回源文档，便于溯源")
    print("   • False: 只返回答案，更简洁\n")

    print("4. max_tokens_limit (对于stuff类型)")
    print("   • 控制合并文档的总token数")
    print("   • 避免超出模型上下文限制")
    print("   • 推荐: 模型上下文的50-70%\n")

    print("优化配置示例:")
    print("""
# 精确型配置（事实查询）
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    ),
    return_source_documents=True
)

# 创造型配置（需要推理）
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(temperature=0.7, model="gpt-4"),
    chain_type="refine",
    retriever=vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 20}
    ),
    return_source_documents=True
)
    """)

    print("\n性能优化策略:")
    print("  1. 缓存常见查询结果")
    print("  2. 批量处理多个查询")
    print("  3. 异步执行（对于独立查询）")
    print("  4. 使用更快的模型（如gpt-3.5-turbo）")
    print("  5. 限制返回文档数量\n")


# ==================== 示例7: 多文档源QA ====================

def demo_multiple_sources():
    """示例7: 多文档源QA"""
    print_section("示例7: 多文档源QA")

    print("多文档源场景:")
    print("  • 多个知识库")
    print("  • 不同类型的文档")
    print("  • 分布式数据源\n")

    print("方法1: 合并检索器")
    print("""
from langchain.retrievers import MergerRetriever

# 创建多个检索器
retriever1 = vectorstore1.as_retriever(search_kwargs={"k": 3})
retriever2 = vectorstore2.as_retriever(search_kwargs={"k": 3})
retriever3 = vectorstore3.as_retriever(search_kwargs={"k": 3})

# 合并检索器
merger_retriever = MergerRetriever(
    retrievers=[retriever1, retriever2, retriever3]
)

# 使用合并后的检索器
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=merger_retriever
)
    """)

    print("\n方法2: 带元数据的统一存储")
    print("""
# 为不同来源添加元数据
docs_source1 = [
    Document(page_content=text, metadata={"source": "manual"})
    for text in manual_texts
]

docs_source2 = [
    Document(page_content=text, metadata={"source": "faq"})
    for text in faq_texts
]

# 统一存储
all_docs = docs_source1 + docs_source2
vectorstore = FAISS.from_documents(all_docs, embeddings)

# 可以基于元数据过滤
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "manual"}  # 只检索手册
    }
)
    """)

    print("\n方法3: 路由检索器")
    print("""
from langchain.retrievers import RouterRetriever

# 定义路由规则
router_retriever = RouterRetriever(
    retrievers={
        "technical": technical_retriever,
        "business": business_retriever,
        "general": general_retriever
    },
    default_retriever=general_retriever
)

# 根据查询自动选择合适的检索器
    """)

    print("\n应用示例:")
    print("  场景: 企业知识库系统")
    print("    • 产品文档 -> vectorstore1")
    print("    • 常见问题 -> vectorstore2")
    print("    • 技术规范 -> vectorstore3")
    print("    • 政策文件 -> vectorstore4")
    print()
    print("  查询: '产品A的技术规格是什么？'")
    print("  -> 自动从产品文档和技术规范中检索\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 06: QA链")
    print("="*70)

    try:
        # 示例1: RetrievalQA基础
        demo_retrieval_qa_basic()

        # 示例2: chain_type对比
        demo_chain_types()

        # 示例3: 对话式检索
        demo_conversational_retrieval()

        # 示例4: 自定义提示词
        demo_custom_prompts()

        # 示例5: 流式输出
        demo_streaming()

        # 示例6: 参数优化
        demo_qa_optimization()

        # 示例7: 多文档源
        demo_multiple_sources()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • RetrievalQA: 基础QA链")
        print("    • stuff chain_type: 最常用")
        print("    • ConversationalRetrievalChain: 支持对话")
        print("    • 自定义提示词优化输出")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
