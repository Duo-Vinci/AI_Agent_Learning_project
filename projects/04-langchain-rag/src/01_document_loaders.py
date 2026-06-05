"""
LangChain RAG应用 - 01: 文档加载器

本模块演示：
1. PDF文档加载（PyPDF2, pdfplumber）
2. Word文档加载（python-docx）
3. 文本文件加载（TXT/CSV/JSON）
4. 网页加载（BeautifulSoup）
5. Markdown文档加载
6. 批量文档加载
7. 文档元数据提取
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    WebBaseLoader
)
from langchain.schema import Document


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 文本文件加载器 ====================

def demo_text_loader():
    """示例1: 加载文本文件"""
    print_section("示例1: 文本文件加载器")

    # 创建示例文本文件
    sample_dir = Path("./sample_docs")
    sample_dir.mkdir(exist_ok=True)

    text_file = sample_dir / "sample.txt"
    text_file.write_text("""
LangChain是一个强大的框架，用于开发由语言模型驱动的应用程序。

主要特点：
1. 模块化设计
2. 丰富的集成
3. 易于使用

LangChain支持多种文档类型，包括文本、PDF、Word等。
RAG（检索增强生成）是LangChain的核心应用之一。
    """.strip(), encoding='utf-8')

    print(f"创建示例文件: {text_file}\n")

    # 加载文本文件
    try:
        loader = TextLoader(str(text_file), encoding='utf-8')
        documents = loader.load()

        print(f"✓ 成功加载 {len(documents)} 个文档\n")

        for i, doc in enumerate(documents, 1):
            print(f"文档 {i}:")
            print(f"  内容长度: {len(doc.page_content)} 字符")
            print(f"  元数据: {doc.metadata}")
            print(f"  内容预览: {doc.page_content[:100]}...\n")

    except Exception as e:
        print(f"✗ 加载失败: {str(e)}")


# ==================== 示例2: CSV文件加载器 ====================

def demo_csv_loader():
    """示例2: 加载CSV文件"""
    print_section("示例2: CSV文件加载器")

    # 创建示例CSV文件
    sample_dir = Path("./sample_docs")
    sample_dir.mkdir(exist_ok=True)

    csv_file = sample_dir / "data.csv"
    csv_content = """id,name,description,category
1,Python基础,学习Python编程基础知识,编程
2,LangChain入门,了解LangChain框架的核心概念,AI
3,RAG应用,构建检索增强生成应用,AI
4,数据分析,使用Pandas进行数据分析,数据科学
5,机器学习,机器学习算法和应用,AI"""

    csv_file.write_text(csv_content, encoding='utf-8')

    print(f"创建示例CSV文件: {csv_file}\n")

    # 加载CSV文件
    try:
        loader = CSVLoader(str(csv_file), encoding='utf-8')
        documents = loader.load()

        print(f"✓ 成功加载 {len(documents)} 行数据\n")

        for i, doc in enumerate(documents[:3], 1):
            print(f"记录 {i}:")
            print(f"  内容: {doc.page_content}")
            print(f"  元数据: {doc.metadata}\n")

    except Exception as e:
        print(f"✗ 加载失败: {str(e)}")


# ==================== 示例3: JSON文件加载器 ====================

def demo_json_loader():
    """示例3: 加载JSON文件"""
    print_section("示例3: JSON文件加载器")

    import json

    # 创建示例JSON文件
    sample_dir = Path("./sample_docs")
    sample_dir.mkdir(exist_ok=True)

    json_file = sample_dir / "data.json"
    json_data = {
        "articles": [
            {
                "id": 1,
                "title": "LangChain简介",
                "content": "LangChain是一个用于开发语言模型应用的框架。",
                "tags": ["AI", "LangChain"]
            },
            {
                "id": 2,
                "title": "RAG技术详解",
                "content": "检索增强生成（RAG）结合了检索和生成两种技术。",
                "tags": ["RAG", "AI"]
            }
        ]
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"创建示例JSON文件: {json_file}\n")

    # 手动加载JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 将JSON转换为Document对象
        documents = []
        for article in data['articles']:
            content = f"标题: {article['title']}\n内容: {article['content']}"
            metadata = {
                "id": article['id'],
                "tags": ", ".join(article['tags']),
                "source": str(json_file)
            }
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)

        print(f"✓ 成功加载 {len(documents)} 个文档\n")

        for i, doc in enumerate(documents, 1):
            print(f"文档 {i}:")
            print(f"  {doc.page_content}")
            print(f"  元数据: {doc.metadata}\n")

    except Exception as e:
        print(f"✗ 加载失败: {str(e)}")


# ==================== 示例4: Markdown文件加载器 ====================

def demo_markdown_loader():
    """示例4: 加载Markdown文件"""
    print_section("示例4: Markdown文件加载器")

    # 创建示例Markdown文件
    sample_dir = Path("./sample_docs")
    sample_dir.mkdir(exist_ok=True)

    md_file = sample_dir / "readme.md"
    md_content = """# LangChain RAG 教程

## 什么是RAG？

RAG（Retrieval-Augmented Generation）是检索增强生成的缩写。

### 核心组件

1. **文档加载器** - 加载各种格式的文档
2. **文本分割器** - 将长文档分割成小块
3. **向量存储** - 存储文档的向量表示
4. **检索器** - 检索相关文档

### 优势

- 提高回答准确性
- 减少幻觉问题
- 支持实时更新知识库

## 开始使用

```python
from langchain import RAG

rag = RAG()
result = rag.query("什么是LangChain?")
```

更多信息请访问 [LangChain官网](https://langchain.com)
"""

    md_file.write_text(md_content, encoding='utf-8')

    print(f"创建示例Markdown文件: {md_file}\n")

    # 加载Markdown文件
    try:
        # 先尝试简单的文本加载
        loader = TextLoader(str(md_file), encoding='utf-8')
        documents = loader.load()

        print(f"✓ 成功加载 {len(documents)} 个文档\n")

        for i, doc in enumerate(documents, 1):
            print(f"文档 {i}:")
            print(f"  内容长度: {len(doc.page_content)} 字符")
            print(f"  内容预览:\n{doc.page_content[:200]}...\n")

    except Exception as e:
        print(f"✗ 加载失败: {str(e)}")


# ==================== 示例5: PDF文件加载器（模拟）====================

def demo_pdf_loader():
    """示例5: PDF文件加载器"""
    print_section("示例5: PDF文件加载器")

    print("PDF加载器说明:")
    print("\nPyPDFLoader - 基于PyPDF2库")
    print("  用法: PyPDFLoader('document.pdf')")
    print("  特点: 轻量级，速度快")
    print("  适用: 简单的文本PDF")

    print("\nPDFPlumberLoader - 基于pdfplumber库")
    print("  用法: PDFPlumberLoader('document.pdf')")
    print("  特点: 更强大的解析能力")
    print("  适用: 复杂布局的PDF")

    # 模拟PDF文档
    print("\n模拟PDF文档内容:")
    mock_pdf_content = """
LangChain RAG应用开发指南

第一章：RAG基础

检索增强生成（RAG）是一种结合了检索和生成的AI技术。
它通过检索相关文档来增强语言模型的回答能力。

第二章：文档处理

文档加载是RAG系统的第一步。支持的格式包括：
- PDF文档
- Word文档
- 文本文件
- 网页内容

第三章：向量存储

向量存储用于高效检索相关文档。常用的向量数据库：
- FAISS
- Chroma
- Pinecone
    """

    # 创建模拟Document对象
    doc = Document(
        page_content=mock_pdf_content.strip(),
        metadata={
            "source": "guide.pdf",
            "page": 1,
            "total_pages": 3
        }
    )

    print(f"\n文档信息:")
    print(f"  来源: {doc.metadata['source']}")
    print(f"  页码: {doc.metadata['page']}/{doc.metadata['total_pages']}")
    print(f"  内容长度: {len(doc.page_content)} 字符")
    print(f"\n内容预览:\n{doc.page_content[:200]}...")


# ==================== 示例6: Word文档加载器（模拟）====================

def demo_word_loader():
    """示例6: Word文档加载器"""
    print_section("示例6: Word文档加载器")

    print("Word加载器说明:")
    print("\nDocx2txtLoader - 基于docx2txt库")
    print("  用法: Docx2txtLoader('document.docx')")
    print("  特点: 简单易用")
    print("  适用: 标准Word文档")

    print("\nUnstructuredWordDocumentLoader")
    print("  用法: UnstructuredWordDocumentLoader('document.docx')")
    print("  特点: 保留更多格式信息")
    print("  适用: 需要保留格式的文档")

    # 模拟Word文档内容
    print("\n模拟Word文档内容:")
    mock_word_content = """
标题：LangChain开发最佳实践

1. 模块化设计
   - 使用清晰的模块划分
   - 保持代码可维护性

2. 错误处理
   - 完善的异常处理
   - 友好的错误提示

3. 性能优化
   - 使用缓存机制
   - 批量处理数据

4. 测试
   - 单元测试
   - 集成测试
    """

    doc = Document(
        page_content=mock_word_content.strip(),
        metadata={
            "source": "best_practices.docx",
            "author": "LangChain Team"
        }
    )

    print(f"\n文档信息:")
    print(f"  来源: {doc.metadata['source']}")
    print(f"  作者: {doc.metadata['author']}")
    print(f"  内容:\n{doc.page_content}")


# ==================== 示例7: 网页加载器 ====================

def demo_web_loader():
    """示例7: 网页加载器"""
    print_section("示例7: 网页加载器")

    print("网页加载器说明:")
    print("\nWebBaseLoader - 基于BeautifulSoup")
    print("  用法: WebBaseLoader('https://example.com')")
    print("  特点: 自动解析HTML")
    print("  适用: 标准网页")

    # 模拟网页内容
    print("\n模拟网页内容:")

    html_content = """
    <html>
    <head><title>LangChain官方文档</title></head>
    <body>
        <h1>欢迎使用LangChain</h1>
        <p>LangChain是构建AI应用的强大框架。</p>
        <h2>快速开始</h2>
        <p>通过pip安装: pip install langchain</p>
        <h2>核心功能</h2>
        <ul>
            <li>文档加载</li>
            <li>向量存储</li>
            <li>问答系统</li>
        </ul>
    </body>
    </html>
    """

    # 解析HTML
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)

    doc = Document(
        page_content=text,
        metadata={
            "source": "https://docs.langchain.com",
            "title": soup.title.string if soup.title else "Unknown"
        }
    )

    print(f"\n文档信息:")
    print(f"  来源: {doc.metadata['source']}")
    print(f"  标题: {doc.metadata['title']}")
    print(f"  内容:\n{doc.page_content}")


# ==================== 示例8: 批量文档加载 ====================

def demo_batch_loading():
    """示例8: 批量文档加载"""
    print_section("示例8: 批量文档加载")

    sample_dir = Path("./sample_docs")

    # 创建多个示例文件
    files_to_create = {
        "doc1.txt": "这是第一个文档，介绍LangChain的基础知识。",
        "doc2.txt": "这是第二个文档，讨论RAG技术的应用。",
        "doc3.txt": "这是第三个文档，分享最佳实践和经验。"
    }

    for filename, content in files_to_create.items():
        file_path = sample_dir / filename
        file_path.write_text(content, encoding='utf-8')

    print("创建示例文件:")
    for filename in files_to_create.keys():
        print(f"  ✓ {filename}")

    # 批量加载
    print("\n批量加载文档:")
    documents = []

    for file_path in sample_dir.glob("doc*.txt"):
        try:
            loader = TextLoader(str(file_path), encoding='utf-8')
            docs = loader.load()
            documents.extend(docs)
            print(f"  ✓ 加载 {file_path.name}")
        except Exception as e:
            print(f"  ✗ 加载 {file_path.name} 失败: {str(e)}")

    print(f"\n总共加载 {len(documents)} 个文档")

    # 显示所有文档
    print("\n文档列表:")
    for i, doc in enumerate(documents, 1):
        print(f"\n{i}. {doc.metadata.get('source', 'Unknown')}")
        print(f"   {doc.page_content}")


# ==================== 示例9: 文档元数据提取 ====================

def demo_metadata_extraction():
    """示例9: 文档元数据提取"""
    print_section("示例9: 文档元数据提取")

    sample_dir = Path("./sample_docs")

    # 创建带丰富元数据的文档
    test_file = sample_dir / "metadata_test.txt"
    test_file.write_text(
        "这是一个测试文档，用于演示元数据提取。",
        encoding='utf-8'
    )

    # 加载并添加元数据
    loader = TextLoader(str(test_file), encoding='utf-8')
    documents = loader.load()

    # 增强元数据
    for doc in documents:
        # 获取文件信息
        file_stat = test_file.stat()

        # 添加自定义元数据
        doc.metadata.update({
            "file_size": file_stat.st_size,
            "created_time": file_stat.st_ctime,
            "file_type": test_file.suffix,
            "word_count": len(doc.page_content.split()),
            "char_count": len(doc.page_content),
            "language": "zh-CN",
            "category": "tutorial"
        })

    print("文档元数据:")
    for doc in documents:
        print("\n完整元数据:")
        for key, value in doc.metadata.items():
            print(f"  {key}: {value}")


# ==================== 示例10: 自定义加载器 ====================

class CustomDocumentLoader:
    """自定义文档加载器"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> List[Document]:
        """加载文档"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        # 读取文件内容
        content = self.file_path.read_text(encoding='utf-8')

        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        # 创建Document对象
        documents = []
        for i, paragraph in enumerate(paragraphs):
            doc = Document(
                page_content=paragraph,
                metadata={
                    "source": str(self.file_path),
                    "paragraph": i + 1,
                    "total_paragraphs": len(paragraphs)
                }
            )
            documents.append(doc)

        return documents


def demo_custom_loader():
    """示例10: 自定义加载器"""
    print_section("示例10: 自定义文档加载器")

    sample_dir = Path("./sample_docs")

    # 创建多段落文档
    multi_para_file = sample_dir / "multi_paragraph.txt"
    content = """LangChain是一个强大的框架。

它提供了丰富的工具和组件。

使用LangChain可以快速构建AI应用。

RAG是其核心功能之一。"""

    multi_para_file.write_text(content, encoding='utf-8')

    # 使用自定义加载器
    loader = CustomDocumentLoader(str(multi_para_file))
    documents = loader.load()

    print(f"✓ 成功加载 {len(documents)} 个段落\n")

    for doc in documents:
        print(f"段落 {doc.metadata['paragraph']}/{doc.metadata['total_paragraphs']}:")
        print(f"  {doc.page_content}\n")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain RAG应用 - 01: 文档加载器")
    print("="*70)

    try:
        # 示例1: 文本文件
        demo_text_loader()

        # 示例2: CSV文件
        demo_csv_loader()

        # 示例3: JSON文件
        demo_json_loader()

        # 示例4: Markdown文件
        demo_markdown_loader()

        # 示例5: PDF文件
        demo_pdf_loader()

        # 示例6: Word文件
        demo_word_loader()

        # 示例7: 网页
        demo_web_loader()

        # 示例8: 批量加载
        demo_batch_loading()

        # 示例9: 元数据提取
        demo_metadata_extraction()

        # 示例10: 自定义加载器
        demo_custom_loader()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  提示: 示例文档保存在 ./sample_docs 目录")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
