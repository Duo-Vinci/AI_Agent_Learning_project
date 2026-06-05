"""
PDF文档加载器
支持单文件和批量加载，包含元数据提取和错误处理
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFDocumentLoader:
    """PDF文档加载器类"""

    def __init__(self, extract_images: bool = False):
        """
        初始化PDF加载器

        Args:
            extract_images: 是否提取图片信息
        """
        self.extract_images = extract_images

    def load_single_pdf(self, file_path: str) -> List[Document]:
        """
        加载单个PDF文件

        Args:
            file_path: PDF文件路径

        Returns:
            文档列表，每页一个Document对象
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            logger.info(f"开始加载PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            # 添加额外的元数据
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'page_number': i + 1,
                    'total_pages': len(documents),
                    'source_type': 'pdf'
                })

            logger.info(f"成功加载 {len(documents)} 页")
            return documents

        except Exception as e:
            logger.error(f"加载PDF失败: {str(e)}")
            raise

    def load_pdf_directory(self, directory_path: str, glob_pattern: str = "**/*.pdf") -> List[Document]:
        """
        批量加载目录下的所有PDF文件

        Args:
            directory_path: 目录路径
            glob_pattern: 文件匹配模式

        Returns:
            所有PDF文档的列表
        """
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"目录不存在: {directory_path}")

            logger.info(f"开始加载目录: {directory_path}")
            loader = PyPDFDirectoryLoader(directory_path, glob=glob_pattern)
            documents = loader.load()

            logger.info(f"成功加载 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"批量加载PDF失败: {str(e)}")
            raise

    def load_with_page_range(self, file_path: str, start_page: int = 0, end_page: Optional[int] = None) -> List[Document]:
        """
        加载PDF的指定页面范围

        Args:
            file_path: PDF文件路径
            start_page: 起始页码（从0开始）
            end_page: 结束页码（不包含），None表示到最后

        Returns:
            指定页面的文档列表
        """
        documents = self.load_single_pdf(file_path)

        if end_page is None:
            end_page = len(documents)

        selected_docs = documents[start_page:end_page]
        logger.info(f"选择了第 {start_page+1} 到 {end_page} 页，共 {len(selected_docs)} 页")

        return selected_docs

    def get_document_info(self, file_path: str) -> dict:
        """
        获取PDF文档的基本信息

        Args:
            file_path: PDF文件路径

        Returns:
            文档信息字典
        """
        documents = self.load_single_pdf(file_path)

        total_chars = sum(len(doc.page_content) for doc in documents)

        info = {
            'file_name': os.path.basename(file_path),
            'total_pages': len(documents),
            'total_characters': total_chars,
            'average_chars_per_page': total_chars // len(documents) if documents else 0,
            'file_size_mb': os.path.getsize(file_path) / (1024 * 1024)
        }

        return info


def demo():
    """演示PDF加载功能"""

    # 创建加载器实例
    loader = PDFDocumentLoader()

    # 示例1：加载单个PDF
    print("=== 示例1: 加载单个PDF ===")
    sample_pdf = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/01-document-loaders/data/sample.pdf"

    # 创建示例PDF目录（如果不存在）
    data_dir = Path(sample_pdf).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    # 如果示例文件不存在，创建一个简单的文本文件作为替代
    if not os.path.exists(sample_pdf):
        print(f"示例PDF不存在，请将PDF文件放置在: {sample_pdf}")
        print("或者使用以下代码加载您自己的PDF文件：")
        print(f"loader.load_single_pdf('your_pdf_path.pdf')")
    else:
        try:
            documents = loader.load_single_pdf(sample_pdf)
            print(f"加载了 {len(documents)} 页")
            if documents:
                print(f"\n第一页预览:")
                print(f"内容: {documents[0].page_content[:200]}...")
                print(f"元数据: {documents[0].metadata}")
        except Exception as e:
            print(f"加载失败: {e}")

    # 示例2：获取文档信息
    print("\n=== 示例2: 获取文档信息 ===")
    if os.path.exists(sample_pdf):
        try:
            info = loader.get_document_info(sample_pdf)
            print(f"文件名: {info['file_name']}")
            print(f"总页数: {info['total_pages']}")
            print(f"总字符数: {info['total_characters']}")
            print(f"平均每页字符数: {info['average_chars_per_page']}")
            print(f"文件大小: {info['file_size_mb']:.2f} MB")
        except Exception as e:
            print(f"获取信息失败: {e}")

    # 示例3：加载指定页面
    print("\n=== 示例3: 加载指定页面 ===")
    if os.path.exists(sample_pdf):
        try:
            # 只加载前3页
            documents = loader.load_with_page_range(sample_pdf, start_page=0, end_page=3)
            print(f"加载了前3页，共 {len(documents)} 个文档")
        except Exception as e:
            print(f"加载失败: {e}")

    # 示例4：批量加载目录
    print("\n=== 示例4: 批量加载目录 ===")
    data_dir = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/01-document-loaders/data"
    try:
        documents = loader.load_pdf_directory(data_dir)
        print(f"从目录加载了 {len(documents)} 个文档")
    except Exception as e:
        print(f"批量加载失败: {e}")


if __name__ == "__main__":
    demo()
