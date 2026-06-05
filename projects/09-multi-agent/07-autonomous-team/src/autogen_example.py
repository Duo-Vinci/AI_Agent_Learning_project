"""
AutoGen框架示例
演示使用AutoGen实现多Agent协作
"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

# 注意：AutoGen需要单独安装
# pip install autogen-agentchat

try:
    import autogen
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("⚠ AutoGen未安装，请运行: pip install autogen-agentchat")


def create_autogen_config() -> List[Dict]:
    """
    创建AutoGen配置

    Returns:
        配置列表
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置OPENAI_API_KEY环境变量")

    return [{
        "model": "gpt-3.5-turbo",
        "api_key": api_key,
        "temperature": 0.7
    }]


def autogen_two_agent_chat(task: str) -> str:
    """
    AutoGen两个Agent对话示例

    Args:
        task: 任务描述

    Returns:
        对话结果
    """
    if not AUTOGEN_AVAILABLE:
        return "AutoGen未安装，无法运行示例"

    print("=" * 60)
    print("AutoGen 两Agent对话示例")
    print("=" * 60)
    print(f"任务: {task}\n")

    try:
        # 配置
        config_list = create_autogen_config()

        # 创建助手Agent
        assistant = autogen.AssistantAgent(
            name="助手",
            llm_config={
                "config_list": config_list,
                "temperature": 0.7
            },
            system_message="你是一个专业的AI助手，擅长分析问题并提供解决方案。"
        )

        # 创建用户代理Agent
        user_proxy = autogen.UserProxyAgent(
            name="用户代理",
            human_input_mode="NEVER",  # 不需要人类输入
            max_consecutive_auto_reply=5,
            code_execution_config=False,
            llm_config={
                "config_list": config_list,
                "temperature": 0.7
            }
        )

        # 启动对话
        print("\n开始对话...\n")
        user_proxy.initiate_chat(
            assistant,
            message=task
        )

        print("\n✓ 对话完成")
        return "对话已完成，请查看上方输出"

    except Exception as e:
        error_msg = f"AutoGen执行出错: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def autogen_group_chat(topic: str) -> str:
    """
    AutoGen群聊示例：多个Agent参与讨论

    Args:
        topic: 讨论主题

    Returns:
        讨论结果
    """
    if not AUTOGEN_AVAILABLE:
        return "AutoGen未安装，无法运行示例"

    print("=" * 60)
    print("AutoGen 群聊示例")
    print("=" * 60)
    print(f"主题: {topic}\n")

    try:
        # 配置
        config_list = create_autogen_config()

        # 创建多个专家Agent
        researcher = autogen.AssistantAgent(
            name="研究员",
            llm_config={"config_list": config_list},
            system_message="你是一位专业的研究员，擅长收集和分析信息。"
        )

        engineer = autogen.AssistantAgent(
            name="工程师",
            llm_config={"config_list": config_list},
            system_message="你是一位经验丰富的软件工程师，擅长技术实现。"
        )

        critic = autogen.AssistantAgent(
            name="评论家",
            llm_config={"config_list": config_list},
            system_message="你是一位批判性思考者，擅长发现问题和风险。"
        )

        # 创建用户代理
        user_proxy = autogen.UserProxyAgent(
            name="主持人",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            code_execution_config=False
        )

        # 创建群聊
        groupchat = autogen.GroupChat(
            agents=[user_proxy, researcher, engineer, critic],
            messages=[],
            max_round=6
        )

        # 创建群聊管理器
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": config_list}
        )

        # 启动讨论
        print("\n开始群聊...\n")
        user_proxy.initiate_chat(
            manager,
            message=f"让我们讨论以下主题：{topic}。每位专家请从自己的角度提供见解。"
        )

        print("\n✓ 讨论完成")
        return "讨论已完成，请查看上方输出"

    except Exception as e:
        error_msg = f"AutoGen群聊执行出错: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def autogen_code_execution_example() -> str:
    """
    AutoGen代码执行示例：Agent自动编写和执行代码

    Returns:
        执行结果
    """
    if not AUTOGEN_AVAILABLE:
        return "AutoGen未安装，无法运行示例"

    print("=" * 60)
    print("AutoGen 代码执行示例")
    print("=" * 60)

    try:
        # 配置
        config_list = create_autogen_config()

        # 创建编程助手
        assistant = autogen.AssistantAgent(
            name="编程助手",
            llm_config={"config_list": config_list}
        )

        # 创建用户代理（可以执行代码）
        user_proxy = autogen.UserProxyAgent(
            name="执行器",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False  # 设置为True以使用Docker（更安全）
            }
        )

        # 请求编写和执行代码
        task = """
        编写一个Python函数来计算斐波那契数列的前10个数字，
        然后执行这个函数并显示结果。
        """

        print("\n开始任务...\n")
        user_proxy.initiate_chat(
            assistant,
            message=task
        )

        print("\n✓ 任务完成")
        return "任务已完成，请查看上方输出"

    except Exception as e:
        error_msg = f"代码执行示例出错: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg


def main():
    """主函数"""
    load_dotenv()

    if not AUTOGEN_AVAILABLE:
        print("=" * 60)
        print("AutoGen未安装")
        print("=" * 60)
        print("\n请运行以下命令安装:")
        print("  pip install autogen-agentchat")
        print("\n安装后重新运行此脚本。")
        return

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    # 示例1: 两Agent对话
    print("\n" + "🔷" * 30)
    print("示例 1: 两Agent对话")
    print("🔷" * 30)

    try:
        result1 = autogen_two_agent_chat(
            "分析AI Agent技术的优势和挑战，给出3个主要观点。"
        )
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例2: 群聊
    print("\n\n" + "🔷" * 30)
    print("示例 2: 多Agent群聊")
    print("🔷" * 30)

    try:
        result2 = autogen_group_chat(
            "如何设计一个可扩展的多Agent系统架构？"
        )
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")

    # 示例3: 代码执行（可选，可能需要较长时间）
    # print("\n\n" + "🔷" * 30)
    # print("示例 3: 代码执行")
    # print("🔷" * 30)
    #
    # try:
    #     result3 = autogen_code_execution_example()
    # except Exception as e:
    #     print(f"\n✗ 执行出错: {str(e)}")


if __name__ == "__main__":
    main()
