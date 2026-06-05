"""
综合示例 - 完整的RAG工作流演示
展示从文档加载到问答的完整流程
"""

import sys
from pathlib import Path

# 添加各模块到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "01-document-loaders" / "src"))
sys.path.append(str(project_root / "02-chunking-strategies" / "src"))
sys.path.append(str(project_root / "04-vector-databases" / "src"))
sys.path.append(str(project_root / "05-retrieval-strategies" / "src"))
sys.path.append(str(project_root / "07-hybrid-search" / "src"))

from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_documents():
    """创建示例文档"""
    documents = [
        Document(
            page_content="""
            深度学习是机器学习的一个分支，它使用包含多个处理层的神经网络来学习数据的多层次表示。
            这些网络通过反向传播算法进行训练，可以自动学习特征，无需人工特征工程。
            深度学习在图像识别、语音识别、自然语言处理等领域取得了突破性进展。
            """,
            metadata={"source": "AI教程", "chapter": "深度学习", "page": 1}
        ),
        Document(
            page_content="""
            卷积神经网络（CNN）是一种专门用于处理网格结构数据的深度学习模型，如图像和视频。
            CNN的核心是卷积层，它通过卷积操作提取局部特征。
            典型的CNN架构包括卷积层、池化层和全连接层。
            著名的CNN模型包括LeNet、AlexNet、VGG、ResNet等。
            """,
            metadata={"source": "AI教程", "chapter": "CNN", "page": 2}
        ),
        Document(
            page_content="""
            循环神经网络（RNN）是一类用于处理序列数据的神经网络。
            RNN具有内部记忆，可以捕捉序列中的时间依赖关系。
            然而，传统RNN存在梯度消失和梯度爆炸问题。
            LSTM（长短期记忆网络）和GRU（门控循环单元）是改进的RNN变体，可以更好地处理长序列。
            """,
            metadata={"source": "AI教程", "chapter": "RNN", "page": 3}
        ),
        Document(
            page_content="""
            Transformer是一种基于自注意力机制的神经网络架构，由Google在2017年提出。
            它摒弃了RNN的循环结构，完全依赖注意力机制来建模序列中的依赖关系。
            Transformer的核心是自注意力（Self-Attention）机制和位置编码。
            BERT、GPT、T5等现代大语言模型都基于Transformer架构。
            """,
            metadata={"source": "AI教程", "chapter": "Transformer", "page": 4}
        ),
        Document(
            page_content="""
            自然语言处理（NLP）是人工智能的一个重要分支，致力于让计算机理解和生成人类语言。
            NLP的任务包括文本分类、命名实体识别、机器翻译、问答系统、文本摘要等。
            现代NLP主要基于深度学习技术，特别是Transformer架构和预训练语言模型。
            """,
            metadata={"source": "AI教程", "chapter": "NLP", "page": 5}
        ),
        Document(
            page_content="""
            预训练语言模型通过在大规模文本语料上进行预训练，学习通用的语言表示。
            然后可以通过微调（Fine-tuning）的方式适应特定的下游任务。
            BERT使用掩码语言模型进行预训练，GPT使用自回归语言模型。
            这种"预训练+微调"的范式显著提升了NLP任务的性能。
            """,
            metadata={"source": "AI教程", "chapter": "预训练模型", "page": 6}
        ),
        Document(
            page_content="""
            检索增强生成（RAG）是一种结合信息检索和文本生成的技术。
            RAG系统首先从知识库中检索相关文档，然后将检索到的文档作为上下文提供给生成模型。
            这种方法可以有效减少大语言模型的幻觉问题，提高生成内容的准确性和可靠性。
            RAG特别适合构建知识密集型应用，如问答系统和智能助手。
            """,
            metadata={"source": "AI教程", "chapter": "RAG", "page": 7}
        ),
        Document(
            page_content="""
            向量数据库是专门用于存储和检索高维向量的数据库系统。
            它们支持高效的相似度搜索，是构建RAG系统的关键组件。
            常见的向量数据库包括FAISS、Pinecone、Milvus、Weaviate、ChromaDB等。
            向量数据库的核心是近似最近邻（ANN）搜索算法，如HNSW、IVF等。
            """,
            metadata={"source": "AI教程", "chapter": "向量数据库", "page": 8}
        ),
    ]

    return documents


def demo_complete_workflow():
    """演示完整的RAG工作流"""
    print("=" * 80)
    print("完整RAG工作流演示")
    print("=" * 80)
    print()

    # 步骤1: 创建文档
    print("步骤1: 准备文档")
    print("-" * 80)
    documents = create_sample_documents()
    print(f"创建了 {len(documents)} 个示例文档")
    print(f"文档主题: 深度学习、CNN、RNN、Transformer、NLP、预训练模型、RAG、向量数据库")
    print()

    # 步骤2: 文档分块
    print("步骤2: 文档分块")
    print("-" * 80)
    try:
        from recursive_chunking import RecursiveChunker

        chunker = RecursiveChunker(chunk_size=300, chunk_overlap=30)
        chunks = chunker.split_documents(documents)
        print(f"分块完成: {len(documents)} 个文档 -> {len(chunks)} 个块")
        print(f"平均块大小: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} 字符")
        print()

    except Exception as e:
        print(f"分块失败: {e}")
        chunks = documents
        print("使用原始文档继续")
        print()

    # 步骤3: 创建向量存储
    print("步骤3: 创建向量存储")
    print("-" * 80)
    print("注意: 首次运行会下载BGE模型（约400MB），需要等待...")
    try:
        from faiss_vectorstore import FAISSVectorStore

        vectorstore = FAISSVectorStore(
            embedding_model_name="BAAI/bge-small-zh-v1.5"
        )
        vectorstore.create_index(chunks)

        stats = vectorstore.get_statistics()
        print(f"向量存储创建成功:")
        print(f"  - 文档数量: {stats['文档数量']}")
        print(f"  - 向量维度: {stats['向量维度']}")
        print()

    except Exception as e:
        print(f"向量存储创建失败: {e}")
        print("提示: 确保已安装 faiss-cpu 和 sentence-transformers")
        return

    # 步骤4: 测试不同的检索策略
    print("步骤4: 测试检索策略")
    print("-" * 80)

    test_queries = [
        "什么是Transformer？",
        "CNN和RNN有什么区别？",
        "RAG系统如何工作？"
    ]

    for query in test_queries:
        print(f"\n查询: {query}")
        print("=" * 60)

        # 基本相似度搜索
        print("\n方法1: 基本相似度搜索")
        results = vectorstore.similarity_search(query, k=2)
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.page_content[:100]}...")
            print(f"   来源: {doc.metadata.get('chapter', 'Unknown')}")

        # MMR搜索
        print("\n方法2: MMR搜索（提高多样性）")
        mmr_results = vectorstore.max_marginal_relevance_search(
            query, k=2, lambda_mult=0.5
        )
        for i, doc in enumerate(mmr_results):
            print(f"{i+1}. {doc.page_content[:100]}...")
            print(f"   来源: {doc.metadata.get('chapter', 'Unknown')}")

    # 步骤5: 混合检索
    print("\n\n步骤5: 混合检索（向量+BM25）")
    print("-" * 80)
    try:
        from hybrid_retrieval import HybridSearchRetriever

        hybrid_retriever = HybridSearchRetriever(
            documents=chunks,
            embedding_model_name="BAAI/bge-small-zh-v1.5",
            dense_weight=0.6,
            sparse_weight=0.4
        )

        query = "深度学习的应用有哪些？"
        print(f"查询: {query}\n")

        results = hybrid_retriever.search(query, k=3)
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.page_content[:120]}...")
            print(f"   章节: {doc.metadata.get('chapter', 'Unknown')}")
        print()

    except Exception as e:
        print(f"混合检索失败: {e}")
        print()

    # 步骤6: 保存索引
    print("步骤6: 保存向量索引")
    print("-" * 80)
    try:
        index_path = str(project_root / "data" / "demo_index")
        vectorstore.save_index(index_path)
        print(f"索引已保存到: {index_path}")
        print()

    except Exception as e:
        print(f"保存索引失败: {e}")
        print()

    # 总结
    print("=" * 80)
    print("演示完成！")
    print("=" * 80)
    print("""
完整工作流总结:
1. ✓ 文档准备 - 创建了8个示例文档
2. ✓ 文档分块 - 使用递归分块策略
3. ✓ 向量存储 - 使用FAISS和BGE Embedding
4. ✓ 检索测试 - 相似度搜索和MMR搜索
5. ✓ 混合检索 - 结合向量和BM25检索
6. ✓ 索引保存 - 持久化到磁盘

下一步:
- 集成LLM进行问答生成（需要API密钥）
- 添加评估指标监控检索质量
- 优化分块和检索参数
- 部署到生产环境

参考代码:
- 完整RAG系统: 08-production-rag/src/complete_system.py
- 各模块示例: 在对应子目录的src文件夹中
    """)


if __name__ == "__main__":
    demo_complete_workflow()
