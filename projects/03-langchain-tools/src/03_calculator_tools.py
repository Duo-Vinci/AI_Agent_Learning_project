"""
LangChain 工具使用 - 03: 计算器工具

本模块演示：
1. 基础数学计算工具
2. 科学计算工具
3. 统计计算工具
4. 表达式求值工具
5. 单位转换工具
6. 金融计算工具
7. 计算器工具组合
"""

import os
import math
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

from langchain.tools import tool, BaseTool
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 基础数学计算工具 ====================

@tool
def add(a: float, b: float) -> float:
    """加法运算：计算两个数的和"""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """减法运算：计算两个数的差"""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """乘法运算：计算两个数的积"""
    return a * b


@tool
def divide(a: float, b: float) -> str:
    """除法运算：计算两个数的商，自动处理除零错误"""
    if b == 0:
        return "错误: 除数不能为0"
    return str(a / b)


@tool
def power(base: float, exponent: float) -> float:
    """幂运算：计算base的exponent次方"""
    return base ** exponent


@tool
def square_root(number: float) -> str:
    """平方根：计算数字的平方根"""
    if number < 0:
        return "错误: 不能计算负数的平方根"
    return str(math.sqrt(number))


def demo_basic_math():
    """示例1: 基础数学计算工具"""
    print_section("示例1: 基础数学计算工具")

    tools = [add, subtract, multiply, divide, power, square_root]

    print("可用的数学工具:\n")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    print("\n计算示例:")
    print(f"10 + 5 = {add.invoke({'a': 10, 'b': 5})}")
    print(f"10 - 5 = {subtract.invoke({'a': 10, 'b': 5})}")
    print(f"10 * 5 = {multiply.invoke({'a': 10, 'b': 5})}")
    print(f"10 / 5 = {divide.invoke({'a': 10, 'b': 5})}")
    print(f"2 ^ 8 = {power.invoke({'base': 2, 'exponent': 8})}")
    print(f"√16 = {square_root.invoke({'number': 16})}")
    print(f"10 / 0 = {divide.invoke({'a': 10, 'b': 0})}")


# ==================== 示例2: 科学计算工具 ====================

@tool
def sin(angle_degrees: float) -> float:
    """正弦函数：计算角度的正弦值（输入为度）"""
    return math.sin(math.radians(angle_degrees))


@tool
def cos(angle_degrees: float) -> float:
    """余弦函数：计算角度的余弦值（输入为度）"""
    return math.cos(math.radians(angle_degrees))


@tool
def tan(angle_degrees: float) -> float:
    """正切函数：计算角度的正切值（输入为度）"""
    return math.tan(math.radians(angle_degrees))


@tool
def logarithm(number: float, base: float = math.e) -> str:
    """对数函数：计算number以base为底的对数"""
    if number <= 0:
        return "错误: 对数的真数必须大于0"
    if base <= 0 or base == 1:
        return "错误: 对数的底数必须大于0且不等于1"
    return str(math.log(number, base))


@tool
def factorial(n: int) -> str:
    """阶乘：计算n的阶乘（n!）"""
    if n < 0:
        return "错误: 不能计算负数的阶乘"
    if n > 100:
        return "错误: 数字过大，超出计算范围"
    return str(math.factorial(n))


def demo_scientific_math():
    """示例2: 科学计算工具"""
    print_section("示例2: 科学计算工具")

    print("三角函数计算:")
    print(f"sin(30°) = {sin.invoke({'angle_degrees': 30}):.4f}")
    print(f"cos(60°) = {cos.invoke({'angle_degrees': 60}):.4f}")
    print(f"tan(45°) = {tan.invoke({'angle_degrees': 45}):.4f}\n")

    print("对数计算:")
    print(f"ln(e) = {logarithm.invoke({'number': math.e})}")
    print(f"log₁₀(100) = {logarithm.invoke({'number': 100, 'base': 10})}\n")

    print("阶乘计算:")
    print(f"5! = {factorial.invoke({'n': 5})}")
    print(f"10! = {factorial.invoke({'n': 10})}")


# ==================== 示例3: 统计计算工具 ====================

@tool
def calculate_mean(numbers: List[float]) -> float:
    """平均值：计算一组数字的平均值"""
    if not numbers:
        raise ValueError("数字列表不能为空")
    return sum(numbers) / len(numbers)


@tool
def calculate_median(numbers: List[float]) -> float:
    """中位数：计算一组数字的中位数"""
    if not numbers:
        raise ValueError("数字列表不能为空")
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 0:
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        return sorted_numbers[n//2]


@tool
def calculate_mode(numbers: List[float]) -> str:
    """众数：计算一组数字的众数（出现最频繁的数）"""
    if not numbers:
        return "错误: 数字列表不能为空"

    from collections import Counter
    counts = Counter(numbers)
    max_count = max(counts.values())
    modes = [num for num, count in counts.items() if count == max_count]

    if len(modes) == len(numbers):
        return "无众数（所有数字出现次数相同）"
    return f"众数: {modes}, 出现次数: {max_count}"


@tool
def calculate_standard_deviation(numbers: List[float]) -> float:
    """标准差：计算一组数字的标准差"""
    if not numbers:
        raise ValueError("数字列表不能为空")

    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return math.sqrt(variance)


def demo_statistics():
    """示例3: 统计计算工具"""
    print_section("示例3: 统计计算工具")

    data = [10, 20, 30, 40, 50, 20, 30]

    print(f"数据集: {data}\n")
    print(f"平均值: {calculate_mean.invoke({'numbers': data}):.2f}")
    print(f"中位数: {calculate_median.invoke({'numbers': data}):.2f}")
    print(f"{calculate_mode.invoke({'numbers': data})}")
    print(f"标准差: {calculate_standard_deviation.invoke({'numbers': data}):.2f}")


# ==================== 示例4: 表达式求值工具 ====================

class ExpressionEvaluator:
    """安全的数学表达式求值器"""

    ALLOWED_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'exp': math.exp,
        'pi': math.pi,
        'e': math.e,
    }

    @staticmethod
    def evaluate(expression: str) -> str:
        """
        安全地求值数学表达式

        Args:
            expression: 数学表达式字符串

        Returns:
            计算结果或错误信息
        """
        try:
            # 移除空格
            expression = expression.replace(' ', '')

            # 安全检查：只允许数字、运算符和允许的函数
            if not re.match(r'^[\d+\-*/().a-z,]+$', expression):
                return "错误: 表达式包含不允许的字符"

            # 创建安全的命名空间
            safe_dict = {"__builtins__": {}}
            safe_dict.update(ExpressionEvaluator.ALLOWED_FUNCTIONS)

            # 求值
            result = eval(expression, safe_dict)

            return str(result)

        except ZeroDivisionError:
            return "错误: 除数为0"
        except Exception as e:
            return f"错误: {str(e)}"


@tool
def evaluate_expression(expression: str) -> str:
    """
    计算数学表达式。
    支持基本运算符(+,-,*,/,**)和常用函数(sin,cos,sqrt,log等)。

    示例:
    - "2 + 3 * 4"
    - "sqrt(16) + pow(2, 3)"
    - "sin(pi/2)"
    """
    evaluator = ExpressionEvaluator()
    return evaluator.evaluate(expression)


def demo_expression_evaluator():
    """示例4: 表达式求值工具"""
    print_section("示例4: 表达式求值工具")

    expressions = [
        "2 + 3 * 4",
        "(10 + 5) * 2",
        "sqrt(16) + pow(2, 3)",
        "sin(pi/2)",
        "log(e)",
        "abs(-10) + max(5, 3, 8)",
        "10 / 0",  # 错误示例
    ]

    print("表达式求值测试:\n")
    for expr in expressions:
        result = evaluate_expression.invoke({"expression": expr})
        print(f"{expr:30} = {result}")


# ==================== 示例5: 单位转换工具 ====================

class UnitConverter:
    """单位转换工具"""

    # 长度转换（转换为米）
    LENGTH_UNITS = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'km': 1000.0,
        'inch': 0.0254,
        'foot': 0.3048,
        'yard': 0.9144,
        'mile': 1609.34,
    }

    # 重量转换（转换为千克）
    WEIGHT_UNITS = {
        'mg': 0.000001,
        'g': 0.001,
        'kg': 1.0,
        'ton': 1000.0,
        'oz': 0.0283495,
        'lb': 0.453592,
    }

    # 温度转换
    @staticmethod
    def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
        """温度转换"""
        # 先转换为摄氏度
        if from_unit == 'C':
            celsius = value
        elif from_unit == 'F':
            celsius = (value - 32) * 5/9
        elif from_unit == 'K':
            celsius = value - 273.15
        else:
            raise ValueError(f"不支持的温度单位: {from_unit}")

        # 再转换为目标单位
        if to_unit == 'C':
            return celsius
        elif to_unit == 'F':
            return celsius * 9/5 + 32
        elif to_unit == 'K':
            return celsius + 273.15
        else:
            raise ValueError(f"不支持的温度单位: {to_unit}")

    @staticmethod
    def convert_unit(
        value: float,
        from_unit: str,
        to_unit: str,
        unit_type: str
    ) -> float:
        """通用单位转换"""
        if unit_type == 'length':
            units = UnitConverter.LENGTH_UNITS
        elif unit_type == 'weight':
            units = UnitConverter.WEIGHT_UNITS
        else:
            raise ValueError(f"不支持的单位类型: {unit_type}")

        if from_unit not in units or to_unit not in units:
            raise ValueError("不支持的单位")

        # 转换为基准单位，再转换为目标单位
        base_value = value * units[from_unit]
        result = base_value / units[to_unit]

        return result


@tool
def convert_length(value: float, from_unit: str, to_unit: str) -> str:
    """
    长度单位转换。
    支持: mm, cm, m, km, inch, foot, yard, mile
    """
    try:
        result = UnitConverter.convert_unit(value, from_unit, to_unit, 'length')
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    except Exception as e:
        return f"错误: {str(e)}"


@tool
def convert_weight(value: float, from_unit: str, to_unit: str) -> str:
    """
    重量单位转换。
    支持: mg, g, kg, ton, oz, lb
    """
    try:
        result = UnitConverter.convert_unit(value, from_unit, to_unit, 'weight')
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    except Exception as e:
        return f"错误: {str(e)}"


@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """
    温度单位转换。
    支持: C (摄氏度), F (华氏度), K (开尔文)
    """
    try:
        result = UnitConverter.convert_temperature(value, from_unit, to_unit)
        return f"{value}°{from_unit} = {result:.2f}°{to_unit}"
    except Exception as e:
        return f"错误: {str(e)}"


def demo_unit_conversion():
    """示例5: 单位转换工具"""
    print_section("示例5: 单位转换工具")

    print("长度转换:")
    print(f"  {convert_length.invoke({'value': 1000, 'from_unit': 'mm', 'to_unit': 'm'})}")
    print(f"  {convert_length.invoke({'value': 1, 'from_unit': 'mile', 'to_unit': 'km'})}")

    print("\n重量转换:")
    print(f"  {convert_weight.invoke({'value': 1000, 'from_unit': 'g', 'to_unit': 'kg'})}")
    print(f"  {convert_weight.invoke({'value': 1, 'from_unit': 'lb', 'to_unit': 'kg'})}")

    print("\n温度转换:")
    print(f"  {convert_temperature.invoke({'value': 25, 'from_unit': 'C', 'to_unit': 'F'})}")
    print(f"  {convert_temperature.invoke({'value': 300, 'from_unit': 'K', 'to_unit': 'C'})}")


# ==================== 示例6: 金融计算工具 ====================

@tool
def calculate_compound_interest(
    principal: float,
    rate: float,
    time: float,
    n: int = 1
) -> str:
    """
    计算复利。

    Args:
        principal: 本金
        rate: 年利率（小数形式，如0.05表示5%）
        time: 时间（年）
        n: 每年复利次数（默认1）

    Returns:
        计算结果
    """
    amount = principal * (1 + rate/n) ** (n * time)
    interest = amount - principal

    return f"本金: {principal:.2f}, 利息: {interest:.2f}, 总额: {amount:.2f}"


@tool
def calculate_loan_payment(
    principal: float,
    annual_rate: float,
    months: int
) -> str:
    """
    计算贷款月供。

    Args:
        principal: 贷款本金
        annual_rate: 年利率（小数形式）
        months: 还款月数

    Returns:
        月供金额
    """
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        monthly_payment = principal / months
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                         ((1 + monthly_rate) ** months - 1)

    total_payment = monthly_payment * months
    total_interest = total_payment - principal

    return f"月供: {monthly_payment:.2f}, 总利息: {total_interest:.2f}, 总还款: {total_payment:.2f}"


def demo_financial_calculations():
    """示例6: 金融计算工具"""
    print_section("示例6: 金融计算工具")

    print("复利计算:")
    result = calculate_compound_interest.invoke({
        'principal': 10000,
        'rate': 0.05,
        'time': 10,
        'n': 12
    })
    print(f"  10000元，年利率5%，10年，月复利")
    print(f"  {result}\n")

    print("贷款月供计算:")
    result = calculate_loan_payment.invoke({
        'principal': 100000,
        'annual_rate': 0.05,
        'months': 60
    })
    print(f"  贷款10万，年利率5%，5年（60个月）")
    print(f"  {result}")


# ==================== 示例7: 计算器工具集合 ====================

def demo_calculator_toolkit():
    """示例7: 完整计算器工具集"""
    print_section("示例7: 完整计算器工具集")

    all_tools = [
        # 基础数学
        add, subtract, multiply, divide, power, square_root,
        # 科学计算
        sin, cos, tan, logarithm, factorial,
        # 统计
        calculate_mean, calculate_median, calculate_standard_deviation,
        # 表达式求值
        evaluate_expression,
        # 单位转换
        convert_length, convert_weight, convert_temperature,
        # 金融计算
        calculate_compound_interest, calculate_loan_payment,
    ]

    print(f"计算器工具集包含 {len(all_tools)} 个工具:\n")

    categories = {
        "基础数学": all_tools[0:6],
        "科学计算": all_tools[6:11],
        "统计分析": all_tools[11:14],
        "表达式求值": all_tools[14:15],
        "单位转换": all_tools[15:18],
        "金融计算": all_tools[18:20],
    }

    for category, tools in categories.items():
        print(f"{category} ({len(tools)}个):")
        for tool in tools:
            print(f"  - {tool.name}")
        print()


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 03: 计算器工具")
    print("="*70)

    try:
        # 示例1: 基础数学
        demo_basic_math()

        # 示例2: 科学计算
        demo_scientific_math()

        # 示例3: 统计计算
        demo_statistics()

        # 示例4: 表达式求值
        demo_expression_evaluator()

        # 示例5: 单位转换
        demo_unit_conversion()

        # 示例6: 金融计算
        demo_financial_calculations()

        # 示例7: 工具集合
        demo_calculator_toolkit()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
