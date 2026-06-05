"""
高级 ReAct Agent 实现
包含错误处理、超时控制、重试机制等高级特性

功能特性：
1. 自定义错误处理
2. 超时控制
3. 重试机制
4. 执行追踪和日志
5. 性能监控
"""

import os
import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler

load_dotenv()


# ============ 自定义回调处理器 ============

class DetailedCallbackHandler(BaseCallbackHandler):
    """
    详细的回调处理器，用于追踪 Agent 执行过程

    记录：
    - 每个工具的调用时间
    - 输入输出内容
    - 错误信息
    - 性能指标
    """

    def __init__(self):
        self.start_time = None
        self.steps = []
        self.current_step = {}

    def on_agent_action(self, action, **kwargs):
        """Agent 执行动作时调用"""
        self.current_step = {
            'action': action.tool,
            'input': action.tool_input,
            'start_time': time.time()
        }
        print(f"\n🤔 [思考] 决定使用工具: {action.tool}")
        print(f"📝 [输入] {action.tool_input}")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """工具开始执行时调用"""
        print(f"⚙️  [执行] 工具正在运行...")

    def on_tool_end(self, output: str, **kwargs):
        """工具执行结束时调用"""
        if self.current_step:
            self.current_step['output'] = output
            self.current_step['duration'] = time.time() - self.current_step['start_time']
            self.steps.append(self.current_step.copy())

        print(f"✅ [结果] {output[:200]}..." if len(output) > 200 else f"✅ [结果] {output}")

    def on_tool_error(self, error: Exception, **kwargs):
        """工具执行出错时调用"""
        print(f"❌ [错误] {str(error)}")
        if self.current_step:
            self.current_step['error'] = str(error)
            self.steps.append(self.current_step.copy())

    def on_agent_finish(self, finish, **kwargs):
        """Agent 完成时调用"""
        total_time = sum(step.get('duration', 0) for step in self.steps)
        print(f"\n🎉 [完成] 总耗时: {total_time:.2f}秒，共执行 {len(self.steps)} 步")

    def get_statistics(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        return {
            'total_steps': len(self.steps),
            'total_duration': sum(step.get('duration', 0) for step in self.steps),
            'steps_detail': self.steps
        }


# ============ 工具定义（带错误处理）============

def safe_calculate(expression: str) -> str:
    """
    安全的计算器工具

    特性：
    - 输入验证
    - 错误处理
    - 安全检查
    """
    try:
        # 验证输入
        if not expression or len(expression) > 200:
            return "错误: 表达式为空或过长"

        # 检查危险字符
        dangerous_chars = ['import', 'exec', 'eval', '__', 'open', 'file']
        if any(char in expression.lower() for char in dangerous_chars):
            return "错误: 检测到不安全的表达式"

        # 只允许数字、运算符和括号
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return "错误: 包含不允许的字符"

        # 执行计算
        result = eval(expression)
        return f"计算结果: {result}"

    except ZeroDivisionError:
        return "错误: 除以零"
    except SyntaxError:
        return "错误: 表达式语法错误"
    except Exception as e:
        return f"错误: {str(e)}"


def search_with_retry(query: str, max_retries: int = 3) -> str:
    """
    带重试机制的搜索工具

    参数:
        query: 搜索查询
        max_retries: 最大重试次数
    """
    for attempt in range(max_retries):
        try:
            # 模拟网络请求可能失败
            if attempt < 1:  # 第一次故意模拟失败（演示用）
                # raise Exception("网络连接失败")
                pass

            # 模拟搜索
            results = {
                "机器学习": "机器学习是人工智能的一个分支，专注于让计算机从数据中学习...",
                "深度学习": "深度学习是机器学习的子集，使用多层神经网络...",
                "自然语言处理": "NLP是AI的一个领域，专注于让计算机理解和处理人类语言..."
            }

            for key in results:
                if key in query:
                    return results[key]

            return f"搜索'{query}'：找到相关信息..."

        except Exception as e:
            if attempt == max_retries - 1:
                return f"搜索失败: {str(e)}"
            time.sleep(1)  # 重试前等待
            continue

    return "搜索失败: 达到最大重试次数"


def get_time_info(timezone: str = "UTC") -> str:
    """
    获取时间信息

    参数:
        timezone: 时区
    """
    try:
        now = datetime.now()
        return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')} ({timezone})"
    except Exception as e:
        return f"获取时间失败: {str(e)}"


# 创建工具列表
tools = [
    Tool(
        name="Calculator",
        func=safe_calculate,
        description="安全的计算器工具。输入数学表达式（如 '2+3*4'），返回计算结果。支持 +、-、*、/、括号。"
    ),
    Tool(
        name="Search",
        func=search_with_retry,
        description="网络搜索工具（带重试机制）。输入搜索关键词，返回相关信息。"
    ),
    Tool(
        name="GetTime",
        func=get_time_info,
        description="获取当前时间。输入时区名称（可选），返回当前日期和时间。"
    )
]


# ============ 高级 Agent 配置 ============

react_prompt = """你是一个智能助手，能够使用工具解决问题。

可用工具：
{tools}

工具名称: {tool_names}

使用格式：
Question: 用户的问题
Thought: 分析问题，决定下一步
Action: 选择一个工具
Action Input: 工具的输入
Observation: 工具的输出
... (重复直到得出答案)
Thought: 我知道答案了
Final Answer: 最终答案

重要提示：
- 严格遵循格式
- 每次只调用一个工具
- 基于观察结果做决策
- 如果工具返回错误，尝试其他方法

Question: {input}
Thought: {agent_scratchpad}
"""


def create_advanced_react_agent(
    max_iterations: int = 10,
    max_execution_time: float = 60.0,
    verbose: bool = True
):
    """
    创建高级 ReAct Agent

    参数:
        max_iterations: 最大迭代次数
        max_execution_time: 最大执行时间（秒）
        verbose: 是否显示详细信息

    返回:
        配置好的 AgentExecutor
    """
    # 初始化 LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        request_timeout=30,  # 单次请求超时
    )

    # 创建提示模板
    prompt = PromptTemplate(
        template=react_prompt,
        input_variables=["input", "agent_scratchpad"],
        partial_variables={
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
            "tool_names": ", ".join([tool.name for tool in tools])
        }
    )

    # 创建 Agent
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    # 创建回调处理器
    callback = DetailedCallbackHandler()

    # 创建执行器（高级配置）
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        handle_parsing_errors="检查你的输出格式！必须包含 Action 和 Action Input。",
        return_intermediate_steps=True,
        callbacks=[callback]
    )

    return agent_executor, callback


# ============ 异步执行支持 ============

async def async_execute_agent(agent_executor, input_text: str) -> Dict[str, Any]:
    """
    异步执行 Agent

    参数:
        agent_executor: Agent 执行器
        input_text: 输入问题

    返回:
        执行结果
    """
    try:
        result = await agent_executor.ainvoke({"input": input_text})
        return {
            "success": True,
            "output": result["output"],
            "steps": result.get("intermediate_steps", [])
        }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "执行超时"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============ 批量处理 ============

def batch_execute(agent_executor, questions: List[str]) -> List[Dict[str, Any]]:
    """
    批量执行多个问题

    参数:
        agent_executor: Agent 执行器
        questions: 问题列表

    返回:
        结果列表
    """
    results = []

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"处理问题 {i}/{len(questions)}: {question}")
        print(f"{'='*80}")

        try:
            result = agent_executor.invoke({"input": question})
            results.append({
                "question": question,
                "success": True,
                "answer": result["output"],
                "steps": len(result.get("intermediate_steps", []))
            })
        except Exception as e:
            results.append({
                "question": question,
                "success": False,
                "error": str(e)
            })

    return results


# ============ 测试示例 ============

def run_advanced_examples():
    """运行高级示例"""

    print("="*80)
    print("高级 ReAct Agent 示例")
    print("="*80)

    # 创建 Agent
    agent_executor, callback = create_advanced_react_agent(
        max_iterations=10,
        max_execution_time=60.0,
        verbose=True
    )

    # 示例1：错误处理
    print("\n【示例1】错误处理 - 无效的计算表达式")
    print("-"*80)
    result = agent_executor.invoke({
        "input": "计算 10 除以 0"
    })
    print(f"\n答案: {result['output']}")

    # 示例2：复杂推理
    print("\n【示例2】复杂推理")
    print("-"*80)
    result = agent_executor.invoke({
        "input": "现在几点？然后计算 100 * 8 + 50"
    })
    print(f"\n答案: {result['output']}")

    # 显示统计信息
    stats = callback.get_statistics()
    print(f"\n执行统计:")
    print(f"  总步数: {stats['total_steps']}")
    print(f"  总耗时: {stats['total_duration']:.2f}秒")

    # 示例3：批量处理
    print("\n【示例3】批量处理")
    print("-"*80)
    questions = [
        "搜索机器学习的信息",
        "计算 15 * 8",
        "现在的时间是多少？"
    ]

    # 重新创建agent（重置callback）
    agent_executor, _ = create_advanced_react_agent(verbose=False)
    results = batch_execute(agent_executor, questions)

    print("\n批量处理结果汇总:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"{status} 问题{i}: {result['question']}")
        if result['success']:
            print(f"   答案: {result['answer'][:100]}...")
        else:
            print(f"   错误: {result['error']}")


if __name__ == "__main__":
    run_advanced_examples()
