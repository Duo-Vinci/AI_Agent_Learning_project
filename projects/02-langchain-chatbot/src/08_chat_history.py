"""
LangChain 聊天机器人 - 08: 对话历史保存与管理

本模块演示：
1. 对话历史持久化（JSON/SQLite）
2. 会话管理与恢复
3. 多用户会话隔离
4. 历史记录查询与过滤
5. 对话导出与导入
6. 历史清理与归档
7. 完整的历史管理系统
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def init_llm():
    """初始化大语言模型"""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise ValueError("未找到 API Key，请配置 .env 文件")

    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )


# ==================== 示例1: JSON文件持久化 ====================

class JSONChatHistory:
    """
    基于JSON文件的对话历史管理器

    特点：
    - 简单易用
    - 人类可读
    - 适合小规模应用
    """

    def __init__(self, file_path: str, session_id: str):
        """
        初始化JSON历史管理器

        Args:
            file_path: JSON文件路径
            session_id: 会话ID
        """
        self.file_path = Path(file_path)
        self.session_id = session_id
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # 初始化文件
        if not self.file_path.exists():
            self._save_data({})

    def _load_data(self) -> Dict[str, List[Dict]]:
        """加载所有会话数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save_data(self, data: Dict[str, List[Dict]]):
        """保存所有会话数据"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_message(self, message: BaseMessage):
        """添加消息到历史"""
        data = self._load_data()

        if self.session_id not in data:
            data[self.session_id] = []

        # 序列化消息
        msg_dict = {
            "type": message.type,
            "content": message.content,
            "timestamp": datetime.now().isoformat()
        }

        data[self.session_id].append(msg_dict)
        self._save_data(data)

    def get_messages(self) -> List[BaseMessage]:
        """获取当前会话的所有消息"""
        data = self._load_data()
        messages = data.get(self.session_id, [])

        # 反序列化消息
        result = []
        for msg in messages:
            if msg["type"] == "human":
                result.append(HumanMessage(content=msg["content"]))
            elif msg["type"] == "ai":
                result.append(AIMessage(content=msg["content"]))
            elif msg["type"] == "system":
                result.append(SystemMessage(content=msg["content"]))

        return result

    def clear(self):
        """清除当前会话的历史"""
        data = self._load_data()
        if self.session_id in data:
            del data[self.session_id]
            self._save_data(data)

    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        data = self._load_data()
        return list(data.keys())


def demo_json_persistence():
    """示例1: JSON文件持久化"""
    print_section("示例1: JSON文件持久化")

    llm = init_llm()
    history_path = "chat_data/history.json"

    # 创建会话1
    session1 = JSONChatHistory(history_path, "user_001")

    print("会话1 - 第一轮对话：")
    session1.add_message(HumanMessage(content="我叫张三"))
    messages = session1.get_messages()
    messages.append(HumanMessage(content="我叫张三"))

    response = llm.invoke(messages)
    session1.add_message(response)
    print(f"用户: 我叫张三")
    print(f"AI: {response.content}\n")

    print("会话1 - 第二轮对话：")
    session1.add_message(HumanMessage(content="我叫什么名字？"))
    messages = session1.get_messages()

    response = llm.invoke(messages)
    session1.add_message(response)
    print(f"用户: 我叫什么名字？")
    print(f"AI: {response.content}\n")

    # 创建会话2
    session2 = JSONChatHistory(history_path, "user_002")

    print("会话2 - 独立对话：")
    session2.add_message(HumanMessage(content="你好"))
    messages2 = session2.get_messages()
    messages2.append(HumanMessage(content="你好"))

    response = llm.invoke(messages2)
    session2.add_message(response)
    print(f"用户: 你好")
    print(f"AI: {response.content}\n")

    # 显示所有会话
    print(f"所有会话ID: {session1.get_all_sessions()}")


# ==================== 示例2: SQLite数据库持久化 ====================

class SQLiteChatHistory:
    """
    基于SQLite的对话历史管理器

    特点：
    - 高效查询
    - 支持复杂过滤
    - 适合大规模应用
    """

    def __init__(self, db_path: str, session_id: str):
        """
        初始化SQLite历史管理器

        Args:
            db_path: 数据库文件路径
            session_id: 会话ID
        """
        self.db_path = db_path
        self.session_id = session_id

        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # 初始化数据库
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id
            ON chat_history(session_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON chat_history(timestamp)
        """)

        conn.commit()
        conn.close()

    def add_message(self, message: BaseMessage):
        """添加消息到历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO chat_history
            (session_id, message_type, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.session_id,
            message.type,
            message.content,
            datetime.now().isoformat(),
            json.dumps({})
        ))

        conn.commit()
        conn.close()

    def get_messages(self, limit: Optional[int] = None) -> List[BaseMessage]:
        """获取当前会话的消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT message_type, content
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (self.session_id,))
        rows = cursor.fetchall()
        conn.close()

        # 转换为消息对象
        messages = []
        for msg_type, content in rows:
            if msg_type == "human":
                messages.append(HumanMessage(content=content))
            elif msg_type == "ai":
                messages.append(AIMessage(content=content))
            elif msg_type == "system":
                messages.append(SystemMessage(content=content))

        return messages

    def get_messages_by_date(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """根据日期范围查询消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT message_type, content, timestamp
            FROM chat_history
            WHERE session_id = ?
        """
        params = [self.session_id]

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "type": row[0],
                "content": row[1],
                "timestamp": row[2]
            }
            for row in rows
        ]

    def clear(self):
        """清除当前会话的历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM chat_history
            WHERE session_id = ?
        """, (self.session_id,))

        conn.commit()
        conn.close()

    def get_session_count(self) -> int:
        """获取会话的消息数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM chat_history
            WHERE session_id = ?
        """, (self.session_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT session_id
            FROM chat_history
        """)

        sessions = [row[0] for row in cursor.fetchall()]
        conn.close()

        return sessions


def demo_sqlite_persistence():
    """示例2: SQLite数据库持久化"""
    print_section("示例2: SQLite数据库持久化")

    llm = init_llm()
    db_path = "chat_data/chat_history.db"

    # 创建会话
    history = SQLiteChatHistory(db_path, "user_sqlite_001")

    # 模拟多轮对话
    conversations = [
        ("我是一名Python开发者", None),
        ("我想学习机器学习", None),
        ("推荐一些学习资源", None)
    ]

    for user_msg, _ in conversations:
        print(f"用户: {user_msg}")

        # 添加用户消息
        history.add_message(HumanMessage(content=user_msg))

        # 获取历史并调用LLM
        messages = history.get_messages()
        response = llm.invoke(messages)

        # 保存AI响应
        history.add_message(response)
        print(f"AI: {response.content}\n")

    # 查询统计
    print(f"当前会话消息数: {history.get_session_count()}")
    print(f"所有会话: {history.get_all_sessions()}")


# ==================== 示例3: 会话管理器 ====================

class SessionManager:
    """
    会话管理器

    功能：
    - 多用户会话隔离
    - 自动过期清理
    - 会话统计
    """

    def __init__(self, db_path: str):
        """
        初始化会话管理器

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化会话元数据表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                message_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)

        conn.commit()
        conn.close()

    def create_session(self, session_id: str, user_id: str) -> SQLiteChatHistory:
        """创建新会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, user_id, created_at, last_active, message_count, metadata)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (session_id, user_id, now, now, json.dumps({})))

        conn.commit()
        conn.close()

        return SQLiteChatHistory(self.db_path, session_id)

    def get_session(self, session_id: str) -> Optional[SQLiteChatHistory]:
        """获取已存在的会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id FROM sessions
            WHERE session_id = ?
        """, (session_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            # 更新最后活跃时间
            self._update_last_active(session_id)
            return SQLiteChatHistory(self.db_path, session_id)

        return None

    def _update_last_active(self, session_id: str):
        """更新会话最后活跃时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sessions
            SET last_active = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))

        conn.commit()
        conn.close()

    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, created_at, last_active, message_count
            FROM sessions
            WHERE user_id = ?
            ORDER BY last_active DESC
        """, (user_id,))

        sessions = [
            {
                "session_id": row[0],
                "created_at": row[1],
                "last_active": row[2],
                "message_count": row[3]
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return sessions

    def cleanup_expired_sessions(self, days: int = 30):
        """清理过期会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # 获取要删除的会话
        cursor.execute("""
            SELECT session_id FROM sessions
            WHERE last_active < ?
        """, (cutoff_date,))

        expired_sessions = [row[0] for row in cursor.fetchall()]

        # 删除会话数据
        for session_id in expired_sessions:
            cursor.execute("""
                DELETE FROM chat_history
                WHERE session_id = ?
            """, (session_id,))

        # 删除会话元数据
        cursor.execute("""
            DELETE FROM sessions
            WHERE last_active < ?
        """, (cutoff_date,))

        conn.commit()
        conn.close()

        return len(expired_sessions)


def demo_session_manager():
    """示例3: 会话管理器"""
    print_section("示例3: 会话管理器")

    db_path = "chat_data/managed_sessions.db"
    manager = SessionManager(db_path)

    # 创建多个用户的会话
    print("创建多个会话：")
    session1 = manager.create_session("session_001", "user_alice")
    session2 = manager.create_session("session_002", "user_alice")
    session3 = manager.create_session("session_003", "user_bob")

    # 添加一些消息
    session1.add_message(HumanMessage(content="Hello from session 1"))
    session1.add_message(AIMessage(content="Hi there!"))

    session2.add_message(HumanMessage(content="Hello from session 2"))

    print("会话创建完成\n")

    # 查询用户会话
    print("用户 alice 的所有会话：")
    alice_sessions = manager.get_user_sessions("user_alice")
    for sess in alice_sessions:
        print(f"  - {sess['session_id']}: {sess['message_count']} 条消息, "
              f"最后活跃: {sess['last_active']}")

    print("\n用户 bob 的所有会话：")
    bob_sessions = manager.get_user_sessions("user_bob")
    for sess in bob_sessions:
        print(f"  - {sess['session_id']}: {sess['message_count']} 条消息")


# ==================== 示例4: 对话导出与导入 ====================

class ChatHistoryExporter:
    """对话历史导出器"""

    @staticmethod
    def export_to_json(
        history: SQLiteChatHistory,
        output_path: str
    ):
        """导出为JSON格式"""
        messages = history.get_messages()

        data = {
            "session_id": history.session_id,
            "exported_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": [
                {
                    "type": msg.type,
                    "content": msg.content
                }
                for msg in messages
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_to_markdown(
        history: SQLiteChatHistory,
        output_path: str
    ):
        """导出为Markdown格式"""
        messages = history.get_messages()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 对话历史\n\n")
            f.write(f"**会话ID**: {history.session_id}\n\n")
            f.write(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**消息数量**: {len(messages)}\n\n")
            f.write("---\n\n")

            for i, msg in enumerate(messages, 1):
                if msg.type == "human":
                    f.write(f"### 消息 {i} - 用户\n\n")
                elif msg.type == "ai":
                    f.write(f"### 消息 {i} - AI\n\n")
                else:
                    f.write(f"### 消息 {i} - 系统\n\n")

                f.write(f"{msg.content}\n\n")

    @staticmethod
    def import_from_json(
        json_path: str,
        history: SQLiteChatHistory
    ):
        """从JSON导入"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for msg_data in data["messages"]:
            if msg_data["type"] == "human":
                history.add_message(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "ai":
                history.add_message(AIMessage(content=msg_data["content"]))
            elif msg_data["type"] == "system":
                history.add_message(SystemMessage(content=msg_data["content"]))


def demo_export_import():
    """示例4: 对话导出与导入"""
    print_section("示例4: 对话导出与导入")

    db_path = "chat_data/export_test.db"

    # 创建会话并添加消息
    history = SQLiteChatHistory(db_path, "export_session")
    history.add_message(HumanMessage(content="你好"))
    history.add_message(AIMessage(content="你好！有什么可以帮助你的吗？"))
    history.add_message(HumanMessage(content="介绍一下Python"))
    history.add_message(AIMessage(content="Python是一种高级编程语言..."))

    # 导出
    export_dir = Path("chat_data/exports")
    export_dir.mkdir(parents=True, exist_ok=True)

    json_path = export_dir / "conversation.json"
    md_path = export_dir / "conversation.md"

    print("导出对话历史...")
    ChatHistoryExporter.export_to_json(history, str(json_path))
    ChatHistoryExporter.export_to_markdown(history, str(md_path))

    print(f"✓ JSON导出: {json_path}")
    print(f"✓ Markdown导出: {md_path}")

    # 导入到新会话
    print("\n从JSON导入到新会话...")
    new_history = SQLiteChatHistory(db_path, "imported_session")
    ChatHistoryExporter.import_from_json(str(json_path), new_history)

    imported_messages = new_history.get_messages()
    print(f"✓ 导入完成，共 {len(imported_messages)} 条消息")


# ==================== 示例5: 历史统计与分析 ====================

class ChatHistoryAnalyzer:
    """对话历史分析器"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_total_messages(self, session_id: Optional[str] = None) -> int:
        """获取消息总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if session_id:
            cursor.execute("""
                SELECT COUNT(*) FROM chat_history
                WHERE session_id = ?
            """, (session_id,))
        else:
            cursor.execute("SELECT COUNT(*) FROM chat_history")

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_message_stats(self) -> Dict[str, Any]:
        """获取消息统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 按类型统计
        cursor.execute("""
            SELECT message_type, COUNT(*)
            FROM chat_history
            GROUP BY message_type
        """)
        type_stats = dict(cursor.fetchall())

        # 按会话统计
        cursor.execute("""
            SELECT session_id, COUNT(*)
            FROM chat_history
            GROUP BY session_id
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)
        session_stats = cursor.fetchall()

        conn.close()

        return {
            "by_type": type_stats,
            "top_sessions": session_stats
        }

    def get_activity_by_date(self) -> List[Dict[str, Any]]:
        """获取按日期的活动统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as message_count,
                COUNT(DISTINCT session_id) as session_count
            FROM chat_history
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        """)

        stats = [
            {
                "date": row[0],
                "messages": row[1],
                "sessions": row[2]
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return stats


def demo_history_analysis():
    """示例5: 历史统计与分析"""
    print_section("示例5: 历史统计与分析")

    db_path = "chat_data/chat_history.db"
    analyzer = ChatHistoryAnalyzer(db_path)

    # 总体统计
    total = analyzer.get_total_messages()
    print(f"消息总数: {total}")

    # 详细统计
    stats = analyzer.get_message_stats()

    print("\n按类型统计:")
    for msg_type, count in stats["by_type"].items():
        print(f"  {msg_type}: {count} 条")

    print("\n最活跃会话 (Top 5):")
    for session_id, count in stats["top_sessions"][:5]:
        print(f"  {session_id}: {count} 条消息")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 08: 对话历史保存与管理")
    print("="*70)

    try:
        # 示例1: JSON持久化
        demo_json_persistence()

        # 示例2: SQLite持久化
        demo_sqlite_persistence()

        # 示例3: 会话管理器
        demo_session_manager()

        # 示例4: 导出与导入
        demo_export_import()

        # 示例5: 历史分析
        demo_history_analysis()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
