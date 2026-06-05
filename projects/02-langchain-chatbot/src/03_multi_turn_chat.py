"""
LangChain 聊天机器人 - 03: 多轮对话管理

本模块演示：
1. 多轮对话的上下文维护
2. 话题切换和追踪
3. 会话管理和恢复
4. 对话状态管理
5. 用户意图识别
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory


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


class ConversationState(Enum):
    """对话状态枚举"""
    GREETING = "greeting"          # 问候
    INFO_GATHERING = "info_gathering"  # 信息收集
    QUESTION_ANSWERING = "question_answering"  # 问题回答
    TASK_EXECUTION = "task_execution"  # 任务执行
    ENDING = "ending"              # 结束


class Topic(Enum):
    """话题枚举"""
    GENERAL = "general"            # 一般对话
    TECHNICAL = "technical"        # 技术讨论
    PERSONAL = "personal"          # 个人信息
    BUSINESS = "business"          # 商务相关
    UNKNOWN = "unknown"            # 未知话题


class MultiTurnConversation:
    """多轮对话管理器"""

    def __init__(self, system_prompt: str = "你是一个友好的AI助手。"):
        """初始化对话管理器"""
        self.llm = init_llm()
        self.messages: List[Any] = [SystemMessage(content=system_prompt)]
        self.current_topic = Topic.GENERAL
        self.state = ConversationState.GREETING
        self.user_info: Dict[str, Any] = {}
        self.turn_count = 0

    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append(HumanMessage(content=content))
        self.turn_count += 1

    def add_ai_message(self, content: str):
        """添加AI消息"""
        self.messages.append(AIMessage(content=content))

    def get_response(self, user_input: str) -> str:
        """获取AI回复"""
        self.add_user_message(user_input)

        # 更新对话状态和话题
        self._update_state(user_input)
        self._detect_topic(user_input)

        # 获取回复
        response = self.llm.invoke(self.messages)
        self.add_ai_message(response.content)

        return response.content

    def _update_state(self, user_input: str):
        """更新对话状态"""
        lower_input = user_input.lower()

        if any(word in lower_input for word in ['你好', 'hello', 'hi', '嗨']):
            self.state = ConversationState.GREETING
        elif any(word in lower_input for word in ['我是', '我叫', '我的名字']):
            self.state = ConversationState.INFO_GATHERING
        elif '?' in user_input or '吗' in user_input or '什么' in user_input:
            self.state = ConversationState.QUESTION_ANSWERING
        elif any(word in lower_input for word in ['帮我', '请', '能否', '可以']):
            self.state = ConversationState.TASK_EXECUTION
        elif any(word in lower_input for word in ['再见', 'bye', '结束']):
            self.state = ConversationState.ENDING

    def _detect_topic(self, user_input: str):
        """检测对话话题"""
        lower_input = user_input.lower()

        if any(word in lower_input for word in ['编程', '代码', 'python', '技术', '算法']):
            self.current_topic = Topic.TECHNICAL
        elif any(word in lower_input for word in ['我', '名字', '年龄', '爱好']):
            self.current_topic = Topic.PERSONAL
        elif any(word in lower_input for word in ['公司', '项目', '工作', '业务']):
            self.current_topic = Topic.BUSINESS
        else:
            self.current_topic = Topic.GENERAL

    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        return f"轮次: {self.turn_count}, 状态: {self.state.value}, 话题: {self.current_topic.value}"


def demo_basic_multi_turn():
    """示例1: 基本的多轮对话"""
    print_section("示例1: 基本的多轮对话")

    conversation = MultiTurnConversation()

    conversations = [
        "你好！",
        "我叫Alice",
        "我是一名数据科学家",
        "我对机器学习很感兴趣",
        "你还记得我的名字吗？",
        "我的职业是什么？"
    ]

    print("多轮对话示例:\n")
    for user_input in conversations:
        print(f"用户: {user_input}")
        response = conversation.get_response(user_input)
        print(f"AI: {response}")
        print(f"  [{conversation.get_context_summary()}]\n")


def demo_topic_switching():
    """示例2: 话题切换追踪"""
    print_section("示例2: 话题切换追踪")

    class TopicAwareConversation(MultiTurnConversation):
        """支持话题追踪的对话管理器"""

        def __init__(self):
            super().__init__()
            self.topic_history: List[Dict[str, Any]] = []

        def get_response(self, user_input: str) -> str:
            """获取回复并追踪话题变化"""
            old_topic = self.current_topic
            response = super().get_response(user_input)

            # 记录话题变化
            if old_topic != self.current_topic:
                self.topic_history.append({
                    'turn': self.turn_count,
                    'from': old_topic.value,
                    'to': self.current_topic.value,
                    'user_input': user_input
                })

            return response

        def show_topic_switches(self):
            """显示话题切换历史"""
            if not self.topic_history:
                print("没有话题切换")
                return

            print("\n话题切换历史:")
            for switch in self.topic_history:
                print(f"  轮次 {switch['turn']}: {switch['from']} -> {switch['to']}")
                print(f"    触发: {switch['user_input'][:30]}...")

    conversation = TopicAwareConversation()

    conversations = [
        "你好！",
        "我对Python编程很感兴趣",  # -> Technical
        "我叫Bob",                    # -> Personal
        "我在一家科技公司工作",      # -> Business
        "你能帮我写一个排序算法吗？",  # -> Technical
    ]

    print("话题切换示例:\n")
    for user_input in conversations:
        print(f"用户: {user_input}")
        response = conversation.get_response(user_input)
        print(f"AI: {response}")
        print(f"  [当前话题: {conversation.current_topic.value}]\n")

    conversation.show_topic_switches()


def demo_session_management():
    """示例3: 会话管理"""
    print_section("示例3: 会话管理")

    class SessionManager:
        """会话管理器"""

        def __init__(self):
            self.sessions: Dict[str, MultiTurnConversation] = {}

        def create_session(self, session_id: str) -> MultiTurnConversation:
            """创建新会话"""
            conversation = MultiTurnConversation()
            self.sessions[session_id] = conversation
            return conversation

        def get_session(self, session_id: str) -> Optional[MultiTurnConversation]:
            """获取会话"""
            return self.sessions.get(session_id)

        def end_session(self, session_id: str):
            """结束会话"""
            if session_id in self.sessions:
                del self.sessions[session_id]

        def list_sessions(self) -> List[str]:
            """列出所有会话"""
            return list(self.sessions.keys())

    manager = SessionManager()

    # 创建两个独立的会话
    print("创建两个独立会话:\n")

    # 会话1
    session1 = manager.create_session("user_001")
    print("【会话1】")
    print("用户: 我叫Alice")
    response1 = session1.get_response("我叫Alice")
    print(f"AI: {response1}\n")

    # 会话2
    session2 = manager.create_session("user_002")
    print("【会话2】")
    print("用户: 我叫Bob")
    response2 = session2.get_response("我叫Bob")
    print(f"AI: {response2}\n")

    # 继续会话1
    print("【继续会话1】")
    print("用户: 我的名字是什么？")
    response1 = session1.get_response("我的名字是什么？")
    print(f"AI: {response1}\n")

    # 继续会话2
    print("【继续会话2】")
    print("用户: 我的名字是什么？")
    response2 = session2.get_response("我的名字是什么？")
    print(f"AI: {response2}\n")

    print(f"活跃会话: {manager.list_sessions()}")


def demo_context_maintenance():
    """示例4: 上下文维护"""
    print_section("示例4: 上下文维护")

    class ContextualConversation:
        """支持上下文维护的对话"""

        def __init__(self, max_context_turns: int = 5):
            self.llm = init_llm()
            self.max_context_turns = max_context_turns
            self.full_history: List[Dict[str, str]] = []
            self.system_message = SystemMessage(
                content="你是一个智能助手，能够维护对话上下文并进行连贯对话。"
            )

        def chat(self, user_input: str) -> str:
            """进行对话"""
            # 记录到完整历史
            self.full_history.append({'role': 'user', 'content': user_input})

            # 构建上下文（只包含最近的N轮对话）
            context_messages = [self.system_message]
            recent_history = self.full_history[-(self.max_context_turns * 2):]

            for msg in recent_history:
                if msg['role'] == 'user':
                    context_messages.append(HumanMessage(content=msg['content']))
                else:
                    context_messages.append(AIMessage(content=msg['content']))

            # 获取回复
            response = self.llm.invoke(context_messages)

            # 记录AI回复
            self.full_history.append({'role': 'assistant', 'content': response.content})

            return response.content

        def show_context_window(self):
            """显示当前上下文窗口"""
            recent = self.full_history[-(self.max_context_turns * 2):]
            print("\n当前上下文窗口:")
            for msg in recent:
                print(f"  {msg['role']}: {msg['content'][:40]}...")

    conversation = ContextualConversation(max_context_turns=3)

    conversations = [
        "我最喜欢的颜色是蓝色",
        "我也喜欢绿色",
        "我的第三个喜欢的是红色",
        "我还喜欢黄色",
        "我最后喜欢的是紫色",
        "我喜欢哪些颜色？"  # 测试上下文窗口
    ]

    print("上下文维护示例（窗口=3轮）:\n")
    for i, user_input in enumerate(conversations, 1):
        print(f"[轮次 {i}] 用户: {user_input}")
        response = conversation.chat(user_input)
        print(f"AI: {response}\n")

    conversation.show_context_window()


def demo_intent_recognition():
    """示例5: 用户意图识别"""
    print_section("示例5: 用户意图识别")

    class Intent(Enum):
        """意图类型"""
        QUESTION = "question"      # 提问
        STATEMENT = "statement"    # 陈述
        COMMAND = "command"        # 命令
        GREETING = "greeting"      # 问候
        FAREWELL = "farewell"      # 告别

    class IntentRecognizer:
        """意图识别器"""

        @staticmethod
        def recognize(text: str) -> Intent:
            """识别用户意图"""
            text_lower = text.lower()

            # 问候
            if any(word in text_lower for word in ['你好', 'hi', 'hello', '嗨']):
                return Intent.GREETING

            # 告别
            if any(word in text_lower for word in ['再见', 'bye', '拜拜']):
                return Intent.FAREWELL

            # 命令
            if any(word in text_lower for word in ['帮我', '请', '给我', '执行']):
                return Intent.COMMAND

            # 提问
            if '?' in text or '吗' in text or any(word in text for word in ['什么', '怎么', '为什么', '哪里']):
                return Intent.QUESTION

            # 默认陈述
            return Intent.STATEMENT

    class IntentAwareConversation:
        """支持意图识别的对话"""

        def __init__(self):
            self.llm = init_llm()
            self.messages = [
                SystemMessage(content="你是一个智能助手，根据用户意图提供相应的回复。")
            ]
            self.recognizer = IntentRecognizer()

        def chat(self, user_input: str) -> tuple[str, Intent]:
            """进行对话并返回意图"""
            intent = self.recognizer.recognize(user_input)

            # 根据意图调整系统行为
            if intent == Intent.GREETING:
                context = "用户在打招呼，请友好回应。"
            elif intent == Intent.QUESTION:
                context = "用户在提问，请详细回答。"
            elif intent == Intent.COMMAND:
                context = "用户在发出指令，请确认并执行。"
            elif intent == Intent.FAREWELL:
                context = "用户在告别，请礼貌回应。"
            else:
                context = "用户在陈述事实，请确认并回应。"

            # 构建带意图上下文的消息
            messages = self.messages + [
                SystemMessage(content=context),
                HumanMessage(content=user_input)
            ]

            response = self.llm.invoke(messages)

            # 更新历史
            self.messages.append(HumanMessage(content=user_input))
            self.messages.append(AIMessage(content=response.content))

            return response.content, intent

    conversation = IntentAwareConversation()

    test_inputs = [
        "你好！",
        "我叫Tom",
        "你能帮我写一段代码吗？",
        "Python是什么？",
        "再见！"
    ]

    print("意图识别示例:\n")
    for user_input in test_inputs:
        print(f"用户: {user_input}")
        response, intent = conversation.chat(user_input)
        print(f"意图: {intent.value}")
        print(f"AI: {response}\n")


def demo_conversation_recovery():
    """示例6: 对话恢复"""
    print_section("示例6: 对话恢复")

    import json

    class RecoverableConversation:
        """支持恢复的对话"""

        def __init__(self, session_id: str):
            self.session_id = session_id
            self.llm = init_llm()
            self.messages = [
                SystemMessage(content="你是一个友好的助手。")
            ]
            self.metadata = {
                'created_at': datetime.now().isoformat(),
                'turn_count': 0
            }

        def chat(self, user_input: str) -> str:
            """对话"""
            self.messages.append(HumanMessage(content=user_input))
            response = self.llm.invoke(self.messages)
            self.messages.append(AIMessage(content=response.content))
            self.metadata['turn_count'] += 1
            return response.content

        def save(self, filepath: str):
            """保存对话状态"""
            data = {
                'session_id': self.session_id,
                'metadata': self.metadata,
                'messages': [
                    {
                        'type': msg.type if hasattr(msg, 'type') else msg.__class__.__name__,
                        'content': msg.content
                    }
                    for msg in self.messages
                ]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        @classmethod
        def load(cls, filepath: str) -> 'RecoverableConversation':
            """加载对话状态"""
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            conversation = cls(data['session_id'])
            conversation.metadata = data['metadata']

            # 重建消息历史
            conversation.messages = []
            for msg_data in data['messages']:
                msg_type = msg_data['type']
                content = msg_data['content']

                if 'system' in msg_type.lower():
                    conversation.messages.append(SystemMessage(content=content))
                elif 'human' in msg_type.lower():
                    conversation.messages.append(HumanMessage(content=content))
                elif 'ai' in msg_type.lower():
                    conversation.messages.append(AIMessage(content=content))

            return conversation

    # 第一阶段对话
    print("【第一阶段对话】\n")
    conv = RecoverableConversation("session_123")

    phase1 = [
        "我叫Emma",
        "我是产品经理"
    ]

    for user_input in phase1:
        print(f"用户: {user_input}")
        response = conv.chat(user_input)
        print(f"AI: {response}\n")

    # 保存状态
    save_path = "conversation_state.json"
    conv.save(save_path)
    print(f"✓ 对话状态已保存\n")

    # 模拟中断...
    print("--- 模拟会话中断 ---\n")

    # 第二阶段：恢复对话
    print("【第二阶段：恢复对话】\n")
    recovered_conv = RecoverableConversation.load(save_path)
    print(f"✓ 对话已恢复（轮次: {recovered_conv.metadata['turn_count']}）\n")

    # 继续对话
    continuation = "我的名字和职业是什么？"
    print(f"用户: {continuation}")
    response = recovered_conv.chat(continuation)
    print(f"AI: {response}")

    # 清理
    import os
    os.unlink(save_path)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 多轮对话管理")
    print("="*70)

    try:
        demo_basic_multi_turn()
        demo_topic_switching()
        demo_session_management()
        demo_context_maintenance()
        demo_intent_recognition()
        demo_conversation_recovery()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
