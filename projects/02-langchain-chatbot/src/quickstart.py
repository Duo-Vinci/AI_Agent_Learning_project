"""
LangChain 聊天机器人 - 快速入门

这是一个快速入门脚本，展示如何快速使用LangChain创建聊天机器人。

包含3个快速示例：
1. 基础聊天机器人（无记忆）
2. 带记忆的聊天机器人
3. 完整功能的聊天机器人

运行方式：
    python quickstart.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 最简单的聊天机器人（5行代码） ====================

def example_1_simple_chat():
    """示例1: 最简单的聊天机器人"""
    print_section("示例1: 最简单的聊天机器人（无记忆）")

    # 加载环境变量
    load_dotenv()

    # 初始化模型
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        temperature=0.7
    )

    # 单轮对话
    print("用户: 你好！")
    response = llm.invoke([HumanMessage(content="你好！")])
    print(f"AI: {response.content}\n")

    # 注意：无记忆，无法记住之前的对话
    print("用户: 我刚才说了什么？")
    response = llm.invoke([HumanMessage(content="我刚才说了什么？")])
    print(f"AI: {response.content}")
    print("\n💡 提示: 这个机器人没有记忆，无法记住之前的对话")


# ==================== 示例2: 带记忆的聊天机器人（10行代码） ====================

def example_2_chat_with_memory():
    """示例2: 带记忆的聊天机器人"""
    print_section("示例2: 带记忆的聊天机器人")

    load_dotenv()

    # 初始化模型
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        temperature=0.7
    )

    # 手动管理对话历史
    conversation_history = []

    # 第一轮对话
    print("用户: 我叫小明")
    user_msg = HumanMessage(content="我叫小明")
    conversation_history.append(user_msg)

    response = llm.invoke(conversation_history)
    conversation_history.append(response)
    print(f"AI: {response.content}\n")

    # 第二轮对话
    print("用户: 我叫什么名字？")
    user_msg = HumanMessage(content="我叫什么名字？")
    conversation_history.append(user_msg)

    response = llm.invoke(conversation_history)
    conversation_history.append(response)
    print(f"AI: {response.content}\n")

    print(f"💡 提示: 对话历史共 {len(conversation_history)} 条消息")


# ==================== 示例3: 完整功能的聊天机器人（使用封装） ====================

def example_3_complete_chatbot():
    """示例3: 完整功能的聊天机器人"""
    print_section("示例3: 完整功能的聊天机器人")

    # 尝试使用完整的聊天机器人
    try:
        from complete_chatbot import CompleteChatbot

        print("使用完整聊天机器人系统...\n")

        # 创建机器人实例
        bot = CompleteChatbot(session_id="quickstart_demo")

        # 模拟对话
        conversations = [
            "你好，我是新用户",
            "你能帮我做什么？",
            "太好了！"
        ]

        for user_input in conversations:
            print(f"\n用户: {user_input}")
            print("AI: ", end="")
            bot.chat(user_input)

        # 显示统计
        print("\n")
        bot.chat("/stats")

        print("\n💡 提示: 完整版支持持久化、流式输出、命令系统等功能")

    except ImportError:
        print("⚠️  未找到 complete_chatbot 模块")
        print("请先运行: python 09_complete_chatbot.py")


# ==================== 示例4: 流式输出聊天机器人 ====================

def example_4_streaming_chat():
    """示例4: 流式输出聊天机器人"""
    print_section("示例4: 流式输出聊天机器人")

    import sys
    import time
    from langchain_core.callbacks import BaseCallbackHandler

    load_dotenv()

    # 自定义回调处理器
    class SimpleStreamHandler(BaseCallbackHandler):
        def on_llm_new_token(self, token: str, **kwargs):
            sys.stdout.write(token)
            sys.stdout.flush()
            time.sleep(0.02)  # 打字机效果

    # 初始化支持流式输出的模型
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        temperature=0.7,
        streaming=True,
        callbacks=[SimpleStreamHandler()]
    )

    print("用户: 请用一句话介绍Python\n")
    print("AI: ", end="")

    response = llm.invoke([HumanMessage(content="请用一句话介绍Python")])

    print("\n\n💡 提示: 流式输出让用户更快看到响应")


# ==================== 交互式聊天 ====================

def interactive_chat():
    """交互式聊天模式"""
    print_section("交互式聊天模式")

    load_dotenv()

    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        temperature=0.7
    )

    conversation_history = []

    print("开始聊天！输入 'quit' 或 'exit' 退出\n")

    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n再见！")
                break

            # 添加到历史
            conversation_history.append(HumanMessage(content=user_input))

            # 获取响应
            print("AI: ", end="")
            response = llm.invoke(conversation_history)
            print(response.content)

            # 保存AI响应
            conversation_history.append(response)

            # 限制历史长度（保留最近10轮对话）
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]

        except KeyboardInterrupt:
            print("\n\n再见！")
            break

        except Exception as e:
            print(f"\n错误: {str(e)}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 快速入门")
    print("="*70)
    print("\n本脚本包含4个示例，展示从简单到复杂的聊天机器人实现\n")

    try:
        # 示例1: 最简单的聊天
        example_1_simple_chat()

        # 示例2: 带记忆的聊天
        example_2_chat_with_memory()

        # 示例3: 完整聊天机器人
        example_3_complete_chatbot()

        # 示例4: 流式输出
        example_4_streaming_chat()

        # 询问是否启动交互式聊天
        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

        print("\n是否启动交互式聊天模式？(y/n): ", end="")
        choice = input().strip().lower()

        if choice == 'y':
            interactive_chat()

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
