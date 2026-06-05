"""
带记忆的对话式Agent实现
功能：对话上下文管理、多轮交互、会话状态维护、多种记忆类型
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool, tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory,
    ConversationTokenBufferMemory,
)
from langchain.schema import BaseMemory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# ============================================================================
# 工具定义
# ============================================================================

@tool
def calculate(expression: str) -> str:
    """执行数学计算。例如: '2 + 2' 或 '10 * 5'"""
    try:
        # 安全评估数学表达式
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，温度25°C，湿度60%",
        "上海": "多云，温度28°C，湿度75%",
        "广州": "小雨，温度30°C，湿度85%",
        "深圳": "阴天，温度29°C，湿度80%",
    }
    return weather_data.get(city, f"{city}的天气信息暂时无法获取")


@tool
def save_note(note: str) -> str:
    """保存用户的笔记或备忘录"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"笔记已保存 [{timestamp}]: {note}"


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库中的信息"""
    # 模拟知识库
    knowledge_base = {
        "python": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名",
        "langchain": "LangChain是一个用于构建语言模型应用的框架",
        "agent": "Agent是能够自主决策和使用工具的智能体",
        "记忆": "记忆系统允许Agent保持对话上下文和历史信息",
    }

    for key, value in knowledge_base.items():
        if key in query.lower():
            return f"找到相关信息: {value}"

    return f"未找到关于'{query}'的信息"


@tool
def get_time() -> str:
    """获取当前时间"""
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# ============================================================================
# 记忆类型枚举
# ============================================================================

class MemoryType(Enum):
    """记忆类型枚举"""
    BUFFER = "buffer"  # 完整缓冲记忆
    WINDOW = "window"  # 窗口记忆（保留最近N轮）
    SUMMARY = "summary"  # 摘要记忆
    SUMMARY_BUFFER = "summary_buffer"  # 摘要+缓冲混合
    TOKEN_BUFFER = "token_buffer"  # 基于token限制的记忆


# ============================================================================
# 记忆工厂类
# ============================================================================

class MemoryFactory:
    """记忆系统工厂类，用于创建不同类型的记忆"""

    @staticmethod
    def create_memory(
        memory_type: MemoryType,
        llm: Optional[ChatOpenAI] = None,
        **kwargs
    ) -> BaseMemory:
        """
        创建指定类型的记忆系统

        Args:
            memory_type: 记忆类型
            llm: 语言模型（某些记忆类型需要）
            **kwargs: 额外参数

        Returns:
            BaseMemory: 记忆实例
        """
        memory_key = kwargs.get("memory_key", "chat_history")
        return_messages = kwargs.get("return_messages", True)

        if memory_type == MemoryType.BUFFER:
            # 完整缓冲记忆：保存所有对话历史
            return ConversationBufferMemory(
                memory_key=memory_key,
                return_messages=return_messages
            )

        elif memory_type == MemoryType.WINDOW:
            # 窗口记忆：只保留最近k轮对话
            k = kwargs.get("k", 5)
            return ConversationBufferWindowMemory(
                memory_key=memory_key,
                return_messages=return_messages,
                k=k
            )

        elif memory_type == MemoryType.SUMMARY:
            # 摘要记忆：自动总结历史对话
            if llm is None:
                raise ValueError("SUMMARY memory type requires an LLM")
            return ConversationSummaryMemory(
                llm=llm,
                memory_key=memory_key,
                return_messages=return_messages
            )

        elif memory_type == MemoryType.SUMMARY_BUFFER:
            # 摘要+缓冲混合：保留最近的对话 + 旧对话的摘要
            if llm is None:
                raise ValueError("SUMMARY_BUFFER memory type requires an LLM")
            max_token_limit = kwargs.get("max_token_limit", 2000)
            return ConversationSummaryBufferMemory(
                llm=llm,
                memory_key=memory_key,
                return_messages=return_messages,
                max_token_limit=max_token_limit
            )

        elif memory_type == MemoryType.TOKEN_BUFFER:
            # Token缓冲记忆：基于token数量限制
            if llm is None:
                raise ValueError("TOKEN_BUFFER memory type requires an LLM")
            max_token_limit = kwargs.get("max_token_limit", 2000)
            return ConversationTokenBufferMemory(
                llm=llm,
                memory_key=memory_key,
                return_messages=return_messages,
                max_token_limit=max_token_limit
            )

        else:
            raise ValueError(f"Unknown memory type: {memory_type}")


# ============================================================================
# 对话式Agent类
# ============================================================================

class ConversationalAgent:
    """带记忆的对话式Agent"""

    def __init__(
        self,
        memory_type: MemoryType = MemoryType.BUFFER,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        memory_kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        初始化对话式Agent

        Args:
            memory_type: 记忆类型
            model_name: 模型名称
            temperature: 温度参数
            memory_kwargs: 记忆系统的额外参数
        """
        self.memory_type = memory_type
        self.model_name = model_name
        self.temperature = temperature

        # 初始化LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )

        # 创建记忆系统
        memory_kwargs = memory_kwargs or {}
        self.memory = MemoryFactory.create_memory(
            memory_type=memory_type,
            llm=self.llm,
            **memory_kwargs
        )

        # 创建工具列表
        self.tools = [
            calculate,
            get_weather,
            save_note,
            search_knowledge,
            get_time
        ]

        # 创建Agent
        self.agent_executor = self._create_agent()

        # 会话状态
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.turn_count = 0

    def _create_agent(self) -> AgentExecutor:
        """创建Agent执行器"""
        # 定义提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能助手，能够进行多轮对话并记住之前的对话内容。

你的能力：
1. 记住整个对话历史，能够引用之前的对话内容
2. 使用工具完成各种任务
3. 理解上下文，提供连贯的回答
4. 主动关联相关信息

请保持友好、专业的态度，并充分利用对话历史来提供更好的服务。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 创建Agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # 创建Agent执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        return agent_executor

    def chat(self, user_input: str) -> str:
        """
        与Agent进行对话

        Args:
            user_input: 用户输入

        Returns:
            str: Agent的回复
        """
        self.turn_count += 1

        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            return f"处理消息时出错: {str(e)}"

    def get_memory_info(self) -> Dict[str, Any]:
        """获取记忆系统信息"""
        memory_vars = self.memory.load_memory_variables({})

        info = {
            "memory_type": self.memory_type.value,
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "memory_content": memory_vars
        }

        return info

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
        self.turn_count = 0
        print("记忆已清空")

    def export_conversation(self) -> List[Dict[str, str]]:
        """导出对话历史"""
        memory_vars = self.memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", [])

        conversation = []
        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                conversation.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                conversation.append({"role": "assistant", "content": msg.content})

        return conversation


# ============================================================================
# 对话管理器类
# ============================================================================

class ConversationManager:
    """对话管理器，用于管理多个对话会话"""

    def __init__(self):
        """初始化对话管理器"""
        self.sessions: Dict[str, ConversationalAgent] = {}

    def create_session(
        self,
        session_id: str,
        memory_type: MemoryType = MemoryType.BUFFER,
        **kwargs
    ) -> ConversationalAgent:
        """
        创建新的对话会话

        Args:
            session_id: 会话ID
            memory_type: 记忆类型
            **kwargs: 额外参数

        Returns:
            ConversationalAgent: Agent实例
        """
        agent = ConversationalAgent(
            memory_type=memory_type,
            **kwargs
        )
        self.sessions[session_id] = agent
        return agent

    def get_session(self, session_id: str) -> Optional[ConversationalAgent]:
        """获取指定会话"""
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        """删除指定会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self.sessions.keys())


# ============================================================================
# 示例函数
# ============================================================================

def example_1_basic_conversation():
    """示例1: 基础多轮对话"""
    print("\n" + "="*80)
    print("示例1: 基础多轮对话（使用完整缓冲记忆）")
    print("="*80 + "\n")

    agent = ConversationalAgent(memory_type=MemoryType.BUFFER)

    # 第一轮对话
    print("用户: 我叫张三，今年25岁")
    response = agent.chat("我叫张三，今年25岁")
    print(f"Agent: {response}\n")

    # 第二轮对话
    print("用户: 你还记得我的名字吗？")
    response = agent.chat("你还记得我的名字吗？")
    print(f"Agent: {response}\n")

    # 第三轮对话
    print("用户: 我今年多大了？")
    response = agent.chat("我今年多大了？")
    print(f"Agent: {response}\n")


def example_2_window_memory():
    """示例2: 窗口记忆（只保留最近3轮对话）"""
    print("\n" + "="*80)
    print("示例2: 窗口记忆（只保留最近3轮对话）")
    print("="*80 + "\n")

    agent = ConversationalAgent(
        memory_type=MemoryType.WINDOW,
        memory_kwargs={"k": 3}  # 只保留最近3轮
    )

    conversations = [
        "我最喜欢的颜色是蓝色",
        "我住在北京",
        "我是一名工程师",
        "我的爱好是摄影",
        "你还记得我最喜欢的颜色吗？",  # 这个信息应该被遗忘了
        "你知道我住在哪里吗？"  # 这个信息还在窗口内
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = agent.chat(user_input)
        print(f"Agent: {response}\n")


def example_3_tool_usage_with_memory():
    """示例3: 带记忆的工具使用"""
    print("\n" + "="*80)
    print("示例3: 带记忆的工具使用")
    print("="*80 + "\n")

    agent = ConversationalAgent(memory_type=MemoryType.BUFFER)

    # 进行多轮对话，涉及工具使用
    conversations = [
        "北京今天天气怎么样？",
        "上海呢？",  # 测试上下文理解
        "帮我保存一条笔记：明天上午10点开会",
        "我刚才让你保存的笔记内容是什么？",  # 测试记忆
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = agent.chat(user_input)
        print(f"Agent: {response}\n")


def example_4_context_awareness():
    """示例4: 上下文感知对话"""
    print("\n" + "="*80)
    print("示例4: 上下文感知对话")
    print("="*80 + "\n")

    agent = ConversationalAgent(memory_type=MemoryType.BUFFER)

    conversations = [
        "帮我计算 15 + 27",
        "再乘以2呢？",  # 需要理解上文的计算结果
        "把这个结果减去50",  # 继续基于前面的结果
        "最终结果是多少？"
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = agent.chat(user_input)
        print(f"Agent: {response}\n")


def example_5_memory_inspection():
    """示例5: 检查和管理记忆"""
    print("\n" + "="*80)
    print("示例5: 检查和管理记忆")
    print("="*80 + "\n")

    agent = ConversationalAgent(memory_type=MemoryType.BUFFER)

    # 进行几轮对话
    agent.chat("我的生日是5月20日")
    agent.chat("我喜欢吃披萨")
    agent.chat("我在学习Python")

    # 检查记忆信息
    print("\n--- 记忆信息 ---")
    memory_info = agent.get_memory_info()
    print(f"记忆类型: {memory_info['memory_type']}")
    print(f"会话ID: {memory_info['session_id']}")
    print(f"对话轮数: {memory_info['turn_count']}")

    # 导出对话历史
    print("\n--- 对话历史 ---")
    conversation = agent.export_conversation()
    for i, turn in enumerate(conversation, 1):
        print(f"{i}. {turn['role']}: {turn['content']}")

    # 清空记忆
    print("\n--- 清空记忆 ---")
    agent.clear_memory()

    # 验证记忆已清空
    print("\n用户: 你还记得我的生日吗？")
    response = agent.chat("你还记得我的生日吗？")
    print(f"Agent: {response}")


def example_6_session_management():
    """示例6: 多会话管理"""
    print("\n" + "="*80)
    print("示例6: 多会话管理")
    print("="*80 + "\n")

    manager = ConversationManager()

    # 创建用户A的会话
    print("--- 用户A的会话 ---")
    agent_a = manager.create_session("user_a", memory_type=MemoryType.BUFFER)
    agent_a.chat("我叫Alice，我喜欢编程")
    response = agent_a.chat("你记得我的名字吗？")
    print(f"用户A的回复: {response}\n")

    # 创建用户B的会话
    print("--- 用户B的会话 ---")
    agent_b = manager.create_session("user_b", memory_type=MemoryType.BUFFER)
    agent_b.chat("我是Bob，我在学习机器学习")
    response = agent_b.chat("你知道我在学什么吗？")
    print(f"用户B的回复: {response}\n")

    # 切回用户A的会话
    print("--- 切回用户A的会话 ---")
    agent_a = manager.get_session("user_a")
    response = agent_a.chat("我喜欢什么？")
    print(f"用户A的回复: {response}\n")

    # 列出所有会话
    print(f"当前活跃会话: {manager.list_sessions()}")


def example_7_complex_conversation():
    """示例7: 复杂对话场景"""
    print("\n" + "="*80)
    print("示例7: 复杂对话场景")
    print("="*80 + "\n")

    agent = ConversationalAgent(memory_type=MemoryType.BUFFER)

    conversations = [
        "我计划下周去北京出差",
        "帮我查一下北京的天气",
        "那我需要带伞吗？",  # 基于天气信息
        "帮我保存一条笔记：记得带雨伞",
        "我什么时候去北京来着？",  # 测试远距离记忆
        "现在几点了？",
    ]

    for user_input in conversations:
        print(f"用户: {user_input}")
        response = agent.chat(user_input)
        print(f"Agent: {response}\n")


def example_8_memory_comparison():
    """示例8: 不同记忆类型对比"""
    print("\n" + "="*80)
    print("示例8: 不同记忆类型对比")
    print("="*80 + "\n")

    # 测试对话序列
    test_conversations = [
        "第一件事：我的车牌号是京A12345",
        "第二件事：我住在朝阳区",
        "第三件事：我的手机号是13800138000",
        "第四件事：我在科技公司工作",
        "第五件事：我养了一只猫叫小白",
        "请问你记得我的车牌号吗？",  # 测试记忆
    ]

    # 测试完整缓冲记忆
    print("--- 完整缓冲记忆 (BUFFER) ---")
    agent_buffer = ConversationalAgent(memory_type=MemoryType.BUFFER)
    for conv in test_conversations:
        response = agent_buffer.chat(conv)
        if "车牌号" in conv:
            print(f"用户: {conv}")
            print(f"Agent: {response}\n")

    # 测试窗口记忆（k=2）
    print("\n--- 窗口记忆 (WINDOW, k=2) ---")
    agent_window = ConversationalAgent(
        memory_type=MemoryType.WINDOW,
        memory_kwargs={"k": 2}
    )
    for conv in test_conversations:
        response = agent_window.chat(conv)
        if "车牌号" in conv:
            print(f"用户: {conv}")
            print(f"Agent: {response}\n")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数，运行所有示例"""
    print("\n" + "="*80)
    print("对话式Agent示例集合")
    print("="*80)

    examples = [
        ("基础多轮对话", example_1_basic_conversation),
        ("窗口记忆", example_2_window_memory),
        ("带记忆的工具使用", example_3_tool_usage_with_memory),
        ("上下文感知对话", example_4_context_awareness),
        ("检查和管理记忆", example_5_memory_inspection),
        ("多会话管理", example_6_session_management),
        ("复杂对话场景", example_7_complex_conversation),
        ("不同记忆类型对比", example_8_memory_comparison),
    ]

    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'='*80}")
        print(f"运行示例 {i}/{len(examples)}: {name}")
        print(f"{'='*80}")

        try:
            func()
        except Exception as e:
            print(f"示例运行出错: {str(e)}")

        if i < len(examples):
            input("\n按回车键继续下一个示例...")


if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: 未设置 OPENAI_API_KEY 环境变量")
        print("请设置后再运行示例")
    else:
        main()
