# LangChain RAG

RAG（检索增强生成）项目，学习如何将外部知识集成到LLM中。

## 学习目标

- 理解 RAG 原理
- 学习向量数据库使用
- 掌握文档加载和检索

## 快速开始

```bash
pip install langchain langchain-openai python-dotenv faiss-cpu
cp .env.example .env
python src/simple_rag.py
```

## 项目结构

```
langchain-rag/
├── src/
│   └── simple_rag.py
├── data/           # 文档数据
├── tests/
├── .env.example
└── README.md
```