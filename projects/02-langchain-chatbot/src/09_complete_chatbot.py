"""
LangChain 聊天机器人 - 09: 完整聊天机器人系统

本模块演示：
1. 集成所有功能的完整聊天机器人
2. 多种记忆策略切换
3. 会话管理与持久化
4. 流式输出与打字机效果
5. 用户配置与个性化
6. 命令系统（清除历史、切换模式等）
7. 生产级错误处理
8. 性能监控与日志
"""

import os
import sys
import time
import json
import sqlite3
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationTokenBufferMemory
)


# ==================== 配置管理 ====================

class ChatbotConfig:
    """聊天机器人配置"""

    def __init__(self, config_path: str = "chat_data/config.json"):
        """
        初始化配置

        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # 默认配置
        self.default_config = {
            "model": {
                "name": "deepseek-v4-flash",
                "temperature": 0.7,
                "max_tokens": 2000,
                "streaming": True
            },
            "memory": {
                "type": "buffer_window",  # buffer, buffer_window, summary, token_buffer
                "window_size": 10,
                "max_tokens": 2000
            },
            "persistence": {
                "enabled": True,
                "backend": "sqlite",  # json, sqlite
                "auto_save": True
            },
            "ui": {
                "show_typing_effect": True,
                "typing_delay": 0.02,
                "show_timestamps": True,
                "color_enabled": True
            },
            "system": {
                "log_enabled": True,
                "log_level": "INFO",
                "max_history_days": 30
            }
        }

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return self.default_config.copy()

    def save_config(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key_path: 配置路径，如 "model.temperature"
            default: 默认值
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        设置配置值

        Args:
            key_path: 配置路径
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value
        self.save_config()


# ==================== 历史管理 ====================

class ChatHistory:
    """统一的聊天历史管理接口"""

    def __init__(self, db_path: str, session_id: str):
        """
        初始化历史管理器

        Args:
            db_path: 数据库路径
            session_id: 会话ID
        """
        self.db_path = db_path
        self.session_id = session_id
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tokens INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session
            ON messages(session_id)
        """)

        conn.commit()
        conn.close()

    def add_message(self, role: str, content: str, tokens: int = 0):
        """添加消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
            (session_id, role, content, timestamp, tokens, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.session_id,
            role,
            content,
            datetime.now().isoformat(),
            tokens,
            json.dumps({})
        ))

        conn.commit()
        conn.close()

    def get_messages(self, limit: Optional[int] = None) -> List[BaseMessage]:
        """获取消息历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (self.session_id,))
        rows = cursor.fetchall()
        conn.close()

        messages = []
        for role, content in rows:
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))

        return messages

    def get_recent_messages(self, count: int = 10) -> List[BaseMessage]:
        """获取最近的N条消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (self.session_id, count))

        rows = cursor.fetchall()
        conn.close()

        # 反转顺序（最早的在前）
        messages = []
        for role, content in reversed(rows):
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))

        return messages

    def clear(self):
        """清除历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM messages
            WHERE session_id = ?
        """, (self.session_id,))

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_msgs,
                SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) as ai_msgs,
                SUM(tokens) as total_tokens
            FROM messages
            WHERE session_id = ?
        """, (self.session_id,))

        row = cursor.fetchone()
        conn.close()

        return {
            "total_messages": row[0],
            "user_messages": row[1],
            "ai_messages": row[2],
            "total_tokens": row[3]
        }


# ==================== 流式回调 ====================

class TypingEffectCallback(BaseCallbackHandler):
    """打字机效果回调处理器"""

    def __init__(self, delay: float = 0.02, enable_color: bool = True):
        """
        初始化回调处理器

        Args:
            delay: 打字延迟（秒）
            enable_color: 是否启用颜色
        """
        self.delay = delay
        self.enable_color = enable_color
        self.tokens = []
        self.start_time = None

    def on_llm_start(self, *args, **kwargs):
        """LLM开始时调用"""
        self.tokens = []
        self.start_time = time.time()

        if self.enable_color:
            sys.stdout.write("\033[92m")  # 绿色

    def on_llm_new_token(self, token: str, **kwargs):
        """接收新token时调用"""
        sys.stdout.write(token)
        sys.stdout.flush()
        time.sleep(self.delay)
        self.tokens.append(token)

    def on_llm_end(self, *args, **kwargs):
        """LLM结束时调用"""
        if self.enable_color:
            sys.stdout.write("\033[0m")  # 重置颜色

        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"\n\n[生成耗时: {elapsed:.2f}s, Tokens: {len(self.tokens)}]")

    def get_full_text(self) -> str:
        """获取完整文本"""
        return "".join(self.tokens)


# ==================== 完整聊天机器人 ====================

class CompleteChatbot:
    """完整的聊天机器人系统"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        config_path: str = "chat_data/config.json"
    ):
        """
        初始化聊天机器人

        Args:
            session_id: 会话ID，如果为None则生成新的
            config_path: 配置文件路径
        """
        # 加载环境变量
        load_dotenv()

        # 初始化配置
        self.config = ChatbotConfig(config_path)

        # 生成或使用会话ID
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 初始化历史管理
        self.history = ChatHistory(
            "chat_data/complete_chatbot.db",
            self.session_id
        )

        # 初始化LLM
        self.llm = self._init_llm()

        # 系统提示
        self.system_prompt = """你是一个友好、专业的AI助手。你的特点：
1. 回答简洁明了，但不失详细
2. 能够记住对话历史
3. 对不确定的事情会坦诚说明
4. 积极帮助用户解决问题"""

        # 添加系统消息到历史
        if not self.history.get_messages():
            self.history.add_message("system", self.system_prompt)

        print(f"\n{'='*70}")
        print(f"  完整聊天机器人系统")
        print(f"{'='*70}")
        print(f"会话ID: {self.session_id}")
        print(f"模型: {self.config.get('model.name')}")
        print(f"记忆类型: {self.config.get('memory.type')}")
        print(f"{'='*70}\n")

    def _init_llm(self) -> ChatOpenAI:
        """初始化大语言模型"""
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

        if not api_key:
            raise ValueError("未找到 API Key，请配置 .env 文件")

        return ChatOpenAI(
            model=self.config.get('model.name'),
            temperature=self.config.get('model.temperature'),
            max_tokens=self.config.get('model.max_tokens'),
            streaming=self.config.get('model.streaming'),
            api_key=api_key,
            base_url=api_base
        )

    def _get_context_messages(self) -> List[BaseMessage]:
        """根据配置获取上下文消息"""
        memory_type = self.config.get('memory.type')

        if memory_type == "buffer":
            # 获取所有历史
            return self.history.get_messages()

        elif memory_type == "buffer_window":
            # 获取最近N条消息
            window_size = self.config.get('memory.window_size', 10)
            return self.history.get_recent_messages(window_size)

        elif memory_type == "token_buffer":
            # 简化实现：获取最近的消息直到达到token限制
            max_tokens = self.config.get('memory.max_tokens', 2000)
            messages = self.history.get_recent_messages(20)

            # 粗略估计：每个消息约100 tokens
            estimated_tokens = len(messages) * 100
            if estimated_tokens > max_tokens:
                # 截断消息
                keep_count = max_tokens // 100
                messages = messages[-keep_count:]

            return messages

        else:
            return self.history.get_messages()

    def chat(self, user_input: str) -> str:
        """
        处理用户输入并返回响应

        Args:
            user_input: 用户输入

        Returns:
            AI响应
        """
        # 检查是否为命令
        if user_input.startswith('/'):
            return self._handle_command(user_input)

        # 保存用户消息
        self.history.add_message("user", user_input)

        # 获取上下文
        context_messages = self._get_context_messages()

        try:
            # 创建回调处理器
            if self.config.get('ui.show_typing_effect'):
                callback = TypingEffectCallback(
                    delay=self.config.get('ui.typing_delay', 0.02),
                    enable_color=self.config.get('ui.color_enabled', True)
                )
                self.llm.callbacks = [callback]

                # 调用LLM
                response = self.llm.invoke(context_messages)

                # 获取完整响应
                response_text = callback.get_full_text() or response.content

            else:
                # 不使用流式输出
                self.llm.streaming = False
                response = self.llm.invoke(context_messages)
                response_text = response.content
                print(response_text)

            # 保存AI响应
            self.history.add_message("assistant", response_text)

            return response_text

        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"\n\033[91m{error_msg}\033[0m\n")
            return error_msg

    def _handle_command(self, command: str) -> str:
        """
        处理命令

        支持的命令：
        - /help: 显示帮助
        - /clear: 清除历史
        - /stats: 显示统计
        - /config: 显示配置
        - /memory [type]: 切换记忆类型
        - /exit: 退出
        """
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/help':
            return self._show_help()

        elif cmd == '/clear':
            self.history.clear()
            return "✓ 历史已清除"

        elif cmd == '/stats':
            return self._show_stats()

        elif cmd == '/config':
            return self._show_config()

        elif cmd == '/memory':
            if len(parts) > 1:
                memory_type = parts[1]
                valid_types = ["buffer", "buffer_window", "token_buffer", "summary"]

                if memory_type in valid_types:
                    self.config.set('memory.type', memory_type)
                    return f"✓ 记忆类型已切换为: {memory_type}"
                else:
                    return f"错误: 无效的记忆类型。有效选项: {', '.join(valid_types)}"
            else:
                return f"当前记忆类型: {self.config.get('memory.type')}"

        elif cmd == '/exit':
            return "EXIT"

        else:
            return f"未知命令: {cmd}。输入 /help 查看帮助"

    def _show_help(self) -> str:
        """显示帮助信息"""
        help_text = """
可用命令：
  /help              - 显示此帮助信息
  /clear             - 清除对话历史
  /stats             - 显示会话统计
  /config            - 显示当前配置
  /memory [type]     - 切换记忆类型 (buffer, buffer_window, token_buffer)
  /exit              - 退出聊天

记忆类型说明：
  buffer             - 保留完整历史
  buffer_window      - 保留最近N条消息
  token_buffer       - 根据token数限制历史
"""
        return help_text

    def _show_stats(self) -> str:
        """显示统计信息"""
        stats = self.history.get_stats()

        stats_text = f"""
会话统计：
  会话ID: {self.session_id}
  总消息数: {stats['total_messages']}
  用户消息: {stats['user_messages']}
  AI消息: {stats['ai_messages']}
  总Tokens: {stats['total_tokens']}
"""
        return stats_text

    def _show_config(self) -> str:
        """显示配置信息"""
        config_text = f"""
当前配置：
  模型: {self.config.get('model.name')}
  温度: {self.config.get('model.temperature')}
  记忆类型: {self.config.get('memory.type')}
  窗口大小: {self.config.get('memory.window_size')}
  流式输出: {self.config.get('model.streaming')}
  打字效果: {self.config.get('ui.show_typing_effect')}
"""
        return config_text

    def run(self):
        """运行交互式聊天循环"""
        print("开始聊天！输入 /help 查看命令，输入 /exit 退出\n")

        while True:
            try:
                # 获取用户输入
                user_input = input("\n\033[94m你: \033[0m").strip()

                if not user_input:
                    continue

                # 显示时间戳
                if self.config.get('ui.show_timestamps'):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{timestamp}]", end=" ")

                print("\033[92mAI: \033[0m", end="")

                # 处理输入
                response = self.chat(user_input)

                # 检查是否退出
                if response == "EXIT":
                    print("\n再见！")
                    break

            except KeyboardInterrupt:
                print("\n\n收到中断信号，退出...")
                break

            except EOFError:
                print("\n\n输入结束，退出...")
                break

            except Exception as e:
                print(f"\n错误: {str(e)}")
                import traceback
                traceback.print_exc()


# ==================== 演示函数 ====================

def demo_complete_chatbot():
    """示例1: 完整聊天机器人演示"""
    print("\n" + "="*70)
    print("  完整聊天机器人演示")
    print("="*70)

    # 创建聊天机器人
    bot = CompleteChatbot()

    # 模拟对话
    conversations = [
        "你好！",
        "我想学习Python编程",
        "能推荐一些好的学习资源吗？",
        "/stats",
        "/config"
    ]

    for user_input in conversations:
        print(f"\n\033[94m你: \033[0m{user_input}")
        print("\033[92mAI: \033[0m", end="")

        response = bot.chat(user_input)

        if not bot.config.get('ui.show_typing_effect'):
            print(response)

        time.sleep(1)  # 演示延迟


def demo_memory_switching():
    """示例2: 记忆类型切换"""
    print("\n" + "="*70)
    print("  记忆类型切换演示")
    print("="*70)

    bot = CompleteChatbot(session_id="memory_test")

    # 测试不同记忆类型
    memory_types = ["buffer", "buffer_window"]

    for mem_type in memory_types:
        print(f"\n--- 使用 {mem_type} 记忆 ---")
        bot.chat(f"/memory {mem_type}")

        # 添加一些对话
        bot.chat("我的名字是张三")
        time.sleep(0.5)

        print(f"\n\033[94m你: \033[0m我叫什么名字？")
        print("\033[92mAI: \033[0m", end="")
        bot.chat("我叫什么名字？")


def demo_persistent_session():
    """示例3: 持久化会话演示"""
    print("\n" + "="*70)
    print("  持久化会话演示")
    print("="*70)

    session_id = "persistent_session_demo"

    # 第一次会话
    print("\n第一次会话：")
    bot1 = CompleteChatbot(session_id=session_id)

    print("\n\033[94m你: \033[0m我喜欢打篮球")
    print("\033[92mAI: \033[0m", end="")
    bot1.chat("我喜欢打篮球")

    print("\n\n--- 模拟程序重启 ---\n")
    time.sleep(1)

    # 第二次会话（恢复）
    print("第二次会话（恢复历史）：")
    bot2 = CompleteChatbot(session_id=session_id)

    print("\n\033[94m你: \033[0m我喜欢什么运动？")
    print("\033[92mAI: \033[0m", end="")
    bot2.chat("我喜欢什么运动？")

    # 显示统计
    print("\n")
    bot2.chat("/stats")


def demo_error_handling():
    """示例4: 错误处理演示"""
    print("\n" + "="*70)
    print("  错误处理演示")
    print("="*70)

    bot = CompleteChatbot()

    # 测试空输入
    print("\n测试1: 空输入")
    response = bot.chat("")
    print(f"响应: {response}")

    # 测试未知命令
    print("\n测试2: 未知命令")
    response = bot.chat("/unknown")
    print(f"响应: {response}")

    # 测试帮助命令
    print("\n测试3: 帮助命令")
    response = bot.chat("/help")
    print(response)


def demo_configuration():
    """示例5: 配置管理演示"""
    print("\n" + "="*70)
    print("  配置管理演示")
    print("="*70)

    # 创建自定义配置
    config = ChatbotConfig("chat_data/custom_config.json")

    print("\n修改配置：")
    config.set("model.temperature", 0.9)
    config.set("memory.window_size", 5)
    config.set("ui.show_typing_effect", False)

    print(f"温度: {config.get('model.temperature')}")
    print(f"窗口大小: {config.get('memory.window_size')}")
    print(f"打字效果: {config.get('ui.show_typing_effect')}")

    # 使用自定义配置创建机器人
    bot = CompleteChatbot(config_path="chat_data/custom_config.json")
    bot.chat("/config")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 09: 完整聊天机器人系统")
    print("="*70)

    try:
        # 示例1: 完整聊天机器人
        demo_complete_chatbot()

        # 示例2: 记忆切换
        demo_memory_switching()

        # 示例3: 持久化会话
        demo_persistent_session()

        # 示例4: 错误处理
        demo_error_handling()

        # 示例5: 配置管理
        demo_configuration()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

        # 询问是否启动交互式聊天
        print("\n是否启动交互式聊天？(y/n): ", end="")
        choice = input().strip().lower()

        if choice == 'y':
            bot = CompleteChatbot()
            bot.run()

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
