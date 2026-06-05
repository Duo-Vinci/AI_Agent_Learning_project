"""
层级协作工作流
演示Manager-Worker模式的完整流程
"""

import os
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import ManagerAgent, WorkerAgent


def create_development_team(llm: ChatOpenAI) -> ManagerAgent:
    """
    创建软件开发团队

    Args:
        llm: 语言模型实例

    Returns:
        配置好的Manager Agent
    """
    print("\n组建开发团队...")
    print("=" * 60)

    # 创建Manager
    manager = ManagerAgent(llm)

    # 创建不同专业的Workers
    researcher = WorkerAgent("研究员Alice", ["research", "analysis", "documentation"], llm)
    developer = WorkerAgent("开发者Bob", ["coding", "debugging", "testing"], llm)
    designer = WorkerAgent("设计师Carol", ["ui_design", "ux_design", "prototyping"], llm)
    writer = WorkerAgent("技术作家David", ["writing", "documentation", "tutorial"], llm)

    # 添加到团队
    manager.add_worker(researcher)
    manager.add_worker(developer)
    manager.add_worker(designer)
    manager.add_worker(writer)

    print("=" * 60)
    return manager


def create_content_team(llm: ChatOpenAI) -> ManagerAgent:
    """
    创建内容创作团队

    Args:
        llm: 语言模型实例

    Returns:
        配置好的Manager Agent
    """
    print("\n组建内容团队...")
    print("=" * 60)

    # 创建Manager
    manager = ManagerAgent(llm)

    # 创建不同角色的Workers
    researcher = WorkerAgent("研究专员Emma", ["research", "fact_checking", "analysis"], llm)
    writer = WorkerAgent("内容作家Frank", ["writing", "storytelling", "editing"], llm)
    seo_specialist = WorkerAgent("SEO专家Grace", ["seo", "keywords", "optimization"], llm)
    editor = WorkerAgent("编辑Henry", ["editing", "proofreading", "quality_control"], llm)

    # 添加到团队
    manager.add_worker(researcher)
    manager.add_worker(writer)
    manager.add_worker(seo_specialist)
    manager.add_worker(editor)

    print("=" * 60)
    return manager


def hierarchical_workflow(task: str, team_type: str = "development") -> str:
    """
    层级协作工作流

    Args:
        task: 主任务描述
        team_type: 团队类型 ("development" 或 "content")

    Returns:
        最终结果
    """
    print("\n" + "=" * 60)
    print("层级协作工作流启动")
    print("=" * 60)
    print(f"任务: {task}")
    print(f"团队类型: {team_type}\n")

    # 初始化LLM
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 根据类型创建团队
    if team_type == "development":
        manager = create_development_team(llm)
    elif team_type == "content":
        manager = create_content_team(llm)
    else:
        raise ValueError(f"未知的团队类型: {team_type}")

    # 执行任务
    result = manager.execute_plan(task)

    # 显示团队状态
    print("\n\n团队工作总结:")
    print("=" * 60)
    team_status = manager.get_team_status()
    print(f"经理: {team_status['manager']}")
    print(f"团队成员: {team_status['total_workers']} 人")
    print("\n各成员完成情况:")
    for worker_status in team_status['workers']:
        print(f"  - {worker_status['name']}: 完成 {worker_status['completed_tasks']} 个任务")
        print(f"    技能: {', '.join(worker_status['skills'])}")

    print("=" * 60)

    return result


def multi_project_workflow(projects: list) -> dict:
    """
    多项目协作：同一个团队处理多个项目

    Args:
        projects: 项目列表，每个项目是一个字典 {'name': '', 'task': '', 'team_type': ''}

    Returns:
        所有项目的结果字典
    """
    print("\n" + "=" * 60)
    print("多项目协作工作流")
    print("=" * 60)
    print(f"项目数量: {len(projects)}\n")

    results = {}
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    for i, project in enumerate(projects, 1):
        print(f"\n\n{'#' * 60}")
        print(f"项目 {i}/{len(projects)}: {project['name']}")
        print('#' * 60)

        # 创建团队
        if project.get('team_type') == "development":
            manager = create_development_team(llm)
        else:
            manager = create_content_team(llm)

        # 执行项目
        result = manager.execute_plan(project['task'])
        results[project['name']] = result

        print(f"\n✓ 项目 '{project['name']}' 完成")

    return results


def dynamic_team_workflow(task: str, required_skills: list) -> str:
    """
    动态团队组建：根据任务需求动态组建团队

    Args:
        task: 任务描述
        required_skills: 所需技能列表

    Returns:
        执行结果
    """
    print("\n" + "=" * 60)
    print("动态团队组建工作流")
    print("=" * 60)
    print(f"任务: {task}")
    print(f"所需技能: {', '.join(required_skills)}\n")

    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建Manager
    manager = ManagerAgent(llm)

    # 技能到Worker的映射（模拟人才库）
    talent_pool = {
        'research': WorkerAgent("研究专家", ["research", "analysis"], llm),
        'coding': WorkerAgent("程序员", ["coding", "debugging"], llm),
        'design': WorkerAgent("设计师", ["ui_design", "ux_design"], llm),
        'writing': WorkerAgent("作家", ["writing", "editing"], llm),
        'testing': WorkerAgent("测试工程师", ["testing", "qa"], llm),
        'documentation': WorkerAgent("文档工程师", ["documentation", "technical_writing"], llm),
    }

    # 根据所需技能组建团队
    print("从人才库中选择合适的成员:")
    for skill in required_skills:
        if skill in talent_pool:
            worker = talent_pool[skill]
            manager.add_worker(worker)

    # 如果没有匹配的技能，添加通用Worker
    if len(manager.workers) == 0:
        print("⚠ 没有完全匹配的技能，添加通用Worker")
        general_worker = WorkerAgent("全能型员工", required_skills, llm)
        manager.add_worker(general_worker)

    print()

    # 执行任务
    result = manager.execute_plan(task)

    return result


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例1: 开发团队工作流
    print("\n" + "🔷" * 30)
    print("示例 1: 软件开发团队")
    print("🔷" * 30)

    task1 = "开发一个AI驱动的客户服务聊天机器人系统"
    try:
        result1 = hierarchical_workflow(task1, team_type="development")

        # 保存结果
        output_file = "hierarchical_output_dev.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"任务: {task1}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result1)
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 内容团队工作流
    print("\n\n" + "🔷" * 30)
    print("示例 2: 内容创作团队")
    print("🔷" * 30)

    task2 = "创作一篇关于'AI Agent技术趋势'的深度文章，需要SEO优化"
    try:
        result2 = hierarchical_workflow(task2, team_type="content")

        # 保存结果
        output_file = "hierarchical_output_content.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"任务: {task2}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result2)
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例3: 动态团队组建
    print("\n\n" + "🔷" * 30)
    print("示例 3: 动态团队组建")
    print("🔷" * 30)

    task3 = "设计并实现一个用户仪表板，包含数据可视化功能"
    required_skills = ["research", "design", "coding", "documentation"]

    try:
        result3 = dynamic_team_workflow(task3, required_skills)

        # 保存结果
        output_file = "hierarchical_output_dynamic.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"任务: {task3}\n")
            f.write(f"所需技能: {', '.join(required_skills)}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result3)
        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
