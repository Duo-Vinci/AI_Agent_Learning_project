"""
LangChain RAG应用 - 02: 文本分割

本模块演示：
1. CharacterTextSplitter - 按字符数分块
2. RecursiveCharacterTextSplitter - 递归分块（推荐）
3. TokenTextSplitter - 按Token分块
4. SemanticChunker - 语义分块
5. 自定义分块策略
6. chunk_size和chunk_overlap参数详解
7. 不同分块策略对比
8. 分块质量评估

文本分割是RAG系统的关键步骤，影响检索质量和模型性能。
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)
from langchain.schema import Document


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_chunks(chunks: List[Document], max_display: int = 3):
    """打印文本块信息"""
    print(f"总共生成 {len(chunks)} 个文本块\n")

    for i, chunk in enumerate(chunks[:max_display], 1):
        print(f"块 {i}:")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  内容: {chunk.page_content[:100]}...")
        if chunk.metadata:
            print(f"  元数据: {chunk.metadata}")
        print()

    if len(chunks) > max_display:
        print(f"... 还有 {len(chunks) - max_display} 个块未显示\n")


# 准备长文本示例
LONG_TEXT = """
LangChain是一个强大的框架，专门用于开发由大型语言模型驱动的应用程序。它提供了一套完整的工具链，帮助开发者快速构建智能应用。

RAG（检索增强生成）是LangChain的核心应用场景之一。RAG技术通过结合信息检索和文本生成，能够让语言模型基于外部知识库生成更准确、更可靠的回答。

文本分割是RAG系统中的关键步骤。合理的文本分割策略可以：
1. 提高检索准确性 - 小块文本更容易精确匹配查询
2. 优化模型性能 - 避免超出模型上下文长度限制
3. 改善用户体验 - 返回更相关、更聚焦的信息

在选择分割策略时，需要考虑多个因素：
- 文档类型（技术文档、新闻文章、对话记录等）
- 内容结构（是否有明确的段落、章节划分）
- 目标应用（问答、摘要、分类等）
- 性能要求（响应速度、准确率等）

CharacterTextSplitter是最基础的分割器，按照固定字符数进行分割。它简单直接，但可能会在句子中间切断，影响语义完整性。

RecursiveCharacterTextSplitter是更智能的选择。它会按照段落、句子、单词的优先级递归分割，尽量保持语义完整。这是最常用和推荐的分割器。

TokenTextSplitter按照token数量分割，这对于需要精确控制模型输入长度的场景特别有用。不同的模型有不同的tokenizer，需要匹配使用。

SemanticChunker是基于语义的分割器，它会分析文本的语义相似度，在语义边界处进行分割。这种方法能产生更有意义的文本块，但计算成本较高。

chunk_size参数控制每个块的大小。较小的chunk_size会产生更多、更精确的块，但可能丢失上下文；较大的chunk_size保留更多上下文，但可能包含无关信息。

chunk_overlap参数定义相邻块之间的重叠部分。适当的重叠可以避免重要信息被切断，但也会增加存储和计算成本。通常建议重叠10-20%的chunk_size。

在实际应用中，需要根据具体场景调整这些参数。可以通过A/B测试、用户反馈等方式不断优化分割策略，找到最佳平衡点。
""".strip()


# ==================== 示例1: CharacterTextSplitter基础用法 ====================

def demo_character_splitter_basic():
    """示例1: CharacterTextSplitter - 按字符数分块"""
    print_section("示例1: CharacterTextSplitter - 按字符数分块")

    print("CharacterTextSplitter特点:")
    print("  ✓ 按固定字符数分割")
    print("  ✓ 简单直接，速度快")
    print("  ✗ 可能在句子中间切断")
    print("  ✗ 不考虑语义完整性\n")

    # 创建分割器
    splitter = CharacterTextSplitter(
        separator="\n\n",  # 分隔符
        chunk_size=200,     # 每块200字符
        chunk_overlap=20,   # 重叠20字符
        length_function=len,  # 长度计算函数
    )

    print(f"配置参数:")
    print(f"  separator: '\\n\\n' (按段落分割)")
    print(f"  chunk_size: 200 字符")
    print(f"  chunk_overlap: 20 字符\n")

    # 分割文本
    chunks = splitter.create_documents([LONG_TEXT])

    print_chunks(chunks, max_display=4)

    # 验证重叠
    if len(chunks) >= 2:
        print("验证重叠:")
        overlap = chunks[0].page_content[-20:]
        next_start = chunks[1].page_content[:20]
        print(f"  第1块结尾: ...{overlap}")
        print(f"  第2块开头: {next_start}...")
        has_overlap = any(word in next_start for word in overlap.split())
        print(f"  存在重叠: {'是' if has_overlap else '否'}\n")


# ==================== 示例2: RecursiveCharacterTextSplitter ====================

def demo_recursive_splitter():
    """示例2: RecursiveCharacterTextSplitter - 递归分块（推荐）"""
    print_section("示例2: RecursiveCharacterTextSplitter - 递归分块")

    print("RecursiveCharacterTextSplitter特点:")
    print("  ✓ 按照优先级递归分割（段落→句子→单词）")
    print("  ✓ 保持语义完整性")
    print("  ✓ 最常用和推荐的分割器")
    print("  ✓ 适用于大多数场景\n")

    # 创建分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,      # 每块300字符
        chunk_overlap=50,    # 重叠50字符
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],  # 分隔符优先级
    )

    print(f"配置参数:")
    print(f"  chunk_size: 300 字符")
    print(f"  chunk_overlap: 50 字符")
    print(f"  separators优先级: 段落 > 句子 > 标点 > 空格\n")

    # 分割文本
    chunks = splitter.create_documents([LONG_TEXT])

    print_chunks(chunks, max_display=4)

    # 分析分块质量
    print("分块质量分析:")
    avg_length = sum(len(c.page_content) for c in chunks) / len(chunks)
    min_length = min(len(c.page_content) for c in chunks)
    max_length = max(len(c.page_content) for c in chunks)

    print(f"  平均长度: {avg_length:.0f} 字符")
    print(f"  最小长度: {min_length} 字符")
    print(f"  最大长度: {max_length} 字符")
    print(f"  长度标准差: {(max_length - min_length):.0f} 字符\n")


# ==================== 示例3: 不同chunk_size对比 ====================

def demo_chunk_size_comparison():
    """示例3: 不同chunk_size参数对比"""
    print_section("示例3: 不同chunk_size参数对比")

    # 测试不同的chunk_size
    sizes = [100, 300, 500]

    results = {}

    for size in sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=size // 10,  # 10%重叠
            length_function=len,
        )
        chunks = splitter.create_documents([LONG_TEXT])
        results[size] = chunks

        print(f"chunk_size={size}:")
        print(f"  生成块数: {len(chunks)}")
        print(f"  平均长度: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} 字符")
        print(f"  第1块预览: {chunks[0].page_content[:60]}...\n")

    print("选择建议:")
    print("  • chunk_size=100-200: 适合精确检索，但上下文较少")
    print("  • chunk_size=300-500: 平衡检索和上下文，推荐")
    print("  • chunk_size=800-1000: 保留更多上下文，适合摘要")
    print("  • 具体值需要根据实际场景调整\n")


# ==================== 示例4: chunk_overlap参数详解 ====================

def demo_chunk_overlap():
    """示例4: chunk_overlap参数详解"""
    print_section("示例4: chunk_overlap参数详解")

    print("chunk_overlap作用:")
    print("  ✓ 避免关键信息在边界被切断")
    print("  ✓ 提供上下文连续性")
    print("  ✗ 增加存储空间")
    print("  ✗ 可能导致重复检索\n")

    # 测试不同的overlap
    overlaps = [0, 30, 60]

    for overlap in overlaps:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=overlap,
            length_function=len,
        )
        chunks = splitter.create_documents([LONG_TEXT])

        print(f"chunk_overlap={overlap}:")
        print(f"  生成块数: {len(chunks)}")

        # 计算实际重叠率
        if len(chunks) >= 2 and overlap > 0:
            # 简单检查：看第二块开头是否在第一块中出现
            overlap_text = chunks[1].page_content[:30]
            has_overlap = overlap_text in chunks[0].page_content
            print(f"  存在重叠: {'是' if has_overlap else '否'}")

        print(f"  总字符数: {sum(len(c.page_content) for c in chunks)}")
        print()

    print("推荐设置:")
    print("  • overlap = chunk_size * 0.1-0.2 (10-20%)")
    print("  • 技术文档: 较小overlap (避免冗余)")
    print("  • 故事叙述: 较大overlap (保持连贯性)\n")


# ==================== 示例5: TokenTextSplitter ====================

def demo_token_splitter():
    """示例5: TokenTextSplitter - 按Token分块"""
    print_section("示例5: TokenTextSplitter - 按Token分块")

    print("TokenTextSplitter特点:")
    print("  ✓ 按token数量分割")
    print("  ✓ 精确控制模型输入长度")
    print("  ✓ 适配不同模型的tokenizer")
    print("  ⚠ 需要安装tiktoken库\n")

    try:
        # 尝试导入tiktoken
        import tiktoken

        # 创建分割器
        splitter = TokenTextSplitter(
            chunk_size=100,      # 100个token
            chunk_overlap=10,    # 重叠10个token
        )

        print("配置参数:")
        print("  chunk_size: 100 tokens")
        print("  chunk_overlap: 10 tokens")
        print("  编码: cl100k_base (GPT-3.5/4默认)\n")

        # 分割文本
        chunks = splitter.create_documents([LONG_TEXT])

        print_chunks(chunks, max_display=3)

        # Token统计
        encoding = tiktoken.get_encoding("cl100k_base")
        print("Token统计:")
        for i, chunk in enumerate(chunks[:3], 1):
            token_count = len(encoding.encode(chunk.page_content))
            print(f"  块{i}: {token_count} tokens")
        print()

    except ImportError:
        print("⚠ 未安装tiktoken库")
        print("安装命令: pip install tiktoken\n")
        print("模拟示例:")
        print("  假设平均每个token约4个字符")

        # 使用字符近似模拟
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,  # 约100 tokens
            chunk_overlap=40,
        )
        chunks = splitter.create_documents([LONG_TEXT])
        print_chunks(chunks, max_display=3)


# ==================== 示例6: 带元数据的分割 ====================

def demo_splitting_with_metadata():
    """示例6: 带元数据的文本分割"""
    print_section("示例6: 带元数据的文本分割")

    # 创建带元数据的文档
    documents = [
        Document(
            page_content=LONG_TEXT,
            metadata={
                "source": "langchain_guide.txt",
                "author": "LangChain Team",
                "chapter": "RAG Basics",
                "page": 1
            }
        )
    ]

    print("原始文档元数据:")
    print(f"  {documents[0].metadata}\n")

    # 分割时保留元数据
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    print(f"分割后生成 {len(chunks)} 个块\n")

    print("分割后的元数据（前3块）:")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n块{i}:")
        print(f"  元数据: {chunk.metadata}")
        print(f"  内容长度: {len(chunk.page_content)} 字符")
        print(f"  内容预览: {chunk.page_content[:80]}...")

    print("\n✓ 元数据在所有块中保持一致，便于溯源\n")


# ==================== 示例7: 自定义分割策略 ====================

class CustomTextSplitter:
    """自定义文本分割器 - 按句子分割"""

    def __init__(self, sentences_per_chunk: int = 3, overlap_sentences: int = 1):
        """
        初始化自定义分割器

        参数:
            sentences_per_chunk: 每块包含的句子数
            overlap_sentences: 重叠的句子数
        """
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences

    def split_text(self, text: str) -> List[str]:
        """分割文本"""
        # 按句子分割（简单方法）
        import re
        sentences = re.split(r'[。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        i = 0
        while i < len(sentences):
            # 取指定数量的句子
            chunk_sentences = sentences[i:i + self.sentences_per_chunk]
            chunk = '。'.join(chunk_sentences) + '。'
            chunks.append(chunk)

            # 移动索引（考虑重叠）
            i += self.sentences_per_chunk - self.overlap_sentences

        return chunks

    def create_documents(self, texts: List[str]) -> List[Document]:
        """创建文档列表"""
        documents = []
        for text in texts:
            chunks = self.split_text(text)
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={"chunk_id": i, "total_chunks": len(chunks)}
                )
                documents.append(doc)
        return documents


def demo_custom_splitter():
    """示例7: 自定义分割策略"""
    print_section("示例7: 自定义分割策略 - 按句子分割")

    print("自定义分割器特点:")
    print("  ✓ 完全控制分割逻辑")
    print("  ✓ 适配特殊需求")
    print("  ✓ 本例按句子分割，保持句子完整性\n")

    # 创建自定义分割器
    splitter = CustomTextSplitter(
        sentences_per_chunk=3,   # 每块3个句子
        overlap_sentences=1       # 重叠1个句子
    )

    print("配置参数:")
    print("  每块句子数: 3")
    print("  重叠句子数: 1\n")

    # 分割文本
    chunks = splitter.create_documents([LONG_TEXT])

    print_chunks(chunks, max_display=4)

    print("自定义分割器的优势:")
    print("  • 可以实现特定领域的分割逻辑")
    print("  • 可以基于语义、结构等高级特征")
    print("  • 完全控制分割边界\n")


# ==================== 示例8: 分割策略对比 ====================

def demo_splitter_comparison():
    """示例8: 不同分割策略对比"""
    print_section("示例8: 不同分割策略对比")

    # 准备测试文本
    test_text = """
第一段：这是一个测试文本。我们将使用不同的分割器来处理它。

第二段：CharacterTextSplitter会按字符数分割。它速度快但可能切断句子。

第三段：RecursiveCharacterTextSplitter会智能分割。它尽量保持语义完整性。

第四段：选择合适的分割器很重要。需要根据实际场景调整参数。
    """.strip()

    # 定义不同的分割器
    splitters = {
        "Character": CharacterTextSplitter(
            separator="\n",
            chunk_size=80,
            chunk_overlap=10,
        ),
        "Recursive": RecursiveCharacterTextSplitter(
            chunk_size=80,
            chunk_overlap=10,
            separators=["\n\n", "\n", "。", " ", ""],
        ),
    }

    # 对比结果
    results = {}
    for name, splitter in splitters.items():
        chunks = splitter.create_documents([test_text])
        results[name] = chunks

        print(f"{name}Splitter:")
        print(f"  块数: {len(chunks)}")
        print(f"  平均长度: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f}")

        # 显示前2块
        for i, chunk in enumerate(chunks[:2], 1):
            print(f"  块{i}: {chunk.page_content}")

        print()

    print("选择建议:")
    print("  • 通用场景: RecursiveCharacterTextSplitter")
    print("  • 结构化文档: CharacterTextSplitter + 合适分隔符")
    print("  • Token限制: TokenTextSplitter")
    print("  • 特殊需求: 自定义分割器\n")


# ==================== 示例9: 分块质量评估 ====================

def demo_chunk_quality_evaluation():
    """示例9: 分块质量评估"""
    print_section("示例9: 分块质量评估")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
    )

    chunks = splitter.create_documents([LONG_TEXT])

    print(f"评估 {len(chunks)} 个文本块的质量\n")

    # 1. 长度分布
    lengths = [len(c.page_content) for c in chunks]
    avg_length = sum(lengths) / len(lengths)

    print("1. 长度分布:")
    print(f"   平均: {avg_length:.0f} 字符")
    print(f"   最小: {min(lengths)} 字符")
    print(f"   最大: {max(lengths)} 字符")
    print(f"   标准差: {(sum((l - avg_length)**2 for l in lengths) / len(lengths))**0.5:.0f}")

    # 2. 完整性检查（是否在句子边界分割）
    print("\n2. 完整性检查:")
    complete_sentences = sum(
        1 for c in chunks
        if c.page_content.strip()[-1] in '。！？'
    )
    print(f"   完整句子结尾: {complete_sentences}/{len(chunks)} ({complete_sentences/len(chunks)*100:.1f}%)")

    # 3. 重叠验证
    print("\n3. 重叠验证:")
    if len(chunks) >= 2:
        overlaps = []
        for i in range(len(chunks) - 1):
            # 简单检查：后一块的开头是否在前一块中
            next_start = chunks[i+1].page_content[:30]
            has_overlap = next_start in chunks[i].page_content
            overlaps.append(has_overlap)

        overlap_rate = sum(overlaps) / len(overlaps)
        print(f"   相邻块重叠: {sum(overlaps)}/{len(overlaps)} ({overlap_rate*100:.1f}%)")

    # 4. 内容覆盖
    print("\n4. 内容覆盖:")
    total_chunk_chars = sum(lengths)
    original_chars = len(LONG_TEXT)
    print(f"   原文: {original_chars} 字符")
    print(f"   分块总和: {total_chunk_chars} 字符")
    print(f"   覆盖率: {total_chunk_chars/original_chars*100:.1f}%")
    print(f"   (>100%说明存在重叠)\n")

    print("质量评估指标:")
    print("  ✓ 长度均匀分布")
    print("  ✓ 在句子边界分割")
    print("  ✓ 适当的重叠")
    print("  ✓ 完整覆盖原文\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 02: 文本分割")
    print("="*70)

    try:
        # 示例1: CharacterTextSplitter基础
        demo_character_splitter_basic()

        # 示例2: RecursiveCharacterTextSplitter
        demo_recursive_splitter()

        # 示例3: chunk_size对比
        demo_chunk_size_comparison()

        # 示例4: chunk_overlap详解
        demo_chunk_overlap()

        # 示例5: TokenTextSplitter
        demo_token_splitter()

        # 示例6: 带元数据的分割
        demo_splitting_with_metadata()

        # 示例7: 自定义分割策略
        demo_custom_splitter()

        # 示例8: 分割策略对比
        demo_splitter_comparison()

        # 示例9: 分块质量评估
        demo_chunk_quality_evaluation()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • RecursiveCharacterTextSplitter是最常用选择")
        print("    • chunk_size通常设置为300-500字符")
        print("    • chunk_overlap建议为chunk_size的10-20%")
        print("    • 根据实际场景调整参数并评估效果")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
