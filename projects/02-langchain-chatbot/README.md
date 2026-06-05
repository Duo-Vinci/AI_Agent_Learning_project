# LangChain 聊天机器人项目

完整的聊天机器人实现，从基础到高级，涵盖记忆管理、流式输出、历史持久化等功能。

## 项目概述

本项目包含10个渐进式示例，展示如何使用LangChain构建生产级聊天机器人：

- **01-06**: 核心功能（记忆、多轮对话、上下文管理、流式输出）
- **07**: Web界面（Streamlit）
- **08**: 历史持久化（JSON/SQLite）
- **09**: 完整系统集成
- **quickstart**: 快速入门

## 学习目标

- ✅ 理解对话记忆机制（Buffer、Window、Summary、Token Buffer）
- ✅ 掌握多轮对话与上下文管理
- ✅ 实现流式输出与打字机效果
- ✅ 学习对话历史持久化（JSON/SQLite）
- ✅ 构建Web聊天界面
- ✅ 会话管理与多用户隔离
- ✅ 生产级错误处理与配置管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加您的 API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 运行快速入门

```bash
# 最快速的入门体验
python src/quickstart.py

# 或运行完整聊天机器人
python src/09_complete_chatbot.py
```

## 文件结构

```
02-langchain-chatbot/
├── src/
│   ├── 01_memory_management.py      # 记忆管理基础（400行）
│   ├── 02_conversation_buffer.py    # 对话缓冲区（450行）
│   ├── 03_multi_turn_chat.py        # 多轮对话（520行）
│   ├── 04_context_window.py         # 上下文窗口管理（480行）
│   ├── 05_conversation_summary.py   # 对话摘要（420行）
│   ├── 06_streaming_chat.py         # 流式输出（450行）
│   ├── 07_web_interface.py          # Web界面（727行）
│   ├── 08_chat_history.py           # 历史持久化（850行）
│   ├── 09_complete_chatbot.py       # 完整系统（750行）
│   ├── quickstart.py                # 快速入门（200行）
│   └── simple_chatbot.py            # 简单示例
├── tests/                           # 测试文件
├── chat_data/                       # 数据存储目录（自动创建）
├── .env.example                     # 环境变量模板
├── requirements.txt                 # 依赖列表
└── README.md                        # 本文件
```

## 各文件说明

### 01_memory_management.py
**对话记忆管理基础**
- 基本对话记忆
- 对话历史管理
- 会话窗口限制
- 对话摘要
- 持久化对话历史

```bash
python src/01_memory_management.py
```

### 02_conversation_buffer.py
**对话缓冲区实现**
- ConversationBufferMemory
- 完整历史保留
- 消息格式化
- 历史查询与过滤

```bash
python src/02_conversation_buffer.py
```

### 03_multi_turn_chat.py
**多轮对话系统**
- 上下文保持
- 多轮推理
- 话题切换
- 对话状态管理

```bash
python src/03_multi_turn_chat.py
```

### 04_context_window.py
**上下文窗口管理**
- 滑动窗口策略
- Token限制管理
- 自动截断
- 摘要压缩

```bash
python src/04_context_window.py
```

### 05_conversation_summary.py
**对话摘要功能**
- 自动摘要生成
- 渐进式摘要
- 长期记忆保持
- Token优化

```bash
python src/05_conversation_summary.py
```

### 06_streaming_chat.py
**流式输出实现**
- 实时Token流
- 打字机效果
- 流式回调
- 性能监控

```bash
python src/06_streaming_chat.py
```

### 07_web_interface.py
**Streamlit Web界面**
- 现代化聊天UI
- 会话管理
- 历史展示
- 配置界面

```bash
streamlit run src/07_web_interface.py
```

### 08_chat_history.py
**对话历史持久化**
- JSON文件存储
- SQLite数据库
- 会话管理器
- 导出导入功能
- 统计分析

```bash
python src/08_chat_history.py
```

### 09_complete_chatbot.py
**完整聊天机器人系统**
- 集成所有功能
- 配置管理
- 命令系统
- 多记忆策略
- 错误处理
- 生产级实现

```bash
python src/09_complete_chatbot.py
```

**支持的命令**：
- `/help` - 显示帮助
- `/clear` - 清除历史
- `/stats` - 显示统计
- `/config` - 查看配置
- `/memory [type]` - 切换记忆类型
- `/exit` - 退出

### quickstart.py
**快速入门指南**
- 5分钟上手
- 4个渐进示例
- 交互式聊天
- 最佳实践

```bash
python src/quickstart.py
```

## 核心概念

### 1. 对话记忆类型

```python
# Buffer Memory - 保留完整历史
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()

# Window Memory - 保留最近N轮
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=5)

# Summary Memory - 自动摘要
from langchain.memory import ConversationSummaryMemory
memory = ConversationSummaryMemory(llm=llm)

# Token Buffer - 基于Token限制
from langchain.memory import ConversationTokenBufferMemory
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=2000)
```

### 2. 消息类型

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是一个友好的助手"),
    HumanMessage(content="你好"),
    AIMessage(content="你好！有什么可以帮你的吗？")
]
```

### 3. 流式输出

```python
from langchain_core.callbacks import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(token, end="", flush=True)

llm = ChatOpenAI(streaming=True, callbacks=[StreamHandler()])
```

### 4. 历史持久化

```python
# SQLite 存储
from sqlite3 import connect

conn = connect("chat_history.db")
# 存储和检索对话历史
```

## 使用场景

1. **客服机器人** - 多轮对话，上下文理解
2. **个人助手** - 长期记忆，个性化服务
3. **教育辅导** - 渐进式对话，知识追踪
4. **技术支持** - 问题诊断，解决方案推荐
5. **内容创作** - 互动式写作，灵感激发

## 高级功能

### 配置管理

```python
# 修改配置
from complete_chatbot import ChatbotConfig

config = ChatbotConfig()
config.set("model.temperature", 0.9)
config.set("memory.type", "buffer_window")
config.set("memory.window_size", 10)
```

### 会话管理

```python
# 多用户会话隔离
from complete_chatbot import SessionManager

manager = SessionManager("chat.db")
session1 = manager.create_session("session_001", "user_alice")
session2 = manager.create_session("session_002", "user_bob")
```

### 历史导出

```python
# 导出为 JSON/Markdown
from chat_history import ChatHistoryExporter

exporter = ChatHistoryExporter()
exporter.export_to_json(history, "conversation.json")
exporter.export_to_markdown(history, "conversation.md")
```

## 性能优化

1. **Token管理** - 使用窗口或摘要减少Token消耗
2. **流式输出** - 提升用户体验，降低等待时间
3. **异步处理** - 提高并发处理能力
4. **缓存策略** - 减少重复请求

## 常见问题

### Q: 如何限制对话历史长度？

使用 `ConversationBufferWindowMemory` 或 `ConversationTokenBufferMemory`：

```python
# 保留最近5轮对话
memory = ConversationBufferWindowMemory(k=5)

# 限制为2000 tokens
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=2000)
```

### Q: 如何持久化对话历史？

使用 `08_chat_history.py` 中的 `SQLiteChatHistory`：

```python
from chat_history import SQLiteChatHistory

history = SQLiteChatHistory("chat.db", "session_001")
history.add_message(HumanMessage(content="你好"))
```

### Q: 如何实现流式输出？

设置 `streaming=True` 并添加回调：

```python
llm = ChatOpenAI(
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)
```

### Q: 如何切换不同的记忆策略？

在完整聊天机器人中使用 `/memory` 命令：

```bash
/memory buffer_window
/memory token_buffer
```

## 注意事项

- ⚠️ 每次对话会发送完整历史，注意Token消耗
- ⚠️ SQLite适合中小规模应用，大规模请使用PostgreSQL等
- ⚠️ 流式输出需要网络稳定，否则可能中断
- ⚠️ 定期清理过期会话，避免数据库膨胀
- ✅ 建议使用环境变量管理API密钥
- ✅ 生产环境请添加错误重试机制
- ✅ 实现速率限制，避免API超限

## 相关教程

- 对应教程：`docs/02-教程/02-聊天机器人教程.md`
- LangChain官方文档：https://python.langchain.com/docs/

## 下一步

完成本项目后，可以继续学习：

- **项目03**: LangChain工具使用（Tool Calling）
- **项目04**: RAG检索增强生成
- **项目05**: Agent自主代理系统

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License