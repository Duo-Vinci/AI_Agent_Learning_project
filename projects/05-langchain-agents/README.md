# LangChain Agents

智能代理项目，演示如何创建能够自主规划和执行任务的 AI 代理。

## 学习目标

- 理解 Agent 的概念
- 学习如何创建智能代理
- 掌握多工具协作的流程

## 运行步骤

```bash
# 安装依赖
pip install langchain langchain-openai python-dotenv

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 添加您的 API Key

# 运行脚本
python src/simple_agent.py
```

## 文件结构

```
05-langchain-agents/
├── src/
│   └── simple_agent.py    # 主脚本
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 相关教程

- 对应教程：`docs/02-教程/05-Agent教程.md`

## 核心概念

Agent 能够：
1. 分析问题
2. 决定需要什么工具
3. 调用工具获取信息
4. 总结结果

## 示例代码

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

tools = [calculator, get_weather]

# 获取 ReAct prompt
prompt = hub.pull("hwchase17/react")

# 创建 agent
agent = create_react_agent(llm, tools, prompt)

# 创建 agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 执行查询
response = agent_executor.invoke({"input": "北京天气怎么样？如果天气好，计算 100+200"})
```

## 注意事项

- 工具安全性很重要
- 注意控制 API 调用成本