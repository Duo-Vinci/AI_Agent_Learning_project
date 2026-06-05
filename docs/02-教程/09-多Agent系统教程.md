# 多 Agent 系统教程

## 一、项目概述

本项目深入讲解多 Agent 协作系统的设计与实现，从简单的顺序协作到复杂的自主团队，帮助你构建强大的 AI 协作系统。

**项目位置**：`projects/09-multi-agent/`

**学习目标**：
- 理解多 Agent 协作的核心模式
- 掌握 Agent 间的通信机制
- 学会设计任务分配和调度策略
- 理解共享记忆和上下文管理
- 掌握冲突解决和一致性保证
- 学习主流多 Agent 框架

---

## 二、多 Agent 核心概念

### 2.1 为什么需要多 Agent？

**单 Agent 的局限**：
- 能力有限，难以处理复杂多领域任务
- 缺乏专业化分工
- 没有互相审查和验证机制
- 难以并行处理任务

**多 Agent 的优势**：
- **专业化**：每个 Agent 专注特定领域
- **并行化**：同时处理多个子任务
- **鲁棒性**：互相验证，减少错误
- **可扩展**：轻松添加新能力

### 2.2 多 Agent 架构类型

```
1. 顺序协作（Sequential）
   Agent A → Agent B → Agent C → 最终输出

2. 并行协作（Parallel）
        ┌─ Agent A ─┐
   输入 ─┤─ Agent B ─┤─ 聚合 → 输出
        └─ Agent C ─┘

3. 层级协作（Hierarchical）
        Manager Agent
         ↓    ↓    ↓
      A₁   A₂   A₃  (Worker Agents)

4. 辩论协作（Debate）
   Agent A ⇄ Agent B ⇄ Agent C
      ↓       ↓       ↓
      Judge Agent → 最终决策

5. 自主协作（Autonomous）
   Agents 自主通信、分工、协调
```

---

## 三、顺序协作

### 3.1 基础顺序链

```python
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI

# 1. 定义专业化 Agent
class ResearchAgent:
    """研究员：负责信息收集"""
    def __init__(self, llm):
        self.llm = llm
    
    def research(self, topic: str) -> str:
        prompt = f"深入研究以下主题，收集关键信息：{topic}"
        return self.llm.predict(prompt)

class WriterAgent:
    """写作员：负责内容创作"""
    def __init__(self, llm):
        self.llm = llm
    
    def write(self, research_data: str) -> str:
        prompt = f"基于以下研究资料，撰写一篇文章：\n{research_data}"
        return self.llm.predict(prompt)

class EditorAgent:
    """编辑：负责审查和优化"""
    def __init__(self, llm):
        self.llm = llm
    
    def edit(self, draft: str) -> str:
        prompt = f"审查并优化以下文章：\n{draft}"
        return self.llm.predict(prompt)

# 2. 顺序执行
def sequential_workflow(topic: str):
    llm = ChatOpenAI(temperature=0.7)
    
    # 研究阶段
    researcher = ResearchAgent(llm)
    research_result = researcher.research(topic)
    print(f"✓ 研究完成\n{research_result[:200]}...\n")
    
    # 写作阶段
    writer = WriterAgent(llm)
    draft = writer.write(research_result)
    print(f"✓ 初稿完成\n{draft[:200]}...\n")
    
    # 编辑阶段
    editor = EditorAgent(llm)
    final_article = editor.edit(draft)
    print(f"✓ 最终稿完成\n{final_article}\n")
    
    return final_article

# 执行
article = sequential_workflow("AI Agent 的应用场景")
```

### 3.2 带反馈的顺序协作

```python
def sequential_with_feedback(topic: str, max_iterations: int = 3):
    """带反馈循环的顺序协作"""
    
    llm = ChatOpenAI(temperature=0.7)
    researcher = ResearchAgent(llm)
    writer = WriterAgent(llm)
    editor = EditorAgent(llm)
    
    # 初始研究
    research_result = researcher.research(topic)
    
    for iteration in range(max_iterations):
        print(f"\n--- 迭代 {iteration + 1} ---")
        
        # 写作
        draft = writer.write(research_result)
        
        # 编辑审查
        edited, feedback = editor.edit_with_feedback(draft)
        
        # 如果通过审查，完成
        if feedback.get("approved", False):
            print("✓ 审查通过，任务完成")
            return edited
        
        # 根据反馈补充研究
        print(f"需要改进: {feedback['issues']}")
        research_result += researcher.research(feedback['missing_info'])
    
    return edited
```

---

## 四、并行协作

### 4.1 基础并行执行

```python
import asyncio
from typing import List, Dict

async def parallel_analysis(text: str) -> Dict[str, str]:
    """多个 Agent 并行分析同一文本"""
    
    llm = ChatOpenAI(temperature=0)
    
    # 定义不同分析 Agent
    async def sentiment_analysis():
        prompt = f"分析以下文本的情感倾向：\n{text}"
        return await llm.apredict(prompt)
    
    async def keyword_extraction():
        prompt = f"提取以下文本的关键词：\n{text}"
        return await llm.apredict(prompt)
    
    async def summary_generation():
        prompt = f"总结以下文本：\n{text}"
        return await llm.apredict(prompt)
    
    async def entity_recognition():
        prompt = f"识别以下文本中的实体（人名、地名、机构）：\n{text}"
        return await llm.apredict(prompt)
    
    # 并行执行
    results = await asyncio.gather(
        sentiment_analysis(),
        keyword_extraction(),
        summary_generation(),
        entity_recognition()
    )
    
    return {
        "sentiment": results[0],
        "keywords": results[1],
        "summary": results[2],
        "entities": results[3]
    }

# 使用
text = "您的文本内容..."
results = asyncio.run(parallel_analysis(text))
```

### 4.2 结果聚合

```python
class AggregatorAgent:
    """聚合器：整合多个 Agent 的结果"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def aggregate(self, results: Dict[str, str]) -> str:
        """聚合多个分析结果"""
        
        prompt = f"""整合以下多个分析结果，生成综合报告：

情感分析：{results['sentiment']}

关键词：{results['keywords']}

摘要：{results['summary']}

实体识别：{results['entities']}

请生成一份结构化的综合分析报告："""
        
        return self.llm.predict(prompt)

# 完整流程
async def parallel_workflow(text: str):
    # 1. 并行分析
    analysis_results = await parallel_analysis(text)
    
    # 2. 聚合结果
    aggregator = AggregatorAgent(ChatOpenAI())
    final_report = aggregator.aggregate(analysis_results)
    
    return final_report
```

---

## 五、层级协作

### 5.1 Manager-Worker 模式

```python
from typing import List, Tuple

class ManagerAgent:
    """管理者：负责任务分解和分配"""
    
    def __init__(self, llm):
        self.llm = llm
        self.workers: List[WorkerAgent] = []
    
    def add_worker(self, worker):
        """添加工作者"""
        self.workers.append(worker)
    
    def decompose_task(self, task: str) -> List[Dict]:
        """分解任务"""
        prompt = f"""将以下任务分解为可并行执行的子任务：

任务：{task}

请输出 JSON 格式的子任务列表：
[
  {{"id": "1", "description": "子任务描述", "required_skill": "技能"}},
  ...
]

子任务列表："""
        
        response = self.llm.predict(prompt)
        subtasks = json.loads(response)
        return subtasks
    
    def assign_tasks(self, subtasks: List[Dict]) -> List[Tuple[WorkerAgent, Dict]]:
        """分配任务给合适的 Worker"""
        assignments = []
        
        for subtask in subtasks:
            # 找到最匹配的 Worker
            best_worker = self._find_best_worker(subtask['required_skill'])
            assignments.append((best_worker, subtask))
        
        return assignments
    
    def _find_best_worker(self, required_skill: str) -> 'WorkerAgent':
        """根据技能选择最佳 Worker"""
        for worker in self.workers:
            if required_skill in worker.skills:
                return worker
        return self.workers[0]  # 默认返回第一个
    
    def execute_plan(self, task: str) -> str:
        """执行完整计划"""
        # 1. 分解任务
        subtasks = self.decompose_task(task)
        
        # 2. 分配任务
        assignments = self.assign_tasks(subtasks)
        
        # 3. 执行子任务
        results = []
        for worker, subtask in assignments:
            print(f"分配给 {worker.name}: {subtask['description']}")
            result = worker.execute(subtask['description'])
            results.append({
                "subtask": subtask,
                "result": result
            })
        
        # 4. 整合结果
        final_result = self._integrate_results(results)
        return final_result
    
    def _integrate_results(self, results: List[Dict]) -> str:
        """整合所有子任务结果"""
        prompt = f"整合以下子任务的执行结果：\n{json.dumps(results, ensure_ascii=False, indent=2)}"
        return self.llm.predict(prompt)

class WorkerAgent:
    """工作者：执行具体任务"""
    
    def __init__(self, name: str, skills: List[str], llm):
        self.name = name
        self.skills = skills
        self.llm = llm
    
    def execute(self, task: str) -> str:
        """执行任务"""
        prompt = f"""你是一个专业的 {', '.join(self.skills)} 专家。
请完成以下任务：{task}

执行结果："""
        return self.llm.predict(prompt)

# 使用示例
def hierarchical_workflow():
    llm = ChatOpenAI(temperature=0)
    
    # 创建 Manager
    manager = ManagerAgent(llm)
    
    # 创建 Workers
    researcher = WorkerAgent("研究员", ["research", "analysis"], llm)
    developer = WorkerAgent("开发者", ["coding", "debugging"], llm)
    writer = WorkerAgent("写作者", ["writing", "documentation"], llm)
    
    manager.add_worker(researcher)
    manager.add_worker(developer)
    manager.add_worker(writer)
    
    # 执行任务
    task = "开发一个 AI Agent 系统并编写文档"
    result = manager.execute_plan(task)
    
    return result
```

---

## 六、辩论协作

### 6.1 多方辩论模式

```python
class DebateAgent:
    """辩论 Agent"""
    
    def __init__(self, name: str, stance: str, llm):
        self.name = name
        self.stance = stance  # 立场
        self.llm = llm
        self.history = []
    
    def argue(self, topic: str, opponent_arguments: List[str]) -> str:
        """提出论点"""
        
        context = "\n".join([
            f"对方观点 {i+1}: {arg}" 
            for i, arg in enumerate(opponent_arguments)
        ])
        
        prompt = f"""你是{self.name}，立场是：{self.stance}

辩论主题：{topic}

{context if context else "这是第一轮辩论"}

请提出你的论点和论据（200字以内）："""
        
        argument = self.llm.predict(prompt)
        self.history.append(argument)
        return argument

class JudgeAgent:
    """裁判 Agent：评估辩论并做出决策"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def evaluate(self, topic: str, arguments: Dict[str, List[str]]) -> Dict:
        """评估辩论结果"""
        
        formatted_args = []
        for agent_name, args in arguments.items():
            formatted_args.append(f"{agent_name}的论点：")
            for i, arg in enumerate(args, 1):
                formatted_args.append(f"  轮次{i}: {arg}")
        
        all_arguments = "\n".join(formatted_args)
        
        prompt = f"""作为公正的裁判，评估以下辩论：

主题：{topic}

{all_arguments}

请评估：
1. 哪一方的论据更充分？
2. 哪一方的逻辑更严密？
3. 最终判定（以 JSON 格式）：
{{
  "winner": "获胜者名称",
  "reasoning": "判定理由",
  "scores": {{"Agent1": 分数, "Agent2": 分数}}
}}

评估结果："""
        
        result = self.llm.predict(prompt)
        return json.loads(result)

def debate_workflow(topic: str, rounds: int = 3):
    """辩论工作流"""
    
    llm = ChatOpenAI(temperature=0.7)
    
    # 创建辩论双方
    agent_pro = DebateAgent(
        name="正方",
        stance="支持使用 AI Agent",
        llm=llm
    )
    
    agent_con = DebateAgent(
        name="反方",
        stance="反对过度依赖 AI Agent",
        llm=llm
    )
    
    judge = JudgeAgent(llm)
    
    # 多轮辩论
    arguments = {"正方": [], "反方": []}
    
    for round_num in range(rounds):
        print(f"\n=== 第 {round_num + 1} 轮辩论 ===\n")
        
        # 正方发言
        pro_arg = agent_pro.argue(topic, arguments["反方"])
        arguments["正方"].append(pro_arg)
        print(f"正方：{pro_arg}\n")
        
        # 反方发言
        con_arg = agent_con.argue(topic, arguments["正方"])
        arguments["反方"].append(con_arg)
        print(f"反方：{con_arg}\n")
    
    # 裁判评估
    print("\n=== 裁判评估 ===\n")
    result = judge.evaluate(topic, arguments)
    print(f"获胜者：{result['winner']}")
    print(f"理由：{result['reasoning']}")
    print(f"分数：{result['scores']}")
    
    return result

# 执行辩论
debate_workflow("是否应该在生产环境大规模使用 AI Agent")
```

---

## 七、通信机制

### 7.1 消息传递

```python
from dataclasses import dataclass
from typing import Any
from queue import Queue
from enum import Enum

class MessageType(Enum):
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    RESPONSE = "response"

@dataclass
class Message:
    """Agent 间的消息"""
    sender: str
    receiver: str
    type: MessageType
    content: Any
    timestamp: float

class MessageBus:
    """消息总线：管理 Agent 间通信"""
    
    def __init__(self):
        self.queues: Dict[str, Queue] = {}
        self.message_history: List[Message] = []
    
    def register_agent(self, agent_id: str):
        """注册 Agent"""
        self.queues[agent_id] = Queue()
    
    def send_message(self, message: Message):
        """发送消息"""
        if message.receiver in self.queues:
            self.queues[message.receiver].put(message)
            self.message_history.append(message)
        else:
            raise ValueError(f"未知的接收者：{message.receiver}")
    
    def receive_message(self, agent_id: str, timeout: float = None) -> Message:
        """接收消息"""
        return self.queues[agent_id].get(timeout=timeout)
    
    def broadcast(self, sender: str, message_type: MessageType, content: Any):
        """广播消息给所有 Agent"""
        for agent_id in self.queues.keys():
            if agent_id != sender:
                msg = Message(
                    sender=sender,
                    receiver=agent_id,
                    type=message_type,
                    content=content,
                    timestamp=time.time()
                )
                self.send_message(msg)

class CommunicatingAgent:
    """支持通信的 Agent"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, llm):
        self.agent_id = agent_id
        self.bus = message_bus
        self.llm = llm
        self.bus.register_agent(agent_id)
    
    def send_to(self, receiver: str, message_type: MessageType, content: Any):
        """发送消息给指定 Agent"""
        msg = Message(
            sender=self.agent_id,
            receiver=receiver,
            type=message_type,
            content=content,
            timestamp=time.time()
        )
        self.bus.send_message(msg)
    
    def receive(self, timeout: float = None) -> Message:
        """接收消息"""
        return self.bus.receive_message(self.agent_id, timeout)
    
    def process_message(self, message: Message):
        """处理收到的消息"""
        if message.type == MessageType.TASK:
            result = self.execute_task(message.content)
            self.send_to(
                message.sender,
                MessageType.RESULT,
                result
            )
        elif message.type == MessageType.QUERY:
            response = self.answer_query(message.content)
            self.send_to(
                message.sender,
                MessageType.RESPONSE,
                response
            )
```

### 7.2 共享记忆

```python
class SharedMemory:
    """共享记忆空间"""
    
    def __init__(self):
        self.facts: Dict[str, Any] = {}  # 事实性知识
        self.context: List[str] = []     # 对话上下文
        self.decisions: List[Dict] = []  # 决策历史
    
    def add_fact(self, key: str, value: Any, source: str):
        """添加事实"""
        self.facts[key] = {
            "value": value,
            "source": source,
            "timestamp": time.time()
        }
    
    def get_fact(self, key: str) -> Any:
        """获取事实"""
        return self.facts.get(key, {}).get("value")
    
    def add_context(self, context: str):
        """添加上下文"""
        self.context.append(context)
        # 保持最近的 N 条上下文
        if len(self.context) > 50:
            self.context = self.context[-50:]
    
    def record_decision(self, decision: Dict):
        """记录决策"""
        self.decisions.append({
            **decision,
            "timestamp": time.time()
        })
    
    def get_relevant_context(self, query: str, k: int = 5) -> List[str]:
        """获取相关上下文"""
        # 简单实现：返回最近的 k 条
        return self.context[-k:]

# 使用共享记忆的 Agent
class CollaborativeAgent:
    def __init__(self, agent_id: str, shared_memory: SharedMemory, llm):
        self.agent_id = agent_id
        self.memory = shared_memory
        self.llm = llm
    
    def execute_with_context(self, task: str):
        """使用共享上下文执行任务"""
        # 1. 获取相关上下文
        context = self.memory.get_relevant_context(task)
        
        # 2. 执行任务
        prompt = f"""上下文：
{chr(10).join(context)}

任务：{task}

结果："""
        result = self.llm.predict(prompt)
        
        # 3. 更新共享记忆
        self.memory.add_context(f"{self.agent_id}: {result}")
        
        return result
```

---

## 八、主流框架

### 8.1 AutoGen

```python
# AutoGen 示例
import autogen

# 配置
config_list = [{
    "model": "gpt-4",
    "api_key": "your-key"
}]

# 创建 Agent
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list}
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10
)

# 启动对话
user_proxy.initiate_chat(
    assistant,
    message="分析这段代码并提供优化建议"
)
```

### 8.2 CrewAI

```python
# CrewAI 示例
from crewai import Agent, Task, Crew

# 定义 Agent
researcher = Agent(
    role='研究员',
    goal='收集和分析信息',
    backstory='你是一个经验丰富的研究员',
    verbose=True
)

writer = Agent(
    role='写作者',
    goal='创作高质量内容',
    backstory='你是一个专业的内容创作者',
    verbose=True
)

# 定义任务
research_task = Task(
    description='研究 AI Agent 的最新进展',
    agent=researcher
)

write_task = Task(
    description='基于研究结果撰写文章',
    agent=writer
)

# 组建团队
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

# 执行
result = crew.kickoff()
```

---

## 九、运行步骤

```bash
# 1. 安装依赖
pip install langchain langchain-openai
pip install autogen-agentchat  # 可选
pip install crewai  # 可选

# 2. 进入项目目录
cd projects/09-multi-agent

# 3. 运行示例
python src/01-sequential-agents/workflow.py
python src/03-hierarchical-agents/manager_worker.py
python src/07-autonomous-team/self_organizing.py
```

---

## 十、最佳实践

1. **明确角色分工**：每个 Agent 有清晰的职责
2. **设计通信协议**：统一的消息格式
3. **避免循环依赖**：清晰的任务流向
4. **实现超时机制**：防止死锁
5. **记录所有交互**：便于调试和审计
6. **渐进式复杂度**：从简单开始，逐步增加 Agent

---

## 十一、相关资源

- [[知识图谱]] - 完整学习路径导航
- [[05-Agent教程]] - Agent 基础入门
- [[08-Agent架构教程]] - Agent 架构设计
- [[03-Agent设计原则]] - Agent 设计最佳实践

---

## 十二、参考资源

- [AutoGen 文档](https://microsoft.github.io/autogen/)
- [CrewAI 文档](https://docs.crewai.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)

---

**构建协作 Agent 团队，释放 AI 的集体智慧！**
