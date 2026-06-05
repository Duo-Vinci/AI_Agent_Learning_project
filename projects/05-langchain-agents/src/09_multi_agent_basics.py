"""
多Agent协作基础

多Agent系统是指多个Agent协同工作来完成复杂任务的系统。
通过合理的协作模式，可以让不同的Agent发挥各自的专长，
实现比单个Agent更强大的功能。

协作模式：
1. 顺序协作：Agent按顺序依次处理
2. 并行协作：多个Agent同时工作
3. 层级协作：管理者分配任务给工作者
4. 辩论协作：多个Agent讨论得出最佳方案

适用场景：
- 复杂的多步骤任务
- 需要多个专业领域知识
- 任务可以并行处理
- 需要多角度分析
"""

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage


# ============ 工具定义 ============

@tool
def research_tool(topic: str) -> str:
    """研究工具：收集信息"""
    knowledge_base = {
        "Python": "Python是一种广泛使用的高级编程语言，以简洁的语法著称。",
        "AI": "人工智能是计算机科学的一个分支，致力于创建智能机器。",
        "区块链": "区块链是一种分布式账本技术，具有去中心化、透明等特点。"
    }
    return knowledge_base.get(topic, f"关于{topic}的基本信息")


@tool
def analyze_tool(data: str) -> str:
    """分析工具：分析数据"""
    return f"分析结果：{data} 的关键要点已提取"


@tool
def write_tool(content: str) -> str:
    """写作工具：生成文本"""
    return f"已生成关于'{content}'的文档"


# ============ Agent类定义 ============

class SimpleAgent:
    """简单的Agent类"""

    def __init__(self, name: str, role: str, llm: Optional[ChatOpenAI] = None):
        """
        初始化Agent

        Args:
            name: Agent名称
            role: Agent角色描述
            llm: 语言模型
        """
        self.name = name
        self.role = role
        self.llm = llm or ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    def execute(self, task: str) -> str:
        """
        执行任务

        Args:
            task: 任务描述

        Returns:
            执行结果
        """
        try:
            messages = [
                SystemMessage(content=f"你是{self.name}，职责是{self.role}"),
                HumanMessage(content=task)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"执行失败: {str(e)}"


# ============ 协作模式实现 ============

class SequentialCollaboration:
    """顺序协作模式"""

    def __init__(self, agents: List[SimpleAgent]):
        """
        初始化顺序协作

        Args:
            agents: Agent列表（按执行顺序）
        """
        self.agents = agents

    def execute(self, initial_task: str) -> Dict[str, Any]:
        """
        执行顺序协作

        Args:
            initial_task: 初始任务

        Returns:
            执行结果
        """
        print(f"\n🔄 开始顺序协作")
        print(f"初始任务: {initial_task}\n")

        results = []
        current_input = initial_task

        for i, agent in enumerate(self.agents, 1):
            print(f"步骤 {i}/{len(self.agents)}: {agent.name}")
            print(f"  角色: {agent.role}")
            print(f"  输入: {current_input[:100]}...")

            result = agent.execute(current_input)
            results.append({
                'agent': agent.name,
                'role': agent.role,
                'output': result
            })

            print(f"  输出: {result[:100]}...")
            print()

            # 下一个Agent的输入是上一个的输出
            current_input = result

        return {
            'final_output': current_input,
            'steps': results
        }


class ParallelCollaboration:
    """并行协作模式"""

    def __init__(self, agents: List[SimpleAgent]):
        """
        初始化并行协作

        Args:
            agents: Agent列表（将并行执行）
        """
        self.agents = agents

    async def execute_async(self, task: str) -> Dict[str, Any]:
        """
        异步执行并行协作

        Args:
            task: 共同任务

        Returns:
            所有Agent的执行结果
        """
        print(f"\n⚡ 开始并行协作")
        print(f"任务: {task}\n")

        # 为每个Agent创建任务
        tasks = []
        for agent in self.agents:
            print(f"启动 {agent.name} ({agent.role})")
            # 模拟异步执行
            task_coro = asyncio.to_thread(agent.execute, task)
            tasks.append(task_coro)

        # 等待所有Agent完成
        results = await asyncio.gather(*tasks)

        # 整理结果
        agent_results = []
        for agent, result in zip(self.agents, results):
            agent_results.append({
                'agent': agent.name,
                'role': agent.role,
                'output': result
            })
            print(f"✓ {agent.name} 完成")

        return {
            'results': agent_results,
            'summary': self._summarize_results(agent_results)
        }

    def _summarize_results(self, results: List[Dict]) -> str:
        """汇总结果"""
        summary = "各Agent的观点:\n"
        for r in results:
            summary += f"- {r['agent']}: {r['output'][:50]}...\n"
        return summary


class HierarchicalCollaboration:
    """层级协作模式"""

    def __init__(self, manager: SimpleAgent, workers: List[SimpleAgent]):
        """
        初始化层级协作

        Args:
            manager: 管理者Agent
            workers: 工作者Agent列表
        """
        self.manager = manager
        self.workers = workers

    def execute(self, task: str) -> Dict[str, Any]:
        """
        执行层级协作

        Args:
            task: 总任务

        Returns:
            执行结果
        """
        print(f"\n👔 开始层级协作")
        print(f"总任务: {task}\n")

        # 1. 管理者分解任务
        print(f"管理者 {self.manager.name} 正在分解任务...")
        decomposition_prompt = f"""
        作为项目管理者，请将以下任务分解为{len(self.workers)}个子任务：
        {task}

        为每个子任务提供清晰的描述。
        """
        subtasks_text = self.manager.execute(decomposition_prompt)
        print(f"  任务分解完成\n")

        # 2. 分配给工作者
        worker_results = []
        for i, worker in enumerate(self.workers, 1):
            subtask = f"子任务{i}: {subtasks_text}"
            print(f"工作者 {worker.name} 正在处理子任务{i}...")

            result = worker.execute(subtask)
            worker_results.append({
                'worker': worker.name,
                'subtask': i,
                'output': result
            })
            print(f"  ✓ 完成\n")

        # 3. 管理者整合结果
        print(f"管理者 {self.manager.name} 正在整合结果...")
        integration_prompt = f"""
        作为项目管理者，整合以下工作成果：
        {[r['output'] for r in worker_results]}

        提供最终的完整报告。
        """
        final_result = self.manager.execute(integration_prompt)

        return {
            'decomposition': subtasks_text,
            'worker_results': worker_results,
            'final_report': final_result
        }


# ============ 示例函数 ============

def example_1_sequential():
    """示例1: 顺序协作"""
    print("\n" + "="*60)
    print("示例1: 顺序协作模式")
    print("="*60)

    print("\n💡 说明:")
    print("顺序协作适合有明确步骤的任务")
    print("每个Agent的输出作为下一个的输入\n")

    try:
        # 创建Agent团队
        agents = [
            SimpleAgent("研究员", "收集和整理信息"),
            SimpleAgent("分析师", "分析数据并提取关键点"),
            SimpleAgent("作家", "撰写清晰的报告")
        ]

        # 创建协作
        collaboration = SequentialCollaboration(agents)

        # 执行任务
        result = collaboration.execute("写一篇关于Python的简短介绍")

        print("="*60)
        print("最终输出:")
        print(result['final_output'])

    except Exception as e:
        print(f"⚠️  需要API Key: {e}")


def example_2_parallel():
    """示例2: 并行协作"""
    print("\n" + "="*60)
    print("示例2: 并行协作模式")
    print("="*60)

    print("\n💡 说明:")
    print("并行协作让多个Agent同时处理同一任务")
    print("从不同角度提供见解\n")

    try:
        # 创建不同专业的Agent
        agents = [
            SimpleAgent("技术专家", "从技术角度分析"),
            SimpleAgent("商业顾问", "从商业角度分析"),
            SimpleAgent("用户体验师", "从用户体验角度分析")
        ]

        # 创建并行协作
        collaboration = ParallelCollaboration(agents)

        # 异步执行
        task = "评估开发一个新的移动应用的可行性"
        result = asyncio.run(collaboration.execute_async(task))

        print("\n" + "="*60)
        print("汇总结果:")
        print(result['summary'])

    except Exception as e:
        print(f"⚠️  需要API Key: {e}")


def example_3_hierarchical():
    """示例3: 层级协作"""
    print("\n" + "="*60)
    print("示例3: 层级协作模式")
    print("="*60)

    print("\n💡 说明:")
    print("层级协作由管理者分配任务")
    print("工作者完成后管理者整合结果\n")

    try:
        # 创建管理者和工作者
        manager = SimpleAgent("项目经理", "分解任务和整合结果")
        workers = [
            SimpleAgent("后端开发", "负责后端开发"),
            SimpleAgent("前端开发", "负责前端开发"),
            SimpleAgent("测试工程师", "负责测试")
        ]

        # 创建层级协作
        collaboration = HierarchicalCollaboration(manager, workers)

        # 执行任务
        result = collaboration.execute("开发一个用户登录功能")

        print("="*60)
        print("最终报告:")
        print(result['final_report'][:200] + "...")

    except Exception as e:
        print(f"⚠️  需要API Key: {e}")


def example_4_communication():
    """示例4: Agent间通信"""
    print("\n" + "="*60)
    print("示例4: Agent间通信机制")
    print("="*60)

    print("\n💡 说明:")
    print("Agent之间需要有效的通信机制\n")

    print("常见通信方式:")
    print("1. 直接传递（Direct Passing）")
    print("   - 简单直接")
    print("   - 适合顺序协作")
    print()
    print("2. 消息队列（Message Queue）")
    print("   - 异步通信")
    print("   - 适合并行协作")
    print()
    print("3. 共享状态（Shared State）")
    print("   - 共享数据存储")
    print("   - 需要同步机制")
    print()
    print("4. 事件驱动（Event-Driven）")
    print("   - 发布-订阅模式")
    print("   - 灵活性高")


def example_5_task_allocation():
    """示例5: 任务分配策略"""
    print("\n" + "="*60)
    print("示例5: 任务分配策略")
    print("="*60)

    print("\n💡 说明:")
    print("如何有效地分配任务给不同的Agent\n")

    print("分配策略:")
    print()
    print("1. 能力匹配")
    print("   - 根据Agent专长分配")
    print("   - 示例：技术问题给技术专家")
    print()
    print("2. 负载均衡")
    print("   - 平均分配工作量")
    print("   - 避免某个Agent过载")
    print()
    print("3. 优先级排序")
    print("   - 重要任务优先处理")
    print("   - 考虑任务依赖关系")
    print()
    print("4. 动态调整")
    print("   - 根据执行情况调整")
    print("   - 失败任务重新分配")


def example_6_result_aggregation():
    """示例6: 结果聚合"""
    print("\n" + "="*60)
    print("示例6: 结果聚合方法")
    print("="*60)

    print("\n💡 说明:")
    print("如何整合多个Agent的输出\n")

    print("聚合方法:")
    print()
    print("1. 投票机制")
    print("   - 多数决定")
    print("   - 适合分类任务")
    print()
    print("2. 加权平均")
    print("   - 根据可信度加权")
    print("   - 适合数值结果")
    print()
    print("3. 串联组合")
    print("   - 依次使用各Agent结果")
    print("   - 适合流程化任务")
    print()
    print("4. LLM整合")
    print("   - 使用LLM总结综合")
    print("   - 灵活但成本高")


def example_7_best_practices():
    """示例7: 最佳实践"""
    print("\n" + "="*60)
    print("示例7: 多Agent系统最佳实践")
    print("="*60)

    print("\n📚 最佳实践:\n")

    print("1. 设计原则")
    print("   - 单一职责：每个Agent专注一件事")
    print("   - 松耦合：Agent独立可测试")
    print("   - 明确接口：清晰的输入输出")
    print()

    print("2. 通信优化")
    print("   - 使用标准化消息格式")
    print("   - 实现重试机制")
    print("   - 记录通信日志")
    print()

    print("3. 错误处理")
    print("   - 单个Agent失败不影响整体")
    print("   - 实现降级方案")
    print("   - 超时保护")
    print()

    print("4. 性能优化")
    print("   - 合理使用并行")
    print("   - 避免不必要的通信")
    print("   - 缓存中间结果")
    print()

    print("5. 监控和调试")
    print("   - 追踪Agent执行状态")
    print("   - 记录详细日志")
    print("   - 性能指标监控")


def example_8_use_cases():
    """示例8: 应用场景"""
    print("\n" + "="*60)
    print("示例8: 多Agent系统应用场景")
    print("="*60)

    print("\n✅ 适合使用多Agent的场景:\n")

    print("1. 内容创作")
    print("   - 研究 → 撰写 → 审核 → 发布")
    print("   - 每个步骤由专门的Agent负责")
    print()

    print("2. 数据分析")
    print("   - 收集 → 清洗 → 分析 → 可视化")
    print("   - 并行处理大量数据")
    print()

    print("3. 客户服务")
    print("   - 意图识别 → 知识检索 → 回答生成")
    print("   - 专业问题转给专家Agent")
    print()

    print("4. 软件开发")
    print("   - 需求分析 → 设计 → 编码 → 测试")
    print("   - 不同专业Agent协作")
    print()

    print("5. 决策支持")
    print("   - 多个专家Agent提供意见")
    print("   - 管理者Agent做最终决策")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*16 + "多Agent协作基础教程")
    print("="*60)

    # 运行示例
    example_1_sequential()
    example_2_parallel()
    example_3_hierarchical()
    example_4_communication()
    example_5_task_allocation()
    example_6_result_aggregation()
    example_7_best_practices()
    example_8_use_cases()

    print("\n" + "="*60)
    print("✅ 教程完成")
    print("="*60)
    print("\n💡 关键要点:")
    print("- 选择合适的协作模式")
    print("- 设计清晰的通信机制")
    print("- 实现有效的任务分配")
    print("- 整合多个Agent的结果")
    print("\n📚 进阶学习:")
    print("- 查看项目09-multi-agent了解更高级的协作模式")
    print("- 学习AutoGen和CrewAI等多Agent框架")
