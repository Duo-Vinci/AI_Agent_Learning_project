"""
LangChain 工具使用 - 08: 自定义工具

本模块演示：
1. 使用StructuredTool创建工具
2. 继承BaseTool创建自定义类
3. 异步工具（async tools）
4. 带状态的工具
5. 工具回调函数
6. 工具错误处理和日志
7. 完整的自定义工具示例
"""

import os
import asyncio
import time
from typing import Optional, Type, List, Dict, Any, Callable
from datetime import datetime
from functools import wraps

from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 使用StructuredTool创建工具 ====================

def calculate_area(shape: str, length: float, width: Optional[float] = None) -> str:
    """
    计算图形面积

    Args:
        shape: 图形类型（square/rectangle/circle）
        length: 长度或半径
        width: 宽度（矩形时需要）

    Returns:
        面积计算结果
    """
    import math

    shape = shape.lower()

    if shape == "square":
        area = length * length
        return f"正方形面积 = {length} × {length} = {area:.2f}"

    elif shape == "rectangle":
        if width is None:
            return "错误: 矩形需要提供宽度"
        area = length * width
        return f"矩形面积 = {length} × {width} = {area:.2f}"

    elif shape == "circle":
        area = math.pi * length * length
        return f"圆形面积 = π × {length}² = {area:.2f}"

    else:
        return f"错误: 不支持的图形类型 '{shape}'"


def demo_structured_tool():
    """示例1: 使用StructuredTool创建工具"""
    print_section("示例1: 使用StructuredTool创建工具")

    # 方式1: 从函数创建
    area_tool = StructuredTool.from_function(
        func=calculate_area,
        name="calculate_area",
        description="计算图形面积（支持正方形、矩形、圆形）"
    )

    print("工具信息:")
    print(f"名称: {area_tool.name}")
    print(f"描述: {area_tool.description}\n")

    # 测试不同图形
    test_cases = [
        {"shape": "square", "length": 5.0},
        {"shape": "rectangle", "length": 6.0, "width": 4.0},
        {"shape": "circle", "length": 3.0},
    ]

    for case in test_cases:
        result = area_tool.invoke(case)
        print(f"  {result}")


# ==================== 示例2: 继承BaseTool创建工具类 ====================

class CalculatorInput(BaseModel):
    """计算器输入模式"""
    operation: str = Field(description="操作类型: add/subtract/multiply/divide/power")
    a: float = Field(description="第一个数字")
    b: float = Field(description="第二个数字")


class CalculatorTool(BaseTool):
    """计算器工具（继承BaseTool）"""

    name: str = "calculator"
    description: str = """
    执行基本数学运算。

    支持的操作:
    - add: 加法
    - subtract: 减法
    - multiply: 乘法
    - divide: 除法
    - power: 幂运算
    """
    args_schema: Type[BaseModel] = CalculatorInput

    # 工具可以有状态
    calculation_count: int = 0

    def _run(
        self,
        operation: str,
        a: float,
        b: float,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行计算（同步版本）"""
        self.calculation_count += 1

        operation = operation.lower()

        if operation == "add":
            result = a + b
            symbol = "+"
        elif operation == "subtract":
            result = a - b
            symbol = "-"
        elif operation == "multiply":
            result = a * b
            symbol = "×"
        elif operation == "divide":
            if b == 0:
                return "错误: 除数不能为0"
            result = a / b
            symbol = "÷"
        elif operation == "power":
            result = a ** b
            symbol = "^"
        else:
            return f"错误: 不支持的操作 '{operation}'"

        return f"{a} {symbol} {b} = {result:.4f} [计算次数: {self.calculation_count}]"

    async def _arun(
        self,
        operation: str,
        a: float,
        b: float,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """执行计算（异步版本）"""
        # 模拟异步操作
        await asyncio.sleep(0.1)
        return self._run(operation, a, b)


def demo_custom_tool_class():
    """示例2: 继承BaseTool创建工具类"""
    print_section("示例2: 继承BaseTool创建工具类")

    calc_tool = CalculatorTool()

    print("工具信息:")
    print(f"名称: {calc_tool.name}")
    print(f"描述: {calc_tool.description.strip()}\n")

    # 测试各种操作
    test_cases = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "subtract", "a": 10, "b": 5},
        {"operation": "multiply", "a": 10, "b": 5},
        {"operation": "divide", "a": 10, "b": 5},
        {"operation": "power", "a": 2, "b": 8},
    ]

    print("计算测试:")
    for case in test_cases:
        result = calc_tool.invoke(case)
        print(f"  {result}")


# ==================== 示例3: 异步工具 ====================

class AsyncWebFetchInput(BaseModel):
    """异步网络请求输入"""
    url: str = Field(description="要请求的URL")
    timeout: int = Field(default=5, description="超时时间（秒）")


class AsyncWebFetchTool(BaseTool):
    """异步网络请求工具"""

    name: str = "async_web_fetch"
    description: str = "异步获取网页内容"
    args_schema: Type[BaseModel] = AsyncWebFetchInput

    def _run(
        self,
        url: str,
        timeout: int = 5,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """同步版本（不推荐用于网络请求）"""
        return "请使用异步版本（_arun）"

    async def _arun(
        self,
        url: str,
        timeout: int = 5,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """异步版本"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    status = response.status
                    text = await response.text()
                    length = len(text)

                    return f"✓ URL: {url}\n" \
                           f"状态码: {status}\n" \
                           f"内容长度: {length} 字符"

        except asyncio.TimeoutError:
            return f"✗ 请求超时: {url}"
        except Exception as e:
            return f"✗ 错误: {str(e)}"


async def demo_async_tool():
    """示例3: 异步工具"""
    print_section("示例3: 异步工具")

    tool = AsyncWebFetchTool()

    print("异步获取网页测试:")

    # 注意：实际运行可能需要安装aiohttp
    # pip install aiohttp

    urls = [
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/posts/1",
    ]

    # 并发获取多个URL
    tasks = []
    for url in urls:
        tasks.append(tool.ainvoke({"url": url, "timeout": 5}))

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"\n请求{i} 失败: {str(result)}")
            else:
                print(f"\n请求{i} 结果:")
                print(result)
    except Exception as e:
        print(f"注意: 需要安装aiohttp库（pip install aiohttp）")
        print(f"错误: {str(e)}")


# ==================== 示例4: 带状态的工具 ====================

class CounterInput(BaseModel):
    """计数器输入"""
    operation: str = Field(description="操作: increment/decrement/reset/get")
    value: int = Field(default=1, description="增减数值")


class CounterTool(BaseTool):
    """带状态的计数器工具"""

    name: str = "counter"
    description: str = """
    带状态的计数器工具。

    操作:
    - increment: 增加
    - decrement: 减少
    - reset: 重置
    - get: 获取当前值
    """
    args_schema: Type[BaseModel] = CounterInput

    # 工具状态
    counter: int = 0
    history: List[str] = []

    def _run(
        self,
        operation: str,
        value: int = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行计数器操作"""
        operation = operation.lower()
        timestamp = datetime.now().strftime("%H:%M:%S")

        if operation == "increment":
            self.counter += value
            action = f"增加 {value}"
        elif operation == "decrement":
            self.counter -= value
            action = f"减少 {value}"
        elif operation == "reset":
            self.counter = 0
            action = "重置"
        elif operation == "get":
            action = "查询"
        else:
            return f"错误: 不支持的操作 '{operation}'"

        # 记录历史
        self.history.append(f"[{timestamp}] {action} -> {self.counter}")

        return f"计数器值: {self.counter}"

    def get_history(self) -> str:
        """获取操作历史"""
        if not self.history:
            return "无操作历史"

        return "操作历史:\n" + "\n".join(f"  {h}" for h in self.history[-10:])


def demo_stateful_tool():
    """示例4: 带状态的工具"""
    print_section("示例4: 带状态的工具")

    counter = CounterTool()

    print("计数器操作测试:\n")

    # 执行一系列操作
    operations = [
        ("increment", 5),
        ("increment", 3),
        ("decrement", 2),
        ("increment", 10),
        ("get", 1),
        ("reset", 1),
        ("increment", 1),
    ]

    for op, val in operations:
        result = counter.invoke({"operation": op, "value": val})
        print(f"  {op}({val}): {result}")

    # 查看历史
    print(f"\n{counter.get_history()}")


# ==================== 示例5: 带回调的工具 ====================

def timing_decorator(func: Callable) -> Callable:
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"    [耗时: {elapsed*1000:.2f}ms]")
        return result
    return wrapper


class CallbackToolInput(BaseModel):
    """回调工具输入"""
    task_name: str = Field(description="任务名称")
    duration: float = Field(default=1.0, description="任务持续时间（秒）")


class CallbackTool(BaseTool):
    """带回调的工具"""

    name: str = "callback_tool"
    description: str = "演示工具回调机制"
    args_schema: Type[BaseModel] = CallbackToolInput

    # 回调函数
    on_start: Optional[Callable] = None
    on_success: Optional[Callable] = None
    on_error: Optional[Callable] = None

    def _run(
        self,
        task_name: str,
        duration: float = 1.0,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行任务"""
        try:
            # 开始回调
            if self.on_start:
                self.on_start(task_name)

            # 模拟任务执行
            time.sleep(duration)
            result = f"任务 '{task_name}' 完成"

            # 成功回调
            if self.on_success:
                self.on_success(task_name, result)

            return result

        except Exception as e:
            # 错误回调
            if self.on_error:
                self.on_error(task_name, str(e))
            raise


def demo_callback_tool():
    """示例5: 带回调的工具"""
    print_section("示例5: 带回调的工具")

    # 定义回调函数
    def on_start(task_name):
        print(f"  ⏳ 开始执行: {task_name}")

    def on_success(task_name, result):
        print(f"  ✓ 执行成功: {result}")

    def on_error(task_name, error):
        print(f"  ✗ 执行失败: {task_name} - {error}")

    # 创建工具并设置回调
    tool = CallbackTool()
    tool.on_start = on_start
    tool.on_success = on_success
    tool.on_error = on_error

    print("执行任务:\n")

    # 测试任务
    tasks = [
        {"task_name": "数据处理", "duration": 0.5},
        {"task_name": "报告生成", "duration": 0.3},
        {"task_name": "邮件发送", "duration": 0.2},
    ]

    for task in tasks:
        tool.invoke(task)
        print()


# ==================== 示例6: 工具日志和调试 ====================

class LoggingToolInput(BaseModel):
    """日志工具输入"""
    message: str = Field(description="消息内容")
    level: str = Field(default="info", description="日志级别")


class LoggingTool(BaseTool):
    """带日志的工具"""

    name: str = "logging_tool"
    description: str = "演示工具日志和调试"
    args_schema: Type[BaseModel] = LoggingToolInput

    # 日志存储
    logs: List[Dict[str, Any]] = []
    verbose: bool = True

    def _log(self, level: str, message: str, **kwargs):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)

        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"    [{timestamp}] [{level.upper()}] {message}")

    def _run(
        self,
        message: str,
        level: str = "info",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行操作"""
        self._log("start", f"开始处理消息")
        self._log(level, message)
        self._log("end", f"处理完成")

        return f"已记录 {level.upper()} 级别消息"

    def get_logs(self, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取日志"""
        if level:
            return [log for log in self.logs if log["level"] == level]
        return self.logs

    def clear_logs(self):
        """清除日志"""
        self.logs.clear()


def demo_logging_tool():
    """示例6: 工具日志和调试"""
    print_section("示例6: 工具日志和调试")

    tool = LoggingTool()

    print("执行日志测试:\n")

    # 记录不同级别的日志
    messages = [
        {"message": "系统启动成功", "level": "info"},
        {"message": "配置文件已加载", "level": "debug"},
        {"message": "检测到潜在问题", "level": "warning"},
    ]

    for msg in messages:
        result = tool.invoke(msg)
        print(f"  返回: {result}\n")

    # 查看日志统计
    print(f"总日志数: {len(tool.get_logs())}")
    print(f"INFO日志: {len(tool.get_logs('info'))}")
    print(f"WARNING日志: {len(tool.get_logs('warning'))}")


# ==================== 示例7: 完整的自定义工具示例 ====================

class DataProcessorInput(BaseModel):
    """数据处理器输入"""
    data: List[float] = Field(description="数据列表")
    operation: str = Field(description="操作: sum/avg/max/min/stats")


class DataProcessorTool(BaseTool):
    """完整的数据处理工具"""

    name: str = "data_processor"
    description: str = """
    数据处理工具，支持多种统计操作。

    操作:
    - sum: 求和
    - avg: 平均值
    - max: 最大值
    - min: 最小值
    - stats: 完整统计信息
    """
    args_schema: Type[BaseModel] = DataProcessorInput

    # 工具配置
    max_data_points: int = 1000
    precision: int = 4

    # 统计信息
    processed_count: int = 0
    last_operation: Optional[str] = None

    def _validate_data(self, data: List[float]) -> None:
        """验证数据"""
        if not data:
            raise ValueError("数据列表不能为空")

        if len(data) > self.max_data_points:
            raise ValueError(f"数据点数量超过限制({self.max_data_points})")

    def _calculate_stats(self, data: List[float]) -> Dict[str, float]:
        """计算统计信息"""
        n = len(data)
        total = sum(data)
        avg = total / n

        # 方差和标准差
        variance = sum((x - avg) ** 2 for x in data) / n
        std_dev = variance ** 0.5

        return {
            "count": n,
            "sum": total,
            "mean": avg,
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data),
            "variance": variance,
            "std_dev": std_dev
        }

    def _run(
        self,
        data: List[float],
        operation: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行数据处理"""
        try:
            # 验证数据
            self._validate_data(data)

            # 更新统计
            self.processed_count += 1
            self.last_operation = operation

            operation = operation.lower()

            if operation == "sum":
                result = sum(data)
                return f"总和: {result:.{self.precision}f}"

            elif operation == "avg":
                result = sum(data) / len(data)
                return f"平均值: {result:.{self.precision}f}"

            elif operation == "max":
                result = max(data)
                return f"最大值: {result:.{self.precision}f}"

            elif operation == "min":
                result = min(data)
                return f"最小值: {result:.{self.precision}f}"

            elif operation == "stats":
                stats = self._calculate_stats(data)
                output = "统计信息:\n"
                output += f"  数据点数: {stats['count']}\n"
                output += f"  总和: {stats['sum']:.{self.precision}f}\n"
                output += f"  平均值: {stats['mean']:.{self.precision}f}\n"
                output += f"  最小值: {stats['min']:.{self.precision}f}\n"
                output += f"  最大值: {stats['max']:.{self.precision}f}\n"
                output += f"  范围: {stats['range']:.{self.precision}f}\n"
                output += f"  标准差: {stats['std_dev']:.{self.precision}f}"
                return output

            else:
                return f"错误: 不支持的操作 '{operation}'"

        except ValueError as e:
            return f"验证错误: {str(e)}"
        except Exception as e:
            return f"处理错误: {str(e)}"


def demo_complete_custom_tool():
    """示例7: 完整的自定义工具示例"""
    print_section("示例7: 完整的自定义工具示例")

    tool = DataProcessorTool()

    # 测试数据
    data = [23.5, 45.2, 12.8, 67.9, 34.1, 56.3, 89.0, 12.4, 78.6, 43.2]

    print(f"测试数据: {data}\n")

    # 测试各种操作
    operations = ["sum", "avg", "max", "min", "stats"]

    for op in operations:
        print(f"{op.upper()}:")
        result = tool.invoke({"data": data, "operation": op})
        print(f"{result}\n")

    # 显示工具统计
    print(f"已处理请求数: {tool.processed_count}")
    print(f"最后操作: {tool.last_operation}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 08: 自定义工具")
    print("="*70)

    try:
        # 示例1: StructuredTool
        demo_structured_tool()

        # 示例2: 继承BaseTool
        demo_custom_tool_class()

        # 示例3: 异步工具
        print_section("示例3: 异步工具")
        print("异步工具示例需要在异步环境中运行")
        print("运行: asyncio.run(demo_async_tool())")

        # 示例4: 带状态的工具
        demo_stateful_tool()

        # 示例5: 带回调的工具
        demo_callback_tool()

        # 示例6: 工具日志
        demo_logging_tool()

        # 示例7: 完整示例
        demo_complete_custom_tool()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
