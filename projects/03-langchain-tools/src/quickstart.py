"""
LangChain 工具使用 - 快速入门

本脚本演示如何快速开始使用LangChain工具：
1. 创建简单工具
2. 工具与LLM集成
3. 常用工具示例
4. 工具链组合

运行方式：
    python quickstart.py
"""

import os
from typing import List
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 创建最简单的工具（3行代码） ====================

@tool
def get_word_length(word: str) -> int:
    """计算单词的长度"""
    return len(word)


def example_1_simple_tool():
    """示例1: 最简单的工具"""
    print_section("示例1: 最简单的工具")

    print("工具信息:")
    print(f"  名称: {get_word_length.name}")
    print(f"  描述: {get_word_length.description}")

    # 使用工具
    result = get_word_length.invoke({"word": "LangChain"})
    print(f"\n使用示例:")
    print(f"  get_word_length('LangChain') = {result}")


# ==================== 示例2: 创建实用工具 ====================

@tool
def calculator(expression: str) -> str:
    """
    计算数学表达式。支持 +, -, *, /, **, ()
    示例: "2 + 3 * 4" 或 "(10 + 5) * 2"
    """
    try:
        # 安全求值
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def reverse_string(text: str) -> str:
    """反转字符串"""
    return text[::-1]


@tool
def count_words(text: str) -> int:
    """统计文本中的单词数量"""
    return len(text.split())


def example_2_practical_tools():
    """示例2: 实用工具集合"""
    print_section("示例2: 实用工具集合")

    tools = [calculator, reverse_string, count_words]

    print("可用工具:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")

    print("\n使用示例:")
    print(f"  计算器: calculator('10 + 5 * 2') = {calculator.invoke({'expression': '10 + 5 * 2'})}")
    print(f"  反转: reverse_string('Hello') = {reverse_string.invoke({'text': 'Hello'})}")
    print(f"  计数: count_words('Hello World LangChain') = {count_words.invoke({'text': 'Hello World LangChain'})}")


# ==================== 示例3: 工具与Agent集成 ====================

def example_3_agent_with_tools():
    """示例3: 工具与Agent集成"""
    print_section("示例3: 工具与Agent集成")

    try:
        load_dotenv()

        # 初始化LLM
        llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
            temperature=0
        )

        # 创建工具
        tools = [calculator, reverse_string, count_words]

        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，可以使用工具来回答问题。"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # 创建agent
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # 测试查询
        queries = [
            "计算 15 * 8 + 12",
            "反转字符串 'Python'",
            "统计 'I love LangChain tools' 有多少个单词"
        ]

        print("Agent测试:\n")
        for query in queries:
            print(f"问题: {query}")
            try:
                result = agent_executor.invoke({"input": query})
                print(f"回答: {result['output']}\n")
            except Exception as e:
                print(f"错误: {str(e)}\n")

    except Exception as e:
        print(f"⚠️  Agent示例需要配置API密钥")
        print(f"错误信息: {str(e)}")


# ==================== 示例4: 自定义工具类 ====================

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.callbacks import CallbackManagerForToolRun


class TemperatureInput(BaseModel):
    """温度转换输入"""
    celsius: float = Field(description="摄氏温度")


class TemperatureConverter(BaseTool):
    """温度转换工具"""
    name: str = "temperature_converter"
    description: str = "将摄氏度转换为华氏度"
    args_schema: Type[BaseModel] = TemperatureInput

    def _run(
        self,
        celsius: float,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        fahrenheit = celsius * 9/5 + 32
        return f"{celsius}°C = {fahrenheit}°F"


def example_4_custom_tool_class():
    """示例4: 自定义工具类"""
    print_section("示例4: 自定义工具类")

    tool = TemperatureConverter()

    print("工具信息:")
    print(f"  名称: {tool.name}")
    print(f"  描述: {tool.description}")

    print("\n使用示例:")
    temperatures = [0, 25, 100]
    for temp in temperatures:
        result = tool.invoke({"celsius": temp})
        print(f"  {result}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 快速入门")
    print("="*70)
    print("\n本脚本展示LangChain工具的快速入门示例\n")

    try:
        # 示例1: 简单工具
        example_1_simple_tool()

        # 示例2: 实用工具
        example_2_practical_tools()

        # 示例3: Agent集成
        example_3_agent_with_tools()

        # 示例4: 自定义工具类
        example_4_custom_tool_class()

        print("\n" + "="*70)
        print("  快速入门完成！")
        print("="*70)
        print("\n下一步:")
        print("  - 查看 01_tool_basics.py 学习工具基础")
        print("  - 查看 02_search_tools.py 学习搜索工具")
        print("  - 查看 03_calculator_tools.py 学习计算工具")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
