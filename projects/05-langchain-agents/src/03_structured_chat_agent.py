"""
Structured Chat Agent

Structured Chat Agent是一种使用结构化对话流程的Agent类型。
它通过JSON格式来组织思考过程和行动，使得Agent的推理过程更加清晰可控。

主要特点：
1. 结构化的输入输出
2. JSON格式的思考过程
3. 明确的行动和观察记录
4. 适合复杂多轮交互
5. 易于调试和追踪

适用场景：
- 需要复杂对话流程的场景
- 需要记录详细推理过程
- 多步骤任务分解
- 结构化数据处理
"""

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory


# ============ 工具定义 ============

@tool
def search_database(query: str) -> str:
    """
    搜索数据库

    Args:
        query: 搜索关键词

    Returns:
        搜索结果
    """
    # 模拟数据库查询
    database = {
        "Python": "一种高级编程语言，广泛用于Web开发、数据科学和AI",
        "JavaScript": "主要用于Web前端开发的脚本语言",
        "Java": "面向对象的编程语言，具有跨平台特性",
    }

    result = database.get(query, f"未找到关于'{query}'的信息")
    return result


@tool
def calculate(expression: str) -> str:
    """
    执行数学计算

    Args:
        expression: 数学表达式

    Returns:
        计算结果
    """
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_user_info(user_id: str) -> str:
    """
    获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        用户信息
    """
    users = {
        "001": {"name": "张三", "age": 25, "city": "北京"},
        "002": {"name": "李四", "age": 30, "city": "上海"},
        "003": {"name": "王五", "age": 28, "city": "广州"},
    }

    if user_id in users:
        info = users[user_id]
        return f"用户{user_id}: {info['name']}, {info['age']}岁, 来自{info['city']}"
    else:
        return f"未找到用户{user_id}"


@tool
def format_data(data: str, format_type: str) -> str:
    """
    格式化数据

    Args:
        data: 原始数据
        format_type: 格式类型（uppercase/lowercase/title）

    Returns:
        格式化后的数据
    """
    if format_type == "uppercase":
        return data.upper()
    elif format_type == "lowercase":
        return data.lower()
    elif format_type == "title":
        return data.title()
    else:
        return data


# ============ 示例函数 ============

def example_1_basic_structured_chat():
    """示例1: 基础Structured Chat Agent"""
    print("\n" + "="*60)
    print("示例1: 基础Structured Chat Agent")
    print("="*60)

    print("\n💡 说明:")
    print("Structured Chat Agent使用JSON格式组织对话")
    print("使得推理过程更加清晰和可控\n")

    # 初始化LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 定义工具
    tools = [search_database, calculate]

    # 创建Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个有用的AI助手。

使用以下格式进行思考和行动：

思考：我需要做什么？
行动：选择一个工具
行动输入：工具的输入
观察：工具返回的结果

当你知道最终答案时：
思考：我现在知道答案了
最终答案：[你的答案]
"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建Agent
    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    # 测试查询
    questions = [
        "Python是什么？",
        "计算 25 * 4 + 10",
        "先告诉我JavaScript是什么，然后计算100除以5"
    ]

    for question in questions:
        print(f"\n❓ 问题: {question}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": question})
            print(f"✅ 回答: {result['output']}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def example_2_multi_turn_interaction():
    """示例2: 多轮交互"""
    print("\n" + "="*60)
    print("示例2: 多轮交互")
    print("="*60)

    print("\n💡 说明:")
    print("Structured Chat Agent支持复杂的多轮对话\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [get_user_info, calculate]

    # 添加记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个用户管理助手，可以查询用户信息和进行计算。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True
    )

    # 多轮对话
    conversations = [
        "查询用户001的信息",
        "他今年多大了？",  # 依赖上一轮的上下文
        "如果他再过5年，会是多少岁？"  # 需要计算
    ]

    for i, user_input in enumerate(conversations, 1):
        print(f"\n第{i}轮对话:")
        print(f"用户: {user_input}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"助手: {result['output']}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def example_3_complex_workflow():
    """示例3: 复杂工作流"""
    print("\n" + "="*60)
    print("示例3: 复杂工作流")
    print("="*60)

    print("\n💡 说明:")
    print("处理需要多个步骤的复杂任务\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [search_database, calculate, format_data]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个任务处理助手。

对于复杂任务，你需要：
1. 分析任务，确定步骤
2. 逐步执行每个步骤
3. 整合结果，给出最终答案

使用工具来完成每个步骤。"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10  # 允许更多迭代
    )

    # 复杂任务
    task = "查找Python的信息，然后将结果转换为大写格式"

    print(f"任务: {task}")
    print("-" * 40)
    try:
        result = agent_executor.invoke({"input": task})
        print(f"\n最终结果: {result['output']}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def example_4_json_output():
    """示例4: JSON格式输出"""
    print("\n" + "="*60)
    print("示例4: JSON格式输出")
    print("="*60)

    print("\n💡 说明:")
    print("Structured Chat Agent的输出可以是JSON格式")
    print("便于程序处理和数据交换\n")

    print("结构化输出的优势:")
    print("1. 易于解析和处理")
    print("2. 明确的数据结构")
    print("3. 便于集成到其他系统")
    print("4. 支持复杂的数据类型")


def example_5_comparison():
    """示例5: 与其他Agent类型对比"""
    print("\n" + "="*60)
    print("示例5: Structured Chat Agent vs 其他Agent")
    print("="*60)

    print("\n📊 对比分析:\n")

    print("1. Structured Chat Agent")
    print("   优势:")
    print("   - 结构化的思考过程")
    print("   - JSON格式易于处理")
    print("   - 适合复杂多轮对话")
    print("   缺点:")
    print("   - 相对冗长的输出")
    print("   - 需要更多tokens")
    print()

    print("2. ReAct Agent")
    print("   优势:")
    print("   - 简洁的推理格式")
    print("   - 直观易懂")
    print("   缺点:")
    print("   - 文本解析可能出错")
    print()

    print("3. OpenAI Functions Agent")
    print("   优势:")
    print("   - 精确的参数提取")
    print("   - 原生API支持")
    print("   缺点:")
    print("   - 仅支持OpenAI模型")
    print()

    print("选择建议:")
    print("- 简单任务 → ReAct Agent")
    print("- 需要精确参数 → Functions Agent")
    print("- 复杂多轮对话 → Structured Chat Agent")


def example_6_error_recovery():
    """示例6: 错误恢复"""
    print("\n" + "="*60)
    print("示例6: 错误恢复机制")
    print("="*60)

    print("\n💡 说明:")
    print("Structured Chat Agent可以从错误中恢复\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [calculate, search_database]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个助手。

如果工具返回错误：
1. 分析错误原因
2. 尝试修正输入
3. 重新调用工具
4. 如果仍然失败，告诉用户

最多尝试3次。"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    # 可能出错的查询
    queries = [
        "计算 10 除以 0",  # 会出错
        "查询一个不存在的内容"
    ]

    for query in queries:
        print(f"\n问题: {query}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": query})
            print(f"回答: {result['output']}")
        except Exception as e:
            print(f"❌ 最终错误: {e}")


def example_7_use_cases():
    """示例7: 适用场景"""
    print("\n" + "="*60)
    print("示例7: Structured Chat Agent适用场景")
    print("="*60)

    print("\n✅ 最适合的场景:\n")

    print("1. 复杂对话系统")
    print("   - 客服机器人")
    print("   - 虚拟助手")
    print("   - 交互式问答")
    print()

    print("2. 多步骤任务")
    print("   - 数据处理流程")
    print("   - 复杂查询")
    print("   - 工作流自动化")
    print()

    print("3. 需要详细日志")
    print("   - 审计追踪")
    print("   - 调试分析")
    print("   - 过程记录")
    print()

    print("4. 结构化数据处理")
    print("   - API集成")
    print("   - 数据转换")
    print("   - 报告生成")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*12 + "Structured Chat Agent教程")
    print("="*60)

    # 运行示例
    try:
        example_1_basic_structured_chat()
    except Exception as e:
        print(f"示例1执行出错（可能需要API Key）: {e}")

    try:
        example_2_multi_turn_interaction()
    except Exception as e:
        print(f"示例2执行出错: {e}")

    try:
        example_3_complex_workflow()
    except Exception as e:
        print(f"示例3执行出错: {e}")

    example_4_json_output()
    example_5_comparison()

    try:
        example_6_error_recovery()
    except Exception as e:
        print(f"示例6执行出错: {e}")

    example_7_use_cases()

    print("\n" + "="*60)
    print("✅ 教程完成")
    print("="*60)
    print("\n💡 提示:")
    print("- Structured Chat Agent适合复杂对话场景")
    print("- 推理过程结构化，易于调试")
    print("- 支持多轮交互和错误恢复")
