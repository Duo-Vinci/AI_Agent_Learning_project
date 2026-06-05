"""
快速开始指南
===========

这是一个5分钟快速入门指南，带你了解Python基础教程的核心内容。
"""


def quick_demo():
    """快速演示所有核心概念"""

    print("="*60)
    print("Python 基础教程 - 5分钟快速入门")
    print("="*60)

    # ========================================
    # 1. 异步编程
    # ========================================
    print("\n【1/5】异步编程")
    print("-"*60)
    print("""
为什么需要异步？
  在AI开发中，经常需要：
  - 并发调用多个LLM API
  - 同时处理多个用户请求
  - 等待外部API响应

代码示例：
  ```python
  # 串行：总耗时 = 3秒 + 2秒 + 1秒 = 6秒
  result1 = call_api_1()  # 3秒
  result2 = call_api_2()  # 2秒
  result3 = call_api_3()  # 1秒

  # 异步：总耗时 = max(3秒, 2秒, 1秒) = 3秒
  results = await asyncio.gather(
      call_api_1(),
      call_api_2(),
      call_api_3()
  )
  ```

运行示例：
  python 01-async-programming/src/01_basic_async.py
    """)

    # ========================================
    # 2. 装饰器
    # ========================================
    print("\n【2/5】装饰器")
    print("-"*60)
    print("""
为什么需要装饰器？
  装饰器让你轻松添加：
  - 日志记录
  - 性能监控
  - 自动重试
  - 结果缓存

代码示例：
  ```python
  @timer           # 计时
  @retry(times=3)  # 重试
  @cache(ttl=60)   # 缓存
  async def call_llm(prompt: str) -> str:
      return await llm.generate(prompt)

  # 调用时自动应用所有功能
  result = await call_llm("什么是AI?")
  ```

运行示例：
  python 02-decorators/src/01_basic_decorators.py
    """)

    # ========================================
    # 3. 类型注解
    # ========================================
    print("\n【3/5】类型注解")
    print("-"*60)
    print("""
为什么需要类型注解？
  - IDE智能提示
  - 静态类型检查
  - 更好的文档
  - 减少运行时错误

代码示例：
  ```python
  from typing import List, Dict, Optional

  def process_messages(
      messages: List[Dict[str, str]],
      model: str = "gpt-4"
  ) -> Optional[str]:
      '''处理消息列表，返回响应'''
      if not messages:
          return None
      return f"处理了 {len(messages)} 条消息"

  # IDE会提示参数类型，检查类型错误
  result = process_messages([{"role": "user", "content": "Hi"}])
  ```

运行示例：
  python 03-type-annotations/src/01_basic_types.py
    """)

    # ========================================
    # 4. 错误处理
    # ========================================
    print("\n【4/5】错误处理")
    print("-"*60)
    print("""
为什么需要错误处理？
  AI应用中常见问题：
  - LLM API可能失败
  - 网络可能超时
  - 数据格式可能错误

代码示例：
  ```python
  class LLMTimeoutError(Exception):
      def __init__(self, timeout: float):
          super().__init__(f"LLM调用超时: {timeout}秒")

  try:
      result = await call_llm(prompt, timeout=30)
  except LLMTimeoutError as e:
      print(f"超时，使用缓存: {e}")
      result = get_cached_response(prompt)
  except LLMAPIError as e:
      print(f"API错误: {e}")
      result = None
  ```

运行示例：
  python 04-error-handling/src/01_basic_error_handling.py
    """)

    # ========================================
    # 5. 上下文管理器
    # ========================================
    print("\n【5/5】上下文管理器")
    print("-"*60)
    print("""
为什么需要上下文管理器？
  确保资源正确清理：
  - 数据库连接
  - 文件操作
  - LLM会话
  - 临时配置

代码示例：
  ```python
  # 自动管理资源
  with LLMSession(model="gpt-4") as session:
      result = session.generate(prompt)
      # 会话自动关闭，无需手动清理

  # 异步版本
  async with AsyncLLMSession(model="gpt-4") as session:
      result = await session.generate(prompt)
  ```

运行示例：
  python 05-context-managers/src/01_context_managers.py
    """)

    # ========================================
    # 综合示例
    # ========================================
    print("\n【综合】完整的AI Agent系统")
    print("-"*60)
    print("""
将所有技术结合起来：

  ```python
  @monitor          # 装饰器：监控
  @retry(times=3)   # 装饰器：重试
  @cache(ttl=300)   # 装饰器：缓存
  async def call_llm(  # 异步函数
      messages: List[Message],     # 类型注解
      model: str = "gpt-4"
  ) -> AgentResponse:

      try:  # 错误处理
          async with LLMSession(model) as session:  # 上下文管理器
              return await session.generate(messages)

      except LLMTimeoutError as e:
          # 优雅的错误恢复
          return get_cached_response(messages)
  ```

运行完整示例：
  python comprehensive_example.py
    """)

    # ========================================
    # 下一步
    # ========================================
    print("\n【下一步】学习路径")
    print("="*60)
    print("""
初学者：
  1. 运行所有基础示例，理解每个概念
  2. 修改示例代码，尝试不同参数
  3. 完成每个模块后的练习

进阶者：
  1. 阅读高级示例代码
  2. 运行真实LLM集成示例（需要API密钥）
  3. 尝试构建自己的AI Agent

实战项目：
  1. 构建一个多模型对比工具
  2. 实现一个带缓存的LLM代理
  3. 创建一个多Agent协作系统
    """)

    # ========================================
    # 资源链接
    # ========================================
    print("\n【资源】推荐阅读")
    print("="*60)
    print("""
官方文档：
  - Python官方教程: https://docs.python.org/zh-cn/3/
  - asyncio文档: https://docs.python.org/zh-cn/3/library/asyncio.html
  - typing文档: https://docs.python.org/zh-cn/3/library/typing.html

学习资源：
  - Real Python: https://realpython.com/
  - Python异步编程在AI中的应用: docs/01-学习笔记/Python异步编程在AI中的应用.md

工具：
  - mypy (类型检查): https://mypy.readthedocs.io/
  - black (代码格式化): https://black.readthedocs.io/
  - pytest (测试): https://docs.pytest.org/
    """)

    # ========================================
    # 快速命令
    # ========================================
    print("\n【命令】快速开始")
    print("="*60)
    print("""
安装依赖：
  pip install -r requirements.txt

运行所有基础示例：
  python 01-async-programming/src/01_basic_async.py
  python 02-decorators/src/01_basic_decorators.py
  python 03-type-annotations/src/01_basic_types.py
  python 04-error-handling/src/01_basic_error_handling.py
  python 05-context-managers/src/01_context_managers.py

运行综合示例：
  python comprehensive_example.py

运行真实API示例（需要API密钥）：
  export OPENAI_API_KEY="sk-..."
  python real_llm_example.py

类型检查：
  mypy comprehensive_example.py
    """)

    print("\n" + "="*60)
    print("🎉 准备好了！现在开始你的Python学习之旅吧！")
    print("="*60)
    print("\n💡 提示: 从 01-async-programming 开始，按顺序学习效果最好。\n")


if __name__ == "__main__":
    quick_demo()
