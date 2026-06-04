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
│   ├── 01-学习笔记/                        # 学习笔记和指南
│   │   ├── 入门指南.md
│   │   └── 环境变量指南.md
│   ├── 02-教程/                            # 完整教程（按顺序学习）
│   │   ├── 00-LangChain入门教程.md
│   │   ├── 01-基础入门教程.md
│   │   ├── 02-聊天机器人教程.md
│   │   ├── 03-工具调用教程.md
│   │   ├── 04-RAG教程.md
│   │   ├── 05-Agent教程.md
│   │   ├── 06-Prompt工程教程.md           # 新增
│   │   ├── 07-高级RAG教程.md              # 新增
│   │   ├── 08-Agent架构教程.md            # 新增
│   │   ├── 09-多Agent系统教程.md          # 新增
│   │   ├── 10-生产级开发教程.md           # 新增
│   │   ├── 11-部署教程.md                 # 新增
│   │   └── 12-运维监控教程.md             # 新增
│   ├── 03-资源链接/                        # 学习资源
│   │   └── 学习资源链接.md
│   ├── 04-速查表/                          # API 速查表
│   │   └── LangChain速查表.md
│   ├── 05-最佳实践/                        # 最佳实践（新增）
│   │   ├── 01-Prompt设计模式.md
│   │   ├── 02-RAG系统优化.md
│   │   ├── 03-Agent设计原则.md
│   │   ├── 04-生产环境检查清单.md
│   │   ├── 05-性能优化指南.md
│   │   └── 06-成本控制策略.md
│   └── 06-案例研究/                        # 案例研究（新增）
│       ├── 01-智能客服系统案例.md
│       ├── 02-代码助手案例.md
│       ├── 03-数据分析Agent案例.md
│       └── 04-文档问答系统案例.md
├── projects/                              # 实践项目（英文）
│   ├── 00-python-fundamentals/           # Python 基础强化（新增）
│   │   ├── 01-async-programming/
│   │   ├── 02-decorators/
│   │   ├── 03-type-annotations/
│   │   ├── 04-error-handling/
│   │   └── 05-context-managers/
│   ├── 01-langchain-basics/              # LLM基础调用
│   ├── 02-langchain-chatbot/             # 聊天机器人
│   ├── 03-langchain-tools/               # 工具调用
│   ├── 04-langchain-rag/                 # RAG检索增强生成
│   ├── 05-langchain-agents/              # 智能代理
│   ├── 06-prompt-engineering/            # Prompt 工程（新增）
│   │   ├── 01-basic-patterns/
│   │   ├── 02-few-shot-learning/
│   │   ├── 03-chain-of-thought/
│   │   ├── 04-output-formatting/
│   │   ├── 05-prompt-optimizer/
│   │   ├── 06-security/
│   │   └── templates/
│   ├── 07-advanced-rag/                  # 高级 RAG（新增）
│   │   ├── 01-document-loaders/
│   │   ├── 02-chunking-strategies/
│   │   ├── 03-embedding-comparison/
│   │   ├── 04-vector-databases/
│   │   ├── 05-retrieval-strategies/
│   │   ├── 06-evaluation/
│   │   ├── 07-hybrid-search/
│   │   └── 08-production-rag/
│   ├── 08-agent-architecture/            # Agent 架构（新增）
│   │   ├── 01-react-agent/
│   │   ├── 02-planning-agent/
│   │   ├── 03-memory-systems/
│   │   ├── 04-tool-calling/
│   │   ├── 05-agent-debugging/
│   │   ├── 06-custom-agent/
│   │   └── 07-agent-evaluation/
│   ├── 09-multi-agent/                   # 多 Agent 系统（新增）
│   │   ├── 01-sequential-agents/
│   │   ├── 02-parallel-agents/
│   │   ├── 03-hierarchical-agents/
│   │   ├── 04-debate-agents/
│   │   ├── 05-research-team/
│   │   ├── 06-code-review-team/
│   │   └── 07-autonomous-team/
│   ├── 10-production-grade/              # 生产级开发（新增）
│   │   ├── 01-project-structure/
│   │   ├── 02-config-management/
│   │   ├── 03-logging-system/
│   │   ├── 04-error-handling/
│   │   ├── 05-retry-circuit-breaker/
│   │   ├── 06-caching/
│   │   ├── 07-testing/
│   │   ├── 08-api-service/
│   │   ├── 09-monitoring/
│   │   └── 10-cost-optimization/
│   ├── 11-deployment/                    # 部署（新增）
│   │   ├── 01-docker/
│   │   ├── 02-docker-compose/
│   │   ├── 03-secrets-management/
│   │   ├── 04-ci-cd/
│   │   ├── 05-cloud-deployment/
│   │   ├── 06-serverless/
│   │   └── 07-nginx-config/
│   └── 12-operations/                    # 运维监控（新增）
│       ├── 01-monitoring/
│       ├── 02-logging/
│       ├── 03-tracing/
│       ├── 04-alerting/
│       ├── 05-performance/
│       ├── 06-backup/
│       └── 07-rate-limiting/
└── README.md                             # 项目说明
```

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
| 01 | 基础入门教程 | 01-langchain-basics | LLM调用、提示词模板、Chain |
| 02 | 聊天机器人教程 | 02-langchain-chatbot | 对话历史、多轮对话 |
| 03 | 工具调用教程 | 03-langchain-tools | 工具定义、工具调用 |
| 04 | RAG教程 | 04-langchain-rag | 向量数据库、文档检索 |
| 05 | Agent教程 | 05-langchain-agents | 智能代理、工具协作 |

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
- 基础模式库、Few-shot 学习
- CoT 推理、输出格式化
- Prompt 优化工具、安全防护

#### 07. 高级 RAG
**目标**：构建生产级知识问答系统

**学习内容**：
- 文档处理和分块策略
- Embedding 模型选择
- 向量数据库对比
- 检索策略优化（MMR、混合检索、重排序）
- RAG 评估和高级技术（HyDE、Self-RAG、RAPTOR）

**项目模块**：
- 文档加载器、分块策略对比
- Embedding 评测、向量数据库
- 检索优化、评估系统、生产级 RAG

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
- ReAct Agent、规划 Agent
- 记忆系统、工具调用
- Agent 调试、自定义 Agent、评估系统

#### 09. 多 Agent 系统
**目标**：构建协作 Agent 团队

**学习内容**：
- 多 Agent 协作模式
- Agent 通信机制
- 任务分配和调度
- 共享记忆管理
- AutoGen、CrewAI 框架

**项目模块**：
- 顺序协作、并行协作、层级管理
- 辩论系统、研究团队
- 代码审查团队、自主协作

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
- 项目模板、配置管理、日志系统
- 错误处理、重试熔断、缓存
- 测试框架、API 服务、监控、成本优化

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
- Docker、Docker Compose
- 密钥管理、CI/CD
- 云平台部署、Serverless、Nginx

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
- 监控系统、日志聚合、链路追踪
- 告警、性能分析、备份、限流

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

| 序号 | 文档 | 难度 | 预计时间 |
|------|------|------|---------|
| 00 | LangChain入门教程 | ⭐ | 2小时 |
| 01 | 基础入门教程 | ⭐ | 3小时 |
| 02 | 聊天机器人教程 | ⭐⭐ | 3小时 |
| 03 | 工具调用教程 | ⭐⭐ | 4小时 |
| 04 | RAG教程 | ⭐⭐⭐ | 5小时 |
| 05 | Agent教程 | ⭐⭐⭐ | 5小时 |
| 06 | Prompt工程教程 | ⭐⭐ | 4小时 |
| 07 | 高级RAG教程 | ⭐⭐⭐⭐ | 8小时 |
| 08 | Agent架构教程 | ⭐⭐⭐⭐ | 8小时 |
| 09 | 多Agent系统教程 | ⭐⭐⭐⭐⭐ | 10小时 |
| 10 | 生产级开发教程 | ⭐⭐⭐⭐ | 8小时 |
| 11 | 部署教程 | ⭐⭐⭐ | 6小时 |
| 12 | 运维监控教程 | ⭐⭐⭐ | 6小时 |

### 最佳实践（docs/05-最佳实践/）

- **Prompt设计模式** - 常用 Prompt 模式和技巧
- **RAG系统优化** - RAG 系统性能优化
- **Agent设计原则** - Agent 设计核心原则
- **生产环境检查清单** - 上线前必查项
- **性能优化指南** - 性能优化技巧
- **成本控制策略** - Token 和资源成本控制

### 案例研究（docs/06-案例研究/）

- **智能客服系统案例** - 完整的客服系统实现
- **代码助手案例** - AI 代码助手
- **数据分析Agent案例** - 数据分析自动化
- **文档问答系统案例** - 企业知识库问答

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
