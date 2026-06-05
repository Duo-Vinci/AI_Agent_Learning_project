"""
研究团队工作流
演示基于消息传递的Agent协作
"""

import os
import sys
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.communication import MessageBus, CommunicatingAgent, CoordinatorAgent, MessageType


def research_team_workflow(research_topic: str):
    """
    研究团队工作流：协调者分配任务给多个研究员

    Args:
        research_topic: 研究主题
    """
    print("=" * 60)
    print("研究团队协作工作流")
    print("=" * 60)
    print(f"研究主题: {research_topic}\n")

    # 创建消息总线
    bus = MessageBus()

    # 创建LLM
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建协调者
    coordinator = CoordinatorAgent("协调者", bus, llm)

    # 创建研究员
    researcher1 = CommunicatingAgent("技术研究员", bus, llm)
    researcher2 = CommunicatingAgent("市场研究员", bus, llm)
    researcher3 = CommunicatingAgent("用户研究员", bus, llm)

    # 注册工作者
    coordinator.add_worker("技术研究员")
    coordinator.add_worker("市场研究员")
    coordinator.add_worker("用户研究员")

    # 启动所有Agent
    researcher1.start()
    researcher2.start()
    researcher3.start()

    # 步骤1: 分配任务
    print("\n[步骤 1/3] 分配研究任务")
    print("-" * 60)

    task = f"研究以下主题并提供专业见解：{research_topic}"

    # 为每个研究员分配任务（在后台处理）
    coordinator.send_to("技术研究员", MessageType.TASK, f"{task}\n请从技术角度分析。")
    coordinator.send_to("市场研究员", MessageType.TASK, f"{task}\n请从市场角度分析。")
    coordinator.send_to("用户研究员", MessageType.TASK, f"{task}\n请从用户角度分析。")

    # 等待研究员处理
    time.sleep(1)

    # 研究员处理任务
    researcher1.run_once()
    researcher2.run_once()
    researcher3.run_once()

    # 步骤2: 收集结果
    print("\n[步骤 2/3] 收集研究结果")
    print("-" * 60)

    results = {}
    for _ in range(3):
        msg = coordinator.receive(timeout=5.0)
        if msg and msg.type == MessageType.RESULT:
            results[msg.sender] = msg.content

    # 显示结果
    print("\n研究结果汇总:")
    for researcher, result in results.items():
        print(f"\n【{researcher}】")
        print(result[:200] + "..." if len(result) > 200 else result)

    # 步骤3: 综合分析
    print("\n\n[步骤 3/3] 综合分析")
    print("-" * 60)

    # 协调者综合所有结果
    summary_prompt = f"""基于以下研究员的分析结果，生成一份综合研究报告：

{chr(10).join([f'{k}的分析：{v}' for k, v in results.items()])}

请生成包含以下部分的综合报告：
1. 执行摘要
2. 技术、市场、用户三个维度的综合分析
3. 关键发现
4. 建议和结论"""

    final_report = coordinator.execute_task(summary_prompt)

    print("\n📊 综合研究报告:")
    print("=" * 60)
    print(final_report)
    print("=" * 60)

    # 显示消息统计
    print("\n\n📈 消息统计:")
    stats = bus.get_statistics()
    print(f"参与Agent数量: {stats['total_agents']}")
    print(f"总消息数: {stats['total_messages']}")
    print("消息类型分布:")
    for msg_type, count in stats['message_types'].items():
        print(f"  - {msg_type}: {count}")

    return {
        'results': results,
        'report': final_report,
        'stats': stats
    }


def collaborative_query_workflow(topic: str):
    """
    协作查询工作流：多个Agent协作回答问题

    Args:
        topic: 查询主题
    """
    print("=" * 60)
    print("协作查询工作流")
    print("=" * 60)
    print(f"查询主题: {topic}\n")

    # 创建消息总线
    bus = MessageBus()
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建协调者
    coordinator = CoordinatorAgent("查询协调者", bus, llm)

    # 创建专家Agent
    expert1 = CommunicatingAgent("技术专家", bus, llm)
    expert2 = CommunicatingAgent("业务专家", bus, llm)
    expert3 = CommunicatingAgent("安全专家", bus, llm)

    # 注册专家
    coordinator.add_worker("技术专家")
    coordinator.add_worker("业务专家")
    coordinator.add_worker("安全专家")

    # 启动专家
    expert1.start()
    expert2.start()
    expert3.start()

    # 发送查询
    print("[查询] 向所有专家发送问题...")
    coordinator.send_to("技术专家", MessageType.QUERY, f"从技术实现角度：{topic}")
    coordinator.send_to("业务专家", MessageType.QUERY, f"从业务价值角度：{topic}")
    coordinator.send_to("安全专家", MessageType.QUERY, f"从安全风险角度：{topic}")

    time.sleep(1)

    # 专家回答
    expert1.run_once()
    expert2.run_once()
    expert3.run_once()

    # 收集回答
    print("\n[收集] 汇总专家意见...")
    responses = {}
    for _ in range(3):
        msg = coordinator.receive(timeout=5.0)
        if msg and msg.type == MessageType.RESPONSE:
            responses[msg.sender] = msg.content

    # 显示结果
    print("\n专家意见汇总:")
    for expert, response in responses.items():
        print(f"\n【{expert}】")
        print(response)

    return responses


def broadcast_workflow():
    """
    广播工作流：演示广播消息机制

    Returns:
        Agent响应列表
    """
    print("=" * 60)
    print("广播消息工作流")
    print("=" * 60)

    # 创建消息总线
    bus = MessageBus()
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # 创建管理者
    manager = CommunicatingAgent("项目经理", bus, llm)

    # 创建团队成员
    member1 = CommunicatingAgent("开发者", bus, llm)
    member2 = CommunicatingAgent("测试员", bus, llm)
    member3 = CommunicatingAgent("设计师", bus, llm)

    # 启动所有成员
    member1.start()
    member2.start()
    member3.start()

    # 广播消息
    print("\n[广播] 项目经理发送全员通知...")
    announcement = "紧急通知：项目截止日期提前到本周五，请各位加快进度！"
    manager.broadcast(MessageType.BROADCAST, announcement)

    time.sleep(1)

    # 成员接收广播
    print("\n[接收] 团队成员收到通知...")
    for member in [member1, member2, member3]:
        msg = member.receive(timeout=2.0)
        if msg:
            print(f"  - {member.agent_id}: 已收到通知")

    # 查看消息历史
    print("\n📜 消息历史:")
    history = bus.get_message_history()
    for msg in history:
        print(f"  {msg.sender} -> {msg.receiver}: {msg.type.value}")

    return history


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例1: 研究团队工作流
    print("\n" + "🔷" * 30)
    print("示例 1: 研究团队协作")
    print("🔷" * 30)

    try:
        result1 = research_team_workflow("AI Agent在智能客服中的应用")

        # 保存结果
        output_file = "research_team_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("研究团队协作结果\n")
            f.write("=" * 60 + "\n\n")
            f.write("各研究员分析:\n")
            for researcher, result in result1['results'].items():
                f.write(f"\n【{researcher}】\n")
                f.write(result + "\n\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("综合研究报告:\n")
            f.write(result1['report'])

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 协作查询工作流
    print("\n\n" + "🔷" * 30)
    print("示例 2: 协作查询")
    print("🔷" * 30)

    try:
        result2 = collaborative_query_workflow("如何在企业中部署大规模AI Agent系统？")

        # 保存结果
        output_file = "collaborative_query_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("协作查询结果\n")
            f.write("=" * 60 + "\n\n")
            for expert, response in result2.items():
                f.write(f"【{expert}】\n")
                f.write(response + "\n\n")

        print(f"\n✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例3: 广播工作流
    print("\n\n" + "🔷" * 30)
    print("示例 3: 广播消息")
    print("🔷" * 30)

    try:
        broadcast_workflow()
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
