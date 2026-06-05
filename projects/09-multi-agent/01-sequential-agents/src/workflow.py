"""
顺序协作工作流
演示研究员 -> 写作者 -> 编辑的完整流程
"""

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import ResearchAgent, WriterAgent, EditorAgent


def sequential_workflow(topic: str) -> str:
    """
    简单的顺序工作流：研究 -> 写作 -> 编辑

    Args:
        topic: 文章主题

    Returns:
        最终完成的文章
    """
    print("=" * 60)
    print("顺序协作工作流启动")
    print("=" * 60)
    print(f"主题: {topic}\n")

    # 初始化LLM（所有Agent共享）
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 阶段1：研究
    print("\n[阶段 1/3] 研究阶段")
    print("-" * 60)
    researcher = ResearchAgent(llm)
    research_result = researcher.research(topic)
    print(f"\n研究结果预览:\n{research_result[:300]}...\n")

    # 阶段2：写作
    print("\n[阶段 2/3] 写作阶段")
    print("-" * 60)
    writer = WriterAgent(llm)
    draft = writer.write(research_result)
    print(f"\n文章草稿预览:\n{draft[:300]}...\n")

    # 阶段3：编辑
    print("\n[阶段 3/3] 编辑阶段")
    print("-" * 60)
    editor = EditorAgent(llm)
    final_article = editor.edit(draft)
    print(f"\n最终文章:\n{final_article}\n")

    print("=" * 60)
    print("工作流完成")
    print("=" * 60)

    return final_article


def sequential_with_feedback(topic: str, max_iterations: int = 3) -> str:
    """
    带反馈循环的顺序协作：如果编辑不满意，会要求重新研究和写作

    Args:
        topic: 文章主题
        max_iterations: 最大迭代次数

    Returns:
        最终完成的文章
    """
    print("=" * 60)
    print("带反馈的顺序协作工作流启动")
    print("=" * 60)
    print(f"主题: {topic}")
    print(f"最大迭代次数: {max_iterations}\n")

    # 初始化Agents
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    researcher = ResearchAgent(llm)
    writer = WriterAgent(llm)
    editor = EditorAgent(llm)

    # 初始研究
    print("\n[初始研究]")
    print("-" * 60)
    research_result = researcher.research(topic)
    print(f"研究完成，字数: {len(research_result)}")

    # 迭代改进
    for iteration in range(max_iterations):
        print(f"\n{'=' * 60}")
        print(f"迭代 {iteration + 1}/{max_iterations}")
        print("=" * 60)

        # 写作
        print("\n[写作]")
        draft = writer.write(research_result)
        print(f"草稿完成，字数: {len(draft)}")

        # 编辑审查
        print("\n[编辑审查]")
        edited, feedback = editor.edit_with_feedback(draft)

        print(f"\n审查结果:")
        print(f"  - 是否通过: {feedback.get('approved', False)}")
        print(f"  - 评分: {feedback.get('score', 0)}/100")

        if feedback.get('issues'):
            print(f"  - 问题: {', '.join(feedback['issues'])}")

        if feedback.get('suggestions'):
            print(f"  - 建议: {', '.join(feedback['suggestions'])}")

        # 如果通过审查，完成任务
        if feedback.get("approved", False):
            print(f"\n✓ 审查通过！最终评分: {feedback.get('score', 0)}/100")
            print("=" * 60)
            return edited

        # 根据反馈补充研究
        if feedback.get('missing_info'):
            print(f"\n[补充研究] {feedback['missing_info']}")
            additional_research = researcher.research(feedback['missing_info'])
            research_result += f"\n\n补充信息:\n{additional_research}"

    print("\n⚠ 达到最大迭代次数，返回当前版本")
    print("=" * 60)
    return edited


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例1: 简单顺序工作流
    print("\n" + "🔷" * 30)
    print("示例 1: 简单顺序工作流")
    print("🔷" * 30)

    topic1 = "AI Agent在企业中的应用"
    try:
        article1 = sequential_workflow(topic1)

        # 保存结果
        output_file = "sequential_output_simple.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"主题: {topic1}\n\n")
            f.write(article1)
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 带反馈的顺序工作流
    print("\n\n" + "🔷" * 30)
    print("示例 2: 带反馈的顺序工作流")
    print("🔷" * 30)

    topic2 = "多Agent协作系统的设计模式"
    try:
        article2 = sequential_with_feedback(topic2, max_iterations=2)

        # 保存结果
        output_file = "sequential_output_feedback.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"主题: {topic2}\n\n")
            f.write(article2)
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
