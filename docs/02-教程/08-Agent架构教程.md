# Agent 架构教程

## 一、项目概述

本项目深入讲解 AI Agent 的架构设计，从基础概念到高级实现，帮助你构建能够自主思考和行动的智能体。

**项目位置**：`projects/08-agent-architecture/`

**学习目标**：
- 理解 Agent 的核心组件和工作原理
- 掌握 ReAct 模式的实现
- 学会设计和管理 Agent 记忆系统
- 理解任务规划和执行策略
- 掌握工具调用和函数调用
- 学习 Agent 的调试和评估方法

---

## 二、Agent 核心概念

### 2.1 什么是 Agent？

Agent（智能体）是能够感知环境、做出决策并采取行动的 AI 系统。

**核心特征**：
- **自主性**：能够独立做出决策
- **目标导向**：为达成目标而行动
- **适应性**：根据环境反馈调整策略
- **工具使用**：能够调用外部工具完成任务

### 2.2 Agent 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                      Agent 核心                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  推理    │  │  记忆    │  │  工具    │  │ 规划   │ │
│  │ Reasoning│  │  Memory  │  │  Tools   │  │Planning│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│       ↓              ↓              ↓            ↓      │
│  ┌──────────────────────────────────────────────────┐  │
│  │           大语言模型 (LLM Core)                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ↑                                        ↓
    [ 输入/观察 ]                            [ 输出/行动 ]
```

### 2.3 Agent vs LLM

| 特性 | 纯 LLM | Agent |
|------|--------|-------|
| 能力 | 文本生成 | 任务执行 |
| 工具使用 | 无 | 有 |
| 记忆 | 仅对话历史 | 长期记忆 |
| 规划 | 无 | 有 |
| 自主性 | 低 | 高 |

---

## 三、推理模式

### 3.1 ReAct 模式（Reasoning + Acting）

ReAct 是最常用的 Agent 模式，循环执行"思考 → 行动 → 观察"：

```
循环：
  1. Thought（思考）：分析当前状态，决定下一步
  2. Action（行动）：选择并执行一个工具
  3. Observation（观察）：获取工具执行结果
  直到任务完成或达到最大步数
```

**代码实现**：

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain import hub

# 1. 定义工具
def search_weather(location: str) -> str:
    """查询天气信息"""
    return f"{location}的天气：晴天，25度"

def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        return str(eval(expression))
    except:
        return "计算错误"

tools = [
    Tool(
        name="Weather",
        func=search_weather,
        description="查询指定地点的天气信息。输入：地点名称"
    ),
    Tool(
        name="Calculator",
        func=calculate,
        description="执行数学计算。输入：数学表达式"
    )
]

# 2. 创建 LLM
llm = ChatOpenAI(temperature=0)

# 3. 使用 ReAct Prompt
prompt = hub.pull("hwchase17/react")

# 4. 创建 Agent
agent = create_react_agent(llm, tools, prompt)

# 5. 创建执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,  # 最大迭代次数
    handle_parsing_errors=True  # 处理解析错误
)

# 6. 执行任务
result = agent_executor.invoke({
    "input": "北京的天气如何？如果气温是25度，华氏度是多少？"
})
```

**执行流程示例**：

```
> Entering new AgentExecutor chain...

Thought: 我需要先查询北京的天气，然后转换温度单位
Action: Weather
Action Input: 北京
Observation: 北京的天气：晴天，25度

Thought: 现在我需要将25摄氏度转换为华氏度，公式是 F = C * 9/5 + 32
Action: Calculator
Action Input: 25 * 9 / 5 + 32
Observation: 77.0

Thought: 我现在知道最终答案了
Final Answer: 北京今天是晴天，气温25摄氏度（77华氏度）

> Finished chain.
```

### 3.2 Plan-and-Execute 模式

先规划整体任务，再逐步执行：

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 1. 规划阶段
planning_prompt = PromptTemplate(
    input_variables=["objective"],
    template="""将以下目标分解为具体的执行步骤：

目标：{objective}

请输出结构化的任务列表：
1. [步骤1]
2. [步骤2]
...

任务列表："""
)

planning_chain = LLMChain(llm=llm, prompt=planning_prompt)

# 2. 执行阶段
def execute_plan(plan: str, tools: list):
    """按计划逐步执行"""
    steps = parse_plan(plan)
    results = []
    
    for step in steps:
        result = execute_step(step, tools)
        results.append(result)
        
        # 根据结果调整后续计划
        if should_replan(result):
            new_plan = replan(step, result)
            steps = parse_plan(new_plan)
    
    return results
```

### 3.3 自我反思模式

Agent 评估自己的输出并改进：

```python
reflection_prompt = """你刚才的回答：
{previous_answer}

请评估这个答案：
1. 是否完整回答了问题？
2. 是否有错误或遗漏？
3. 如何改进？

评估和改进建议："""

# 循环：生成 → 反思 → 改进 → 生成
for iteration in range(max_reflections):
    answer = agent.generate_answer(question)
    reflection = agent.reflect(answer)
    
    if reflection.is_satisfactory():
        break
    
    question = f"{question}\n\n改进要求：{reflection.improvements}"
```

---

## 四、记忆系统

### 4.1 记忆类型

```python
from langchain.memory import (
    ConversationBufferMemory,          # 完整对话历史
    ConversationBufferWindowMemory,    # 窗口记忆（最近N轮）
    ConversationSummaryMemory,         # 摘要记忆
    ConversationKGMemory,              # 知识图谱记忆
    VectorStoreRetrieverMemory,        # 向量检索记忆
)

# 1. 窗口记忆（短期）
memory = ConversationBufferWindowMemory(
    k=5,  # 保留最近5轮对话
    memory_key="chat_history",
    return_messages=True
)

# 2. 摘要记忆（压缩历史）
memory = ConversationSummaryMemory(
    llm=llm,
    memory_key="history",
    return_messages=True
)

# 3. 向量记忆（长期）
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts([], embeddings)

memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    memory_key="relevant_context"
)
```

### 4.2 组合记忆

结合多种记忆类型：

```python
from langchain.memory import CombinedMemory

# 短期记忆 + 长期记忆
combined_memory = CombinedMemory(
    memories=[
        ConversationBufferWindowMemory(k=5),  # 最近对话
        VectorStoreRetrieverMemory(retriever=retriever)  # 历史相关内容
    ]
)

agent = create_agent(
    llm=llm,
    tools=tools,
    memory=combined_memory
)
```

### 4.3 自定义记忆系统

```python
from langchain.schema import BaseMemory
from typing import Dict, List, Any

class CustomMemory(BaseMemory):
    """自定义记忆系统"""
    
    short_term: List[Dict] = []  # 短期记忆
    long_term: Dict[str, Any] = {}  # 长期记忆
    semantic_memory: FAISS = None  # 语义记忆
    
    @property
    def memory_variables(self) -> List[str]:
        return ["history", "relevant_facts"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """加载相关记忆"""
        # 1. 获取短期记忆
        recent_history = self.short_term[-5:]
        
        # 2. 从语义记忆中检索相关信息
        query = inputs.get("input", "")
        relevant_facts = self.semantic_memory.similarity_search(query, k=3)
        
        return {
            "history": recent_history,
            "relevant_facts": relevant_facts
        }
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]):
        """保存上下文到记忆"""
        # 保存到短期记忆
        self.short_term.append({
            "input": inputs["input"],
            "output": outputs["output"],
            "timestamp": datetime.now()
        })
        
        # 提取重要信息到长期记忆
        if self._is_important(outputs["output"]):
            key = self._extract_key(inputs["input"])
            self.long_term[key] = outputs["output"]
        
        # 添加到语义记忆
        self.semantic_memory.add_texts([outputs["output"]])
    
    def clear(self):
        """清空记忆"""
        self.short_term = []
```

---

## 五、工具系统

### 5.1 定义工具

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# 方法1：使用 @tool 装饰器
from langchain.tools import tool

@tool
def search_database(query: str) -> str:
    """在数据库中搜索信息"""
    # 实现搜索逻辑
    return f"搜索结果：{query}"

# 方法2：使用 Pydantic 定义参数
class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    limit: int = Field(default=10, description="返回结果数量")

def search_function(query: str, limit: int = 10) -> str:
    """执行搜索"""
    return f"找到{limit}条关于'{query}'的结果"

search_tool = StructuredTool.from_function(
    func=search_function,
    name="Search",
    description="搜索相关信息",
    args_schema=SearchInput
)
```

### 5.2 工具类型

```python
# 1. 搜索工具
from langchain.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()

# 2. Python REPL（代码执行）
from langchain.tools import PythonREPLTool
python_repl = PythonREPLTool()

# 3. Shell 命令
from langchain.tools import ShellTool
shell = ShellTool()

# 4. API 调用
from langchain.tools import APIChain
api_chain = APIChain.from_llm_and_api_docs(
    llm=llm,
    api_docs="API文档内容",
    verbose=True
)

# 5. 数据库查询
from langchain.tools import QuerySQLDataBaseTool
from langchain.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///example.db")
db_tool = QuerySQLDataBaseTool(db=db)
```

### 5.3 工具选择策略

```python
# 根据任务自动选择工具
def select_tools(task: str, available_tools: List[Tool]) -> List[Tool]:
    """智能工具选择"""
    
    tool_selection_prompt = f"""
    任务：{task}
    
    可用工具：
    {format_tools(available_tools)}
    
    请选择完成任务所需的工具（返回工具名称列表）：
    """
    
    selected_names = llm.predict(tool_selection_prompt)
    selected_tools = [t for t in available_tools if t.name in selected_names]
    
    return selected_tools
```

---

## 六、任务规划

### 6.1 任务分解

```python
def decompose_task(objective: str) -> List[str]:
    """将复杂任务分解为子任务"""
    
    prompt = f"""将以下目标分解为可执行的子任务：

目标：{objective}

要求：
1. 每个子任务要具体、可执行
2. 子任务之间要有逻辑顺序
3. 标注依赖关系

子任务列表："""

    response = llm.predict(prompt)
    subtasks = parse_tasks(response)
    
    return subtasks

# 示例输出
objective = "分析公司上季度销售数据并生成报告"
subtasks = [
    "从数据库获取上季度销售数据",
    "清洗和预处理数据",
    "计算关键指标（总销售额、增长率等）",
    "生成可视化图表",
    "撰写分析报告",
    "导出为 PDF"
]
```

### 6.2 依赖管理

```python
from typing import Dict, List, Set

class TaskGraph:
    """任务依赖图"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, Set[str]] = {}
    
    def add_task(self, task_id: str, task: Task, depends_on: List[str] = None):
        """添加任务"""
        self.tasks[task_id] = task
        self.dependencies[task_id] = set(depends_on or [])
    
    def get_ready_tasks(self, completed: Set[str]) -> List[str]:
        """获取可以执行的任务（依赖已满足）"""
        ready = []
        for task_id, deps in self.dependencies.items():
            if task_id not in completed and deps.issubset(completed):
                ready.append(task_id)
        return ready
    
    def execute_plan(self):
        """按依赖顺序执行任务"""
        completed = set()
        
        while len(completed) < len(self.tasks):
            ready_tasks = self.get_ready_tasks(completed)
            
            if not ready_tasks:
                raise Exception("存在循环依赖或无法完成的任务")
            
            for task_id in ready_tasks:
                result = self.tasks[task_id].execute()
                completed.add(task_id)
                print(f"✓ 完成任务：{task_id}")
```

---

## 七、Agent 调试

### 7.1 日志和追踪

```python
import logging
from langchain.callbacks import StdOutCallbackHandler

# 1. 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 2. 使用回调追踪执行
from langchain.callbacks import BaseCallbackHandler

class DebugCallbackHandler(BaseCallbackHandler):
    """调试回调处理器"""
    
    def on_agent_action(self, action, **kwargs):
        print(f"\n[Agent Action]")
        print(f"  Tool: {action.tool}")
        print(f"  Input: {action.tool_input}")
    
    def on_tool_end(self, output, **kwargs):
        print(f"[Tool Output]")
        print(f"  Result: {output[:200]}...")
    
    def on_agent_finish(self, finish, **kwargs):
        print(f"\n[Agent Finish]")
        print(f"  Output: {finish.return_values}")

# 使用回调
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[DebugCallbackHandler()],
    verbose=True
)
```

### 7.2 中间结果检查

```python
# 保存中间步骤
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    return_intermediate_steps=True
)

result = agent_executor.invoke({"input": "任务描述"})

# 查看执行步骤
for step in result["intermediate_steps"]:
    action, observation = step
    print(f"动作: {action.tool} - {action.tool_input}")
    print(f"结果: {observation}\n")
```

### 7.3 常见问题诊断

```python
# 1. 工具调用失败
# 原因：工具描述不清晰、参数格式错误
# 解决：优化工具的 description，使用 args_schema

# 2. 无限循环
# 原因：Agent 无法判断任务完成
# 解决：设置 max_iterations，优化停止条件

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=10,  # 限制最大迭代
    early_stopping_method="generate"  # 提前停止策略
)

# 3. 解析错误
# 原因：LLM 输出格式不符合预期
# 解决：使用 handle_parsing_errors

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,  # 自动处理解析错误
    # 或自定义错误处理
    handle_parsing_errors="检查你的输出格式，必须包含 Action 和 Action Input"
)
```

---

## 八、Agent 评估

### 8.1 评估指标

```python
from typing import List, Dict

def evaluate_agent(
    agent: AgentExecutor,
    test_cases: List[Dict[str, str]]
) -> Dict[str, float]:
    """评估 Agent 性能"""
    
    metrics = {
        "success_rate": 0,      # 成功率
        "avg_steps": 0,         # 平均步数
        "avg_tokens": 0,        # 平均 Token 消耗
        "avg_time": 0,          # 平均耗时
    }
    
    results = []
    
    for case in test_cases:
        start_time = time.time()
        
        try:
            result = agent.invoke(case["input"])
            
            # 检查答案是否正确
            is_correct = check_answer(
                result["output"],
                case["expected_output"]
            )
            
            results.append({
                "success": is_correct,
                "steps": len(result.get("intermediate_steps", [])),
                "time": time.time() - start_time
            })
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    
    # 计算指标
    metrics["success_rate"] = sum(r["success"] for r in results) / len(results)
    metrics["avg_steps"] = sum(r.get("steps", 0) for r in results) / len(results)
    metrics["avg_time"] = sum(r.get("time", 0) for r in results) / len(results)
    
    return metrics
```

### 8.2 测试用例设计

```python
test_cases = [
    {
        "input": "北京今天天气如何？",
        "expected_output": "包含天气信息",
        "required_tools": ["Weather"],
        "max_steps": 2
    },
    {
        "input": "计算 123 + 456，然后查询结果对应的质数",
        "expected_output": "579不是质数",
        "required_tools": ["Calculator", "Math"],
        "max_steps": 4
    }
]
```

---

## 九、运行步骤

```bash
# 1. 安装依赖
pip install langchain langchain-openai
pip install langchainhub  # 用于加载 Prompt 模板

# 2. 进入项目目录
cd projects/08-agent-architecture

# 3. 配置环境
copy .env.example .env

# 4. 运行示例
python src/01-react-agent/basic_react.py
python src/03-memory-systems/custom_memory.py
python src/06-custom-agent/my_agent.py
```

---

## 十、最佳实践

### 10.1 工具设计原则

1. **单一职责**：每个工具只做一件事
2. **清晰描述**：description 要准确描述功能和输入
3. **错误处理**：工具内部要处理异常
4. **幂等性**：相同输入应返回相同结果
5. **参数验证**：使用 Pydantic 验证输入

### 10.2 Prompt 优化

```python
# 好的 Agent Prompt
agent_prompt = """你是一个任务执行助手。

可用工具：
{tools}

使用以下格式：
Question: 需要回答的问题
Thought: 思考下一步应该做什么
Action: 选择一个工具
Action Input: 工具的输入
Observation: 工具的输出
... (重复 Thought/Action/Observation 直到得出答案)
Thought: 我现在知道最终答案了
Final Answer: 最终答案

注意：
- 必须严格遵循格式
- 一次只能调用一个工具
- 基于 Observation 做出下一步决策

开始！

Question: {input}
{agent_scratchpad}"""
```

### 10.3 性能优化

```python
# 1. 并行工具调用
async def parallel_tool_execution(tools_to_call):
    tasks = [tool.arun(input) for tool, input in tools_to_call]
    results = await asyncio.gather(*tasks)
    return results

# 2. 工具结果缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_tool_call(tool_name: str, input: str):
    return tools[tool_name].run(input)

# 3. 提前终止
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_execution_time=30,  # 30秒超时
    early_stopping_method="generate"
)
```

---

## 十一、相关资源

- [[知识图谱]] - 完整学习路径导航
- [[05-Agent教程]] - Agent 基础入门
- [[03-工具调用教程]] - 工具集成
- [[09-多Agent系统教程]] - 多Agent协作
- [[03-Agent设计原则]] - Agent 设计最佳实践
- [[Agent API迁移指南]] - API 版本变化说明

---

## 十二、参考资源

- [LangChain Agents 文档](https://python.langchain.com/docs/modules/agents/)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [LangSmith Agent 调试](https://docs.smith.langchain.com/)

---

**构建智能 Agent，让 AI 自主完成复杂任务！**
