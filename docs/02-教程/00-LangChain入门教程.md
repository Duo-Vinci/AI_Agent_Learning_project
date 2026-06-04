# LangChain 入门教程

## 一、什么是 LangChain？

LangChain 是一个开源框架，旨在简化基于大语言模型（LLM）的应用程序开发。

### 核心特点

- **模块化设计**：将功能拆分成多个独立的包
- **链式调用**：支持多步骤的复杂任务
- **工具集成**：让 AI 能够调用外部工具
- **记忆管理**：支持对话历史和上下文

---

## 二、LangChain 家族包

LangChain 采用模块化设计，将功能拆分成多个独立的包：

### 核心包

| 包名 | 作用 |
|------|------|
| `langchain-core` | 核心抽象和接口 |
| `langchain` | 主包，整合所有功能 |
| `langchain-community` | 社区集成 |

### 模型集成包

| 包名 | 作用 |
|------|------|
| `langchain-openai` | OpenAI/DeepSeek 集成 |
| `langchain-anthropic` | Claude 模型集成 |
| `langchain-google` | Gemini 模型集成 |

### 功能扩展包

| 包名 | 作用 |
|------|------|
| `langchainhub` | 提示词模板仓库 |
| `langchain-text-splitters` | 文本分割 |
| `langgraph` | 图结构 Agent |

> 💡 **提示**：详细说明见 [[LangChain家族包详解]]

---

## 三、LangChainHub 是什么？

**LangChainHub** 是 LangChain 官方提供的提示词和模板仓库。

### 主要功能

- 获取预定义的 Prompt 模板
- 分享自定义模板
- 版本控制

### 使用示例

```python
from langchain import hub

# 获取 ReAct prompt
prompt = hub.pull("hwchase17/react")
```

---

## 四、环境配置

### .env 文件配置

`.env` 文件用于存储敏感配置信息（如 API 密钥）。

> 📖 **详细说明**：见 [[环境变量配置指南]]

### DeepSeek API 配置

```env
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash
```

### OpenAI API 配置

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

---

## 五、学习路径

建议按照以下顺序学习：

1. [[01-基础入门教程]] - LLM 调用、提示词模板
2. [[02-聊天机器人教程]] - 对话历史、多轮对话
3. [[03-工具调用教程]] - 工具定义、Agent 创建
4. [[04-RAG教程]] - 向量数据库、文档检索
5. [[05-Agent教程]] - 智能代理、多工具协作

---

## 六、API 版本变化

LangChain 在新版本中更新了 Agent API：

| 旧版本（已弃用） | 新版本 |
|-----------------|--------|
| `initialize_agent` | `create_react_agent` |
| `AgentType` | `AgentExecutor` |
| `agent.run()` | `agent_executor.invoke({"input": ...})` |

> ⚠️ **重要**：详细迁移说明见 [[Agent API迁移指南]]

---

## 七、快速开始

```bash
# 安装依赖
pip install langchain langchain-openai python-dotenv langchainhub

# 创建 .env 文件
copy .env.example .env

# 运行示例
python src/basic_llm.py
```

---

## 八、相关资源

- [[环境变量配置指南]] - .env 文件详细说明
- [[LangChain家族包详解]] - 包依赖关系
- [[Agent API迁移指南]] - API 版本变化说明
- [[学习资源链接]] - 外部学习资源

---

## 九、常见问题

### Q: ModuleNotFoundError: No module named 'dotenv'

**原因**：未安装 `python-dotenv`

**解决**：
```bash
pip install python-dotenv
```

### Q: ImportError: cannot import name 'initialize_agent'

**原因**：LangChain 新版本已弃用 `initialize_agent`

**解决**：使用新的 Agent API，详见 [[Agent API迁移指南]]

---

**下一步**：开始学习 [[01-基础入门教程]]