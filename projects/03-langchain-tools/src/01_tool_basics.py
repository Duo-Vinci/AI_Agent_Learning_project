"""
LangChain 工具使用 - 01: 工具基础

本模块演示：
1. 什么是工具（Tool）
2. 工具的基本结构
3. 创建简单工具
4. 工具的参数和返回值
5. 工具的描述和元数据
6. 工具的错误处理
7. 同步和异步工具
"""

import os
from typing import Optional, Type
from datetime import datetime
from dotenv import load_dotenv

from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 使用装饰器创建简单工具 ====================

@tool
def get_current_time() -> str:
    """获取当前时间。这个工具不需要任何参数。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate_sum(a: int, b: int) -> int:
    """
    计算两个数的和。

    Args:
        a: 第一个数字
        b: 第二个数字

    Returns:
        两个数字的和
    """
    return a + b


@tool
def string_length(text: str) -> int:
    """
    计算字符串长度。

    Args:
        text: 要计算长度的字符串

    Returns:
        字符串的长度
    """
    return len(text)


def demo_simple_tools():
    """示例1: 使用装饰器创建简单工具"""
    print_section("示例1: 使用装饰器创建简单工具")

    # 测试时间工具
    print("工具1: get_current_time")
    print(f"名称: {get_current_time.name}")
    print(f"描述: {get_current_time.description}")
    print(f"参数: {get_current_time.args}")
    print(f"执行结果: {get_current_time.invoke({})}\n")

    # 测试计算工具
    print("工具2: calculate_sum")
    print(f"名称: {calculate_sum.name}")
    print(f"描述: {calculate_sum.description}")
    print(f"参数: {calculate_sum.args}")
    result = calculate_sum.invoke({"a": 10, "b": 20})
    print(f"执行结果: calculate_sum(10, 20) = {result}\n")

    # 测试字符串工具
    print("工具3: string_length")
    print(f"名称: {string_length.name}")
    print(f"描述: {string_length.description}")
    result = string_length.invoke({"text": "Hello, LangChain!"})
    print(f"执行结果: string_length('Hello, LangChain!') = {result}")


# ==================== 示例2: 使用StructuredTool创建工具 ====================

def multiply_numbers(a: float, b: float) -> float:
    """将两个数字相乘"""
    return a * b


def divide_numbers(a: float, b: float) -> str:
    """将两个数字相除，处理除零错误"""
    if b == 0:
        return "错误: 除数不能为0"
    return str(a / b)


def demo_structured_tools():
    """示例2: 使用StructuredTool创建工具"""
    print_section("示例2: 使用StructuredTool创建工具")

    # 创建乘法工具
    multiply_tool = StructuredTool.from_function(
        func=multiply_numbers,
        name="multiply",
        description="将两个数字相乘。当需要计算乘积时使用这个工具。"
    )

    # 创建除法工具
    divide_tool = StructuredTool.from_function(
        func=divide_numbers,
        name="divide",
        description="将两个数字相除。自动处理除零错误。"
    )

    print("乘法工具测试:")
    result = multiply_tool.invoke({"a": 5.5, "b": 2.0})
    print(f"5.5 * 2.0 = {result}\n")

    print("除法工具测试:")
    result = divide_tool.invoke({"a": 10.0, "b": 2.0})
    print(f"10.0 / 2.0 = {result}")

    result = divide_tool.invoke({"a": 10.0, "b": 0.0})
    print(f"10.0 / 0.0 = {result}")


# ==================== 示例3: 使用BaseTool创建自定义工具类 ====================

class TemperatureConverterInput(BaseModel):
    """温度转换工具的输入模式"""
    temperature: float = Field(description="要转换的温度值")
    from_unit: str = Field(description="原始温度单位 (C, F, K)")
    to_unit: str = Field(description="目标温度单位 (C, F, K)")


class TemperatureConverterTool(BaseTool):
    """温度转换工具"""

    name: str = "temperature_converter"
    description: str = """
    转换不同单位的温度值。
    支持摄氏度(C)、华氏度(F)和开尔文(K)之间的相互转换。

    使用示例:
    - 将 25°C 转换为 F
    - 将 77°F 转换为 C
    - 将 300K 转换为 C
    """
    args_schema: Type[BaseModel] = TemperatureConverterInput

    def _run(
        self,
        temperature: float,
        from_unit: str,
        to_unit: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行温度转换"""
        from_unit = from_unit.upper()
        to_unit = to_unit.upper()

        # 先转换为摄氏度
        if from_unit == "C":
            celsius = temperature
        elif from_unit == "F":
            celsius = (temperature - 32) * 5/9
        elif from_unit == "K":
            celsius = temperature - 273.15
        else:
            return f"错误: 不支持的温度单位 '{from_unit}'"

        # 再转换为目标单位
        if to_unit == "C":
            result = celsius
        elif to_unit == "F":
            result = celsius * 9/5 + 32
        elif to_unit == "K":
            result = celsius + 273.15
        else:
            return f"错误: 不支持的温度单位 '{to_unit}'"

        return f"{temperature}°{from_unit} = {result:.2f}°{to_unit}"

    async def _arun(
        self,
        temperature: float,
        from_unit: str,
        to_unit: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """异步执行（这里简单调用同步方法）"""
        return self._run(temperature, from_unit, to_unit, run_manager)


def demo_custom_tool_class():
    """示例3: 使用BaseTool创建自定义工具类"""
    print_section("示例3: 使用BaseTool创建自定义工具类")

    converter = TemperatureConverterTool()

    print("工具信息:")
    print(f"名称: {converter.name}")
    print(f"描述: {converter.description.strip()}\n")

    # 测试转换
    test_cases = [
        {"temperature": 25, "from_unit": "C", "to_unit": "F"},
        {"temperature": 77, "from_unit": "F", "to_unit": "C"},
        {"temperature": 300, "from_unit": "K", "to_unit": "C"},
        {"temperature": 0, "from_unit": "C", "to_unit": "K"}
    ]

    print("转换测试:")
    for case in test_cases:
        result = converter.invoke(case)
        print(f"  {result}")


# ==================== 示例4: 工具参数验证 ====================

class StringOperationInput(BaseModel):
    """字符串操作输入模式"""
    text: str = Field(description="要操作的字符串")
    operation: str = Field(
        description="操作类型: upper, lower, reverse, capitalize"
    )
    repeat: int = Field(
        default=1,
        ge=1,
        le=10,
        description="重复次数（1-10）"
    )


class StringOperationTool(BaseTool):
    """字符串操作工具（带参数验证）"""

    name: str = "string_operation"
    description: str = "对字符串执行各种操作（大写、小写、反转、首字母大写）"
    args_schema: Type[BaseModel] = StringOperationInput

    def _run(
        self,
        text: str,
        operation: str,
        repeat: int = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行字符串操作"""
        operation = operation.lower()

        if operation == "upper":
            result = text.upper()
        elif operation == "lower":
            result = text.lower()
        elif operation == "reverse":
            result = text[::-1]
        elif operation == "capitalize":
            result = text.capitalize()
        else:
            return f"错误: 不支持的操作 '{operation}'"

        # 重复指定次数
        return result * repeat


def demo_parameter_validation():
    """示例4: 工具参数验证"""
    print_section("示例4: 工具参数验证")

    tool = StringOperationTool()

    print("测试各种字符串操作:\n")

    test_cases = [
        {"text": "hello world", "operation": "upper", "repeat": 1},
        {"text": "HELLO WORLD", "operation": "lower", "repeat": 1},
        {"text": "hello", "operation": "reverse", "repeat": 1},
        {"text": "hello world", "operation": "capitalize", "repeat": 1},
        {"text": "Hi! ", "operation": "upper", "repeat": 3},
    ]

    for case in test_cases:
        result = tool.invoke(case)
        print(f"  {case['operation']}('{case['text']}', repeat={case['repeat']}) = '{result}'")

    # 测试参数验证
    print("\n测试参数验证（无效操作）:")
    try:
        result = tool.invoke({
            "text": "test",
            "operation": "invalid",
            "repeat": 1
        })
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  捕获错误: {str(e)}")


# ==================== 示例5: 工具返回值类型 ====================

@tool
def get_user_info(user_id: int) -> dict:
    """
    根据用户ID获取用户信息。

    Args:
        user_id: 用户ID

    Returns:
        包含用户信息的字典
    """
    # 模拟数据库查询
    users = {
        1: {"name": "张三", "age": 25, "email": "zhangsan@example.com"},
        2: {"name": "李四", "age": 30, "email": "lisi@example.com"},
        3: {"name": "王五", "age": 28, "email": "wangwu@example.com"}
    }

    user = users.get(user_id)
    if user:
        return {"user_id": user_id, **user}
    else:
        return {"error": f"未找到ID为{user_id}的用户"}


@tool
def calculate_statistics(numbers: list) -> dict:
    """
    计算数字列表的统计信息。

    Args:
        numbers: 数字列表

    Returns:
        包含统计信息的字典（最小值、最大值、平均值、总和）
    """
    if not numbers:
        return {"error": "数字列表为空"}

    return {
        "count": len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers)
    }


def demo_return_types():
    """示例5: 工具返回值类型"""
    print_section("示例5: 工具返回值类型")

    print("工具1: get_user_info (返回字典)")
    for user_id in [1, 2, 99]:
        result = get_user_info.invoke({"user_id": user_id})
        print(f"  用户{user_id}: {result}")

    print("\n工具2: calculate_statistics (返回字典)")
    numbers = [10, 20, 30, 40, 50]
    result = calculate_statistics.invoke({"numbers": numbers})
    print(f"  数据: {numbers}")
    print(f"  统计: {result}")


# ==================== 示例6: 工具错误处理 ====================

class SafeDivisionTool(BaseTool):
    """安全除法工具（完善的错误处理）"""

    name: str = "safe_division"
    description: str = "安全地执行除法运算，包含完整的错误处理"

    class InputSchema(BaseModel):
        dividend: float = Field(description="被除数")
        divisor: float = Field(description="除数")

    args_schema: Type[BaseModel] = InputSchema

    def _run(
        self,
        dividend: float,
        divisor: float,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> dict:
        """执行安全除法"""
        try:
            if divisor == 0:
                return {
                    "success": False,
                    "error": "除数不能为0",
                    "error_type": "ZeroDivisionError"
                }

            result = dividend / divisor

            return {
                "success": True,
                "result": result,
                "dividend": dividend,
                "divisor": divisor
            }

        except TypeError as e:
            return {
                "success": False,
                "error": f"类型错误: {str(e)}",
                "error_type": "TypeError"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"未知错误: {str(e)}",
                "error_type": type(e).__name__
            }


def demo_error_handling():
    """示例6: 工具错误处理"""
    print_section("示例6: 工具错误处理")

    tool = SafeDivisionTool()

    test_cases = [
        {"dividend": 10, "divisor": 2},
        {"dividend": 10, "divisor": 0},
        {"dividend": 7, "divisor": 3},
    ]

    print("除法运算测试:\n")
    for case in test_cases:
        result = tool.invoke(case)
        if result["success"]:
            print(f"  {case['dividend']} / {case['divisor']} = {result['result']:.4f}")
        else:
            print(f"  {case['dividend']} / {case['divisor']} = 错误: {result['error']}")


# ==================== 示例7: 工具组合 ====================

def demo_tool_composition():
    """示例7: 工具组合使用"""
    print_section("示例7: 工具组合使用")

    # 创建多个工具
    tools = [
        get_current_time,
        calculate_sum,
        string_length,
        TemperatureConverterTool(),
        StringOperationTool()
    ]

    print("可用工具列表:\n")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   描述: {tool.description[:50]}...")
        print()

    # 演示组合使用
    print("组合使用示例:")
    time = get_current_time.invoke({})
    print(f"1. 获取当前时间: {time}")

    sum_result = calculate_sum.invoke({"a": 10, "b": 20})
    print(f"2. 计算和: 10 + 20 = {sum_result}")

    length = string_length.invoke({"text": time})
    print(f"3. 时间字符串长度: {length}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 01: 工具基础")
    print("="*70)

    try:
        # 示例1: 简单工具
        demo_simple_tools()

        # 示例2: StructuredTool
        demo_structured_tools()

        # 示例3: 自定义工具类
        demo_custom_tool_class()

        # 示例4: 参数验证
        demo_parameter_validation()

        # 示例5: 返回值类型
        demo_return_types()

        # 示例6: 错误处理
        demo_error_handling()

        # 示例7: 工具组合
        demo_tool_composition()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
