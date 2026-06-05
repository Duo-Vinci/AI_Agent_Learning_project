"""
LangChain 工具使用 - 10: 完整工具系统

本模块演示：
1. 完整的工具管理系统
2. 工具注册表
3. 动态工具加载
4. 工具性能监控
5. 工具权限管理
6. Agent集成工具系统
7. 实际应用场景
"""

import os
import time
import json
from typing import Optional, Type, List, Dict, Any, Callable
from datetime import datetime
from collections import defaultdict

from langchain.tools import BaseTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 工具注册表 ====================

class ToolRegistry:
    """工具注册表 - 管理所有可用工具"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = defaultdict(list)
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        tool: BaseTool,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        注册工具

        Args:
            tool: 工具实例
            category: 工具分类
            metadata: 工具元数据
        """
        tool_name = tool.name

        if tool_name in self._tools:
            raise ValueError(f"工具 '{tool_name}' 已经注册")

        self._tools[tool_name] = tool
        self._categories[category].append(tool_name)
        self._metadata[tool_name] = metadata or {}

        print(f"✓ 已注册工具: {tool_name} (分类: {category})")

    def unregister(self, tool_name: str) -> None:
        """注销工具"""
        if tool_name not in self._tools:
            raise ValueError(f"工具 '{tool_name}' 未注册")

        # 从分类中移除
        for category, tools in self._categories.items():
            if tool_name in tools:
                tools.remove(tool_name)

        del self._tools[tool_name]
        del self._metadata[tool_name]

        print(f"✓ 已注销工具: {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(tool_name)

    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """获取指定分类的工具"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names]

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具"""
        return list(self._tools.values())

    def list_tools(self) -> str:
        """列出所有工具"""
        if not self._tools:
            return "没有注册的工具"

        output = "已注册的工具:\n"

        for category, tool_names in sorted(self._categories.items()):
            output += f"\n📁 {category}:\n"
            for name in tool_names:
                tool = self._tools[name]
                desc = tool.description.split('\n')[0][:50]
                output += f"  - {name}: {desc}...\n"

        return output

    def search_tools(self, keyword: str) -> List[BaseTool]:
        """搜索工具"""
        keyword_lower = keyword.lower()
        results = []

        for tool in self._tools.values():
            if (keyword_lower in tool.name.lower() or
                keyword_lower in tool.description.lower()):
                results.append(tool)

        return results


# ==================== 工具性能监控 ====================

class ToolPerformanceMonitor:
    """工具性能监控器"""

    def __init__(self):
        self._call_count: Dict[str, int] = defaultdict(int)
        self._total_time: Dict[str, float] = defaultdict(float)
        self._error_count: Dict[str, int] = defaultdict(int)
        self._last_call: Dict[str, datetime] = {}

    def record_call(
        self,
        tool_name: str,
        duration: float,
        success: bool = True
    ) -> None:
        """记录工具调用"""
        self._call_count[tool_name] += 1
        self._total_time[tool_name] += duration
        self._last_call[tool_name] = datetime.now()

        if not success:
            self._error_count[tool_name] += 1

    def get_stats(self, tool_name: str) -> Dict[str, Any]:
        """获取工具统计信息"""
        call_count = self._call_count[tool_name]

        if call_count == 0:
            return {"error": "该工具未被调用"}

        avg_time = self._total_time[tool_name] / call_count
        error_rate = self._error_count[tool_name] / call_count

        return {
            "tool_name": tool_name,
            "call_count": call_count,
            "total_time": f"{self._total_time[tool_name]:.3f}s",
            "avg_time": f"{avg_time:.3f}s",
            "error_count": self._error_count[tool_name],
            "error_rate": f"{error_rate:.2%}",
            "last_call": self._last_call[tool_name].strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_all_stats(self) -> List[Dict[str, Any]]:
        """获取所有工具统计"""
        stats = []

        for tool_name in self._call_count.keys():
            stats.append(self.get_stats(tool_name))

        # 按调用次数排序
        stats.sort(key=lambda x: x["call_count"], reverse=True)

        return stats

    def print_report(self) -> None:
        """打印性能报告"""
        stats = self.get_all_stats()

        if not stats:
            print("没有工具调用记录")
            return

        print("工具性能报告:\n")
        print(f"{'工具名称':<20} {'调用次数':<10} {'平均耗时':<12} {'错误率':<10}")
        print("-" * 60)

        for stat in stats:
            print(f"{stat['tool_name']:<20} "
                  f"{stat['call_count']:<10} "
                  f"{stat['avg_time']:<12} "
                  f"{stat['error_rate']:<10}")


# ==================== 工具包装器（添加监控）====================

class MonitoredToolWrapper(BaseTool):
    """带监控的工具包装器"""

    def __init__(
        self,
        tool: BaseTool,
        monitor: ToolPerformanceMonitor
    ):
        super().__init__()
        self._tool = tool
        self._monitor = monitor

        # 复制工具属性
        self.name = tool.name
        self.description = tool.description
        self.args_schema = tool.args_schema

    def _run(self, *args, **kwargs) -> Any:
        """执行工具（带监控）"""
        start_time = time.time()
        success = True

        try:
            result = self._tool._run(*args, **kwargs)
            return result

        except Exception as e:
            success = False
            raise

        finally:
            duration = time.time() - start_time
            self._monitor.record_call(self.name, duration, success)


# ==================== 工具权限管理 ====================

class ToolPermissionManager:
    """工具权限管理器"""

    def __init__(self):
        self._permissions: Dict[str, List[str]] = defaultdict(list)

    def grant_permission(self, user: str, tool_name: str) -> None:
        """授予权限"""
        if tool_name not in self._permissions[user]:
            self._permissions[user].append(tool_name)
            print(f"✓ 已授予 {user} 使用 {tool_name} 的权限")

    def revoke_permission(self, user: str, tool_name: str) -> None:
        """撤销权限"""
        if tool_name in self._permissions[user]:
            self._permissions[user].remove(tool_name)
            print(f"✓ 已撤销 {user} 使用 {tool_name} 的权限")

    def check_permission(self, user: str, tool_name: str) -> bool:
        """检查权限"""
        return tool_name in self._permissions[user]

    def get_user_permissions(self, user: str) -> List[str]:
        """获取用户权限"""
        return self._permissions.get(user, [])


# ==================== 示例工具定义 ====================

# 工具1: 文本分析工具
class TextAnalyzerInput(BaseModel):
    text: str = Field(description="要分析的文本")


class TextAnalyzerTool(BaseTool):
    name: str = "text_analyzer"
    description: str = "分析文本内容，返回统计信息"
    args_schema: Type[BaseModel] = TextAnalyzerInput

    def _run(
        self,
        text: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        words = text.split()
        chars = len(text)
        sentences = text.count('.') + text.count('!') + text.count('?')

        return json.dumps({
            "字符数": chars,
            "单词数": len(words),
            "句子数": sentences,
            "平均词长": f"{sum(len(w) for w in words) / len(words):.1f}" if words else "0"
        }, ensure_ascii=False)


# 工具2: 数据转换工具
class DataConverterInput(BaseModel):
    data: str = Field(description="要转换的数据")
    from_format: str = Field(description="源格式: json/csv")
    to_format: str = Field(description="目标格式: json/csv")


class DataConverterTool(BaseTool):
    name: str = "data_converter"
    description: str = "转换数据格式（JSON <-> CSV）"
    args_schema: Type[BaseModel] = DataConverterInput

    def _run(
        self,
        data: str,
        from_format: str,
        to_format: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # 简化实现
        if from_format == "json" and to_format == "csv":
            return "已转换为CSV格式"
        elif from_format == "csv" and to_format == "json":
            return "已转换为JSON格式"
        else:
            return f"不支持的转换: {from_format} -> {to_format}"


# 工具3: 数据验证工具
class DataValidatorInput(BaseModel):
    data: Dict[str, Any] = Field(description="要验证的数据")
    schema: Dict[str, str] = Field(description="验证模式")


class DataValidatorTool(BaseTool):
    name: str = "data_validator"
    description: str = "验证数据是否符合模式"
    args_schema: Type[BaseModel] = DataValidatorInput

    def _run(
        self,
        data: Dict[str, Any],
        schema: Dict[str, str],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        errors = []

        for field, expected_type in schema.items():
            if field not in data:
                errors.append(f"缺少字段: {field}")
            else:
                actual_type = type(data[field]).__name__
                if actual_type != expected_type:
                    errors.append(f"字段 {field} 类型错误: 期望 {expected_type}, 实际 {actual_type}")

        if errors:
            return "验证失败:\n" + "\n".join(f"  - {e}" for e in errors)
        else:
            return "✓ 验证通过"


# 工具4: 计算工具
class CalculatorInput(BaseModel):
    expression: str = Field(description="数学表达式")


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "计算数学表达式"
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(
        self,
        expression: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"


# ==================== 完整的工具管理系统 ====================

class ToolManagementSystem:
    """完整的工具管理系统"""

    def __init__(self):
        self.registry = ToolRegistry()
        self.monitor = ToolPerformanceMonitor()
        self.permission_manager = ToolPermissionManager()

    def register_tool(
        self,
        tool: BaseTool,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """注册工具（带监控包装）"""
        # 包装工具添加监控
        monitored_tool = MonitoredToolWrapper(tool, self.monitor)

        # 注册到注册表
        self.registry.register(monitored_tool, category, metadata)

    def execute_tool(
        self,
        user: str,
        tool_name: str,
        params: Dict[str, Any]
    ) -> str:
        """执行工具（带权限检查）"""
        # 检查权限
        if not self.permission_manager.check_permission(user, tool_name):
            return f"✗ 权限不足: 用户 '{user}' 无权使用工具 '{tool_name}'"

        # 获取工具
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return f"✗ 工具不存在: '{tool_name}'"

        # 执行工具
        try:
            result = tool.invoke(params)
            return result
        except Exception as e:
            return f"✗ 执行错误: {str(e)}"

    def get_available_tools(self, user: str) -> List[BaseTool]:
        """获取用户可用的工具"""
        permissions = self.permission_manager.get_user_permissions(user)
        tools = []

        for tool_name in permissions:
            tool = self.registry.get_tool(tool_name)
            if tool:
                tools.append(tool)

        return tools


# ==================== 示例1: 工具注册和管理 ====================

def demo_tool_registration():
    """示例1: 工具注册和管理"""
    print_section("示例1: 工具注册和管理")

    system = ToolManagementSystem()

    # 注册工具
    print("注册工具:")
    system.register_tool(TextAnalyzerTool(), "文本处理", {"version": "1.0"})
    system.register_tool(DataConverterTool(), "数据处理", {"version": "1.0"})
    system.register_tool(DataValidatorTool(), "数据处理", {"version": "1.0"})
    system.register_tool(CalculatorTool(), "计算", {"version": "1.0"})

    # 列出工具
    print(f"\n{system.registry.list_tools()}")

    # 搜索工具
    print("\n搜索包含'数据'的工具:")
    results = system.registry.search_tools("数据")
    for tool in results:
        print(f"  - {tool.name}")


# ==================== 示例2: 工具权限管理 ====================

def demo_permission_management():
    """示例2: 工具权限管理"""
    print_section("示例2: 工具权限管理")

    system = ToolManagementSystem()

    # 注册工具
    system.register_tool(TextAnalyzerTool(), "文本处理")
    system.register_tool(CalculatorTool(), "计算")

    # 授予权限
    print("授予权限:")
    system.permission_manager.grant_permission("user1", "text_analyzer")
    system.permission_manager.grant_permission("user1", "calculator")
    system.permission_manager.grant_permission("user2", "text_analyzer")

    # 检查权限
    print("\n检查权限:")
    print(f"user1 可使用 text_analyzer: {system.permission_manager.check_permission('user1', 'text_analyzer')}")
    print(f"user2 可使用 calculator: {system.permission_manager.check_permission('user2', 'calculator')}")

    # 执行工具
    print("\n执行工具:")
    result = system.execute_tool(
        "user1",
        "text_analyzer",
        {"text": "Hello LangChain! This is a test."}
    )
    print(f"user1 执行 text_analyzer: {result}")

    result = system.execute_tool(
        "user2",
        "calculator",
        {"expression": "10 + 20"}
    )
    print(f"user2 执行 calculator: {result}")


# ==================== 示例3: 工具性能监控 ====================

def demo_performance_monitoring():
    """示例3: 工具性能监控"""
    print_section("示例3: 工具性能监控")

    system = ToolManagementSystem()

    # 注册工具
    system.register_tool(TextAnalyzerTool(), "文本处理")
    system.register_tool(CalculatorTool(), "计算")

    # 授予权限
    system.permission_manager.grant_permission("admin", "text_analyzer")
    system.permission_manager.grant_permission("admin", "calculator")

    # 执行多次工具调用
    print("\n执行工具调用:")
    for i in range(5):
        system.execute_tool(
            "admin",
            "text_analyzer",
            {"text": f"Test message number {i+1}"}
        )

    for i in range(3):
        system.execute_tool(
            "admin",
            "calculator",
            {"expression": f"{i+1} * 10"}
        )

    # 查看性能报告
    print("\n")
    system.monitor.print_report()


# ==================== 示例4: 集成Agent示例 ====================

class SimpleToolAgent:
    """简单的工具Agent"""

    def __init__(self, system: ToolManagementSystem, user: str):
        self.system = system
        self.user = user
        self.available_tools = system.get_available_tools(user)

    def process_request(self, request: str) -> str:
        """处理用户请求"""
        print(f"\n用户请求: {request}")

        # 简单的工具选择逻辑
        if "分析" in request or "统计" in request:
            tool_name = "text_analyzer"
            params = {"text": request}
        elif "计算" in request:
            # 提取表达式
            import re
            match = re.search(r'[\d+\-*/\s]+', request)
            if match:
                params = {"expression": match.group().strip()}
                tool_name = "calculator"
            else:
                return "无法识别计算表达式"
        else:
            return "无法确定使用哪个工具"

        print(f"选择工具: {tool_name}")

        # 执行工具
        result = self.system.execute_tool(self.user, tool_name, params)

        return result


def demo_agent_integration():
    """示例4: 集成Agent"""
    print_section("示例4: 集成Agent")

    # 创建系统
    system = ToolManagementSystem()

    # 注册工具
    system.register_tool(TextAnalyzerTool(), "文本处理")
    system.register_tool(CalculatorTool(), "计算")

    # 授予权限
    system.permission_manager.grant_permission("agent_user", "text_analyzer")
    system.permission_manager.grant_permission("agent_user", "calculator")

    # 创建Agent
    agent = SimpleToolAgent(system, "agent_user")

    # 测试请求
    requests = [
        "请分析这段文本: LangChain is amazing!",
        "帮我计算 25 * 4 + 10",
        "分析一下今天的天气",  # 无合适工具
    ]

    for request in requests:
        result = agent.process_request(request)
        print(f"结果: {result}\n")


# ==================== 示例5: 实际应用场景 ====================

def demo_real_world_scenario():
    """示例5: 实际应用场景 - 数据处理工作流"""
    print_section("示例5: 实际应用场景 - 数据处理工作流")

    system = ToolManagementSystem()

    # 注册所有工具
    system.register_tool(TextAnalyzerTool(), "文本处理")
    system.register_tool(DataConverterTool(), "数据处理")
    system.register_tool(DataValidatorTool(), "数据处理")
    system.register_tool(CalculatorTool(), "计算")

    # 设置数据分析师权限
    analyst = "data_analyst"
    for tool_name in ["text_analyzer", "data_converter", "data_validator", "calculator"]:
        system.permission_manager.grant_permission(analyst, tool_name)

    print("场景: 数据分析师处理文本数据\n")

    # 步骤1: 分析文本
    print("步骤1: 分析文本数据")
    text = "LangChain provides a comprehensive toolkit for building AI applications. It includes tools, agents, and memory systems."
    result1 = system.execute_tool(
        analyst,
        "text_analyzer",
        {"text": text}
    )
    print(f"分析结果: {result1}\n")

    # 步骤2: 验证数据
    print("步骤2: 验证数据结构")
    data = {"name": "John", "age": 30, "email": "john@example.com"}
    schema = {"name": "str", "age": "int", "email": "str"}
    result2 = system.execute_tool(
        analyst,
        "data_validator",
        {"data": data, "schema": schema}
    )
    print(f"验证结果: {result2}\n")

    # 步骤3: 数学计算
    print("步骤3: 计算统计值")
    result3 = system.execute_tool(
        analyst,
        "calculator",
        {"expression": "30 * 2 + 10"}
    )
    print(f"计算结果: {result3}\n")

    # 查看性能报告
    print("性能报告:")
    system.monitor.print_report()


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 10: 完整工具系统")
    print("="*70)

    try:
        # 示例1: 工具注册
        demo_tool_registration()

        # 示例2: 权限管理
        demo_permission_management()

        # 示例3: 性能监控
        demo_performance_monitoring()

        # 示例4: Agent集成
        demo_agent_integration()

        # 示例5: 实际应用
        demo_real_world_scenario()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  ")
        print("  本模块演示了完整的工具管理系统，包括：")
        print("  - 工具注册表和分类管理")
        print("  - 工具权限控制")
        print("  - 性能监控和统计")
        print("  - Agent集成")
        print("  - 实际应用场景")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
