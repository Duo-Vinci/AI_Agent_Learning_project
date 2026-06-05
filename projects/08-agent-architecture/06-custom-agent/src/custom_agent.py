"""
自定义 Agent 框架
从零构建自定义的 Agent 架构

核心组件：
1. Agent 基类：定义 Agent 接口
2. 思考引擎：负责推理和决策
3. 动作执行器：执行具体操作
4. 记忆管理：管理上下文和历史
5. 工具系统：工具注册和调用
"""

import os
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()


# ============ Agent 状态和动作 ============

class AgentState(Enum):
    """Agent 状态"""
    IDLE = "idle"           # 空闲
    THINKING = "thinking"   # 思考中
    ACTING = "acting"       # 执行中
    COMPLETED = "completed" # 完成
    FAILED = "failed"       # 失败


@dataclass
class Action:
    """
    动作数据类

    属性:
        name: 动作名称
        params: 动作参数
        result: 执行结果
    """
    name: str
    params: Dict[str, Any]
    result: Optional[Any] = None


@dataclass
class Thought:
    """
    思考数据类

    属性:
        reasoning: 推理过程
        decision: 决策结果
        confidence: 置信度
    """
    reasoning: str
    decision: str
    confidence: float = 0.5


# ============ Agent 基类 ============

class BaseAgent(ABC):
    """
    Agent 基类
    定义所有 Agent 必须实现的接口
    """

    def __init__(self, name: str, description: str):
        """
        初始化 Agent

        参数:
            name: Agent 名称
            description: Agent 描述
        """
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self.history: List[Dict[str, Any]] = []

    @abstractmethod
    def think(self, task: str, context: Dict[str, Any]) -> Thought:
        """
        思考：分析任务，决定下一步行动

        参数:
            task: 任务描述
            context: 上下文信息

        返回:
            思考结果
        """
        pass

    @abstractmethod
    def act(self, action: Action) -> Any:
        """
        行动：执行具体的操作

        参数:
            action: 要执行的动作

        返回:
            执行结果
        """
        pass

    @abstractmethod
    def observe(self, observation: Any) -> Dict[str, Any]:
        """
        观察：处理执行结果

        参数:
            observation: 观察到的结果

        返回:
            处理后的观察结果
        """
        pass

    def run(self, task: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        运行 Agent

        参数:
            task: 任务
            max_iterations: 最大迭代次数

        返回:
            执行结果
        """
        print(f"\n🚀 {self.name} 开始执行任务")
        print(f"📋 任务: {task}\n")

        context = {"task": task, "iterations": 0}
        self.state = AgentState.THINKING

        for i in range(max_iterations):
            context["iterations"] = i + 1

            try:
                # 1. 思考
                self.state = AgentState.THINKING
                thought = self.think(task, context)
                print(f"💭 [第{i+1}步] 思考: {thought.reasoning}")
                print(f"   决策: {thought.decision}")

                # 检查是否完成
                if self._is_complete(thought):
                    self.state = AgentState.COMPLETED
                    print(f"\n✅ 任务完成！")
                    return {
                        "success": True,
                        "result": thought.decision,
                        "iterations": i + 1
                    }

                # 2. 行动
                action = self._parse_action(thought.decision)
                self.state = AgentState.ACTING
                print(f"⚡ [执行] {action.name}({action.params})")

                result = self.act(action)
                action.result = result

                # 3. 观察
                observation = self.observe(result)
                print(f"👁️  [观察] {observation.get('summary', result)}\n")

                # 更新上下文
                context["last_action"] = action
                context["last_observation"] = observation

                # 记录历史
                self.history.append({
                    "step": i + 1,
                    "thought": thought,
                    "action": action,
                    "observation": observation
                })

            except Exception as e:
                self.state = AgentState.FAILED
                print(f"❌ 执行失败: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "iterations": i + 1
                }

        # 达到最大迭代次数
        print(f"⚠️  达到最大迭代次数 ({max_iterations})")
        return {
            "success": False,
            "error": "达到最大迭代次数",
            "iterations": max_iterations
        }

    def _is_complete(self, thought: Thought) -> bool:
        """
        判断任务是否完成

        参数:
            thought: 思考结果

        返回:
            是否完成
        """
        complete_keywords = ["完成", "结束", "答案是", "final answer", "done"]
        return any(kw in thought.decision.lower() for kw in complete_keywords)

    def _parse_action(self, decision: str) -> Action:
        """
        从决策中解析出动作

        参数:
            decision: 决策文本

        返回:
            动作对象
        """
        # 简单的解析逻辑（子类可以重写）
        if "搜索" in decision or "search" in decision.lower():
            return Action(name="search", params={"query": decision})
        elif "计算" in decision or "calculate" in decision.lower():
            return Action(name="calculate", params={"expression": decision})
        else:
            return Action(name="respond", params={"text": decision})


# ============ 工具系统 ============

class ToolRegistry:
    """
    工具注册表
    管理可用的工具
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable, description: str):
        """
        注册工具

        参数:
            name: 工具名称
            func: 工具函数
            description: 工具描述
        """
        self.tools[name] = {
            "func": func,
            "description": description
        }
        print(f"✅ 已注册工具: {name}")

    def call(self, name: str, **kwargs) -> Any:
        """
        调用工具

        参数:
            name: 工具名称
            **kwargs: 工具参数

        返回:
            工具执行结果
        """
        if name not in self.tools:
            raise ValueError(f"工具 '{name}' 不存在")

        tool = self.tools[name]
        return tool["func"](**kwargs)

    def get_tools_description(self) -> str:
        """
        获取所有工具的描述

        返回:
            工具描述文本
        """
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool['description']}")
        return "\n".join(descriptions)


# ============ 自定义 ReAct Agent ============

class CustomReActAgent(BaseAgent):
    """
    自定义的 ReAct Agent
    实现 Reasoning + Acting 循环
    """

    def __init__(self, name: str, llm: ChatOpenAI, tools: ToolRegistry):
        """
        初始化 ReAct Agent

        参数:
            name: Agent 名称
            llm: 语言模型
            tools: 工具注册表
        """
        super().__init__(name, "自定义 ReAct Agent")
        self.llm = llm
        self.tools = tools

        # 思考提示模板
        self.think_prompt = PromptTemplate(
            input_variables=["task", "tools", "history", "last_observation"],
            template="""你是一个智能助手，需要完成用户的任务。

任务: {task}

可用工具:
{tools}

执行历史:
{history}

上次观察: {last_observation}

请思考下一步应该做什么。如果任务已完成，输出"完成：[最终答案]"。
否则，选择一个工具并说明原因。

格式:
推理: [你的推理过程]
决策: [你的决策]

推理:"""
        )

    def think(self, task: str, context: Dict[str, Any]) -> Thought:
        """
        思考：使用 LLM 分析任务

        参数:
            task: 任务
            context: 上下文

        返回:
            思考结果
        """
        # 准备提示
        tools_desc = self.tools.get_tools_description()

        history_text = ""
        if self.history:
            recent_history = self.history[-3:]  # 最近3步
            history_text = "\n".join([
                f"步骤{h['step']}: {h['action'].name} -> {h['observation'].get('summary', 'N/A')}"
                for h in recent_history
            ])

        last_obs = context.get("last_observation", {}).get("summary", "无")

        prompt_text = self.think_prompt.format(
            task=task,
            tools=tools_desc,
            history=history_text or "无",
            last_observation=last_obs
        )

        # 调用 LLM
        response = self.llm.predict(prompt_text)

        # 解析响应
        lines = response.strip().split('\n')
        reasoning = ""
        decision = ""

        for line in lines:
            if line.startswith("推理:") or line.startswith("Reasoning:"):
                reasoning = line.split(":", 1)[1].strip()
            elif line.startswith("决策:") or line.startswith("Decision:"):
                decision = line.split(":", 1)[1].strip()
            elif reasoning and not decision:
                reasoning += " " + line.strip()
            elif decision:
                decision += " " + line.strip()

        if not decision:
            decision = response.strip()

        return Thought(
            reasoning=reasoning or "分析中...",
            decision=decision,
            confidence=0.8
        )

    def act(self, action: Action) -> Any:
        """
        行动：执行工具调用

        参数:
            action: 动作

        返回:
            执行结果
        """
        # 如果是respond动作，直接返回文本
        if action.name == "respond":
            return action.params.get("text", "")

        # 调用工具
        try:
            result = self.tools.call(action.name, **action.params)
            return result
        except Exception as e:
            return f"执行错误: {str(e)}"

    def observe(self, observation: Any) -> Dict[str, Any]:
        """
        观察：处理执行结果

        参数:
            observation: 观察结果

        返回:
            处理后的观察
        """
        # 简单处理：截断过长的输出
        obs_str = str(observation)
        summary = obs_str[:100] + "..." if len(obs_str) > 100 else obs_str

        return {
            "full": observation,
            "summary": summary
        }


# ============ 工具实现 ============

def search_tool(query: str) -> str:
    """搜索工具"""
    # 模拟搜索
    knowledge = {
        "Python": "Python是一种高级编程语言，以简洁和可读性著称",
        "AI": "人工智能(AI)是计算机科学的一个分支，旨在创建智能机器",
        "机器学习": "机器学习是AI的子集，让计算机从数据中学习而无需明确编程"
    }

    for key, value in knowledge.items():
        if key.lower() in query.lower():
            return value

    return f"关于 '{query}' 的搜索结果"


def calculate_tool(expression: str) -> str:
    """计算工具"""
    try:
        # 提取表达式中的数字和运算符
        import re
        match = re.search(r'[\d\+\-\*/\(\)\.\s]+', expression)
        if match:
            expr = match.group()
            result = eval(expr)
            return str(result)
        else:
            return "无法识别的表达式"
    except Exception as e:
        return f"计算错误: {str(e)}"


def get_weather_tool(location: str) -> str:
    """天气查询工具"""
    weather_db = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C",
        "深圳": "小雨，26°C"
    }

    return weather_db.get(location, f"{location}: 晴天，22°C")


# ============ 测试示例 ============

def run_custom_agent_examples():
    """运行自定义 Agent 示例"""

    print("="*80)
    print("自定义 Agent 框架示例")
    print("="*80)

    # 1. 创建工具注册表
    tools = ToolRegistry()
    tools.register("search", search_tool, "搜索信息，输入查询关键词")
    tools.register("calculate", calculate_tool, "执行数学计算，输入数学表达式")
    tools.register("weather", get_weather_tool, "查询天气，输入地点名称")

    # 2. 创建 LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 3. 创建自定义 Agent
    agent = CustomReActAgent(
        name="CustomAgent",
        llm=llm,
        tools=tools
    )

    # 示例1：简单任务
    print("\n【示例1】简单搜索任务")
    print("-"*80)
    result = agent.run("搜索Python的信息", max_iterations=5)
    print(f"\n结果: {result}")

    # 示例2：多步骤任务
    print("\n\n【示例2】多步骤任务")
    print("-"*80)
    agent2 = CustomReActAgent(name="CustomAgent2", llm=llm, tools=tools)
    result = agent2.run("搜索AI的信息，然后计算 50 * 20", max_iterations=10)
    print(f"\n结果: {result}")

    # 示例3：查看执行历史
    print("\n\n【示例3】执行历史")
    print("-"*80)
    print(f"Agent '{agent2.name}' 执行了 {len(agent2.history)} 步:")
    for h in agent2.history:
        print(f"\n步骤 {h['step']}:")
        print(f"  思考: {h['thought'].reasoning}")
        print(f"  决策: {h['thought'].decision}")
        print(f"  动作: {h['action'].name}")
        print(f"  结果: {h['observation']['summary']}")


# ============ 扩展示例：目标导向 Agent ============

class GoalOrientedAgent(BaseAgent):
    """
    目标导向 Agent
    明确跟踪目标的完成进度
    """

    def __init__(self, name: str, goal: str, llm: ChatOpenAI, tools: ToolRegistry):
        """
        初始化目标导向 Agent

        参数:
            name: Agent 名称
            goal: 目标描述
            llm: 语言模型
            tools: 工具注册表
        """
        super().__init__(name, "目标导向 Agent")
        self.goal = goal
        self.llm = llm
        self.tools = tools
        self.progress = 0.0  # 进度 0-1

    def think(self, task: str, context: Dict[str, Any]) -> Thought:
        """思考：评估目标进度并决策"""

        # 评估当前进度
        self._update_progress(context)

        prompt = f"""目标: {self.goal}
当前任务: {task}
进度: {self.progress*100:.0f}%

最近的观察: {context.get('last_observation', {}).get('summary', '无')}

请评估：
1. 距离目标还有多远？
2. 下一步应该做什么？

推理:"""

        response = self.llm.predict(prompt)

        return Thought(
            reasoning=response[:200],
            decision=response,
            confidence=self.progress
        )

    def act(self, action: Action) -> Any:
        """执行动作"""
        if action.name in ["search", "calculate", "weather"]:
            return self.tools.call(action.name, **action.params)
        return action.params.get("text", "")

    def observe(self, observation: Any) -> Dict[str, Any]:
        """观察结果"""
        obs_str = str(observation)
        return {
            "full": observation,
            "summary": obs_str[:100] + "..." if len(obs_str) > 100 else obs_str
        }

    def _update_progress(self, context: Dict[str, Any]):
        """更新进度"""
        # 简单的进度估算
        iterations = context.get("iterations", 0)
        self.progress = min(0.9, iterations * 0.2)


if __name__ == "__main__":
    run_custom_agent_examples()
