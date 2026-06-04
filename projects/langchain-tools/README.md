# LangChain Tools

工具调用项目，学习如何让AI调用外部工具。

## 学习目标

- 理解工具定义和注册
- 学习工具调用流程
- 掌握 Agent 与工具的交互

## 快速开始

```bash
pip install langchain langchain-openai python-dotenv
cp .env.example .env
python src/weather_tool.py
```

## 项目结构

```
langchain-tools/
├── src/
│   └── weather_tool.py
├── tests/
├── .env.example
└── README.md
```