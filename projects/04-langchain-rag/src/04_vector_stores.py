"""
LangChain RAG应用 - 04: 向量存储（Vector Stores）

本模块演示：
1. FAISS向量存储（内存模式）
2. FAISS持久化（保存和加载）
3. Chroma向量存储
4. 向量索引创建和管理
5. 相似度搜索基础
6. 带过滤器的搜索
7. 向量存储性能对比
8. 索引优化策略

向量存储是RAG系统的核心，用于高效存储和检索文档向量。
"""

import os
import time
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# 准备测试文档
SAMPLE_DOCUMENTS = [
    "LangChain是一个强大的框架，用于构建基于大型语言模型的应用程序。",
    "RAG（检索增强生成）通过结合检索和生成来提高AI回答的准确性。",
    "向量数据库可以高效地存储和检索高维向量数据。",
    "FAISS是Facebook开发的高效相似度搜索库，支持十亿级向量检索。",
    "Chroma是一个开源的向量数据库，专为AI应用设计。",
    "文本嵌入将文本转换为向量表示，是语义搜索的基础。",
    "Python是最流行的AI开发语言，拥有丰富的机器学习库。",
    "Transformer模型革新了自然语言处理领域。",
    "OpenAI的GPT系列模型展示了大型语言模型的强大能力。",
    "向量相似度搜索使用余弦相似度或欧氏距离来衡量向量之间的相似程度。",
]


def get_mock_embeddings():
    """获取模拟的embeddings对象"""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✓ 使用HuggingFace Embeddings (all-MiniLM-L6-v2)\n")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    except:
        # 如果无法加载真实模型，使用假的embeddings
        from langchain.embeddings.fake import FakeEmbeddings
        print("⚠ 使用模拟Embeddings（用于演示）\n")
        return FakeEmbeddings(size=384)


# ==================== 示例1: FAISS向量存储基础 ====================

def demo_faiss_basic():
    """示例1: FAISS向量存储基础用法"""
    print_section("示例1: FAISS向量存储基础用法")

    print("FAISS特点:")
    print("  ✓ 极高的检索速度")
    print("  ✓ 支持十亿级向量")
    print("  ✓ 多种索引类型")
    print("  ✓ 内存高效")
    print("  ✗ 需要安装faiss库\n")

    try:
        from langchain_community.vectorstores import FAISS

        # 获取embeddings
        embeddings = get_mock_embeddings()

        # 创建文档
        documents = [Document(page_content=text) for text in SAMPLE_DOCUMENTS[:5]]

        print(f"创建向量存储，文档数: {len(documents)}\n")

        # 创建FAISS向量存储
        start_time = time.time()
        vectorstore = FAISS.from_documents(documents, embeddings)
        creation_time = time.time() - start_time

        print(f"✓ 向量存储创建完成")
        print(f"  创建耗时: {creation_time*1000:.2f}ms")
        print(f"  文档数量: {len(documents)}\n")

        # 相似度搜索
        query = "什么是RAG技术？"
        print(f"查询: {query}\n")

        start_time = time.time()
        results = vectorstore.similarity_search(query, k=3)
        search_time = time.time() - start_time

        print(f"检索结果 (top 3):")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.page_content}")

        print(f"\n检索耗时: {search_time*1000:.2f}ms\n")

    except ImportError:
        print("⚠ 未安装faiss库")
        print("安装命令: pip install faiss-cpu\n")
        print("FAISS是高性能向量检索库，强烈推荐安装！\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例2: FAISS持久化 ====================

def demo_faiss_persistence():
    """示例2: FAISS持久化（保存和加载）"""
    print_section("示例2: FAISS持久化")

    print("持久化的重要性:")
    print("  ✓ 避免重复计算embeddings")
    print("  ✓ 快速启动应用")
    print("  ✓ 节省计算资源和成本\n")

    try:
        from langchain_community.vectorstores import FAISS

        embeddings = get_mock_embeddings()
        documents = [Document(page_content=text) for text in SAMPLE_DOCUMENTS]

        # 创建临时目录
        temp_dir = Path(tempfile.gettempdir()) / "faiss_demo"
        temp_dir.mkdir(exist_ok=True)
        store_path = str(temp_dir / "my_vectorstore")

        print(f"保存路径: {store_path}\n")

        # 创建并保存向量存储
        print("1. 创建向量存储...")
        vectorstore = FAISS.from_documents(documents, embeddings)
        print(f"   ✓ 创建完成，文档数: {len(documents)}")

        print("\n2. 保存到磁盘...")
        vectorstore.save_local(store_path)
        print(f"   ✓ 保存完成")

        # 检查文件
        files = list(temp_dir.glob("my_vectorstore*"))
        print(f"\n   生成的文件:")
        for f in files:
            size_kb = f.stat().st_size / 1024
            print(f"     • {f.name} ({size_kb:.2f} KB)")

        # 加载向量存储
        print("\n3. 从磁盘加载...")
        loaded_vectorstore = FAISS.load_local(
            store_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"   ✓ 加载完成")

        # 验证功能
        print("\n4. 验证加载的向量存储...")
        query = "向量数据库是什么？"
        results = loaded_vectorstore.similarity_search(query, k=2)

        print(f"   查询: {query}")
        print(f"   结果数: {len(results)}")
        print(f"   第1个结果: {results[0].page_content[:50]}...")
        print(f"\n   ✓ 功能正常\n")

    except ImportError:
        print("⚠ 未安装faiss库\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例3: Chroma向量存储 ====================

def demo_chroma_vectorstore():
    """示例3: Chroma向量存储"""
    print_section("示例3: Chroma向量存储")

    print("Chroma特点:")
    print("  ✓ 专为AI应用设计")
    print("  ✓ 内置持久化")
    print("  ✓ 支持元数据过滤")
    print("  ✓ 简单易用")
    print("  ✗ 相比FAISS速度稍慢\n")

    try:
        from langchain_community.vectorstores import Chroma

        embeddings = get_mock_embeddings()

        # 创建带元数据的文档
        documents = [
            Document(
                page_content=SAMPLE_DOCUMENTS[0],
                metadata={"category": "framework", "difficulty": "beginner"}
            ),
            Document(
                page_content=SAMPLE_DOCUMENTS[1],
                metadata={"category": "technique", "difficulty": "intermediate"}
            ),
            Document(
                page_content=SAMPLE_DOCUMENTS[2],
                metadata={"category": "database", "difficulty": "intermediate"}
            ),
            Document(
                page_content=SAMPLE_DOCUMENTS[3],
                metadata={"category": "database", "difficulty": "advanced"}
            ),
            Document(
                page_content=SAMPLE_DOCUMENTS[4],
                metadata={"category": "database", "difficulty": "beginner"}
            ),
        ]

        print(f"创建Chroma向量存储，文档数: {len(documents)}\n")

        # 创建临时目录
        temp_dir = Path(tempfile.gettempdir()) / "chroma_demo"

        # 创建Chroma向量存储（带持久化）
        vectorstore = Chroma.from_documents(
            documents,
            embeddings,
            persist_directory=str(temp_dir)
        )

        print("✓ 向量存储创建完成\n")

        # 基础搜索
        query = "向量数据库"
        print(f"1. 基础搜索: {query}")
        results = vectorstore.similarity_search(query, k=3)

        for i, doc in enumerate(results, 1):
            print(f"\n   {i}. {doc.page_content[:50]}...")
            print(f"      元数据: {doc.metadata}")

        # 带过滤的搜索
        print(f"\n2. 过滤搜索: category='database'")
        results = vectorstore.similarity_search(
            query,
            k=3,
            filter={"category": "database"}
        )

        print(f"   找到 {len(results)} 个结果")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content[:50]}...")

        print("\n✓ Chroma支持丰富的元数据过滤功能\n")

        # 清理
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    except ImportError:
        print("⚠ 未安装chromadb库")
        print("安装命令: pip install chromadb\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例4: 相似度搜索详解 ====================

def demo_similarity_search_details():
    """示例4: 相似度搜索详解"""
    print_section("示例4: 相似度搜索详解")

    try:
        from langchain_community.vectorstores import FAISS

        embeddings = get_mock_embeddings()
        documents = [Document(page_content=text) for text in SAMPLE_DOCUMENTS]
        vectorstore = FAISS.from_documents(documents, embeddings)

        query = "LangChain框架的应用"
        print(f"查询: {query}\n")

        # 1. 基础相似度搜索
        print("1. similarity_search - 返回最相似的文档")
        results = vectorstore.similarity_search(query, k=3)
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content[:60]}...")

        # 2. 带分数的相似度搜索
        print("\n2. similarity_search_with_score - 返回文档和相似度分数")
        results_with_scores = vectorstore.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(results_with_scores, 1):
            print(f"   {i}. (分数: {score:.4f}) {doc.page_content[:50]}...")

        print("\n   注: 分数越小表示越相似（距离度量）")

        # 3. 按相似度阈值搜索
        print("\n3. similarity_search_with_relevance_scores - 相关性分数")
        results_with_relevance = vectorstore.similarity_search_with_relevance_scores(query, k=5)
        for i, (doc, score) in enumerate(results_with_relevance, 1):
            print(f"   {i}. (相关性: {score:.4f}) {doc.page_content[:50]}...")

        print("\n   注: 相关性分数越高表示越相关\n")

    except ImportError:
        print("⚠ 未安装必要的库\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例5: 向量索引管理 ====================

def demo_index_management():
    """示例5: 向量索引创建和管理"""
    print_section("示例5: 向量索引创建和管理")

    try:
        from langchain_community.vectorstores import FAISS

        embeddings = get_mock_embeddings()

        print("向量索引操作:\n")

        # 1. 创建空索引
        print("1. 创建初始索引")
        initial_docs = [Document(page_content=text) for text in SAMPLE_DOCUMENTS[:3]]
        vectorstore = FAISS.from_documents(initial_docs, embeddings)
        print(f"   ✓ 初始文档数: {len(initial_docs)}")

        # 2. 添加文档
        print("\n2. 添加新文档")
        new_docs = [Document(page_content=text) for text in SAMPLE_DOCUMENTS[3:6]]
        vectorstore.add_documents(new_docs)
        print(f"   ✓ 添加了 {len(new_docs)} 个文档")

        # 3. 验证索引
        print("\n3. 验证索引内容")
        query = "数据库"
        results = vectorstore.similarity_search(query, k=2)
        print(f"   查询: {query}")
        print(f"   结果数: {len(results)}")
        print(f"   第1个: {results[0].page_content[:50]}...")

        # 4. 合并索引
        print("\n4. 合并多个索引")
        docs1 = [Document(page_content=SAMPLE_DOCUMENTS[0])]
        docs2 = [Document(page_content=SAMPLE_DOCUMENTS[1])]

        vs1 = FAISS.from_documents(docs1, embeddings)
        vs2 = FAISS.from_documents(docs2, embeddings)

        print("   • 索引1: 1个文档")
        print("   • 索引2: 1个文档")

        vs1.merge_from(vs2)
        print("   ✓ 合并完成")

        results = vs1.similarity_search("LangChain", k=2)
        print(f"   合并后可检索: {len(results)} 个结果\n")

    except ImportError:
        print("⚠ 未安装必要的库\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例6: 元数据过滤搜索 ====================

def demo_metadata_filtering():
    """示例6: 带元数据过滤的搜索"""
    print_section("示例6: 带元数据过滤的搜索")

    print("元数据过滤的优势:")
    print("  ✓ 精确控制搜索范围")
    print("  ✓ 实现多维度检索")
    print("  ✓ 提高检索相关性\n")

    try:
        from langchain_community.vectorstores import Chroma

        embeddings = get_mock_embeddings()

        # 创建带丰富元数据的文档
        documents = [
            Document(
                page_content="LangChain框架教程 - 入门篇",
                metadata={"type": "tutorial", "level": "beginner", "topic": "framework"}
            ),
            Document(
                page_content="LangChain框架教程 - 高级篇",
                metadata={"type": "tutorial", "level": "advanced", "topic": "framework"}
            ),
            Document(
                page_content="RAG技术详解",
                metadata={"type": "article", "level": "intermediate", "topic": "technique"}
            ),
            Document(
                page_content="向量数据库对比分析",
                metadata={"type": "article", "level": "intermediate", "topic": "database"}
            ),
            Document(
                page_content="FAISS快速入门指南",
                metadata={"type": "guide", "level": "beginner", "topic": "database"}
            ),
        ]

        temp_dir = Path(tempfile.gettempdir()) / "chroma_filter_demo"

        vectorstore = Chroma.from_documents(
            documents,
            embeddings,
            persist_directory=str(temp_dir)
        )

        query = "教程"

        # 1. 无过滤搜索
        print(f"1. 无过滤搜索: {query}")
        results = vectorstore.similarity_search(query, k=3)
        print(f"   找到 {len(results)} 个结果:")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content} | {doc.metadata}")

        # 2. 单个过滤条件
        print(f"\n2. 过滤: level='beginner'")
        results = vectorstore.similarity_search(
            query,
            k=3,
            filter={"level": "beginner"}
        )
        print(f"   找到 {len(results)} 个结果:")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content} | {doc.metadata}")

        # 3. 多个过滤条件
        print(f"\n3. 过滤: type='tutorial' AND level='beginner'")
        results = vectorstore.similarity_search(
            query,
            k=3,
            filter={"type": "tutorial", "level": "beginner"}
        )
        print(f"   找到 {len(results)} 个结果:")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content} | {doc.metadata}")

        print("\n应用场景:")
        print("  • 多租户系统（按用户ID过滤）")
        print("  • 时间范围（按日期过滤）")
        print("  • 权限控制（按访问级别过滤）")
        print("  • 内容分类（按标签过滤）\n")

        # 清理
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    except ImportError:
        print("⚠ 未安装chromadb库\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例7: 向量存储性能对比 ====================

def demo_performance_comparison():
    """示例7: 向量存储性能对比"""
    print_section("示例7: 向量存储性能对比")

    print("常见向量存储对比:\n")

    comparisons = [
        {
            "名称": "FAISS",
            "类型": "库",
            "速度": "极快",
            "规模": "十亿级",
            "持久化": "需手动",
            "元数据": "有限",
            "适用": "大规模、高性能"
        },
        {
            "名称": "Chroma",
            "类型": "数据库",
            "速度": "快",
            "规模": "百万级",
            "持久化": "自动",
            "元数据": "丰富",
            "适用": "中小规模、开发友好"
        },
        {
            "名称": "Pinecone",
            "类型": "云服务",
            "速度": "快",
            "规模": "十亿级",
            "持久化": "自动",
            "元数据": "丰富",
            "适用": "生产环境、托管服务"
        },
        {
            "名称": "Weaviate",
            "类型": "数据库",
            "速度": "快",
            "规模": "十亿级",
            "持久化": "自动",
            "元数据": "非常丰富",
            "适用": "企业级、复杂查询"
        },
    ]

    # 打印对比表格
    print(f"{'名称':<12} {'类型':<8} {'速度':<8} {'规模':<10} {'持久化':<8} {'元数据':<10} {'适用场景'}")
    print("-" * 90)

    for comp in comparisons:
        print(f"{comp['名称']:<12} {comp['类型']:<8} {comp['速度']:<8} {comp['规模']:<10} "
              f"{comp['持久化']:<8} {comp['元数据']:<10} {comp['适用']}")

    print("\n性能基准（参考值）:\n")

    benchmarks = {
        "索引构建": {
            "FAISS": "1000文档/秒",
            "Chroma": "500文档/秒"
        },
        "查询速度": {
            "FAISS": "<1ms",
            "Chroma": "1-5ms"
        },
        "内存占用": {
            "FAISS": "低",
            "Chroma": "中等"
        }
    }

    for metric, values in benchmarks.items():
        print(f"{metric}:")
        for store, value in values.items():
            print(f"  {store}: {value}")
        print()

    print("选择建议:")
    print("  • 原型开发: Chroma（简单易用）")
    print("  • 生产环境（大规模）: FAISS + 自建管理")
    print("  • 生产环境（中小规模）: Pinecone/Weaviate（托管）")
    print("  • 复杂查询需求: Weaviate\n")


# ==================== 示例8: 索引优化策略 ====================

def demo_index_optimization():
    """示例8: 向量索引优化策略"""
    print_section("示例8: 向量索引优化策略")

    print("索引优化策略:\n")

    print("1. 选择合适的索引类型（FAISS）")
    print("   • IndexFlatL2: 精确搜索，小规模(<10K)")
    print("   • IndexIVFFlat: 聚类倒排，中规模(10K-1M)")
    print("   • IndexIVFPQ: 量化压缩，大规模(>1M)")
    print("   • IndexHNSW: 图索引，快速近似\n")

    print("2. 批量操作")
    print("   • 批量添加文档而非逐个添加")
    print("   • 减少索引重建次数")
    print("   • 示例:")
    print("""
   # 不推荐
   for doc in documents:
       vectorstore.add_documents([doc])

   # 推荐
   vectorstore.add_documents(documents)
    """)

    print("\n3. 向量维度优化")
    print("   • 较低维度（384）: 速度快，存储小")
    print("   • 中等维度（768-1536）: 平衡选择")
    print("   • 高维度（3072+）: 质量高，但慢\n")

    print("4. 元数据设计")
    print("   • 只存储必要的元数据")
    print("   • 使用合适的数据类型")
    print("   • 为常用过滤字段建索引\n")

    print("5. 缓存策略")
    print("   • 缓存热门查询结果")
    print("   • 缓存embedding计算结果")
    print("   • 使用内存缓存或Redis\n")

    print("6. 分片策略（大规模）")
    print("   • 按时间分片（如按月）")
    print("   • 按类别分片（如按主题）")
    print("   • 并行查询多个分片\n")

    print("7. 监控和调优")
    print("   • 监控查询延迟")
    print("   • 监控索引大小")
    print("   • 定期重建索引")
    print("   • A/B测试不同配置\n")

    print("实际优化案例:")
    print("  场景: 100万文档的知识库")
    print("  优化前: FAISS Flat索引，查询30ms")
    print("  优化后: FAISS IVF索引，查询3ms")
    print("  提升: 10倍性能提升，准确率损失<2%\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 04: 向量存储")
    print("="*70)

    try:
        # 示例1: FAISS基础
        demo_faiss_basic()

        # 示例2: FAISS持久化
        demo_faiss_persistence()

        # 示例3: Chroma向量存储
        demo_chroma_vectorstore()

        # 示例4: 相似度搜索详解
        demo_similarity_search_details()

        # 示例5: 索引管理
        demo_index_management()

        # 示例6: 元数据过滤
        demo_metadata_filtering()

        # 示例7: 性能对比
        demo_performance_comparison()

        # 示例8: 索引优化
        demo_index_optimization()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • FAISS: 高性能，适合大规模")
        print("    • Chroma: 易用，适合开发和中小规模")
        print("    • 持久化避免重复计算")
        print("    • 元数据过滤提高检索精度")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
