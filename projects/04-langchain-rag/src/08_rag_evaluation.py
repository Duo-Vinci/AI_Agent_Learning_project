"""
LangChain RAG应用 - 08: RAG评估（Evaluation）

本模块演示：
1. 检索准确率评估（Precision@K, Recall@K）
2. 答案质量评估（相关性、准确性、完整性）
3. RAGAS评估框架
4. 评估数据集构建
5. 自动化评估流程
6. 性能指标可视化
7. A/B测试

评估是优化RAG系统的关键，需要量化检索和生成的质量。
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 检索准确率评估 ====================

def demo_retrieval_metrics():
    """示例1: 检索准确率评估"""
    print_section("示例1: 检索准确率评估")

    print("核心指标:\n")

    print("1. Precision@K (精确率)")
    print("   • 定义: 前K个结果中相关的比例")
    print("   • 公式: Precision@K = 相关文档数 / K")
    print("   • 示例: 检索3个文档，2个相关 → Precision@3 = 2/3 = 0.67\n")

    print("2. Recall@K (召回率)")
    print("   • 定义: 前K个结果召回了多少相关文档")
    print("   • 公式: Recall@K = 召回的相关文档 / 总相关文档")
    print("   • 示例: 共5个相关文档，召回3个 → Recall@3 = 3/5 = 0.60\n")

    print("3. MRR (Mean Reciprocal Rank)")
    print("   • 定义: 第一个相关结果的排名倒数")
    print("   • 公式: MRR = 1 / rank_of_first_relevant")
    print("   • 示例: 第一个相关结果在第2位 → MRR = 1/2 = 0.50\n")

    print("4. NDCG (Normalized Discounted Cumulative Gain)")
    print("   • 考虑排名位置的质量指标")
    print("   • 越靠前的相关文档权重越高\n")

    print("实现代码:")
    print("""
def evaluate_retrieval(retrieved_docs: List[str],
                      relevant_docs: List[str],
                      k: int = 5) -> Dict[str, float]:
    '''评估检索质量'''

    # Precision@K
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = set(retrieved_k) & set(relevant_docs)
    precision = len(relevant_retrieved) / k if k > 0 else 0

    # Recall@K
    recall = len(relevant_retrieved) / len(relevant_docs) if relevant_docs else 0

    # F1-Score
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # MRR
    mrr = 0
    for i, doc in enumerate(retrieved_docs, 1):
        if doc in relevant_docs:
            mrr = 1 / i
            break

    return {
        'precision@k': precision,
        'recall@k': recall,
        'f1_score': f1,
        'mrr': mrr
    }

# 使用示例
retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
relevant = ['doc2', 'doc3', 'doc7', 'doc9']

metrics = evaluate_retrieval(retrieved, relevant, k=5)
print(f"Precision@5: {metrics['precision@k']:.2f}")
print(f"Recall@5: {metrics['recall@k']:.2f}")
print(f"F1-Score: {metrics['f1_score']:.2f}")
print(f"MRR: {metrics['mrr']:.2f}")
    """)

    print("\n评估示例:")
    # 模拟评估
    retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
    relevant = ['doc2', 'doc3', 'doc7', 'doc9']

    print(f"检索结果: {retrieved[:3]}...")
    print(f"相关文档: {relevant}")

    relevant_retrieved = [d for d in retrieved[:5] if d in relevant]
    precision = len(relevant_retrieved) / 5
    recall = len(relevant_retrieved) / len(relevant)
    f1 = 2 * precision * recall / (precision + recall)

    print(f"\nPrecision@5: {precision:.2f}")
    print(f"Recall@5: {recall:.2f}")
    print(f"F1-Score: {f1:.2f}\n")


# ==================== 示例2: 答案质量评估 ====================

def demo_answer_quality():
    """示例2: 答案质量评估"""
    print_section("示例2: 答案质量评估")

    print("评估维度:\n")

    print("1. 相关性 (Relevance)")
    print("   • 答案是否回答了问题")
    print("   • 评分: 1-5分")
    print("   • 5分: 完全相关")
    print("   • 1分: 完全无关\n")

    print("2. 准确性 (Accuracy)")
    print("   • 答案是否事实正确")
    print("   • 需要与ground truth对比")
    print("   • 可以使用LLM辅助判断\n")

    print("3. 完整性 (Completeness)")
    print("   • 答案是否全面")
    print("   • 是否遗漏关键信息\n")

    print("4. 忠实度 (Faithfulness)")
    print("   • 答案是否基于提供的文档")
    print("   • 是否出现幻觉\n")

    print("5. 简洁性 (Conciseness)")
    print("   • 答案是否简洁明了")
    print("   • 避免冗余信息\n")

    print("实现方法:\n")

    print("方法1: 人工评估")
    print("""
# 创建评估表格
evaluation_form = {
    'question': '什么是LangChain？',
    'answer': 'LangChain是一个用于构建LLM应用的框架...',
    'relevance': 5,      # 1-5
    'accuracy': 5,       # 1-5
    'completeness': 4,   # 1-5
    'faithfulness': 5,   # 1-5
    'conciseness': 4,    # 1-5
    'comments': '答案准确但略显冗长'
}
    """)

    print("\n方法2: LLM辅助评估")
    print("""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(temperature=0)

eval_prompt = PromptTemplate(
    template='''请评估以下答案的质量：

问题: {question}
答案: {answer}
参考文档: {context}

请从以下维度评分（1-5分）：
1. 相关性: 答案是否回答了问题
2. 准确性: 答案是否事实正确
3. 完整性: 答案是否全面
4. 忠实度: 答案是否基于文档，无幻觉

输出JSON格式:
{{
    "relevance": <分数>,
    "accuracy": <分数>,
    "completeness": <分数>,
    "faithfulness": <分数>,
    "explanation": "<评分理由>"
}}''',
    input_variables=['question', 'answer', 'context']
)

evaluation = llm(eval_prompt.format(
    question=query,
    answer=answer,
    context=context
))
    """)

    print("\n评估示例:")
    print("""
问题: 什么是LangChain？
答案: LangChain是一个开源框架，用于构建基于大型语言模型的应用。

评估结果:
  相关性: ⭐⭐⭐⭐⭐ (5/5) - 直接回答了问题
  准确性: ⭐⭐⭐⭐⭐ (5/5) - 描述准确
  完整性: ⭐⭐⭐⭐ (4/5) - 缺少创建者等细节
  忠实度: ⭐⭐⭐⭐⭐ (5/5) - 基于文档，无幻觉
  简洁性: ⭐⭐⭐⭐⭐ (5/5) - 简洁明了

总分: 24/25 (96%)
    """)


# ==================== 示例3: RAGAS评估框架 ====================

def demo_ragas():
    """示例3: RAGAS评估框架"""
    print_section("示例3: RAGAS评估框架")

    print("RAGAS (RAG Assessment) 特点:")
    print("  ✓ 专门为RAG系统设计")
    print("  ✓ 自动化评估")
    print("  ✓ 多维度指标")
    print("  ✓ 无需ground truth\n")

    print("核心指标:\n")

    print("1. Context Relevance (上下文相关性)")
    print("   • 检索的文档是否相关")
    print("   • 评估检索质量\n")

    print("2. Faithfulness (忠实度)")
    print("   • 答案是否基于上下文")
    print("   • 检测幻觉\n")

    print("3. Answer Relevance (答案相关性)")
    print("   • 答案是否回答问题")
    print("   • 评估生成质量\n")

    print("4. Context Recall (上下文召回)")
    print("   • ground truth在检索中的覆盖")
    print("   • 需要标注数据\n")

    print("安装和使用:")
    print("""
# 安装
pip install ragas

# 使用
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_relevancy,
    context_recall
)

from datasets import Dataset

# 准备数据
data = {
    'question': ['什么是LangChain？'],
    'answer': ['LangChain是一个AI框架...'],
    'contexts': [['LangChain是...', '它提供了...']],
    'ground_truths': [['LangChain是一个开源框架...']]
}

dataset = Dataset.from_dict(data)

# 评估
results = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_relevancy,
        context_recall
    ]
)

print(results)
    """)

    print("\n示例输出:")
    print("""
{
    'faithfulness': 0.92,
    'answer_relevancy': 0.88,
    'context_relevancy': 0.85,
    'context_recall': 0.90
}
    """)

    print("\n解读:")
    print("  • faithfulness > 0.9: 答案可信，无明显幻觉")
    print("  • answer_relevancy > 0.8: 答案相关")
    print("  • context_relevancy > 0.8: 检索质量好")
    print("  • 综合评分: 良好\n")


# ==================== 示例4: 评估数据集构建 ====================

def demo_evaluation_dataset():
    """示例4: 评估数据集构建"""
    print_section("示例4: 评估数据集构建")

    print("评估数据集的重要性:")
    print("  ✓ 客观评估系统性能")
    print("  ✓ 对比不同配置")
    print("  ✓ 监控性能变化")
    print("  ✓ 发现问题案例\n")

    print("数据集结构:\n")

    print("""
evaluation_dataset = [
    {
        'id': 'q001',
        'question': '什么是LangChain？',
        'ground_truth': 'LangChain是一个开源框架，用于构建LLM应用...',
        'relevant_docs': ['doc_001', 'doc_003', 'doc_007'],
        'category': 'definition',
        'difficulty': 'easy'
    },
    {
        'id': 'q002',
        'question': 'LangChain和LlamaIndex有什么区别？',
        'ground_truth': 'LangChain更注重应用构建，LlamaIndex专注数据索引...',
        'relevant_docs': ['doc_012', 'doc_045'],
        'category': 'comparison',
        'difficulty': 'medium'
    },
    # ... 更多问题
]
    """)

    print("\n构建方法:\n")

    print("1. 手工标注（质量最高）")
    print("   • 领域专家创建问题")
    print("   • 标注相关文档")
    print("   • 编写标准答案")
    print("   • 数量: 50-200个\n")

    print("2. 从真实数据提取")
    print("   • 用户历史查询")
    print("   • FAQ问题")
    print("   • 客服记录")
    print("   • 后续人工审核\n")

    print("3. LLM辅助生成")
    print("""
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

# 从文档生成问题
doc_text = "LangChain是一个开源框架..."

prompt = f'''基于以下文档，生成5个问答对：

文档: {doc_text}

要求:
- 问题多样化（what, how, why）
- 难度分级（easy, medium, hard）
- 提供标准答案

输出JSON格式:
[{{"question": "...", "answer": "...", "difficulty": "easy"}}, ...]
'''

generated_qa = llm.predict(prompt)
    """)

    print("\n数据集质量检查:")
    print("  ✓ 问题清晰明确")
    print("  ✓ 答案准确完整")
    print("  ✓ 覆盖不同场景")
    print("  ✓ 难度分布合理")
    print("  ✓ 定期更新\n")


# ==================== 示例5: 自动化评估流程 ====================

def demo_automated_evaluation():
    """示例5: 自动化评估流程"""
    print_section("示例5: 自动化评估流程")

    print("自动化评估的价值:")
    print("  ✓ 快速迭代")
    print("  ✓ 持续监控")
    print("  ✓ 回归测试")
    print("  ✓ A/B测试\n")

    print("完整评估流程:")
    print("""
def evaluate_rag_system(qa_chain, eval_dataset: List[Dict]) -> Dict:
    '''自动化评估RAG系统'''

    results = []

    for item in eval_dataset:
        question = item['question']
        ground_truth = item['ground_truth']
        relevant_docs = item['relevant_docs']

        # 1. 执行查询
        result = qa_chain({'query': question})
        answer = result['result']
        retrieved_docs = [doc.metadata['id'] for doc in result['source_documents']]

        # 2. 评估检索
        retrieval_metrics = evaluate_retrieval(
            retrieved_docs,
            relevant_docs,
            k=5
        )

        # 3. 评估答案
        answer_metrics = evaluate_answer(
            question,
            answer,
            ground_truth,
            result['source_documents']
        )

        # 4. 记录结果
        results.append({
            'question_id': item['id'],
            'question': question,
            'answer': answer,
            **retrieval_metrics,
            **answer_metrics
        })

    # 5. 聚合统计
    summary = {
        'avg_precision': np.mean([r['precision@k'] for r in results]),
        'avg_recall': np.mean([r['recall@k'] for r in results]),
        'avg_relevance': np.mean([r['relevance'] for r in results]),
        'avg_faithfulness': np.mean([r['faithfulness'] for r in results])
    }

    return {
        'detailed_results': results,
        'summary': summary
    }

# 运行评估
eval_results = evaluate_rag_system(qa_chain, evaluation_dataset)

# 生成报告
generate_report(eval_results)
    """)

    print("\n持续评估（CI/CD集成）:")
    print("""
# .github/workflows/eval.yml
name: RAG Evaluation

on:
  pull_request:
  schedule:
    - cron: '0 0 * * *'  # 每天运行

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evaluation
        run: |
          python evaluate.py
          python compare_with_baseline.py

      - name: Comment Results
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '📊 Evaluation Results:\\n' + results
            })
    """)


# ==================== 示例6: 性能指标可视化 ====================

def demo_visualization():
    """示例6: 性能指标可视化"""
    print_section("示例6: 性能指标可视化")

    print("可视化的重要性:")
    print("  ✓ 直观展示性能")
    print("  ✓ 发现趋势")
    print("  ✓ 对比配置")
    print("  ✓ 沟通结果\n")

    print("常用图表:\n")

    print("1. 指标对比图")
    print("""
import matplotlib.pyplot as plt

metrics = ['Precision', 'Recall', 'F1', 'MRR']
config_a = [0.85, 0.72, 0.78, 0.80]
config_b = [0.88, 0.68, 0.77, 0.85]

x = range(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar([i - width/2 for i in x], config_a, width, label='Config A')
ax.bar([i + width/2 for i in x], config_b, width, label='Config B')

ax.set_ylabel('Score')
ax.set_title('RAG System Performance Comparison')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
plt.show()
    """)

    print("\n2. 时间序列图（监控性能变化）")
    print("""
import pandas as pd

# 历史数据
dates = pd.date_range('2024-01-01', periods=30, freq='D')
precision = np.random.normal(0.85, 0.05, 30)

plt.figure(figsize=(12, 6))
plt.plot(dates, precision, marker='o')
plt.axhline(y=0.80, color='r', linestyle='--', label='Threshold')
plt.xlabel('Date')
plt.ylabel('Precision@5')
plt.title('RAG Precision Over Time')
plt.legend()
plt.grid(True)
plt.show()
    """)

    print("\n3. 混淆矩阵（检索结果分析）")
    print("""
from sklearn.metrics import confusion_matrix
import seaborn as sns

# 示例数据
y_true = [1, 1, 0, 1, 0, 0, 1, 0]
y_pred = [1, 0, 0, 1, 0, 1, 1, 0]

cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Retrieval Confusion Matrix')
plt.show()
    """)

    print("\n4. 雷达图（多维度评估）")
    print("""
from math import pi

categories = ['Relevance', 'Accuracy', 'Completeness', 'Faithfulness', 'Conciseness']
values = [0.9, 0.85, 0.8, 0.95, 0.88]

angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
values += values[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
ax.plot(angles, values)
ax.fill(angles, values, alpha=0.25)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_ylim(0, 1)
plt.title('Answer Quality Assessment')
plt.show()
    """)


# ==================== 示例7: A/B测试 ====================

def demo_ab_testing():
    """示例7: A/B测试"""
    print_section("示例7: A/B测试")

    print("A/B测试场景:")
    print("  • 不同检索策略")
    print("  • 不同prompt模板")
    print("  • 不同参数配置")
    print("  • 不同模型\n")

    print("A/B测试流程:")
    print("""
def ab_test(config_a, config_b, test_dataset, n_iterations=5):
    '''A/B测试比较两个配置'''

    results_a = []
    results_b = []

    for _ in range(n_iterations):
        # 随机打乱数据
        shuffled = test_dataset.copy()
        random.shuffle(shuffled)

        # 测试配置A
        metrics_a = evaluate_config(config_a, shuffled)
        results_a.append(metrics_a)

        # 测试配置B
        metrics_b = evaluate_config(config_b, shuffled)
        results_b.append(metrics_b)

    # 统计检验
    from scipy import stats

    for metric in metrics_a[0].keys():
        scores_a = [r[metric] for r in results_a]
        scores_b = [r[metric] for r in results_b]

        # t检验
        t_stat, p_value = stats.ttest_ind(scores_a, scores_b)

        print(f"{metric}:")
        print(f"  Config A: {np.mean(scores_a):.3f} ± {np.std(scores_a):.3f}")
        print(f"  Config B: {np.mean(scores_b):.3f} ± {np.std(scores_b):.3f}")
        print(f"  p-value: {p_value:.4f}")
        if p_value < 0.05:
            winner = 'A' if np.mean(scores_a) > np.mean(scores_b) else 'B'
            print(f"  ✓ Config {winner} 显著更好\\n")
        else:
            print(f"  - 无显著差异\\n")

# 使用示例
config_a = {'retriever': 'similarity', 'k': 3}
config_b = {'retriever': 'mmr', 'k': 5}

ab_test(config_a, config_b, eval_dataset)
    """)

    print("\n示例输出:")
    print("""
Precision@5:
  Config A: 0.825 ± 0.032
  Config B: 0.867 ± 0.028
  p-value: 0.0123
  ✓ Config B 显著更好

Recall@5:
  Config A: 0.745 ± 0.041
  Config B: 0.732 ± 0.038
  p-value: 0.5432
  - 无显著差异

建议: 采用 Config B (MMR检索)
    """)


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 08: RAG评估")
    print("="*70)

    try:
        # 示例1: 检索指标
        demo_retrieval_metrics()

        # 示例2: 答案质量
        demo_answer_quality()

        # 示例3: RAGAS框架
        demo_ragas()

        # 示例4: 评估数据集
        demo_evaluation_dataset()

        # 示例5: 自动化评估
        demo_automated_evaluation()

        # 示例6: 可视化
        demo_visualization()

        # 示例7: A/B测试
        demo_ab_testing()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  关键要点:")
        print("    • 构建高质量评估数据集")
        print("    • 使用多维度指标")
        print("    • 自动化评估流程")
        print("    • 通过A/B测试优化")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
