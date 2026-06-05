# Agent 架构项目 - 完整示例

本项目包含了完整的 AI Agent 架构实现，从基础到高级。

## 项目结构

```
08-agent-architecture/
├── 01-react-agent/          # ReAct 模式 Agent
│   └── src/
│       ├── basic_react.py   # 基础 ReAct 实现
│       └── advanced_react.py # 高级特性（错误处理、重试等）
├── 02-planning-agent/       # 规划型 Agent
│   └── src/
│       └── plan_execute.py  # Plan-and-Execute 模式
├── 03-memory-systems/       # 记忆系统
│   └── src/
│       └── memory_system.py # 工作记忆、情节记忆、语义记忆
├── 04-tool-calling/         # 工具调用系统
│   └── src/
│       └── tool_system.py   # 工具注册、调用、验证
├── 05-agent-debugging/      # Agent 调试工具
│   └── src/
│       └── debug_tools.py   # 详细追踪、可视化、错误诊断
├── 06-custom-agent/         # 自定义 Agent 框架
│   └── src/
│       └── custom_agent.py  # 从零构建 Agent
└── 07-agent-evaluation/     # Agent 评估系统
    └── src/
        └── evaluation.py    # 性能评估、测试套件
```

## 快速开始

### 1. 安装依赖

```bash
cd Z:\Agent_WorkSpace\AI_Agent_Learning_project\projects\08-agent-architecture
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 运行示例

#### ReAct Agent（推荐从这里开始）

```bash
# 基础 ReAct Agent
python 01-react-agent/src/basic_react.py

# 高级 ReAct Agent（带错误处理和重试）
python 01-react-agent/src/advanced_react.py
```

#### 规划型 Agent

```bash
python 02-planning-agent/src/plan_execute.py
```

#### 记忆系统

```bash
python 03-memory-systems/src/memory_system.py
```

#### 工具调用系统

```bash
python 04-tool-calling/src/tool_system.py
```

#### Agent 调试

```bash
python 05-agent-debugging/src/debug_tools.py
```

#### 自定义 Agent

```bash
python 06-custom-agent/src/custom_agent.py
```

#### Agent 评估

```bash
python 07-agent-evaluation/src/evaluation.py
```

## 核心概念

### 1. ReAct 模式

ReAct（Reasoning + Acting）是最经典的 Agent 模式：

```
循环：
  1. Thought（思考）：分析当前状态，决定下一步
  2. Action（行动）：选择并执行一个工具
  3. Observation（观察）：获取工具执行结果
  4. 重复直到任务完成
```

**示例**：
```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# 定义工具
tools = [
    Tool(name="Calculator", func=calculate, description="执行数学计算"),
    Tool(name="Search", func=search, description="搜索信息")
]

# 创建 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 执行任务
result = agent_executor.invoke({"input": "查询天气并计算温度转换"})
```

### 2. 规划型 Agent

先制定完整计划，再逐步执行：

```python
# 1. 规划阶段：分解任务
tasks = planner.plan("分析销售数据并生成报告")
# -> [获取数据, 清洗数据, 计算指标, 生成图表, 撰写报告]

# 2. 执行阶段：按顺序执行
for task in tasks:
    result = executor.execute(task)
```

### 3. 记忆系统

三种记忆类型：

- **工作记忆**：短期，保存最近 5-7 条
- **情节记忆**：对话历史，可搜索
- **语义记忆**：长期知识，向量存储

```python
memory_system = UnifiedMemorySystem()

# 保存对话
memory_system.save_context(
    {"input": "Python是什么？"},
    {"output": "Python是一种高级编程语言"}
)

# 检索相关记忆
memories = memory_system.load_memory_variables({"input": "Python学习"})
```

### 4. 工具系统

使用 Pydantic 进行参数验证：

```python
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool

class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, description="搜索关键词")
    limit: int = Field(default=10, ge=1, le=100, description="结果数量")

tool = StructuredTool.from_function(
    func=search_function,
    name="Search",
    description="搜索信息",
    args_schema=SearchInput
)
```

## 最佳实践

### 1. 工具设计原则

✅ **好的工具设计**：
- 单一职责
- 清晰的描述
- 参数验证
- 错误处理

```python
@tool
def search_weather(location: str) -> str:
    """查询指定地点的天气信息。
    
    输入：地点名称（如'北京'）
    输出：天气描述字符串
    """
    return get_weather_api(location)
```

❌ **避免**：
- 工具做太多事
- 描述模糊
- 缺少错误处理

### 2. Prompt 优化

清晰的格式说明：

```python
prompt = """你是一个任务执行助手。

可用工具：
{tools}

使用格式：
Question: 问题
Thought: 思考
Action: 工具名称
Action Input: 工具输入
Observation: 工具输出
... (重复)
Thought: 我知道答案了
Final Answer: 最终答案

Question: {input}
{agent_scratchpad}"""
```

### 3. 错误处理

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=10,              # 限制最大迭代
    max_execution_time=60,          # 超时控制（秒）
    handle_parsing_errors=True,     # 自动处理解析错误
    early_stopping_method="generate" # 提前停止策略
)
```

### 4. 调试技巧

启用详细输出：

```python
# 方法1：使用 verbose
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 方法2：使用自定义回调
from langchain.callbacks import BaseCallbackHandler

class DebugCallback(BaseCallbackHandler):
    def on_agent_action(self, action, **kwargs):
        print(f"工具: {action.tool}, 输入: {action.tool_input}")
    
    def on_tool_end(self, output, **kwargs):
        print(f"输出: {output}")

agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    callbacks=[DebugCallback()]
)
```

查看中间步骤：

```python
result = agent_executor.invoke(
    {"input": "任务"},
    {"return_intermediate_steps": True}
)

for action, observation in result["intermediate_steps"]:
    print(f"动作: {action.tool}")
    print(f"输入: {action.tool_input}")
    print(f"输出: {observation}")
```

## 性能优化

### 1. 并行工具调用

```python
async def parallel_execution(tools_to_call):
    tasks = [tool.arun(input) for tool, input in tools_to_call]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 工具结果缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_tool_call(tool_name: str, input: str):
    return tools[tool_name].run(input)
```

### 3. 记忆压缩

```python
# 保留最近的消息
recent = history[-5:]

# 压缩旧消息
summary = llm.generate(f"总结以下对话：{old_messages}")
```

## 评估指标

运行评估系统：

```python
from evaluation import AgentEvaluator, create_test_suite

# 创建测试套件
test_cases = create_test_suite()

# 评估 Agent
evaluator = AgentEvaluator(agent_executor, test_cases)
results = evaluator.run_evaluation()

# 生成报告
evaluator.print_report()
```

**关键指标**：
- 任务成功率
- 平均步数
- 平均耗时
- Token 消耗
- 工具使用准确率

## 常见问题

### Q1: Agent 陷入无限循环怎么办？

**解决方案**：
1. 设置 `max_iterations` 限制
2. 使用 `early_stopping_method="generate"`
3. 优化提示词，明确停止条件

### Q2: 工具调用失败？

**解决方案**：
1. 检查工具描述是否清晰
2. 使用 `args_schema` 进行参数验证
3. 添加错误处理和重试机制

### Q3: LLM 输出格式错误？

**解决方案**：
1. 使用 `handle_parsing_errors=True`
2. 在提示词中添加格式示例
3. 使用结构化输出

### Q4: 如何减少 Token 消耗？

**解决方案**：
1. 使用记忆压缩
2. 限制历史长度
3. 选择更小的模型（如 gpt-3.5-turbo）
4. 优化提示词长度

## 进阶主题

### 1. 多 Agent 协作

```python
research_agent = create_agent("研究员", research_tools)
writer_agent = create_agent("作家", writing_tools)

# 研究员收集信息
research_result = research_agent.run("收集AI信息")

# 作家撰写文章
article = writer_agent.run(f"根据以下信息写文章：{research_result}")
```

### 2. Agent 反思

```python
# 生成初步答案
answer = agent.generate(question)

# 自我评估
reflection = agent.reflect(answer)

# 改进答案
if not reflection.is_satisfactory():
    improved_answer = agent.improve(answer, reflection.feedback)
```

### 3. 持久化记忆

```python
# 保存记忆到数据库
semantic_memory.save()  # 保存向量存储

# 下次加载
semantic_memory = SemanticMemory.load("./memory_dir")
```

## 参考资源

- [LangChain Agents 文档](https://python.langchain.com/docs/modules/agents/)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Agent 设计原则](../../docs/05-最佳实践/03-Agent设计原则.md)
- [Agent 架构教程](../../docs/02-教程/08-Agent架构教程.md)

## 下一步

1. 运行所有示例，理解每个模式
2. 尝试修改工具和提示词
3. 创建自己的 Agent 解决实际问题
4. 阅读相关论文深入理解原理

**祝学习愉快！** 🚀
