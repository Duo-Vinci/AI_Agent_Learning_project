"""
LangChain Agents - 快速入门

本脚本演示如何快速开始使用LangChain构建Agent系统：
1. 什么是Agent
2. 创建简单Agent
3. Agent使用工具
4. Agent推理过程

运行方式：
    python quickstart.py
"""

import os
from typing import List
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 理解Agent ====================

def example_1_what_is_agent():
    """示例1: 什么是Agent"""
    print_section("示例1: 什么是Agent")

    print("""
Agent（代理）是一个能够自主决策和行动的AI系统。

关键特点：
1. 自主性：能够自己决定下一步做什么
2. 工具使用：可以调用各种工具来完成任务
3. 推理能力：通过思考来选择合适的工具和行动
4. 循环执行：观察-思考-行动的循环过程

Agent vs 普通LLM调用：
- 普通LLM：你问什么，它答什么
- Agent：根据任务自主规划，选择工具，执行步骤

典型流程：
1. 接收任务
2. 思考：我需要什么信息？
3. 选择工具并执行
4. 观察结果
5. 继续思考或给出最终答案
    """)


# ==================== 示例2: 创建简单Agent ====================

def example_2_simple_agent():
    """示例2: 创建第一个Agent"""
    print_section("示例2: 创建第一个Agent")

    try:
        load_dotenv()

        # 1. 创建工具
        @tool
        def get_current_time() -> str:
            """获取当前时间。当用户询问现在几点时使用此工具。"""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        @tool
        def calculate(expression: str) -> str:
            """
            计算数学表达式。支持基本运算符: +, -, *, /, **
            示例: "2 + 3 * 4" 或 "(10 + 5) / 3"
            """
            try:
                result = eval(expression, {"__builtins__": {}}, {})
                return str(result)
            except Exception as e:
                return f"计算错误: {str(e)}"

        tools = [get_current_time, calculate]

        # 2. 创建LLM
        llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0
        )

        # 3. 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个有用的助手，可以使用工具来回答问题。"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 4. 创建Agent
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5
        )

        # 5. 测试Agent
        print("Agent已创建，可用工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        print("\n开始测试...\n")

        # 测试问题
        questions = [
            "现在几点了？",
            "计算 15 * 8 + 12",
            "计算 (100 + 50) / 3 的结果"
        ]

        for question in questions:
            print(f"\n{'='*60}")
            print(f"问题: {question}")
            print('='*60)
            try:
                result = agent_executor.invoke({"input": question})
                print(f"\n最终答案: {result['output']}")
            except Exception as e:
                print(f"错误: {str(e)}")

    except Exception as e:
        print(f"错误: {str(e)}")
        print("提示: 请确保已配置API密钥")


# ==================== 示例3: Agent推理过程 ====================

def example_3_agent_reasoning():
    """示例3: 观察Agent推理过程"""
    print_section("示例3: Agent推理过程")

    print("""
Agent的推理过程（ReAct模式）：

步骤1 - 思考(Thought):
  "用户问现在几点，我需要使用get_current_time工具"

步骤2 - 行动(Action):
  调用工具: get_current_time()

步骤3 - 观察(Observation):
  工具返回: "2024-06-05 14:30:00"

步骤4 - 思考(Thought):
  "我已经得到了时间信息，可以回答用户了"

步骤5 - 最终答案(Final Answer):
  "现在是2024年6月5日下午2点30分"

这个循环会持续进行，直到Agent认为可以给出最终答案。
    """)


# ==================== 示例4: 多工具Agent ====================

def example_4_multi_tool_agent():
    """示例4: 使用多个工具的Agent"""
    print_section("示例4: 多工具Agent")

    try:
        load_dotenv()

        # 创建多个工具
        @tool
        def search_knowledge(query: str) -> str:
            """
            搜索知识库。当需要查找特定信息时使用。
            """
            knowledge = {
                "python": "Python是一种高级编程语言，由Guido van Rossum创建。",
                "langchain": "LangChain是一个用于开发AI应用的框架。",
                "ai": "人工智能是计算机科学的一个分支。"
            }
            query_lower = query.lower()
            for key, value in knowledge.items():
                if key in query_lower:
                    return value
            return "未找到相关信息"

        @tool
        def calculate(expression: str) -> str:
            """计算数学表达式"""
            try:
                return str(eval(expression, {"__builtins__": {}}, {}))
            except:
                return "计算错误"

        @tool
        def count_words(text: str) -> int:
            """统计文本中的单词数量"""
            return len(text.split())

        tools = [search_knowledge, calculate, count_words]

        # 创建Agent
        llm = ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个智能助手，可以搜索知识、计算数学、统计文字。根据问题选择合适的工具。"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )

        # 测试复杂任务
        questions = [
            "Python是什么？",
            "计算 50 * 2 + 10",
            "统计'Hello World from LangChain'有多少个单词"
        ]

        print("多工具Agent测试:\n")
        for question in questions:
            print(f"\n{'='*60}")
            print(f"问题: {question}")
            print('='*60)
            try:
                result = agent_executor.invoke({"input": question})
                print(f"\n答案: {result['output']}")
            except Exception as e:
                print(f"错误: {str(e)}")

    except Exception as e:
        print(f"错误: {str(e)}")


# ==================== 示例5: Agent最佳实践 ====================

def example_5_best_practices():
    """示例5: Agent最佳实践"""
    print_section("示例5: Agent最佳实践")

    print("""
构建高效Agent的最佳实践：

1. 工具设计
   - 清晰的工具描述（告诉Agent何时使用）
   - 合理的工具粒度（不要太大也不要太小）
   - 完善的错误处理

2. 提示工程
   - 明确Agent的角色和能力
   - 提供工具使用示例
   - 设置清晰的任务目标

3. 控制机制
   - 设置最大迭代次数（避免无限循环）
   - 添加超时控制
   - 记录Agent的推理过程

4. 测试与优化
   - 测试各种边界情况
   - 分析Agent的决策过程
   - 优化工具选择逻辑

5. 安全考虑
   - 验证工具输入
   - 限制敏感操作
   - 监控Agent行为

常见陷阱：
- 工具描述不清晰，导致Agent选错工具
- 没有设置迭代上限，导致死循环
- 工具返回值格式不统一，难以解析
- 缺少错误处理，一个错误导致整个流程中断
    """)


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain Agents - 快速入门")
    print("="*70)
    print("\n本脚本展示Agent系统的快速入门示例\n")

    try:
        # 示例1: 理解Agent
        example_1_what_is_agent()

        # 示例2: 简单Agent
        example_2_simple_agent()

        # 示例3: 推理过程
        example_3_agent_reasoning()

        # 示例4: 多工具Agent
        example_4_multi_tool_agent()

        # 示例5: 最佳实践
        example_5_best_practices()

        print("\n" + "="*70)
        print("  快速入门完成！")
        print("="*70)
        print("\n下一步:")
        print("  - 学习不同类型的Agent（ReAct, Function Calling等）")
        print("  - 探索Agent记忆管理")
        print("  - 构建多Agent系统")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
