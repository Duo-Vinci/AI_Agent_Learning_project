"""
LangChain 工具使用 - 09: 工具组合与协作

本模块演示：
1. 多工具协作
2. 工具链（Tool Chain）
3. 条件工具选择
4. 工具结果传递
5. 复杂工作流
6. 工具依赖管理
7. Agent使用多工具示例
"""

import os
from typing import Optional, Type, List, Dict, Any
from datetime import datetime

from langchain.tools import BaseTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 工具集合 ====================

# 工具1: 文本处理工具
class TextProcessorInput(BaseModel):
    """文本处理输入"""
    text: str = Field(description="要处理的文本")
    operation: str = Field(description="操作: upper/lower/reverse/word_count")


class TextProcessorTool(BaseTool):
    """文本处理工具"""

    name: str = "text_processor"
    description: str = """
    处理文本内容。

    操作:
    - upper: 转大写
    - lower: 转小写
    - reverse: 反转
    - word_count: 统计字数
    """
    args_schema: Type[BaseModel] = TextProcessorInput

    def _run(
        self,
        text: str,
        operation: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行文本处理"""
        operation = operation.lower()

        if operation == "upper":
            return text.upper()
        elif operation == "lower":
            return text.lower()
        elif operation == "reverse":
            return text[::-1]
        elif operation == "word_count":
            words = len(text.split())
            chars = len(text)
            return f"字数: {words}, 字符数: {chars}"
        else:
            return f"错误: 不支持的操作 '{operation}'"


# 工具2: 数学计算工具
class MathCalculatorInput(BaseModel):
    """数学计算输入"""
    expression: str = Field(description="数学表达式")


class MathCalculatorTool(BaseTool):
    """数学计算工具"""

    name: str = "math_calculator"
    description: str = "计算数学表达式（支持+、-、*、/、**、sqrt等）"
    args_schema: Type[BaseModel] = MathCalculatorInput

    def _run(
        self,
        expression: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行数学计算"""
        try:
            import math

            # 安全的计算环境
            safe_dict = {
                "sqrt": math.sqrt,
                "pow": pow,
                "abs": abs,
                "round": round,
                "pi": math.pi,
                "e": math.e
            }

            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return f"{expression} = {result}"

        except Exception as e:
            return f"计算错误: {str(e)}"


# 工具3: 数据存储工具
class DataStoreInput(BaseModel):
    """数据存储输入"""
    action: str = Field(description="操作: save/get/list/delete")
    key: Optional[str] = Field(default=None, description="数据键")
    value: Optional[str] = Field(default=None, description="数据值")


class DataStoreTool(BaseTool):
    """数据存储工具"""

    name: str = "data_store"
    description: str = """
    存储和检索数据。

    操作:
    - save: 保存数据
    - get: 获取数据
    - list: 列出所有键
    - delete: 删除数据
    """
    args_schema: Type[BaseModel] = DataStoreInput

    # 内存存储
    storage: Dict[str, str] = {}

    def _run(
        self,
        action: str,
        key: Optional[str] = None,
        value: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行数据操作"""
        action = action.lower()

        if action == "save":
            if not key or value is None:
                return "错误: save操作需要key和value"
            self.storage[key] = value
            return f"✓ 已保存: {key} = {value}"

        elif action == "get":
            if not key:
                return "错误: get操作需要key"
            if key in self.storage:
                return f"{key} = {self.storage[key]}"
            else:
                return f"错误: 未找到键 '{key}'"

        elif action == "list":
            if not self.storage:
                return "存储为空"
            items = [f"{k} = {v}" for k, v in self.storage.items()]
            return "存储内容:\n" + "\n".join(f"  {item}" for item in items)

        elif action == "delete":
            if not key:
                return "错误: delete操作需要key"
            if key in self.storage:
                del self.storage[key]
                return f"✓ 已删除: {key}"
            else:
                return f"错误: 未找到键 '{key}'"

        else:
            return f"错误: 不支持的操作 '{action}'"


# 工具4: 条件判断工具
class ConditionCheckerInput(BaseModel):
    """条件检查输入"""
    value: float = Field(description="要检查的值")
    condition: str = Field(description="条件: >0 / <0 / ==0 / >100 / even / odd")


class ConditionCheckerTool(BaseTool):
    """条件判断工具"""

    name: str = "condition_checker"
    description: str = """
    检查数值条件。

    条件:
    - >0: 大于0
    - <0: 小于0
    - ==0: 等于0
    - >100: 大于100
    - even: 偶数
    - odd: 奇数
    """
    args_schema: Type[BaseModel] = ConditionCheckerInput

    def _run(
        self,
        value: float,
        condition: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行条件检查"""
        condition = condition.strip()

        if condition == ">0":
            result = value > 0
        elif condition == "<0":
            result = value < 0
        elif condition == "==0":
            result = value == 0
        elif condition == ">100":
            result = value > 100
        elif condition == "even":
            result = int(value) % 2 == 0
        elif condition == "odd":
            result = int(value) % 2 != 0
        else:
            return f"错误: 不支持的条件 '{condition}'"

        return f"{value} {condition}: {result}"


# ==================== 示例1: 基本工具协作 ====================

def demo_basic_collaboration():
    """示例1: 基本工具协作"""
    print_section("示例1: 基本工具协作")

    # 创建工具实例
    text_tool = TextProcessorTool()
    math_tool = MathCalculatorTool()
    store_tool = DataStoreTool()

    print("场景: 处理文本并存储结果\n")

    # 步骤1: 处理文本
    text = "Hello LangChain Tools"
    print(f"步骤1: 转换文本为大写")
    result1 = text_tool.invoke({"text": text, "operation": "upper"})
    print(f"  结果: {result1}")

    # 步骤2: 统计字数
    print(f"\n步骤2: 统计字数")
    result2 = text_tool.invoke({"text": result1, "operation": "word_count"})
    print(f"  结果: {result2}")

    # 步骤3: 存储结果
    print(f"\n步骤3: 存储结果")
    result3 = store_tool.invoke({
        "action": "save",
        "key": "processed_text",
        "value": result1
    })
    print(f"  {result3}")

    # 步骤4: 查看存储
    print(f"\n步骤4: 查看所有存储")
    result4 = store_tool.invoke({"action": "list"})
    print(f"{result4}")


# ==================== 示例2: 工具链（顺序执行）====================

class ToolChain:
    """工具链管理器"""

    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
        self.results = []

    def execute(self, initial_input: Dict[str, Any]) -> List[str]:
        """执行工具链"""
        self.results = []
        current_input = initial_input

        for i, tool in enumerate(self.tools, 1):
            print(f"步骤{i}: 执行 {tool.name}")

            try:
                result = tool.invoke(current_input)
                self.results.append(result)
                print(f"  结果: {result}\n")

                # 下一个工具可以使用这个结果
                current_input = {"text": result, "operation": "upper"}

            except Exception as e:
                error = f"错误: {str(e)}"
                self.results.append(error)
                print(f"  {error}\n")
                break

        return self.results


def demo_tool_chain():
    """示例2: 工具链"""
    print_section("示例2: 工具链（顺序执行）")

    # 创建工具链
    text_tool = TextProcessorTool()

    chain = ToolChain([
        text_tool,  # 第一步处理
    ])

    print("执行工具链:\n")

    # 执行链
    results = chain.execute({
        "text": "hello world",
        "operation": "upper"
    })

    print(f"工具链完成，共{len(results)}步")


# ==================== 示例3: 条件工具选择 ====================

class ConditionalToolSelector:
    """条件工具选择器"""

    def __init__(self):
        self.text_tool = TextProcessorTool()
        self.math_tool = MathCalculatorTool()
        self.condition_tool = ConditionCheckerTool()

    def process(self, input_data: Any, data_type: str) -> str:
        """根据数据类型选择工具"""
        if data_type == "text":
            print("检测到文本数据，使用文本处理工具")
            return self.text_tool.invoke({
                "text": input_data,
                "operation": "upper"
            })

        elif data_type == "math":
            print("检测到数学表达式，使用计算工具")
            return self.math_tool.invoke({
                "expression": input_data
            })

        elif data_type == "number":
            print("检测到数字，使用条件检查工具")
            return self.condition_tool.invoke({
                "value": float(input_data),
                "condition": ">0"
            })

        else:
            return f"错误: 不支持的数据类型 '{data_type}'"


def demo_conditional_selection():
    """示例3: 条件工具选择"""
    print_section("示例3: 条件工具选择")

    selector = ConditionalToolSelector()

    # 测试不同类型的输入
    test_cases = [
        ("hello world", "text"),
        ("2 + 3 * 4", "math"),
        (42, "number"),
    ]

    for input_data, data_type in test_cases:
        print(f"\n输入: {input_data} (类型: {data_type})")
        result = selector.process(input_data, data_type)
        print(f"输出: {result}\n")


# ==================== 示例4: 工具结果传递 ====================

class DataPipeline:
    """数据处理管道"""

    def __init__(self):
        self.text_tool = TextProcessorTool()
        self.math_tool = MathCalculatorTool()
        self.store_tool = DataStoreTool()

    def process_pipeline(self, text: str) -> Dict[str, Any]:
        """执行完整的数据处理管道"""
        results = {}

        # 阶段1: 文本处理
        print("阶段1: 文本处理")
        upper_text = self.text_tool.invoke({
            "text": text,
            "operation": "upper"
        })
        results["upper"] = upper_text
        print(f"  大写: {upper_text}")

        # 阶段2: 统计信息
        print("\n阶段2: 统计信息")
        stats = self.text_tool.invoke({
            "text": text,
            "operation": "word_count"
        })
        results["stats"] = stats
        print(f"  {stats}")

        # 阶段3: 计算字数的平方
        print("\n阶段3: 数学计算")
        word_count = len(text.split())
        calc_result = self.math_tool.invoke({
            "expression": f"{word_count} ** 2"
        })
        results["calculation"] = calc_result
        print(f"  字数的平方: {calc_result}")

        # 阶段4: 存储所有结果
        print("\n阶段4: 存储结果")
        for key, value in results.items():
            self.store_tool.invoke({
                "action": "save",
                "key": key,
                "value": str(value)
            })
            print(f"  已保存: {key}")

        return results


def demo_result_passing():
    """示例4: 工具结果传递"""
    print_section("示例4: 工具结果传递")

    pipeline = DataPipeline()

    text = "LangChain makes AI applications easy"
    print(f"输入文本: {text}\n")

    results = pipeline.process_pipeline(text)

    print("\n最终结果:")
    for key, value in results.items():
        print(f"  {key}: {value}")


# ==================== 示例5: 复杂工作流 ====================

class WorkflowEngine:
    """工作流引擎"""

    def __init__(self):
        self.text_tool = TextProcessorTool()
        self.math_tool = MathCalculatorTool()
        self.store_tool = DataStoreTool()
        self.condition_tool = ConditionCheckerTool()

    def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[str]:
        """执行工作流"""
        results = []
        context = {}  # 存储中间结果

        for i, step in enumerate(workflow, 1):
            tool_name = step["tool"]
            params = step["params"]

            # 替换参数中的变量引用
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("$"):
                    var_name = value[1:]
                    if var_name in context:
                        params[key] = context[var_name]

            print(f"步骤{i}: {tool_name}")
            print(f"  参数: {params}")

            # 执行工具
            if tool_name == "text_processor":
                result = self.text_tool.invoke(params)
            elif tool_name == "math_calculator":
                result = self.math_tool.invoke(params)
            elif tool_name == "data_store":
                result = self.store_tool.invoke(params)
            elif tool_name == "condition_checker":
                result = self.condition_tool.invoke(params)
            else:
                result = f"错误: 未知工具 '{tool_name}'"

            print(f"  结果: {result}\n")

            # 保存结果到上下文
            if "save_as" in step:
                context[step["save_as"]] = result

            results.append(result)

        return results


def demo_complex_workflow():
    """示例5: 复杂工作流"""
    print_section("示例5: 复杂工作流")

    engine = WorkflowEngine()

    # 定义工作流
    workflow = [
        {
            "tool": "text_processor",
            "params": {"text": "calculate fibonacci", "operation": "upper"},
            "save_as": "processed_text"
        },
        {
            "tool": "math_calculator",
            "params": {"expression": "1 + 1 + 2 + 3 + 5 + 8"},
            "save_as": "fib_sum"
        },
        {
            "tool": "condition_checker",
            "params": {"value": 20, "condition": "even"},
            "save_as": "is_even"
        },
        {
            "tool": "data_store",
            "params": {"action": "list"}
        }
    ]

    print("执行复杂工作流:\n")
    results = engine.execute_workflow(workflow)

    print(f"工作流完成，共执行{len(results)}个步骤")


# ==================== 示例6: 工具依赖管理 ====================

class ToolDependencyManager:
    """工具依赖管理器"""

    def __init__(self):
        self.tools = {
            "text_processor": TextProcessorTool(),
            "math_calculator": MathCalculatorTool(),
            "data_store": DataStoreTool(),
        }
        self.dependencies = {
            "text_processor": [],
            "math_calculator": [],
            "data_store": ["text_processor"],  # 依赖文本处理器
        }

    def check_dependencies(self, tool_name: str) -> bool:
        """检查工具依赖"""
        deps = self.dependencies.get(tool_name, [])

        if not deps:
            return True

        print(f"  检查依赖: {tool_name} 依赖于 {deps}")

        for dep in deps:
            if dep not in self.tools:
                print(f"  ✗ 缺失依赖: {dep}")
                return False

        print(f"  ✓ 依赖满足")
        return True

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """执行工具（检查依赖）"""
        if not self.check_dependencies(tool_name):
            return f"错误: {tool_name} 的依赖不满足"

        tool = self.tools.get(tool_name)
        if not tool:
            return f"错误: 未找到工具 '{tool_name}'"

        return tool.invoke(params)


def demo_dependency_management():
    """示例6: 工具依赖管理"""
    print_section("示例6: 工具依赖管理")

    manager = ToolDependencyManager()

    print("测试1: 执行无依赖的工具")
    result = manager.execute_tool("math_calculator", {"expression": "10 + 20"})
    print(f"结果: {result}\n")

    print("测试2: 执行有依赖的工具")
    result = manager.execute_tool("data_store", {
        "action": "save",
        "key": "test",
        "value": "value"
    })
    print(f"结果: {result}")


# ==================== 示例7: 模拟Agent使用多工具 ====================

class SimpleAgent:
    """简单的Agent（模拟）"""

    def __init__(self):
        self.tools = {
            "text_processor": TextProcessorTool(),
            "math_calculator": MathCalculatorTool(),
            "data_store": DataStoreTool(),
            "condition_checker": ConditionCheckerTool(),
        }

    def select_tool(self, task: str) -> Optional[str]:
        """根据任务选择工具"""
        task_lower = task.lower()

        if any(word in task_lower for word in ["文本", "text", "转换", "统计"]):
            return "text_processor"
        elif any(word in task_lower for word in ["计算", "数学", "math"]):
            return "math_calculator"
        elif any(word in task_lower for word in ["存储", "保存", "store"]):
            return "data_store"
        elif any(word in task_lower for word in ["检查", "判断", "condition"]):
            return "condition_checker"
        else:
            return None

    def execute_task(self, task: str, params: Dict[str, Any]) -> str:
        """执行任务"""
        print(f"任务: {task}")

        # 选择工具
        tool_name = self.select_tool(task)

        if not tool_name:
            return "无法确定使用哪个工具"

        print(f"选择工具: {tool_name}")

        # 执行工具
        tool = self.tools[tool_name]
        result = tool.invoke(params)

        return result


def demo_agent_multi_tool():
    """示例7: Agent使用多工具"""
    print_section("示例7: 模拟Agent使用多工具")

    agent = SimpleAgent()

    # 测试不同任务
    tasks = [
        {
            "task": "将文本转换为大写",
            "params": {"text": "hello world", "operation": "upper"}
        },
        {
            "task": "计算表达式",
            "params": {"expression": "15 * 8 + 7"}
        },
        {
            "task": "存储数据",
            "params": {"action": "save", "key": "result", "value": "success"}
        },
        {
            "task": "检查数字是否为偶数",
            "params": {"value": 42, "condition": "even"}
        }
    ]

    for i, task_info in enumerate(tasks, 1):
        print(f"\n任务{i}:")
        result = agent.execute_task(task_info["task"], task_info["params"])
        print(f"结果: {result}\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 09: 工具组合与协作")
    print("="*70)

    try:
        # 示例1: 基本协作
        demo_basic_collaboration()

        # 示例2: 工具链
        demo_tool_chain()

        # 示例3: 条件选择
        demo_conditional_selection()

        # 示例4: 结果传递
        demo_result_passing()

        # 示例5: 复杂工作流
        demo_complex_workflow()

        # 示例6: 依赖管理
        demo_dependency_management()

        # 示例7: Agent多工具
        demo_agent_multi_tool()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
