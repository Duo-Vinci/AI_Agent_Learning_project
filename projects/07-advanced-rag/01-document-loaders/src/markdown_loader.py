"""
Markdown文档加载器
支持标准Markdown格式，保留文档结构
"""

import os
from typing import List
from pathlib import Path
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkdownDocumentLoader:
    """Markdown文档加载器类"""

    def load_markdown(self, file_path: str) -> List[Document]:
        """
        加载Markdown文档

        Args:
            file_path: Markdown文件路径

        Returns:
            文档列表
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            logger.info(f"开始加载Markdown文档: {file_path}")
            loader = UnstructuredMarkdownLoader(file_path)
            documents = loader.load()

            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'source_type': 'markdown',
                    'file_size_kb': os.path.getsize(file_path) / 1024
                })

            logger.info(f"成功加载Markdown文档")
            return documents

        except Exception as e:
            logger.error(f"加载Markdown文档失败: {str(e)}")
            raise

    def load_directory(self, directory_path: str) -> List[Document]:
        """
        批量加载目录下的所有Markdown文档

        Args:
            directory_path: 目录路径

        Returns:
            所有文档列表
        """
        try:
            documents = []
            path = Path(directory_path)

            for md_file in path.glob("**/*.md"):
                try:
                    docs = self.load_markdown(str(md_file))
                    documents.extend(docs)
                except Exception as e:
                    logger.warning(f"跳过文件 {md_file}: {str(e)}")

            logger.info(f"从目录加载了 {len(documents)} 个Markdown文档")
            return documents

        except Exception as e:
            logger.error(f"批量加载失败: {str(e)}")
            raise


def demo():
    """演示Markdown文档加载"""
    loader = MarkdownDocumentLoader()

    print("=== Markdown文档加载器演示 ===")
    sample_md = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/01-document-loaders/data/sample.md"

    # 创建数据目录和示例文件
    data_dir = Path(sample_md).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    # 创建示例Markdown文件
    if not os.path.exists(sample_md):
        with open(sample_md, 'w', encoding='utf-8') as f:
            f.write("""# RAG系统介绍

## 什么是RAG？

RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合信息检索和文本生成的AI技术。

### 核心优势

1. **准确性高**: 基于真实文档回答
2. **知识可更新**: 无需重新训练模型
3. **可追溯性**: 能够引用信息来源

## 应用场景

- 智能客服
- 知识库问答
- 文档分析
- 代码助手

## 技术架构

```python
# RAG基本流程
documents = load_documents()
chunks = split_into_chunks(documents)
embeddings = create_embeddings(chunks)
vectorstore = store_in_database(embeddings)
```

这是一个简单的RAG系统示例。
""")
        print(f"已创建示例Markdown文件: {sample_md}")

    try:
        documents = loader.load_markdown(sample_md)
        print(f"加载成功! 共 {len(documents)} 个文档")
        if documents:
            print(f"\n内容预览: {documents[0].page_content[:300]}...")
            print(f"\n元数据: {documents[0].metadata}")
    except Exception as e:
        print(f"加载失败: {e}")


if __name__ == "__main__":
    demo()
