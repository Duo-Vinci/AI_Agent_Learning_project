"""
固定大小分块策略
按固定字符数或token数分割文本
"""

import os
from typing import List
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter
)
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FixedSizeChunker:
    """固定大小分块器"""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        初始化分块器

        Args:
            chunk_size: 块大小（字符数）
            chunk_overlap: 重叠大小
            separators: 分隔符优先级列表
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", ".", " ", ""]

    def split_by_character(self, documents: List[Document]) -> List[Document]:
        """
        按字符分割（简单分割）

        Args:
            documents: 原始文档列表

        Returns:
            分块后的文档列表
        """
        try:
            logger.info("使用字符分割器...")
            splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
            )

            chunks = splitter.split_documents(documents)
            logger.info(f"分割完成: {len(documents)} 个文档 -> {len(chunks)} 个块")
            return chunks

        except Exception as e:
            logger.error(f"字符分割失败: {str(e)}")
            raise

    def split_by_recursive(self, documents: List[Document]) -> List[Document]:
        """
        递归字符分割（推荐）
        按优先级尝试不同的分隔符

        Args:
            documents: 原始文档列表

        Returns:
            分块后的文档列表
        """
        try:
            logger.info("使用递归字符分割器...")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=self.separators
            )

            chunks = splitter.split_documents(documents)
            logger.info(f"分割完成: {len(documents)} 个文档 -> {len(chunks)} 个块")

            return chunks

        except Exception as e:
            logger.error(f"递归分割失败: {str(e)}")
            raise

    def split_by_token(self, documents: List[Document], encoding_name: str = "cl100k_base") -> List[Document]:
        """
        按Token分割（适用于LLM输入）

        Args:
            documents: 原始文档列表
            encoding_name: Token编码器名称（OpenAI模型使用cl100k_base）

        Returns:
            分块后的文档列表
        """
        try:
            logger.info("使用Token分割器...")
            splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                encoding_name=encoding_name
            )

            chunks = splitter.split_documents(documents)
            logger.info(f"分割完成: {len(documents)} 个文档 -> {len(chunks)} 个块")

            return chunks

        except Exception as e:
            logger.error(f"Token分割失败: {str(e)}")
            raise

    def analyze_chunks(self, chunks: List[Document]) -> dict:
        """
        分析分块结果的统计信息

        Args:
            chunks: 分块列表

        Returns:
            统计信息字典
        """
        if not chunks:
            return {"error": "空分块列表"}

        chunk_lengths = [len(chunk.page_content) for chunk in chunks]

        stats = {
            "总块数": len(chunks),
            "平均长度": sum(chunk_lengths) / len(chunks),
            "最小长度": min(chunk_lengths),
            "最大长度": max(chunk_lengths),
            "总字符数": sum(chunk_lengths)
        }

        return stats


def demo():
    """演示固定大小分块"""
    from pathlib import Path

    print("=== 固定大小分块策略演示 ===\n")

    # 创建示例文档
    sample_text = """
人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。

深度学习是机器学习的一个子领域，它使用神经网络来模拟人脑的学习过程。深度学习在图像识别、自然语言处理和语音识别等领域取得了突破性进展。

自然语言处理（Natural Language Processing，NLP）是人工智能的一个重要分支，专注于让计算机理解、解释和生成人类语言。NLP的应用包括机器翻译、情感分析、文本摘要和聊天机器人等。

大语言模型（Large Language Models，LLMs）是近年来NLP领域的重大突破。这些模型通过在海量文本数据上进行训练，能够生成连贯、有意义的文本，并执行各种语言理解任务。

检索增强生成（Retrieval-Augmented Generation，RAG）是一种结合信息检索和文本生成的技术。RAG系统首先从知识库中检索相关文档，然后基于这些文档生成答案，从而提高答案的准确性和可靠性。
    """.strip()

    documents = [Document(page_content=sample_text, metadata={"source": "demo"})]

    # 示例1: 字符分割
    print("=== 示例1: 字符分割（简单） ===")
    chunker = FixedSizeChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split_by_character(documents)

    print(f"原始文档: 1 个")
    print(f"分块结果: {len(chunks)} 个块\n")

    for i, chunk in enumerate(chunks[:3]):  # 只显示前3个
        print(f"块 {i+1}:")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  内容: {chunk.page_content[:100]}...\n")

    stats = chunker.analyze_chunks(chunks)
    print("统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

    # 示例2: 递归分割（推荐）
    print("\n\n=== 示例2: 递归字符分割（推荐） ===")
    chunker = FixedSizeChunker(
        chunk_size=200,
        chunk_overlap=20,
        separators=["\n\n", "\n", "。", ".", " ", ""]
    )
    chunks = chunker.split_by_recursive(documents)

    print(f"分块结果: {len(chunks)} 个块\n")

    for i, chunk in enumerate(chunks[:3]):
        print(f"块 {i+1}:")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  内容: {chunk.page_content[:100]}...\n")

    stats = chunker.analyze_chunks(chunks)
    print("统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

    # 示例3: Token分割
    print("\n\n=== 示例3: Token分割（适用于LLM） ===")
    try:
        chunker = FixedSizeChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.split_by_token(documents)

        print(f"分块结果: {len(chunks)} 个块\n")

        for i, chunk in enumerate(chunks[:3]):
            print(f"块 {i+1}:")
            print(f"  长度: {len(chunk.page_content)} 字符")
            print(f"  内容: {chunk.page_content[:100]}...\n")

        stats = chunker.analyze_chunks(chunks)
        print("统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

    except Exception as e:
        print(f"Token分割需要安装tiktoken: pip install tiktoken")
        print(f"错误: {e}")

    # 示例4: 不同参数对比
    print("\n\n=== 示例4: 不同参数对比 ===")
    configs = [
        {"chunk_size": 150, "chunk_overlap": 0, "name": "小块无重叠"},
        {"chunk_size": 300, "chunk_overlap": 30, "name": "中块小重叠"},
        {"chunk_size": 500, "chunk_overlap": 100, "name": "大块大重叠"},
    ]

    for config in configs:
        chunker = FixedSizeChunker(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"]
        )
        chunks = chunker.split_by_recursive(documents)
        stats = chunker.analyze_chunks(chunks)

        print(f"\n{config['name']} (size={config['chunk_size']}, overlap={config['chunk_overlap']}):")
        print(f"  总块数: {stats['总块数']}")
        print(f"  平均长度: {stats['平均长度']:.0f}")


if __name__ == "__main__":
    demo()
