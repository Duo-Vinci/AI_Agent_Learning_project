# Agent（智能代理）教程

## 一、项目概述

本项目演示如何使用 LangChain 创建智能代理（Agent），让 AI 能够自主规划和执行任务。

**项目位置**：`projects/05-langchain-agents/`

**学习目标**：
- 理解 Agent 的概念
- 学习如何创建智能代理
- 掌握多工具协作的流程

---

## 二、核心概念

### 2.1 什么是 Agent

Agent 是一种能够自主思考、规划和执行任务的 AI 系统。它可以：
1. 分析问题
2. 决定需要什么工具
3. 调用工具获取信息
4. 总结结果

### 2.2 Agent 的特点

- **自主性**：能够自主决定下一步做什么
- **多工具协作**：可以使用多种工具完成复杂任务
- **反思能力**：能够评估执行结果并调整策略

---

## 三、Agent 工作流程示意图

```
┌─────────────────────────────────────────────────────────────────┐
│ 用户提问："帮我查询今天北京的天气，然后推荐一些适合户外活动"          │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Agent 分析问题，制定计划：                                        │
│ 1. 先查询北京天气                                                │
│ 2. 根据天气推荐户外活动                                           │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 步骤1: 调用天气工具                                              │
│  结果：北京今天晴朗，温度25度                                     │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 步骤2: 分析天气结果，决定下一步                                    │
│  决定：天气很好，可以推荐户外活动                                   │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 步骤3: 生成最终回答                                              │
│  基于天气结果，推荐适合的户外活动                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 多工具协作示例

```
用户问题："计算 100 + 200，然后用中文解释结果"
              ↓
    Agent 分析：需要两步
              ↓
    步骤1: 调用计算器工具
           输入：100 + 200
           结果：300
              ↓
    步骤2: 调用 LLM 生成解释
           输入：解释 300 的含义
           结果："100加200等于300..."
              ↓
    最终回答：计算结果是300。这意味着...
```

---

## 四、代码解析

### 4.1 定义工具

```python
from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    weather_data = {
        "北京": "晴朗，温度25度",
        "上海": "多云，温度28度"
    }
    return weather_data.get(city, "未知城市")
```

**作用**：定义可供 Agent 使用的工具。

### 4.2 创建 Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

llm = ChatOpenAI(model="deepseek-v4-flash", temperature=0)

tools = [calculator, get_weather]

# 获取 ReAct prompt
prompt = hub.pull("hwchase17/react")

# 创建 agent
agent = create_react_agent(llm, tools, prompt)

# 创建 agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

**作用**：创建智能代理，配置可用工具。

### 4.3 执行任务

```python
response = agent_executor.invoke({"input": "今天北京天气怎么样？如果天气好的话，计算一下 100 + 200"})
print(response["output"])
```

**作用**：让 Agent 自主规划并执行任务。

---

## 五、运行步骤

```bash
# 1. 安装依赖
pip install langchain langchain-openai python-dotenv

# 2. 创建 .env 文件
cd projects/05-langchain-agents
copy .env.example .env
# 编辑 .env 添加您的 API Key

# 3. 运行脚本
python src/simple_agent.py
```

---

## 六、关键概念

### 6.1 Agent 类型

LangChain 新版本使用 `create_react_agent` 创建 Agent，基于 ReAct 框架：

| 方法 | 说明 |
|------|------|
| `create_react_agent` | 使用 ReAct 框架，根据工具描述决定是否调用 |
| `create_structured_chat_agent` | 支持复杂的多步骤任务 |
| `create_openai_functions_agent` | 使用 OpenAI 的函数调用能力 |

### 6.2 工具描述的重要性

工具描述必须清晰，让 Agent 知道：
- 这个工具是做什么的
- 什么时候应该使用这个工具
- 需要什么参数

---

## 七、注意事项

1. **工具安全性**：谨慎使用可能有风险的工具
2. **成本控制**：复杂任务可能会调用多次工具
3. **结果验证**：对重要任务进行结果验证

---

## 八、相关资源

- [[知识图谱]] - 完整学习路径导航
- [[03-工具调用教程]] - 前置知识
- [[02-聊天机器人教程]] - 对话管理
- [[08-Agent架构教程]] - Agent 架构设计
- [[09-多Agent系统教程]] - 多Agent协作
- [[03-Agent设计原则]] - Agent 设计最佳实践
- [[Agent API迁移指南]] - API 版本变化说明

---

## 九、进阶扩展

可以尝试：
1. 添加更多工具（搜索、数据库查询等）
2. 实现复杂的多步骤任务
3. 添加记忆功能
4. 实现 Agent 的反思和自我修正能力

---

**下一步**: 学习 [[08-Agent架构教程]]