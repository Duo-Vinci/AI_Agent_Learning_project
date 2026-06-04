# Python 异步编程在 AI 中的应用

## 一、为什么需要异步编程？

在 AI Agent 开发中，经常需要：
- 并发调用多个 LLM API
- 同时处理多个用户请求
- 并行执行多个工具
- 等待外部 API 响应

**同步 vs 异步**：
```python
# 同步：总耗时 = 3秒 + 2秒 + 1秒 = 6秒
result1 = call_api_1()  # 3秒
result2 = call_api_2()  # 2秒
result3 = call_api_3()  # 1秒

# 异步：总耗时 = max(3秒, 2秒, 1秒) = 3秒
result1, result2, result3 = await asyncio.gather(
    call_api_1(),
    call_api_2(),
    call_api_3()
)
```

---

## 二、基础概念

### 协程（Coroutine）

```python
import asyncio

# 定义协程函数
async def fetch_data(url: str) -> str:
    """异步获取数据"""
    print(f"开始获取: {url}")
    await asyncio.sleep(1)  # 模拟网络请求
    print(f"完成获取: {url}")
    return f"数据来自 {url}"

# 运行协程
result = asyncio.run(fetch_data("https://api.example.com"))
```

### await 关键字

```python
async def process_data():
    # await 暂停当前协程，等待结果
    data = await fetch_data("url")
    
    # 处理数据
    processed = data.upper()
    
    return processed
```

---

## 三、并发执行

### asyncio.gather（推荐）

```python
async def parallel_llm_calls():
    """并行调用多个 LLM"""
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI()
    
    # 并行执行多个查询
    results = await asyncio.gather(
        llm.agenerate("什么是 AI？"),
        llm.agenerate("什么是 Agent？"),
        llm.agenerate("什么是 RAG？")
    )
    
    return results
```

### asyncio.create_task

```python
async def background_tasks():
    """后台任务"""
    # 创建任务（立即开始执行）
    task1 = asyncio.create_task(fetch_data("url1"))
    task2 = asyncio.create_task(fetch_data("url2"))
    
    # 做其他事情
    print("任务已启动，继续其他工作...")
    
    # 等待任务完成
    result1 = await task1
    result2 = await task2
    
    return result1, result2
```

---

## 四、实战示例

### 示例 1：并行调用多个 Agent

```python
from typing import List, Dict
import asyncio
from langchain_openai import ChatOpenAI

class AsyncAgent:
    def __init__(self, name: str, llm):
        self.name = name
        self.llm = llm
    
    async def execute(self, task: str) -> Dict:
        """异步执行任务"""
        print(f"[{self.name}] 开始执行: {task}")
        
        result = await self.llm.agenerate(task)
        
        print(f"[{self.name}] 执行完成")
        
        return {
            "agent": self.name,
            "task": task,
            "result": result
        }

async def multi_agent_workflow(tasks: List[str]):
    """多 Agent 并行工作流"""
    llm = ChatOpenAI()
    
    # 创建多个 Agent
    agents = [
        AsyncAgent("研究员", llm),
        AsyncAgent("分析师", llm),
        AsyncAgent("写作者", llm)
    ]
    
    # 并行执行
    results = await asyncio.gather(
        *[agent.execute(task) for agent, task in zip(agents, tasks)]
    )
    
    return results

# 运行
tasks = [
    "研究 AI Agent 的最新进展",
    "分析市场趋势",
    "撰写技术文章"
]
results = asyncio.run(multi_agent_workflow(tasks))
```

### 示例 2：带超时的异步调用

```python
async def call_with_timeout(timeout: float = 10.0):
    """带超时的 API 调用"""
    try:
        result = await asyncio.wait_for(
            slow_api_call(),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        print("请求超时")
        return None

async def slow_api_call():
    """模拟慢速 API"""
    await asyncio.sleep(15)  # 15秒
    return "结果"
```

### 示例 3：异步生成器

```python
async def stream_llm_response(prompt: str):
    """流式输出 LLM 响应"""
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(streaming=True)
    
    async for chunk in llm.astream(prompt):
        yield chunk.content
        await asyncio.sleep(0.1)  # 控制输出速度

# 使用
async def main():
    async for chunk in stream_llm_response("讲个故事"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

---

## 五、错误处理

```python
async def safe_async_call():
    """安全的异步调用"""
    try:
        result = await risky_operation()
        return result
    except Exception as e:
        print(f"错误: {e}")
        return None

async def gather_with_error_handling():
    """gather 的错误处理"""
    results = await asyncio.gather(
        task1(),
        task2(),
        task3(),
        return_exceptions=True  # 返回异常而不是抛出
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"任务 {i} 失败: {result}")
        else:
            print(f"任务 {i} 成功: {result}")
```

---

## 六、最佳实践

1. **使用 asyncio.run() 作为入口**
2. **对 I/O 密集操作使用异步**
3. **避免在异步函数中使用同步阻塞调用**
4. **使用 asyncio.gather() 并行执行独立任务**
5. **为长时间运行的任务设置超时**
6. **正确处理异常**

---

## 运行示例

```bash
cd projects/00-python-fundamentals/01-async-programming
python async_agents.py
```
