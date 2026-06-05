"""
并行协作工作流
演示多个Agent同时分析文本的不同维度
"""

import os
import sys
import asyncio
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import (
    SentimentAnalysisAgent,
    KeywordExtractionAgent,
    SummaryAgent,
    EntityRecognitionAgent,
    TopicAnalysisAgent,
    AggregatorAgent
)


async def parallel_analysis(text: str) -> dict:
    """
    并行分析：多个Agent同时分析文本

    Args:
        text: 待分析的文本

    Returns:
        包含所有分析结果的字典
    """
    print("=" * 60)
    print("并行分析启动")
    print("=" * 60)
    print(f"文本长度: {len(text)} 字符\n")

    # 初始化LLM
    llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")

    # 创建所有Agent
    sentiment_agent = SentimentAnalysisAgent(llm)
    keyword_agent = KeywordExtractionAgent(llm)
    summary_agent = SummaryAgent(llm)
    entity_agent = EntityRecognitionAgent(llm)
    topic_agent = TopicAnalysisAgent(llm)

    # 记录开始时间
    start_time = time.time()

    print("[并行执行] 5个Agent同时开始分析...\n")

    # 并行执行所有分析任务
    results = await asyncio.gather(
        sentiment_agent.analyze(text),
        keyword_agent.extract(text),
        summary_agent.summarize(text),
        entity_agent.recognize(text),
        topic_agent.analyze_topic(text),
        return_exceptions=True  # 捕获异常而不中断其他任务
    )

    # 计算执行时间
    elapsed_time = time.time() - start_time
    print(f"\n⏱ 并行执行完成，用时: {elapsed_time:.2f} 秒\n")

    # 组织结果
    analysis_results = {
        "情感分析": results[0] if not isinstance(results[0], Exception) else f"错误: {results[0]}",
        "关键词提取": results[1] if not isinstance(results[1], Exception) else f"错误: {results[1]}",
        "内容摘要": results[2] if not isinstance(results[2], Exception) else f"错误: {results[2]}",
        "实体识别": results[3] if not isinstance(results[3], Exception) else f"错误: {results[3]}",
        "主题分析": results[4] if not isinstance(results[4], Exception) else f"错误: {results[4]}",
    }

    return analysis_results


async def parallel_workflow(text: str) -> str:
    """
    完整的并行工作流：分析 + 聚合

    Args:
        text: 待分析的文本

    Returns:
        综合分析报告
    """
    # 步骤1: 并行分析
    print("\n[步骤 1/2] 并行分析")
    print("-" * 60)
    analysis_results = await parallel_analysis(text)

    # 打印各项分析结果预览
    print("\n分析结果预览:")
    for key, value in analysis_results.items():
        print(f"\n【{key}】")
        preview = value[:200] + "..." if len(value) > 200 else value
        print(preview)

    # 步骤2: 聚合结果
    print("\n\n[步骤 2/2] 聚合结果")
    print("-" * 60)
    aggregator = AggregatorAgent(ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo"))
    final_report = aggregator.aggregate(analysis_results)

    print("\n" + "=" * 60)
    print("并行工作流完成")
    print("=" * 60)

    return final_report


async def selective_parallel_analysis(text: str, tasks: list) -> dict:
    """
    选择性并行分析：只执行指定的分析任务

    Args:
        text: 待分析的文本
        tasks: 要执行的任务列表，如 ['sentiment', 'keywords', 'summary']

    Returns:
        包含选定分析结果的字典
    """
    llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")

    # 任务映射
    task_map = {
        'sentiment': ('情感分析', SentimentAnalysisAgent(llm).analyze),
        'keywords': ('关键词提取', KeywordExtractionAgent(llm).extract),
        'summary': ('内容摘要', SummaryAgent(llm).summarize),
        'entities': ('实体识别', EntityRecognitionAgent(llm).recognize),
        'topic': ('主题分析', TopicAnalysisAgent(llm).analyze_topic),
    }

    # 准备要执行的任务
    selected_tasks = []
    task_names = []

    for task in tasks:
        if task in task_map:
            task_names.append(task_map[task][0])
            selected_tasks.append(task_map[task][1](text))

    print(f"[选择性并行] 执行 {len(selected_tasks)} 个任务: {', '.join(task_names)}\n")

    # 并行执行
    start_time = time.time()
    results = await asyncio.gather(*selected_tasks, return_exceptions=True)
    elapsed_time = time.time() - start_time

    print(f"\n⏱ 执行完成，用时: {elapsed_time:.2f} 秒\n")

    # 组织结果
    analysis_results = {}
    for i, task in enumerate(tasks):
        if task in task_map:
            name = task_map[task][0]
            analysis_results[name] = results[i] if not isinstance(results[i], Exception) else f"错误: {results[i]}"

    return analysis_results


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 测试文本
    test_text = """
人工智能（Artificial Intelligence, AI）正在深刻改变我们的世界。从自动驾驶汽车到智能助手，
AI技术已经渗透到日常生活的方方面面。

在企业领域，AI Agent系统展现出巨大的潜力。这些智能代理不仅能够自主完成复杂任务，
还能相互协作，形成强大的多Agent系统。例如，在客户服务领域，多个AI Agent可以并行处理
不同类型的客户咨询，大幅提升服务效率。

然而，AI技术的发展也带来了一些挑战。数据隐私、算法偏见、就业影响等问题需要我们认真对待。
正如图灵奖得主Yoshua Bengio所说："我们需要确保AI技术的发展符合人类的价值观和利益。"

展望未来，AI与人类的协作将成为常态。关键是要建立合理的监管框架，确保技术向善发展。
只有这样，我们才能充分发挥AI的潜力，创造一个更美好的未来。
    """.strip()

    # 示例1: 完整并行分析
    print("\n" + "🔷" * 30)
    print("示例 1: 完整并行分析工作流")
    print("🔷" * 30)

    try:
        final_report = asyncio.run(parallel_workflow(test_text))

        print(f"\n\n📊 综合分析报告:\n")
        print("=" * 60)
        print(final_report)
        print("=" * 60)

        # 保存结果
        output_file = "parallel_output_full.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("原始文本:\n")
            f.write("=" * 60 + "\n")
            f.write(test_text + "\n\n")
            f.write("综合分析报告:\n")
            f.write("=" * 60 + "\n")
            f.write(final_report)
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 选择性并行分析
    print("\n\n" + "🔷" * 30)
    print("示例 2: 选择性并行分析")
    print("🔷" * 30)

    try:
        # 只执行情感分析、关键词提取和摘要
        selected_results = asyncio.run(
            selective_parallel_analysis(test_text, ['sentiment', 'keywords', 'summary'])
        )

        print("\n📊 选择性分析结果:\n")
        for key, value in selected_results.items():
            print(f"\n【{key}】")
            print("-" * 60)
            print(value)

        # 保存结果
        output_file = "parallel_output_selective.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("选择性并行分析结果\n")
            f.write("=" * 60 + "\n\n")
            for key, value in selected_results.items():
                f.write(f"【{key}】\n")
                f.write(value + "\n\n")
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
