# LangChain Tools

工具调用项目，演示如何让 AI 调用外部工具获取信息。

## 学习目标

- 理解工具调用的概念
- 学习如何定义自定义工具
- 掌握工具调用的流程

## 运行步骤

```bash
# 安装依赖
pip install langchain langchain-openai python-dotenv

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 添加您的 API Key

# 运行脚本
python src/weather_tool.py
```

## 文件结构

```
03-langchain-tools/
├── src/
│   └── weather_tool.py    # 主脚本
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 相关教程

- 对应教程：`docs/02-教程/03-工具调用教程.md`

## 核心代码

```python
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}今天天气晴朗"

# 获取 ReAct prompt
prompt = hub.pull("hwchase17/react")

# 创建 agent
agent = create_react_agent(llm, [get_weather], prompt)

# 创建 agent executor
agent_executor = AgentExecutor(agent=agent, tools=[get_weather], verbose=True)

# 执行查询
response = agent_executor.invoke({"input": "北京今天天气怎么样？"})
```

## 注意事项

- 工具描述要清晰，让 AI 知道何时使用
- 谨慎使用有风险的工具