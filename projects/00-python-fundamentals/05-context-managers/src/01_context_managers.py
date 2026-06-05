"""
上下文管理器
===========

本模块介绍Python上下文管理器：
- with 语句
- 自定义上下文管理器
- contextlib 模块
- 异步上下文管理器
- 实际应用场景

在AI开发中，上下文管理器用于：
- 数据库连接管理
- 文件操作
- LLM会话管理
- 资源清理
- 临时配置
"""

import time
from typing import Optional, Any
from contextlib import contextmanager, suppress, redirect_stdout
import io


# ============================================================================
# 1. with 语句基础
# ============================================================================

def basic_with_example():
    """with 语句基础示例"""
    print("\n【示例1】with 语句基础")
    print("=" * 60)

    # 1. 文件操作（自动关闭）
    print("\n1. 文件操作:")

    # 不使用 with（需要手动关闭）
    print("  不使用 with:")
    file = open("temp1.txt", "w", encoding='utf-8')
    file.write("Hello, World!")
    file.close()
    print("    文件已写入（需手动关闭）")

    # 使用 with（自动关闭）
    print("\n  使用 with:")
    with open("temp2.txt", "w", encoding='utf-8') as file:
        file.write("Hello, Python!")
        print("    文件已写入（自动关闭）")
    # 离开 with 块后，文件自动关闭

    # 验证文件已关闭
    print(f"    文件已关闭: {file.closed}")

    # 清理
    import os
    os.remove("temp1.txt")
    os.remove("temp2.txt")


# ============================================================================
# 2. 自定义上下文管理器（类方式）
# ============================================================================

class Timer:
    """
    计时上下文管理器

    测量代码块的执行时间
    """

    def __init__(self, name: str = "代码块"):
        self.name = name
        self.start_time: Optional[float] = None
        self.elapsed: Optional[float] = None

    def __enter__(self):
        """进入上下文时调用"""
        print(f"  [{self.name}] 开始执行")
        self.start_time = time.time()
        return self  # 返回自身，可以在 as 中使用

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时调用

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯信息

        Returns:
            True 表示抑制异常，False 表示传播异常
        """
        self.elapsed = time.time() - self.start_time
        print(f"  [{self.name}] 执行完成，耗时: {self.elapsed:.4f}秒")

        # 返回 False 表示不抑制异常
        return False


class DatabaseConnection:
    """
    数据库连接上下文管理器

    模拟数据库连接的管理
    """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connected = False

    def __enter__(self):
        """建立连接"""
        print(f"  连接到数据库: {self.db_name}")
        self.connected = True
        time.sleep(0.5)  # 模拟连接延迟
        print(f"  ✓ 连接成功")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """关闭连接"""
        print(f"  关闭数据库连接: {self.db_name}")
        self.connected = False
        time.sleep(0.3)  # 模拟关闭延迟
        print(f"  ✓ 连接已关闭")
        return False

    def query(self, sql: str) -> list:
        """执行查询"""
        if not self.connected:
            raise RuntimeError("数据库未连接")
        print(f"  执行查询: {sql}")
        return [{"id": 1, "name": "示例数据"}]


def custom_context_manager_example():
    """自定义上下文管理器示例"""
    print("\n【示例2】自定义上下文管理器（类方式）")
    print("=" * 60)

    # 计时器
    print("\n1. 计时器:")
    with Timer("耗时操作") as timer:
        time.sleep(1)
        print(f"    执行某些操作...")

    # 数据库连接
    print("\n2. 数据库连接:")
    with DatabaseConnection("users_db") as db:
        result = db.query("SELECT * FROM users")
        print(f"    查询结果: {result}")


# ============================================================================
# 3. 使用 @contextmanager 装饰器
# ============================================================================

@contextmanager
def temporary_value(obj: dict, key: str, value: Any):
    """
    临时修改字典的值

    使用 @contextmanager 装饰器创建上下文管理器
    更简洁，适用于简单场景
    """
    # __enter__ 部分
    old_value = obj.get(key)
    obj[key] = value
    print(f"  临时设置 {key}={value} (原值: {old_value})")

    try:
        yield obj  # yield 的值会传递给 as 子句
    finally:
        # __exit__ 部分（在 finally 中确保执行）
        if old_value is None:
            obj.pop(key, None)
        else:
            obj[key] = old_value
        print(f"  恢复 {key}={old_value}")


@contextmanager
def llm_session(model: str, temperature: float = 0.7):
    """
    LLM会话上下文管理器

    管理LLM会话的生命周期
    """
    print(f"  创建LLM会话: {model} (temperature={temperature})")

    # 模拟会话对象
    session = {
        "model": model,
        "temperature": temperature,
        "messages": []
    }

    try:
        yield session
    finally:
        # 清理资源
        message_count = len(session["messages"])
        print(f"  关闭LLM会话 (处理了 {message_count} 条消息)")


@contextmanager
def error_handler(operation_name: str):
    """
    错误处理上下文管理器

    统一处理错误
    """
    print(f"  开始: {operation_name}")
    try:
        yield
        print(f"  ✓ {operation_name} 成功")
    except Exception as e:
        print(f"  ✗ {operation_name} 失败: {e}")
        raise


def contextmanager_decorator_example():
    """@contextmanager 装饰器示例"""
    print("\n【示例3】@contextmanager 装饰器")
    print("=" * 60)

    # 临时值
    print("\n1. 临时修改配置:")
    config = {"debug": False, "timeout": 30}
    print(f"  原始配置: {config}")

    with temporary_value(config, "debug", True):
        print(f"  临时配置: {config}")
        # 在这里 debug=True

    print(f"  恢复配置: {config}")

    # LLM会话
    print("\n2. LLM会话:")
    with llm_session("gpt-4", temperature=0.8) as session:
        session["messages"].append({"role": "user", "content": "Hello"})
        session["messages"].append({"role": "assistant", "content": "Hi!"})
        print(f"  会话中: {len(session['messages'])} 条消息")

    # 错误处理
    print("\n3. 错误处理:")
    with error_handler("数据处理"):
        data = [1, 2, 3]
        result = sum(data)
        print(f"    结果: {result}")


# ============================================================================
# 4. contextlib 工具
# ============================================================================

def contextlib_tools_example():
    """contextlib 工具示例"""
    print("\n【示例4】contextlib 工具")
    print("=" * 60)

    # 1. suppress - 抑制指定的异常
    print("\n1. suppress - 抑制异常:")

    # 不使用 suppress
    print("  不使用 suppress:")
    try:
        result = 10 / 0
    except ZeroDivisionError:
        print("    捕获到异常")

    # 使用 suppress
    print("\n  使用 suppress:")
    with suppress(ZeroDivisionError):
        result = 10 / 0
        print("    这行不会执行")
    print("    程序继续执行")

    # 2. redirect_stdout - 重定向标准输出
    print("\n2. redirect_stdout - 重定向输出:")

    output = io.StringIO()
    with redirect_stdout(output):
        print("这些内容被重定向了")
        print("不会显示在控制台")

    captured = output.getvalue()
    print(f"  捕获的输出: {repr(captured)}")


# ============================================================================
# 5. 嵌套上下文管理器
# ============================================================================

def nested_context_managers_example():
    """嵌套上下文管理器示例"""
    print("\n【示例5】嵌套上下文管理器")
    print("=" * 60)

    # 方式1: 多个 with 语句
    print("\n1. 多个 with 语句:")
    with Timer("外层"):
        with Timer("内层"):
            time.sleep(0.5)

    # 方式2: 逗号分隔（Python 3.1+）
    print("\n2. 逗号分隔（推荐）:")
    with Timer("任务1"), Timer("任务2"):
        time.sleep(0.3)

    # 方式3: 多个资源
    print("\n3. 管理多个资源:")
    with (
        open("temp_a.txt", "w", encoding='utf-8') as file_a,
        open("temp_b.txt", "w", encoding='utf-8') as file_b
    ):
        file_a.write("文件A")
        file_b.write("文件B")
        print("  两个文件都已写入")

    # 清理
    import os
    os.remove("temp_a.txt")
    os.remove("temp_b.txt")


# ============================================================================
# 6. 异步上下文管理器
# ============================================================================

import asyncio


class AsyncTimer:
    """
    异步计时器

    使用 async with 语法
    """

    def __init__(self, name: str = "异步代码块"):
        self.name = name
        self.start_time: Optional[float] = None

    async def __aenter__(self):
        """异步进入"""
        print(f"  [{self.name}] 开始")
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出"""
        elapsed = time.time() - self.start_time
        print(f"  [{self.name}] 完成，耗时: {elapsed:.4f}秒")
        return False


class AsyncLLMSession:
    """
    异步LLM会话

    管理异步LLM调用
    """

    def __init__(self, model: str):
        self.model = model
        self.session_id = None

    async def __aenter__(self):
        """建立会话"""
        print(f"  建立异步LLM会话: {self.model}")
        await asyncio.sleep(0.3)  # 模拟异步初始化
        self.session_id = "session_123"
        print(f"  ✓ 会话ID: {self.session_id}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """关闭会话"""
        print(f"  关闭会话: {self.session_id}")
        await asyncio.sleep(0.2)  # 模拟异步清理
        print(f"  ✓ 会话已关闭")
        return False

    async def generate(self, prompt: str) -> str:
        """异步生成"""
        await asyncio.sleep(1)  # 模拟LLM推理
        return f"[{self.model}] 响应: {prompt}"


async def async_context_manager_example():
    """异步上下文管理器示例"""
    print("\n【示例6】异步上下文管理器")
    print("=" * 60)

    # 异步计时器
    print("\n1. 异步计时器:")
    async with AsyncTimer("异步操作"):
        await asyncio.sleep(0.5)
        print("    执行异步任务...")

    # 异步LLM会话
    print("\n2. 异步LLM会话:")
    async with AsyncLLMSession("gpt-4") as session:
        response = await session.generate("什么是AI?")
        print(f"    {response}")


# ============================================================================
# 7. AI应用：完整的资源管理
# ============================================================================

class LLMClient:
    """
    LLM客户端（带资源管理）

    完整的资源管理示例
    """

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.connected = False
        self.request_count = 0

    def __enter__(self):
        """初始化客户端"""
        print(f"  初始化LLM客户端: {self.model}")
        print(f"  API密钥: {self.api_key[:8]}...")
        self.connected = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        print(f"  清理LLM客户端")
        print(f"  总请求数: {self.request_count}")
        self.connected = False

        if exc_type:
            print(f"  ⚠ 会话期间发生异常: {exc_type.__name__}")

        return False

    def generate(self, prompt: str) -> str:
        """生成文本"""
        if not self.connected:
            raise RuntimeError("客户端未连接")

        self.request_count += 1
        print(f"  [请求 {self.request_count}] {prompt[:30]}...")
        time.sleep(0.5)  # 模拟API调用
        return f"响应: {prompt}"


class AgentWorkspace:
    """
    Agent工作空间

    管理Agent运行期间的资源和状态
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.temp_files = []
        self.start_time = None

    def __enter__(self):
        """设置工作空间"""
        print(f"\n  设置Agent工作空间: {self.agent_name}")
        self.start_time = time.time()

        # 创建临时目录
        print(f"  创建临时资源...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理工作空间"""
        elapsed = time.time() - self.start_time
        print(f"\n  清理工作空间: {self.agent_name}")
        print(f"  运行时间: {elapsed:.2f}秒")

        # 清理临时文件
        if self.temp_files:
            print(f"  清理 {len(self.temp_files)} 个临时文件")

        return False

    def create_temp_file(self, name: str):
        """创建临时文件"""
        self.temp_files.append(name)
        print(f"    创建临时文件: {name}")


def ai_resource_management_example():
    """AI应用的资源管理示例"""
    print("\n【示例7】AI应用：完整的资源管理")
    print("=" * 60)

    print("\n1. LLM客户端管理:")
    with LLMClient("sk-1234567890abcdef", "gpt-4") as client:
        client.generate("什么是机器学习?")
        client.generate("什么是深度学习?")
        client.generate("什么是强化学习?")

    print("\n2. Agent工作空间:")
    with AgentWorkspace("研究助手") as workspace:
        workspace.create_temp_file("research_data.json")
        workspace.create_temp_file("analysis_result.txt")

        print(f"    执行研究任务...")
        time.sleep(0.5)

    print("\n3. 组合使用:")
    with (
        AgentWorkspace("智能助手") as workspace,
        LLMClient("sk-test", "gpt-4") as client
    ):
        workspace.create_temp_file("context.json")
        response = client.generate("分析数据")
        print(f"    处理响应: {response[:30]}...")


# ============================================================================
# 8. 实用技巧
# ============================================================================

@contextmanager
def temporary_env(key: str, value: str):
    """临时修改环境变量"""
    import os

    old_value = os.environ.get(key)
    os.environ[key] = value
    print(f"  设置环境变量: {key}={value}")

    try:
        yield
    finally:
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value
        print(f"  恢复环境变量: {key}")


@contextmanager
def log_context(operation: str):
    """日志上下文"""
    print(f"\n{'='*60}")
    print(f"开始: {operation}")
    print('='*60)

    start = time.time()

    try:
        yield
    except Exception as e:
        print(f"\n✗ {operation} 失败: {e}")
        raise
    else:
        elapsed = time.time() - start
        print(f"\n✓ {operation} 成功 (耗时: {elapsed:.2f}秒)")
    finally:
        print('='*60)


def practical_tips_example():
    """实用技巧示例"""
    print("\n【示例8】实用技巧")
    print("=" * 60)

    # 临时环境变量
    print("\n1. 临时环境变量:")
    import os
    print(f"  DEBUG (修改前): {os.environ.get('DEBUG', 'None')}")

    with temporary_env("DEBUG", "true"):
        print(f"  DEBUG (修改后): {os.environ.get('DEBUG')}")

    print(f"  DEBUG (恢复后): {os.environ.get('DEBUG', 'None')}")

    # 日志上下文
    print("\n2. 日志上下文:")
    with log_context("数据处理任务"):
        time.sleep(0.5)
        data = [1, 2, 3, 4, 5]
        result = sum(data)
        print(f"处理 {len(data)} 个数据点，结果: {result}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("Python 上下文管理器")
    print("=" * 60)

    basic_with_example()
    custom_context_manager_example()
    contextmanager_decorator_example()
    contextlib_tools_example()
    nested_context_managers_example()

    # 异步示例
    asyncio.run(async_context_manager_example())

    ai_resource_management_example()
    practical_tips_example()

    print("\n" + "=" * 60)
    print("上下文管理器总结")
    print("=" * 60)
    print("1. with 语句自动管理资源")
    print("2. 实现 __enter__ 和 __exit__ 创建上下文管理器")
    print("3. 使用 @contextmanager 装饰器更简洁")
    print("4. async with 用于异步上下文")
    print("5. contextlib 提供实用工具（suppress, redirect等）")
    print("6. 上下文管理器确保资源正确清理")
    print("7. 在AI应用中管理:")
    print("   - 数据库连接")
    print("   - LLM会话")
    print("   - 临时配置")
    print("   - 文件操作")
    print("   - 工作空间")
    print("\n最佳实践:")
    print("- 所有需要清理的资源都应使用上下文管理器")
    print("- 优先使用 with 而不是手动 try-finally")
    print("- 嵌套时使用逗号分隔多个上下文")


if __name__ == "__main__":
    main()
