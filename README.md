# AI Agent 学习项目

这是一个用于学习 LangChain 和 AI Agent 开发的项目，包含完整的教学文档和实践项目。

## 🚀 项目特点

- 📚 **完整教程**：从基础到进阶的中文教学文档
- 💻 **实践项目**：5个循序渐进的实战项目
- 🔧 **多模型支持**：支持 DeepSeek、OpenAI 等多种大语言模型
- ⚙️ **环境变量配置**：使用 `.env` 文件管理敏感配置
- 🔄 **技能支持**：内置教程-项目对齐技能

## 📁 项目结构

```
AI_Agent_Learning_project/
├── .trae/
│   └── skills/
│       └── tutorial-project-aligner/  # 教程-项目对齐技能
├── docs/                              # 教学文档（中文）
│   ├── 01-学习笔记/                    # 学习笔记和指南
│   ├── 02-教程/                        # 完整教程（按顺序学习）
│   ├── 03-资源链接/                    # 学习资源
│   └── 04-速查表/                      # API 速查表
├── projects/                          # 实践项目（英文）
│   ├── 01-langchain-basics/           # LLM基础调用
│   ├── 02-langchain-chatbot/          # 聊天机器人
│   ├── 03-langchain-tools/            # 工具调用
│   ├── 04-langchain-rag/              # RAG检索增强生成
│   └── 05-langchain-agents/           # 智能代理
└── README.md                          # 项目说明
```

## 📖 学习路径

### 教程顺序

| 序号 | 教程 | 学习内容 |
|------|------|---------|
| 00 | LangChain入门教程 | 概述和核心概念 |
| 01 | 基础入门教程 | LLM调用、提示词模板、Chain |
| 02 | 聊天机器人教程 | 对话历史、多轮对话 |
| 03 | 工具调用教程 | 工具定义、工具调用 |
| 04 | RAG教程 | 向量数据库、文档检索 |
| 05 | Agent教程 | 智能代理、多工具协作 |

### 项目对应关系

| 序号 | 项目 | 教程 | 核心功能 |
|------|------|------|---------|
| 01 | `01-langchain-basics` | 基础入门教程 | LLM基础调用 |
| 02 | `02-langchain-chatbot` | 聊天机器人教程 | 多轮对话 |
| 03 | `03-langchain-tools` | 工具调用教程 | 工具调用 |
| 04 | `04-langchain-rag` | RAG教程 | 检索问答 |
| 05 | `05-langchain-agents` | Agent教程 | 智能代理 |

## 🔧 环境配置

### 安装依赖

```bash
# 基础依赖
pip install langchain langchain-openai python-dotenv

# RAG 项目额外依赖
pip install faiss-cpu
```

### 配置 API Key

在每个项目目录下创建 `.env` 文件：

```env
# DeepSeek API 配置（推荐）
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash

# 或使用 OpenAI
# OPENAI_API_KEY=your-api-key-here
# OPENAI_MODEL=gpt-3.5-turbo
```

**获取 API Key：**
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Duo-Vinci/AI_Agent_Learning_project.git
cd AI_Agent_Learning_project

# 2. 从第一个项目开始
cd projects/01-langchain-basics

# 3. 创建 .env 文件
copy .env.example .env
# 编辑 .env 添加您的 API Key

# 4. 运行示例
python src/basic_llm.py
```

## 📚 文档目录

### 学习笔记
- `入门指南.md` - 项目入门说明
- `环境变量指南.md` - .env 文件配置说明

### 教程
- `00-LangChain入门教程.md` - LangChain 概述
- `01-基础入门教程.md` - LLM基础调用
- `02-聊天机器人教程.md` - 聊天机器人开发
- `03-工具调用教程.md` - 工具调用实现
- `04-RAG教程.md` - RAG检索增强生成
- `05-Agent教程.md` - 智能代理开发

### 资源链接
- `学习资源链接.md` - 推荐学习资源

### 速查表
- `LangChain速查表.md` - 常用 API 速查

## ⚡ 内置技能

### tutorial-project-aligner

**功能**：对齐教程和工程，生成对应的教程文档和 README 文件

**触发场景**：
- 用户要求同步文档时
- 用户完成新工程后需要生成教程时
- 需要更新整体 README 时

## 🎯 学习目标

1. **基础阶段**：理解 LLM 调用原理
2. **进阶阶段**：掌握 Chain、提示词工程
3. **高级阶段**：实现工具调用和 RAG
4. **专家阶段**：构建智能 Agent

## ⚠️ 注意事项

1. **API Key 安全**：不要将 `.env` 文件提交到版本控制
2. **成本控制**：注意 API 调用的费用
3. **网络环境**：确保网络能够访问 API 服务
4. **依赖版本**：建议使用最新版本的依赖包

## 📝 贡献

欢迎提交问题和建议！

## 📄 许可证

MIT License

---

**开始您的 AI Agent 学习之旅吧！🚀**