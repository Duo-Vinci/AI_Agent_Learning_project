# LangChain Basics

基础入门项目，演示如何调用大语言模型、创建提示词模板和构建执行链。

## 学习目标

- 学习如何配置和调用大语言模型
- 理解提示词模板的作用
- 掌握 Chain 的基本概念

## 运行步骤

```bash
# 安装依赖
pip install langchain langchain-openai python-dotenv

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 添加您的 API Key

# 运行脚本
python src/basic_llm.py
```

## 文件结构

```
01-langchain-basics/
├── src/
│   └── basic_llm.py    # 主脚本
├── .env.example        # 环境变量示例
└── README.md           # 项目说明
```

## 相关教程

- 对应教程：`docs/02-教程/01-基础入门教程.md`

## 核心代码

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="deepseek-v4-flash")
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的AI助手。"),
    ("user", "{question}")
])
chain = prompt | llm
response = chain.invoke({"question": "什么是LangChain?"})
```

## 注意事项

- 确保已配置 API Key
- 支持 DeepSeek 和 OpenAI 两种 API