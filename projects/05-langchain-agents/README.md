# LangChain Agents 项目

完整的智能代理（Agent）系统，从基础概念到实际应用。

## 项目概述

Agent是能够自主决策、规划和执行任务的AI系统。它可以：
- 理解复杂任务
- 选择合适的工具
- 执行多步骤推理
- 自主完成目标

本项目包含：
- **quickstart.py**: 快速入门（理解Agent核心概念）
- **simple_agent.py**: 基础Agent实现

## 学习目标

- ✅ 理解Agent的概念和工作原理
- ✅ 掌握Agent的推理过程（ReAct模式）
- ✅ 学习创建不同类型的Agent
- ✅ 实现工具与Agent的集成
- ✅ 管理Agent的记忆和状态
- ✅ 构建多Agent协作系统
- ✅ Agent的调试和优化

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 API Key
```

### 3. 运行快速入门

```bash
# 最快的Agent体验
python src/quickstart.py
```

## 核心概念

### Agent vs 普通LLM调用

| 特性 | 普通LLM | Agent |
|------|---------|-------|
| 决策能力 | 被动响应 | 主动规划 |
| 工具使用 | 不支持 | 自主选择和使用工具 |
| 多步推理 | 单次生成 | 循环思考-行动 |
| 任务复杂度 | 简单问答 | 复杂任务自动化 |

### Agent工作流程（ReAct模式）

```
1. Thought（思考）
   分析问题，决定下一步做什么

2. Action（行动）
   选择并执行工具

3. Observation（观察）
   获取工具执行结果

4. 重复1-3，直到可以给出最终答案

5. Final Answer（最终答案）
   综合所有信息，回答用户问题
```

### 创建简单Agent

```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1. 创建工具
@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))

@tool
def get_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [calculator, get_time]

# 2. 创建LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 3. 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手，可以使用工具来回答问题。"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 4. 创建Agent
agent = create_openai_tools_agent(llm, tools, prompt)

# 5. 创建Agent执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5
)

# 6. 执行任务
result = agent_executor.invoke({
    "input": "现在几点？计算 15 * 8"
})
```

## Agent类型

### 1. OpenAI Functions Agent
最推荐的Agent类型，使用函数调用。

```python
from langchain.agents import create_openai_functions_agent

agent = create_openai_functions_agent(llm, tools, prompt)
```

### 2. OpenAI Tools Agent
支持最新的工具调用格式。

```python
from langchain.agents import create_openai_tools_agent

agent = create_openai_tools_agent(llm, tools, prompt)
```

### 3. ReAct Agent
经典的推理-行动模式。

```python
from langchain.agents import create_react_agent
from langchain import hub

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
```

### 4. Structured Chat Agent
支持多输入工具的对话Agent。

```python
from langchain.agents import create_structured_chat_agent

agent = create_structured_chat_agent(llm, tools, prompt)
```

## 工具设计

### 好的工具设计

```python
@tool
def search_database(query: str) -> str:
    """
    在数据库中搜索信息。
    
    使用场景：
    - 需要查找用户数据
    - 需要检索历史记录
    - 需要查询产品信息
    
    参数：
    - query: 搜索关键词
    
    返回：
    - 搜索结果的JSON字符串
    """
    # 实现搜索逻辑
    results = database.search(query)
    return json.dumps(results, ensure_ascii=False)
```

### 工具设计原则

1. **清晰的描述**：告诉Agent何时使用该工具
2. **明确的参数**：使用类型注解和描述
3. **可靠的执行**：完善的错误处理
4. **标准的返回**：统一的返回格式（通常是字符串）
5. **适当的粒度**：一个工具做一件事

## Agent记忆管理

### 添加对话记忆

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)
```

### 使用检查点保存状态

```python
from langchain.memory import ConversationBufferMemory

# 对话后保存
memory.save_context(
    {"input": "用户问题"},
    {"output": "Agent回答"}
)

# 下次对话时加载
history = memory.load_memory_variables({})
```

## 最佳实践

### 1. 控制Agent行为

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,        # 最大迭代次数
    max_execution_time=30,   # 最大执行时间（秒）
    early_stopping_method="generate",  # 提前停止策略
    verbose=True
)
```

### 2. 自定义停止条件

```python
def should_continue(output: str) -> bool:
    """自定义停止逻辑"""
    if "STOP" in output:
        return False
    return True
```

### 3. 错误处理

```python
try:
    result = agent_executor.invoke({"input": question})
except Exception as e:
    print(f"Agent执行失败: {str(e)}")
    # 记录错误，重试或降级处理
```

### 4. 日志和调试

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 使用verbose查看推理过程
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True  # 打印推理步骤
)
```

## 实际应用场景

### 1. 客户服务Agent
```python
tools = [
    search_knowledge_base,  # 搜索知识库
    query_order_status,     # 查询订单
    create_ticket,          # 创建工单
    send_email             # 发送邮件
]
```

### 2. 数据分析Agent
```python
tools = [
    execute_sql,           # 执行SQL查询
    generate_chart,        # 生成图表
    calculate_statistics,  # 统计计算
    export_report         # 导出报告
]
```

### 3. 自动化运维Agent
```python
tools = [
    check_server_status,   # 检查服务器状态
    restart_service,       # 重启服务
    query_logs,           # 查询日志
    send_alert            # 发送告警
]
```

## 安全注意事项

### 1. 工具权限控制

```python
@tool
def execute_command(command: str) -> str:
    """执行系统命令（受限）"""
    # 白名单检查
    allowed_commands = ['ls', 'pwd', 'date']
    cmd = command.split()[0]
    
    if cmd not in allowed_commands:
        return "错误: 不允许执行此命令"
    
    # 执行命令
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode()
```

### 2. 输入验证

```python
from pydantic import BaseModel, Field, validator

class SearchInput(BaseModel):
    query: str = Field(description="搜索查询")
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) > 100:
            raise ValueError("查询过长")
        if any(char in v for char in [';', '--', '/*']):
            raise ValueError("查询包含非法字符")
        return v
```

### 3. 速率限制

```python
from time import time, sleep

class RateLimiter:
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def allow_call(self) -> bool:
        now = time()
        self.calls = [c for c in self.calls if now - c < self.period]
        
        if len(self.calls) >= self.max_calls:
            return False
        
        self.calls.append(now)
        return True
```

## 常见问题

### Q: Agent和Chain的区别？
- **Chain**: 预定义的执行流程，按顺序执行
- **Agent**: 自主决策，根据情况选择工具和步骤

### Q: Agent陷入循环怎么办？
设置`max_iterations`参数限制最大迭代次数：
```python
agent_executor = AgentExecutor(agent=agent, tools=tools, max_iterations=5)
```

### Q: 如何让Agent更可靠？
1. 编写清晰的工具描述
2. 优化系统提示词
3. 添加错误处理和重试机制
4. 测试各种边界情况
5. 记录和分析失败案例

### Q: 成本如何控制？
1. 限制最大迭代次数
2. 使用更便宜的模型（如gpt-3.5-turbo）
3. 缓存常见查询结果
4. 监控API调用次数

## 调试技巧

### 1. 查看推理过程
```python
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### 2. 自定义回调
```python
from langchain.callbacks import StdOutCallbackHandler

handler = StdOutCallbackHandler()
agent_executor.invoke({"input": question}, callbacks=[handler])
```

### 3. 分析工具使用
```python
# 记录每次工具调用
tool_calls = []

class ToolLogger(BaseCallbackHandler):
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_calls.append({
            "tool": serialized["name"],
            "input": input_str
        })
```

## 注意事项

- ⚠️ 工具安全性很重要（验证输入、限制权限）
- ⚠️ 注意控制API调用成本
- ⚠️ 设置合理的超时和迭代限制
- ⚠️ 敏感操作需要人工确认
- ✅ 详细记录Agent的决策过程
- ✅ 为关键工具添加审计日志
- ✅ 定期审查和优化工具集

## 相关教程

- 对应教程：`docs/02-教程/05-Agent教程.md`
- LangChain Agent文档：https://python.langchain.com/docs/modules/agents/

## 下一步

完成本项目后，可以继续学习：
- 多Agent协作系统
- 自定义Agent类型
- 生产级Agent部署

## 许可证

MIT License