"""
LangChain 工具使用 - 04: 数据库工具

本模块演示：
1. SQLite数据库连接和管理
2. 安全的SQL查询（防SQL注入）
3. 参数化查询
4. 查询结果格式化
5. 数据库连接池管理
6. 事务处理
7. CRUD操作工具（创建、读取、更新、删除）
"""

import os
import sqlite3
from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 数据库管理类 ====================

class DatabaseManager:
    """数据库连接管理器"""

    def __init__(self, db_path: str = "example.db"):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._connection = None

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接（上下文管理器）

        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式的行
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_query(
        self,
        query: str,
        params: tuple = (),
        fetch_one: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        执行SQL查询（参数化查询，防止SQL注入）

        Args:
            query: SQL查询语句
            params: 查询参数（使用?占位符）
            fetch_one: 是否只返回一条记录

        Returns:
            查询结果列表或None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                if fetch_one:
                    row = cursor.fetchone()
                    return [dict(row)] if row else []
                else:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
            else:
                # INSERT, UPDATE, DELETE
                return None

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        批量执行SQL语句

        Args:
            query: SQL语句
            params_list: 参数列表

        Returns:
            影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def create_tables(self):
        """创建示例表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建产品表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER DEFAULT 0,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建订单表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)

    def drop_tables(self):
        """删除所有表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS users")


# ==================== 示例1: 创建表工具 ====================

class CreateTableInput(BaseModel):
    """创建表输入模式"""
    table_name: str = Field(description="表名")
    columns: str = Field(description="列定义，格式: 'col1 TYPE, col2 TYPE, ...'")


class CreateTableTool(BaseTool):
    """创建数据库表工具"""

    name: str = "create_table"
    description: str = """
    在数据库中创建新表。
    需要提供表名和列定义。

    示例:
    - table_name: "students"
    - columns: "id INTEGER PRIMARY KEY, name TEXT, grade REAL"
    """
    args_schema: Type[BaseModel] = CreateTableInput
    db_manager: DatabaseManager = None

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def _run(
        self,
        table_name: str,
        columns: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行创建表操作"""
        try:
            # 验证表名（防止SQL注入）
            if not table_name.replace("_", "").isalnum():
                return f"错误: 无效的表名 '{table_name}'"

            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)

            return f"成功创建表 '{table_name}'"

        except sqlite3.Error as e:
            return f"数据库错误: {str(e)}"
        except Exception as e:
            return f"错误: {str(e)}"


def demo_create_table():
    """示例1: 创建表工具"""
    print_section("示例1: 创建表工具")

    db_manager = DatabaseManager("demo.db")
    create_tool = CreateTableTool(db_manager=db_manager)

    # 创建学生表
    result = create_tool.invoke({
        "table_name": "students",
        "columns": "id INTEGER PRIMARY KEY, name TEXT NOT NULL, grade REAL, age INTEGER"
    })
    print(f"创建学生表: {result}")

    # 创建课程表
    result = create_tool.invoke({
        "table_name": "courses",
        "columns": "id INTEGER PRIMARY KEY, title TEXT NOT NULL, credits INTEGER"
    })
    print(f"创建课程表: {result}")


# ==================== 示例2: 插入数据工具 ====================

class InsertDataInput(BaseModel):
    """插入数据输入模式"""
    table_name: str = Field(description="表名")
    data: Dict[str, Any] = Field(description="要插入的数据（字典格式）")


class InsertDataTool(BaseTool):
    """插入数据工具（使用参数化查询）"""

    name: str = "insert_data"
    description: str = """
    向数据库表中插入数据，使用参数化查询防止SQL注入。

    示例:
    - table_name: "users"
    - data: {"name": "张三", "email": "zhangsan@example.com", "age": 25}
    """
    args_schema: Type[BaseModel] = InsertDataInput
    db_manager: DatabaseManager = None

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def _run(
        self,
        table_name: str,
        data: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行插入操作"""
        try:
            if not data:
                return "错误: 数据不能为空"

            # 验证表名
            if not table_name.replace("_", "").isalnum():
                return f"错误: 无效的表名 '{table_name}'"

            # 构建参数化查询
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # 执行查询
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(data.values()))
                row_id = cursor.lastrowid

            return f"成功插入数据，ID: {row_id}"

        except sqlite3.IntegrityError as e:
            return f"完整性错误: {str(e)}"
        except sqlite3.Error as e:
            return f"数据库错误: {str(e)}"
        except Exception as e:
            return f"错误: {str(e)}"


def demo_insert_data():
    """示例2: 插入数据工具"""
    print_section("示例2: 插入数据工具")

    db_manager = DatabaseManager("demo.db")
    db_manager.create_tables()

    insert_tool = InsertDataTool(db_manager=db_manager)

    # 插入用户数据
    users = [
        {"name": "张三", "email": "zhangsan@example.com", "age": 25},
        {"name": "李四", "email": "lisi@example.com", "age": 30},
        {"name": "王五", "email": "wangwu@example.com", "age": 28},
    ]

    print("插入用户数据:")
    for user in users:
        result = insert_tool.invoke({"table_name": "users", "data": user})
        print(f"  {result}")

    # 插入产品数据
    products = [
        {"name": "笔记本电脑", "price": 5999.00, "stock": 10, "category": "电子产品"},
        {"name": "无线鼠标", "price": 99.00, "stock": 50, "category": "电子产品"},
        {"name": "机械键盘", "price": 499.00, "stock": 30, "category": "电子产品"},
    ]

    print("\n插入产品数据:")
    for product in products:
        result = insert_tool.invoke({"table_name": "products", "data": product})
        print(f"  {result}")


# ==================== 示例3: 查询数据工具 ====================

class QueryDataInput(BaseModel):
    """查询数据输入模式"""
    table_name: str = Field(description="表名")
    conditions: Optional[str] = Field(
        default=None,
        description="查询条件（WHERE子句，不含WHERE关键字）"
    )
    limit: Optional[int] = Field(default=10, description="返回记录数量限制")


class QueryDataTool(BaseTool):
    """查询数据工具"""

    name: str = "query_data"
    description: str = """
    从数据库表中查询数据。

    示例:
    - table_name: "users"
    - conditions: "age > 25"
    - limit: 10
    """
    args_schema: Type[BaseModel] = QueryDataInput
    db_manager: DatabaseManager = None

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def _run(
        self,
        table_name: str,
        conditions: Optional[str] = None,
        limit: int = 10,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行查询操作"""
        try:
            # 验证表名
            if not table_name.replace("_", "").isalnum():
                return f"错误: 无效的表名 '{table_name}'"

            # 构建查询
            query = f"SELECT * FROM {table_name}"
            if conditions:
                query += f" WHERE {conditions}"
            query += f" LIMIT {limit}"

            # 执行查询
            results = self.db_manager.execute_query(query)

            if not results:
                return "未找到匹配的记录"

            # 格式化结果
            output = f"找到 {len(results)} 条记录:\n"
            for i, row in enumerate(results, 1):
                output += f"\n记录 {i}:\n"
                for key, value in row.items():
                    output += f"  {key}: {value}\n"

            return output

        except sqlite3.Error as e:
            return f"数据库错误: {str(e)}"
        except Exception as e:
            return f"错误: {str(e)}"


def demo_query_data():
    """示例3: 查询数据工具"""
    print_section("示例3: 查询数据工具")

    db_manager = DatabaseManager("demo.db")
    query_tool = QueryDataTool(db_manager=db_manager)

    # 查询所有用户
    print("查询所有用户:")
    result = query_tool.invoke({"table_name": "users", "limit": 10})
    print(result)

    # 条件查询
    print("\n查询年龄大于26的用户:")
    result = query_tool.invoke({
        "table_name": "users",
        "conditions": "age > 26",
        "limit": 10
    })
    print(result)

    # 查询产品
    print("\n查询价格低于500的产品:")
    result = query_tool.invoke({
        "table_name": "products",
        "conditions": "price < 500",
        "limit": 10
    })
    print(result)


# ==================== 示例4: 更新数据工具 ====================

class UpdateDataInput(BaseModel):
    """更新数据输入模式"""
    table_name: str = Field(description="表名")
    set_values: Dict[str, Any] = Field(description="要更新的字段和值")
    conditions: str = Field(description="更新条件（WHERE子句）")


class UpdateDataTool(BaseTool):
    """更新数据工具"""

    name: str = "update_data"
    description: str = """
    更新数据库表中的数据，使用参数化查询。

    示例:
    - table_name: "users"
    - set_values: {"age": 26, "email": "newemail@example.com"}
    - conditions: "id = 1"
    """
    args_schema: Type[BaseModel] = UpdateDataInput
    db_manager: DatabaseManager = None

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def _run(
        self,
        table_name: str,
        set_values: Dict[str, Any],
        conditions: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行更新操作"""
        try:
            if not set_values:
                return "错误: 更新值不能为空"

            # 验证表名
            if not table_name.replace("_", "").isalnum():
                return f"错误: 无效的表名 '{table_name}'"

            # 构建参数化查询
            set_clause = ", ".join([f"{key} = ?" for key in set_values.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {conditions}"

            # 执行更新
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(set_values.values()))
                affected_rows = cursor.rowcount

            return f"成功更新 {affected_rows} 条记录"

        except sqlite3.Error as e:
            return f"数据库错误: {str(e)}"
        except Exception as e:
            return f"错误: {str(e)}"


def demo_update_data():
    """示例4: 更新数据工具"""
    print_section("示例4: 更新数据工具")

    db_manager = DatabaseManager("demo.db")
    update_tool = UpdateDataTool(db_manager=db_manager)
    query_tool = QueryDataTool(db_manager=db_manager)

    # 查看更新前的数据
    print("更新前的用户数据:")
    result = query_tool.invoke({"table_name": "users", "conditions": "id = 1"})
    print(result)

    # 更新用户年龄
    print("执行更新操作:")
    result = update_tool.invoke({
        "table_name": "users",
        "set_values": {"age": 26},
        "conditions": "id = 1"
    })
    print(f"  {result}")

    # 查看更新后的数据
    print("\n更新后的用户数据:")
    result = query_tool.invoke({"table_name": "users", "conditions": "id = 1"})
    print(result)


# ==================== 示例5: 删除数据工具 ====================

class DeleteDataInput(BaseModel):
    """删除数据输入模式"""
    table_name: str = Field(description="表名")
    conditions: str = Field(description="删除条件（WHERE子句）")


class DeleteDataTool(BaseTool):
    """删除数据工具"""

    name: str = "delete_data"
    description: str = """
    从数据库表中删除数据。

    示例:
    - table_name: "users"
    - conditions: "id = 1"

    警告: 请谨慎使用，删除操作不可恢复！
    """
    args_schema: Type[BaseModel] = DeleteDataInput
    db_manager: DatabaseManager = None

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def _run(
        self,
        table_name: str,
        conditions: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行删除操作"""
        try:
            # 验证表名
            if not table_name.replace("_", "").isalnum():
                return f"错误: 无效的表名 '{table_name}'"

            # 构建删除查询
            query = f"DELETE FROM {table_name} WHERE {conditions}"

            # 执行删除
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                affected_rows = cursor.rowcount

            return f"成功删除 {affected_rows} 条记录"

        except sqlite3.Error as e:
            return f"数据库错误: {str(e)}"
        except Exception as e:
            return f"错误: {str(e)}"


def demo_delete_data():
    """示例5: 删除数据工具"""
    print_section("示例5: 删除数据工具")

    db_manager = DatabaseManager("demo.db")
    delete_tool = DeleteDataTool(db_manager=db_manager)
    query_tool = QueryDataTool(db_manager=db_manager)

    # 查看删除前的数据
    print("删除前的产品数据:")
    result = query_tool.invoke({"table_name": "products"})
    print(result)

    # 删除价格低于100的产品
    print("执行删除操作（删除价格低于100的产品）:")
    result = delete_tool.invoke({
        "table_name": "products",
        "conditions": "price < 100"
    })
    print(f"  {result}")

    # 查看删除后的数据
    print("\n删除后的产品数据:")
    result = query_tool.invoke({"table_name": "products"})
    print(result)


# ==================== 示例6: 事务处理 ====================

class TransactionManager:
    """事务管理器"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def transfer_stock(
        self,
        from_product_id: int,
        to_product_id: int,
        quantity: int
    ) -> Dict[str, Any]:
        """
        在两个产品之间转移库存（事务示例）

        Args:
            from_product_id: 源产品ID
            to_product_id: 目标产品ID
            quantity: 转移数量

        Returns:
            操作结果
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # 检查源产品库存
                cursor.execute(
                    "SELECT stock FROM products WHERE id = ?",
                    (from_product_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "error": "源产品不存在"}

                from_stock = row[0]
                if from_stock < quantity:
                    return {"success": False, "error": "源产品库存不足"}

                # 减少源产品库存
                cursor.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, from_product_id)
                )

                # 增加目标产品库存
                cursor.execute(
                    "UPDATE products SET stock = stock + ? WHERE id = ?",
                    (quantity, to_product_id)
                )

                return {
                    "success": True,
                    "message": f"成功转移 {quantity} 件库存",
                    "from_product": from_product_id,
                    "to_product": to_product_id
                }

        except Exception as e:
            return {"success": False, "error": str(e)}


def demo_transaction():
    """示例6: 事务处理"""
    print_section("示例6: 事务处理")

    db_manager = DatabaseManager("demo.db")
    transaction_mgr = TransactionManager(db_manager)
    query_tool = QueryDataTool(db_manager=db_manager)

    # 查看转移前的库存
    print("转移前的产品库存:")
    result = query_tool.invoke({"table_name": "products"})
    print(result)

    # 执行库存转移
    print("执行库存转移（从产品1转移10件到产品2）:")
    result = transaction_mgr.transfer_stock(
        from_product_id=1,
        to_product_id=2,
        quantity=5
    )

    if result["success"]:
        print(f"  ✓ {result['message']}")
    else:
        print(f"  ✗ {result['error']}")

    # 查看转移后的库存
    print("\n转移后的产品库存:")
    result = query_tool.invoke({"table_name": "products"})
    print(result)


# ==================== 示例7: 批量操作 ====================

def demo_batch_operations():
    """示例7: 批量操作"""
    print_section("示例7: 批量操作")

    db_manager = DatabaseManager("demo.db")

    # 批量插入订单
    print("批量插入订单数据:")
    orders = [
        (1, 1, 2, 11998.00),
        (1, 2, 1, 99.00),
        (2, 1, 1, 5999.00),
        (3, 3, 2, 998.00),
    ]

    query = """
        INSERT INTO orders (user_id, product_id, quantity, total_price)
        VALUES (?, ?, ?, ?)
    """

    affected = db_manager.execute_many(query, orders)
    print(f"  成功插入 {affected} 条订单记录")

    # 查询订单
    print("\n查询所有订单:")
    results = db_manager.execute_query("SELECT * FROM orders")
    for order in results:
        print(f"  订单ID: {order['id']}, "
              f"用户ID: {order['user_id']}, "
              f"产品ID: {order['product_id']}, "
              f"数量: {order['quantity']}, "
              f"总价: {order['total_price']}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 04: 数据库工具")
    print("="*70)

    try:
        # 清理旧数据库
        if os.path.exists("demo.db"):
            os.remove("demo.db")

        # 示例1: 创建表
        demo_create_table()

        # 示例2: 插入数据
        demo_insert_data()

        # 示例3: 查询数据
        demo_query_data()

        # 示例4: 更新数据
        demo_update_data()

        # 示例5: 删除数据
        demo_delete_data()

        # 示例6: 事务处理
        demo_transaction()

        # 示例7: 批量操作
        demo_batch_operations()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("  提示: 数据库文件保存在 demo.db")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理演示数据库（可选）
        # if os.path.exists("demo.db"):
        #     os.remove("demo.db")
        pass


if __name__ == "__main__":
    main()
