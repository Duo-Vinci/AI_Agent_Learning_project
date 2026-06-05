"""
LangChain RAG - 快速入门

本脚本演示如何快速开始使用LangChain构建RAG系统：
1. 文档加载
2. 文本分块
3. 向量存储
4. 检索问答

运行方式：
    python quickstart.py
"""

import os
from typing import List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.documents import Document


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 最简单的RAG（10行代码） ====================

def example_1_simple_rag():
    """示例1: 最简单的RAG系统"""
    print_section("示例1: 最简单的RAG系统（10行代码）")

    try:
        load_dotenv()

        # 1. 准备文档
        documents = [
            Document(page_content="LangChain是一个用于开发由语言模型驱动的应用程序的框架。"),
            Document(page_content="RAG代表检索增强生成，它结合了检索和生成两种技术。"),
            Document(page_content="向量数据库用于存储和检索文档的向量表示。")
        ]

        # 2. 创建向量存储
        embeddings = OpenAIEmbeddings(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE")
        )
        vectorstore = FAISS.from_documents(documents, embeddings)

        # 3. 创建检索器
        retriever = vectorstore.as_retriever()

        # 4. 创建LLM
        llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0
        )

        # 5. 创建问答链
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        # 6. 提问
        questions = [
            "什么是LangChain？",
            "RAG是什么？",
            "向量数据库有什么用？"
        ]

        for question in questions:
            print(f"问题: {question}")
            result = qa_chain.invoke({"query": question})
            print(f"回答: {result['result']}\n")

    except Exception as e:
        print(f"错误: {str(e)}")
        print("提示: 请确保已配置API密钥和安装必要依赖")


# ==================== 示例2: 文档分块 ====================

def example_2_text_splitting():
    """示例2: 文档分块"""
    print_section("示例2: 文档分块")

    # 长文本
    long_text = """
    人工智能（Artificial Intelligence，AI）是计算机科学的一个分支。
    它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。

    机器学习是人工智能的一个子领域。机器学习算法使计算机能够从数据中学习。
    深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的表示。

    自然语言处理（NLP）是人工智能的另一个重要分支，它使计算机能够理解和生成人类语言。
    """

    # 创建分块器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=["\n\n", "\n", "。", "，", " ", ""]
    )

    # 分块
    chunks = splitter.split_text(long_text)

    print(f"原文长度: {len(long_text)} 字符")
    print(f"分块数量: {len(chunks)}\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"块 {i}: {chunk.strip()[:80]}...")


# ==================== 示例3: 向量检索 ====================

def example_3_vector_search():
    """示例3: 向量相似度搜索"""
    print_section("示例3: 向量相似度搜索")

    try:
        load_dotenv()

        # 知识库文档
        documents = [
            Document(
                page_content="Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。",
                metadata={"source": "python_intro", "category": "编程"}
            ),
            Document(
                page_content="Java是一种面向对象的编程语言，广泛用于企业级应用开发。",
                metadata={"source": "java_intro", "category": "编程"}
            ),
            Document(
                page_content="机器学习是人工智能的一个分支，使计算机能够从数据中学习。",
                metadata={"source": "ml_intro", "category": "AI"}
            ),
            Document(
                page_content="深度学习使用神经网络来处理复杂的模式识别任务。",
                metadata={"source": "dl_intro", "category": "AI"}
            ),
        ]

        # 创建向量存储
        embeddings = OpenAIEmbeddings(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE")
        )
        vectorstore = FAISS.from_documents(documents, embeddings)

        # 相似度搜索
        queries = [
            "编程语言",
            "人工智能和机器学习"
        ]

        for query in queries:
            print(f"查询: {query}")
            results = vectorstore.similarity_search(query, k=2)

            for i, doc in enumerate(results, 1):
                print(f"  {i}. {doc.page_content[:50]}...")
                print(f"     类别: {doc.metadata['category']}")
            print()

    except Exception as e:
        print(f"错误: {str(e)}")


# ==================== 示例4: 完整的RAG问答系统 ====================

def example_4_complete_rag():
    """示例4: 完整的RAG问答系统"""
    print_section("示例4: 完整的RAG问答系统")

    try:
        load_dotenv()

        # 1. 准备知识库
        knowledge_base = """
        # Python编程语言

        Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。
        Python由Guido van Rossum于1989年底发明，第一个公开发行版发行于1991年。

        Python的设计哲学强调代码的可读性和简洁的语法。
        Python拥有丰富的标准库，被称为"内置电池"（batteries included）。

        Python的应用领域包括：
        - Web开发（Django、Flask）
        - 数据科学和机器学习（NumPy、Pandas、Scikit-learn）
        - 自动化脚本
        - 游戏开发
        - 桌面应用

        # LangChain框架

        LangChain是一个用于开发由语言模型驱动的应用程序的框架。
        它提供了一系列工具和抽象，使开发者能够轻松构建复杂的AI应用。

        LangChain的核心组件包括：
        - Models：与各种LLM进行交互
        - Prompts：管理和优化提示词
        - Chains：将多个组件链接在一起
        - Agents：让LLM自主决策和使用工具
        - Memory：在交互之间保持状态
        """

        # 2. 文本分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50
        )
        texts = splitter.split_text(knowledge_base)
        documents = [Document(page_content=text) for text in texts]

        print(f"知识库已分为 {len(documents)} 个块\n")

        # 3. 创建向量存储
        embeddings = OpenAIEmbeddings(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE")
        )
        vectorstore = FAISS.from_documents(documents, embeddings)

        # 4. 创建问答链
        llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
            return_source_documents=True
        )

        # 5. 问答测试
        questions = [
            "Python是什么时候发明的？",
            "Python的应用领域有哪些？",
            "LangChain的核心组件有哪些？"
        ]

        for question in questions:
            print(f"问题: {question}")
            result = qa_chain.invoke({"query": question})
            print(f"回答: {result['result']}")
            print(f"引用来源: {len(result['source_documents'])} 个文档片段\n")

    except Exception as e:
        print(f"错误: {str(e)}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG - 快速入门")
    print("="*70)
    print("\n本脚本展示RAG系统的快速入门示例\n")

    try:
        # 示例1: 简单RAG
        example_1_simple_rag()

        # 示例2: 文本分块
        example_2_text_splitting()

        # 示例3: 向量搜索
        example_3_vector_search()

        # 示例4: 完整RAG
        example_4_complete_rag()

        print("\n" + "="*70)
        print("  快速入门完成！")
        print("="*70)
        print("\n下一步:")
        print("  - 学习更多文档加载器")
        print("  - 探索不同的向量数据库")
        print("  - 优化检索策略")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
