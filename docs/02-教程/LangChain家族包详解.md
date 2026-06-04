# LangChain 家族包详解

> 📖 **返回**：[[00-LangChain入门教程]]

---

## 一、包依赖关系图

```
langchain (主包)
    ├── langchain-core (核心接口)
    ├── langchain-community (社区集成)
    ├── langchain-openai (模型集成)
    ├── langchain-text-splitters (文本分割)
    └── langchainhub (提示词仓库)

langgraph (图结构 Agent)
    ├── langchain-core
    └── langgraph-sdk
```

---

## 二、核心包

### langchain-core

**作用**：定义 LangChain 的基础接口

包含：
- LLM 抽象接口
- Chain 基础类
- Tool 定义
- Message 类型

### langchain

**作用**：主包，整合所有功能

包含：
- Agent 创建
- Chain 组合
- Memory 管理
- 文档加载

### langchain-community

**作用**：社区集成

包含：
- 各种数据库集成
- API 集成
- 工具集成

---

## 三、模型集成包

### langchain-openai

**作用**：OpenAI 和兼容 API 集成

支持：
- GPT-3.5、GPT-4
- DALL-E
- **DeepSeek**（兼容 OpenAI API）

```python
from langchain_openai import ChatOpenAI

# DeepSeek 配置
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key="...",
    base_url="https://api.deepseek.com/v1"
)
```

### langchain-anthropic

**作用**：Anthropic Claude 集成

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-opus")
```

### langchain-google

**作用**：Google Gemini 集成

```python
from langchain_google import ChatGoogle

llm = ChatGoogle(model="gemini-pro")
```

---

## 四、功能扩展包

### langchainhub

**作用**：提示词模板仓库

```python
from langchain import hub

# 获取 ReAct prompt
prompt = hub.pull("hwchase17/react")

# 获取 OpenAI Functions prompt
prompt = hub.pull("hwchase17/openai-functions-agent")
```

### langchain-text-splitters

**作用**：文本分割算法

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

### langgraph

**作用**：图结构 Agent

用于构建复杂的多步骤 Agent 流程。

---

## 五、安装建议

### 基础安装

```bash
pip install langchain langchain-core langchain-openai python-dotenv
```

### Agent 开发

```bash
pip install langchainhub langgraph
```

### RAG 开发

```bash
pip install langchain-text-splitters faiss-cpu
```

### 完整安装

```bash
pip install langchain langchain-community langchain-openai langchainhub langgraph
```

---

## 六、为什么拆分成多个包？

1. **减少依赖**：只安装需要的包
2. **版本独立**：各包可以独立更新
3. **社区贡献**：社区可以独立贡献集成包
4. **轻量化**：核心包更小，加载更快

---

**返回**：[[00-LangChain入门教程]]