"""
CrewAI框架示例
演示使用CrewAI实现多Agent协作
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# 注意：CrewAI需要单独安装
# pip install crewai crewai-tools

try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("⚠ CrewAI未安装，请运行: pip install crewai crewai-tools")


def crewai_research_team(topic: str) -> str:
    """
    CrewAI研究团队示例

    Args:
        topic: 研究主题

    Returns:
        研究结果
    """
    if not CREWAI_AVAILABLE:
        return "CrewAI未安装，无法运行示例"

    print("=" * 60)
    print("CrewAI 研究团队示例")
    print("=" * 60)
    print(f"研究主题: {topic}\n")

    try:
        # 创建研究员Agent
        researcher = Agent(
            role='资深研究员',
            goal=f'深入研究{topic}，收集全面的信息',
            backstory="""你是一位经验丰富的研究员，擅长信息收集和分析。
            你总是能找到最相关和最新的信息。""",
            verbose=True,
            allow_delegation=False
        )

        # 创建分析师Agent
        analyst = Agent(
            role='数据分析师',
            goal='分析研究数据，提取关键洞察',
            backstory="""你是一位专业的数据分析师，擅长从大量信息中
            提取有价值的洞察和趋势。""",
            verbose=True,
            allow_delegation=False
        )

        # 创建撰写者Agent
        writer = Agent(
            role='技术写作者',
            goal='撰写清晰、专业的研究报告',
            backstory="""你是一位经验丰富的技术写作者，擅长将复杂的
            技术内容转化为易于理解的文档。""",
            verbose=True,
            allow_delegation=False
        )

        # 定义任务
        research_task = Task(
            description=f"""研究{topic}，包括：
            1. 核心概念和定义
            2. 当前发展状况
            3. 主要应用场景
            4. 技术挑战和机遇

            提供详细的研究报告。""",
            agent=researcher,
            expected_output="详细的研究报告，包含所有要求的内容"
        )

        analysis_task = Task(
            description="""分析研究结果，提取关键洞察：
            1. 识别主要趋势
            2. 分析优势和劣势
            3. 提供数据支持的结论

            生成分析报告。""",
            agent=analyst,
            expected_output="分析报告，包含关键洞察和数据支持的结论"
        )

        writing_task = Task(
            description="""基于研究和分析结果，撰写最终报告：
            1. 执行摘要
            2. 详细分析
            3. 结论和建议

            报告应结构清晰、内容专业。""",
            agent=writer,
            expected_output="完整的专业报告，结构清晰，内容全面"
        )

        # 组建团队
        crew = Crew(
            agents=[researcher, analyst, writer],
            tasks=[research_task, analysis_task, writing_task],
            process=Process.sequential,  # 顺序执行
            verbose=True
        )

        # 执行
        print("\n开始执行...\n")
        result = crew.kickoff()

        print("\n✓ 执行完成")
        return str(result)

    except Exception as e:
        error_msg = f"CrewAI执行出错: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def crewai_content_creation(topic: str) -> str:
    """
    CrewAI内容创作团队示例

    Args:
        topic: 内容主题

    Returns:
        创作结果
    """
    if not CREWAI_AVAILABLE:
        return "CrewAI未安装，无法运行示例"

    print("=" * 60)
    print("CrewAI 内容创作团队示例")
    print("=" * 60)
    print(f"内容主题: {topic}\n")

    try:
        # 创建内容策划Agent
        planner = Agent(
            role='内容策划师',
            goal=f'为{topic}制定内容策略',
            backstory="""你是一位资深的内容策划师，擅长理解受众需求
            并制定有效的内容策略。""",
            verbose=True,
            allow_delegation=True
        )

        # 创建写作者Agent
        writer = Agent(
            role='内容创作者',
            goal='创作高质量、引人入胜的内容',
            backstory="""你是一位才华横溢的内容创作者，擅长讲故事
            和吸引读者注意力。""",
            verbose=True,
            allow_delegation=False
        )

        # 创建编辑Agent
        editor = Agent(
            role='内容编辑',
            goal='确保内容质量和一致性',
            backstory="""你是一位严谨的编辑，对细节有极高的要求，
            总能发现需要改进的地方。""",
            verbose=True,
            allow_delegation=False
        )

        # 定义任务
        planning_task = Task(
            description=f"""为{topic}制定内容计划：
            1. 确定目标受众
            2. 规划内容结构
            3. 制定关键信息点
            4. 确定内容风格

            提供详细的内容策略。""",
            agent=planner,
            expected_output="详细的内容策略文档"
        )

        writing_task = Task(
            description="""根据内容策略创作文章：
            1. 引人入胜的开头
            2. 结构清晰的正文
            3. 有力的结尾
            4. 包含实例和案例

            创作800-1000字的文章。""",
            agent=writer,
            expected_output="完整的文章草稿，800-1000字"
        )

        editing_task = Task(
            description="""编辑和优化文章：
            1. 检查语法和拼写
            2. 优化结构和流畅度
            3. 确保信息准确性
            4. 提升可读性

            提供最终版本。""",
            agent=editor,
            expected_output="经过编辑优化的最终文章"
        )

        # 组建团队
        crew = Crew(
            agents=[planner, writer, editor],
            tasks=[planning_task, writing_task, editing_task],
            process=Process.sequential,
            verbose=True
        )

        # 执行
        print("\n开始创作...\n")
        result = crew.kickoff()

        print("\n✓ 创作完成")
        return str(result)

    except Exception as e:
        error_msg = f"CrewAI执行出错: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def crewai_problem_solving(problem: str) -> str:
    """
    CrewAI问题解决团队示例

    Args:
        problem: 问题描述

    Returns:
        解决方案
    """
    if not CREWAI_AVAILABLE:
        return "CrewAI未安装，无法运行示例"

    print("=" * 60)
    print("CrewAI 问题解决团队示例")
    print("=" * 60)
    print(f"问题: {problem}\n")

    try:
        # 创建问题分析师
        analyst = Agent(
            role='问题分析师',
            goal='深入分析问题，识别根本原因',
            backstory="""你是一位经验丰富的问题分析专家，擅长将复杂
            问题分解为可管理的部分。""",
            verbose=True,
            allow_delegation=False
        )

        # 创建解决方案架构师
        architect = Agent(
            role='解决方案架构师',
            goal='设计可行的解决方案',
            backstory="""你是一位资深架构师，擅长设计创新且实用的
            解决方案。""",
            verbose=True,
            allow_delegation=False
        )

        # 创建实施顾问
        consultant = Agent(
            role='实施顾问',
            goal='提供实施指导和最佳实践',
            backstory="""你是一位实施专家，拥有丰富的项目经验，
            知道如何将方案落地。""",
            verbose=True,
            allow_delegation=False
        )

        # 定义任务
        analysis_task = Task(
            description=f"""分析以下问题：{problem}

            提供：
            1. 问题的根本原因
            2. 影响范围
            3. 约束条件
            4. 关键考虑因素""",
            agent=analyst,
            expected_output="详细的问题分析报告"
        )

        solution_task = Task(
            description="""基于问题分析，设计解决方案：
            1. 提出2-3个候选方案
            2. 分析每个方案的优劣
            3. 推荐最佳方案
            4. 提供架构设计""",
            agent=architect,
            expected_output="解决方案设计文档，包含架构图和技术选型"
        )

        implementation_task = Task(
            description="""制定实施计划：
            1. 实施步骤
            2. 资源需求
            3. 时间线
            4. 风险和缓解措施
            5. 成功指标""",
            agent=consultant,
            expected_output="详细的实施计划和指南"
        )

        # 组建团队
        crew = Crew(
            agents=[analyst, architect, consultant],
            tasks=[analysis_task, solution_task, implementation_task],
            process=Process.sequential,
            verbose=True
        )

        # 执行
        print("\n开始解决问题...\n")
        result = crew.kickoff()

        print("\n✓ 问题解决完成")
        return str(result)

    except Exception as e:
        error_msg = f"CrewAI执行出错: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def main():
    """主函数"""
    load_dotenv()

    if not CREWAI_AVAILABLE:
        print("=" * 60)
        print("CrewAI未安装")
        print("=" * 60)
        print("\n请运行以下命令安装:")
        print("  pip install crewai crewai-tools")
        print("\n安装后重新运行此脚本。")
        return

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例1: 研究团队
    print("\n" + "🔷" * 30)
    print("示例 1: 研究团队")
    print("🔷" * 30)

    try:
        result1 = crewai_research_team("多Agent系统的协作模式")

        # 保存结果
        output_file = "crewai_research_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("CrewAI研究团队结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(result1)

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 内容创作团队
    print("\n\n" + "🔷" * 30)
    print("示例 2: 内容创作团队")
    print("🔷" * 30)

    try:
        result2 = crewai_content_creation("AI Agent在企业中的应用")

        # 保存结果
        output_file = "crewai_content_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("CrewAI内容创作结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(result2)

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例3: 问题解决团队
    print("\n\n" + "🔷" * 30)
    print("示例 3: 问题解决团队")
    print("🔷" * 30)

    try:
        result3 = crewai_problem_solving(
            "如何优化大规模分布式系统的性能和可靠性？"
        )

        # 保存结果
        output_file = "crewai_solution_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("CrewAI问题解决结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(result3)

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
