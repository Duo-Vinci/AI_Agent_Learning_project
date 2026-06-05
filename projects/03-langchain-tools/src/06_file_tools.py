"""
LangChain 工具使用 - 06: 文件操作工具

本模块演示：
1. 文件读写工具
2. 目录操作（创建、删除、列出）
3. 文件搜索和过滤
4. 文本文件处理
5. JSON/CSV文件处理
6. 安全的文件操作（路径验证）
7. 文件信息查询
"""

import os
import json
import csv
import shutil
from typing import Optional, Type, List, Dict, Any
from pathlib import Path
from datetime import datetime

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 文件管理器类 ====================

class FileManager:
    """文件管理器，提供安全的文件操作"""

    def __init__(self, base_dir: str = "./workspace"):
        """
        初始化文件管理器

        Args:
            base_dir: 工作目录（所有操作限制在此目录内）
        """
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def validate_path(self, path: str) -> Path:
        """
        验证路径是否在工作目录内（防止路径遍历攻击）

        Args:
            path: 要验证的路径

        Returns:
            解析后的绝对路径

        Raises:
            ValueError: 如果路径不安全
        """
        full_path = (self.base_dir / path).resolve()

        # 确保路径在base_dir内
        if not str(full_path).startswith(str(self.base_dir)):
            raise ValueError(f"路径 '{path}' 超出工作目录范围")

        return full_path

    def read_file(self, path: str) -> str:
        """
        读取文件内容

        Args:
            path: 文件路径

        Returns:
            文件内容
        """
        full_path = self.validate_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        if not full_path.is_file():
            raise ValueError(f"不是文件: {path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str, append: bool = False) -> None:
        """
        写入文件

        Args:
            path: 文件路径
            content: 文件内容
            append: 是否追加模式
        """
        full_path = self.validate_path(path)

        # 确保父目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)

        mode = 'a' if append else 'w'
        with open(full_path, mode, encoding='utf-8') as f:
            f.write(content)

    def delete_file(self, path: str) -> None:
        """删除文件"""
        full_path = self.validate_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        if full_path.is_file():
            full_path.unlink()
        else:
            raise ValueError(f"不是文件: {path}")

    def list_directory(self, path: str = ".") -> List[Dict[str, Any]]:
        """
        列出目录内容

        Args:
            path: 目录路径

        Returns:
            文件和目录信息列表
        """
        full_path = self.validate_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"目录不存在: {path}")

        if not full_path.is_dir():
            raise ValueError(f"不是目录: {path}")

        items = []
        for item in full_path.iterdir():
            stat = item.stat()
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return sorted(items, key=lambda x: (x["type"], x["name"]))

    def create_directory(self, path: str) -> None:
        """创建目录"""
        full_path = self.validate_path(path)
        full_path.mkdir(parents=True, exist_ok=True)

    def delete_directory(self, path: str) -> None:
        """删除目录"""
        full_path = self.validate_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"目录不存在: {path}")

        if not full_path.is_dir():
            raise ValueError(f"不是目录: {path}")

        shutil.rmtree(full_path)

    def file_exists(self, path: str) -> bool:
        """检查文件是否存在"""
        try:
            full_path = self.validate_path(path)
            return full_path.exists() and full_path.is_file()
        except:
            return False


# ==================== 示例1: 读取文件工具 ====================

class ReadFileInput(BaseModel):
    """读取文件输入模式"""
    path: str = Field(description="文件路径（相对于工作目录）")


class ReadFileTool(BaseTool):
    """读取文件工具"""

    name: str = "read_file"
    description: str = """
    读取文本文件内容。

    示例:
    - path: "notes.txt"
    - path: "data/config.json"
    """
    args_schema: Type[BaseModel] = ReadFileInput
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行读取操作"""
        try:
            content = self.file_manager.read_file(path)
            return f"✓ 成功读取文件: {path}\n\n文件内容:\n{content}"
        except FileNotFoundError as e:
            return f"✗ 错误: {str(e)}"
        except ValueError as e:
            return f"✗ 错误: {str(e)}"
        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_read_file():
    """示例1: 读取文件工具"""
    print_section("示例1: 读取文件工具")

    file_manager = FileManager("./demo_workspace")
    read_tool = ReadFileTool(file_manager=file_manager)

    # 先创建一个测试文件
    file_manager.write_file("test.txt", "Hello, LangChain!\n这是一个测试文件。")

    # 读取文件
    print("读取测试文件:")
    result = read_tool.invoke({"path": "test.txt"})
    print(result)


# ==================== 示例2: 写入文件工具 ====================

class WriteFileInput(BaseModel):
    """写入文件输入模式"""
    path: str = Field(description="文件路径")
    content: str = Field(description="要写入的内容")
    append: bool = Field(default=False, description="是否追加模式")


class WriteFileTool(BaseTool):
    """写入文件工具"""

    name: str = "write_file"
    description: str = """
    写入内容到文件。如果文件不存在会自动创建。

    示例:
    - path: "notes.txt"
    - content: "这是新内容"
    - append: False（覆盖） 或 True（追加）
    """
    args_schema: Type[BaseModel] = WriteFileInput
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        path: str,
        content: str,
        append: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行写入操作"""
        try:
            self.file_manager.write_file(path, content, append)
            mode = "追加" if append else "写入"
            return f"✓ 成功{mode}文件: {path}"
        except ValueError as e:
            return f"✗ 错误: {str(e)}"
        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_write_file():
    """示例2: 写入文件工具"""
    print_section("示例2: 写入文件工具")

    file_manager = FileManager("./demo_workspace")
    write_tool = WriteFileTool(file_manager=file_manager)
    read_tool = ReadFileTool(file_manager=file_manager)

    # 写入新文件
    print("1. 写入新文件:")
    result = write_tool.invoke({
        "path": "diary.txt",
        "content": "2024-01-01: 今天开始学习LangChain\n",
        "append": False
    })
    print(result)

    # 追加内容
    print("\n2. 追加内容:")
    result = write_tool.invoke({
        "path": "diary.txt",
        "content": "2024-01-02: 学习了工具的使用\n",
        "append": True
    })
    print(result)

    # 读取文件验证
    print("\n3. 读取文件验证:")
    result = read_tool.invoke({"path": "diary.txt"})
    print(result)


# ==================== 示例3: 列出目录工具 ====================

class ListDirectoryInput(BaseModel):
    """列出目录输入模式"""
    path: str = Field(default=".", description="目录路径")


class ListDirectoryTool(BaseTool):
    """列出目录工具"""

    name: str = "list_directory"
    description: str = """
    列出目录中的文件和子目录。

    示例:
    - path: "." （当前目录）
    - path: "data" （data子目录）
    """
    args_schema: Type[BaseModel] = ListDirectoryInput
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        path: str = ".",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行列出目录操作"""
        try:
            items = self.file_manager.list_directory(path)

            if not items:
                return f"目录为空: {path}"

            output = f"目录内容: {path}\n\n"

            # 分别显示目录和文件
            dirs = [item for item in items if item["type"] == "directory"]
            files = [item for item in items if item["type"] == "file"]

            if dirs:
                output += "📁 目录:\n"
                for item in dirs:
                    output += f"  {item['name']}/\n"

            if files:
                output += "\n📄 文件:\n"
                for item in files:
                    size_kb = item['size'] / 1024
                    output += f"  {item['name']} ({size_kb:.2f} KB)\n"

            output += f"\n总计: {len(dirs)} 个目录, {len(files)} 个文件"
            return output

        except FileNotFoundError as e:
            return f"✗ 错误: {str(e)}"
        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_list_directory():
    """示例3: 列出目录工具"""
    print_section("示例3: 列出目录工具")

    file_manager = FileManager("./demo_workspace")
    list_tool = ListDirectoryTool(file_manager=file_manager)

    # 创建一些测试文件和目录
    file_manager.create_directory("data")
    file_manager.write_file("data/file1.txt", "内容1")
    file_manager.write_file("data/file2.txt", "内容2")
    file_manager.create_directory("notes")
    file_manager.write_file("notes/note1.txt", "笔记1")

    # 列出根目录
    print("列出根目录:")
    result = list_tool.invoke({"path": "."})
    print(result)

    # 列出data目录
    print("\n列出data目录:")
    result = list_tool.invoke({"path": "data"})
    print(result)


# ==================== 示例4: JSON文件工具 ====================

class ReadJSONInput(BaseModel):
    """读取JSON输入模式"""
    path: str = Field(description="JSON文件路径")


class WriteJSONInput(BaseModel):
    """写入JSON输入模式"""
    path: str = Field(description="JSON文件路径")
    data: Dict[str, Any] = Field(description="要写入的JSON数据")


class JSONFileTool(BaseTool):
    """JSON文件工具"""

    name: str = "json_file"
    description: str = """
    读取或写入JSON文件。

    操作:
    - action: "read" 读取JSON
    - action: "write" 写入JSON
    """

    class InputSchema(BaseModel):
        action: str = Field(description="操作类型: read, write")
        path: str = Field(description="文件路径")
        data: Optional[Dict[str, Any]] = Field(
            default=None,
            description="写入时的JSON数据"
        )

    args_schema: Type[BaseModel] = InputSchema
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        action: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行JSON操作"""
        try:
            if action == "read":
                content = self.file_manager.read_file(path)
                json_data = json.loads(content)
                return f"✓ 成功读取JSON文件: {path}\n\n" + \
                       json.dumps(json_data, indent=2, ensure_ascii=False)

            elif action == "write":
                if data is None:
                    return "✗ 错误: 写入操作需要提供data参数"

                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                self.file_manager.write_file(path, json_str)
                return f"✓ 成功写入JSON文件: {path}"

            else:
                return f"✗ 错误: 不支持的操作 '{action}'"

        except json.JSONDecodeError as e:
            return f"✗ JSON解析错误: {str(e)}"
        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_json_file():
    """示例4: JSON文件工具"""
    print_section("示例4: JSON文件工具")

    file_manager = FileManager("./demo_workspace")
    json_tool = JSONFileTool(file_manager=file_manager)

    # 写入JSON文件
    print("1. 写入JSON文件:")
    result = json_tool.invoke({
        "action": "write",
        "path": "config.json",
        "data": {
            "app_name": "LangChain Demo",
            "version": "1.0.0",
            "settings": {
                "debug": True,
                "max_retries": 3
            },
            "features": ["tools", "agents", "memory"]
        }
    })
    print(result)

    # 读取JSON文件
    print("\n2. 读取JSON文件:")
    result = json_tool.invoke({
        "action": "read",
        "path": "config.json"
    })
    print(result)


# ==================== 示例5: CSV文件工具 ====================

class CSVFileTool(BaseTool):
    """CSV文件工具"""

    name: str = "csv_file"
    description: str = """
    读取或写入CSV文件。

    操作:
    - action: "read" 读取CSV
    - action: "write" 写入CSV
    """

    class InputSchema(BaseModel):
        action: str = Field(description="操作类型: read, write")
        path: str = Field(description="文件路径")
        data: Optional[List[Dict[str, Any]]] = Field(
            default=None,
            description="写入时的数据（字典列表）"
        )

    args_schema: Type[BaseModel] = InputSchema
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        action: str,
        path: str,
        data: Optional[List[Dict[str, Any]]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行CSV操作"""
        try:
            if action == "read":
                full_path = self.file_manager.validate_path(path)
                rows = []

                with open(full_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                output = f"✓ 成功读取CSV文件: {path}\n"
                output += f"共 {len(rows)} 行数据\n\n"

                for i, row in enumerate(rows[:5], 1):
                    output += f"行 {i}: {row}\n"

                if len(rows) > 5:
                    output += f"\n... 还有 {len(rows) - 5} 行"

                return output

            elif action == "write":
                if not data:
                    return "✗ 错误: 写入操作需要提供data参数"

                full_path = self.file_manager.validate_path(path)
                full_path.parent.mkdir(parents=True, exist_ok=True)

                fieldnames = data[0].keys() if data else []

                with open(full_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)

                return f"✓ 成功写入CSV文件: {path} ({len(data)} 行)"

            else:
                return f"✗ 错误: 不支持的操作 '{action}'"

        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_csv_file():
    """示例5: CSV文件工具"""
    print_section("示例5: CSV文件工具")

    file_manager = FileManager("./demo_workspace")
    csv_tool = CSVFileTool(file_manager=file_manager)

    # 写入CSV文件
    print("1. 写入CSV文件:")
    result = csv_tool.invoke({
        "action": "write",
        "path": "users.csv",
        "data": [
            {"id": 1, "name": "张三", "age": 25, "city": "北京"},
            {"id": 2, "name": "李四", "age": 30, "city": "上海"},
            {"id": 3, "name": "王五", "age": 28, "city": "广州"},
            {"id": 4, "name": "赵六", "age": 32, "city": "深圳"},
        ]
    })
    print(result)

    # 读取CSV文件
    print("\n2. 读取CSV文件:")
    result = csv_tool.invoke({
        "action": "read",
        "path": "users.csv"
    })
    print(result)


# ==================== 示例6: 文件搜索工具 ====================

class SearchFilesInput(BaseModel):
    """搜索文件输入模式"""
    pattern: str = Field(description="搜索模式（文件名匹配）")
    directory: str = Field(default=".", description="搜索目录")


class SearchFilesTool(BaseTool):
    """文件搜索工具"""

    name: str = "search_files"
    description: str = """
    在目录中搜索文件（按文件名模糊匹配）。

    示例:
    - pattern: "*.txt" 或 "test" 或 ".json"
    - directory: "." 或 "data"
    """
    args_schema: Type[BaseModel] = SearchFilesInput
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        pattern: str,
        directory: str = ".",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行搜索操作"""
        try:
            base_path = self.file_manager.validate_path(directory)
            matches = []

            # 递归搜索
            for path in base_path.rglob("*"):
                if path.is_file():
                    # 简单的模式匹配
                    if pattern in path.name or \
                       (pattern.startswith("*.") and path.suffix == pattern[1:]):
                        rel_path = path.relative_to(self.file_manager.base_dir)
                        matches.append({
                            "path": str(rel_path),
                            "name": path.name,
                            "size": path.stat().st_size
                        })

            if not matches:
                return f"未找到匹配 '{pattern}' 的文件"

            output = f"找到 {len(matches)} 个匹配的文件:\n\n"
            for item in matches:
                size_kb = item['size'] / 1024
                output += f"  📄 {item['path']} ({size_kb:.2f} KB)\n"

            return output

        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_search_files():
    """示例6: 文件搜索工具"""
    print_section("示例6: 文件搜索工具")

    file_manager = FileManager("./demo_workspace")
    search_tool = SearchFilesTool(file_manager=file_manager)

    # 搜索所有txt文件
    print("1. 搜索所有.txt文件:")
    result = search_tool.invoke({
        "pattern": "*.txt",
        "directory": "."
    })
    print(result)

    # 搜索包含"note"的文件
    print("\n2. 搜索文件名包含'note'的文件:")
    result = search_tool.invoke({
        "pattern": "note",
        "directory": "."
    })
    print(result)


# ==================== 示例7: 文件信息工具 ====================

class FileInfoInput(BaseModel):
    """文件信息输入模式"""
    path: str = Field(description="文件路径")


class FileInfoTool(BaseTool):
    """文件信息工具"""

    name: str = "file_info"
    description: str = """
    获取文件详细信息（大小、修改时间等）。

    示例:
    - path: "data.json"
    """
    args_schema: Type[BaseModel] = FileInfoInput
    file_manager: FileManager = None

    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager

    def _run(
        self,
        path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行获取文件信息操作"""
        try:
            full_path = self.file_manager.validate_path(path)

            if not full_path.exists():
                return f"✗ 文件不存在: {path}"

            stat = full_path.stat()

            output = f"文件信息: {path}\n\n"
            output += f"名称: {full_path.name}\n"
            output += f"类型: {'目录' if full_path.is_dir() else '文件'}\n"

            if full_path.is_file():
                size_bytes = stat.st_size
                size_kb = size_bytes / 1024
                size_mb = size_kb / 1024

                output += f"大小: {size_bytes} 字节 "
                output += f"({size_kb:.2f} KB" if size_kb < 1024 else f"({size_mb:.2f} MB"
                output += ")\n"

                output += f"扩展名: {full_path.suffix}\n"

            output += f"创建时间: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"修改时间: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"访问时间: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}"

            return output

        except Exception as e:
            return f"✗ 错误: {str(e)}"


def demo_file_info():
    """示例7: 文件信息工具"""
    print_section("示例7: 文件信息工具")

    file_manager = FileManager("./demo_workspace")
    info_tool = FileInfoTool(file_manager=file_manager)

    # 获取JSON文件信息
    print("1. 获取config.json文件信息:")
    result = info_tool.invoke({"path": "config.json"})
    print(result)

    # 获取CSV文件信息
    print("\n2. 获取users.csv文件信息:")
    result = info_tool.invoke({"path": "users.csv"})
    print(result)


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 06: 文件操作工具")
    print("="*70)

    try:
        # 清理旧工作空间
        if os.path.exists("./demo_workspace"):
            shutil.rmtree("./demo_workspace")

        # 示例1: 读取文件
        demo_read_file()

        # 示例2: 写入文件
        demo_write_file()

        # 示例3: 列出目录
        demo_list_directory()

        # 示例4: JSON文件
        demo_json_file()

        # 示例5: CSV文件
        demo_csv_file()

        # 示例6: 文件搜索
        demo_search_files()

        # 示例7: 文件信息
        demo_file_info()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  提示: 工作空间位于 ./demo_workspace")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理演示工作空间（可选）
        # if os.path.exists("./demo_workspace"):
        #     shutil.rmtree("./demo_workspace")
        pass


if __name__ == "__main__":
    main()
