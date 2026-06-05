"""
语义分块策略
基于语义相似度进行智能分块，保持语义完整性
"""

from typing import List
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticChunker:
    """语义分块器 - 基于句子之间的语义相似度进行分块"""

    def __init__(
        self,
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5",
        breakpoint_threshold_type: str = "percentile",
        breakpoint_threshold_amount: float = 95
    ):
        """
        初始化语义分块器

        Args:
            embedding_model_name: Embedding模型名称
            breakpoint_threshold_type: 断点阈值类型 ('percentile', 'standard_deviation', 'interquartile')
            breakpoint_threshold_amount: 阈值数量
        """
        self.embedding_model_name = embedding_model_name
        self.breakpoint_threshold_type = breakpoint_threshold_type
        self.breakpoint_threshold_amount = breakpoint_threshold_amount

        # 初始化Embedding模型
        logger.info(f"加载Embedding模型: {embedding_model_name}")
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model_name,
                model_kwargs={'device': 'cpu'},  # 使用CPU，如有GPU可改为'cuda'
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("Embedding模型加载成功")
        except Exception as e:
            logger.warning(f"加载模型失败，使用简化版本: {e}")
            self.embeddings = None

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        基于语义相似度分割文档

        Args:
            documents: 原始文档列表

        Returns:
            分块后的文档列表
        """
        if self.embeddings is None:
            logger.error("Embedding模型未加载，无法进行语义分块")
            raise RuntimeError("Embedding模型未加载")

        try:
            logger.info("开始语义分块...")

            # 创建语义分块器
            semantic_splitter = SemanticChunker(
                embeddings=self.embeddings,
                breakpoint_threshold_type=self.breakpoint_threshold_type,
                breakpoint_threshold_amount=self.breakpoint_threshold_amount
            )

            # 分割文档
            chunks = semantic_splitter.split_documents(documents)
            logger.info(f"语义分块完成: {len(documents)} 个文档 -> {len(chunks)} 个块")

            return chunks

        except Exception as e:
            logger.error(f"语义分块失败: {str(e)}")
            raise

    def analyze_semantic_coherence(self, chunks: List[Document]) -> dict:
        """
        分析分块的语义连贯性

        Args:
            chunks: 分块列表

        Returns:
            连贯性分析结果
        """
        if self.embeddings is None or not chunks:
            return {"error": "无法分析"}

        try:
            # 计算每个块的embedding
            chunk_texts = [chunk.page_content for chunk in chunks]
            embeddings = [self.embeddings.embed_query(text) for text in chunk_texts]

            # 计算相邻块之间的相似度
            similarities = []
            for i in range(len(embeddings) - 1):
                emb1 = np.array(embeddings[i])
                emb2 = np.array(embeddings[i + 1])
                similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                similarities.append(similarity)

            stats = {
                "块数量": len(chunks),
                "平均相邻相似度": np.mean(similarities) if similarities else 0,
                "最小相邻相似度": np.min(similarities) if similarities else 0,
                "最大相邻相似度": np.max(similarities) if similarities else 0,
            }

            return stats

        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            return {"error": str(e)}


class SimplifiedSemanticChunker:
    """简化版语义分块器 - 基于句子边界的启发式分块"""

    def __init__(self, target_chunk_size: int = 500, min_chunk_size: int = 100):
        """
        初始化简化语义分块器

        Args:
            target_chunk_size: 目标块大小
            min_chunk_size: 最小块大小
        """
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        基于句子边界分割文档

        Args:
            documents: 原始文档列表

        Returns:
            分块后的文档列表
        """
        try:
            logger.info("使用简化语义分块...")
            chunks = []

            for doc in documents:
                text = doc.page_content
                # 按句子分割（中英文）
                sentences = self._split_into_sentences(text)

                current_chunk = ""
                for sentence in sentences:
                    # 如果当前块加上新句子不超过目标大小，继续添加
                    if len(current_chunk) + len(sentence) <= self.target_chunk_size:
                        current_chunk += sentence
                    else:
                        # 保存当前块（如果达到最小大小）
                        if len(current_chunk) >= self.min_chunk_size:
                            chunks.append(Document(
                                page_content=current_chunk.strip(),
                                metadata=doc.metadata.copy()
                            ))
                        current_chunk = sentence

                # 添加最后一个块
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata=doc.metadata.copy()
                    ))

            logger.info(f"简化语义分块完成: {len(documents)} 个文档 -> {len(chunks)} 个块")
            return chunks

        except Exception as e:
            logger.error(f"简化语义分块失败: {str(e)}")
            raise

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        import re

        # 句子分隔符（中英文）
        sentence_delimiters = r'([。！？!?.;；])'
        sentences = re.split(sentence_delimiters, text)

        # 重新组合句子和标点
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])

        return [s for s in result if s.strip()]


def demo():
    """演示语义分块"""
    print("=== 语义分块策略演示 ===\n")

    # 创建示例文档
    sample_text = """
人工智能的发展历程可以追溯到20世纪50年代。当时，科学家们开始探索让机器模拟人类智能的可能性。

早期的人工智能研究主要集中在符号推理和专家系统。这些系统通过规则和逻辑来处理问题。但是，它们在处理不确定性和复杂情况时遇到了困难。

随着计算能力的提升和大数据的出现，机器学习成为了人工智能的主流方法。机器学习让计算机能够从数据中学习，而不需要明确的编程指令。

深度学习是机器学习的一个重要分支。它使用多层神经网络来学习数据的层次化表示。深度学习在图像识别、语音识别和自然语言处理等领域取得了巨大成功。

大语言模型代表了深度学习的最新进展。这些模型在海量文本数据上训练，能够理解和生成人类语言。它们展示了令人印象深刻的语言能力和推理能力。

检索增强生成技术结合了信息检索和文本生成。这种方法先从知识库中检索相关信息，然后基于这些信息生成答案。这大大提高了生成内容的准确性和可靠性。
    """.strip()

    documents = [Document(page_content=sample_text, metadata={"source": "demo"})]

    # 示例1: 简化版语义分块
    print("=== 示例1: 简化版语义分块（基于句子边界） ===")
    chunker = SimplifiedSemanticChunker(target_chunk_size=200, min_chunk_size=50)
    chunks = chunker.split_documents(documents)

    print(f"原始文档: 1 个")
    print(f"分块结果: {len(chunks)} 个块\n")

    for i, chunk in enumerate(chunks):
        print(f"块 {i+1}:")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  内容: {chunk.page_content}\n")

    # 示例2: 完整语义分块（需要模型）
    print("\n=== 示例2: 完整语义分块（需要下载模型） ===")
    print("注意: 首次运行会自动下载BGE模型（约400MB），需要等待...")
    print("如果下载失败，将跳过此示例\n")

    try:
        # 使用轻量级模型
        semantic_chunker = SemanticChunker(
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=90
        )

        chunks = semantic_chunker.split_documents(documents)

        print(f"分块结果: {len(chunks)} 个块\n")

        for i, chunk in enumerate(chunks):
            print(f"块 {i+1}:")
            print(f"  长度: {len(chunk.page_content)} 字符")
            print(f"  内容: {chunk.page_content[:150]}...\n")

        # 分析语义连贯性
        print("=== 语义连贯性分析 ===")
        stats = semantic_chunker.analyze_semantic_coherence(chunks)
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"完整语义分块示例跳过: {e}")
        print("提示: 可以先运行简化版，或确保网络连接正常以下载模型")


if __name__ == "__main__":
    demo()
