"""
分块策略对比
比较不同分块策略的效果
"""

from typing import List, Dict
from langchain.schema import Document
import time
import matplotlib.pyplot as plt
import numpy as np
import logging

from fixed_size_chunking import FixedSizeChunker
from semantic_chunking import SimplifiedSemanticChunker
from recursive_chunking import RecursiveChunker, MarkdownStructureChunker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChunkingComparison:
    """分块策略对比工具"""

    def __init__(self):
        self.results = {}

    def compare_strategies(self, documents: List[Document]) -> Dict:
        """
        对比多种分块策略

        Args:
            documents: 原始文档列表

        Returns:
            对比结果字典
        """
        strategies = {
            "固定大小-字符分割": lambda: FixedSizeChunker(chunk_size=300, chunk_overlap=30).split_by_character(documents),
            "固定大小-递归分割": lambda: FixedSizeChunker(chunk_size=300, chunk_overlap=30).split_by_recursive(documents),
            "递归分块": lambda: RecursiveChunker(chunk_size=300, chunk_overlap=30).split_documents(documents),
            "语义分块-简化版": lambda: SimplifiedSemanticChunker(target_chunk_size=300, min_chunk_size=100).split_documents(documents),
        }

        results = {}

        for strategy_name, strategy_func in strategies.items():
            try:
                logger.info(f"测试策略: {strategy_name}")

                # 记录开始时间
                start_time = time.time()

                # 执行分块
                chunks = strategy_func()

                # 记录结束时间
                end_time = time.time()
                duration = end_time - start_time

                # 统计信息
                chunk_lengths = [len(chunk.page_content) for chunk in chunks]

                results[strategy_name] = {
                    "块数量": len(chunks),
                    "平均长度": np.mean(chunk_lengths) if chunk_lengths else 0,
                    "最小长度": np.min(chunk_lengths) if chunk_lengths else 0,
                    "最大长度": np.max(chunk_lengths) if chunk_lengths else 0,
                    "标准差": np.std(chunk_lengths) if chunk_lengths else 0,
                    "耗时(秒)": duration,
                    "chunks": chunks
                }

                logger.info(f"{strategy_name} 完成: {len(chunks)} 个块")

            except Exception as e:
                logger.error(f"{strategy_name} 失败: {str(e)}")
                results[strategy_name] = {"error": str(e)}

        self.results = results
        return results

    def print_comparison(self):
        """打印对比结果"""
        if not self.results:
            print("没有对比结果")
            return

        print("\n" + "=" * 80)
        print("分块策略对比结果")
        print("=" * 80 + "\n")

        # 表格头
        print(f"{'策略名称':<20} {'块数量':<10} {'平均长度':<12} {'最小长度':<10} {'最大长度':<10} {'耗时(s)':<10}")
        print("-" * 80)

        # 数据行
        for strategy_name, result in self.results.items():
            if "error" in result:
                print(f"{strategy_name:<20} 失败: {result['error']}")
            else:
                print(f"{strategy_name:<20} "
                      f"{result['块数量']:<10} "
                      f"{result['平均长度']:<12.1f} "
                      f"{result['最小长度']:<10} "
                      f"{result['最大长度']:<10} "
                      f"{result['耗时(秒)']:<10.4f}")

        print("=" * 80 + "\n")

    def visualize_comparison(self, save_path: str = None):
        """
        可视化对比结果

        Args:
            save_path: 保存图片的路径，None则显示
        """
        if not self.results:
            print("没有对比结果")
            return

        try:
            # 准备数据
            strategies = []
            chunk_counts = []
            avg_lengths = []
            std_devs = []

            for strategy_name, result in self.results.items():
                if "error" not in result:
                    strategies.append(strategy_name)
                    chunk_counts.append(result['块数量'])
                    avg_lengths.append(result['平均长度'])
                    std_devs.append(result['标准差'])

            if not strategies:
                print("没有有效的对比数据")
                return

            # 创建图表
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('分块策略对比', fontsize=16, fontproperties='SimHei')

            # 1. 块数量对比
            axes[0, 0].bar(range(len(strategies)), chunk_counts, color='skyblue')
            axes[0, 0].set_xticks(range(len(strategies)))
            axes[0, 0].set_xticklabels(strategies, rotation=45, ha='right', fontproperties='SimHei')
            axes[0, 0].set_ylabel('块数量', fontproperties='SimHei')
            axes[0, 0].set_title('块数量对比', fontproperties='SimHei')
            axes[0, 0].grid(axis='y', alpha=0.3)

            # 2. 平均长度对比
            axes[0, 1].bar(range(len(strategies)), avg_lengths, color='lightgreen')
            axes[0, 1].set_xticks(range(len(strategies)))
            axes[0, 1].set_xticklabels(strategies, rotation=45, ha='right', fontproperties='SimHei')
            axes[0, 1].set_ylabel('平均长度(字符)', fontproperties='SimHei')
            axes[0, 1].set_title('平均长度对比', fontproperties='SimHei')
            axes[0, 1].grid(axis='y', alpha=0.3)

            # 3. 长度分布箱线图
            box_data = []
            for strategy_name in strategies:
                result = self.results[strategy_name]
                lengths = [len(chunk.page_content) for chunk in result['chunks']]
                box_data.append(lengths)

            axes[1, 0].boxplot(box_data, labels=strategies)
            axes[1, 0].set_xticklabels(strategies, rotation=45, ha='right', fontproperties='SimHei')
            axes[1, 0].set_ylabel('长度(字符)', fontproperties='SimHei')
            axes[1, 0].set_title('长度分布箱线图', fontproperties='SimHei')
            axes[1, 0].grid(axis='y', alpha=0.3)

            # 4. 标准差对比
            axes[1, 1].bar(range(len(strategies)), std_devs, color='salmon')
            axes[1, 1].set_xticks(range(len(strategies)))
            axes[1, 1].set_xticklabels(strategies, rotation=45, ha='right', fontproperties='SimHei')
            axes[1, 1].set_ylabel('标准差', fontproperties='SimHei')
            axes[1, 1].set_title('长度标准差对比', fontproperties='SimHei')
            axes[1, 1].grid(axis='y', alpha=0.3)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"图表已保存到: {save_path}")
            else:
                plt.show()

        except ImportError:
            print("可视化需要安装matplotlib: pip install matplotlib")
        except Exception as e:
            logger.error(f"可视化失败: {str(e)}")


def demo():
    """演示分块策略对比"""
    print("=== 分块策略对比演示 ===\n")

    # 创建示例文档
    sample_text = """
自然语言处理的发展历程

自然语言处理（Natural Language Processing, NLP）是人工智能领域的一个重要分支，致力于让计算机理解、处理和生成人类语言。

早期方法
早期的NLP系统主要基于规则和符号方法。研究者手工编写语法规则和词典，通过模式匹配来处理文本。这种方法在特定领域表现良好，但难以扩展到开放域任务。

统计方法的兴起
随着计算能力的提升和语料库的建设，统计方法逐渐成为主流。隐马尔可夫模型、条件随机场等概率图模型被广泛应用于词性标注、命名实体识别等任务。

深度学习革命
深度学习的出现彻底改变了NLP领域。词向量技术（如Word2Vec、GloVe）让计算机能够学习词语的语义表示。循环神经网络（RNN）和长短期记忆网络（LSTM）成功处理了序列数据。

Transformer时代
2017年，Transformer架构的提出标志着NLP进入新时代。自注意力机制让模型能够高效地捕捉长距离依赖关系。BERT、GPT等预训练模型在多个任务上取得了突破性进展。

大语言模型
近年来，大语言模型（Large Language Models）展现了惊人的能力。这些模型在海量文本数据上训练，不仅能够理解语言，还展现了推理、对话、代码生成等多种能力。

未来展望
NLP的未来发展方向包括多模态理解、低资源语言处理、可解释性增强、以及更高效的模型架构。检索增强生成（RAG）等技术正在解决大模型的幻觉问题，使其更加实用可靠。
    """.strip()

    documents = [Document(page_content=sample_text, metadata={"source": "demo"})]

    # 创建对比工具
    comparator = ChunkingComparison()

    # 执行对比
    print("开始对比不同分块策略...\n")
    results = comparator.compare_strategies(documents)

    # 打印结果
    comparator.print_comparison()

    # 可视化（可选）
    print("\n提示: 可视化需要安装matplotlib")
    print("如需生成对比图表，取消注释以下代码：")
    print("# comparator.visualize_comparison(save_path='chunking_comparison.png')")

    # 详细查看某个策略的结果
    print("\n=== 详细查看: 递归分块结果 ===")
    if "递归分块" in results and "error" not in results["递归分块"]:
        chunks = results["递归分块"]["chunks"]
        for i, chunk in enumerate(chunks[:3]):  # 只显示前3个
            print(f"\n块 {i+1}:")
            print(f"长度: {len(chunk.page_content)} 字符")
            print(f"内容: {chunk.page_content}")
            print("-" * 60)


if __name__ == "__main__":
    demo()
