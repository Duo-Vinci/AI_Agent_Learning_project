# AI Agent Learning Project

一个用于学习 AI Agent 和 LangChain 的项目结构。

## 项目结构

```
├── docs/                    # 学习文档
│   ├── notes/              # 学习笔记
│   ├── tutorials/          # 教程文档
│   ├── resources/          # 学习资源
│   └── cheat-sheets/       # 速查表
├── projects/               # 工程实践
│   ├── langchain-basics/   # LangChain基础
│   ├── langchain-chatbot/  # 聊天机器人
│   ├── langchain-rag/      # RAG检索增强
│   ├── langchain-tools/    # 工具调用
│   └── langchain-agents/   # Agent智能体
└── .gitignore
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Duo-Vinci/AI_Agent_Learning_project.git
cd AI_Agent_Learning_project
```

### 2. 设置环境变量

在每个项目目录中创建 `.env` 文件：

```bash
cd projects/langchain-basics
cp .env.example .env
```

编辑 `.env` 文件，添加您的 API 密钥：

```
OPENAI_API_KEY=your-api-key-here
```

### 3. 安装依赖

```bash
pip install langchain langchain-openai python-dotenv faiss-cpu
```

### 4. 运行示例

```bash
python src/basic_llm.py
```

## 学习路径

1. **langchain-basics** - 学习 LangChain 核心概念
2. **langchain-chatbot** - 构建简单聊天机器人
3. **langchain-rag** - 实现 RAG 检索增强生成
4. **langchain-tools** - 学习工具调用机制
5. **langchain-agents** - 开发完整 Agent 智能体

## 环境变量配置

请参考各项目中的 `.env.example` 文件了解需要配置的环境变量。

## 贡献

欢迎提交 issue 和 pull request！

## 许可证

MIT License