"""
Agent 评估系统
全面评估 Agent 的性能、质量和可靠性

评估维度：
1. 任务成功率
2. 执行效率（步数、时间、Token消耗）
3. 工具使用准确性
4. 输出质量
5. 错误处理能力
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback

load_dotenv()


# ============ 测试用例定义 ============

@dataclass
class TestCase:
    """
    测试用例

    属性:
        id: 用例ID
        description: 描述
        input: 输入
        expected_output: 期望输出
        expected_tools: 期望使用的工具
        max_steps: 最大步数
        difficulty: 难度等级 (1-5)
    """
    id: str
    description: str
    input: str
    expected_output: str
    expected_tools: List[str] = field(default_factory=list)
    max_steps: int = 5
    difficulty: int = 1


@dataclass
class TestResult:
    """
    测试结果

    属性:
        test_case: 测试用例
        success: 是否成功
        output: 实际输出
        steps: 实际步数
        duration: 执行时长（秒）
        tokens_used: Token消耗
        tools_called: 调用的工具
        error: 错误信息
    """
    test_case: TestCase
    success: bool
    output: str
    steps: int
    duration: float
    tokens_used: int = 0
    tools_called: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "test_id": self.test_case.id,
            "success": self.success,
            "output": self.output,
            "expected_output": self.test_case.expected_output,
            "steps": self.steps,
            "max_steps": self.test_case.max_steps,
            "duration": self.duration,
            "tokens_used": self.tokens_used,
            "tools_called": self.tools_called,
            "expected_tools": self.test_case.expected_tools,
            "error": self.error
        }


# ============ 评估指标 ============

class EvaluationMetrics:
    """
    评估指标计算器
    """

    @staticmethod
    def calculate_success_rate(results: List[TestResult]) -> float:
        """
        计算成功率

        参数:
            results: 测试结果列表

        返回:
            成功率 (0-1)
        """
        if not results:
            return 0.0

        success_count = sum(1 for r in results if r.success)
        return success_count / len(results)

    @staticmethod
    def calculate_avg_steps(results: List[TestResult]) -> float:
        """
        计算平均步数

        参数:
            results: 测试结果列表

        返回:
            平均步数
        """
        if not results:
            return 0.0

        total_steps = sum(r.steps for r in results if r.success)
        success_count = sum(1 for r in results if r.success)

        return total_steps / success_count if success_count > 0 else 0.0

    @staticmethod
    def calculate_avg_duration(results: List[TestResult]) -> float:
        """
        计算平均执行时长

        参数:
            results: 测试结果列表

        返回:
            平均时长（秒）
        """
        if not results:
            return 0.0

        total_duration = sum(r.duration for r in results if r.success)
        success_count = sum(1 for r in results if r.success)

        return total_duration / success_count if success_count > 0 else 0.0

    @staticmethod
    def calculate_tool_accuracy(results: List[TestResult]) -> float:
        """
        计算工具使用准确率

        参数:
            results: 测试结果列表

        返回:
            工具准确率 (0-1)
        """
        if not results:
            return 0.0

        correct_count = 0
        total_count = 0

        for result in results:
            if result.test_case.expected_tools:
                expected = set(result.test_case.expected_tools)
                actual = set(result.tools_called)

                # 检查是否使用了正确的工具
                if expected == actual:
                    correct_count += 1
                total_count += 1

        return correct_count / total_count if total_count > 0 else 0.0

    @staticmethod
    def calculate_efficiency_score(results: List[TestResult]) -> float:
        """
        计算效率分数

        参数:
            results: 测试结果列表

        返回:
            效率分数 (0-1)
        """
        if not results:
            return 0.0

        efficiency_scores = []

        for result in results:
            if result.success:
                # 效率 = 1 - (实际步数 / 最大步数)
                step_efficiency = 1.0 - (result.steps / result.test_case.max_steps)
                efficiency_scores.append(max(0.0, step_efficiency))

        return sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0.0


# ============ Agent 评估器 ============

class AgentEvaluator:
    """
    Agent 评估器
    运行测试用例并生成评估报告
    """

    def __init__(self, agent_executor: AgentExecutor, test_cases: List[TestCase]):
        """
        初始化评估器

        参数:
            agent_executor: 要评估的 Agent
            test_cases: 测试用例列表
        """
        self.agent_executor = agent_executor
        self.test_cases = test_cases
        self.results: List[TestResult] = []

    def run_evaluation(self, verbose: bool = True) -> List[TestResult]:
        """
        运行评估

        参数:
            verbose: 是否显示详细输出

        返回:
            测试结果列表
        """
        print("="*80)
        print(f"🧪 开始 Agent 评估 (共 {len(self.test_cases)} 个测试用例)")
        print("="*80)

        self.results = []

        for i, test_case in enumerate(self.test_cases, 1):
            if verbose:
                print(f"\n{'─'*80}")
                print(f"测试 {i}/{len(self.test_cases)}: {test_case.description}")
                print(f"输入: {test_case.input}")
                print(f"难度: {'⭐' * test_case.difficulty}")
                print(f"{'─'*80}")

            result = self._run_single_test(test_case, verbose)
            self.results.append(result)

            if verbose:
                status = "✅ 成功" if result.success else "❌ 失败"
                print(f"\n{status}")
                print(f"输出: {result.output[:100]}...")
                print(f"步数: {result.steps}/{test_case.max_steps}")
                print(f"耗时: {result.duration:.2f}秒")
                if result.tokens_used:
                    print(f"Token: {result.tokens_used}")

        if verbose:
            print("\n" + "="*80)
            print("✅ 评估完成")
            print("="*80)

        return self.results

    def _run_single_test(self, test_case: TestCase, verbose: bool) -> TestResult:
        """
        运行单个测试

        参数:
            test_case: 测试用例
            verbose: 是否详细输出

        返回:
            测试结果
        """
        start_time = time.time()
        tokens_used = 0
        tools_called = []

        try:
            # 使用 OpenAI callback 追踪 token 使用
            with get_openai_callback() as cb:
                result = self.agent_executor.invoke(
                    {"input": test_case.input},
                    {"return_intermediate_steps": True}
                )

                tokens_used = cb.total_tokens

                # 提取使用的工具
                if "intermediate_steps" in result:
                    for action, _ in result["intermediate_steps"]:
                        tools_called.append(action.tool)

                output = result.get("output", "")
                steps = len(result.get("intermediate_steps", []))

                # 判断是否成功
                success = self._check_success(output, test_case.expected_output)

                duration = time.time() - start_time

                return TestResult(
                    test_case=test_case,
                    success=success,
                    output=output,
                    steps=steps,
                    duration=duration,
                    tokens_used=tokens_used,
                    tools_called=tools_called
                )

        except Exception as e:
            duration = time.time() - start_time

            return TestResult(
                test_case=test_case,
                success=False,
                output="",
                steps=0,
                duration=duration,
                tokens_used=tokens_used,
                tools_called=tools_called,
                error=str(e)
            )

    def _check_success(self, actual_output: str, expected_output: str) -> bool:
        """
        检查输出是否符合预期

        参数:
            actual_output: 实际输出
            expected_output: 期望输出

        返回:
            是否成功
        """
        # 简单的关键词匹配
        expected_keywords = expected_output.lower().split()
        actual_lower = actual_output.lower()

        # 至少包含一半的关键词
        match_count = sum(1 for kw in expected_keywords if kw in actual_lower)
        return match_count >= len(expected_keywords) * 0.5

    def generate_report(self) -> Dict[str, Any]:
        """
        生成评估报告

        返回:
            报告字典
        """
        if not self.results:
            return {"error": "没有测试结果"}

        metrics = EvaluationMetrics()

        report = {
            "summary": {
                "total_tests": len(self.results),
                "success_count": sum(1 for r in self.results if r.success),
                "failed_count": sum(1 for r in self.results if not r.success),
                "success_rate": metrics.calculate_success_rate(self.results),
            },
            "performance": {
                "avg_steps": metrics.calculate_avg_steps(self.results),
                "avg_duration": metrics.calculate_avg_duration(self.results),
                "total_tokens": sum(r.tokens_used for r in self.results),
                "avg_tokens": sum(r.tokens_used for r in self.results) / len(self.results)
            },
            "quality": {
                "tool_accuracy": metrics.calculate_tool_accuracy(self.results),
                "efficiency_score": metrics.calculate_efficiency_score(self.results)
            },
            "details": [r.to_dict() for r in self.results]
        }

        return report

    def print_report(self):
        """打印评估报告"""
        report = self.generate_report()

        print("\n" + "="*80)
        print("📊 Agent 评估报告")
        print("="*80)

        # 摘要
        summary = report["summary"]
        print(f"\n📋 测试摘要:")
        print(f"  总测试数: {summary['total_tests']}")
        print(f"  成功: {summary['success_count']}")
        print(f"  失败: {summary['failed_count']}")
        print(f"  成功率: {summary['success_rate']:.1%}")

        # 性能
        perf = report["performance"]
        print(f"\n⚡ 性能指标:")
        print(f"  平均步数: {perf['avg_steps']:.1f}")
        print(f"  平均耗时: {perf['avg_duration']:.2f}秒")
        print(f"  平均Token: {perf['avg_tokens']:.0f}")
        print(f"  总Token: {perf['total_tokens']}")

        # 质量
        quality = report["quality"]
        print(f"\n🎯 质量指标:")
        print(f"  工具使用准确率: {quality['tool_accuracy']:.1%}")
        print(f"  效率分数: {quality['efficiency_score']:.1%}")

        # 失败案例
        failed_cases = [r for r in self.results if not r.success]
        if failed_cases:
            print(f"\n❌ 失败案例:")
            for result in failed_cases:
                print(f"  - {result.test_case.description}")
                if result.error:
                    print(f"    错误: {result.error}")

        print("\n" + "="*80)

    def export_report(self, filename: str):
        """
        导出报告到文件

        参数:
            filename: 文件名
        """
        report = self.generate_report()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📁 报告已导出到: {filename}")


# ============ 创建测试用例 ============

def create_test_suite() -> List[TestCase]:
    """
    创建测试套件

    返回:
        测试用例列表
    """
    test_cases = [
        TestCase(
            id="test_001",
            description="简单搜索",
            input="搜索Python的信息",
            expected_output="Python 编程语言",
            expected_tools=["Search"],
            max_steps=2,
            difficulty=1
        ),
        TestCase(
            id="test_002",
            description="简单计算",
            input="计算 15 * 8",
            expected_output="120",
            expected_tools=["Calculator"],
            max_steps=2,
            difficulty=1
        ),
        TestCase(
            id="test_003",
            description="多步骤任务",
            input="搜索人工智能的信息，然后计算 100 + 50",
            expected_output="人工智能 150",
            expected_tools=["Search", "Calculator"],
            max_steps=4,
            difficulty=2
        ),
        TestCase(
            id="test_004",
            description="天气查询",
            input="北京的天气怎么样？",
            expected_output="北京 天气",
            expected_tools=["Weather"],
            max_steps=2,
            difficulty=1
        ),
        TestCase(
            id="test_005",
            description="复杂推理",
            input="如果一个班有40个学生，75%通过了考试，那么有多少学生通过了？",
            expected_output="30",
            expected_tools=["Calculator"],
            max_steps=3,
            difficulty=3
        )
    ]

    return test_cases


# ============ 工具定义 ============

def search_tool(query: str) -> str:
    """搜索工具"""
    knowledge = {
        "Python": "Python是一种高级编程语言，以简洁和可读性著称",
        "人工智能": "人工智能(AI)是计算机科学的一个分支",
        "机器学习": "机器学习是AI的子集"
    }

    for key, value in knowledge.items():
        if key.lower() in query.lower():
            return value

    return f"关于'{query}'的搜索结果"


def calculator_tool(expression: str) -> str:
    """计算器工具"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"


def weather_tool(location: str) -> str:
    """天气工具"""
    weather_db = {
        "北京": "晴天，25°C",
        "上海": "多云，28°C"
    }
    return weather_db.get(location, f"{location}: 晴天，22°C")


# ============ 创建测试 Agent ============

def create_test_agent() -> AgentExecutor:
    """
    创建用于测试的 Agent

    返回:
        Agent 执行器
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    tools = [
        Tool(name="Search", func=search_tool, description="搜索信息"),
        Tool(name="Calculator", func=calculator_tool, description="执行数学计算"),
        Tool(name="Weather", func=weather_tool, description="查询天气")
    ]

    prompt = PromptTemplate(
        template="""Answer the question using tools.

Tools: {tools}
Tool Names: {tool_names}

Format:
Question: the question
Thought: think
Action: tool name
Action Input: input
Observation: result
... (repeat)
Thought: I know the answer
Final Answer: the answer

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
        verbose=False,
        max_iterations=5,
        return_intermediate_steps=True
    )

    return agent_executor


# ============ 运行评估 ============

def run_evaluation_example():
    """运行评估示例"""

    print("="*80)
    print("Agent 评估系统示例")
    print("="*80)

    # 1. 创建测试用例
    test_cases = create_test_suite()
    print(f"\n✅ 已创建 {len(test_cases)} 个测试用例")

    # 2. 创建测试 Agent
    agent = create_test_agent()
    print("✅ 已创建测试 Agent")

    # 3. 创建评估器
    evaluator = AgentEvaluator(agent, test_cases)

    # 4. 运行评估
    results = evaluator.run_evaluation(verbose=True)

    # 5. 生成并打印报告
    evaluator.print_report()

    # 6. 导出报告
    evaluator.export_report("agent_evaluation_report.json")


if __name__ == "__main__":
    run_evaluation_example()
