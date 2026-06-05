"""
ReAct Agent 详解与实战
===================

ReAct (Reasoning and Acting) 模式是一种将推理和行动结合的 Agent 架构。
核心思想：让 LLM 在执行任务时交替进行"思考"和"行动"，通过观察结果来指导下一步。

核心概念：
---------
1. Thought (思考): Agent 分析当前情况，决定下一步做什么
2. Action (行动): Agent 选择并执行一个工具
3. Observation (观察): 获取工具执行的结果
4. 循环迭代: 基于观察结果继续思考，直到得出最终答案

ReAct 优势：
-----------
- 可解释性强：每步都有明确的推理过程
- 错误可纠正：通过观察可以调整策略
- 灵活性高：可以动态选择工具组合
- 适合复杂任务：多步骤推理和工具调用

作者: AI Agent Learning Project
日期: 2026-06-05
"""

import os
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime
import json

from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction as SchemaAgentAction, AgentFinish as SchemaAgentFinish
from pydantic import BaseModel, Field


# ============================================================================
# 第一部分：自定义工具集
# ============================================================================

def search_tool_func(query: str) -> str:
    """
    模拟搜索工具

    Args:
        query: 搜索查询

    Returns:
        搜索结果
    """
    # 模拟搜索数据库
    search_db = {
        "python": "Python 是一种高级编程语言，创建于 1991 年，由 Guido van Rossum 设计。",
        "langchain": "LangChain 是一个用于开发由语言模型驱动的应用程序的框架，发布于 2022 年。",
        "react": "ReAct 是一种结合推理和行动的 AI Agent 模式，论文发表于 2022 年。",
        "北京": "北京是中国的首都，人口约 2170 万，面积 16410 平方公里。",
        "weather": "今天北京天气晴朗，温度 18-25°C，适合户外活动。",
        "stock": "截至今日收盘，沪深300指数上涨 1.2%，成交额 8500 亿元。",
    }

    # 模糊匹配
    for key, value in search_db.items():
        if key.lower() in query.lower():
            return f"搜索结果: {value}"

    return f"未找到关于 '{query}' 的相关信息。"


def calculator_tool_func(expression: str) -> str:
    """
    计算器工具

    Args:
        expression: 数学表达式

    Returns:
        计算结果
    """
    try:
        # 安全的数学计算
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def get_current_time_func(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前时间工具

    Args:
        format: 时间格式

    Returns:
        当前时间字符串
    """
    return f"当前时间: {datetime.now().strftime(format)}"


def translate_tool_func(text: str) -> str:
    """
    翻译工具（模拟）

    Args:
        text: 要翻译的文本

    Returns:
        翻译结果
    """
    # 简单的中英翻译模拟
    translations = {
        "hello": "你好",
        "world": "世界",
        "agent": "智能体",
        "react": "推理行动模式",
        "你好": "hello",
        "世界": "world",
    }

    for key, value in translations.items():
        if key.lower() in text.lower():
            return f"翻译结果: {value}"

    return f"无法翻译: {text}"


def weather_api_func(city: str) -> str:
    """
    天气查询工具

    Args:
        city: 城市名称

    Returns:
        天气信息
    """
    weather_data = {
        "北京": {"temp": "18-25°C", "condition": "晴朗", "humidity": "45%"},
        "上海": {"temp": "20-28°C", "condition": "多云", "humidity": "60%"},
        "深圳": {"temp": "25-32°C", "condition": "阵雨", "humidity": "75%"},
        "广州": {"temp": "24-31°C", "condition": "雷阵雨", "humidity": "80%"},
    }

    if city in weather_data:
        data = weather_data[city]
        return f"{city}天气: {data['condition']}, 温度 {data['temp']}, 湿度 {data['humidity']}"

    return f"暂无 {city} 的天气数据"


# ============================================================================
# 第二部分：自定义回调处理器 - 追踪 ReAct 循环
# ============================================================================

class ReActCallbackHandler(BaseCallbackHandler):
    """
    自定义回调处理器，用于追踪和显示 ReAct Agent 的思考过程
    """

    def __init__(self):
        self.step_count = 0
        self.thoughts: List[str] = []
        self.actions: List[Dict[str, Any]] = []
        self.observations: List[str] = []

    def on_agent_action(self, action: SchemaAgentAction, **kwargs: Any) -> None:
        """当 Agent 执行动作时调用"""
        self.step_count += 1
        print(f"\n{'='*60}")
        print(f"步骤 {self.step_count}: ACTION")
        print(f"{'='*60}")
        print(f"工具: {action.tool}")
        print(f"输入: {action.tool_input}")
        print(f"推理日志:\n{action.log}")

        self.actions.append({
            "step": self.step_count,
            "tool": action.tool,
            "input": action.tool_input,
            "log": action.log
        })

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """当工具执行完成时调用"""
        print(f"\n{'='*60}")
        print(f"步骤 {self.step_count}: OBSERVATION")
        print(f"{'='*60}")
        print(f"观察结果: {output}")

        self.observations.append(output)

    def on_agent_finish(self, finish: SchemaAgentFinish, **kwargs: Any) -> None:
        """当 Agent 完成任务时调用"""
        print(f"\n{'='*60}")
        print(f"FINAL ANSWER")
        print(f"{'='*60}")
        print(f"最终答案: {finish.return_values.get('output', '')}")
        print(f"\n总共执行了 {self.step_count} 个步骤")

    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "total_steps": self.step_count,
            "actions": self.actions,
            "observations": self.observations
        }


# ============================================================================
# 第三部分：ReAct Prompt 模板
# ============================================================================

# 标准 ReAct Prompt 模板
REACT_PROMPT_TEMPLATE = """你是一个问题解决助手。请使用以下格式回答问题：

Question: 需要回答的问题
Thought: 你应该思考该做什么
Action: 要执行的动作，应该是 [{tool_names}] 中的一个
Action Input: 动作的输入
Observation: 动作执行的结果
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我现在知道最终答案了
Final Answer: 原始问题的最终答案

重要提示：
1. 必须严格按照上述格式输出
2. Action 必须是可用工具列表中的一个
3. 每次只能执行一个 Action
4. 基于 Observation 继续思考下一步

可用工具:
{tools}

开始!

Question: {input}
Thought: {agent_scratchpad}"""


# 中文优化的 ReAct Prompt 模板
REACT_PROMPT_CHINESE = """你是一个智能问题解决助手，请按照以下步骤分析和解决问题：

问题: {input}

请使用以下循环模式来解决问题：

思考: [分析当前情况，决定下一步做什么]
行动: [选择一个工具] 从 [{tool_names}] 中选择
行动输入: [工具的输入参数]
观察: [工具执行的结果]

重复上述过程直到你能给出最终答案。

当你确定答案后，使用以下格式：
思考: 我现在知道最终答案了
最终答案: [你的答案]

可用工具说明:
{tools}

历史记录:
{agent_scratchpad}

现在开始分析问题并逐步解决！"""


# ============================================================================
# 第四部分：创建 ReAct Agent
# ============================================================================

def create_tools() -> List[Tool]:
    """
    创建工具列表

    Returns:
        工具列表
    """
    tools = [
        Tool(
            name="Search",
            func=search_tool_func,
            description="用于搜索信息。输入应该是搜索查询。适合查找事实、定义和一般知识。"
        ),
        Tool(
            name="Calculator",
            func=calculator_tool_func,
            description="用于数学计算。输入应该是数学表达式，例如: '2+2' 或 '10*5+3'。"
        ),
        Tool(
            name="CurrentTime",
            func=get_current_time_func,
            description="获取当前时间。不需要输入参数，直接调用即可。"
        ),
        Tool(
            name="Weather",
            func=weather_api_func,
            description="查询城市天气。输入应该是城市名称，例如: '北京' 或 '上海'。"
        ),
        Tool(
            name="Translate",
            func=translate_tool_func,
            description="翻译文本。输入应该是要翻译的文本。支持中英互译。"
        ),
    ]

    return tools


def create_react_agent_executor(
    verbose: bool = True,
    max_iterations: int = 10,
    handle_parsing_errors: bool = True
) -> Tuple[AgentExecutor, ReActCallbackHandler]:
    """
    创建 ReAct Agent 执行器

    Args:
        verbose: 是否输出详细信息
        max_iterations: 最大迭代次数
        handle_parsing_errors: 是否处理解析错误

    Returns:
        (AgentExecutor, ReActCallbackHandler) 元组
    """
    # 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
        openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )

    # 创建工具
    tools = create_tools()

    # 创建 Prompt
    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

    # 创建 ReAct Agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # 创建回调处理器
    callback_handler = ReActCallbackHandler()

    # 创建 Agent 执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=max_iterations,
        handle_parsing_errors=handle_parsing_errors,
        callbacks=[callback_handler]
    )

    return agent_executor, callback_handler


# ============================================================================
# 第五部分：手动实现 ReAct 循环（教学用）
# ============================================================================

class ManualReActAgent:
    """
    手动实现的 ReAct Agent，用于教学和理解 ReAct 循环原理
    """

    def __init__(self, llm: ChatOpenAI, tools: List[Tool], max_iterations: int = 10):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        self.history: List[Dict[str, str]] = []

    def parse_action(self, text: str) -> Optional[Tuple[str, str]]:
        """
        解析 LLM 输出中的 Action 和 Action Input

        Args:
            text: LLM 输出文本

        Returns:
            (action, action_input) 或 None
        """
        if "Action:" in text and "Action Input:" in text:
            action_start = text.find("Action:") + 7
            action_end = text.find("Action Input:")
            action = text[action_start:action_end].strip()

            input_start = action_end + 13
            # 查找下一行或结束
            input_end = text.find("\n", input_start)
            if input_end == -1:
                input_end = len(text)
            action_input = text[input_start:input_end].strip()

            return action, action_input

        return None

    def is_final_answer(self, text: str) -> bool:
        """判断是否包含最终答案"""
        return "Final Answer:" in text or "最终答案:" in text

    def extract_final_answer(self, text: str) -> str:
        """提取最终答案"""
        if "Final Answer:" in text:
            return text.split("Final Answer:")[1].strip()
        elif "最终答案:" in text:
            return text.split("最终答案:")[1].strip()
        return text

    def run(self, question: str) -> Dict[str, Any]:
        """
        运行 ReAct 循环

        Args:
            question: 问题

        Returns:
            包含答案和历史记录的字典
        """
        print(f"\n{'='*70}")
        print(f"问题: {question}")
        print(f"{'='*70}\n")

        self.history = []
        scratchpad = ""

        for iteration in range(self.max_iterations):
            print(f"\n--- 迭代 {iteration + 1} ---")

            # 构建提示
            prompt = f"""问题: {question}

你需要逐步思考并使用工具来回答问题。

可用工具:
{self._format_tools()}

{scratchpad}

请按以下格式回答:
Thought: [你的思考]
Action: [工具名称]
Action Input: [工具输入]

或者如果你知道答案:
Thought: 我现在知道最终答案了
Final Answer: [答案]"""

            # 调用 LLM
            response = self.llm.predict(prompt)
            print(f"\nLLM 输出:\n{response}")

            # 检查是否是最终答案
            if self.is_final_answer(response):
                final_answer = self.extract_final_answer(response)
                print(f"\n{'='*70}")
                print(f"最终答案: {final_answer}")
                print(f"{'='*70}")

                return {
                    "answer": final_answer,
                    "history": self.history,
                    "iterations": iteration + 1
                }

            # 解析 Action
            action_tuple = self.parse_action(response)
            if not action_tuple:
                print("警告: 无法解析 Action，尝试继续...")
                scratchpad += f"\n{response}\n"
                continue

            action, action_input = action_tuple

            # 执行工具
            if action not in self.tools:
                observation = f"错误: 工具 '{action}' 不存在"
            else:
                try:
                    observation = self.tools[action].func(action_input)
                except Exception as e:
                    observation = f"工具执行错误: {str(e)}"

            print(f"\n观察结果: {observation}")

            # 记录历史
            self.history.append({
                "iteration": iteration + 1,
                "thought": response,
                "action": action,
                "action_input": action_input,
                "observation": observation
            })

            # 更新 scratchpad
            scratchpad += f"\n{response}\nObservation: {observation}\n"

        return {
            "answer": "达到最大迭代次数，未能找到答案",
            "history": self.history,
            "iterations": self.max_iterations
        }

    def _format_tools(self) -> str:
        """格式化工具描述"""
        tool_descriptions = []
        for name, tool in self.tools.items():
            tool_descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(tool_descriptions)


# ============================================================================
# 第六部分：示例演示
# ============================================================================

def example_01_basic_react():
    """示例1: 基础 ReAct Agent 使用"""
    print("\n" + "="*70)
    print("示例1: 基础 ReAct Agent - 简单搜索和计算")
    print("="*70)

    agent_executor, callback = create_react_agent_executor(verbose=True)

    question = "Python 语言是什么时候创建的？创建到现在多少年了？"

    result = agent_executor.invoke({"input": question})

    print(f"\n最终结果: {result['output']}")
    print(f"\n执行摘要: {json.dumps(callback.get_summary(), indent=2, ensure_ascii=False)}")


def example_02_multi_tool():
    """示例2: 多工具组合使用"""
    print("\n" + "="*70)
    print("示例2: 多工具组合 - 天气查询和时间获取")
    print("="*70)

    agent_executor, callback = create_react_agent_executor(verbose=True)

    question = "现在是什么时间？北京的天气怎么样？"

    result = agent_executor.invoke({"input": question})

    print(f"\n最终结果: {result['output']}")


def example_03_complex_reasoning():
    """示例3: 复杂推理任务"""
    print("\n" + "="*70)
    print("示例3: 复杂推理 - 多步骤计算和搜索")
    print("="*70)

    agent_executor, callback = create_react_agent_executor(verbose=True)

    question = "如果一个团队有 5 个人，每人每天工作 8 小时，工作 10 天，总共工作多少小时？"

    result = agent_executor.invoke({"input": question})

    print(f"\n最终结果: {result['output']}")


def example_04_error_recovery():
    """示例4: 错误恢复和调整策略"""
    print("\n" + "="*70)
    print("示例4: 错误恢复 - Agent 如何处理错误并调整策略")
    print("="*70)

    agent_executor, callback = create_react_agent_executor(
        verbose=True,
        handle_parsing_errors=True
    )

    # 这个问题可能需要多次尝试才能正确解答
    question = "搜索 LangChain 的信息，然后计算 2022 到现在的年份差"

    result = agent_executor.invoke({"input": question})

    print(f"\n最终结果: {result['output']}")


def example_05_manual_react():
    """示例5: 手动 ReAct 循环实现"""
    print("\n" + "="*70)
    print("示例5: 手动 ReAct 循环 - 理解内部工作原理")
    print("="*70)

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
        openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )

    tools = create_tools()

    manual_agent = ManualReActAgent(llm=llm, tools=tools, max_iterations=5)

    question = "北京的天气如何？"

    result = manual_agent.run(question)

    print(f"\n执行历史:")
    for step in result['history']:
        print(f"\n步骤 {step['iteration']}:")
        print(f"  思考: {step['thought'][:100]}...")
        print(f"  行动: {step['action']}")
        print(f"  输入: {step['action_input']}")
        print(f"  观察: {step['observation']}")


def example_06_intermediate_steps():
    """示例6: 追踪中间步骤"""
    print("\n" + "="*70)
    print("示例6: 中间步骤追踪 - 详细分析推理过程")
    print("="*70)

    agent_executor, callback = create_react_agent_executor(verbose=False)

    question = "搜索 ReAct 的信息，然后告诉我它是什么时候发表的"

    result = agent_executor.invoke({"input": question})

    # 获取中间步骤
    if "intermediate_steps" in result:
        print("\n中间步骤详情:")
        for i, (action, observation) in enumerate(result["intermediate_steps"], 1):
            print(f"\n步骤 {i}:")
            print(f"  工具: {action.tool}")
            print(f"  输入: {action.tool_input}")
            print(f"  输出: {observation}")

    print(f"\n最终答案: {result['output']}")


def example_07_tool_selection_strategy():
    """示例7: 工具选择策略对比"""
    print("\n" + "="*70)
    print("示例7: 工具选择策略 - 不同问题的工具选择")
    print("="*70)

    agent_executor, _ = create_react_agent_executor(verbose=False)

    questions = [
        "计算 15 * 23 + 47",
        "搜索 Python 的信息",
        "现在几点了？",
        "上海天气怎么样？",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        result = agent_executor.invoke({"input": question})
        print(f"答案: {result['output']}")


def example_08_performance_optimization():
    """示例8: ReAct Agent 性能优化技巧"""
    print("\n" + "="*70)
    print("示例8: 性能优化 - 减少不必要的工具调用")
    print("="*70)

    # 优化的 Agent - 更清晰的工具描述
    optimized_tools = [
        Tool(
            name="MathCalculator",
            func=calculator_tool_func,
            description="仅用于数学计算。输入格式: 纯数学表达式，如 '2+2' 或 '10*5'。不要输入文字描述。"
        ),
        Tool(
            name="InformationSearch",
            func=search_tool_func,
            description="搜索知识和信息。输入应该是具体的搜索关键词，不是完整的句子。"
        ),
    ]

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key")
    )

    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

    agent = create_react_agent(llm=llm, tools=optimized_tools, prompt=prompt)

    callback = ReActCallbackHandler()

    agent_executor = AgentExecutor(
        agent=agent,
        tools=optimized_tools,
        verbose=True,
        max_iterations=5,
        callbacks=[callback]
    )

    question = "计算 100 除以 5 的结果"

    result = agent_executor.invoke({"input": question})

    print(f"\n最终结果: {result['output']}")
    print(f"优化后总步骤数: {callback.step_count}")


# ============================================================================
# 第七部分：对比和分析
# ============================================================================

def compare_react_approaches():
    """对比不同的 ReAct 实现方式"""
    print("\n" + "="*70)
    print("ReAct Agent 实现方式对比")
    print("="*70)

    comparison = """
    1. LangChain 内置 ReAct Agent
       优点:
       - 开箱即用，简单易用
       - 内置错误处理和解析
       - 与 LangChain 生态集成良好
       缺点:
       - 定制化程度有限
       - 黑盒操作，难以调试

    2. 手动实现 ReAct 循环
       优点:
       - 完全控制每个步骤
       - 易于理解和调试
       - 可以自定义任何逻辑
       缺点:
       - 需要处理更多边界情况
       - 代码量较大

    3. 混合方式
       优点:
       - 平衡了灵活性和便利性
       - 可以在关键部分自定义
       - 保留了 LangChain 的优势

    推荐使用场景:
    - 快速原型: 使用 LangChain 内置
    - 生产环境: 混合方式，添加监控和错误处理
    - 研究学习: 手动实现，深入理解原理
    """

    print(comparison)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*70)
    print("ReAct Agent 完整教程")
    print("="*70)

    # 运行示例（注意：实际运行需要有效的 API Key）
    examples = [
        ("基础使用", example_01_basic_react),
        ("多工具组合", example_02_multi_tool),
        ("复杂推理", example_03_complex_reasoning),
        ("错误恢复", example_04_error_recovery),
        ("手动实现", example_05_manual_react),
        ("中间步骤", example_06_intermediate_steps),
        ("工具选择", example_07_tool_selection_strategy),
        ("性能优化", example_08_performance_optimization),
    ]

    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n对比分析:")
    compare_react_approaches()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    # 取消注释以运行特定示例
    # example_01_basic_react()
    # example_05_manual_react()


if __name__ == "__main__":
    main()
