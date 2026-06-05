# AI Agent 学习项目

这是一个完整的 AI Agent 学习体系，从 Python 基础到生产部署，涵盖 LangChain、RAG、多 Agent 协作等核心技术。

## 🚀 项目特点

- 📚 **系统化教程**：13个循序渐进的中文教学文档
- 💻 **实战项目**：13个完整的实践项目，包含60+子项目
- 🔧 **多模型支持**：支持 DeepSeek、OpenAI、Claude 等多种大语言模型
- ⚙️ **生产级实践**：从开发到部署的完整工程化实践
- 📖 **最佳实践**：行业经验总结和案例研究
- 🎯 **编号体系**：所有文件和目录都有学习顺序编号

---

## 📁 项目结构

```
AI_Agent_Learning_project/
├── docs/                                  # 教学文档（中文）
│   ├── 知识图谱.md                        # 🗺️ 学习导航中心（双链入口）
│   ├── 01-学习笔记/                        # 学习笔记和指南
│   │   ├── 入门指南.md
│   │   ├── 环境变量指南.md
│   │   ├── 环境变量配置指南.md
│   │   ├── Python异步编程在AI中的应用.md
│   │   └── 项目实战与简历指南.md
│   ├── 02-教程/                            # 完整教程（按顺序学习）
│   │   ├── 00-LangChain入门教程.md
│   │   ├── 01-基础入门教程.md
│   │   ├── 02-聊天机器人教程.md
│   │   ├── 03-工具调用教程.md
│   │   ├── 04-RAG教程.md
│   │   ├── 05-Agent教程.md
│   │   ├── 06-Prompt工程教程.md
│   │   ├── 07-高级RAG教程.md
│   │   ├── 08-Agent架构教程.md
│   │   ├── 09-多Agent系统教程.md
│   │   ├── 10-生产级开发教程.md
│   │   ├── 11-部署教程.md
│   │   ├── 12-运维监控教程.md
│   │   ├── LangChain家族包详解.md
│   │   └── Agent API迁移指南.md
│   ├── 03-资源链接/                        # 学习资源
│   │   └── 学习资源链接.md
│   ├── 04-速查表/                          # API 速查表
│   │   └── LangChain速查表.md
│   ├── 05-最佳实践/                        # 最佳实践
│   │   ├── 01-Prompt设计模式.md
│   │   ├── 02-RAG系统优化.md
│   │   ├── 03-Agent设计原则.md
│   │   ├── 04-生产环境检查清单.md
│   │   ├── 05-性能优化指南.md
│   │   └── 06-成本控制策略.md
│   └── 06-案例研究/                        # 案例研究
│       ├── 01-智能客服系统案例.md
│       ├── 02-代码助手案例.md
│       ├── 03-数据分析Agent案例.md
│       └── 04-文档问答系统案例.md
├── projects/                              # 实践项目（英文）
│   ├── 00-python-fundamentals/           # Python 基础强化
│   │   ├── 01-async-programming/         # 异步编程
│   │   ├── 02-decorators/                # 装饰器
│   │   ├── 03-type-annotations/          # 类型注解
│   │   ├── 04-error-handling/            # 错误处理
│   │   └── 05-context-managers/          # 上下文管理器
│   ├── 01-langchain-basics/              # LLM基础调用
│   │   └── src/
│   │       ├── basic_llm.py
│   │       ├── 01_prompt_templates.py     # 提示词模板
│   │       ├── 02_chains.py              # Chain链式组合
│   │       ├── 03_streaming.py           # 流式输出
│   │       ├── 04_output_parsers.py      # 输出解析器
│   │       ├── 05_callbacks.py           # 回调系统
│   │       ├── 06_model_comparison.py    # 模型对比
│   │       ├── 07_error_handling.py      # 错误处理
│   │       └── 08_complete_example.py    # 完整应用
│   ├── 02-langchain-chatbot/             # 聊天机器人
│   │   └── src/
│   │       ├── simple_chatbot.py
│   │       ├── 01_memory_management.py   # 记忆管理
│   │       ├── 02_conversation_buffer.py # 对话缓冲区
│   │       ├── 03_multi_turn_chat.py     # 多轮对话
│   │       ├── 04_context_window.py      # 上下文窗口
│   │       ├── 05_conversation_summary.py# 对话摘要
│   │       ├── 06_streaming_chat.py      # 流式输出
│   │       ├── 07_web_interface.py       # Web界面(Streamlit)
│   │       ├── 08_chat_history.py        # 历史持久化
│   │       └── 09_complete_chatbot.py    # 完整系统
│   ├── 03-langchain-tools/               # 工具调用
│   │   └── src/
│   │       ├── 01_tool_basics.py         # 工具基础
│   │       ├── 02_search_tools.py        # 搜索工具
│   │       ├── 03_calculator_tools.py    # 计算器工具
│   │       ├── 04_database_tools.py      # 数据库工具
│   │       ├── 05_api_tools.py           # API工具
│   │       ├── 06_file_tools.py          # 文件工具
│   │       ├── 07_tool_validation.py     # 工具验证
│   │       ├── 08_custom_tools.py        # 自定义工具
│   │       ├── 09_tool_composition.py    # 工具组合
│   │       └── 10_complete_tool_system.py# 完整工具系统
│   ├── 04-langchain-rag/                 # RAG检索增强生成
│   │   └── src/
│   │       ├── simple_rag.py
│   │       ├── 01_document_loaders.py    # 文档加载器
│   │       ├── 02_text_splitting.py      # 文本分块
│   │       ├── 03_embeddings.py          # 向量嵌入
│   │       ├── 04_vector_stores.py       # 向量存储
│   │       ├── 05_retrieval_strategies.py# 检索策略
│   │       ├── 06_qa_chain.py            # 问答链
│   │       ├── 07_source_citation.py     # 来源引用
│   │       ├── 08_rag_evaluation.py      # RAG评估
│   │       ├── 09_advanced_rag.py        # 高级RAG
│   │       └── 10_complete_rag_system.py # 完整RAG系统
│   ├── 05-langchain-agents/              # 智能代理
│   │   └── src/
│   │       ├── simple_agent.py
│   │       ├── 01_react_agent.py          # ReAct Agent
│   │       ├── 02_openai_functions_agent.py # OpenAI Functions
│   │       ├── 03_structured_chat_agent.py  # 结构化对话
│   │       ├── 04_conversational_agent.py   # 对话Agent
│   │       ├── 05_custom_agent.py         # 自定义Agent
│   │       ├── 06_agent_memory.py         # Agent记忆
│   │       ├── 08_agent_debugging.py      # Agent调试
│   │       └── 09_multi_agent_basics.py   # 多Agent基础
│   ├── 06-prompt-engineering/            # Prompt 工程
│   │   ├── 01-basic-patterns/            # 基础Prompt模式
│   │   │   └── src/
│   │   │       ├── zero_shot.py          # 零样本模式
│   │   │       ├── few_shot.py           # 少样本模式
│   │   │       ├── role_playing.py       # 角色扮演模式
│   │   │       └── chain_of_thought.py   # 思维链模式
│   │   ├── 02-few-shot-learning/         # Few-shot学习
│   │   ├── 03-chain-of-thought/          # 思维链推理
│   │   ├── 04-output-formatting/         # 输出格式控制
│   │   ├── 05-prompt-optimizer/          # Prompt优化器
│   │   ├── 06-security/                  # 安全防护
│   │   └── templates/                    # Prompt模板库
│   ├── 07-advanced-rag/                  # 高级 RAG
│   │   ├── 01-document-loaders/          # 文档加载器
│   │   │   └── src/
│   │   │       ├── pdf_loader.py         # PDF加载
│   │   │       ├── word_loader.py        # Word文档加载
│   │   │       ├── markdown_loader.py    # Markdown加载
│   │   │       ├── html_loader.py        # HTML加载
│   │   │       └── universal_loader.py   # 统一加载器
│   │   ├── 02-chunking-strategies/       # 分块策略
│   │   ├── 03-embedding-comparison/      # Embedding对比
│   │   ├── 04-vector-databases/          # 向量数据库
│   │   ├── 05-retrieval-strategies/      # 检索策略
│   │   ├── 06-evaluation/                # RAG评估
│   │   ├── 07-hybrid-search/             # 混合检索
│   │   └── 08-production-rag/            # 生产级系统
│   ├── 08-agent-architecture/            # Agent 架构
│   │   ├── 01-react-agent/               # ReAct Agent
│   │   ├── 02-planning-agent/            # 规划Agent
│   │   ├── 03-memory-systems/            # 记忆系统
│   │   ├── 04-tool-calling/              # 工具调用
│   │   ├── 05-agent-debugging/           # Agent调试
│   │   ├── 06-custom-agent/              # 自定义Agent
│   │   └── 07-agent-evaluation/          # Agent评估
│   ├── 09-multi-agent/                   # 多 Agent 系统
│   │   ├── 01-sequential-agents/         # 顺序协作
│   │   ├── 02-parallel-agents/           # 并行协作
│   │   ├── 03-hierarchical-agents/       # 层级协作
│   │   ├── 04-debate-agents/             # 辩论协作
│   │   ├── 05-research-team/             # 研究团队
│   │   ├── 06-code-review-team/          # 代码审查团队
│   │   └── 07-autonomous-team/           # 自主协作团队
│   ├── 10-production-grade/              # 生产级开发
│   │   ├── 01-project-structure/         # 项目结构
│   │   ├── 02-config-management/         # 配置管理
│   │   ├── 03-logging-system/            # 日志系统
│   │   ├── 04-error-handling/            # 错误处理
│   │   ├── 05-retry-circuit-breaker/     # 重试熔断
│   │   ├── 06-caching/                   # 缓存策略
│   │   ├── 07-testing/                   # 测试框架
│   │   ├── 08-api-service/               # API服务
│   │   ├── 09-monitoring/                # 监控指标
│   │   └── 10-cost-optimization/         # 成本优化
│   ├── 11-deployment/                    # 部署
│   │   ├── 01-docker/                    # Docker容器化
│   │   ├── 02-docker-compose/            # Docker Compose编排
│   │   ├── 03-secrets-management/        # 密钥管理
│   │   ├── 04-ci-cd/                     # CI/CD流水线
│   │   ├── 05-cloud-deployment/          # 云平台部署
│   │   ├── 06-serverless/                # Serverless部署
│   │   └── 07-nginx-config/              # Nginx配置
│   └── 12-operations/                    # 运维监控
│       ├── 01-monitoring/               # Prometheus+Grafana监控
│       ├── 02-logging/                  # ELK日志系统
│       ├── 03-tracing/                  # Jaeger分布式追踪
│       ├── 04-alerting/                 # AlertManager告警
│       ├── 05-performance/              # 性能测试优化
│       ├── 06-backup/                   # 备份恢复
│       └── 07-rate-limiting/            # 速率限制
└── README.md                             # 项目说明
```

> 📖 **知识图谱导航**：查看 [docs/知识图谱.md](docs/知识图谱.md) 获取完整的学习路径和文档双链链接

---

## 📖 完整学习路径

### 第一阶段：基础能力（2-3周）

#### 00. Python 基础强化
**目标**：掌握 AI 开发必备的 Python 高级特性

| 项目 | 学习内容 |
|------|---------|
| 00-python-fundamentals | 异步编程、装饰器、类型注解、错误处理、上下文管理器 |

#### 01-05. LangChain 核心技术
**目标**：掌握 LangChain 的基础使用

| 序号 | 教程 | 项目 | 核心功能 |
|------|------|------|---------|
| 01 | 基础入门教程 | 01-langchain-basics | LLM调用、提示词模板、Chain、流式输出、输出解析器、回调系统 |
| 02 | 聊天机器人教程 | 02-langchain-chatbot | 对话历史、多轮对话、记忆管理、流式输出、Web界面、历史持久化 |
| 03 | 工具调用教程 | 03-langchain-tools | 工具定义、工具调用、搜索工具、计算器工具、数据库工具、API工具 |
| 04 | RAG教程 | 04-langchain-rag | 文档加载、文本分块、向量嵌入、向量存储、检索策略、问答链 |
| 05 | Agent教程 | 05-langchain-agents | ReAct模式、OpenAI Functions、结构化对话、自定义Agent、Agent记忆、多Agent基础 |

---

### 第二阶段：核心技能（3-4周）

#### 06. Prompt 工程
**目标**：掌握与 AI 有效沟通的艺术

**学习内容**：
- Prompt 设计原则和模式
- Zero-shot、Few-shot、Chain-of-Thought
- 输出格式控制（JSON、XML）
- Prompt 优化和安全防护

**项目模块**：
- **01-basic-patterns**: Zero-shot、Few-shot、角色扮演、Chain-of-Thought
- **02-few-shot-learning**: 细粒度情感分析、意图识别、多标签分类
- **03-chain-of-thought**: 数学应用题、算法分析、战略规划
- **04-output-formatting**: JSON/表格/代码格式输出控制
- **05-prompt-optimizer**: Prompt 分析、优化、测试、对比
- **06-security**: 输入验证、注入检测、安全防护
- **templates**: 常用 Prompt 模板库

#### 07. 高级 RAG
**目标**：构建生产级知识问答系统

**学习内容**：
- 文档处理和分块策略
- Embedding 模型选择
- 向量数据库对比
- 检索策略优化（MMR、混合检索、重排序）
- RAG 评估和高级技术（HyDE、Self-RAG、RAPTOR）

**项目模块**：
- **01-document-loaders**: PDF/Word/Markdown/HTML 加载器、统一接口
- **02-chunking-strategies**: 固定大小、语义、递归分块策略对比
- **03-embedding-comparison**: BGE-Small/Base/Large 模型对比
- **04-vector-databases**: FAISS、ChromaDB 向量存储
- **05-retrieval-strategies**: 相似度搜索、MMR、多查询检索
- **06-evaluation**: Precision、Recall、F1、MRR、NDCG 评估指标
- **07-hybrid-search**: 向量+BM25 混合检索
- **08-production-rag**: 完整端到端生产级 RAG 系统

---

### 第三阶段：架构设计（3-4周）

#### 08. Agent 架构
**目标**：设计和实现智能 Agent

**学习内容**：
- Agent 核心组件（推理、记忆、工具、规划）
- ReAct、Plan-and-Execute 模式
- 记忆系统设计
- 工具系统和任务规划
- Agent 调试和评估

**项目模块**：
- **01-react-agent**: ReAct（Reasoning + Acting）模式实现
- **02-planning-agent**: 基于规划的 Agent，支持目标分解
- **03-memory-systems**: 短期记忆、长期记忆、情景记忆
- **04-tool-calling**: 工具/函数调用模式
- **05-agent-debugging**: Agent 行为调试和追踪
- **06-custom-agent**: 自定义 Agent 架构构建
- **07-agent-evaluation**: Agent 性能评估

#### 09. 多 Agent 系统
**目标**：构建协作 Agent 团队

**学习内容**：
- 多 Agent 协作模式
- Agent 通信机制
- 任务分配和调度
- 共享记忆管理
- AutoGen、CrewAI 框架

**项目模块**：
- **01-sequential-agents**: 顺序 Agent 链
- **02-parallel-agents**: 并行 Agent 执行
- **03-hierarchical-agents**: 管理者-工作者层级架构
- **04-debate-agents**: 多 Agent 辩论和共识达成
- **05-research-team**: 研究团队模拟
- **06-code-review-team**: 代码审查 Agent 团队
- **07-autonomous-team**: 自组织 Agent 团队（AutoGen、CrewAI）

---

### 第四阶段：工程化（4-5周）

#### 10. 生产级开发
**目标**：将原型转变为生产应用

**学习内容**：
- 标准项目结构
- 配置管理和环境隔离
- 日志、监控和追踪
- 错误处理、重试、熔断
- 测试和质量保证
- API 服务设计
- 性能优化和成本控制

**项目模块**：
- **01-project-structure**: 专业项目组织结构
- **02-config-management**: 配置和设置管理
- **03-logging-system**: 结构化日志和监控
- **04-error-handling**: 健壮的错误处理和恢复
- **05-retry-circuit-breaker**: 重试逻辑和熔断
- **06-caching**: 缓存策略优化性能
- **07-testing**: 单元、集成、端到端测试
- **08-api-service**: RESTful API 服务实现
- **09-monitoring**: 指标、追踪和可观测性
- **10-cost-optimization**: 成本追踪和优化

#### 11. 部署
**目标**：安全可靠地部署到生产环境

**学习内容**：
- Docker 容器化
- CI/CD 流程
- 密钥管理
- 云平台部署（AWS、GCP、Azure、阿里云）
- Serverless 部署
- 负载均衡和高可用

**项目模块**：
- **01-docker**: Docker 容器化（Dockerfile、多阶段构建）
- **02-docker-compose**: Docker Compose 编排（开发/生产环境）
- **03-secrets-management**: 密钥管理（K8s Secrets、云密钥服务）
- **04-ci-cd**: CI/CD 流水线（GitHub Actions、GitLab CI）
- **05-cloud-deployment**: 云平台部署（AWS ECS、GCP Cloud Run、Azure、阿里云）
- **06-serverless**: Serverless 部署（AWS Lambda）
- **07-nginx-config**: Nginx 负载均衡配置

#### 12. 运维监控
**目标**：保障系统稳定运行

**学习内容**：
- 应用监控（Prometheus、Grafana）
- 日志聚合（ELK）
- 链路追踪
- 告警系统
- 性能分析和优化
- 备份恢复、限流

**项目模块**：
- **01-monitoring**: Prometheus + Grafana 监控（指标收集、仪表板）
- **02-logging**: ELK 日志系统（Filebeat、Logstash、Kibana）
- **03-tracing**: Jaeger 分布式追踪（OpenTelemetry）
- **04-alerting**: AlertManager 告警（多渠道通知）
- **05-performance**: 性能测试和优化（Locust、性能分析）
- **06-backup**: 备份和恢复（自动化备份脚本）
- **07-rate-limiting**: 速率限制（令牌桶、Redis 分布式限流）

---

## 🎯 学习建议

### 推荐路径

```
第1-2周：Python 基础 + LangChain 入门（00-02）
第3-4周：工具调用 + RAG（03-04）
第5-6周：Agent + Prompt 工程（05-06）
第7-9周：高级 RAG + Agent 架构（07-08）
第10-12周：多 Agent 系统（09）
第13-15周：生产级开发（10）
第16-18周：部署 + 运维（11-12）
```

### 学习方法

1. **先理论后实践**：先看教程理解概念，再动手做项目
2. **循序渐进**：按编号顺序学习，不要跳过基础
3. **边学边记**：记录关键概念和遇到的问题
4. **多实验**：尝试修改参数，观察效果变化
5. **查看案例**：参考最佳实践和案例研究
6. **构建项目**：用学到的知识构建自己的项目

---

## 🔧 环境配置

### 安装依赖

```bash
# 基础依赖
pip install langchain langchain-openai langchain-community python-dotenv

# RAG 相关
pip install faiss-cpu chromadb sentence-transformers

# 生产环境
pip install fastapi uvicorn redis prometheus-client sentry-sdk

# 开发工具
pip install pytest pytest-cov black flake8
```

### 配置 API Key

在每个项目目录下创建 `.env` 文件：

```env
# DeepSeek API 配置（推荐，性价比高）
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash

# 或使用 OpenAI
# OPENAI_API_KEY=your-api-key-here
# OPENAI_MODEL=gpt-4

# 或使用 Claude
# ANTHROPIC_API_KEY=your-api-key-here
# ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**获取 API Key：**
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/
- Claude: https://console.anthropic.com/

---

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

---

## 📚 文档导航

### 教程文档（docs/02-教程/）

| 序号 | 教程文档 | 对应项目 | 难度 | 预计时间 |
|------|----------|----------|------|---------|
| 00 | LangChain入门教程 | 00-python-fundamentals | ⭐ | 2小时 |
| 01 | 基础入门教程 | 01-langchain-basics | ⭐ | 3小时 |
| 02 | 聊天机器人教程 | 02-langchain-chatbot | ⭐⭐ | 3小时 |
| 03 | 工具调用教程 | 03-langchain-tools | ⭐⭐ | 4小时 |
| 04 | RAG教程 | 04-langchain-rag | ⭐⭐⭐ | 5小时 |
| 05 | Agent教程 | 05-langchain-agents | ⭐⭐⭐ | 5小时 |
| 06 | Prompt工程教程 | 06-prompt-engineering | ⭐⭐ | 4小时 |
| 07 | 高级RAG教程 | 07-advanced-rag | ⭐⭐⭐⭐ | 8小时 |
| 08 | Agent架构教程 | 08-agent-architecture | ⭐⭐⭐⭐ | 8小时 |
| 09 | 多Agent系统教程 | 09-multi-agent | ⭐⭐⭐⭐⭐ | 10小时 |
| 10 | 生产级开发教程 | 10-production-grade | ⭐⭐⭐⭐ | 8小时 |
| 11 | 部署教程 | 11-deployment | ⭐⭐⭐ | 6小时 |
| 12 | 运维监控教程 | 12-operations | ⭐⭐⭐ | 6小时 |

### 最佳实践（docs/05-最佳实践/）

- **01-Prompt设计模式** - 常用 Prompt 模式和技巧
- **02-RAG系统优化** - RAG 系统性能优化
- **03-Agent设计原则** - Agent 设计核心原则
- **04-生产环境检查清单** - 上线前必查项
- **05-性能优化指南** - 性能优化技巧
- **06-成本控制策略** - Token 和资源成本控制

### 案例研究（docs/06-案例研究/）

- **01-智能客服系统案例** - 完整的客服系统实现
- **02-代码助手案例** - AI 代码助手
- **03-数据分析Agent案例** - 数据分析自动化
- **04-文档问答系统案例** - 企业知识库问答

### 🗺️ 知识图谱导航

建议从 [知识图谱](docs/知识图谱.md) 开始，了解完整的学习路径和文档间的双链链接关系。

---

## 💡 项目亮点

### 1. 完整的知识体系
从 Python 基础到生产部署，覆盖 AI Agent 开发的所有环节。

### 2. 实战导向
每个教程都配有完整的代码项目，边学边练。

### 3. 生产级实践
不仅教你做原型，更教你如何构建可靠的生产系统。

### 4. 最佳实践总结
汇总行业经验和常见问题解决方案。

### 5. 案例驱动
通过真实案例学习如何解决实际问题。

---

## ⚠️ 注意事项

1. **API Key 安全**：不要将 `.env` 文件提交到版本控制
2. **成本控制**：注意 API 调用的费用，建议使用 DeepSeek（性价比高）
3. **网络环境**：确保网络能够访问 API 服务
4. **依赖版本**：建议使用最新版本的依赖包
5. **循序渐进**：建议按编号顺序学习，不要跳过基础内容

---

## 🤝 贡献

欢迎提交问题、建议和改进！

- 提交 Issue：报告问题或建议
- 提交 PR：改进文档或代码
- 分享经验：在 Discussions 中分享你的学习心得

---

## 📄 许可证

MIT License

---

## 🌟 致谢

感谢 LangChain、OpenAI、DeepSeek 等开源社区和公司的贡献。

---

**开始您的 AI Agent 学习之旅吧！🚀**

从零基础到生产部署，成为 AI Agent 开发专家！
