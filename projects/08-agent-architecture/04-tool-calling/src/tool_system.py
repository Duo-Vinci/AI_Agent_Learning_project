"""
工具调用系统实现
完整的工具定义、调用、验证和管理

功能特性：
1. 结构化工具定义（使用Pydantic）
2. 工具参数验证
3. 工具调用追踪
4. 错误处理和重试
5. 工具组合和链式调用
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

from pydantic import BaseModel, Field, validator
from langchain.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

load_dotenv()


# ============ 工具参数定义（使用Pydantic）============

class SearchInput(BaseModel):
    """搜索工具输入参数"""
    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    limit: int = Field(default=10, ge=1, le=100, description="返回结果数量")

    @validator('query')
    def query_must_not_be_empty(cls, v):
        """验证查询不为空"""
        if not v.strip():
            raise ValueError('查询不能为空或只包含空格')
        return v.strip()


class CalculatorInput(BaseModel):
    """计算器工具输入参数"""
    expression: str = Field(..., description="数学表达式")

    @validator('expression')
    def validate_expression(cls, v):
        """验证表达式安全性"""
        # 只允许数字和基本运算符
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in v):
            raise ValueError('表达式包含不允许的字符')
        return v


class WeatherInput(BaseModel):
    """天气查询工具输入参数"""
    location: str = Field(..., min_length=1, description="地点名称")
    units: str = Field(default="celsius", description="温度单位：celsius 或 fahrenheit")

    @validator('units')
    def validate_units(cls, v):
        """验证温度单位"""
        if v not in ['celsius', 'fahrenheit']:
            raise ValueError('温度单位必须是 celsius 或 fahrenheit')
        return v


class EmailInput(BaseModel):
    """邮件发送工具输入参数"""
    to: str = Field(..., description="收件人邮箱")
    subject: str = Field(..., min_length=1, max_length=100, description="邮件主题")
    content: str = Field(..., min_length=1, description="邮件内容")

    @validator('to')
    def validate_email(cls, v):
        """简单的邮箱验证"""
        if '@' not in v or '.' not in v:
            raise ValueError('无效的邮箱地址')
        return v


# ============ 工具调用记录 ============

class ToolCallStatus(Enum):
    """工具调用状态"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class ToolCallRecord:
    """
    工具调用记录

    属性:
        tool_name: 工具名称
        input_params: 输入参数
        output: 输出结果
        status: 调用状态
        start_time: 开始时间
        end_time: 结束时间
        error: 错误信息
    """
    tool_name: str
    input_params: Dict[str, Any]
    start_time: datetime = field(default_factory=datetime.now)
    status: ToolCallStatus = ToolCallStatus.PENDING
    output: Optional[str] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None

    @property
    def duration(self) -> float:
        """计算执行时长（秒）"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def __str__(self):
        status_icon = "✅" if self.status == ToolCallStatus.SUCCESS else "❌"
        return f"{status_icon} {self.tool_name}({self.input_params}) -> {self.output}"


# ============ 工具管理器 ============

class ToolManager:
    """
    工具管理器
    负责工具的注册、调用、追踪和统计

    特性：
    - 工具注册和管理
    - 调用历史记录
    - 性能统计
    - 错误处理
    """

    def __init__(self):
        self.tools: Dict[str, StructuredTool] = {}
        self.call_history: List[ToolCallRecord] = []

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        args_schema: Optional[BaseModel] = None
    ):
        """
        注册工具

        参数:
            name: 工具名称
            func: 工具函数
            description: 工具描述
            args_schema: 参数模式（Pydantic模型）
        """
        tool = StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema
        )
        self.tools[name] = tool
        print(f"✅ 已注册工具: {name}")

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        调用工具

        参数:
            tool_name: 工具名称
            **kwargs: 工具参数

        返回:
            工具执行结果
        """
        # 创建调用记录
        record = ToolCallRecord(
            tool_name=tool_name,
            input_params=kwargs
        )

        try:
            if tool_name not in self.tools:
                raise ValueError(f"工具 '{tool_name}' 不存在")

            tool = self.tools[tool_name]

            # 执行工具
            result = tool.run(kwargs)

            # 记录成功
            record.status = ToolCallStatus.SUCCESS
            record.output = str(result)
            record.end_time = datetime.now()

            return result

        except Exception as e:
            # 记录失败
            record.status = ToolCallStatus.FAILED
            record.error = str(e)
            record.end_time = datetime.now()
            raise

        finally:
            # 保存调用记录
            self.call_history.append(record)

    def get_tool_list(self) -> List[StructuredTool]:
        """获取所有工具列表"""
        return list(self.tools.values())

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取工具使用统计

        返回:
            统计信息字典
        """
        total_calls = len(self.call_history)
        success_calls = sum(1 for r in self.call_history
                          if r.status == ToolCallStatus.SUCCESS)
        failed_calls = total_calls - success_calls

        tool_usage = {}
        for record in self.call_history:
            if record.tool_name not in tool_usage:
                tool_usage[record.tool_name] = {
                    'count': 0,
                    'success': 0,
                    'failed': 0,
                    'avg_duration': 0.0
                }

            tool_usage[record.tool_name]['count'] += 1
            if record.status == ToolCallStatus.SUCCESS:
                tool_usage[record.tool_name]['success'] += 1
            else:
                tool_usage[record.tool_name]['failed'] += 1

        return {
            'total_calls': total_calls,
            'success_calls': success_calls,
            'failed_calls': failed_calls,
            'success_rate': success_calls / total_calls if total_calls > 0 else 0,
            'tool_usage': tool_usage
        }

    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("工具使用统计")
        print("="*60)
        print(f"总调用次数: {stats['total_calls']}")
        print(f"成功: {stats['success_calls']}")
        print(f"失败: {stats['failed_calls']}")
        print(f"成功率: {stats['success_rate']:.1%}")

        print("\n各工具使用情况:")
        for tool_name, usage in stats['tool_usage'].items():
            print(f"  {tool_name}:")
            print(f"    调用次数: {usage['count']}")
            print(f"    成功: {usage['success']}, 失败: {usage['failed']}")

        print("="*60)


# ============ 具体工具实现 ============

def search_web(query: str, limit: int = 10) -> str:
    """
    网络搜索工具

    参数:
        query: 搜索关键词
        limit: 返回结果数量

    返回:
        搜索结果
    """
    # 模拟搜索
    results = {
        "人工智能": "人工智能(AI)是计算机科学的一个分支...",
        "机器学习": "机器学习是AI的子集，专注于让计算机从数据中学习...",
        "深度学习": "深度学习使用多层神经网络来学习数据表示..."
    }

    for key, value in results.items():
        if key in query:
            return f"搜索结果（共{limit}条）：\n{value}"

    return f"搜索'{query}'，找到{limit}条结果"


def calculate_math(expression: str) -> str:
    """
    数学计算工具

    参数:
        expression: 数学表达式

    返回:
        计算结果
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def get_weather(location: str, units: str = "celsius") -> str:
    """
    天气查询工具

    参数:
        location: 地点
        units: 温度单位

    返回:
        天气信息
    """
    # 模拟天气数据
    weather_data = {
        "北京": {"temp_c": 25, "desc": "晴天"},
        "上海": {"temp_c": 28, "desc": "多云"},
        "深圳": {"temp_c": 30, "desc": "小雨"}
    }

    if location in weather_data:
        data = weather_data[location]
        temp = data["temp_c"]

        if units == "fahrenheit":
            temp = temp * 9/5 + 32
            unit_str = "°F"
        else:
            unit_str = "°C"

        return f"{location}的天气：{data['desc']}，温度{temp}{unit_str}"

    return f"{location}的天气：晴天，温度22°C"


def send_email(to: str, subject: str, content: str) -> str:
    """
    发送邮件工具（模拟）

    参数:
        to: 收件人
        subject: 主题
        content: 内容

    返回:
        发送结果
    """
    # 模拟发送
    print(f"\n📧 发送邮件:")
    print(f"  收件人: {to}")
    print(f"  主题: {subject}")
    print(f"  内容: {content[:50]}...")

    return f"邮件已发送到 {to}"


def get_current_time() -> str:
    """
    获取当前时间

    返回:
        当前时间字符串
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# ============ 创建工具管理器并注册工具 ============

def create_tool_manager() -> ToolManager:
    """
    创建并配置工具管理器

    返回:
        配置好的工具管理器
    """
    manager = ToolManager()

    # 注册工具（带参数验证）
    manager.register_tool(
        name="Search",
        func=search_web,
        description="在网络上搜索信息。输入搜索关键词和结果数量（可选）。",
        args_schema=SearchInput
    )

    manager.register_tool(
        name="Calculator",
        func=calculate_math,
        description="执行数学计算。输入数学表达式，如'2+3*4'。",
        args_schema=CalculatorInput
    )

    manager.register_tool(
        name="Weather",
        func=get_weather,
        description="查询天气信息。输入地点名称和温度单位（可选）。",
        args_schema=WeatherInput
    )

    manager.register_tool(
        name="Email",
        func=send_email,
        description="发送邮件。输入收件人、主题和内容。",
        args_schema=EmailInput
    )

    manager.register_tool(
        name="GetTime",
        func=get_current_time,
        description="获取当前时间。"
    )

    return manager


# ============ 带工具的Agent ============

def create_agent_with_tools(tool_manager: ToolManager) -> AgentExecutor:
    """
    创建带工具的Agent

    参数:
        tool_manager: 工具管理器

    返回:
        Agent执行器
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    tools = tool_manager.get_tool_list()

    prompt = PromptTemplate(
        template="""你是一个助手，可以使用工具帮助用户。

可用工具：
{tools}

工具名称: {tool_names}

格式：
Question: 用户问题
Thought: 思考
Action: 工具名称
Action Input: 工具输入（JSON格式）
Observation: 工具输出
... (重复)
Thought: 知道答案了
Final Answer: 最终答案

Question: {input}
Thought: {agent_scratchpad}
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
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )

    return agent_executor


# ============ 测试示例 ============

def run_examples():
    """运行示例"""

    print("="*80)
    print("工具调用系统示例")
    print("="*80)

    # 创建工具管理器
    tool_manager = create_tool_manager()

    # 示例1：直接调用工具
    print("\n【示例1】直接调用工具")
    print("-"*80)

    try:
        result = tool_manager.call_tool("Search", query="人工智能", limit=5)
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {e}")

    try:
        result = tool_manager.call_tool("Calculator", expression="10 * 5 + 3")
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {e}")

    # 示例2：参数验证
    print("\n【示例2】参数验证")
    print("-"*80)

    try:
        # 这会失败，因为query为空
        result = tool_manager.call_tool("Search", query="", limit=5)
    except Exception as e:
        print(f"✅ 捕获到验证错误: {e}")

    try:
        # 这会失败，因为包含非法字符
        result = tool_manager.call_tool("Calculator", expression="import os")
    except Exception as e:
        print(f"✅ 捕获到验证错误: {e}")

    # 示例3：使用Agent调用工具
    print("\n【示例3】Agent调用工具")
    print("-"*80)

    agent = create_agent_with_tools(tool_manager)

    result = agent.invoke({
        "input": "查询北京的天气，如果是25度，用华氏度是多少？"
    })

    print(f"\n最终答案: {result['output']}")

    # 显示统计
    tool_manager.print_statistics()


if __name__ == "__main__":
    run_examples()
