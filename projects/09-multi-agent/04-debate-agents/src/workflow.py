"""
辩论协作工作流
演示多方辩论、裁判评估和调解的完整流程
"""

import os
import sys
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents import DebateAgent, JudgeAgent, MediatorAgent


def two_party_debate(topic: str, stance_pro: str, stance_con: str, rounds: int = 3) -> dict:
    """
    双方辩论工作流

    Args:
        topic: 辩论主题
        stance_pro: 正方立场
        stance_con: 反方立场
        rounds: 辩论轮数

    Returns:
        包含辩论结果和评估的字典
    """
    print("=" * 60)
    print("双方辩论模式")
    print("=" * 60)
    print(f"主题: {topic}")
    print(f"正方立场: {stance_pro}")
    print(f"反方立场: {stance_con}")
    print(f"辩论轮数: {rounds}\n")

    # 初始化LLM
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建辩论双方
    agent_pro = DebateAgent(name="正方", stance=stance_pro, llm=llm)
    agent_con = DebateAgent(name="反方", stance=stance_con, llm=llm)
    judge = JudgeAgent(llm)

    # 记录所有论点
    arguments = {"正方": [], "反方": []}

    # 多轮辩论
    for round_num in range(rounds):
        print(f"\n{'=' * 60}")
        print(f"第 {round_num + 1} 轮辩论")
        print("=" * 60)

        # 正方发言
        print(f"\n[正方发言]")
        pro_arg = agent_pro.argue(topic, arguments["反方"])
        arguments["正方"].append(pro_arg)
        print(f"\n{pro_arg}\n")

        # 反方发言
        print(f"[反方发言]")
        con_arg = agent_con.argue(topic, arguments["正方"])
        arguments["反方"].append(con_arg)
        print(f"\n{con_arg}\n")

    # 裁判评估
    print(f"\n{'=' * 60}")
    print("裁判评估")
    print("=" * 60)
    evaluation = judge.evaluate(topic, arguments)

    print(f"\n🏆 获胜者: {evaluation.get('winner', '未知')}")
    print(f"\n📝 判定理由:\n{evaluation.get('reasoning', '无')}")

    if evaluation.get('scores'):
        print(f"\n📊 详细评分:")
        for agent_name, score_details in evaluation['scores'].items():
            print(f"\n  {agent_name}:")
            for criterion, score in score_details.items():
                print(f"    - {criterion}: {score}")

    if evaluation.get('highlights'):
        print(f"\n✨ 辩论亮点:")
        for highlight in evaluation['highlights']:
            print(f"  - {highlight}")

    # 生成总结报告
    print(f"\n{'=' * 60}")
    print("生成辩论总结")
    print("=" * 60)
    summary = judge.summarize_debate(topic, arguments, evaluation)

    return {
        'topic': topic,
        'arguments': arguments,
        'evaluation': evaluation,
        'summary': summary
    }


def multi_party_debate(topic: str, stances: dict, rounds: int = 2) -> dict:
    """
    多方辩论工作流

    Args:
        topic: 辩论主题
        stances: 各方立场字典 {名称: 立场描述}
        rounds: 辩论轮数

    Returns:
        辩论结果字典
    """
    print("=" * 60)
    print("多方辩论模式")
    print("=" * 60)
    print(f"主题: {topic}")
    print(f"参与方: {len(stances)} 方")
    for name, stance in stances.items():
        print(f"  - {name}: {stance}")
    print(f"辩论轮数: {rounds}\n")

    # 初始化LLM
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建各方辩论者
    debaters = {}
    for name, stance in stances.items():
        debaters[name] = DebateAgent(name=name, stance=stance, llm=llm)

    judge = JudgeAgent(llm)

    # 记录所有论点
    arguments = {name: [] for name in stances.keys()}

    # 多轮辩论
    for round_num in range(rounds):
        print(f"\n{'=' * 60}")
        print(f"第 {round_num + 1} 轮辩论")
        print("=" * 60)

        # 每方依次发言
        for name, debater in debaters.items():
            print(f"\n[{name} 发言]")

            # 收集其他方的论点
            other_arguments = []
            for other_name, args in arguments.items():
                if other_name != name and args:
                    other_arguments.extend(args)

            # 发言
            argument = debater.argue(topic, other_arguments)
            arguments[name].append(argument)
            print(f"\n{argument}\n")
            print("-" * 60)

    # 裁判评估
    print(f"\n{'=' * 60}")
    print("裁判评估")
    print("=" * 60)
    evaluation = judge.evaluate(topic, arguments)

    print(f"\n🏆 获胜者: {evaluation.get('winner', '未知')}")
    print(f"\n📝 判定理由:\n{evaluation.get('reasoning', '无')}")

    if evaluation.get('scores'):
        print(f"\n📊 详细评分:")
        for agent_name, score_details in evaluation['scores'].items():
            print(f"\n  {agent_name}:")
            if isinstance(score_details, dict):
                for criterion, score in score_details.items():
                    print(f"    - {criterion}: {score}")

    # 生成总结
    summary = judge.summarize_debate(topic, arguments, evaluation)

    return {
        'topic': topic,
        'arguments': arguments,
        'evaluation': evaluation,
        'summary': summary
    }


def debate_with_mediation(topic: str, stance_pro: str, stance_con: str, rounds: int = 3) -> dict:
    """
    带调解的辩论工作流

    Args:
        topic: 辩论主题
        stance_pro: 正方立场
        stance_con: 反方立场
        rounds: 辩论轮数

    Returns:
        辩论和调解结果
    """
    print("=" * 60)
    print("带调解的辩论模式")
    print("=" * 60)

    # 先进行辩论
    debate_result = two_party_debate(topic, stance_pro, stance_con, rounds)

    # 调解员介入
    print(f"\n{'=' * 60}")
    print("调解员介入")
    print("=" * 60)

    llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
    mediator = MediatorAgent(llm)

    mediation = mediator.mediate(topic, debate_result['arguments'])
    print(f"\n{mediation}\n")

    # 建议下一个话题
    print(f"\n{'=' * 60}")
    print("建议深入探讨的话题")
    print("=" * 60)
    next_topic = mediator.suggest_next_topic(topic, debate_result)
    print(f"\n💡 {next_topic}\n")

    debate_result['mediation'] = mediation
    debate_result['next_topic'] = next_topic

    return debate_result


def progressive_debate(initial_topic: str, depth: int = 2) -> list:
    """
    递进式辩论：从一个话题逐步深入

    Args:
        initial_topic: 初始话题
        depth: 递进深度

    Returns:
        所有辩论结果的列表
    """
    print("=" * 60)
    print("递进式辩论模式")
    print("=" * 60)
    print(f"初始话题: {initial_topic}")
    print(f"递进深度: {depth}\n")

    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    mediator = MediatorAgent(llm)

    all_debates = []
    current_topic = initial_topic

    for level in range(depth):
        print(f"\n{'#' * 60}")
        print(f"深度 {level + 1}/{depth}")
        print('#' * 60)

        # 进行辩论
        debate_result = two_party_debate(
            topic=current_topic,
            stance_pro=f"支持：{current_topic}",
            stance_con=f"反对：{current_topic}",
            rounds=2
        )

        all_debates.append(debate_result)

        # 如果不是最后一层，建议下一个话题
        if level < depth - 1:
            print(f"\n{'=' * 60}")
            print("规划下一层话题")
            print("=" * 60)
            current_topic = mediator.suggest_next_topic(current_topic, debate_result)
            print(f"\n下一个话题: {current_topic}\n")

    return all_debates


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例1: 双方辩论
    print("\n" + "🔷" * 30)
    print("示例 1: 双方辩论")
    print("🔷" * 30)

    try:
        result1 = two_party_debate(
            topic="是否应该在企业中大规模部署AI Agent系统",
            stance_pro="支持在企业中大规模部署AI Agent，认为能显著提升效率",
            stance_con="反对过快部署AI Agent，担心风险和伦理问题",
            rounds=3
        )

        # 保存结果
        output_file = "debate_output_two_party.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"辩论主题: {result1['topic']}\n")
            f.write("=" * 60 + "\n\n")
            f.write("辩论内容:\n")
            for agent_name, args in result1['arguments'].items():
                f.write(f"\n【{agent_name}】\n")
                for i, arg in enumerate(args, 1):
                    f.write(f"轮次 {i}:\n{arg}\n\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("评估结果:\n")
            f.write(json.dumps(result1['evaluation'], ensure_ascii=False, indent=2))
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("辩论总结:\n")
            f.write(result1['summary'])

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 多方辩论
    print("\n\n" + "🔷" * 30)
    print("示例 2: 多方辩论")
    print("🔷" * 30)

    try:
        result2 = multi_party_debate(
            topic="AI技术对就业市场的影响",
            stances={
                "技术乐观派": "AI会创造更多新工作机会，提升人类工作质量",
                "技术悲观派": "AI会导致大规模失业，加剧社会不平等",
                "中立观察派": "AI的影响取决于如何管理和应用，需要政策引导"
            },
            rounds=2
        )

        # 保存结果
        output_file = "debate_output_multi_party.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"辩论主题: {result2['topic']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result2['summary'])

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例3: 带调解的辩论
    print("\n\n" + "🔷" * 30)
    print("示例 3: 带调解的辩论")
    print("🔷" * 30)

    try:
        result3 = debate_with_mediation(
            topic="AI生成内容的版权归属问题",
            stance_pro="AI生成内容的版权应归使用者所有",
            stance_con="AI生成内容应该是公共领域作品",
            rounds=2
        )

        # 保存结果
        output_file = "debate_output_mediation.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"辩论主题: {result3['topic']}\n")
            f.write("=" * 60 + "\n\n")
            f.write("辩论总结:\n")
            f.write(result3['summary'])
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("调解意见:\n")
            f.write(result3['mediation'])
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("建议深入探讨的话题:\n")
            f.write(result3['next_topic'])

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
