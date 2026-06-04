# Agent API 迁移指南

> 📖 **返回**: [[00-LangChain入门教程]]

---

## 一、API 变化概述

**旧方式（已废弃）**: 使用 `initialize_agent` + `AgentType`

**新方式（推荐）**: 使用 **LangGraph** 中的 `create_react_agent`

从 `langchain` 0.1.0+ 版本开始，旧的 Agent API 已被完全替换。

---

## 二、API 对比

### 旧版本（已废弃）

```python
from langchain.agents import initialize_agent, AgentType

# 创建 agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 执行查询
result = agent.run("今天天气怎么样？")
```

### 新版本（推荐）

```python
from langgraph.prebuilt import create_react_agent

# 创建 agent（不需要 prompt，LangGraph 会自动处理）
agent_executor = create_react_agent(llm, tools)

# 执行查询（使用 messages 格式）
result = agent_executor.invoke({"messages": [("user", "今天天气怎么样？")]})

# 获取回答
final_answer = result["messages"][-1].content
```

---

## 三、主要变化对比表

| 旧版本 | 新版本 |
|--------|--------|
| `initialize_agent(tools, llm, ...)` | `create_react_agent(llm, tools)` |
| `AgentType.ZERO_SHOT_REACT_DESCRIPTION` | 不再需要，自动使用 |
| `agent.run("问题")` | `agent_executor.invoke({"messages": [("user", "问题")]})` |
| 直接返回字符串 | 返回包含 `messages` 的字典，取最后一条消息的 `content` |
| 不需要 `langchainhub` | 不依赖 `langchainhub` |

---

## 四、完整迁移示例

### 工具调用项目迁移

#### 旧代码（已废弃）:

```python
from langchain.agents import initialize_agent, AgentType

@tool
def get_weather(city: str) -> str:
    """获取天气"""
    return f"{city}天气晴朗"

agent = initialize_agent(
    [get_weather],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

result = agent.run("北京今天天气怎么样？")
```

#### 新代码（推荐）:

```python
from langgraph.prebuilt import create_react_agent

@tool
def get_weather(city: str) -> str:
    """获取天气"""
    return f"{city}天气晴朗"

agent_executor = create_react_agent(llm, [get_weather])
result = agent_executor.invoke({"messages": [("user", "北京今天天气怎么样？")]})
print(result["messages"][-1].content)
```

---

## 五、为什么使用 LangGraph

1. **更现代**: LangGraph 是官方推荐的新方式
2. **更强大**: 支持多轮对话、状态管理
3. **更简单**: 不需要手动拉取 prompt
4. **更稳定**: 持续更新和维护

---

## 六、相关教程

- [[03-工具调用教程]] - 工具调用详解
- [[05-Agent教程]] - Agent 开发详解
