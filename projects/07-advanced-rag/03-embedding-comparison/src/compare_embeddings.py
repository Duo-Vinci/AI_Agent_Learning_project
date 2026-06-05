"""
Embedding模型对比
比较不同Embedding模型在中文文本上的表现
"""

from typing import List, Dict, Tuple
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingModelComparison:
    """Embedding模型对比工具"""

    def __init__(self):
        self.models = {}
        self.results = {}

    def add_model(self, name: str, embeddings):
        """
        添加要对比的模型

        Args:
            name: 模型名称
            embeddings: LangChain Embeddings对象
        """
        self.models[name] = embeddings
        logger.info(f"添加模型: {name}")

    def load_common_models(self):
        """加载常用的中文Embedding模型"""
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings

            # 模型列表（按大小从小到大）
            models_config = {
                "BGE-Small-ZH": "BAAI/bge-small-zh-v1.5",
                "BGE-Base-ZH": "BAAI/bge-base-zh-v1.5",
                "M3E-Base": "moka-ai/m3e-base",
            }

            for name, model_name in models_config.items():
                try:
                    logger.info(f"尝试加载模型: {name} ({model_name})")
                    embeddings = HuggingFaceEmbeddings(
                        model_name=model_name,
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                    self.add_model(name, embeddings)
                    logger.info(f"成功加载: {name}")
                except Exception as e:
                    logger.warning(f"加载模型 {name} 失败: {e}")

        except ImportError:
            logger.error("需要安装 sentence-transformers: pip install sentence-transformers")

    def compare_embedding_quality(
        self,
        queries: List[str],
        documents: List[str],
        relevance_matrix: np.ndarray = None
    ) -> Dict:
        """
        对比Embedding质量

        Args:
            queries: 查询列表
            documents: 文档列表
            relevance_matrix: 相关性矩阵（可选），shape=(len(queries), len(documents))

        Returns:
            对比结果
        """
        results = {}

        for model_name, embeddings in self.models.items():
            try:
                logger.info(f"测试模型: {model_name}")

                # 1. 测试速度
                start_time = time.time()
                query_embeddings = [embeddings.embed_query(q) for q in queries]
                doc_embeddings = [embeddings.embed_query(d) for d in documents]
                duration = time.time() - start_time

                # 2. 计算相似度矩阵
                similarity_matrix = cosine_similarity(query_embeddings, doc_embeddings)

                # 3. 统计信息
                embedding_dim = len(query_embeddings[0])

                result = {
                    "维度": embedding_dim,
                    "查询耗时(秒)": duration,
                    "平均每个查询(秒)": duration / len(queries),
                    "相似度矩阵": similarity_matrix,
                }

                # 4. 如果提供了相关性矩阵，计算准确性指标
                if relevance_matrix is not None:
                    accuracy_metrics = self._calculate_accuracy_metrics(
                        similarity_matrix,
                        relevance_matrix
                    )
                    result.update(accuracy_metrics)

                results[model_name] = result
                logger.info(f"{model_name} 测试完成")

            except Exception as e:
                logger.error(f"{model_name} 测试失败: {str(e)}")
                results[model_name] = {"error": str(e)}

        self.results = results
        return results

    def _calculate_accuracy_metrics(
        self,
        similarity_matrix: np.ndarray,
        relevance_matrix: np.ndarray
    ) -> Dict:
        """
        计算准确性指标

        Args:
            similarity_matrix: 模型预测的相似度矩阵
            relevance_matrix: 真实相关性矩阵

        Returns:
            准确性指标
        """
        # 计算每个查询的Top-K准确率
        k_values = [1, 3, 5]
        metrics = {}

        for k in k_values:
            correct = 0
            total = len(similarity_matrix)

            for i in range(total):
                # 获取预测的Top-K
                pred_top_k = np.argsort(similarity_matrix[i])[-k:][::-1]
                # 获取真实的相关文档
                true_relevant = np.where(relevance_matrix[i] > 0)[0]

                # 检查是否有交集
                if len(set(pred_top_k) & set(true_relevant)) > 0:
                    correct += 1

            metrics[f"Top-{k}准确率"] = correct / total

        return metrics

    def print_comparison(self):
        """打印对比结果"""
        if not self.results:
            print("没有对比结果")
            return

        print("\n" + "=" * 80)
        print("Embedding模型对比结果")
        print("=" * 80 + "\n")

        # 表格头
        print(f"{'模型名称':<20} {'维度':<10} {'总耗时(s)':<12} {'每查询(s)':<12}")
        print("-" * 80)

        # 数据行
        for model_name, result in self.results.items():
            if "error" in result:
                print(f"{model_name:<20} 失败: {result['error']}")
            else:
                print(f"{model_name:<20} "
                      f"{result['维度']:<10} "
                      f"{result['查询耗时(秒)']:<12.4f} "
                      f"{result['平均每个查询(秒)']:<12.4f}")

        # 如果有准确性指标，也打印
        has_accuracy = any("Top-1准确率" in r for r in self.results.values() if "error" not in r)
        if has_accuracy:
            print("\n准确性指标:")
            print(f"{'模型名称':<20} {'Top-1':<10} {'Top-3':<10} {'Top-5':<10}")
            print("-" * 80)
            for model_name, result in self.results.items():
                if "error" not in result and "Top-1准确率" in result:
                    print(f"{model_name:<20} "
                          f"{result['Top-1准确率']:<10.2%} "
                          f"{result['Top-3准确率']:<10.2%} "
                          f"{result['Top-5准确率']:<10.2%}")

        print("=" * 80 + "\n")

    def analyze_similarity_patterns(self, query_idx: int = 0):
        """
        分析特定查询的相似度模式

        Args:
            query_idx: 查询索引
        """
        print(f"\n=== 查询 {query_idx+1} 的相似度分析 ===\n")

        for model_name, result in self.results.items():
            if "error" not in result:
                similarities = result["相似度矩阵"][query_idx]
                print(f"{model_name}:")
                print(f"  最高相似度: {np.max(similarities):.4f}")
                print(f"  最低相似度: {np.min(similarities):.4f}")
                print(f"  平均相似度: {np.mean(similarities):.4f}")
                print(f"  Top-3文档索引: {np.argsort(similarities)[-3:][::-1]}")
                print()


def demo():
    """演示Embedding模型对比"""
    print("=== Embedding模型对比演示 ===\n")

    # 测试数据：查询和相关文档
    queries = [
        "什么是深度学习？",
        "如何训练神经网络？",
        "NLP有哪些应用？",
        "RAG系统的优势是什么？"
    ]

    documents = [
        "深度学习是机器学习的一个分支，使用多层神经网络来学习数据表示。",
        "神经网络的训练过程包括前向传播、损失计算和反向传播更新权重。",
        "自然语言处理应用包括机器翻译、情感分析、问答系统等。",
        "检索增强生成结合了信息检索和文本生成，提高了答案的准确性。",
        "计算机视觉主要处理图像和视频数据，包括目标检测和图像分类。",
        "强化学习让智能体通过与环境交互来学习最优策略。",
    ]

    # 相关性矩阵（1表示相关，0表示不相关）
    relevance_matrix = np.array([
        [1, 0, 0, 0, 0, 0],  # 查询0: 深度学习
        [0, 1, 0, 0, 0, 0],  # 查询1: 训练神经网络
        [0, 0, 1, 0, 0, 0],  # 查询2: NLP应用
        [0, 0, 0, 1, 0, 0],  # 查询3: RAG优势
    ])

    # 创建对比工具
    comparator = EmbeddingModelComparison()

    # 方式1: 使用简单的模拟Embedding（用于演示）
    print("使用模拟Embedding模型进行演示...")
    print("（实际使用时应加载真实模型）\n")

    from langchain.embeddings.base import Embeddings

    class MockEmbeddings(Embeddings):
        """模拟Embedding模型"""

        def __init__(self, dim: int = 384, name: str = "Mock"):
            self.dim = dim
            self.name = name

        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return [self.embed_query(text) for text in texts]

        def embed_query(self, text: str) -> List[float]:
            # 简单的基于哈希的模拟embedding
            np.random.seed(hash(text) % (2**32))
            return np.random.randn(self.dim).tolist()

    # 添加模拟模型
    comparator.add_model("Mock-Small (384维)", MockEmbeddings(dim=384))
    comparator.add_model("Mock-Base (768维)", MockEmbeddings(dim=768))
    comparator.add_model("Mock-Large (1024维)", MockEmbeddings(dim=1024))

    # 执行对比
    print("开始对比Embedding模型...\n")
    results = comparator.compare_embedding_quality(queries, documents, relevance_matrix)

    # 打印结果
    comparator.print_comparison()

    # 分析特定查询
    comparator.analyze_similarity_patterns(query_idx=0)

    # 提示如何使用真实模型
    print("\n" + "=" * 80)
    print("使用真实模型的方法:")
    print("=" * 80)
    print("""
1. 安装依赖:
   pip install sentence-transformers

2. 加载真实模型:
   comparator = EmbeddingModelComparison()
   comparator.load_common_models()  # 自动加载BGE等中文模型

3. 或手动添加模型:
   from langchain_community.embeddings import HuggingFaceEmbeddings

   embeddings = HuggingFaceEmbeddings(
       model_name="BAAI/bge-large-zh-v1.5",
       model_kwargs={'device': 'cpu'}
   )
   comparator.add_model("BGE-Large-ZH", embeddings)

注意: 首次运行会自动下载模型文件（约400MB-1GB），需要等待。
""")

    # 方式2: 尝试加载真实模型（可选）
    print("\n尝试加载真实模型（需要网络连接）...")
    try:
        real_comparator = EmbeddingModelComparison()
        real_comparator.load_common_models()

        if real_comparator.models:
            print(f"\n成功加载 {len(real_comparator.models)} 个真实模型")
            print("可以使用以下代码进行对比:")
            print("real_results = real_comparator.compare_embedding_quality(queries, documents, relevance_matrix)")
            print("real_comparator.print_comparison()")
        else:
            print("未能加载真实模型，请检查网络连接或手动下载模型")

    except Exception as e:
        print(f"加载真实模型失败: {e}")
        print("继续使用模拟模型进行演示")


if __name__ == "__main__":
    demo()
