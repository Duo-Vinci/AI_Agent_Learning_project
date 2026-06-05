"""
LangChain 聊天机器人 - 04: 上下文窗口管理

本模块演示：
1. Token计数和限制
2. 智能上下文截断
3. 上下文压缩技术
4. 滑动窗口策略
5. 优先级保留策略
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage


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


def estimate_tokens(text: str) -> int:
    """
    估算文本的token数量
    简单估算：1个token约等于4个字符（英文），中文约1.5个字符
    """
    # 简单估算
    chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
    other_chars = len(text) - chinese_chars

    # 中文字符：约1.5字符/token，英文：约4字符/token
    estimated_tokens = (chinese_chars / 1.5) + (other_chars / 4)
    return int(estimated_tokens)


def demo_token_counting():
    """示例1: Token计数基础"""
    print_section("示例1: Token计数基础")

    test_texts = [
        "Hello, how are you?",
        "你好，最近怎么样？",
        "This is a longer text that contains both English and Chinese characters. 这是一段包含中英文的长文本。",
        "A" * 100,  # 100个字符
    ]

    print("Token估算示例:\n")
    for i, text in enumerate(test_texts, 1):
        tokens = estimate_tokens(text)
        print(f"示例 {i}:")
        print(f"  文本: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"  字符数: {len(text)}")
        print(f"  估算tokens: {tokens}\n")


def demo_simple_truncation():
    """示例2: 简单截断策略"""
    print_section("示例2: 简单截断策略")

    class SimpleTruncation:
        """简单截断管理器"""

        def __init__(self, max_tokens: int = 1000):
            self.max_tokens = max_tokens
            self.messages: List[BaseMessage] = []
            self.system_message = SystemMessage(content="你是一个智能助手。")

        def add_message(self, message: BaseMessage):
            """添加消息"""
            self.messages.append(message)
            self._truncate()

        def _truncate(self):
            """截断消息历史"""
            # 计算总token数
            total_tokens = estimate_tokens(self.system_message.content)

            for msg in self.messages:
                total_tokens += estimate_tokens(msg.content)

            # 如果超出限制，删除最旧的消息（保留系统消息）
            while total_tokens > self.max_tokens and len(self.messages) > 0:
                removed = self.messages.pop(0)
                total_tokens -= estimate_tokens(removed.content)
                print(f"  [截断] 删除旧消息: {removed.content[:30]}...")

        def get_messages(self) -> List[BaseMessage]:
            """获取所有消息"""
            return [self.system_message] + self.messages

        def get_token_count(self) -> int:
            """获取当前token数"""
            total = estimate_tokens(self.system_message.content)
            for msg in self.messages:
                total += estimate_tokens(msg.content)
            return total

    truncator = SimpleTruncation(max_tokens=500)

    print("添加消息并自动截断（限制: 500 tokens）\n")

    messages = [
        HumanMessage(content="你好！我想了解一下人工智能的基本概念。"),
        AIMessage(content="你好！人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"),
        HumanMessage(content="能详细讲讲机器学习吗？"),
        AIMessage(content="机器学习是人工智能的一个子领域，它使计算机系统能够从数据中学习和改进，而无需明确编程。主要包括监督学习、无监督学习和强化学习。"),
        HumanMessage(content="深度学习又是什么呢？"),
        AIMessage(content="深度学习是机器学习的一个分支，使用多层神经网络来处理和学习数据。它在图像识别、自然语言处理等领域表现出色。"),
    ]

    for msg in messages:
        print(f"添加: {msg.__class__.__name__} ({estimate_tokens(msg.content)} tokens)")
        truncator.add_message(msg)
        print(f"  当前总计: {truncator.get_token_count()} tokens")
        print(f"  消息数: {len(truncator.messages)}\n")

    print(f"\n最终保留的消息数: {len(truncator.messages)}")


def demo_sliding_window():
    """示例3: 滑动窗口策略"""
    print_section("示例3: 滑动窗口策略")

    class SlidingWindowManager:
        """滑动窗口管理器"""

        def __init__(self, window_size: int = 5):
            """
            初始化滑动窗口

            Args:
                window_size: 窗口大小（对话轮数）
            """
            self.window_size = window_size
            self.messages: List[BaseMessage] = []
            self.system_message = SystemMessage(content="你是一个助手。")
            self.archived_count = 0

        def add_exchange(self, user_msg: str, ai_msg: str):
            """添加一轮对话（问答对）"""
            self.messages.append(HumanMessage(content=user_msg))
            self.messages.append(AIMessage(content=ai_msg))

            # 保持窗口大小（每轮对话=2条消息）
            max_messages = self.window_size * 2
            if len(self.messages) > max_messages:
                # 删除最旧的一轮对话
                archived = self.messages[:2]
                self.messages = self.messages[2:]
                self.archived_count += 1
                print(f"  [归档] 第{self.archived_count}轮对话已移出窗口")

        def get_messages(self) -> List[BaseMessage]:
            """获取窗口内的消息"""
            return [self.system_message] + self.messages

        def get_window_info(self) -> Dict[str, Any]:
            """获取窗口信息"""
            return {
                'window_size': self.window_size,
                'current_turns': len(self.messages) // 2,
                'archived_turns': self.archived_count,
                'total_messages': len(self.messages)
            }

    manager = SlidingWindowManager(window_size=3)

    print("滑动窗口示例（窗口大小: 3轮对话）\n")

    conversations = [
        ("第1轮：我喜欢苹果", "好的，记住了。"),
        ("第2轮：我也喜欢香蕉", "明白。"),
        ("第3轮：橙子也不错", "是的。"),
        ("第4轮：我还喜欢葡萄", "好的。"),  # 第1轮将被移出
        ("第5轮：草莓很美味", "确实。"),    # 第2轮将被移出
    ]

    for user_msg, ai_msg in conversations:
        manager.add_exchange(user_msg, ai_msg)
        info = manager.get_window_info()
        print(f"{user_msg}")
        print(f"  窗口内: {info['current_turns']}轮, 已归档: {info['archived_turns']}轮\n")

    print("\n最终窗口内容:")
    for msg in manager.messages:
        print(f"  {msg.__class__.__name__}: {msg.content}")


def demo_priority_preservation():
    """示例4: 优先级保留策略"""
    print_section("示例4: 优先级保留策略")

    class PriorityMessage:
        """带优先级的消息"""

        def __init__(self, message: BaseMessage, priority: int = 0):
            self.message = message
            self.priority = priority  # 数字越大优先级越高
            self.timestamp = 0

    class PriorityPreservationManager:
        """优先级保留管理器"""

        def __init__(self, max_messages: int = 10):
            self.max_messages = max_messages
            self.messages: List[PriorityMessage] = []
            self.counter = 0

        def add_message(self, message: BaseMessage, priority: int = 0):
            """添加带优先级的消息"""
            pmsg = PriorityMessage(message, priority)
            pmsg.timestamp = self.counter
            self.counter += 1
            self.messages.append(pmsg)

            self._trim()

        def _trim(self):
            """根据优先级修剪消息"""
            if len(self.messages) <= self.max_messages:
                return

            # 按优先级排序（优先级高的在前，相同优先级按时间戳排序）
            sorted_msgs = sorted(
                self.messages,
                key=lambda x: (-x.priority, -x.timestamp)
            )

            # 保留优先级最高的消息
            self.messages = sorted_msgs[:self.max_messages]

            # 恢复时间顺序
            self.messages.sort(key=lambda x: x.timestamp)

            print(f"  [修剪] 保留 {len(self.messages)} 条消息（按优先级）")

        def get_messages(self) -> List[BaseMessage]:
            """获取消息列表"""
            return [pm.message for pm in self.messages]

        def show_messages(self):
            """显示所有消息及其优先级"""
            print("\n当前消息列表:")
            for pm in self.messages:
                content = pm.message.content[:40]
                print(f"  [P{pm.priority}] {pm.message.__class__.__name__}: {content}...")

    manager = PriorityPreservationManager(max_messages=6)

    print("优先级保留策略（最多保留6条消息）\n")

    # 添加不同优先级的消息
    messages = [
        (HumanMessage(content="普通消息1"), 0),
        (AIMessage(content="普通回复1"), 0),
        (HumanMessage(content="【重要】用户的关键信息"), 5),
        (AIMessage(content="【重要】确认收到"), 5),
        (HumanMessage(content="普通消息2"), 0),
        (AIMessage(content="普通回复2"), 0),
        (HumanMessage(content="普通消息3"), 0),
        (AIMessage(content="普通回复3"), 0),
        (HumanMessage(content="【重要】需要记住的信息"), 5),
    ]

    for i, (msg, priority) in enumerate(messages, 1):
        print(f"添加消息 {i} (优先级: {priority})")
        manager.add_message(msg, priority)

    manager.show_messages()


def demo_smart_compression():
    """示例5: 智能压缩策略"""
    print_section("示例5: 智能压缩策略")

    class SmartCompressor:
        """智能压缩管理器"""

        def __init__(self, max_tokens: int = 1000):
            self.max_tokens = max_tokens
            self.messages: List[BaseMessage] = []
            self.llm = init_llm()
            self.system_message = SystemMessage(content="你是一个助手。")

        def add_message(self, message: BaseMessage):
            """添加消息"""
            self.messages.append(message)
            self._compress_if_needed()

        def _compress_if_needed(self):
            """如果需要则压缩"""
            total_tokens = self._count_tokens()

            if total_tokens > self.max_tokens and len(self.messages) > 4:
                print(f"  [压缩] 当前 {total_tokens} tokens，开始压缩...")
                self._compress_old_messages()

        def _count_tokens(self) -> int:
            """计算总token数"""
            total = estimate_tokens(self.system_message.content)
            for msg in self.messages:
                total += estimate_tokens(msg.content)
            return total

        def _compress_old_messages(self):
            """压缩旧消息"""
            # 保留最近2轮对话，压缩其余
            recent_messages = self.messages[-4:]  # 最近2轮（4条消息）
            old_messages = self.messages[:-4]

            if not old_messages:
                return

            # 生成摘要
            summary_text = "历史对话摘要：\n"
            for msg in old_messages:
                role = "用户" if isinstance(msg, HumanMessage) else "助手"
                summary_text += f"{role}: {msg.content}\n"

            # 用LLM生成压缩摘要
            summary_prompt = f"请将以下对话压缩成简短摘要（不超过50字）：\n\n{summary_text}"

            try:
                response = self.llm.invoke([HumanMessage(content=summary_prompt)])
                summary = response.content

                # 替换旧消息为摘要
                self.messages = [
                    SystemMessage(content=f"[历史摘要] {summary}")
                ] + recent_messages

                print(f"  ✓ 已压缩 {len(old_messages)} 条旧消息")
                print(f"  摘要: {summary[:50]}...")
            except Exception as e:
                print(f"  压缩失败: {e}")

        def get_messages(self) -> List[BaseMessage]:
            """获取消息"""
            return [self.system_message] + self.messages

    compressor = SmartCompressor(max_tokens=400)

    print("智能压缩策略（Token限制: 400）\n")

    conversations = [
        ("我昨天去了公园", "听起来不错。"),
        ("看到了很多花", "一定很美。"),
        ("还遇到了老朋友", "真巧！"),
        ("我们聊了很久", "很开心吧。"),
        ("谈到了工作的事情", "是吗？"),
        ("现在想问你一个新问题", "请说。"),
    ]

    for user_msg, ai_msg in conversations:
        print(f"用户: {user_msg}")
        compressor.add_message(HumanMessage(content=user_msg))
        compressor.add_message(AIMessage(content=ai_msg))
        print(f"AI: {ai_msg}")
        print(f"  当前tokens: {compressor._count_tokens()}\n")


def demo_hybrid_strategy():
    """示例6: 混合策略"""
    print_section("示例6: 混合策略")

    class HybridContextManager:
        """混合上下文管理器：结合多种策略"""

        def __init__(
            self,
            max_tokens: int = 2000,
            window_size: int = 5,
            preserve_system: bool = True
        ):
            self.max_tokens = max_tokens
            self.window_size = window_size
            self.preserve_system = preserve_system

            self.system_messages: List[BaseMessage] = []
            self.important_messages: List[BaseMessage] = []
            self.recent_messages: List[BaseMessage] = []

        def add_message(self, message: BaseMessage, is_important: bool = False):
            """添加消息"""
            if isinstance(message, SystemMessage):
                self.system_messages.append(message)
            elif is_important:
                self.important_messages.append(message)
            else:
                self.recent_messages.append(message)

                # 维持窗口大小
                if len(self.recent_messages) > self.window_size * 2:
                    self.recent_messages.pop(0)

        def get_messages(self) -> List[BaseMessage]:
            """获取优化后的消息列表"""
            messages = []

            # 1. 系统消息
            if self.preserve_system:
                messages.extend(self.system_messages)

            # 2. 重要消息
            messages.extend(self.important_messages)

            # 3. 最近消息
            messages.extend(self.recent_messages)

            # 4. Token检查和截断
            total_tokens = sum(estimate_tokens(m.content) for m in messages)

            while total_tokens > self.max_tokens and len(self.recent_messages) > 2:
                removed = self.recent_messages.pop(0)
                messages.remove(removed)
                total_tokens -= estimate_tokens(removed.content)

            return messages

        def get_stats(self) -> Dict[str, Any]:
            """获取统计信息"""
            messages = self.get_messages()
            return {
                'system_count': len(self.system_messages),
                'important_count': len(self.important_messages),
                'recent_count': len(self.recent_messages),
                'total_count': len(messages),
                'total_tokens': sum(estimate_tokens(m.content) for m in messages)
            }

    manager = HybridContextManager(max_tokens=800, window_size=3)

    print("混合策略管理器\n")

    # 添加系统消息
    manager.add_message(SystemMessage(content="你是一个智能助手。"))

    # 添加对话
    conversations = [
        (HumanMessage(content="我叫Alice"), False),
        (AIMessage(content="你好Alice！"), False),
        (HumanMessage(content="我的电话是123456"), True),  # 重要
        (AIMessage(content="已记录"), False),
        (HumanMessage(content="今天天气不错"), False),
        (AIMessage(content="是的"), False),
        (HumanMessage(content="我住在北京"), True),  # 重要
        (AIMessage(content="明白"), False),
        (HumanMessage(content="周末去哪玩？"), False),
    ]

    for msg, is_important in conversations:
        flag = "[重要]" if is_important else ""
        print(f"{flag} {msg.__class__.__name__}: {msg.content}")
        manager.add_message(msg, is_important)

    print("\n\n管理器统计:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n保留的消息:")
    for msg in manager.get_messages():
        print(f"  {msg.__class__.__name__}: {msg.content}")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 上下文窗口管理")
    print("="*70)

    try:
        demo_token_counting()
        demo_simple_truncation()
        demo_sliding_window()
        demo_priority_preservation()
        demo_smart_compression()
        demo_hybrid_strategy()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
