"""
LangChain RAG应用 - 03: 文本嵌入（Embeddings）

本模块演示：
1. OpenAI Embeddings（text-embedding-ada-002、text-embedding-3-small/large）
2. HuggingFace Embeddings
3. 本地Embeddings（sentence-transformers）
4. 中文Embeddings（BGE: BAAI/bge-large-zh-v1.5）
5. Embedding维度对比
6. 性能和质量对比
7. 成本分析
8. Embedding缓存策略

Embeddings将文本转换为向量表示，是语义检索的基础。
"""

import os
import time
from typing import List, Dict, Any, Optional
import numpy as np


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算余弦相似度"""
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    return np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np))


# 测试文本
TEST_TEXTS = [
    "LangChain是一个用于构建AI应用的框架",
    "LangChain框架帮助开发者快速构建智能应用",
    "Python是一种流行的编程语言",
    "机器学习是人工智能的重要分支",
]


# ==================== 示例1: OpenAI Embeddings基础 ====================

def demo_openai_embeddings_basic():
    """示例1: OpenAI Embeddings基础用法"""
    print_section("示例1: OpenAI Embeddings基础用法")

    print("OpenAI Embeddings特点:")
    print("  ✓ 高质量向量表示")
    print("  ✓ 支持多语言")
    print("  ✓ API调用简单")
    print("  ✗ 需要API密钥")
    print("  ✗ 按使用量付费\n")

    try:
        from langchain_openai import OpenAIEmbeddings

        # 检查API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠ 未设置OPENAI_API_KEY环境变量")
            print("设置方法: export OPENAI_API_KEY='your-api-key'\n")
            print("模拟示例（实际需要API密钥）:\n")
            demo_simulated_embeddings()
            return

        # 创建embeddings对象
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # 新模型，性价比高
            openai_api_key=api_key
        )

        print("模型配置:")
        print("  模型: text-embedding-3-small")
        print("  维度: 1536")
        print("  成本: ~$0.02/1M tokens\n")

        # 嵌入单个文本
        text = "LangChain是一个强大的AI开发框架"
        print(f"文本: {text}")

        vector = embeddings.embed_query(text)

        print(f"\n向量维度: {len(vector)}")
        print(f"向量前10个值: {vector[:10]}")
        print(f"向量范围: [{min(vector):.4f}, {max(vector):.4f}]\n")

        # 嵌入多个文本
        print("批量嵌入多个文本:")
        texts = TEST_TEXTS[:3]
        vectors = embeddings.embed_documents(texts)

        for i, (text, vec) in enumerate(zip(texts, vectors), 1):
            print(f"\n文本{i}: {text}")
            print(f"  维度: {len(vec)}")
            print(f"  前5个值: {vec[:5]}")

        # 计算相似度
        print("\n相似度计算:")
        sim1 = cosine_similarity(vectors[0], vectors[1])
        sim2 = cosine_similarity(vectors[0], vectors[2])
        print(f"  文本1 vs 文本2: {sim1:.4f} (相关)")
        print(f"  文本1 vs 文本3: {sim2:.4f} (不太相关)\n")

    except ImportError:
        print("⚠ 未安装langchain-openai")
        print("安装命令: pip install langchain-openai\n")
        demo_simulated_embeddings()
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")
        demo_simulated_embeddings()


def demo_simulated_embeddings():
    """模拟embeddings示例"""
    print("模拟示例（用于演示）:\n")

    # 生成随机向量（仅用于演示）
    np.random.seed(42)

    text = "LangChain是一个强大的AI开发框架"
    vector = np.random.randn(1536).tolist()

    print(f"文本: {text}")
    print(f"向量维度: {len(vector)}")
    print(f"向量前10个值: {[f'{v:.4f}' for v in vector[:10]]}")
    print(f"向量范围: [{min(vector):.4f}, {max(vector):.4f}]\n")


# ==================== 示例2: OpenAI模型对比 ====================

def demo_openai_models_comparison():
    """示例2: OpenAI不同模型对比"""
    print_section("示例2: OpenAI不同Embedding模型对比")

    print("OpenAI Embedding模型对比:\n")

    models_info = {
        "text-embedding-ada-002": {
            "维度": 1536,
            "成本": "$0.10/1M tokens",
            "发布": "2022",
            "特点": "经典模型，广泛使用"
        },
        "text-embedding-3-small": {
            "维度": 1536,
            "成本": "$0.02/1M tokens",
            "发布": "2024",
            "特点": "性价比最高，推荐"
        },
        "text-embedding-3-large": {
            "维度": 3072,
            "成本": "$0.13/1M tokens",
            "发布": "2024",
            "特点": "最高质量，维度最大"
        },
    }

    for model, info in models_info.items():
        print(f"{model}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()

    print("选择建议:")
    print("  • 一般应用: text-embedding-3-small (性价比高)")
    print("  • 高精度需求: text-embedding-3-large")
    print("  • 兼容老系统: text-embedding-ada-002")
    print()

    print("成本计算示例:")
    print("  假设1000个文档，平均500 tokens/文档")
    print("  总tokens: 500,000")
    print("  • 3-small成本: $0.01")
    print("  • 3-large成本: $0.065")
    print("  • ada-002成本: $0.05\n")


# ==================== 示例3: HuggingFace Embeddings ====================

def demo_huggingface_embeddings():
    """示例3: HuggingFace Embeddings"""
    print_section("示例3: HuggingFace Embeddings")

    print("HuggingFace Embeddings特点:")
    print("  ✓ 完全免费")
    print("  ✓ 可本地运行")
    print("  ✓ 模型选择丰富")
    print("  ✗ 首次下载模型较慢")
    print("  ✗ 需要较多内存\n")

    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        print("加载模型（首次会下载，请耐心等待）...")

        # 使用轻量级模型
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        print("✓ 模型加载完成\n")

        print("模型信息:")
        print("  模型: all-MiniLM-L6-v2")
        print("  维度: 384")
        print("  大小: ~80MB")
        print("  速度: 快\n")

        # 嵌入文本
        text = "LangChain帮助开发AI应用"
        print(f"文本: {text}")

        start_time = time.time()
        vector = embeddings.embed_query(text)
        elapsed = time.time() - start_time

        print(f"\n向量维度: {len(vector)}")
        print(f"向量前10个值: {[f'{v:.4f}' for v in vector[:10]]}")
        print(f"嵌入耗时: {elapsed*1000:.2f}ms\n")

        # 批量嵌入
        print("批量嵌入:")
        texts = TEST_TEXTS[:3]

        start_time = time.time()
        vectors = embeddings.embed_documents(texts)
        elapsed = time.time() - start_time

        print(f"  文本数: {len(texts)}")
        print(f"  总耗时: {elapsed*1000:.2f}ms")
        print(f"  平均: {elapsed*1000/len(texts):.2f}ms/文本\n")

    except ImportError:
        print("⚠ 未安装必要的库")
        print("安装命令: pip install langchain-huggingface sentence-transformers\n")
        print("模拟示例:")
        print("  模型: all-MiniLM-L6-v2")
        print("  维度: 384")
        print("  嵌入速度: ~20ms/文本\n")
    except Exception as e:
        print(f"✗ 错误: {str(e)}\n")


# ==================== 示例4: 中文Embeddings（BGE）====================

def demo_chinese_embeddings():
    """示例4: 中文Embeddings（BGE模型）"""
    print_section("示例4: 中文Embeddings（BGE模型）")

    print("BGE (BAAI General Embedding) 特点:")
    print("  ✓ 专为中文优化")
    print("  ✓ MTEB中文榜单第一")
    print("  ✓ 支持多种尺寸")
    print("  ✓ 完全开源免费\n")

    print("BGE模型系列:\n")

    bge_models = {
        "bge-small-zh-v1.5": {
            "维度": 512,
            "大小": "~95MB",
            "速度": "快",
            "适用": "一般应用"
        },
        "bge-base-zh-v1.5": {
            "维度": 768,
            "大小": "~400MB",
            "速度": "中等",
            "适用": "平衡性能和质量"
        },
        "bge-large-zh-v1.5": {
            "维度": 1024,
            "大小": "~1.3GB",
            "速度": "较慢",
            "适用": "最高质量"
        },
    }

    for model, info in bge_models.items():
        print(f"BAAI/{model}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()

    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        print("加载bge-small-zh-v1.5模型...")

        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        print("✓ 模型加载完成\n")

        # 中文测试文本
        chinese_texts = [
            "向量数据库用于存储和检索高维向量",
            "向量数据库可以快速进行相似度搜索",
            "今天天气很好，适合出门散步",
        ]

        print("中文文本嵌入测试:")
        vectors = embeddings.embed_documents(chinese_texts)

        for i, (text, vec) in enumerate(zip(chinese_texts, vectors), 1):
            print(f"\n文本{i}: {text}")
            print(f"  维度: {len(vec)}")
            print(f"  前5个值: {[f'{v:.4f}' for v in vec[:5]]}")

        # 相似度测试
        print("\n中文语义相似度:")
        sim1 = cosine_similarity(vectors[0], vectors[1])
        sim2 = cosine_similarity(vectors[0], vectors[2])
        print(f"  文本1 vs 文本2: {sim1:.4f} (语义相关)")
        print(f"  文本1 vs 文本3: {sim2:.4f} (语义不相关)\n")

    except ImportError:
        print("⚠ 未安装必要的库")
        print("安装命令: pip install langchain-huggingface sentence-transformers\n")
    except Exception as e:
        print(f"注: 实际使用需要下载模型 (~95MB)\n")


# ==================== 示例5: Embedding维度对比 ====================

def demo_dimension_comparison():
    """示例5: Embedding维度对比"""
    print_section("示例5: Embedding维度对比")

    print("不同维度的特点:\n")

    dimensions = {
        384: {
            "模型": "all-MiniLM-L6-v2",
            "存储": "1.5KB/向量",
            "速度": "非常快",
            "质量": "中等",
            "适用": "大规模应用，对速度要求高"
        },
        768: {
            "模型": "bge-base-zh-v1.5",
            "存储": "3KB/向量",
            "速度": "快",
            "质量": "良好",
            "适用": "平衡的选择"
        },
        1536: {
            "模型": "text-embedding-3-small",
            "存储": "6KB/向量",
            "速度": "中等",
            "质量": "很好",
            "适用": "通用推荐"
        },
        3072: {
            "模型": "text-embedding-3-large",
            "存储": "12KB/向量",
            "速度": "较慢",
            "质量": "最好",
            "适用": "高精度需求"
        },
    }

    for dim, info in dimensions.items():
        print(f"维度 {dim}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()

    print("存储成本估算（100万个向量）:")
    for dim in [384, 768, 1536, 3072]:
        size_mb = dim * 4 * 1000000 / (1024 * 1024)  # float32
        print(f"  {dim}维: ~{size_mb:.0f}MB")
    print()

    print("选择建议:")
    print("  • 384-512维: 适合大规模、实时应用")
    print("  • 768-1024维: 平衡的选择，推荐")
    print("  • 1536+维: 追求最高质量\n")


# ==================== 示例6: 性能基准测试 ====================

def demo_performance_benchmark():
    """示例6: Embedding性能基准测试"""
    print_section("示例6: Embedding性能基准测试")

    print("性能测试对比（参考值）:\n")

    # 模拟性能数据
    benchmarks = [
        {
            "模型": "OpenAI text-embedding-3-small",
            "维度": 1536,
            "单个": "50ms",
            "批量(100)": "800ms",
            "每秒": "125个",
            "成本": "$0.02/1M tokens"
        },
        {
            "模型": "OpenAI text-embedding-3-large",
            "维度": 3072,
            "单个": "80ms",
            "批量(100)": "1200ms",
            "每秒": "83个",
            "成本": "$0.13/1M tokens"
        },
        {
            "模型": "HF all-MiniLM-L6-v2",
            "维度": 384,
            "单个": "20ms",
            "批量(100)": "500ms",
            "每秒": "200个",
            "成本": "免费"
        },
        {
            "模型": "BGE bge-base-zh-v1.5",
            "维度": 768,
            "单个": "40ms",
            "批量(100)": "1000ms",
            "每秒": "100个",
            "成本": "免费"
        },
    ]

    # 打印表格
    print(f"{'模型':<35} {'维度':<6} {'单个':<8} {'批量':<10} {'吞吐':<10} {'成本'}")
    print("-" * 95)

    for b in benchmarks:
        print(f"{b['模型']:<35} {b['维度']:<6} {b['单个']:<8} {b['批量']:<10} {b['每秒']:<10} {b['成本']}")

    print("\n注:")
    print("  • 性能受硬件、网络等因素影响")
    print("  • API模型性能稳定，本地模型可优化")
    print("  • 批量处理通常更高效\n")

    print("实际测试示例（本地模型）:")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
        )

        test_texts = TEST_TEXTS * 5  # 20个文本

        # 单个测试
        start = time.time()
        for text in test_texts[:3]:
            _ = embeddings.embed_query(text)
        single_time = (time.time() - start) / 3

        # 批量测试
        start = time.time()
        _ = embeddings.embed_documents(test_texts)
        batch_time = time.time() - start

        print(f"\n测试结果（{len(test_texts)}个文本）:")
        print(f"  单个平均: {single_time*1000:.2f}ms")
        print(f"  批量总时: {batch_time*1000:.2f}ms")
        print(f"  批量平均: {batch_time*1000/len(test_texts):.2f}ms")
        print(f"  速度提升: {single_time/(batch_time/len(test_texts)):.2f}x\n")

    except:
        print("  （需要安装相关库才能运行实际测试）\n")


# ==================== 示例7: 成本分析 ====================

def demo_cost_analysis():
    """示例7: Embedding成本分析"""
    print_section("示例7: Embedding成本分析")

    print("成本对比分析:\n")

    # 场景定义
    scenarios = [
        {
            "场景": "小型知识库",
            "文档数": 1000,
            "平均长度": "500 tokens",
            "总tokens": 500000,
        },
        {
            "场景": "中型知识库",
            "文档数": 10000,
            "平均长度": "500 tokens",
            "总tokens": 5000000,
        },
        {
            "场景": "大型知识库",
            "文档数": 100000,
            "平均长度": "500 tokens",
            "总tokens": 50000000,
        },
    ]

    # 模型价格
    prices = {
        "text-embedding-3-small": 0.02,  # 每1M tokens
        "text-embedding-3-large": 0.13,
        "text-embedding-ada-002": 0.10,
        "本地模型（HF/BGE）": 0.0,
    }

    for scenario in scenarios:
        print(f"{scenario['场景']}:")
        print(f"  文档数: {scenario['文档数']:,}")
        print(f"  总tokens: {scenario['总tokens']:,}\n")

        print("  成本对比:")
        for model, price in prices.items():
            cost = scenario['总tokens'] / 1000000 * price
            if cost > 0:
                print(f"    {model}: ${cost:.2f}")
            else:
                print(f"    {model}: 免费（仅硬件成本）")
        print()

    print("总结:")
    print("  • OpenAI: 按使用量付费，质量高，无需维护")
    print("  • 本地模型: 一次性硬件成本，适合大规模应用")
    print("  • 建议: 小规模用API，大规模用本地模型\n")

    print("隐性成本考虑:")
    print("  • API: 网络延迟、速率限制、数据隐私")
    print("  • 本地: 硬件投资、维护成本、技术门槛\n")


# ==================== 示例8: Embedding缓存策略 ====================

def demo_embedding_cache():
    """示例8: Embedding缓存策略"""
    print_section("示例8: Embedding缓存策略")

    print("为什么需要缓存:")
    print("  ✓ 避免重复计算")
    print("  ✓ 降低API成本")
    print("  ✓ 提高响应速度")
    print("  ✓ 减少网络请求\n")

    print("缓存策略:\n")

    print("1. 内存缓存（适合小规模）")
    print("   • 使用Python字典")
    print("   • 快速但重启丢失")
    print("   • 示例:")
    print("""
   cache = {}
   def get_embedding(text):
       if text not in cache:
           cache[text] = embeddings.embed_query(text)
       return cache[text]
    """)

    print("\n2. 文件缓存（适合中等规模）")
    print("   • 使用pickle或joblib")
    print("   • 持久化存储")
    print("   • 示例:")
    print("""
   import pickle

   def save_cache(cache, filename):
       with open(filename, 'wb') as f:
           pickle.dump(cache, f)

   def load_cache(filename):
       with open(filename, 'rb') as f:
           return pickle.load(f)
    """)

    print("\n3. 数据库缓存（适合大规模）")
    print("   • 使用SQLite或Redis")
    print("   • 支持查询和更新")
    print("   • 适合生产环境")

    print("\n4. LangChain缓存")
    print("   • 内置缓存支持")
    print("   • 示例:")
    print("""
   from langchain.embeddings import CacheBackedEmbeddings
   from langchain.storage import LocalFileStore

   store = LocalFileStore("./cache/")
   cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
       embeddings, store, namespace="my_embeddings"
   )
    """)

    print("\n简单缓存实现演示:")

    class SimpleEmbeddingCache:
        """简单的Embedding缓存"""

        def __init__(self, embeddings):
            self.embeddings = embeddings
            self.cache = {}
            self.hits = 0
            self.misses = 0

        def embed_query(self, text: str) -> List[float]:
            """嵌入单个文本（带缓存）"""
            if text in self.cache:
                self.hits += 1
                return self.cache[text]

            self.misses += 1
            vector = self.embeddings.embed_query(text)
            self.cache[text] = vector
            return vector

        def stats(self) -> Dict[str, Any]:
            """返回缓存统计"""
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "cache_size": len(self.cache)
            }

    # 模拟使用
    print("\n模拟缓存效果:")
    print("  查询序列: [A, B, A, C, B, A]")
    print("  第1次查询A: 未命中，计算embedding")
    print("  第2次查询A: 命中缓存，直接返回")
    print("  第3次查询A: 命中缓存，直接返回")
    print()
    print("  结果: 3次命中，3次未命中，命中率50%")
    print("  性能提升: 减少50%的计算/API调用\n")

    print("缓存最佳实践:")
    print("  • 对相同文本使用一致的预处理")
    print("  • 设置合理的缓存大小限制")
    print("  • 定期清理过期缓存")
    print("  • 监控缓存命中率\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 03: 文本嵌入（Embeddings）")
    print("="*70)

    try:
        # 示例1: OpenAI Embeddings基础
        demo_openai_embeddings_basic()

        # 示例2: OpenAI模型对比
        demo_openai_models_comparison()

        # 示例3: HuggingFace Embeddings
        demo_huggingface_embeddings()

        # 示例4: 中文Embeddings
        demo_chinese_embeddings()

        # 示例5: 维度对比
        demo_dimension_comparison()

        # 示例6: 性能基准测试
        demo_performance_benchmark()

        # 示例7: 成本分析
        demo_cost_analysis()

        # 示例8: 缓存策略
        demo_embedding_cache()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • OpenAI: 高质量，按需付费")
        print("    • HuggingFace: 免费，本地运行")
        print("    • BGE: 中文首选，开源免费")
        print("    • 选择合适的维度和缓存策略")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
