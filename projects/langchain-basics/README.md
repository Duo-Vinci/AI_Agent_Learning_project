# LangChain Basics

LangChain 基础学习项目，涵盖核心概念和基础用法。

## 学习目标

- 了解 LangChain 的核心组件
- 学习如何使用 ChatOpenAI
- 掌握提示词模板的使用
- 理解 Chain 的概念

## 快速开始

### 安装依赖

```bash
pip install langchain langchain-openai python-dotenv
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
OPENAI_API_KEY=your-api-key-here
```

### 运行示例

```bash
python src/basic_llm.py
```

## 项目结构

```
langchain-basics/
├── src/           # 源代码
│   └── basic_llm.py
├── tests/         # 测试代码
├── .env.example   # 环境变量模板
└── README.md
```

## 学习内容

1. **basic_llm.py** - 基础 LLM 调用和提示词模板