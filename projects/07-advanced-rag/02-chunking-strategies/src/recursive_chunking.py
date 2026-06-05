"""
递归分块策略
根据文档结构（标题、段落）进行智能递归分块
"""

from typing import List, Optional
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    Language,
    RecursiveCharacterTextSplitter
)
from langchain.schema import Document
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecursiveChunker:
    """递归分块器 - 根据文档结构递归分割"""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        """
        初始化递归分块器

        Args:
            chunk_size: 块大小
            chunk_overlap: 重叠大小
            separators: 分隔符优先级列表
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 默认分隔符（从大到小）
        if separators is None:
            self.separators = [
                "\n\n\n",  # 多个空行
                "\n\n",    # 段落
                "\n",      # 行
                "。",      # 中文句号
                "！",      # 中文感叹号
                "？",      # 中文问号
                ".",       # 英文句号
                "!",       # 英文感叹号
                "?",       # 英文问号
                "；",      # 中文分号
                ";",       # 英文分号
                "，",      # 中文逗号
                ",",       # 英文逗号
                " ",       # 空格
                ""         # 字符
            ]
        else:
            self.separators = separators

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        递归分割文档

        Args:
            documents: 原始文档列表

        Returns:
            分块后的文档列表
        """
        try:
            logger.info("开始递归分块...")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=self.separators
            )

            chunks = splitter.split_documents(documents)
            logger.info(f"递归分块完成: {len(documents)} 个文档 -> {len(chunks)} 个块")

            return chunks

        except Exception as e:
            logger.error(f"递归分块失败: {str(e)}")
            raise

    def split_text(self, text: str) -> List[str]:
        """
        递归分割单个文本

        Args:
            text: 输入文本

        Returns:
            分块列表
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=self.separators
        )

        return splitter.split_text(text)


class MarkdownStructureChunker:
    """Markdown结构化分块器 - 基于Markdown标题层级分块"""

    def __init__(
        self,
        headers_to_split_on: Optional[List[tuple]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        初始化Markdown结构化分块器

        Args:
            headers_to_split_on: 要分割的标题层级
            chunk_size: 二次分块的大小
            chunk_overlap: 重叠大小
        """
        if headers_to_split_on is None:
            self.headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
            ]
        else:
            self.headers_to_split_on = headers_to_split_on

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_markdown(self, markdown_text: str) -> List[Document]:
        """
        基于Markdown标题分割文档

        Args:
            markdown_text: Markdown文本

        Returns:
            分块后的文档列表
        """
        try:
            logger.info("开始Markdown结构化分块...")

            # 第一步：按标题分割
            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=self.headers_to_split_on
            )
            md_header_splits = markdown_splitter.split_text(markdown_text)

            # 第二步：如果块太大，再进行递归分割
            final_chunks = []
            if md_header_splits:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )

                for doc in md_header_splits:
                    if len(doc.page_content) > self.chunk_size:
                        # 需要进一步分割
                        sub_chunks = text_splitter.split_documents([doc])
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(doc)

            logger.info(f"Markdown分块完成: {len(final_chunks)} 个块")
            return final_chunks

        except Exception as e:
            logger.error(f"Markdown分块失败: {str(e)}")
            raise


class CodeChunker:
    """代码文档分块器 - 根据代码结构分块"""

    def __init__(
        self,
        language: str = "python",
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ):
        """
        初始化代码分块器

        Args:
            language: 编程语言
            chunk_size: 块大小
            chunk_overlap: 重叠大小
        """
        self.language = language
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 语言映射
        self.language_map = {
            "python": Language.PYTHON,
            "javascript": Language.JS,
            "java": Language.JAVA,
            "cpp": Language.CPP,
            "go": Language.GO,
            "rust": Language.RUST,
            "markdown": Language.MARKDOWN,
        }

    def split_code(self, code_text: str) -> List[str]:
        """
        根据代码结构分割

        Args:
            code_text: 代码文本

        Returns:
            分块列表
        """
        try:
            logger.info(f"开始{self.language}代码分块...")

            language_enum = self.language_map.get(self.language.lower())
            if language_enum is None:
                logger.warning(f"不支持的语言: {self.language}，使用通用分块")
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            else:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=language_enum,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )

            chunks = splitter.split_text(code_text)
            logger.info(f"代码分块完成: {len(chunks)} 个块")

            return chunks

        except Exception as e:
            logger.error(f"代码分块失败: {str(e)}")
            raise


def demo():
    """演示递归分块策略"""
    print("=== 递归分块策略演示 ===\n")

    # 示例1: 通用递归分块
    print("=== 示例1: 通用递归分块 ===")
    sample_text = """
深度学习的基础

深度学习是机器学习的一个子领域，它使用多层神经网络来学习数据的表示。深度学习模型能够自动学习特征，无需人工特征工程。

神经网络结构

神经网络由多个层组成，包括输入层、隐藏层和输出层。每一层包含多个神经元，神经元之间通过权重连接。

前向传播过程中，输入数据通过各层进行变换，最终产生输出。反向传播算法用于计算梯度并更新权重，使模型不断优化。

常见应用

深度学习在多个领域取得了成功。在计算机视觉中，卷积神经网络（CNN）用于图像分类和目标检测。在自然语言处理中，循环神经网络（RNN）和Transformer用于文本生成和翻译。

训练技巧

成功训练深度学习模型需要注意多个方面。首先，需要足够的训练数据。其次，要选择合适的学习率和优化器。此外，还要注意防止过拟合，可以使用正则化、Dropout等技术。
    """.strip()

    documents = [Document(page_content=sample_text, metadata={"source": "demo"})]

    chunker = RecursiveChunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.split_documents(documents)

    print(f"原始文档: 1 个")
    print(f"分块结果: {len(chunks)} 个块\n")

    for i, chunk in enumerate(chunks):
        print(f"块 {i+1}:")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  内容: {chunk.page_content[:150]}...\n")

    # 示例2: Markdown结构化分块
    print("\n=== 示例2: Markdown结构化分块 ===")
    markdown_text = """
# 人工智能概述

人工智能是计算机科学的一个重要分支。

## 机器学习

机器学习让计算机能够从数据中学习。

### 监督学习

监督学习使用标注数据训练模型。常见算法包括线性回归、决策树等。

### 非监督学习

非监督学习从无标注数据中发现模式。典型方法有聚类、降维等。

## 深度学习

深度学习使用多层神经网络。

### 卷积神经网络

CNN主要用于图像处理任务。

### 循环神经网络

RNN适合处理序列数据。

# 自然语言处理

NLP让计算机理解人类语言。

## Transformer架构

Transformer是现代NLP的基础。它使用注意力机制处理序列数据。
    """.strip()

    md_chunker = MarkdownStructureChunker(chunk_size=200, chunk_overlap=20)
    md_chunks = md_chunker.split_markdown(markdown_text)

    print(f"分块结果: {len(md_chunks)} 个块\n")

    for i, chunk in enumerate(md_chunks[:5]):  # 只显示前5个
        print(f"块 {i+1}:")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  元数据: {chunk.metadata}")
        print(f"  内容: {chunk.page_content[:100]}...\n")

    # 示例3: 代码分块
    print("\n=== 示例3: Python代码分块 ===")
    python_code = '''
def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度"""
    # 将文本转换为向量
    vec1 = vectorize(text1)
    vec2 = vectorize(text2)

    # 计算余弦相似度
    similarity = cosine_similarity(vec1, vec2)
    return similarity


class RAGSystem:
    """检索增强生成系统"""

    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm

    def retrieve(self, query: str, k: int = 4):
        """检索相关文档"""
        docs = self.vectorstore.similarity_search(query, k=k)
        return docs

    def generate(self, query: str, context: str):
        """生成答案"""
        prompt = f"根据上下文回答问题\\n\\n上下文: {context}\\n\\n问题: {query}"
        answer = self.llm.generate(prompt)
        return answer
    '''

    code_chunker = CodeChunker(language="python", chunk_size=300, chunk_overlap=50)
    code_chunks = code_chunker.split_code(python_code)

    print(f"分块结果: {len(code_chunks)} 个块\n")

    for i, chunk in enumerate(code_chunks):
        print(f"块 {i+1}:")
        print(f"  长度: {len(chunk)} 字符")
        print(f"  内容:\n{chunk}\n")
        print("-" * 60)


if __name__ == "__main__":
    demo()
