"""
HTML文档加载器
支持网页和HTML文件加载，自动清理HTML标签
"""

import os
from typing import List
from pathlib import Path
from langchain_community.document_loaders import UnstructuredHTMLLoader, WebBaseLoader
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTMLDocumentLoader:
    """HTML文档加载器类"""

    def load_html_file(self, file_path: str) -> List[Document]:
        """
        加载HTML文件

        Args:
            file_path: HTML文件路径

        Returns:
            文档列表
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            logger.info(f"开始加载HTML文件: {file_path}")
            loader = UnstructuredHTMLLoader(file_path)
            documents = loader.load()

            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'source_type': 'html',
                    'file_size_kb': os.path.getsize(file_path) / 1024
                })

            logger.info(f"成功加载HTML文件")
            return documents

        except Exception as e:
            logger.error(f"加载HTML文件失败: {str(e)}")
            raise

    def load_web_page(self, url: str) -> List[Document]:
        """
        从URL加载网页内容

        Args:
            url: 网页URL

        Returns:
            文档列表
        """
        try:
            logger.info(f"开始加载网页: {url}")
            loader = WebBaseLoader(url)
            documents = loader.load()

            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    'url': url,
                    'source_type': 'web',
                })

            logger.info(f"成功加载网页")
            return documents

        except Exception as e:
            logger.error(f"加载网页失败: {str(e)}")
            raise

    def load_web_pages(self, urls: List[str]) -> List[Document]:
        """
        批量加载多个网页

        Args:
            urls: URL列表

        Returns:
            所有网页的文档列表
        """
        documents = []
        for url in urls:
            try:
                docs = self.load_web_page(url)
                documents.extend(docs)
            except Exception as e:
                logger.warning(f"跳过URL {url}: {str(e)}")

        logger.info(f"成功加载 {len(documents)} 个网页")
        return documents


def demo():
    """演示HTML文档加载"""
    loader = HTMLDocumentLoader()

    print("=== HTML文档加载器演示 ===")

    # 示例1: 加载本地HTML文件
    print("\n示例1: 加载本地HTML文件")
    sample_html = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/01-document-loaders/data/sample.html"

    # 创建数据目录和示例文件
    data_dir = Path(sample_html).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(sample_html):
        with open(sample_html, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>RAG系统介绍</title>
</head>
<body>
    <h1>什么是RAG系统？</h1>
    <p>RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术。</p>

    <h2>核心组件</h2>
    <ul>
        <li>文档加载器</li>
        <li>文本分块器</li>
        <li>向量数据库</li>
        <li>检索器</li>
        <li>生成模型</li>
    </ul>

    <h2>优势</h2>
    <p>相比传统的大语言模型，RAG系统具有以下优势：</p>
    <ol>
        <li>答案更准确，基于真实文档</li>
        <li>知识可以实时更新</li>
        <li>可以追溯信息来源</li>
    </ol>
</body>
</html>
""")
        print(f"已创建示例HTML文件: {sample_html}")

    try:
        documents = loader.load_html_file(sample_html)
        print(f"加载成功! 共 {len(documents)} 个文档")
        if documents:
            print(f"\n内容预览: {documents[0].page_content[:300]}...")
            print(f"\n元数据: {documents[0].metadata}")
    except Exception as e:
        print(f"加载失败: {e}")

    # 示例2: 加载网页（可选，需要网络连接）
    print("\n\n示例2: 加载网页（需要网络连接）")
    print("注意: 这需要网络连接，如果失败请检查网络或跳过此步骤")
    # 取消注释以下代码来测试网页加载
    # try:
    #     documents = loader.load_web_page("https://python.langchain.com/docs/get_started/introduction")
    #     print(f"加载成功! 共 {len(documents)} 个文档")
    # except Exception as e:
    #     print(f"加载失败: {e}")


if __name__ == "__main__":
    demo()
