"""
Agent调试工具

Agent调试是开发和优化Agent系统的关键环节。
本模块提供了全面的调试工具和技术，帮助开发者：
- 追踪Agent执行过程
- 诊断问题和错误
- 分析性能瓶颈
- 优化Agent行为

主要功能：
1. 执行追踪和日志
2. 中间步骤可视化
3. 性能分析
4. 错误诊断
5. 调试模式

适用场景：
- Agent开发调试
- 问题排查
- 性能优化
- 行为分析
"""

from typing import List, Dict, Any, Optional
import time
import json
from datetime import datetime
from collections import defaultdict

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler


# ============ 工具定义 ============

@tool
def search(query: str) -> str:
    """搜索工具"""
    time.sleep(0.5)  # 模拟网络延迟
    return f"关于'{query}'的搜索结果"


@tool
def calculate(expression: str) -> str:
    """计算器"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_info(topic: str) -> str:
    """获取信息"""
    time.sleep(0.3)
    info_db = {
        "Python": "高级编程语言",
        "AI": "人工智能技术",
        "LangChain": "LLM应用开发框架"
    }
    return info_db.get(topic, f"未找到关于{topic}的信息")


# ============ 自定义回调处理器 ============

class DetailedDebugCallback(BaseCallbackHandler):
    """详细调试回调"""

    def __init__(self):
        self.steps = []
        self.start_time = None
        self.llm_calls = 0
        self.tool_calls = 0

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs):
        """链开始"""
        self.start_time = time.time()
        print("\n🚀 Agent开始执行")
        print(f"输入: {inputs.get('input', '')}")
        print("="*60)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs):
        """链结束"""
        elapsed = time.time() - self.start_time
        print("\n" + "="*60)
        print(f"✅ Agent执行完成")
        print(f"⏱️  总耗时: {elapsed:.2f}秒")
        print(f"📊 LLM调用: {self.llm_calls}次")
        print(f"🔧 工具调用: {self.tool_calls}次")

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """LLM开始"""
        self.llm_calls += 1
        print(f"\n🤖 LLM调用 #{self.llm_calls}")

    def on_llm_end(self, response, **kwargs):
        """LLM结束"""
        print(f"✓ LLM响应完成")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """工具开始"""
        self.tool_calls += 1
        tool_name = serialized.get('name', 'unknown')
        print(f"\n🔧 工具调用 #{self.tool_calls}: {tool_name}")
        print(f"   输入: {input_str}")

    def on_tool_end(self, output: str, **kwargs):
        """工具结束"""
        print(f"   输出: {output}")

    def on_agent_action(self, action, **kwargs):
        """Agent行动"""
        print(f"\n💭 Agent决策:")
        print(f"   工具: {action.tool}")
        print(f"   输入: {action.tool_input}")
        print(f"   日志: {action.log[:100]}...")

    def on_agent_finish(self, finish, **kwargs):
        """Agent完成"""
        print(f"\n🎯 Agent最终答案:")
        print(f"   {finish.return_values.get('output', '')}")


class PerformanceCallback(BaseCallbackHandler):
    """性能分析回调"""

    def __init__(self):
        self.timing = defaultdict(list)
        self.current_timing = {}

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """记录LLM开始时间"""
        self.current_timing['llm'] = time.time()

    def on_llm_end(self, response, **kwargs):
        """记录LLM耗时"""
        if 'llm' in self.current_timing:
            elapsed = time.time() - self.current_timing['llm']
            self.timing['llm'].append(elapsed)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """记录工具开始时间"""
        tool_name = serialized.get('name', 'tool')
        self.current_timing[f'tool_{tool_name}'] = time.time()

    def on_tool_end(self, output: str, **kwargs):
        """记录工具耗时"""
        for key in list(self.current_timing.keys()):
            if key.startswith('tool_'):
                elapsed = time.time() - self.current_timing[key]
                self.timing[key].append(elapsed)
                del self.current_timing[key]
                break

    def get_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        report = {}
        for key, times in self.timing.items():
            if times:
                report[key] = {
                    'count': len(times),
                    'total': sum(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times)
                }
        return report


# ============ 示例函数 ============

def example_1_basic_debugging():
    """示例1: 基础调试"""
    print("\n" + "="*60)
    print("示例1: 基础调试 - verbose模式")
    print("="*60)

    print("\n💡 说明:")
    print("使用verbose=True开启基础调试模式\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [search, calculate]

    prompt = PromptTemplate.from_template(
        """回答以下问题，你可以使用工具。

工具：
{tools}

工具名称: {tool_names}

问题: {input}

思考: {agent_scratchpad}"""
    )

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 开启详细输出
        handle_parsing_errors=True
    )

    try:
        print("执行查询...")
        result = agent_executor.invoke({"input": "搜索Python，然后计算2+3"})
        print(f"\n最终结果: {result['output']}")
    except Exception as e:
        print(f"⚠️  执行出错（可能需要API Key）: {e}")


def example_2_detailed_callback():
    """示例2: 详细调试回调"""
    print("\n" + "="*60)
    print("示例2: 使用自定义调试回调")
    print("="*60)

    print("\n💡 说明:")
    print("自定义回调可以追踪每个执行步骤\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [search, get_info]

    prompt = PromptTemplate.from_template(
        """回答问题，使用必要的工具。

工具: {tools}
工具名称: {tool_names}

问题: {input}
{agent_scratchpad}"""
    )

    # 创建自定义回调
    debug_callback = DetailedDebugCallback()

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[debug_callback],  # 添加回调
        verbose=False  # 关闭默认输出
    )

    try:
        result = agent_executor.invoke({"input": "搜索LangChain并获取相关信息"})
        print(f"\n执行统计:")
        print(f"- LLM调用: {debug_callback.llm_calls}次")
        print(f"- 工具调用: {debug_callback.tool_calls}次")
    except Exception as e:
        print(f"⚠️  需要API Key: {e}")


def example_3_performance_analysis():
    """示例3: 性能分析"""
    print("\n" + "="*60)
    print("示例3: 性能分析")
    print("="*60)

    print("\n💡 说明:")
    print("分析各个组件的性能消耗\n")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [search, calculate, get_info]

    prompt = PromptTemplate.from_template(
        """使用工具回答问题。

工具: {tools}
工具名称: {tool_names}

问题: {input}
{agent_scratchpad}"""
    )

    # 创建性能回调
    perf_callback = PerformanceCallback()

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[perf_callback],
        verbose=False
    )

    try:
        print("执行测试查询...")
        agent_executor.invoke({"input": "搜索Python，获取AI信息，计算10+20"})

        # 显示性能报告
        print("\n📊 性能报告:")
        report = perf_callback.get_report()
        for component, metrics in report.items():
            print(f"\n{component}:")
            print(f"  调用次数: {metrics['count']}")
            print(f"  总耗时: {metrics['total']:.3f}秒")
            print(f"  平均耗时: {metrics['average']:.3f}秒")
            print(f"  最小/最大: {metrics['min']:.3f}s / {metrics['max']:.3f}s")
    except Exception as e:
        print(f"⚠️  需要API Key: {e}")


def example_4_error_diagnosis():
    """示例4: 错误诊断"""
    print("\n" + "="*60)
    print("示例4: 错误诊断")
    print("="*60)

    print("\n💡 说明:")
    print("捕获和分析Agent执行过程中的错误\n")

    # 创建一个会出错的工具
    @tool
    def buggy_tool(input_str: str) -> str:
        """一个有bug的工具"""
        if "error" in input_str.lower():
            raise ValueError("故意触发的错误")
        return "正常执行"

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tools = [buggy_tool, calculate]

    prompt = PromptTemplate.from_template(
        """回答问题。

工具: {tools}
工具名称: {tool_names}

问题: {input}
{agent_scratchpad}"""
    )

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,  # 自动处理错误
        max_iterations=3
    )

    # 测试正常和错误情况
    test_cases = [
        "使用buggy_tool处理'normal input'",
        "使用buggy_tool处理'trigger error'"
    ]

    for test_input in test_cases:
        print(f"\n测试: {test_input}")
        print("-" * 40)
        try:
            result = agent_executor.invoke({"input": test_input})
            print(f"结果: {result.get('output', 'N/A')}")
        except Exception as e:
            print(f"❌ 捕获到错误: {type(e).__name__}: {e}")


def example_5_step_by_step():
    """示例5: 单步调试"""
    print("\n" + "="*60)
    print("示例5: 单步调试技术")
    print("="*60)

    print("\n💡 说明:")
    print("通过设置max_iterations=1来单步执行\n")

    print("单步调试步骤:")
    print("1. 设置max_iterations=1")
    print("2. 观察当前步骤的输出")
    print("3. 分析Agent的决策")
    print("4. 逐步增加iterations继续")
    print()
    print("这种方法适合:")
    print("- 理解Agent的决策过程")
    print("- 发现逻辑问题")
    print("- 优化提示词")


def example_6_debugging_checklist():
    """示例6: 调试检查清单"""
    print("\n" + "="*60)
    print("示例6: Agent调试检查清单")
    print("="*60)

    print("\n📋 调试检查清单:\n")

    checklist = {
        "1. 基础检查": [
            "API Key配置正确",
            "依赖包版本兼容",
            "网络连接正常",
            "工具定义正确"
        ],
        "2. 输入验证": [
            "输入格式正确",
            "参数类型匹配",
            "边界条件测试",
            "异常输入处理"
        ],
        "3. 执行追踪": [
            "开启verbose模式",
            "使用调试回调",
            "记录中间步骤",
            "检查工具调用"
        ],
        "4. 性能分析": [
            "测量LLM耗时",
            "测量工具耗时",
            "分析瓶颈",
            "优化慢操作"
        ],
        "5. 错误处理": [
            "捕获所有异常",
            "记录错误日志",
            "提供降级方案",
            "友好错误消息"
        ]
    }

    for category, items in checklist.items():
        print(f"{category}:")
        for item in items:
            print(f"  □ {item}")
        print()


def example_7_common_issues():
    """示例7: 常见问题排查"""
    print("\n" + "="*60)
    print("示例7: 常见问题及解决方案")
    print("="*60)

    print("\n🔧 常见问题:\n")

    issues = {
        "问题1: Agent不调用工具": {
            "症状": "Agent直接回答，不使用工具",
            "原因": [
                "提示词不清晰",
                "工具描述不明确",
                "LLM判断不需要工具"
            ],
            "解决": [
                "明确告诉Agent必须使用工具",
                "改进工具的描述",
                "提供使用示例"
            ]
        },
        "问题2: 工具调用失败": {
            "症状": "工具执行报错",
            "原因": [
                "参数格式错误",
                "工具实现有bug",
                "依赖服务不可用"
            ],
            "解决": [
                "验证参数类型",
                "添加错误处理",
                "实现重试机制"
            ]
        },
        "问题3: 响应太慢": {
            "症状": "等待时间过长",
            "原因": [
                "工具执行慢",
                "LLM调用多",
                "网络延迟"
            ],
            "解决": [
                "优化工具性能",
                "减少迭代次数",
                "使用缓存"
            ]
        },
        "问题4: 无限循环": {
            "症状": "Agent重复相同操作",
            "原因": [
                "提示词设计问题",
                "停止条件不明确",
                "工具返回不确定"
            ],
            "解决": [
                "设置max_iterations",
                "改进停止条件",
                "检查工具输出"
            ]
        }
    }

    for issue_name, details in issues.items():
        print(f"{issue_name}:")
        print(f"  症状: {details['症状']}")
        print(f"  原因:")
        for reason in details['原因']:
            print(f"    - {reason}")
        print(f"  解决方案:")
        for solution in details['解决']:
            print(f"    - {solution}")
        print()


def example_8_optimization_tips():
    """示例8: 优化技巧"""
    print("\n" + "="*60)
    print("示例8: Agent优化技巧")
    print("="*60)

    print("\n💡 优化技巧:\n")

    print("1. 提示词优化")
    print("   - 清晰的指令")
    print("   - 明确的工具说明")
    print("   - 提供示例")
    print("   - 设置约束条件")
    print()

    print("2. 工具优化")
    print("   - 原子化设计")
    print("   - 快速执行")
    print("   - 清晰的返回值")
    print("   - 完善的错误处理")
    print()

    print("3. 性能优化")
    print("   - 使用缓存")
    print("   - 限制迭代次数")
    print("   - 异步执行")
    print("   - 批量处理")
    print()

    print("4. 成本优化")
    print("   - 使用较小的模型")
    print("   - 压缩提示词")
    print("   - 减少LLM调用")
    print("   - 缓存常见查询")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*20 + "Agent调试教程")
    print("="*60)

    # 运行示例
    example_1_basic_debugging()
    example_2_detailed_callback()
    example_3_performance_analysis()
    example_4_error_diagnosis()
    example_5_step_by_step()
    example_6_debugging_checklist()
    example_7_common_issues()
    example_8_optimization_tips()

    print("\n" + "="*60)
    print("✅ 教程完成")
    print("="*60)
    print("\n💡 关键要点:")
    print("- 使用verbose和回调追踪执行")
    print("- 分析性能找出瓶颈")
    print("- 建立完善的错误处理")
    print("- 持续优化和改进")
