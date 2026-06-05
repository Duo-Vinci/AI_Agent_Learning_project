"""
代码审查团队工作流
演示基于共享记忆的多Agent协作
"""

import os
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shared_memory import SharedMemory, MemoryAwareAgent


def code_review_workflow(code_snippet: str):
    """
    代码审查工作流：多个审查员共享发现和决策

    Args:
        code_snippet: 待审查的代码
    """
    print("=" * 60)
    print("代码审查团队工作流")
    print("=" * 60)
    print(f"代码长度: {len(code_snippet)} 字符\n")

    # 创建共享记忆
    shared_memory = SharedMemory()

    # 创建LLM
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建审查团队
    security_reviewer = MemoryAwareAgent("安全审查员", shared_memory, llm)
    performance_reviewer = MemoryAwareAgent("性能审查员", shared_memory, llm)
    quality_reviewer = MemoryAwareAgent("质量审查员", shared_memory, llm)

    # 步骤1: 记录待审查代码
    print("[步骤 1/4] 记录待审查代码")
    print("-" * 60)
    shared_memory.add_fact("code_to_review", code_snippet, "System")
    shared_memory.add_fact("review_status", "in_progress", "System")
    shared_memory.add_context(f"开始审查代码，长度: {len(code_snippet)} 字符")

    # 步骤2: 各审查员独立审查
    print("\n[步骤 2/4] 独立审查")
    print("-" * 60)

    print("\n[安全审查员] 审查中...")
    security_result = security_reviewer.execute_with_context(
        f"从安全角度审查以下代码，识别潜在的安全漏洞：\n{code_snippet}"
    )
    print(f"审查结果: {security_result[:150]}...")

    # 记录发现
    if "漏洞" in security_result or "风险" in security_result:
        security_reviewer.contribute_knowledge("security_issues_found", True, confidence=0.8)
        security_reviewer.make_decision(
            "sec_001",
            "发现安全问题",
            "代码中存在潜在的安全风险"
        )

    print("\n[性能审查员] 审查中...")
    performance_result = performance_reviewer.execute_with_context(
        f"从性能角度审查以下代码，识别性能瓶颈：\n{code_snippet}"
    )
    print(f"审查结果: {performance_result[:150]}...")

    # 记录发现
    if "优化" in performance_result or "性能" in performance_result:
        performance_reviewer.contribute_knowledge("performance_issues_found", True, confidence=0.7)
        performance_reviewer.make_decision(
            "perf_001",
            "发现性能问题",
            "代码存在可优化的性能问题"
        )

    print("\n[质量审查员] 审查中...")
    quality_result = quality_reviewer.execute_with_context(
        f"从代码质量角度审查以下代码，检查可读性、可维护性：\n{code_snippet}"
    )
    print(f"审查结果: {quality_result[:150]}...")

    # 记录发现
    quality_reviewer.contribute_knowledge("quality_review_complete", True, confidence=0.9)

    # 步骤3: 综合审查意见
    print("\n\n[步骤 3/4] 综合审查意见")
    print("-" * 60)

    # 质量审查员基于所有发现生成综合报告
    synthesis_task = """基于团队的审查发现，生成一份综合审查报告。报告应包括：
1. 安全方面的发现和建议
2. 性能方面的发现和建议
3. 代码质量方面的发现和建议
4. 综合评价和优先级建议"""

    comprehensive_report = quality_reviewer.collaborate_with_memory(
        synthesis_task,
        use_facts=True,
        use_decisions=True
    )

    print("\n📊 综合审查报告:")
    print("=" * 60)
    print(comprehensive_report)
    print("=" * 60)

    # 步骤4: 做出最终决策
    print("\n\n[步骤 4/4] 最终决策")
    print("-" * 60)

    # 检查是否有严重问题
    security_issues = shared_memory.get_fact("security_issues_found")
    performance_issues = shared_memory.get_fact("performance_issues_found")

    if security_issues:
        quality_reviewer.make_decision(
            "final_001",
            "代码需要修改",
            "存在安全问题，必须修复后才能合并"
        )
        shared_memory.update_fact("review_status", "rejected", "质量审查员")
        print("❌ 审查结论: 代码需要修改（存在安全问题）")
    elif performance_issues:
        quality_reviewer.make_decision(
            "final_001",
            "建议优化后合并",
            "存在性能问题，建议优化但不阻塞合并"
        )
        shared_memory.update_fact("review_status", "approved_with_suggestions", "质量审查员")
        print("⚠️ 审查结论: 建议优化后合并")
    else:
        quality_reviewer.make_decision(
            "final_001",
            "批准合并",
            "代码质量良好，无重大问题"
        )
        shared_memory.update_fact("review_status", "approved", "质量审查员")
        print("✅ 审查结论: 批准合并")

    # 显示共享记忆摘要
    print("\n\n📈 共享记忆摘要:")
    summary = shared_memory.get_summary()
    print(f"事实数量: {summary['total_facts']}")
    print(f"上下文条数: {summary['total_context']}")
    print(f"决策数量: {summary['total_decisions']}")

    print("\n记录的事实:")
    for key, fact in shared_memory.facts.items():
        print(f"  - {key}: {fact.value} (来源: {fact.source}, 置信度: {fact.confidence})")

    print("\n决策历史:")
    for decision in shared_memory.decisions:
        print(f"  - {decision.decision_id}: {decision.description} (by {decision.made_by})")

    return {
        'security_review': security_result,
        'performance_review': performance_result,
        'quality_review': quality_result,
        'comprehensive_report': comprehensive_report,
        'final_status': shared_memory.get_fact("review_status"),
        'memory_summary': summary
    }


def collaborative_problem_solving():
    """
    协作问题解决：多个Agent共享知识解决问题
    """
    print("=" * 60)
    print("协作问题解决工作流")
    print("=" * 60)

    # 创建共享记忆
    shared_memory = SharedMemory()
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建问题解决团队
    analyst = MemoryAwareAgent("问题分析师", shared_memory, llm)
    researcher = MemoryAwareAgent("研究员", shared_memory, llm)
    architect = MemoryAwareAgent("架构师", shared_memory, llm)

    problem = "设计一个高可用、高性能的分布式缓存系统"

    # 步骤1: 分析问题
    print("\n[步骤 1/3] 问题分析")
    print("-" * 60)

    analysis = analyst.execute_with_context(
        f"分析以下问题，识别关键需求和挑战：{problem}"
    )
    print(f"\n分析结果: {analysis[:200]}...")

    # 记录关键需求
    analyst.contribute_knowledge("key_requirements", "高可用、高性能、分布式", confidence=0.9)
    analyst.contribute_knowledge("problem_domain", "缓存系统", confidence=1.0)

    # 步骤2: 研究解决方案
    print("\n\n[步骤 2/3] 研究解决方案")
    print("-" * 60)

    research = researcher.collaborate_with_memory(
        "基于已识别的需求，研究可行的技术方案和最佳实践"
    )
    print(f"\n研究结果: {research[:200]}...")

    # 记录技术选型
    researcher.contribute_knowledge("suggested_technologies", "Redis Cluster, Memcached", confidence=0.8)
    researcher.make_decision(
        "tech_001",
        "推荐使用Redis Cluster",
        "Redis Cluster提供了内置的分片和高可用性支持"
    )

    # 步骤3: 设计架构
    print("\n\n[步骤 3/3] 架构设计")
    print("-" * 60)

    architecture = architect.collaborate_with_memory(
        "基于团队的分析和研究，设计详细的系统架构",
        use_facts=True,
        use_decisions=True
    )
    print(f"\n架构设计:\n{architecture}")

    # 最终决策
    architect.make_decision(
        "arch_001",
        "采用三层架构设计",
        "客户端层、缓存层、持久化层的分层设计提供了良好的可扩展性"
    )

    # 导出状态
    print("\n\n📊 项目状态导出:")
    state = shared_memory.export_state()
    print(json.dumps(state, ensure_ascii=False, indent=2))

    return architecture


def incremental_knowledge_building():
    """
    增量知识构建：Agent逐步积累和完善知识
    """
    print("=" * 60)
    print("增量知识构建工作流")
    print("=" * 60)

    # 创建共享记忆
    shared_memory = SharedMemory()
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建学习Agent
    learner1 = MemoryAwareAgent("学习者A", shared_memory, llm)
    learner2 = MemoryAwareAgent("学习者B", shared_memory, llm)
    learner3 = MemoryAwareAgent("学习者C", shared_memory, llm)

    topics = [
        ("AI Agent的定义", learner1),
        ("AI Agent的核心能力", learner2),
        ("AI Agent的应用场景", learner3),
        ("AI Agent的技术挑战", learner1),
        ("AI Agent的未来趋势", learner2)
    ]

    print("\n逐步学习和积累知识...\n")

    for i, (topic, learner) in enumerate(topics, 1):
        print(f"[轮次 {i}/{len(topics)}] {learner.agent_id} 学习: {topic}")
        print("-" * 60)

        result = learner.collaborate_with_memory(
            f"学习并总结关于'{topic}'的知识，参考已有的知识库"
        )

        # 贡献知识
        learner.contribute_knowledge(f"knowledge_{i}", result[:100], confidence=0.8)

        print(f"✓ 知识已添加\n")

    # 最终综合
    print("\n[最终综合] 生成完整知识库")
    print("=" * 60)

    final_summary = learner1.collaborate_with_memory(
        "综合所有学到的知识，生成一份完整的'AI Agent技术'知识库"
    )

    print(f"\n📚 知识库:\n{final_summary}")

    return final_summary


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例代码
    sample_code = """
def process_user_data(user_input):
    # 直接执行用户输入
    result = eval(user_input)

    # 将结果存入全局变量
    global user_data
    user_data = result

    # 返回处理结果
    return result
"""

    # 示例1: 代码审查工作流
    print("\n" + "🔷" * 30)
    print("示例 1: 代码审查团队协作")
    print("🔷" * 30)

    try:
        result1 = code_review_workflow(sample_code)

        # 保存结果
        output_file = "code_review_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("代码审查结果\n")
            f.write("=" * 60 + "\n\n")
            f.write("待审查代码:\n")
            f.write(sample_code + "\n\n")
            f.write("=" * 60 + "\n\n")
            f.write("安全审查:\n")
            f.write(result1['security_review'] + "\n\n")
            f.write("性能审查:\n")
            f.write(result1['performance_review'] + "\n\n")
            f.write("质量审查:\n")
            f.write(result1['quality_review'] + "\n\n")
            f.write("=" * 60 + "\n\n")
            f.write("综合审查报告:\n")
            f.write(result1['comprehensive_report'] + "\n\n")
            f.write(f"最终状态: {result1['final_status']}\n")

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 协作问题解决
    print("\n\n" + "🔷" * 30)
    print("示例 2: 协作问题解决")
    print("🔷" * 30)

    try:
        result2 = collaborative_problem_solving()

        # 保存结果
        output_file = "collaborative_solving_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("协作问题解决结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(result2)

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例3: 增量知识构建
    print("\n\n" + "🔷" * 30)
    print("示例 3: 增量知识构建")
    print("🔷" * 30)

    try:
        result3 = incremental_knowledge_building()

        # 保存结果
        output_file = "knowledge_building_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("增量知识构建结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(result3)

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
