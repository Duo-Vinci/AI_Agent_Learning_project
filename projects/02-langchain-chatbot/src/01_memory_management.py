"""
LangChain 聊天机器人 - 01: 带记忆的对话

本模块演示：
1. 基本的对话记忆
2. 对话历史管理
3. 会话窗口限制
4. 对话摘要
5. 持久化对话历史
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def init_llm():
    """初始化大语言模型"""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise ValueError("未找到 API Key，请配置 .env 文件")

    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )


def demo_basic_memory():
    """示例1: 基本的对话记忆"""
    print_section("示例1: 基本的对话记忆")

    llm = init_llm()

    # 初始化对话历史
    messages = [
        SystemMessage(content="你是一个友好的AI助手，记住用户说的内容。")
    ]

    print("开始对话（输入 'exit' 退出）\n")

    conversations = [
        "我叫张三",
        "我今年25岁",
        "我的名字是什么？",
        "我多大了？"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")

        # 添加用户消息
        messages.append(HumanMessage(content=user_input))

        # 获取 AI 回复
        response = llm.invoke(messages)

        # 添加 AI 消息到历史
        messages.append(AIMessage(content=response.content))

        print(f"AI: {response.content}\n")

    print(f"对话历史长度: {len(messages)} 条消息")


def demo_conversation_buffer():
    """示例2: 使用 ChatMessageHistory"""
    print_section("示例2: 使用 ChatMessageHistory")

    llm = init_llm()

    # 创建对话历史
    history = ChatMessageHistory()

    # 添加系统消息
    history.add_message(SystemMessage(content="你是一个有用的助手。"))

    print("对话示例:\n")

    conversations = [
        ("我喜欢吃苹果", "好的，我记住了你喜欢吃苹果。"),
        ("我也喜欢香蕉", "明白了，你喜欢苹果和香蕉。"),
        ("我喜欢吃什么？", None)
    ]

    for user_msg, expected in conversations:
        print(f"用户: {user_msg}")

        # 添加用户消息
        history.add_user_message(user_msg)

        # 获取完整历史
        messages = history.messages

        # 调用 LLM
        response = llm.invoke(messages)

        # 添加 AI 回复
        history.add_ai_message(response.content)

        print(f"AI: {response.content}\n")

    print(f"历史记录:")
    for i, msg in enumerate(history.messages):
        print(f"  {i+1}. {msg.__class__.__name__}: {msg.content[:50]}...")


def demo_windowed_memory():
    """示例3: 窗口记忆（限制历史长度）"""
    print_section("示例3: 窗口记忆")

    llm = init_llm()

    class WindowedMemory:
        """窗口记忆管理器"""

        def __init__(self, window_size=5):
            self.window_size = window_size
            self.messages = [
                SystemMessage(content="你是一个AI助手。")
            ]

        def add_user_message(self, content: str):
            """添加用户消息"""
            self.messages.append(HumanMessage(content=content))
            self._trim()

        def add_ai_message(self, content: str):
            """添加AI消息"""
            self.messages.append(AIMessage(content=content))
            self._trim()

        def _trim(self):
            """修剪历史，保留系统消息和最近的N条对话"""
            if len(self.messages) > self.window_size + 1:
                # 保留系统消息和最后N条
                self.messages = [self.messages[0]] + self.messages[-(self.window_size):]

        def get_messages(self):
            """获取消息列表"""
            return self.messages

    memory = WindowedMemory(window_size=4)  # 只保留最近4条消息

    print("窗口大小: 4条消息\n")

    conversations = [
        "第1条: 我喜欢红色",
        "第2条: 我喜欢蓝色",
        "第3条: 我喜欢绿色",
        "第4条: 我喜欢黄色",
        "我喜欢什么颜色？（测试记忆范围）"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")

        memory.add_user_message(user_input)
        messages = memory.get_messages()

        response = llm.invoke(messages)
        memory.add_ai_message(response.content)

        print(f"AI: {response.content}")
        print(f"当前记忆长度: {len(memory.get_messages())} 条\n")


def demo_conversation_summary():
    """示例4: 对话摘要"""
    print_section("示例4: 对话摘要")

    llm = init_llm()

    # 模拟一段对话历史
    conversation_history = [
        ("用户", "我最近在学习Python"),
        ("AI", "很好！Python是一门非常实用的编程语言。"),
        ("用户", "我想用它来做数据分析"),
        ("AI", "那你可以学习pandas和numpy这些库。"),
        ("用户", "还需要学什么吗？"),
        ("AI", "建议学习matplotlib用于数据可视化。")
    ]

    print("原始对话:")
    for role, content in conversation_history:
        print(f"  {role}: {content}")

    # 生成摘要
    summary_prompt = ChatPromptTemplate.from_template(
        "请将以下对话总结成一段简短的摘要（50字内）：\n\n{conversation}"
    )

    conversation_text = "\n".join([f"{role}: {content}" for role, content in conversation_history])

    chain = summary_prompt | llm

    response = chain.invoke({"conversation": conversation_text})

    print(f"\n对话摘要:")
    print(f"  {response.content}")


def demo_persistent_history():
    """示例5: 持久化对话历史"""
    print_section("示例5: 持久化对话历史")

    llm = init_llm()

    class PersistentChatHistory:
        """持久化对话历史"""

        def __init__(self, filename="chat_history.json"):
            self.filename = filename
            self.messages = self._load()

        def _load(self):
            """从文件加载历史"""
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = []
                    for msg in data:
                        if msg['type'] == 'system':
                            messages.append(SystemMessage(content=msg['content']))
                        elif msg['type'] == 'human':
                            messages.append(HumanMessage(content=msg['content']))
                        elif msg['type'] == 'ai':
                            messages.append(AIMessage(content=msg['content']))
                    return messages
            return [SystemMessage(content="你是一个友好的AI助手。")]

        def _save(self):
            """保存历史到文件"""
            data = []
            for msg in self.messages:
                msg_dict = {
                    'content': msg.content,
                    'timestamp': datetime.now().isoformat()
                }
                if isinstance(msg, SystemMessage):
                    msg_dict['type'] = 'system'
                elif isinstance(msg, HumanMessage):
                    msg_dict['type'] = 'human'
                elif isinstance(msg, AIMessage):
                    msg_dict['type'] = 'ai'
                data.append(msg_dict)

            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        def add_user_message(self, content: str):
            """添加用户消息"""
            self.messages.append(HumanMessage(content=content))
            self._save()

        def add_ai_message(self, content: str):
            """添加AI消息"""
            self.messages.append(AIMessage(content=content))
            self._save()

        def get_messages(self):
            """获取消息列表"""
            return self.messages

        def clear(self):
            """清除历史"""
            self.messages = [SystemMessage(content="你是一个友好的AI助手。")]
            self._save()

    # 创建持久化历史
    history = PersistentChatHistory("demo_history.json")

    print("使用持久化对话历史\n")

    conversations = [
        "我的名字是李四",
        "我在北京工作"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")

        history.add_user_message(user_input)
        messages = history.get_messages()

        response = llm.invoke(messages)
        history.add_ai_message(response.content)

        print(f"AI: {response.content}\n")

    print(f"✓ 对话历史已保存到 demo_history.json")
    print(f"  共 {len(history.get_messages())} 条消息")

    # 清理
    history.clear()
    if os.path.exists("demo_history.json"):
        os.remove("demo_history.json")


def demo_session_management():
    """示例6: 会话管理（多用户）"""
    print_section("示例6: 会话管理")

    llm = init_llm()

    # 多用户会话存储
    sessions = {}

    def get_session(session_id: str) -> ChatMessageHistory:
        """获取或创建会话"""
        if session_id not in sessions:
            sessions[session_id] = ChatMessageHistory()
            sessions[session_id].add_message(
                SystemMessage(content="你是一个友好的AI助手。")
            )
        return sessions[session_id]

    print("模拟多用户对话:\n")

    # 用户1的对话
    print("【用户1的会话】")
    session1 = get_session("user_1")
    session1.add_user_message("我喜欢打篮球")
    response = llm.invoke(session1.messages)
    session1.add_ai_message(response.content)
    print(f"用户1: 我喜欢打篮球")
    print(f"AI: {response.content}\n")

    # 用户2的对话
    print("【用户2的会话】")
    session2 = get_session("user_2")
    session2.add_user_message("我喜欢读书")
    response = llm.invoke(session2.messages)
    session2.add_ai_message(response.content)
    print(f"用户2: 我喜欢读书")
    print(f"AI: {response.content}\n")

    # 用户1继续对话
    print("【用户1继续对话】")
    session1.add_user_message("我喜欢什么运动？")
    response = llm.invoke(session1.messages)
    session1.add_ai_message(response.content)
    print(f"用户1: 我喜欢什么运动？")
    print(f"AI: {response.content}\n")

    print(f"会话统计:")
    print(f"  用户1: {len(session1.messages)} 条消息")
    print(f"  用户2: {len(session2.messages)} 条消息")


def main():
    """运行所有示例"""
    try:
        demo_basic_memory()
        demo_conversation_buffer()
        demo_windowed_memory()
        demo_conversation_summary()
        demo_persistent_history()
        demo_session_management()

        print_section("所有示例执行完成")
        print("对话记忆是聊天机器人的核心功能，")
        print("选择合适的记忆策略可以平衡性能和用户体验！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
