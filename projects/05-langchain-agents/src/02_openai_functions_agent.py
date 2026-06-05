"""
OpenAI Functions Agent

OpenAI Functions Agent是利用OpenAI的函数调用功能实现的Agent。
与传统的ReAct Agent相比，Functions Agent使用结构化的函数定义，
让模型能够更准确地选择和调用工具。

主要特点：
1. 结构化函数定义
2. 自动参数提取
3. 更准确的工具选择
4. 支持复杂参数类型
5. 原生JSON输出

适用场景：
- 需要精确参数提取的场景
- 复杂的API调用
- 结构化数据处理
- 多步骤工作流
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field


# ============ 工具定义 ============

class WeatherInput(BaseModel):
    """天气查询输入"""
    city: str = Field(description="城市名称，如：北京、上海")
    date: Optional[str] = Field(default=None, description="日期，格式：YYYY-MM-DD")


class SearchInput(BaseModel):
    """搜索输入"""
    query: str = Field(description="搜索关键词")
    max_results: int = Field(default=5, description="最大结果数量")


class CalculatorInput(BaseModel):
    """计算器输入"""
    expression: str = Field(description="数学表达式，如：2+3*4")


@tool(args_schema=WeatherInput)
def get_weather(city: str, date: Optional[str] = None) -> str:
    """
    获取天气信息

    Args:
        city: 城市名称
        date: 日期（可选）

    Returns:
        天气信息
    """
    weather_data = {
        "北京": {"temp": "25°C", "condition": "晴天"},
        "上海": {"temp": "28°C", "condition": "多云"},
        "广州": {"temp": "32°C", "condition": "雨天"},
    }

    if city in weather_data:
        info = weather_data[city]
        date_str = f"{date}的" if date else "今天"
        return f"{city}{date_str}天气：{info['condition']}，温度{info['temp']}"
    else:
        return f"未找到{city}的天气信息"


@tool(args_schema=SearchInput)
def web_search(query: str, max_results: int = 5) -> str:
    """
    网络搜索

    Args:
        query: 搜索关键词
        max_results: 最大结果数量

    Returns:
        搜索结果
    """
    # 模拟搜索结果
    results = [
        f"关于'{query}'的搜索结果 {i+1}" for i in range(max_results)
    ]
    return "\n".join(results)


@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """
    计算器

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
def get_current_time() -> str:
    """
    获取当前时间

    Returns:
        当前时间字符串
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


class ContactInfo(BaseModel):
    """联系人信息"""
    name: str = Field(description="姓名")
    phone: str = Field(description="电话号码")
    email: Optional[str] = Field(default=None, description="邮箱地址")


@tool(args_schema=ContactInfo)
def save_contact(name: str, phone: str, email: Optional[str] = None) -> str:
    """
    保存联系人

    Args:
        name: 姓名
        phone: 电话号码
        email: 邮箱地址（可选）

    Returns:
        保存结果
    """
    contact = {"name": name, "phone": phone}
    if email:
        contact["email"] = email

    return f"✅ 联系人已保存: {json.dumps(contact, ensure_ascii=False)}"


# ============ 示例函数 ============

def example_1_basic_functions_agent():
    """示例1: 基础Functions Agent"""
    print("\n" + "="*60)
    print("示例1: 基础Functions Agent")
    print("="*60)

    print("\n💡 说明:")
    print("Functions Agent使用OpenAI的函数调用功能")
    print("模型会自动选择合适的函数并提取参数\n")

    # 初始化LLM（需要支持函数调用）
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 定义工具
    tools = [get_weather, calculator, get_current_time]

    # 创建Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的AI助手，可以使用工具来回答问题。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建Agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    # 测试查询
    questions = [
        "北京今天天气怎么样？",
        "计算 15 * 23 + 100",
        "现在几点了？"
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": question})
            print(f"回答: {result['output']}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def example_2_multi_step_reasoning():
    """示例2: 多步骤推理"""
    print("\n" + "="*60)
    print("示例2: 多步骤推理")
    print("="*60)

    print("\n💡 说明:")
    print("Functions Agent可以自动进行多步骤推理")
    print("根据需要调用多个函数\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [get_weather, calculator, web_search]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有用的AI助手。先分析问题，然后逐步使用工具解决。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )

    # 需要多步骤的问题
    question = "如果北京今天的温度是25度，上海是28度，它们的平均温度是多少？"

    print(f"问题: {question}")
    print("-" * 40)

    try:
        result = agent_executor.invoke({"input": question})
        print(f"\n最终回答: {result['output']}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def example_3_structured_output():
    """示例3: 结构化输出"""
    print("\n" + "="*60)
    print("示例3: 结构化输出")
    print("="*60)

    print("\n💡 说明:")
    print("Functions Agent特别适合处理结构化数据")
    print("可以精确提取复杂的参数\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [save_contact]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个联系人管理助手，帮助用户保存联系人信息。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 测试不同格式的输入
    inputs = [
        "帮我保存张三的联系方式，电话是13800138000",
        "添加李四，手机13900139000，邮箱lisi@example.com",
        "记录一下：王五 15800158000 wangwu@qq.com"
    ]

    for user_input in inputs:
        print(f"\n用户输入: {user_input}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"结果: {result['output']}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def example_4_function_comparison():
    """示例4: 函数调用 vs 工具调用对比"""
    print("\n" + "="*60)
    print("示例4: 函数调用 vs 工具调用对比")
    print("="*60)

    print("\n💡 OpenAI Functions Agent的优势:")
    print("1. 更准确的参数提取")
    print("   - 使用JSON Schema定义参数")
    print("   - 模型直接返回结构化参数")
    print("   - 减少解析错误")
    print()
    print("2. 更好的类型安全")
    print("   - Pydantic模型验证")
    print("   - 自动类型转换")
    print("   - 清晰的错误提示")
    print()
    print("3. 原生支持")
    print("   - OpenAI API原生功能")
    print("   - 不需要额外解析")
    print("   - 更快的响应速度")
    print()
    print("4. 适用场景")
    print("   - 复杂的API调用")
    print("   - 需要精确参数的场景")
    print("   - 结构化数据处理")


def example_5_error_handling():
    """示例5: 错误处理"""
    print("\n" + "="*60)
    print("示例5: 错误处理")
    print("="*60)

    print("\n💡 说明:")
    print("Functions Agent内置了错误处理机制\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [calculator, get_weather]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个助手，使用工具帮助用户。如果工具返回错误，请告诉用户。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,  # 自动处理解析错误
        max_iterations=3
    )

    # 可能出错的查询
    error_queries = [
        "计算 10 / 0",  # 除零错误
        "查询火星的天气",  # 未知城市
    ]

    for query in error_queries:
        print(f"\n问题: {query}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": query})
            print(f"回答: {result['output']}")
        except Exception as e:
            print(f"❌ 捕获到异常: {e}")


def example_6_custom_function():
    """示例6: 自定义函数"""
    print("\n" + "="*60)
    print("示例6: 创建自定义函数")
    print("="*60)

    print("\n💡 说明:")
    print("可以创建任意复杂的自定义函数\n")

    # 定义一个数据分析函数
    class DataAnalysisInput(BaseModel):
        """数据分析输入"""
        data: List[float] = Field(description="数字列表")
        operation: str = Field(description="操作类型: sum, avg, max, min")

    @tool(args_schema=DataAnalysisInput)
    def analyze_data(data: List[float], operation: str) -> str:
        """
        分析数据

        Args:
            data: 数字列表
            operation: 操作类型（sum/avg/max/min）

        Returns:
            分析结果
        """
        if operation == "sum":
            result = sum(data)
        elif operation == "avg":
            result = sum(data) / len(data)
        elif operation == "max":
            result = max(data)
        elif operation == "min":
            result = min(data)
        else:
            return f"不支持的操作: {operation}"

        return f"{operation}({data}) = {result}"

    # 使用自定义函数
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [analyze_data]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个数据分析助手。"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 测试
    questions = [
        "计算 [1, 2, 3, 4, 5] 的总和",
        "找出 [10, 20, 15, 25, 30] 的最大值",
        "[5, 10, 15, 20] 的平均值是多少？"
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": question})
            print(f"回答: {result['output']}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def example_7_best_practices():
    """示例7: 最佳实践"""
    print("\n" + "="*60)
    print("示例7: Functions Agent最佳实践")
    print("="*60)

    print("\n📌 最佳实践:")
    print()
    print("1. 函数设计")
    print("   - 函数名称要清晰描述功能")
    print("   - 使用详细的docstring")
    print("   - 参数使用Pydantic模型定义")
    print("   - 添加Field描述帮助模型理解")
    print()
    print("2. 错误处理")
    print("   - 设置handle_parsing_errors=True")
    print("   - 在函数内部处理异常")
    print("   - 返回友好的错误消息")
    print()
    print("3. 性能优化")
    print("   - 设置max_iterations限制")
    print("   - 使用temperature=0提高确定性")
    print("   - 缓存常用查询结果")
    print()
    print("4. 提示词优化")
    print("   - 明确告诉模型可用的工具")
    print("   - 指导模型何时使用工具")
    print("   - 提供清晰的系统消息")
    print()
    print("5. 测试和调试")
    print("   - 使用verbose=True查看执行过程")
    print("   - 测试边界情况")
    print("   - 验证参数提取的准确性")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*15 + "OpenAI Functions Agent教程")
    print("="*60)

    # 运行示例
    try:
        example_1_basic_functions_agent()
    except Exception as e:
        print(f"示例1执行出错（可能需要API Key）: {e}")

    try:
        example_2_multi_step_reasoning()
    except Exception as e:
        print(f"示例2执行出错: {e}")

    try:
        example_3_structured_output()
    except Exception as e:
        print(f"示例3执行出错: {e}")

    example_4_function_comparison()

    try:
        example_5_error_handling()
    except Exception as e:
        print(f"示例5执行出错: {e}")

    try:
        example_6_custom_function()
    except Exception as e:
        print(f"示例6执行出错: {e}")

    example_7_best_practices()

    print("\n" + "="*60)
    print("✅ 教程完成")
    print("="*60)
    print("\n💡 提示:")
    print("- Functions Agent需要OpenAI API Key")
    print("- 支持gpt-3.5-turbo和gpt-4模型")
    print("- 适合需要精确参数提取的场景")
