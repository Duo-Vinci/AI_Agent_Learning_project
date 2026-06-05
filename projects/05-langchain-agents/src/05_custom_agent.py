"""
LangChain 自定义 Agent 完整示例
演示如何完全自定义 Agent 的各个组件和行为
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple, Union, Sequence
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.schema import AgentAction, AgentFinish
from langchain.prompts import StringPromptTemplate
from langchain.tools import Tool, BaseTool
from langchain_openai import ChatOpenAI
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.schema.language_model import BaseLanguageModel


# ============================================================================
# 第一部分：自定义输出解析器
# ============================================================================

class AgentOutputParser:
    """自定义 Agent 输出解析器 - 解析 LLM 输出为 AgentAction 或 AgentFinish"""

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        """
        解析 LLM 输出

        Args:
            llm_output: LLM 的原始输出文本

        Returns:
            AgentAction 或 AgentFinish 对象
        """
        # 检查是否包含最终答案
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )

        # 解析 Action 和 Action Input
        # 格式: Action: tool_name\nAction Input: input_text
        action_match = re.search(r"Action:\s*(.+?)\s*\n", llm_output)
        action_input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", llm_output, re.DOTALL)

        if not action_match or not action_input_match:
            raise ValueError(f"无法解析输出: {llm_output}")

        action = action_match.group(1).strip()
        action_input = action_input_match.group(1).strip()

        return AgentAction(
            tool=action,
            tool_input=action_input,
            log=llm_output
        )


# ============================================================================
# 第二部分：自定义 Prompt 模板
# ============================================================================

class CustomAgentPromptTemplate(StringPromptTemplate):
    """自定义 Agent Prompt 模板"""

    # 模板字符串
    template: str
    # 可用工具列表
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        """
        格式化 prompt

        Args:
            **kwargs: 包含 intermediate_steps 和 input 等参数

        Returns:
            格式化后的 prompt 字符串
        """
        # 获取中间步骤
        intermediate_steps = kwargs.pop("intermediate_steps", [])

        # 构建思考过程
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += f"\n思考: 我需要使用 {action.tool}\n"
            thoughts += f"Action: {action.tool}\n"
            thoughts += f"Action Input: {action.tool_input}\n"
            thoughts += f"Observation: {observation}\n"

        # 设置 agent_scratchpad
        kwargs["agent_scratchpad"] = thoughts

        # 构建工具描述
        tools_description = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])
        kwargs["tools"] = tools_description

        # 构建工具名称列表
        tool_names = ", ".join([tool.name for tool in self.tools])
        kwargs["tool_names"] = tool_names

        return self.template.format(**kwargs)


# ============================================================================
# 第三部分：自定义工具
# ============================================================================

class SearchTool(BaseTool):
    """自定义搜索工具"""

    name: str = "search"
    description: str = "当需要搜索信息时使用。输入应该是搜索查询。"

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行搜索"""
        # 模拟搜索结果
        results = {
            "python": "Python是一种高级编程语言，由Guido van Rossum创建于1991年。",
            "langchain": "LangChain是一个用于开发由语言模型驱动的应用程序的框架。",
            "agent": "Agent是一个可以使用工具完成任务的自主系统。",
        }

        query_lower = query.lower()
        for key, value in results.items():
            if key in query_lower:
                return f"搜索结果: {value}"

        return f"未找到关于 '{query}' 的相关信息。"

    async def _arun(self, query: str) -> str:
        """异步执行搜索"""
        raise NotImplementedError("该工具不支持异步执行")


class CalculatorTool(BaseTool):
    """自定义计算器工具"""

    name: str = "calculator"
    description: str = "当需要进行数学计算时使用。输入应该是数学表达式。"

    def _run(
        self,
        expression: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """执行计算"""
        try:
            # 安全地评估数学表达式
            result = eval(expression, {"__builtins__": {}}, {})
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"

    async def _arun(self, expression: str) -> str:
        """异步执行计算"""
        raise NotImplementedError("该工具不支持异步执行")


class DateTimeTool(BaseTool):
    """自定义日期时间工具"""

    name: str = "datetime"
    description: str = "获取当前日期和时间。不需要输入参数。"

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """获取当前时间"""
        now = datetime.now()
        return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    async def _arun(self, query: str = "") -> str:
        """异步获取当前时间"""
        raise NotImplementedError("该工具不支持异步执行")


# ============================================================================
# 第四部分：自定义 Agent
# ============================================================================

class CustomAgent(BaseSingleActionAgent):
    """
    完全自定义的 Agent
    实现自定义的工具选择逻辑和决策过程
    """

    llm: BaseLanguageModel
    tools: List[BaseTool]
    prompt: CustomAgentPromptTemplate
    output_parser: AgentOutputParser
    max_iterations: int = 10
    max_execution_time: Optional[float] = None

    @property
    def input_keys(self) -> List[str]:
        """Agent 需要的输入键"""
        return ["input"]

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """
        计划下一步动作

        Args:
            intermediate_steps: 已执行的步骤列表
            **kwargs: 其他参数

        Returns:
            下一步动作或最终结果
        """
        # 检查是否超过最大迭代次数
        if len(intermediate_steps) >= self.max_iterations:
            return AgentFinish(
                return_values={"output": "已达到最大迭代次数，任务可能未完成。"},
                log="超过最大迭代次数"
            )

        # 格式化 prompt
        full_prompt = self.prompt.format(
            intermediate_steps=intermediate_steps,
            **kwargs
        )

        # 调用 LLM
        llm_output = self.llm.predict(full_prompt)

        # 解析输出
        return self.output_parser.parse(llm_output)

    async def aplan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """异步计划下一步动作"""
        raise NotImplementedError("该 Agent 不支持异步执行")


# ============================================================================
# 第五部分：带优先级的自定义 Agent
# ============================================================================

class ToolPriority(Enum):
    """工具优先级枚举"""
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class PrioritizedTool:
    """带优先级的工具"""
    tool: BaseTool
    priority: ToolPriority
    cost: float  # 使用成本


class PriorityBasedAgent(BaseSingleActionAgent):
    """
    基于优先级的自定义 Agent
    根据工具优先级和成本选择工具
    """

    llm: BaseLanguageModel
    prioritized_tools: List[PrioritizedTool]
    prompt: CustomAgentPromptTemplate
    output_parser: AgentOutputParser
    max_iterations: int = 10
    total_cost_limit: float = 100.0

    def __init__(self, **data):
        super().__init__(**data)
        self._total_cost_used = 0.0

    @property
    def input_keys(self) -> List[str]:
        return ["input"]

    def _select_tool_by_priority(self, tool_name: str) -> Optional[PrioritizedTool]:
        """根据优先级选择工具"""
        for pt in self.prioritized_tools:
            if pt.tool.name == tool_name:
                return pt
        return None

    def _check_cost_limit(self, cost: float) -> bool:
        """检查是否超过成本限制"""
        return (self._total_cost_used + cost) <= self.total_cost_limit

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """计划下一步动作，考虑优先级和成本"""

        # 检查迭代次数
        if len(intermediate_steps) >= self.max_iterations:
            return AgentFinish(
                return_values={
                    "output": f"达到最大迭代次数。总成本: {self._total_cost_used}"
                },
                log="超过最大迭代次数"
            )

        # 格式化 prompt
        tools_list = [pt.tool for pt in self.prioritized_tools]
        temp_prompt = CustomAgentPromptTemplate(
            template=self.prompt.template,
            tools=tools_list,
            input_variables=self.prompt.input_variables
        )

        full_prompt = temp_prompt.format(
            intermediate_steps=intermediate_steps,
            **kwargs
        )

        # 调用 LLM
        llm_output = self.llm.predict(full_prompt)

        # 解析输出
        parsed_output = self.output_parser.parse(llm_output)

        # 如果是 AgentFinish，直接返回
        if isinstance(parsed_output, AgentFinish):
            return parsed_output

        # 检查工具优先级和成本
        prioritized_tool = self._select_tool_by_priority(parsed_output.tool)

        if prioritized_tool is None:
            return AgentFinish(
                return_values={"output": f"工具 {parsed_output.tool} 不存在"},
                log="工具不存在"
            )

        # 检查成本限制
        if not self._check_cost_limit(prioritized_tool.cost):
            return AgentFinish(
                return_values={
                    "output": f"超过成本限制。已使用: {self._total_cost_used}, 限制: {self.total_cost_limit}"
                },
                log="超过成本限制"
            )

        # 更新成本
        self._total_cost_used += prioritized_tool.cost

        return parsed_output

    async def aplan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """异步计划"""
        raise NotImplementedError("不支持异步执行")


# ============================================================================
# 第六部分：带记忆的自定义 Agent
# ============================================================================

class MemoryAgent(BaseSingleActionAgent):
    """
    带记忆功能的自定义 Agent
    可以记住之前的交互并影响决策
    """

    llm: BaseLanguageModel
    tools: List[BaseTool]
    prompt: CustomAgentPromptTemplate
    output_parser: AgentOutputParser
    max_iterations: int = 10
    memory_size: int = 5  # 记住最近的 N 次交互

    def __init__(self, **data):
        super().__init__(**data)
        self._memory: List[Dict[str, str]] = []

    @property
    def input_keys(self) -> List[str]:
        return ["input"]

    def _add_to_memory(self, input_text: str, output_text: str):
        """添加到记忆"""
        self._memory.append({
            "input": input_text,
            "output": output_text,
            "timestamp": datetime.now().isoformat()
        })

        # 保持记忆大小限制
        if len(self._memory) > self.memory_size:
            self._memory = self._memory[-self.memory_size:]

    def _format_memory(self) -> str:
        """格式化记忆为字符串"""
        if not self._memory:
            return "无历史记忆"

        memory_str = "历史交互:\n"
        for i, mem in enumerate(self._memory, 1):
            memory_str += f"{i}. 输入: {mem['input'][:50]}...\n"
            memory_str += f"   输出: {mem['output'][:50]}...\n"

        return memory_str

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """计划下一步动作，结合历史记忆"""

        if len(intermediate_steps) >= self.max_iterations:
            return AgentFinish(
                return_values={"output": "达到最大迭代次数"},
                log="超过最大迭代次数"
            )

        # 添加记忆到 prompt
        memory_context = self._format_memory()
        kwargs["memory"] = memory_context

        # 格式化 prompt
        full_prompt = self.prompt.format(
            intermediate_steps=intermediate_steps,
            **kwargs
        )

        # 调用 LLM
        llm_output = self.llm.predict(full_prompt)

        # 解析输出
        parsed_output = self.output_parser.parse(llm_output)

        # 如果是最终结果，保存到记忆
        if isinstance(parsed_output, AgentFinish):
            self._add_to_memory(
                kwargs.get("input", ""),
                parsed_output.return_values.get("output", "")
            )

        return parsed_output

    async def aplan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """异步计划"""
        raise NotImplementedError("不支持异步执行")


# ============================================================================
# 第七部分：示例1 - 基础自定义 Agent
# ============================================================================

def example1_basic_custom_agent():
    """示例1: 基础自定义 Agent"""
    print("\n" + "="*50)
    print("示例1: 基础自定义 Agent")
    print("="*50)

    # 初始化 LLM
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 创建工具
    tools = [
        SearchTool(),
        CalculatorTool(),
        DateTimeTool(),
    ]

    # 创建 prompt 模板
    template = """回答以下问题，尽可能准确。你可以使用以下工具:

{tools}

使用以下格式:

Question: 需要回答的问题
Thought: 思考需要做什么
Action: 要使用的工具，应该是 [{tool_names}] 之一
Action Input: 工具的输入
Observation: 工具的输出
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我现在知道最终答案了
Final Answer: 原始问题的最终答案

开始!

{memory}

Question: {input}
{agent_scratchpad}"""

    prompt = CustomAgentPromptTemplate(
        template=template,
        tools=tools,
        input_variables=["input", "intermediate_steps", "memory"]
    )

    # 创建输出解析器
    output_parser = AgentOutputParser()

    # 创建自定义 Agent
    agent = CustomAgent(
        llm=llm,
        tools=tools,
        prompt=prompt,
        output_parser=output_parser,
        max_iterations=5
    )

    # 创建 AgentExecutor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )

    # 测试
    try:
        result = agent_executor.invoke({"input": "搜索 Python 的信息"})
        print(f"\n结果: {result['output']}")
    except Exception as e:
        print(f"执行出错: {e}")


# ============================================================================
# 第八部分：示例2 - 带优先级的 Agent
# ============================================================================

def example2_priority_based_agent():
    """示例2: 带优先级的自定义 Agent"""
    print("\n" + "="*50)
    print("示例2: 带优先级的自定义 Agent")
    print("="*50)

    # 初始化 LLM
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 创建带优先级的工具
    prioritized_tools = [
        PrioritizedTool(
            tool=SearchTool(),
            priority=ToolPriority.HIGH,
            cost=1.0
        ),
        PrioritizedTool(
            tool=CalculatorTool(),
            priority=ToolPriority.MEDIUM,
            cost=0.5
        ),
        PrioritizedTool(
            tool=DateTimeTool(),
            priority=ToolPriority.LOW,
            cost=0.1
        ),
    ]

    # 创建 prompt 模板
    template = """回答以下问题。你可以使用以下工具:

{tools}

格式:
Question: 问题
Thought: 思考
Action: 工具名 [{tool_names}]
Action Input: 输入
Observation: 观察结果
... (重复)
Thought: 知道答案了
Final Answer: 最终答案

注意: 每个工具都有使用成本，请谨慎选择。

Question: {input}
{agent_scratchpad}"""

    tools_list = [pt.tool for pt in prioritized_tools]
    prompt = CustomAgentPromptTemplate(
        template=template,
        tools=tools_list,
        input_variables=["input", "intermediate_steps"]
    )

    # 创建输出解析器
    output_parser = AgentOutputParser()

    # 创建优先级 Agent
    agent = PriorityBasedAgent(
        llm=llm,
        prioritized_tools=prioritized_tools,
        prompt=prompt,
        output_parser=output_parser,
        max_iterations=5,
        total_cost_limit=5.0
    )

    # 创建 AgentExecutor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools_list,
        verbose=True,
        max_iterations=5
    )

    # 测试
    try:
        result = agent_executor.invoke({"input": "搜索 LangChain 并告诉我当前时间"})
        print(f"\n结果: {result['output']}")
        print(f"总成本: {agent._total_cost_used}")
    except Exception as e:
        print(f"执行出错: {e}")


# ============================================================================
# 第九部分：示例3 - 带记忆的 Agent
# ============================================================================

def example3_memory_agent():
    """示例3: 带记忆的自定义 Agent"""
    print("\n" + "="*50)
    print("示例3: 带记忆的自定义 Agent")
    print("="*50)

    # 初始化 LLM
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 创建工具
    tools = [
        SearchTool(),
        CalculatorTool(),
        DateTimeTool(),
    ]

    # 创建 prompt 模板
    template = """回答以下问题。你可以使用以下工具:

{tools}

{memory}

格式:
Question: 问题
Thought: 思考
Action: 工具名 [{tool_names}]
Action Input: 输入
Observation: 观察
... (重复)
Thought: 知道答案
Final Answer: 答案

Question: {input}
{agent_scratchpad}"""

    prompt = CustomAgentPromptTemplate(
        template=template,
        tools=tools,
        input_variables=["input", "intermediate_steps", "memory"]
    )

    # 创建输出解析器
    output_parser = AgentOutputParser()

    # 创建记忆 Agent
    agent = MemoryAgent(
        llm=llm,
        tools=tools,
        prompt=prompt,
        output_parser=output_parser,
        max_iterations=5,
        memory_size=3
    )

    # 创建 AgentExecutor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )

    # 多轮对话测试
    queries = [
        "搜索 Python 的信息",
        "现在是几点？",
        "计算 10 + 20",
    ]

    for query in queries:
        try:
            print(f"\n>>> 查询: {query}")
            result = agent_executor.invoke({"input": query})
            print(f"结果: {result['output']}")
        except Exception as e:
            print(f"执行出错: {e}")

    # 显示记忆
    print("\n记忆内容:")
    for i, mem in enumerate(agent._memory, 1):
        print(f"{i}. {mem['input']} -> {mem['output'][:50]}...")


# ============================================================================
# 第十部分：主函数
# ============================================================================

def main():
    """主函数"""
    print("LangChain 自定义 Agent 示例")
    print("="*60)

    # 检查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请设置 OPENAI_API_KEY 环境变量")
        return

    # 运行示例
    try:
        example1_basic_custom_agent()
    except Exception as e:
        print(f"示例1 执行失败: {e}")

    try:
        example2_priority_based_agent()
    except Exception as e:
        print(f"示例2 执行失败: {e}")

    try:
        example3_memory_agent()
    except Exception as e:
        print(f"示例3 执行失败: {e}")

    print("\n" + "="*60)
    print("所有示例执行完成")


if __name__ == "__main__":
    main()
