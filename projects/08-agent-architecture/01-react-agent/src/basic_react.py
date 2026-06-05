"""
ReAct Agent 基础实现
ReAct = Reasoning + Acting（推理 + 行动）

核心思想：
1. Thought（思考）：分析当前状态，决定下一步
2. Action（行动）：选择并执行一个工具
3. Observation（观察）：获取工具执行结果
4. 重复上述过程直到任务完成

这是最经典的 Agent 模式，适用于大多数场景。
"""

import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

# 加载环境变量
load_dotenv()


# ============ 定义工具 ============

def search_weather(location: str) -> str:
    """
    查询天气信息（模拟）

    参数:
        location: 地点名称
    返回:
        天气信息字符串
    """
    # 实际应用中这里应该调用真实的天气API
    weather_data = {
        "北京": "晴天，温度25°C，湿度60%",
        "上海": "多云，温度28°C，湿度75%",
        "深圳": "雨天，温度26°C，湿度85%"
    }

    return weather_data.get(location, f"{location}的天气：晴天，温度22°C")


def calculate(expression: str) -> str:
    """
    计算数学表达式

    参数:
        expression: 数学表达式字符串，如 "2 + 3 * 4"
    返回:
        计算结果字符串
    """
    try:
        # 注意：生产环境中应该使用更安全的表达式求值方式
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def search_web(query: str) -> str:
    """
    网络搜索（模拟）

    参数:
        query: 搜索关键词
    返回:
        搜索结果摘要
    """
    # 实际应用中应该调用真实的搜索API（如Google、Bing等）
    mock_results = {
        "Python": "Python是一种高级编程语言，由Guido van Rossum创建...",
        "AI": "人工智能(AI)是计算机科学的一个分支，旨在创建智能机器...",
        "LangChain": "LangChain是一个用于开发由语言模型驱动的应用程序的框架..."
    }

    for key in mock_results:
        if key.lower() in query.lower():
            return mock_results[key]

    return f"搜索'{query}'的结果：找到相关信息..."


# 创建工具列表
tools = [
    Tool(
        name="Weather",
        func=search_weather,
        description="查询指定地点的天气信息。输入应该是一个地点名称，如'北京'、'上海'等。"
    ),
    Tool(
        name="Calculator",
        func=calculate,
        description="执行数学计算。输入应该是一个数学表达式，如'2 + 3'、'10 * 5 + 2'等。"
    ),
    Tool(
        name="Search",
        func=search_web,
        description="在网络上搜索信息。输入应该是搜索关键词或问题。"
    )
]


# ============ 创建 ReAct Prompt ============

# 自定义 ReAct 提示模板（中文版）
react_prompt_template = """你是一个智能助手，能够使用工具来帮助用户解决问题。

你有以下工具可以使用：

{tools}

使用以下格式来回答问题：

Question: 用户提出的问题
Thought: 你应该思考接下来要做什么
Action: 要使用的工具，必须是 [{tool_names}] 中的一个
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (可以重复 Thought/Action/Action Input/Observation 多次)
Thought: 我现在知道最终答案了
Final Answer: 对原始问题的最终答案

注意事项：
- 必须严格遵循上述格式
- 每次只能调用一个工具
- 必须基于 Observation 的结果来决定下一步
- 如果不需要使用工具，直接给出 Final Answer

开始！

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate(
    template=react_prompt_template,
    input_variables=["input", "agent_scratchpad"],
    partial_variables={
        "tools": "\n".join([f"- {tool.name}: {tool.description}" for tool in tools]),
        "tool_names": ", ".join([tool.name for tool in tools])
    }
)


# ============ 创建 Agent ============

def create_basic_react_agent():
    """
    创建基础的 ReAct Agent

    返回:
        AgentExecutor: 可执行的 Agent
    """
    # 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,  # 降低温度使输出更加确定
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 创建 ReAct Agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # 创建 Agent 执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 显示详细执行过程
        max_iterations=5,  # 最大迭代次数，防止无限循环
        handle_parsing_errors=True,  # 自动处理解析错误
        return_intermediate_steps=True  # 返回中间步骤
    )

    return agent_executor


# ============ 测试示例 ============

def run_examples():
    """运行示例测试"""

    print("=" * 80)
    print("ReAct Agent 示例")
    print("=" * 80)

    agent_executor = create_basic_react_agent()

    # 示例1：单工具调用
    print("\n【示例1】单工具调用 - 查询天气")
    print("-" * 80)
    result = agent_executor.invoke({
        "input": "北京今天的天气怎么样？"
    })
    print(f"\n最终答案: {result['output']}\n")

    # 示例2：多工具组合
    print("\n【示例2】多工具组合 - 天气查询 + 数学计算")
    print("-" * 80)
    result = agent_executor.invoke({
        "input": "查询北京的天气，如果温度是25摄氏度，转换成华氏度是多少？"
    })
    print(f"\n最终答案: {result['output']}\n")

    # 示例3：复杂推理
    print("\n【示例3】复杂推理 - 搜索 + 计算")
    print("-" * 80)
    result = agent_executor.invoke({
        "input": "搜索 Python 的信息，然后计算 100 除以 5 的结果"
    })
    print(f"\n最终答案: {result['output']}\n")

    # 示例4：查看中间步骤
    print("\n【示例4】查看执行的中间步骤")
    print("-" * 80)
    result = agent_executor.invoke({
        "input": "上海的天气如何？"
    })

    print("\n中间步骤详情:")
    for i, (action, observation) in enumerate(result['intermediate_steps'], 1):
        print(f"\n步骤 {i}:")
        print(f"  Action: {action.tool}")
        print(f"  Action Input: {action.tool_input}")
        print(f"  Observation: {observation}")


def interactive_mode():
    """交互模式：允许用户输入问题"""

    print("\n" + "=" * 80)
    print("ReAct Agent 交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 80 + "\n")

    agent_executor = create_basic_react_agent()

    while True:
        try:
            user_input = input("\n请输入你的问题: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break

            if not user_input:
                continue

            print("\n处理中...\n")
            result = agent_executor.invoke({"input": user_input})

            print(f"\n{'=' * 80}")
            print(f"答案: {result['output']}")
            print(f"{'=' * 80}\n")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {str(e)}\n")


if __name__ == "__main__":
    # 运行示例
    run_examples()

    # 启动交互模式（可选）
    # interactive_mode()
