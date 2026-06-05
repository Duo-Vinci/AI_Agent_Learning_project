"""
Word文档加载器
支持.docx格式，提取文本内容和格式信息
"""

import os
from typing import List
from pathlib import Path
from langchain_community.document_loaders import Docx2txtLoader
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordDocumentLoader:
    """Word文档加载器类"""

    def load_docx(self, file_path: str) -> List[Document]:
        """
        加载Word文档

        Args:
            file_path: Word文件路径

        Returns:
            文档列表
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            logger.info(f"开始加载Word文档: {file_path}")
            loader = Docx2txtLoader(file_path)
            documents = loader.load()

            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'source_type': 'docx',
                    'file_size_kb': os.path.getsize(file_path) / 1024
                })

            logger.info(f"成功加载Word文档")
            return documents

        except Exception as e:
            logger.error(f"加载Word文档失败: {str(e)}")
            raise

    def load_directory(self, directory_path: str) -> List[Document]:
        """
        批量加载目录下的所有Word文档

        Args:
            directory_path: 目录路径

        Returns:
            所有文档列表
        """
        try:
            documents = []
            path = Path(directory_path)

            for docx_file in path.glob("**/*.docx"):
                if not docx_file.name.startswith('~$'):  # 跳过临时文件
                    try:
                        docs = self.load_docx(str(docx_file))
                        documents.extend(docs)
                    except Exception as e:
                        logger.warning(f"跳过文件 {docx_file}: {str(e)}")

            logger.info(f"从目录加载了 {len(documents)} 个Word文档")
            return documents

        except Exception as e:
            logger.error(f"批量加载失败: {str(e)}")
            raise


def demo():
    """演示Word文档加载"""
    loader = WordDocumentLoader()

    print("=== Word文档加载器演示 ===")
    sample_docx = "Z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/07-advanced-rag/01-document-loaders/data/sample.docx"

    # 创建数据目录
    data_dir = Path(sample_docx).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(sample_docx):
        print(f"示例Word文档不存在，请将.docx文件放置在: {sample_docx}")
        print("或使用: loader.load_docx('your_file.docx')")
    else:
        try:
            documents = loader.load_docx(sample_docx)
            print(f"加载成功! 共 {len(documents)} 个文档")
            if documents:
                print(f"\n内容预览: {documents[0].page_content[:300]}...")
                print(f"\n元数据: {documents[0].metadata}")
        except Exception as e:
            print(f"加载失败: {e}")


if __name__ == "__main__":
    demo()
