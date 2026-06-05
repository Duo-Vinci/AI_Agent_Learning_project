# 生产级AI Agent开发项目

这是一个完整的生产级AI Agent开发项目，包含从项目结构到成本优化的所有关键组件。

## 项目结构

```
10-production-grade/
├── 01-project-structure/      # 标准项目结构和Agent基类
├── 02-config-management/      # 配置管理系统
├── 03-logging-system/         # 结构化日志系统
├── 04-error-handling/         # 错误处理和异常管理
├── 05-retry-circuit-breaker/  # 重试和熔断器机制
├── 06-caching/                # 多级缓存系统
├── 07-testing/                # 单元测试、集成测试和性能测试
├── 08-api-service/            # FastAPI REST API服务
├── 09-monitoring/             # Prometheus监控指标
├── 10-cost-optimization/      # Token计数和成本优化
└── requirements.txt           # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例

每个子模块都包含可独立运行的示例代码：

```bash
# 测试Agent基类
python 01-project-structure/src/base_agent.py

# 测试配置管理
python 02-config-management/src/config_manager.py

# 测试日志系统
python 03-logging-system/src/structured_logger.py

# 测试错误处理
python 04-error-handling/src/error_handler.py

# 测试重试机制
python 05-retry-circuit-breaker/src/retry_logic.py

# 测试熔断器
python 05-retry-circuit-breaker/src/circuit_breaker.py

# 测试缓存系统
python 06-caching/src/cache_system.py

# 运行测试
pytest 07-testing/src/ -v

# 启动API服务
python 08-api-service/src/api_service.py

# 测试监控指标
python 09-monitoring/src/metrics_collector.py

# 测试成本优化
python 10-cost-optimization/src/cost_optimizer.py
```

### 3. 启动API服务

```bash
cd 08-api-service/src
uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
```

访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 指标端点: http://localhost:8000/api/v1/metrics

## 核心功能

### 1. Agent基类 (01-project-structure)

提供标准化的Agent接口和性能指标收集：

```python
from base_agent import BaseAgent

class MyAgent(BaseAgent):
    async def execute(self, input_data):
        # 实现你的逻辑
        return {"result": "success"}

agent = MyAgent("my-agent", config={})
result = await agent.run({"query": "test"})
metrics = agent.get_metrics()
```

### 2. 配置管理 (02-config-management)

支持多环境配置和环境变量覆盖：

```python
from config_manager import Config

config = Config(env="production")
llm_model = config.get("llm.model")
db_host = config.get("database.host", "localhost")
```

### 3. 结构化日志 (03-logging-system)

JSON格式日志，支持请求追踪：

```python
from structured_logger import StructuredLogger, set_request_context

logger = StructuredLogger("app", level="INFO", format_type="json")
set_request_context(request_id="req-001", user_id="user-123")
logger.info("操作完成", operation="create", duration=1.5)
```

### 4. 错误处理 (04-error-handling)

统一的异常处理和降级策略：

```python
from exceptions import LLMException
from error_handler import with_error_handler

@with_error_handler(fallback=lambda: "默认值", reraise=False)
async def risky_operation():
    # 可能失败的操作
    pass
```

### 5. 重试和熔断器 (05-retry-circuit-breaker)

保护系统免受失败服务的影响：

```python
from retry_logic import retry
from circuit_breaker import CircuitBreaker

@retry(max_attempts=3, delay=1.0, backoff=2.0)
async def unstable_api_call():
    # API调用
    pass

breaker = CircuitBreaker("external-service", failure_threshold=5)
result = breaker.call(lambda: external_api())
```

### 6. 多级缓存 (06-caching)

L1内存缓存 + L2 Redis缓存：

```python
from cache_system import MultiLevelCache, MemoryCache, cached

cache = MultiLevelCache(l1_cache=MemoryCache())

@cached(cache, ttl=3600)
def expensive_computation(x, y):
    return x + y
```

### 7. 测试 (07-testing)

完整的测试套件：

```bash
# 单元测试
pytest 07-testing/src/test_agent.py -v

# 集成测试
pytest 07-testing/src/test_integration.py -v -m integration

# 性能测试
pytest 07-testing/src/test_performance.py -v -m performance
```

### 8. API服务 (08-api-service)

基于FastAPI的REST API：

- `POST /api/v1/agents/execute` - 执行Agent
- `GET /health` - 健康检查
- `GET /agents` - 列出所有Agent
- `GET /api/v1/metrics` - 获取指标

### 9. 监控指标 (09-monitoring)

Prometheus指标收集：

```python
from metrics_collector import metrics, track_request

@track_request(agent_id="my-agent")
async def process_request():
    # 自动记录请求、延迟和错误
    pass

# 手动记录
metrics.record_llm_tokens("gpt-4", prompt_tokens=100, completion_tokens=200)
metrics.record_cache_hit("L1")
```

### 10. 成本优化 (10-cost-optimization)

Token计数和成本追踪：

```python
from cost_optimizer import TokenManager, CostTracker

# Token管理
token_manager = TokenManager("gpt-4")
token_count = token_manager.count_tokens("你的文本")
cost = token_manager.estimate_cost(prompt_tokens=1000, completion_tokens=500)

# 成本追踪
tracker = CostTracker()
tracker.record_usage("gpt-4", 1000, 500, operation="research")
stats = tracker.get_statistics()
print(f"总成本: ${stats['total_cost']:.4f}")
```

## 生产环境部署

### Docker部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "08-api-service.src.api_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t ai-agent-service .
docker run -p 8000:8000 ai-agent-service
```

### 环境变量配置

```bash
export ENV=production
export APP_LLM__MODEL=gpt-4
export APP_DATABASE__HOST=prod-db.example.com
export APP_CACHE__HOST=prod-redis.example.com
```

### 监控配置

Prometheus配置 (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'ai-agent'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
```

## 最佳实践

### 1. 配置管理
- 使用环境变量覆盖敏感配置
- 为不同环境创建独立配置文件
- 验证必需的配置项

### 2. 日志记录
- 使用结构化JSON日志
- 为每个请求添加唯一ID
- 记录关键业务指标

### 3. 错误处理
- 定义明确的异常层次
- 实现优雅降级
- 记录详细的错误上下文

### 4. 性能优化
- 使用多级缓存减少API调用
- 实现请求重试和熔断器
- 监控响应时间和吞吐量

### 5. 成本控制
- 根据任务选择合适的模型
- 设置Token使用限制
- 定期审查成本报告

### 6. 测试覆盖
- 单元测试覆盖率 > 80%
- 集成测试关键工作流
- 性能测试验证SLA

## 监控指标

### 关键指标

- `agent_requests_total` - 总请求数
- `agent_request_duration_seconds` - 请求延迟
- `llm_tokens_used_total` - Token使用量
- `cache_hits_total` - 缓存命中数
- `errors_total` - 错误数

### 告警规则

```yaml
groups:
  - name: ai_agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        annotations:
          summary: "错误率过高"
      
      - alert: SlowResponse
        expr: histogram_quantile(0.95, agent_request_duration_seconds) > 5
        annotations:
          summary: "响应时间过慢"
```

## 故障排查

### 常见问题

1. **API调用失败**
   - 检查网络连接
   - 验证API密钥
   - 查看熔断器状态

2. **性能下降**
   - 检查缓存命中率
   - 分析慢查询
   - 监控资源使用

3. **成本过高**
   - 审查Token使用统计
   - 优化提示词
   - 考虑使用更经济的模型

## 参考文档

- [配置管理详解](../../docs/02-教程/10-生产级开发教程.md)
- [生产环境检查清单](../../docs/05-最佳实践/04-生产环境检查清单.md)

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！
