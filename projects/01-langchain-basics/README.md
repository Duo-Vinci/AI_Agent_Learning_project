# LangChain Basics - 基础入门项目

这是一个完整的 LangChain 基础教程项目，包含 8 个循序渐进的示例，从入门到进阶，帮助你全面掌握 LangChain 的核心概念。

## 项目概述

本项目包含 8 个独立的学习模块，每个模块都可以独立运行，覆盖 LangChain 的核心功能：

1. **提示词模板** - 学习如何创建和使用各种提示词模板
2. **Chain（链）** - 掌握 LCEL 和链式组合
3. **流式输出** - 实现实时响应和流式处理
4. **输出解析器** - 将 LLM 输出转换为结构化数据
5. **回调系统** - 监控和控制 LLM 执行过程
6. **模型对比** - 对比不同模型的性能和输出
7. **错误处理** - 实现重试、降级和容错机制
8. **完整应用** - 整合所有概念的实战项目

## 快速开始

### 1. 安装依赖

```bash
cd projects/01-langchain-basics
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API Key
# DEEPSEEK_API_KEY=your_key_here
```

### 3. 运行快速开始

```bash
python quickstart.py
```

## 学习路径

### 初级（必学）

**01_prompt_templates.py** - 提示词模板详解
- 基本提示词模板
- 对话提示词模板
- Few-shot 提示词
- 模板组合
- 部分变量预填充

```bash
python src/01_prompt_templates.py
```

**02_chains.py** - Chain 链式组合
- 简单 LLM Chain
- 顺序链
- LCEL 高级特性
- 并行链
- 条件分支链

```bash
python src/02_chains.py
```

**03_streaming.py** - 流式输出
- 基本流式输出
- 流式 Chain
- 回调函数
- 异步流式输出
- 流式 vs 非流式对比

```bash
python src/03_streaming.py
```

### 中级（推荐）

**04_output_parsers.py** - 输出解析器
- 字符串解析器
- JSON 解析器
- Pydantic 解析器
- 列表解析器
- 自定义解析器

```bash
python src/04_output_parsers.py
```

**05_callbacks.py** - 回调系统
- 标准回调处理器
- 自定义回调
- 性能监控
- 错误处理回调
- Token 计数

```bash
python src/05_callbacks.py
```

### 高级（进阶）

**06_model_comparison.py** - 模型对比
- 不同模型输出对比
- 温度参数影响
- 性能对比
- 成本估算
- 模型选择指南

```bash
python src/06_model_comparison.py
```

**07_error_handling.py** - 错误处理
- 基本错误处理
- 重试机制
- 超时处理
- 降级策略
- 优雅降级

```bash
python src/07_error_handling.py
```

**08_complete_example.py** - 完整应用示例
- 文章生成器
- 多步骤处理
- 流式生成
- 批量处理
- 文件保存

```bash
python src/08_complete_example.py
```

## 项目结构

```
01-langchain-basics/
├── src/
│   ├── basic_llm.py              # 原始基础示例
│   ├── 01_prompt_templates.py    # 提示词模板详解
│   ├── 02_chains.py              # Chain 详解
│   ├── 03_streaming.py           # 流式输出详解
│   ├── 04_output_parsers.py      # 输出解析器详解
│   ├── 05_callbacks.py           # 回调系统详解
│   ├── 06_model_comparison.py    # 模型对比
│   ├── 07_error_handling.py      # 错误处理
│   └── 08_complete_example.py    # 完整应用示例
├── tests/                         # 测试文件
├── output/                        # 输出目录（自动创建）
├── .env.example                   # 环境变量示例
├── requirements.txt               # 项目依赖
├── quickstart.py                  # 快速开始脚本
└── README.md                      # 项目说明
```

## 核心概念

### 1. LLM（大语言模型）

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    temperature=0.7,
    api_key="your_key"
)
```

### 2. Prompt Template（提示词模板）

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("user", "{question}")
])
```

### 3. Chain（链）

```python
# LCEL 语法
chain = prompt | llm | output_parser

# 执行
result = chain.invoke({"role": "助手", "question": "你好"})
```

### 4. Output Parser（输出解析器）

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
chain = prompt | llm | parser  # 直接返回字符串
```

## 学习建议

1. **按顺序学习** - 从 01 到 08，每个模块都基于前面的知识
2. **动手实践** - 运行每个示例，修改参数，观察输出变化
3. **阅读注释** - 代码中有详细的中文注释
4. **尝试修改** - 改变提示词、温度、模型等参数
5. **构建项目** - 基于 08_complete_example.py 构建自己的应用

## 常见问题

### Q: 如何选择合适的模型？
A: 参考 `06_model_comparison.py`，根据任务类型、预算和性能要求选择。

### Q: 如何处理 API 调用失败？
A: 参考 `07_error_handling.py`，实现重试机制和降级策略。

### Q: 如何提升用户体验？
A: 使用流式输出（`03_streaming.py`），让用户立即看到响应。

### Q: 如何控制输出格式？
A: 使用输出解析器（`04_output_parsers.py`），将文本转换为结构化数据。

## 下一步

完成本项目后，你可以继续学习：

- **02-langchain-chatbot** - 构建聊天机器人
- **03-langchain-tools** - 工具调用系统
- **04-langchain-rag** - RAG 检索增强
- **05-langchain-agents** - Agent 智能体

## 相关资源

- [LangChain 官方文档](https://python.langchain.com/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)
- [OpenAI API 文档](https://platform.openai.com/docs)

## 注意事项

- 确保已正确配置 API Key
- 注意 API 调用成本
- 建议先在测试环境运行
- 生产环境需要完善的错误处理

## 技术支持

如有问题，请检查：
1. API Key 是否正确配置
2. 网络连接是否正常
3. 依赖包是否完整安装
4. Python 版本是否 >= 3.8