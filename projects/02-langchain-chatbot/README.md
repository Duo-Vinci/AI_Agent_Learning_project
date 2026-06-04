# LangChain Chatbot

聊天机器人项目，演示如何实现多轮对话和上下文保持。

## 学习目标

- 理解对话历史机制
- 掌握多轮对话实现
- 学习消息类型的使用

## 运行步骤

```bash
# 安装依赖
pip install langchain langchain-openai python-dotenv

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 添加您的 API Key

# 运行脚本
python src/simple_chatbot.py
```

## 文件结构

```
02-langchain-chatbot/
├── src/
│   └── simple_chatbot.py  # 主脚本
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 相关教程

- 对应教程：`docs/02-教程/02-聊天机器人教程.md`

## 核心概念

大语言模型本身没有记忆能力，每次对话需要发送完整的对话历史：

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是一个友好的聊天机器人。"),
    HumanMessage(content="你好"),
    AIMessage(content="你好！有什么我可以帮你的吗？")
]
```

## 注意事项

- 每次对话会发送完整历史，注意 Token 消耗
- 支持 exit 命令退出对话