# Agent 设计原则

## 一、核心设计原则

### 1.1 单一职责原则（Single Responsibility）

**定义**：每个 Agent 应该只负责一个明确的任务领域。

```python
# ❌ 错误：一个 Agent 做太多事
class SuperAgent:
    def research(self, topic): ...
    def write_article(self, data): ...
    def send_email(self, content): ...
    def analyze_data(self, dataset): ...

# ✅ 正确：职责分离
class ResearchAgent:
    def research(self, topic): ...

class WriterAgent:
    def write_article(self, data): ...

class EmailAgent:
    def send_email(self, content): ...
```

**优势**：
- 易于理解和维护
- 可独立测试
- 便于复用
- 减少耦合

---

## 二、工具设计原则

### 2.1 工具应该是原子操作

```python
# ✅ 好的工具设计
@tool
def search_weather(location: str) -> str:
    """查询指定地点的天气"""
    return get_weather_api(location)

@tool
def convert_temperature(celsius: float) -> float:
    """摄氏度转华氏度"""
    return celsius * 9/5 + 32

# ❌ 避免：工具做太多事
@tool
def weather_and_convert(location: str) -> str:
    """查天气并转换温度（职责不清）"""
    weather = get_weather_api(location)
    temp_f = weather['celsius'] * 9/5 + 32
    return f"{weather['desc']}, {temp_f}F"
```

### 2.2 工具描述要清晰准确

```python
# ❌ 描述不清
@tool
def do_something(data: str) -> str:
    """处理数据"""  # 太模糊
    return process(data)

# ✅ 描述清晰
@tool
def extract_keywords(text: str) -> List[str]:
    """从文本中提取关键词。
    
    输入：一段文本
    输出：关键词列表，按重要性排序
    示例：extract_keywords("AI is great") -> ["AI", "great"]
    """
    return extract_keywords_impl(text)
```

### 2.3 工具参数验证

```python
from pydantic import BaseModel, Field, validator

class SearchInput(BaseModel):
    """搜索工具输入"""
    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    limit: int = Field(10, ge=1, le=100, description="返回结果数量")
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('查询不能为空')
        return v.strip()

@tool(args_schema=SearchInput)
def search(query: str, limit: int = 10) -> List[dict]:
    """执行搜索"""
    # 参数已被 Pydantic 验证
    return perform_search(query, limit)
```

---

## 三、记忆系统设计

### 3.1 分层记忆架构

```python
class AgentMemory:
    """分层记忆系统"""
    
    def __init__(self):
        self.working_memory = []      # 工作记忆（短期）
        self.episodic_memory = []     # 情节记忆（对话历史）
        self.semantic_memory = {}     # 语义记忆（知识图谱）
        self.procedural_memory = {}   # 程序记忆（技能）
    
    def add_to_working(self, item: dict):
        """添加到工作记忆（最近5条）"""
        self.working_memory.append(item)
        if len(self.working_memory) > 5:
            # 移到情节记忆
            old = self.working_memory.pop(0)
            self.episodic_memory.append(old)
    
    def store_knowledge(self, key: str, value: Any):
        """存储长期知识"""
        self.semantic_memory[key] = {
            'value': value,
            'timestamp': datetime.now(),
            'access_count': 0
        }
    
    def recall(self, query: str) -> List[dict]:
        """检索相关记忆"""
        results = []
        
        # 1. 优先从工作记忆
        results.extend(self.working_memory)
        
        # 2. 从情节记忆检索相关内容
        relevant = self._search_episodic(query)
        results.extend(relevant[:3])
        
        # 3. 从语义记忆检索
        knowledge = self._search_semantic(query)
        results.extend(knowledge)
        
        return results
```

### 3.2 记忆压缩策略

```python
async def compress_memory(long_history: List[dict]) -> str:
    """压缩长对话历史"""
    
    # 保留最近的消息
    recent = long_history[-5:]
    
    # 压缩中间的消息
    middle = long_history[:-5]
    if middle:
        summary_prompt = f"""总结以下对话的关键信息（100字以内）：

对话历史：
{format_messages(middle)}

关键信息摘要："""
        
        summary = await llm.agenerate(summary_prompt)
    else:
        summary = ""
    
    return {
        'summary': summary,
        'recent_messages': recent
    }
```

---

## 四、错误处理原则

### 4.1 优雅降级

```python
class ResilientAgent:
    """具有降级能力的 Agent"""
    
    async def execute(self, task: dict):
        """执行任务（带降级）"""
        try:
            # 尝试主要方案
            return await self._execute_primary(task)
        
        except LLMTimeoutError:
            # 降级：使用更快的模型
            logger.warning("主模型超时，切换到快速模型")
            return await self._execute_with_fast_model(task)
        
        except ToolExecutionError as e:
            # 降级：不使用工具直接回答
            logger.warning(f"工具执行失败: {e}，使用备用方案")
            return await self._execute_without_tools(task)
        
        except Exception as e:
            # 最后的降级：返回错误但不崩溃
            logger.error(f"执行失败: {e}")
            return {
                'status': 'error',
                'message': '抱歉，我遇到了问题，请稍后重试',
                'error_type': type(e).__name__
            }
```

### 4.2 超时保护

```python
import asyncio

async def execute_with_timeout(
    agent_func,
    timeout: float = 30.0,
    fallback_func = None
):
    """带超时的执行"""
    try:
        return await asyncio.wait_for(agent_func(), timeout=timeout)
    
    except asyncio.TimeoutError:
        logger.warning(f"执行超时 ({timeout}s)")
        
        if fallback_func:
            return await fallback_func()
        
        raise TimeoutException(f"操作超时 ({timeout}s)")
```

---

## 五、性能优化原则

### 5.1 延迟加载

```python
class LazyAgent:
    """延迟加载的 Agent"""
    
    def __init__(self):
        self._llm = None
        self._tools = None
        self._memory = None
    
    @property
    def llm(self):
        """延迟初始化 LLM"""
        if self._llm is None:
            self._llm = ChatOpenAI(model="gpt-4")
        return self._llm
    
    @property
    def tools(self):
        """延迟加载工具"""
        if self._tools is None:
            self._tools = self._load_tools()
        return self._tools
```

### 5.2 资源池化

```python
class AgentPool:
    """Agent 对象池"""
    
    def __init__(self, agent_factory, pool_size: int = 10):
        self.pool = Queue(maxsize=pool_size)
        
        for _ in range(pool_size):
            agent = agent_factory()
            self.pool.put(agent)
    
    @contextmanager
    def acquire(self):
        """获取 Agent"""
        agent = self.pool.get()
        try:
            yield agent
        finally:
            agent.reset()  # 重置状态
            self.pool.put(agent)

# 使用
pool = AgentPool(lambda: ResearchAgent(), pool_size=10)

async def handle_request(query):
    with pool.acquire() as agent:
        return await agent.execute(query)
```

---

## 六、可测试性设计

### 6.1 依赖注入

```python
# ❌ 难以测试
class Agent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")  # 硬编码依赖
    
    async def execute(self, task):
        return await self.llm.agenerate(task)

# ✅ 易于测试
class Agent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm  # 依赖注入
    
    async def execute(self, task):
        return await self.llm.agenerate(task)

# 测试时可以注入 Mock
def test_agent():
    mock_llm = MockLLM()
    agent = Agent(llm=mock_llm)
    result = await agent.execute("test")
    assert result == "expected"
```

### 6.2 接口抽象

```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Agent 基类"""
    
    @abstractmethod
    async def execute(self, task: dict) -> dict:
        """执行任务（子类必须实现）"""
        pass
    
    @abstractmethod
    def validate_input(self, task: dict) -> bool:
        """验证输入"""
        pass

class ResearchAgent(BaseAgent):
    async def execute(self, task: dict) -> dict:
        # 实现具体逻辑
        pass
    
    def validate_input(self, task: dict) -> bool:
        return 'query' in task
```

---

## 七、安全性原则

### 7.1 输入验证

```python
class SecureAgent:
    """安全的 Agent"""
    
    def validate_input(self, user_input: str) -> str:
        """验证和清理用户输入"""
        # 1. 长度限制
        if len(user_input) > 10000:
            raise ValueError("输入过长")
        
        # 2. 危险字符过滤
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',
            r'eval\(',
            r'exec\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                raise SecurityError("检测到危险输入")
        
        # 3. SQL 注入防护
        if any(keyword in user_input.lower() for keyword in ['drop table', 'delete from', '; --']):
            raise SecurityError("检测到可疑SQL语句")
        
        return user_input.strip()
```

### 7.2 权限控制

```python
class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.permissions = {
            'read': ['user', 'admin'],
            'write': ['admin'],
            'delete': ['admin'],
            'execute_tool': ['user', 'admin']
        }
    
    def check_permission(self, user_role: str, action: str) -> bool:
        """检查权限"""
        allowed_roles = self.permissions.get(action, [])
        return user_role in allowed_roles

class SecureAgent:
    def __init__(self, permission_manager: PermissionManager):
        self.pm = permission_manager
    
    async def execute(self, task: dict, user_role: str):
        """执行任务（带权限检查）"""
        if not self.pm.check_permission(user_role, 'execute_tool'):
            raise PermissionError("权限不足")
        
        return await self._execute_impl(task)
```

---

## 八、监控和可观察性

### 8.1 结构化日志

```python
import logging
import json

class AgentLogger:
    """Agent 专用日志器"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = logging.getLogger(agent_id)
    
    def log_execution(self, task: dict, result: dict, duration: float):
        """记录执行"""
        log_entry = {
            'agent_id': self.agent_id,
            'task_type': task.get('type'),
            'status': result.get('status'),
            'duration_ms': duration * 1000,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_error(self, error: Exception, context: dict):
        """记录错误"""
        log_entry = {
            'agent_id': self.agent_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.error(json.dumps(log_entry))
```

### 8.2 指标收集

```python
from prometheus_client import Counter, Histogram

class AgentMetrics:
    """Agent 指标"""
    
    def __init__(self, agent_id: str):
        self.executions = Counter(
            'agent_executions_total',
            'Total executions',
            ['agent_id', 'status']
        )
        
        self.duration = Histogram(
            'agent_execution_duration_seconds',
            'Execution duration',
            ['agent_id']
        )
        
        self.agent_id = agent_id
    
    def record_execution(self, status: str, duration: float):
        """记录执行指标"""
        self.executions.labels(
            agent_id=self.agent_id,
            status=status
        ).inc()
        
        self.duration.labels(
            agent_id=self.agent_id
        ).observe(duration)
```

---

## 九、设计检查清单

### 功能设计
- [ ] Agent 职责单一明确
- [ ] 工具设计简洁原子
- [ ] 输入输出类型明确
- [ ] 错误处理完善

### 性能设计
- [ ] 使用异步处理
- [ ] 实现资源池化
- [ ] 添加缓存机制
- [ ] 设置超时限制

### 可靠性设计
- [ ] 实现降级策略
- [ ] 添加重试机制
- [ ] 输入验证完善
- [ ] 异常处理全面

### 可测试性
- [ ] 使用依赖注入
- [ ] 接口清晰抽象
- [ ] 易于 Mock
- [ ] 有单元测试

### 可观察性
- [ ] 结构化日志
- [ ] 指标收集
- [ ] 链路追踪
- [ ] 性能监控

---

**遵循设计原则，构建高质量 Agent 系统！**
