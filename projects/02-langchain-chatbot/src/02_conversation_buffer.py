"""
LangChain 聊天机器人 - 02: 对话缓冲区详解

本模块演示：
1. ConversationBufferMemory 基础使用
2. ConversationBufferWindowMemory 窗口记忆
3. ConversationSummaryMemory 摘要记忆
4. 对话缓冲区的持久化
5. 自定义缓冲区策略
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory
)
from langchain.chains import ConversationChain
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


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


def demo_buffer_memory():
    """示例1: ConversationBufferMemory - 完整历史记忆"""
    print_section("示例1: ConversationBufferMemory")

    llm = init_llm()

    # 创建完整缓冲区记忆
    memory = ConversationBufferMemory()

    # 创建对话链
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True  # 显示详细信息
    )

    print("完整缓冲区记忆 - 保留所有对话历史\n")

    # 模拟多轮对话
    conversations = [
        "你好，我叫Alice",
        "我是一名软件工程师",
        "我喜欢Python编程",
        "我的名字是什么？我的职业是什么？"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = conversation.predict(input=user_input)
        print(f"AI: {response}\n")

    # 查看记忆内容
    print("\n记忆内容:")
    print(memory.load_memory_variables({}))

    # 获取对话历史
    print("\n对话历史:")
    print(memory.chat_memory.messages)


def demo_window_memory():
    """示例2: ConversationBufferWindowMemory - 窗口记忆"""
    print_section("示例2: ConversationBufferWindowMemory")

    llm = init_llm()

    # 创建窗口记忆（只保留最近3轮对话）
    memory = ConversationBufferWindowMemory(k=3)

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    print("窗口记忆 - 只保留最近3轮对话\n")

    conversations = [
        "我的第一个爱好是游泳",
        "我的第二个爱好是跑步",
        "我的第三个爱好是骑自行车",
        "我的第四个爱好是打篮球",
        "我的第五个爱好是读书",
        "我有哪些爱好？"  # 只能记住最近3轮
    ]

    for i, user_input in enumerate(conversations, 1):
        print(f"[轮次 {i}] 用户: {user_input}")
        response = conversation.predict(input=user_input)
        print(f"AI: {response}")

        # 显示当前窗口内容
        memory_vars = memory.load_memory_variables({})
        message_count = len(memory.chat_memory.messages)
        print(f"  → 当前记忆窗口: {message_count // 2} 轮对话\n")

    print("\n最终记忆内容（只有最近3轮）:")
    for msg in memory.chat_memory.messages:
        print(f"  {msg.type}: {msg.content[:50]}...")


def demo_summary_memory():
    """示例3: ConversationSummaryMemory - 摘要记忆"""
    print_section("示例3: ConversationSummaryMemory")

    llm = init_llm()

    # 创建摘要记忆
    memory = ConversationSummaryMemory(llm=llm)

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    print("摘要记忆 - 自动总结对话历史\n")

    conversations = [
        "我在一家科技公司工作",
        "公司位于北京",
        "我的团队有10个人",
        "我们主要做AI产品开发",
        "请总结一下我的工作情况"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = conversation.predict(input=user_input)
        print(f"AI: {response}\n")

    # 查看摘要
    print("\n对话摘要:")
    summary = memory.load_memory_variables({})
    print(summary.get('history', ''))


def demo_summary_buffer_memory():
    """示例4: ConversationSummaryBufferMemory - 摘要+缓冲区混合"""
    print_section("示例4: ConversationSummaryBufferMemory")

    llm = init_llm()

    # 创建摘要缓冲区记忆（保留最近2轮，其余生成摘要）
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=200  # Token限制
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    print("摘要缓冲区记忆 - 近期完整保留，历史生成摘要\n")

    conversations = [
        "我出生在上海",
        "我在那里度过了童年",
        "后来我去北京上大学",
        "大学毕业后我留在北京工作",
        "现在我在考虑回上海发展",
        "请总结一下我的经历"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = conversation.predict(input=user_input)
        print(f"AI: {response}\n")

    print("\n记忆结构:")
    memory_vars = memory.load_memory_variables({})
    print(memory_vars.get('history', ''))


def demo_custom_buffer():
    """示例5: 自定义缓冲区策略"""
    print_section("示例5: 自定义缓冲区策略")

    class SmartBuffer:
        """智能缓冲区 - 重要消息优先保留"""

        def __init__(self, max_messages: int = 6):
            self.max_messages = max_messages
            self.messages: List[Dict[str, Any]] = []
            self.important_keywords = ['重要', '关键', '记住', '姓名', '联系']

        def add_message(self, role: str, content: str):
            """添加消息"""
            is_important = any(keyword in content for keyword in self.important_keywords)

            message = {
                'role': role,
                'content': content,
                'important': is_important,
                'timestamp': len(self.messages)
            }

            self.messages.append(message)
            self._trim()

        def _trim(self):
            """修剪消息 - 优先保留重要消息"""
            if len(self.messages) <= self.max_messages:
                return

            # 分离重要和普通消息
            important = [m for m in self.messages if m['important']]
            normal = [m for m in self.messages if not m['important']]

            # 保留所有重要消息 + 最近的普通消息
            keep_normal_count = max(0, self.max_messages - len(important))
            kept_messages = important + normal[-keep_normal_count:]

            # 按时间戳排序
            self.messages = sorted(kept_messages, key=lambda x: x['timestamp'])

        def get_messages(self) -> List[Dict[str, Any]]:
            """获取所有消息"""
            return self.messages

        def get_context(self) -> str:
            """获取上下文字符串"""
            context = []
            for msg in self.messages:
                prefix = "[重要]" if msg['important'] else ""
                context.append(f"{prefix}{msg['role']}: {msg['content']}")
            return "\n".join(context)

    # 使用自定义缓冲区
    buffer = SmartBuffer(max_messages=6)

    conversations = [
        ("user", "你好"),
        ("ai", "你好！有什么可以帮你的？"),
        ("user", "我的名字是张伟（重要）"),
        ("ai", "你好张伟！"),
        ("user", "今天天气不错"),
        ("ai", "是的，阳光明媚"),
        ("user", "我的电话是13812345678（重要）"),
        ("ai", "好的，我记住了"),
        ("user", "你知道我的名字和电话吗？"),
    ]

    print("智能缓冲区 - 重要信息优先保留\n")

    for role, content in conversations:
        buffer.add_message(role, content)
        print(f"{role}: {content}")

    print("\n\n当前缓冲区内容:")
    print(buffer.get_context())

    print(f"\n缓冲区统计:")
    print(f"  总消息数: {len(buffer.messages)}")
    important_count = sum(1 for m in buffer.messages if m['important'])
    print(f"  重要消息: {important_count}")
    print(f"  普通消息: {len(buffer.messages) - important_count}")


def demo_memory_persistence():
    """示例6: 对话缓冲区持久化"""
    print_section("示例6: 对话缓冲区持久化")

    import json
    from pathlib import Path

    llm = init_llm()
    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=llm, memory=memory, verbose=False)

    print("演示对话缓冲区的保存和加载\n")

    # 模拟对话
    conversations = [
        "我叫Bob",
        "我是数据科学家",
        "我擅长机器学习"
    ]

    print("第一阶段对话:")
    for user_input in conversations:
        print(f"用户: {user_input}")
        response = conversation.predict(input=user_input)
        print(f"AI: {response}\n")

    # 保存对话历史
    save_path = Path("conversation_history.json")
    history_data = {
        'messages': [
            {
                'type': msg.type,
                'content': msg.content
            }
            for msg in memory.chat_memory.messages
        ]
    }

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    print(f"✓ 对话历史已保存到: {save_path}")

    # 模拟新会话 - 加载历史
    print("\n\n--- 模拟新会话，加载历史 ---\n")

    new_memory = ConversationBufferMemory()

    # 加载历史
    with open(save_path, 'r', encoding='utf-8') as f:
        history_data = json.load(f)

    for msg_data in history_data['messages']:
        if msg_data['type'] == 'human':
            new_memory.chat_memory.add_user_message(msg_data['content'])
        elif msg_data['type'] == 'ai':
            new_memory.chat_memory.add_ai_message(msg_data['content'])

    print("✓ 历史记录已加载")

    # 继续对话
    new_conversation = ConversationChain(llm=llm, memory=new_memory, verbose=False)

    print("\n第二阶段对话（基于加载的历史）:")
    continuation = "我叫什么名字？我的职业是什么？"
    print(f"用户: {continuation}")
    response = new_conversation.predict(input=continuation)
    print(f"AI: {response}")

    # 清理临时文件
    save_path.unlink()
    print(f"\n✓ 临时文件已清理")


def demo_memory_comparison():
    """示例7: 不同记忆类型对比"""
    print_section("示例7: 不同记忆类型对比")

    llm = init_llm()

    # 准备测试对话
    test_conversations = [
        "我在2020年加入公司",
        "2021年晋升为高级工程师",
        "2022年开始带团队",
        "2023年负责整个项目",
        "2024年获得公司最佳员工奖",
        "请总结我的职业发展"
    ]

    # 测试1: 完整缓冲区
    print("【完整缓冲区记忆】")
    memory1 = ConversationBufferMemory()
    conv1 = ConversationChain(llm=llm, memory=memory1, verbose=False)

    for msg in test_conversations:
        response = conv1.predict(input=msg)

    print(f"记忆大小: {len(memory1.chat_memory.messages)} 条消息")
    print(f"最后回复: {response[:100]}...")

    # 测试2: 窗口记忆
    print("\n【窗口记忆 (k=2)】")
    memory2 = ConversationBufferWindowMemory(k=2)
    conv2 = ConversationChain(llm=llm, memory=memory2, verbose=False)

    for msg in test_conversations:
        response = conv2.predict(input=msg)

    print(f"记忆大小: {len(memory2.chat_memory.messages)} 条消息")
    print(f"最后回复: {response[:100]}...")

    # 测试3: 摘要记忆
    print("\n【摘要记忆】")
    memory3 = ConversationSummaryMemory(llm=llm)
    conv3 = ConversationChain(llm=llm, memory=memory3, verbose=False)

    for msg in test_conversations:
        response = conv3.predict(input=msg)

    print(f"摘要内容: {memory3.buffer[:150]}...")
    print(f"最后回复: {response[:100]}...")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 对话缓冲区详解")
    print("="*70)

    try:
        # 运行所有示例
        demo_buffer_memory()
        demo_window_memory()
        demo_summary_memory()
        demo_summary_buffer_memory()
        demo_custom_buffer()
        demo_memory_persistence()
        demo_memory_comparison()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
