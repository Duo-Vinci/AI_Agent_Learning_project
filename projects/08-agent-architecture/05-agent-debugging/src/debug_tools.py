"""
Agent 调试工具
提供完整的调试、追踪和可视化功能

功能特性：
1. 详细的执行追踪
2. 中间步骤可视化
3. 性能分析
4. 错误诊断
5. 日志记录
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from colorama import init, Fore, Style

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

# 初始化colorama（用于彩色输出）
init(autoreset=True)
load_dotenv()


# ============ 追踪数据结构 ============

class EventType(Enum):
    """事件类型"""
    LLM_START = "llm_start"
    LLM_END = "llm_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    AGENT_ACTION = "agent_action"
    AGENT_FINISH = "agent_finish"
    ERROR = "error"


@dataclass
class TraceEvent:
    """
    追踪事件

    属性:
        event_type: 事件类型
        timestamp: 时间戳
        data: 事件数据
        duration: 持续时间（秒）
    """
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None

    def __str__(self):
        time_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
        duration_str = f" ({self.duration:.2f}s)" if self.duration else ""
        return f"[{time_str}] {self.event_type.value}{duration_str}: {self.data}"


# ============ 调试回调处理器 ============

class DebugCallbackHandler(BaseCallbackHandler):
    """
    详细的调试回调处理器
    记录所有执行细节用于调试

    特性：
    - 彩色输出
    - 详细的步骤追踪
    - 性能计时
    - 错误捕获
    """

    def __init__(self, verbose: bool = True):
        """
        初始化调试处理器

        参数:
            verbose: 是否显示详细输出
        """
        self.verbose = verbose
        self.traces: List[TraceEvent] = []
        self.start_times: Dict[str, float] = {}
        self.step_count = 0
        self.llm_call_count = 0
        self.tool_call_count = 0

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """LLM开始时调用"""
        self.llm_call_count += 1
        self.start_times['llm'] = time.time()

        event = TraceEvent(
            event_type=EventType.LLM_START,
            data={
                "call_number": self.llm_call_count,
                "prompt_length": len(prompts[0]) if prompts else 0
            }
        )
        self.traces.append(event)

        if self.verbose:
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.CYAN}🤖 LLM 调用 #{self.llm_call_count}")
            print(f"{Fore.CYAN}{'='*80}")
            print(f"{Fore.WHITE}提示词长度: {len(prompts[0])} 字符")

    def on_llm_end(self, response: LLMResult, **kwargs):
        """LLM结束时调用"""
        duration = time.time() - self.start_times.get('llm', time.time())

        event = TraceEvent(
            event_type=EventType.LLM_END,
            data={
                "call_number": self.llm_call_count,
                "response_length": len(str(response.generations[0][0].text))
            },
            duration=duration
        )
        self.traces.append(event)

        if self.verbose:
            print(f"{Fore.GREEN}✅ LLM 响应完成 (耗时: {duration:.2f}秒)")
            print(f"{Fore.WHITE}响应内容:\n{response.generations[0][0].text[:200]}...")

    def on_agent_action(self, action: AgentAction, **kwargs):
        """Agent执行动作时调用"""
        self.step_count += 1

        event = TraceEvent(
            event_type=EventType.AGENT_ACTION,
            data={
                "step": self.step_count,
                "tool": action.tool,
                "tool_input": action.tool_input,
                "log": action.log
            }
        )
        self.traces.append(event)

        if self.verbose:
            print(f"\n{Fore.YELLOW}{'─'*80}")
            print(f"{Fore.YELLOW}📍 步骤 {self.step_count}: Agent 决策")
            print(f"{Fore.YELLOW}{'─'*80}")
            print(f"{Fore.MAGENTA}🛠️  选择工具: {action.tool}")
            print(f"{Fore.WHITE}📝 工具输入: {action.tool_input}")
            if action.log:
                print(f"{Fore.CYAN}💭 思考过程:\n{action.log[:300]}...")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """工具开始执行时调用"""
        self.tool_call_count += 1
        self.start_times['tool'] = time.time()

        event = TraceEvent(
            event_type=EventType.TOOL_START,
            data={
                "tool_name": serialized.get("name", "unknown"),
                "input": input_str
            }
        )
        self.traces.append(event)

        if self.verbose:
            print(f"{Fore.BLUE}⚙️  工具执行中...")

    def on_tool_end(self, output: str, **kwargs):
        """工具执行结束时调用"""
        duration = time.time() - self.start_times.get('tool', time.time())

        event = TraceEvent(
            event_type=EventType.TOOL_END,
            data={"output": output},
            duration=duration
        )
        self.traces.append(event)

        if self.verbose:
            print(f"{Fore.GREEN}✅ 工具执行完成 (耗时: {duration:.2f}秒)")
            print(f"{Fore.WHITE}📤 输出结果:\n{output[:200]}...")

    def on_tool_error(self, error: Exception, **kwargs):
        """工具执行出错时调用"""
        event = TraceEvent(
            event_type=EventType.ERROR,
            data={
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
        self.traces.append(event)

        if self.verbose:
            print(f"{Fore.RED}❌ 工具执行错误: {str(error)}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        """Agent完成时调用"""
        event = TraceEvent(
            event_type=EventType.AGENT_FINISH,
            data={
                "output": finish.return_values.get("output", ""),
                "total_steps": self.step_count
            }
        )
        self.traces.append(event)

        if self.verbose:
            print(f"\n{Fore.GREEN}{'='*80}")
            print(f"{Fore.GREEN}🎉 Agent 执行完成")
            print(f"{Fore.GREEN}{'='*80}")
            print(f"{Fore.WHITE}总步数: {self.step_count}")
            print(f"{Fore.WHITE}LLM调用次数: {self.llm_call_count}")
            print(f"{Fore.WHITE}工具调用次数: {self.tool_call_count}")

    def get_summary(self) -> Dict[str, Any]:
        """
        获取执行摘要

        返回:
            摘要信息字典
        """
        total_duration = sum(e.duration for e in self.traces if e.duration) or 0

        llm_events = [e for e in self.traces if e.event_type == EventType.LLM_END]
        tool_events = [e for e in self.traces if e.event_type == EventType.TOOL_END]

        llm_duration = sum(e.duration for e in llm_events if e.duration) or 0
        tool_duration = sum(e.duration for e in tool_events if e.duration) or 0

        return {
            "total_steps": self.step_count,
            "llm_calls": self.llm_call_count,
            "tool_calls": self.tool_call_count,
            "total_duration": total_duration,
            "llm_duration": llm_duration,
            "tool_duration": tool_duration,
            "llm_percentage": (llm_duration / total_duration * 100) if total_duration > 0 else 0,
            "tool_percentage": (tool_duration / total_duration * 100) if total_duration > 0 else 0
        }

    def print_summary(self):
        """打印执行摘要"""
        summary = self.get_summary()

        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}📊 执行统计")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.WHITE}总步数: {summary['total_steps']}")
        print(f"{Fore.WHITE}LLM 调用: {summary['llm_calls']} 次，耗时 {summary['llm_duration']:.2f}秒 ({summary['llm_percentage']:.1f}%)")
        print(f"{Fore.WHITE}工具调用: {summary['tool_calls']} 次，耗时 {summary['tool_duration']:.2f}秒 ({summary['tool_percentage']:.1f}%)")
        print(f"{Fore.WHITE}总耗时: {summary['total_duration']:.2f}秒")
        print(f"{Fore.CYAN}{'='*80}\n")

    def export_traces(self, filename: str):
        """
        导出追踪数据到文件

        参数:
            filename: 输出文件名
        """
        traces_data = [
            {
                "event_type": t.event_type.value,
                "timestamp": t.timestamp.isoformat(),
                "data": t.data,
                "duration": t.duration
            }
            for t in self.traces
        ]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(traces_data, f, indent=2, ensure_ascii=False)

        print(f"📁 追踪数据已导出到: {filename}")


# ============ 步骤可视化 ============

class StepVisualizer:
    """
    步骤可视化器
    将Agent执行过程可视化展示
    """

    @staticmethod
    def visualize_execution(result: Dict[str, Any]):
        """
        可视化执行过程

        参数:
            result: Agent执行结果（包含intermediate_steps）
        """
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🔍 执行流程可视化")
        print(f"{Fore.CYAN}{'='*80}\n")

        steps = result.get("intermediate_steps", [])

        for i, (action, observation) in enumerate(steps, 1):
            print(f"{Fore.YELLOW}┌─ 步骤 {i}")
            print(f"{Fore.YELLOW}│")
            print(f"{Fore.YELLOW}├─ 💭 思考")
            print(f"{Fore.WHITE}│  决定使用工具: {action.tool}")
            print(f"{Fore.YELLOW}│")
            print(f"{Fore.YELLOW}├─ ⚡ 行动")
            print(f"{Fore.WHITE}│  输入: {action.tool_input}")
            print(f"{Fore.YELLOW}│")
            print(f"{Fore.YELLOW}├─ 👁️  观察")
            obs_short = observation[:100] + "..." if len(observation) > 100 else observation
            print(f"{Fore.WHITE}│  结果: {obs_short}")
            print(f"{Fore.YELLOW}└{'─'*78}\n")

        print(f"{Fore.GREEN}🎯 最终答案:")
        print(f"{Fore.WHITE}{result.get('output', 'N/A')}\n")


# ============ 错误诊断器 ============

class ErrorDiagnostics:
    """
    错误诊断器
    分析和诊断常见的Agent错误
    """

    @staticmethod
    def diagnose(error: Exception, context: Dict[str, Any]) -> str:
        """
        诊断错误

        参数:
            error: 异常对象
            context: 上下文信息

        返回:
            诊断建议
        """
        error_type = type(error).__name__
        error_msg = str(error)

        diagnosis = f"\n{Fore.RED}{'='*80}\n"
        diagnosis += f"{Fore.RED}🔧 错误诊断\n"
        diagnosis += f"{Fore.RED}{'='*80}\n"
        diagnosis += f"{Fore.WHITE}错误类型: {error_type}\n"
        diagnosis += f"{Fore.WHITE}错误信息: {error_msg}\n\n"

        # 常见错误诊断
        if "parsing" in error_msg.lower():
            diagnosis += f"{Fore.YELLOW}💡 诊断: LLM输出格式解析错误\n"
            diagnosis += f"{Fore.WHITE}建议:\n"
            diagnosis += f"{Fore.WHITE}  1. 检查提示词格式是否清晰\n"
            diagnosis += f"{Fore.WHITE}  2. 增加格式示例\n"
            diagnosis += f"{Fore.WHITE}  3. 使用 handle_parsing_errors=True\n"

        elif "timeout" in error_msg.lower():
            diagnosis += f"{Fore.YELLOW}💡 诊断: 执行超时\n"
            diagnosis += f"{Fore.WHITE}建议:\n"
            diagnosis += f"{Fore.WHITE}  1. 增加 max_execution_time\n"
            diagnosis += f"{Fore.WHITE}  2. 优化工具执行效率\n"
            diagnosis += f"{Fore.WHITE}  3. 减少 max_iterations\n"

        elif "max iterations" in error_msg.lower():
            diagnosis += f"{Fore.YELLOW}💡 诊断: 达到最大迭代次数\n"
            diagnosis += f"{Fore.WHITE}建议:\n"
            diagnosis += f"{Fore.WHITE}  1. 检查是否存在循环推理\n"
            diagnosis += f"{Fore.WHITE}  2. 优化提示词，明确停止条件\n"
            diagnosis += f"{Fore.WHITE}  3. 增加 max_iterations 或使用 early_stopping\n"

        elif "tool" in error_msg.lower():
            diagnosis += f"{Fore.YELLOW}💡 诊断: 工具执行错误\n"
            diagnosis += f"{Fore.WHITE}建议:\n"
            diagnosis += f"{Fore.WHITE}  1. 检查工具描述是否准确\n"
            diagnosis += f"{Fore.WHITE}  2. 验证工具参数是否正确\n"
            diagnosis += f"{Fore.WHITE}  3. 添加工具错误处理\n"

        else:
            diagnosis += f"{Fore.YELLOW}💡 诊断: 未知错误\n"
            diagnosis += f"{Fore.WHITE}建议:\n"
            diagnosis += f"{Fore.WHITE}  1. 启用详细日志\n"
            diagnosis += f"{Fore.WHITE}  2. 检查输入数据\n"
            diagnosis += f"{Fore.WHITE}  3. 查看完整堆栈跟踪\n"

        diagnosis += f"{Fore.RED}{'='*80}\n"

        return diagnosis


# ============ 工具定义 ============

def search_tool(query: str) -> str:
    """搜索工具"""
    time.sleep(0.5)  # 模拟网络延迟
    return f"关于'{query}'的搜索结果..."


def calculator_tool(expression: str) -> str:
    """计算器工具"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


tools = [
    Tool(name="Search", func=search_tool, description="搜索信息"),
    Tool(name="Calculator", func=calculator_tool, description="执行数学计算")
]


# ============ 测试示例 ============

def run_debug_examples():
    """运行调试示例"""

    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Agent 调试工具示例")
    print(f"{Fore.CYAN}{'='*80}")

    # 创建调试回调
    debug_handler = DebugCallbackHandler(verbose=True)

    # 创建Agent
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    prompt = PromptTemplate(
        template="""Answer the following question using tools.

Tools: {tools}
Tool Names: {tool_names}

Format:
Question: the input question
Thought: think about what to do
Action: tool name
Action Input: tool input
Observation: tool output
... (repeat)
Thought: I know the answer
Final Answer: the final answer

Question: {input}
{agent_scratchpad}
""",
        input_variables=["input", "agent_scratchpad"],
        partial_variables={
            "tools": "\n".join([f"{t.name}: {t.description}" for t in tools]),
            "tool_names": ", ".join([t.name for t in tools])
        }
    )

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,  # 使用我们的回调处理器
        max_iterations=5,
        callbacks=[debug_handler],
        return_intermediate_steps=True
    )

    # 示例1：正常执行
    print(f"\n{Fore.MAGENTA}【示例1】正常执行并调试")
    try:
        result = agent_executor.invoke({
            "input": "搜索人工智能，然后计算 10 * 5"
        })

        # 可视化执行过程
        StepVisualizer.visualize_execution(result)

        # 打印统计摘要
        debug_handler.print_summary()

        # 导出追踪数据
        debug_handler.export_traces("agent_trace.json")

    except Exception as e:
        diagnosis = ErrorDiagnostics.diagnose(e, {"input": "test"})
        print(diagnosis)


if __name__ == "__main__":
    run_debug_examples()
