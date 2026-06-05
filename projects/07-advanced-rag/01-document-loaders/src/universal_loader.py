"""
统一文档加载器
整合所有文档加载功能，提供统一接口
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain.schema import Document
import logging

from pdf_loader import PDFDocumentLoader
from word_loader import WordDocumentLoader
from markdown_loader import MarkdownDocumentLoader
from html_loader import HTMLDocumentLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalDocumentLoader:
    """统一文档加载器，自动识别文件类型"""

    def __init__(self):
        self.pdf_loader = PDFDocumentLoader()
        self.word_loader = WordDocumentLoader()
        self.markdown_loader = MarkdownDocumentLoader()
        self.html_loader = HTMLDocumentLoader()

        # 文件扩展名到加载器的映射
        self.loaders_map = {
            '.pdf': self.pdf_loader.load_single_pdf,
            '.docx': self.word_loader.load_docx,
            '.md': self.markdown_loader.load_markdown,
            '.html': self.html_loader.load_html_file,
            '.htm': self.html_loader.load_html_file,
        }

    def load_file(self, file_path: str) -> List[Document]:
        """
        自动识别文件类型并加载

        Args:
            file_path: 文件路径

        Returns:
            文档列表
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 获取文件扩展名
            ext = Path(file_path).suffix.lower()

            if ext not in self.loaders_map:
                raise ValueError(f"不支持的文件类型: {ext}")

            logger.info(f"识别文件类型: {ext}, 开始加载...")
            loader_func = self.loaders_map[ext]
            documents = loader_func(file_path)

            return documents

        except Exception as e:
            logger.error(f"加载文件失败: {str(e)}")
            raise

    def load_directory(
        self,
        directory_path: str,
        file_types: Optional[List[str]] = None,
        recursive: bool = True
    ) -> List[Document]:
        """
        加载目录下的所有支持的文档

        Args:
            directory_path: 目录路径
            file_types: 要加载的文件类型列表，如['.pdf', '.docx']，None表示所有支持的类型
            recursive: 是否递归搜索子目录

        Returns:
            所有文档列表
        """
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"目录不存在: {directory_path}")

            documents = []
            path = Path(directory_path)

            # 如果未指定文件类型，使用所有支持的类型
            if file_types is None:
                file_types = list(self.loaders_map.keys())

            # 遍历文件
            pattern = "**/*" if recursive else "*"
            for file_path in path.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in file_types:
                    try:
                        docs = self.load_file(str(file_path))
                        documents.extend(docs)
                        logger.info(f"成功加载: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"跳过文件 {file_path.name}: {str(e)}")

            logger.info(f"从目录加载了 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"批量加载失败: {str(e)}")
            raise

    def get_supported_types(self) -> List[str]:
        """
        获取支持的文件类型列表

        Returns:
            文件扩展名列表
        """
        return list(self.loaders_map.keys())


def demo():
    """演示统一文档加载器"""
    loader = UniversalDocumentLoader()

    print("=== 统一文档加载器演示 ===\n")

    # 显示支持的文件类型
    print("支持的文件类型:", ", ".join(loader.get_supported_types()))

    # 创建测试数据目录
    data_dir = Path("Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/01-document-loaders/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # 示例1: 加载单个文件（自动识别类型）
    print("\n=== 示例1: 自动识别文件类型 ===")
    test_files = [
        data_dir / "sample.pdf",
        data_dir / "sample.docx",
        data_dir / "sample.md",
        data_dir / "sample.html"
    ]

    for test_file in test_files:
        if test_file.exists():
            try:
                documents = loader.load_file(str(test_file))
                print(f"✓ {test_file.name}: 加载了 {len(documents)} 个文档")
            except Exception as e:
                print(f"✗ {test_file.name}: {e}")
        else:
            print(f"- {test_file.name}: 文件不存在（跳过）")

    # 示例2: 批量加载目录
    print("\n=== 示例2: 批量加载目录 ===")
    try:
        all_documents = loader.load_directory(str(data_dir), recursive=True)
        print(f"总共加载了 {len(all_documents)} 个文档")

        # 按文件类型统计
        type_counts = {}
        for doc in all_documents:
            source_type = doc.metadata.get('source_type', 'unknown')
            type_counts[source_type] = type_counts.get(source_type, 0) + 1

        print("\n文档类型分布:")
        for doc_type, count in type_counts.items():
            print(f"  {doc_type}: {count} 个")

    except Exception as e:
        print(f"批量加载失败: {e}")

    # 示例3: 只加载特定类型
    print("\n=== 示例3: 只加载Markdown和HTML ===")
    try:
        filtered_docs = loader.load_directory(
            str(data_dir),
            file_types=['.md', '.html'],
            recursive=True
        )
        print(f"加载了 {len(filtered_docs)} 个Markdown/HTML文档")
    except Exception as e:
        print(f"加载失败: {e}")


if __name__ == "__main__":
    demo()
