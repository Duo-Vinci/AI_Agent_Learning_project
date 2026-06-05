# Python 基础教程 - AI Agent 开发必备

完整的Python基础教程，专注于AI Agent开发中最重要的技术。每个模块包含详细的中文注释、从基础到高级的示例，以及实际的AI应用场景。

## 📚 模块概览

### 01. 异步编程 (Async Programming)
**为什么重要**: AI应用需要并发调用多个LLM、并行处理任务、处理多用户请求

**包含内容**:
- `01_basic_async.py` - 异步编程基础（协程、async/await、并发执行）
- `02_async_patterns.py` - 高级异步模式（超时、重试、限流、异步生成器）
- `03_async_http.py` - 异步HTTP请求（httpx、aiohttp、LLM API调用）

**核心概念**:
- 协程与事件循环
- `asyncio.gather()` 并发执行
- `asyncio.create_task()` 后台任务
- 信号量与限流
- 异步上下文管理器

**实际应用**:
```python
# 并发调用多个LLM
results = await asyncio.gather(
    call_gpt("什么是AI?"),
    call_claude("什么是AI?"),
    call_gemini("什么是AI?")
)
```

---

### 02. 装饰器 (Decorators)
**为什么重要**: 装饰器用于日志、监控、缓存、重试等横切关注点，是构建可维护系统的关键

**包含内容**:
- `01_basic_decorators.py` - 装饰器基础（函数装饰器、参数化装饰器、多层装饰器）
- `02_class_decorators.py` - 高级装饰器（类装饰器、装饰器类、异步装饰器）

**核心概念**:
- 函数是一等公民
- `@functools.wraps` 保留元信息
- 带参数的装饰器
- 装饰器类（带状态）
- 异步装饰器

**实际应用**:
```python
@monitor_llm_call
@retry(max_attempts=3)
@cache(ttl=60)
async def call_llm(prompt: str) -> str:
    return await llm.generate(prompt)
```

---

### 03. 类型注解 (Type Annotations)
**为什么重要**: 类型注解提高代码可读性、启用IDE智能提示、支持静态类型检查，减少运行时错误

**包含内容**:
- `01_basic_types.py` - 基础类型注解（基本类型、复合类型、Optional、Union）
- `02_advanced_types.py` - 高级类型（泛型、协议、TypedDict、Literal）

**核心概念**:
- 基本类型：`str`, `int`, `float`, `bool`
- 复合类型：`List[T]`, `Dict[K,V]`, `Tuple`, `Set`
- `Optional[T]` = `Union[T, None]`
- 泛型 `Generic[T]`
- 协议 `Protocol`
- `TypedDict` 精确的字典类型

**实际应用**:
```python
class Agent(Generic[T]):
    def process(self, input_data: T) -> T:
        ...

agent: Agent[str] = Agent("文本处理Agent")
```

---

### 04. 错误处理 (Error Handling)
**为什么重要**: LLM API调用可能失败、网络可能超时、数据可能错误，良好的错误处理确保系统健壮性

**包含内容**:
- `01_basic_error_handling.py` - 错误处理基础（try-except、自定义异常、异常链、最佳实践）

**核心概念**:
- `try-except-else-finally`
- 自定义异常类
- 异常链 (`raise ... from ...`)
- 重试机制
- 优雅失败

**实际应用**:
```python
class LLMError(Exception):
    pass

class LLMTimeoutError(LLMError):
    def __init__(self, timeout: float):
        super().__init__(f"LLM调用超时 ({timeout}秒)")

try:
    result = await call_llm(prompt)
except LLMTimeoutError as e:
    # 使用缓存或默认响应
    result = get_cached_response(prompt)
```

---

### 05. 上下文管理器 (Context Managers)
**为什么重要**: 确保资源正确清理（数据库连接、文件、LLM会话），避免资源泄漏

**包含内容**:
- `01_context_managers.py` - 上下文管理器（with语句、自定义管理器、异步管理器）

**核心概念**:
- `with` 语句
- `__enter__` 和 `__exit__`
- `@contextmanager` 装饰器
- 异步上下文管理器
- `contextlib` 工具

**实际应用**:
```python
class LLMSession:
    def __enter__(self):
        # 建立连接
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理资源
        self.close()

with LLMSession() as session:
    result = session.generate(prompt)
# 自动清理
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd projects/00-python-fundamentals
pip install -r requirements.txt
```

### 2. 运行示例

每个模块都可以独立运行：

```bash
# 异步编程
python 01-async-programming/src/01_basic_async.py
python 01-async-programming/src/02_async_patterns.py
python 01-async-programming/src/03_async_http.py

# 装饰器
python 02-decorators/src/01_basic_decorators.py
python 02-decorators/src/02_class_decorators.py

# 类型注解
python 03-type-annotations/src/01_basic_types.py
python 03-type-annotations/src/02_advanced_types.py

# 错误处理
python 04-error-handling/src/01_basic_error_handling.py

# 上下文管理器
python 05-context-managers/src/01_context_managers.py
```

### 3. 真实LLM集成示例

```bash
# 设置API密钥（可选）
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 运行集成示例
python real_llm_example.py
```

---

## 📖 学习路径

### 初学者路径
1. **异步编程基础** → 理解协程和并发
2. **装饰器基础** → 掌握函数装饰器
3. **类型注解基础** → 学习基本类型
4. **错误处理** → 了解异常处理
5. **上下文管理器** → 学习资源管理

### 进阶路径
1. **异步HTTP请求** → 实际API调用
2. **高级装饰器** → 装饰器类和异步装饰器
3. **高级类型系统** → 泛型和协议
4. **完整错误处理策略** → 重试和恢复
5. **真实LLM集成** → 综合应用

---

## 💡 核心要点

### 异步编程
- ✅ 使用 `async/await` 处理I/O密集型操作
- ✅ 使用 `asyncio.gather()` 并发执行独立任务
- ✅ 使用信号量限制并发数
- ❌ 不要在异步函数中使用同步阻塞调用

### 装饰器
- ✅ 使用 `@functools.wraps` 保留函数元信息
- ✅ 装饰器用于横切关注点（日志、监控、缓存）
- ✅ 装饰器类用于需要状态的场景
- ❌ 避免装饰器过于复杂

### 类型注解
- ✅ 为所有公共API添加类型注解
- ✅ 使用 `mypy` 进行静态类型检查
- ✅ 使用 `Protocol` 定义接口
- ❌ 不要过度使用 `Any`

### 错误处理
- ✅ 捕获具体的异常类型
- ✅ 创建自定义异常类
- ✅ 使用异常链保留上下文
- ❌ 不要使用空的 `except:` 块

### 上下文管理器
- ✅ 所有需要清理的资源都使用 `with`
- ✅ 使用 `@contextmanager` 简化实现
- ✅ 异步资源使用 `async with`
- ❌ 不要手动管理可以用上下文管理器的资源

---

## 🛠️ 工具推荐

### 开发工具
- **VSCode** - Python开发IDE
- **PyCharm** - 专业Python IDE
- **IPython** - 交互式Python Shell

### 类型检查
- **mypy** - 静态类型检查器
- **pyright** - 微软的类型检查器
- **pydantic** - 运行时数据验证

### 代码质量
- **black** - 代码格式化
- **ruff** - 快速Linter
- **pytest** - 测试框架

---

## 📊 实际应用场景

### 场景1: 并发调用多个LLM
```python
async def multi_model_query(prompt: str):
    results = await asyncio.gather(
        gpt_client.generate(prompt),
        claude_client.generate(prompt),
        gemini_client.generate(prompt)
    )
    return choose_best_response(results)
```

### 场景2: 带监控的LLM调用
```python
@monitor_llm_call
@retry(max_attempts=3)
@cache(ttl=300)
async def call_llm(prompt: str) -> str:
    async with LLMSession() as session:
        return await session.generate(prompt)
```

### 场景3: 类型安全的Agent系统
```python
class Agent(Generic[T], Protocol):
    def process(self, input_data: T) -> T: ...

class TextAgent:
    def process(self, input_data: str) -> str:
        return input_data.upper()

agent: Agent[str] = TextAgent()
```

---

## 🎯 最佳实践总结

1. **异步优先**: I/O密集型操作使用异步
2. **装饰器抽象**: 横切关注点用装饰器
3. **类型清晰**: 公共API添加类型注解
4. **错误明确**: 创建清晰的自定义异常
5. **资源安全**: 使用上下文管理器

---

## 📚 推荐阅读

- [Python官方文档](https://docs.python.org/zh-cn/3/)
- [PEP 8 - Python代码风格指南](https://peps.python.org/pep-0008/)
- [PEP 484 - 类型注解](https://peps.python.org/pep-0484/)
- [asyncio官方文档](https://docs.python.org/zh-cn/3/library/asyncio.html)
- [Real Python教程](https://realpython.com/)

---

## ❓ 常见问题

**Q: 什么时候使用异步？**  
A: I/O密集型操作（网络请求、文件读写、数据库查询）使用异步，CPU密集型操作使用多进程。

**Q: 装饰器和继承的区别？**  
A: 装饰器用于添加功能，不改变对象本质；继承用于扩展类型。装饰器更灵活。

**Q: 类型注解是必须的吗？**  
A: 不是必须的，但强烈推荐。类型注解提高可读性、减少错误、改善IDE体验。

**Q: 如何选择异常类型？**  
A: 捕获时尽可能具体；抛出时创建自定义异常，继承自合适的内置异常。

**Q: 什么时候需要上下文管理器？**  
A: 任何需要配对操作的场景（打开/关闭、连接/断开、获取/释放）。

---

## 🤝 贡献

发现问题或有改进建议？欢迎提Issue或PR！

---

## 📝 许可证

MIT License - 自由使用和分享

---

**Happy Coding! 🚀**
