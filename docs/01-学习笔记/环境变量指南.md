# .env 文件配置指南

## 什么是 .env 文件

`.env` 文件是一个用于存储环境变量的配置文件，通常包含敏感信息如 API 密钥、数据库连接字符串等。

## 为什么需要 .env 文件

1. **安全性**：避免将敏感信息硬编码到代码中
2. **灵活性**：不同环境可以使用不同的配置
3. **便捷性**：集中管理所有配置项

## .env 文件规则

### 基本格式

```
KEY=VALUE
```

### 注意事项

1. **不使用引号**（除非值包含空格）
2. **不使用等号两侧空格**
3. **注释以 # 开头**
4. **敏感信息不要提交到版本控制**

### 示例

```env
# OpenAI API 密钥
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 模型配置
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydatabase
```

## 在 Python 中使用 .env

### 安装依赖

```bash
pip install python-dotenv
```

### 加载环境变量

```python
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 获取环境变量
api_key = os.getenv("OPENAI_API_KEY")
```

## LangChain 项目常用环境变量

### OpenAI

```env
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1
```

### 其他 LLM 提供商

```env
# Anthropic
ANTHROPIC_API_KEY=your-api-key

# Google
GOOGLE_API_KEY=your-api-key

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### 向量数据库

```env
# Pinecone
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=gcp-starter

# Weaviate
WEAVIATE_URL=http://localhost:8080
```

## 最佳实践

1. **创建 .env.example**：作为配置模板，包含占位符
2. **将 .env 添加到 .gitignore**：确保不会被提交
3. **使用不同的 .env 文件**：如 .env.development, .env.production
4. **设置合适的文件权限**：确保只有管理员可以读取

## .env.example 模板

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Model Settings
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=1024

# Optional: Other LLM Providers
# ANTHROPIC_API_KEY=your-anthropic-api-key
# GOOGLE_API_KEY=your-google-api-key
```