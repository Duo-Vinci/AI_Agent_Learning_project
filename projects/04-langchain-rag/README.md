# LangChain RAG

检索增强生成项目，演示如何基于自定义文档进行问答。

## 学习目标

- 理解 RAG 的概念和原理
- 学习如何构建向量数据库
- 掌握文档检索和问答的流程

## 运行步骤

```bash
# 安装依赖
pip install langchain langchain-openai python-dotenv faiss-cpu

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 添加您的 API Key

# 创建文档目录并添加文档
mkdir -p documents
# 在 documents 目录下创建知识文档

# 运行脚本
python src/simple_rag.py
```

## 文件结构

```
04-langchain-rag/
├── src/
│   └── simple_rag.py      # 主脚本
├── documents/             # 文档目录
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 相关教程

- 对应教程：`docs/02-教程/04-RAG教程.md`

## 核心流程

1. 文档准备 → 分割 → 向量化 → 存储到向量数据库
2. 用户提问 → 向量化 → 检索相似文档 → 生成回答

## 注意事项

- 文档质量直接影响回答质量
- 注意选择合适的嵌入模型