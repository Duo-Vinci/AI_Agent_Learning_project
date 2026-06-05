# 多Agent系统项目

完整的多Agent协作系统实现，涵盖从基础协作模式到高级框架应用。

## 项目结构

```
09-multi-agent/
├── 01-sequential-agents/      # 顺序协作模式
│   └── src/
│       ├── agents.py          # 研究员、写作者、编辑Agent
│       └── workflow.py        # 顺序工作流实现
│
├── 02-parallel-agents/        # 并行协作模式
│   └── src/
│       ├── agents.py          # 情感分析、关键词提取等Agent
│       └── workflow.py        # 并行分析工作流
│
├── 03-hierarchical-agents/    # 层级协作模式
│   └── src/
│       ├── agents.py          # Manager-Worker模式实现
│       └── workflow.py        # 层级协作工作流
│
├── 04-debate-agents/          # 辩论协作模式
│   └── src/
│       ├── agents.py          # 辩论者、裁判、调解员Agent
│       └── workflow.py        # 辩论工作流
│
├── 05-research-team/          # 通信机制示例
│   └── src/
│       ├── communication.py   # 消息总线、通信Agent
│       └── workflow.py        # 基于消息的协作
│
├── 06-code-review-team/       # 共享记忆示例
│   └── src/
│       ├── shared_memory.py   # 共享记忆管理
│       └── workflow.py        # 代码审查工作流
│
├── 07-autonomous-team/        # 框架示例
│   └── src/
│       ├── autogen_example.py # AutoGen框架示例
│       ├── crewai_example.py  # CrewAI框架示例
│       └── main.py           # 主入口
│
├── requirements.txt           # 项目依赖
└── README.md                 # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd projects/09-multi-agent

# 安装核心依赖
pip install -r requirements.txt

# 可选：安装框架（根据需要）
pip install autogen-agentchat  # AutoGen框架
pip install crewai crewai-tools  # CrewAI框架
```

### 2. 配置环境

创建 `.env` 文件并设置API密钥：

```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. 运行示例

```bash
# 顺序协作
python 01-sequential-agents/src/workflow.py

# 并行协作
python 02-parallel-agents/src/workflow.py

# 层级协作
python 03-hierarchical-agents/src/workflow.py

# 辩论模式
python 04-debate-agents/src/workflow.py

# 通信机制
python 05-research-team/src/workflow.py

# 共享记忆
python 06-code-review-team/src/workflow.py

# AutoGen框架
python 07-autonomous-team/src/autogen_example.py

# CrewAI框架
python 07-autonomous-team/src/crewai_example.py
```

## 核心概念

### 1. 顺序协作（Sequential）

**特点**：Agent按照预定顺序依次执行任务，前一个Agent的输出作为下一个Agent的输入。

**适用场景**：
- 内容创作流程（研究 → 写作 → 编辑）
- 数据处理管道
- 需要逐步细化的任务

**示例**：
```python
# 研究员收集信息
research_result = researcher.research(topic)

# 写作者基于研究创作
draft = writer.write(research_result)

# 编辑审查和优化
final_article = editor.edit(draft)
```

### 2. 并行协作（Parallel）

**特点**：多个Agent同时处理同一任务的不同方面，最后聚合结果。

**适用场景**：
- 多维度分析（情感、关键词、实体识别）
- 需要快速响应的场景
- 独立的子任务处理

**示例**：
```python
# 多个Agent并行分析
results = await asyncio.gather(
    sentiment_agent.analyze(text),
    keyword_agent.extract(text),
    summary_agent.summarize(text)
)

# 聚合结果
final_report = aggregator.aggregate(results)
```

### 3. 层级协作（Hierarchical）

**特点**：Manager负责任务分解和分配，Worker执行具体任务。

**适用场景**：
- 复杂项目管理
- 需要任务分配的场景
- 团队协作模拟

**示例**：
```python
# Manager分解任务
subtasks = manager.decompose_task(main_task)

# 分配给Worker
assignments = manager.assign_tasks(subtasks)

# Worker执行并返回结果
results = [worker.execute(task) for worker, task in assignments]

# Manager整合结果
final_result = manager.integrate_results(results)
```

### 4. 辩论协作（Debate）

**特点**：多个Agent代表不同立场进行辩论，裁判评估并做出判定。

**适用场景**：
- 决策支持
- 多角度问题分析
- 风险评估

**示例**：
```python
# 多轮辩论
for round in range(rounds):
    pro_arg = agent_pro.argue(topic, con_arguments)
    con_arg = agent_con.argue(topic, pro_arguments)

# 裁判评估
evaluation = judge.evaluate(topic, all_arguments)
```

### 5. 通信机制（Communication）

**特点**：通过消息总线实现Agent间的异步通信。

**核心组件**：
- MessageBus：消息总线
- Message：消息对象
- CommunicatingAgent：支持通信的Agent

**示例**：
```python
# 创建消息总线
bus = MessageBus()

# Agent注册
agent1 = CommunicatingAgent("Agent1", bus)
agent2 = CommunicatingAgent("Agent2", bus)

# 发送消息
agent1.send_to("Agent2", MessageType.TASK, "执行任务X")

# 接收消息
message = agent2.receive(timeout=5.0)

# 处理并响应
result = agent2.process_message(message)
agent2.send_to("Agent1", MessageType.RESULT, result)
```

### 6. 共享记忆（Shared Memory）

**特点**：多个Agent共享知识库和上下文。

**核心组件**：
- SharedMemory：共享记忆空间
- Facts：事实性知识
- Context：对话上下文
- Decisions：决策历史

**示例**：
```python
# 创建共享记忆
memory = SharedMemory()

# Agent添加知识
agent1.contribute_knowledge("key", "value", confidence=0.9)

# 其他Agent查询
value = agent2.query_knowledge("key")

# 基于共享记忆协作
result = agent3.collaborate_with_memory(task)
```

## 框架对比

### AutoGen

**优势**：
- 支持代码执行
- 灵活的Agent配置
- 强大的对话管理

**适用场景**：
- 编程助手
- 代码生成和调试
- 需要工具调用的场景

### CrewAI

**优势**：
- 简单易用
- 角色和任务清晰
- 内置任务编排

**适用场景**：
- 内容创作
- 研究团队
- 业务流程自动化

## 最佳实践

### 1. 设计原则

- **单一职责**：每个Agent专注一个明确的任务
- **松耦合**：Agent间通过消息或共享记忆通信
- **可扩展**：易于添加新Agent
- **容错性**：处理Agent失败的情况

### 2. 性能优化

- **并行化**：独立任务使用异步并行执行
- **缓存**：缓存重复的LLM调用结果
- **超时控制**：设置合理的超时时间
- **资源管理**：限制并发Agent数量

### 3. 调试技巧

- **日志记录**：记录所有Agent交互
- **可视化**：可视化Agent协作流程
- **单元测试**：测试单个Agent的行为
- **集成测试**：测试整个工作流

### 4. 常见问题

**Q: Agent响应慢怎么办？**
A: 使用并行执行、减少LLM调用、使用更快的模型。

**Q: 如何处理Agent冲突？**
A: 引入仲裁机制、优先级设置、投票机制。

**Q: 共享记忆占用太多内存？**
A: 设置最大条数限制、定期清理、使用向量数据库。

**Q: Agent给出错误结果？**
A: 增加验证步骤、使用多Agent投票、引入审查机制。

## 扩展阅读

- [AutoGen文档](https://microsoft.github.io/autogen/)
- [CrewAI文档](https://docs.crewai.com/)
- [LangChain文档](https://python.langchain.com/)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)

## 贡献指南

欢迎贡献新的协作模式或改进现有实现：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 许可证

本项目仅用于学习目的。

## 联系方式

如有问题或建议，请创建Issue。
