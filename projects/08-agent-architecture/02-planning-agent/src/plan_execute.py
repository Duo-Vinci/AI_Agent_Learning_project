"""
规划型 Agent 实现
Plan-and-Execute 模式：先制定计划，再逐步执行

核心思想：
1. Planning（规划）：将复杂任务分解为多个子任务
2. Execution（执行）：按顺序执行每个子任务
3. Re-planning（重新规划）：根据执行结果动态调整计划

适用场景：
- 需要多步骤的复杂任务
- 需要明确执行顺序的任务
- 需要中间结果来指导后续步骤的任务
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool

load_dotenv()


# ============ 任务状态定义 ============

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过


@dataclass
class Task:
    """
    任务数据类

    属性:
        id: 任务ID
        description: 任务描述
        dependencies: 依赖的任务ID列表
        status: 任务状态
        result: 执行结果
        error: 错误信息
    """
    id: int
    description: str
    dependencies: List[int]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None

    def __str__(self):
        return f"Task {self.id}: {self.description} [{self.status.value}]"


# ============ 规划器 ============

class TaskPlanner:
    """
    任务规划器
    负责将复杂目标分解为可执行的子任务
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

        # 规划提示模板
        self.planning_prompt = PromptTemplate(
            input_variables=["objective", "context"],
            template="""你是一个任务规划专家。请将以下目标分解为具体的执行步骤。

目标：{objective}

上下文信息：{context}

要求：
1. 每个步骤要具体、可执行
2. 步骤之间要有清晰的逻辑顺序
3. 标注每个步骤的依赖关系
4. 使用JSON格式输出

输出格式：
{{
  "tasks": [
    {{
      "id": 1,
      "description": "步骤描述",
      "dependencies": []
    }},
    {{
      "id": 2,
      "description": "步骤描述",
      "dependencies": [1]
    }}
  ]
}}

任务分解："""
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.planning_prompt)

    def plan(self, objective: str, context: str = "") -> List[Task]:
        """
        制定执行计划

        参数:
            objective: 总体目标
            context: 上下文信息

        返回:
            任务列表
        """
        print(f"📋 [规划阶段] 正在分解任务...")

        try:
            # 调用 LLM 生成计划
            result = self.chain.run(objective=objective, context=context)

            # 解析 JSON 结果
            plan_data = self._parse_plan(result)

            # 创建任务对象
            tasks = []
            for task_data in plan_data["tasks"]:
                task = Task(
                    id=task_data["id"],
                    description=task_data["description"],
                    dependencies=task_data.get("dependencies", [])
                )
                tasks.append(task)

            print(f"✅ 已生成 {len(tasks)} 个子任务\n")
            for task in tasks:
                deps = f" (依赖: {task.dependencies})" if task.dependencies else ""
                print(f"  {task.id}. {task.description}{deps}")

            return tasks

        except Exception as e:
            print(f"❌ 规划失败: {str(e)}")
            # 返回一个简单的备用计划
            return [Task(id=1, description=objective, dependencies=[])]

    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """
        解析 LLM 输出的计划

        参数:
            plan_text: LLM 输出的文本

        返回:
            解析后的计划字典
        """
        try:
            # 尝试提取 JSON 部分
            start_idx = plan_text.find('{')
            end_idx = plan_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = plan_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("未找到有效的 JSON 格式")

        except json.JSONDecodeError:
            # 如果解析失败，尝试简单分割
            lines = [line.strip() for line in plan_text.split('\n') if line.strip()]
            tasks = []
            for i, line in enumerate(lines, 1):
                if line and not line.startswith(('#', '//', '*')):
                    tasks.append({
                        "id": i,
                        "description": line,
                        "dependencies": [i-1] if i > 1 else []
                    })
            return {"tasks": tasks}

    def replan(self, original_tasks: List[Task], failed_task: Task, error: str) -> List[Task]:
        """
        重新规划（当任务失败时）

        参数:
            original_tasks: 原始任务列表
            failed_task: 失败的任务
            error: 错误信息

        返回:
            新的任务列表
        """
        print(f"\n🔄 [重新规划] 任务 {failed_task.id} 失败，调整计划...")

        replan_prompt = f"""原计划的任务 {failed_task.id} 失败了。

失败任务：{failed_task.description}
错误信息：{error}

请提供替代方案或调整后续步骤。输出 JSON 格式的新任务列表。
"""

        try:
            result = self.llm.predict(replan_prompt)
            plan_data = self._parse_plan(result)

            new_tasks = []
            for task_data in plan_data["tasks"]:
                task = Task(
                    id=task_data["id"],
                    description=task_data["description"],
                    dependencies=task_data.get("dependencies", [])
                )
                new_tasks.append(task)

            return new_tasks

        except Exception as e:
            print(f"❌ 重新规划失败: {str(e)}")
            return original_tasks


# ============ 执行器 ============

class TaskExecutor:
    """
    任务执行器
    负责执行具体的任务
    """

    def __init__(self, tools: List[Tool], llm: ChatOpenAI):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm

        # 执行提示模板
        self.execution_prompt = PromptTemplate(
            input_variables=["task", "tools", "previous_results"],
            template="""请执行以下任务：

任务：{task}

可用工具：
{tools}

之前步骤的结果：
{previous_results}

请选择合适的工具并提供输入，格式如下：
Tool: [工具名称]
Input: [工具输入]

如果不需要工具，直接回答。

执行："""
        )

    def execute(self, task: Task, previous_results: Dict[int, str]) -> str:
        """
        执行单个任务

        参数:
            task: 要执行的任务
            previous_results: 之前任务的结果

        返回:
            执行结果
        """
        print(f"\n⚙️  [执行] 任务 {task.id}: {task.description}")
        task.status = TaskStatus.RUNNING

        try:
            # 准备上下文
            tools_desc = "\n".join([f"- {name}: {tool.description}"
                                   for name, tool in self.tools.items()])

            prev_results_text = "\n".join([f"任务{tid}: {result}"
                                          for tid, result in previous_results.items()
                                          if tid in task.dependencies])

            # 生成执行指令
            prompt_text = self.execution_prompt.format(
                task=task.description,
                tools=tools_desc,
                previous_results=prev_results_text or "无"
            )

            response = self.llm.predict(prompt_text)

            # 解析响应并执行工具
            result = self._parse_and_execute(response)

            task.status = TaskStatus.COMPLETED
            task.result = result
            print(f"✅ 完成: {result[:100]}...")

            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            print(f"❌ 失败: {str(e)}")
            raise

    def _parse_and_execute(self, response: str) -> str:
        """
        解析响应并执行工具

        参数:
            response: LLM 的响应

        返回:
            执行结果
        """
        lines = response.strip().split('\n')

        tool_name = None
        tool_input = None

        for line in lines:
            if line.startswith('Tool:'):
                tool_name = line.replace('Tool:', '').strip()
            elif line.startswith('Input:'):
                tool_input = line.replace('Input:', '').strip()

        # 如果找到了工具调用
        if tool_name and tool_name in self.tools:
            tool = self.tools[tool_name]
            result = tool.run(tool_input)
            return result
        else:
            # 没有工具调用，直接返回响应
            return response


# ============ 规划执行 Agent ============

class PlanAndExecuteAgent:
    """
    规划执行 Agent
    整合规划器和执行器
    """

    def __init__(self, tools: List[Tool], llm: ChatOpenAI):
        self.planner = TaskPlanner(llm)
        self.executor = TaskExecutor(tools, llm)
        self.llm = llm

    def run(self, objective: str, context: str = "") -> Dict[str, Any]:
        """
        执行完整的规划和执行流程

        参数:
            objective: 目标
            context: 上下文

        返回:
            执行结果
        """
        print("="*80)
        print(f"🎯 目标: {objective}")
        print("="*80)

        # 1. 规划阶段
        tasks = self.planner.plan(objective, context)

        if not tasks:
            return {"success": False, "error": "规划失败"}

        # 2. 执行阶段
        completed_tasks = {}
        previous_results = {}

        while tasks:
            # 找到可以执行的任务（依赖已满足）
            ready_tasks = [t for t in tasks if t.status == TaskStatus.PENDING
                          and all(dep in completed_tasks for dep in t.dependencies)]

            if not ready_tasks:
                # 没有可执行的任务，检查是否有循环依赖
                pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
                if pending_tasks:
                    print("❌ 检测到循环依赖或无法满足的依赖")
                    break
                else:
                    break

            # 执行就绪的任务
            for task in ready_tasks:
                try:
                    result = self.executor.execute(task, previous_results)
                    completed_tasks[task.id] = task
                    previous_results[task.id] = result

                except Exception as e:
                    # 任务失败，尝试重新规划
                    print(f"\n⚠️  任务 {task.id} 失败，尝试重新规划...")
                    remaining_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]

                    if len(remaining_tasks) > 1:
                        # 重新规划
                        new_tasks = self.planner.replan(tasks, task, str(e))
                        tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED] + new_tasks
                    else:
                        task.status = TaskStatus.FAILED
                        completed_tasks[task.id] = task

        # 3. 总结结果
        print("\n" + "="*80)
        print("📊 执行总结")
        print("="*80)

        success_count = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        failed_count = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

        print(f"总任务数: {len(tasks)}")
        print(f"成功: {success_count}")
        print(f"失败: {failed_count}")

        # 生成最终答案
        final_answer = self._generate_final_answer(objective, tasks, previous_results)

        return {
            "success": failed_count == 0,
            "objective": objective,
            "tasks": tasks,
            "results": previous_results,
            "final_answer": final_answer
        }

    def _generate_final_answer(self, objective: str, tasks: List[Task],
                               results: Dict[int, str]) -> str:
        """
        根据执行结果生成最终答案

        参数:
            objective: 原始目标
            tasks: 任务列表
            results: 执行结果

        返回:
            最终答案
        """
        summary_prompt = f"""基于以下任务执行结果，回答原始问题。

原始问题：{objective}

执行的任务和结果：
"""
        for task in tasks:
            if task.status == TaskStatus.COMPLETED:
                result = results.get(task.id, "无结果")
                summary_prompt += f"\n{task.id}. {task.description}\n   结果: {result}\n"

        summary_prompt += "\n请综合以上结果，给出最终答案："

        final_answer = self.llm.predict(summary_prompt)
        return final_answer


# ============ 工具定义 ============

def search_info(query: str) -> str:
    """搜索信息"""
    info_db = {
        "Python": "Python 是一种高级编程语言，由 Guido van Rossum 于1991年创建",
        "机器学习": "机器学习是人工智能的一个分支，专注于让计算机从数据中学习",
        "数据分析": "数据分析是检查、清理、转换和建模数据的过程"
    }

    for key, value in info_db.items():
        if key in query:
            return value

    return f"关于 '{query}' 的搜索结果"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"


def summarize_text(text: str) -> str:
    """文本摘要"""
    if len(text) > 100:
        return text[:100] + "..."
    return text


tools = [
    Tool(name="Search", func=search_info, description="搜索信息"),
    Tool(name="Calculator", func=calculate, description="执行数学计算"),
    Tool(name="Summarize", func=summarize_text, description="生成文本摘要")
]


# ============ 测试示例 ============

def run_examples():
    """运行示例"""

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    agent = PlanAndExecuteAgent(tools=tools, llm=llm)

    # 示例1：简单任务
    print("\n【示例1】多步骤任务")
    result = agent.run(
        objective="搜索 Python 的信息，然后计算 50 * 20",
        context="需要了解 Python 并进行一些计算"
    )
    print(f"\n最终答案: {result['final_answer']}")

    # 示例2：复杂任务
    print("\n\n【示例2】复杂任务")
    result = agent.run(
        objective="分析机器学习的应用：先搜索机器学习信息，再总结要点，最后计算如果有100个样本，80%训练集是多少个",
        context="需要研究机器学习并进行相关计算"
    )
    print(f"\n最终答案: {result['final_answer']}")


if __name__ == "__main__":
    run_examples()
