# 快速启动指南

## 🚀 5分钟快速体验

### 步骤1: 安装依赖 (1分钟)

```bash
cd /z/Agent_WorkSpace/AI_Agent_Learning_project/projects/10-production-grade
pip install -r requirements.txt
```

### 步骤2: 运行完整演示 (2分钟)

```bash
python run_demo.py
```

这将依次运行所有10个模块的示例代码，展示完整功能。

### 步骤3: 尝试单个模块 (2分钟)

#### 示例1: Agent基类
```bash
python 01-project-structure/src/base_agent.py
```

#### 示例2: 配置管理
```bash
python 02-config-management/src/config_manager.py
```

#### 示例3: 启动API服务
```bash
python 08-api-service/src/api_service.py
# 然后访问 http://localhost:8000/docs
```

---

## 📋 完整功能清单

### ✅ 已实现的功能

| 模块 | 功能 | 文件 | 状态 |
|------|------|------|------|
| **01-项目结构** | Agent基类、指标收集 | `base_agent.py` | ✅ |
| **02-配置管理** | 多环境配置、环境变量覆盖 | `config_manager.py` | ✅ |
| **03-日志系统** | 结构化JSON日志、请求追踪 | `structured_logger.py` | ✅ |
| **04-错误处理** | 自定义异常、错误处理器 | `exceptions.py`, `error_handler.py` | ✅ |
| **05-重试熔断** | 指数退避重试、熔断器模式 | `retry_logic.py`, `circuit_breaker.py` | ✅ |
| **06-缓存系统** | 内存+Redis多级缓存、LRU | `cache_system.py` | ✅ |
| **07-测试** | 单元/集成/性能测试 | `test_*.py` (3个文件) | ✅ |
| **08-API服务** | FastAPI REST接口 | `api_service.py` | ✅ |
| **09-监控** | Prometheus指标收集 | `metrics_collector.py` | ✅ |
| **10-成本优化** | Token计数、成本追踪 | `cost_optimizer.py` | ✅ |

---

## 🎯 使用场景

### 场景1: 学习生产级开发

**目标**: 了解如何构建生产级AI Agent

**步骤**:
1. 阅读 `PROJECT_README.md`
2. 依次运行每个模块的示例代码
3. 查看代码中的详细注释
4. 修改代码进行实验

**推荐顺序**:
```
01-项目结构 → 02-配置管理 → 03-日志系统 → 04-错误处理 
→ 05-重试熔断 → 06-缓存 → 07-测试 → 08-API → 09-监控 → 10-成本
```

---

### 场景2: 构建新项目

**目标**: 基于模板创建自己的AI Agent项目

**步骤**:
1. 复制整个项目目录
2. 修改 `01-project-structure/src/base_agent.py` 中的Agent类
3. 配置 `02-config-management` 中的配置文件
4. 在 `08-api-service` 中添加自己的API端点
5. 运行测试验证功能

---

### 场景3: 集成到现有项目

**目标**: 将特定模块集成到现有项目

**步骤**:
1. 选择需要的模块（如缓存、监控）
2. 复制对应的 `src/` 目录
3. 安装相关依赖
4. 按照模块文档集成

**示例 - 集成缓存系统**:
```python
from cache_system import MultiLevelCache, MemoryCache

# 初始化缓存
cache = MultiLevelCache(l1_cache=MemoryCache(max_size=1000))

# 使用缓存
cache.set("key", "value", ttl=3600)
value = cache.get("key")
```

---

### 场景4: 部署到生产环境

**目标**: 将项目部署到生产环境

**步骤**:
1. **环境准备**
   ```bash
   export ENV=production
   export APP_LLM__MODEL=gpt-4
   export APP_DATABASE__HOST=prod-db.example.com
   ```

2. **运行测试**
   ```bash
   pytest 07-testing/src/ -v --cov
   ```

3. **启动服务**
   ```bash
   uvicorn 08-api-service.src.api_service:app --host 0.0.0.0 --port 8000
   ```

4. **配置监控**
   - 配置Prometheus抓取 `/api/v1/metrics` 端点
   - 在Grafana中创建仪表板

---

## 🔧 常用命令

### 运行单个模块
```bash
# Agent基类
python 01-project-structure/src/base_agent.py

# 配置管理
python 02-config-management/src/config_manager.py

# 日志系统
python 03-logging-system/src/structured_logger.py

# 错误处理
python 04-error-handling/src/error_handler.py

# 重试机制
python 05-retry-circuit-breaker/src/retry_logic.py

# 熔断器
python 05-retry-circuit-breaker/src/circuit_breaker.py

# 缓存系统
python 06-caching/src/cache_system.py

# API服务
python 08-api-service/src/api_service.py

# 监控指标
python 09-monitoring/src/metrics_collector.py

# 成本优化
python 10-cost-optimization/src/cost_optimizer.py
```

### 运行测试
```bash
# 所有测试
pytest 07-testing/src/ -v

# 单元测试
pytest 07-testing/src/test_agent.py -v

# 集成测试
pytest 07-testing/src/test_integration.py -v -m integration

# 性能测试
pytest 07-testing/src/test_performance.py -v -m performance

# 测试覆盖率
pytest 07-testing/src/ --cov --cov-report=html
```

### API服务
```bash
# 开发模式（自动重载）
uvicorn 08-api-service.src.api_service:app --reload

# 生产模式（多worker）
uvicorn 08-api-service.src.api_service:app --workers 4 --host 0.0.0.0

# 访问API文档
# http://localhost:8000/docs
```

---

## 📚 学习资源

### 项目文档
- [项目README](./PROJECT_README.md) - 完整功能说明
- [完成总结](./COMPLETION_SUMMARY.md) - 项目完成情况
- [快速启动](./QUICKSTART.md) - 本文档

### 教程文档
- [生产级开发教程](../../docs/02-教程/10-生产级开发教程.md)
- [生产环境检查清单](../../docs/05-最佳实践/04-生产环境检查清单.md)

### 代码示例
每个模块的Python文件末尾都包含完整的使用示例（`if __name__ == "__main__":` 部分）

---

## 💡 提示和技巧

### 1. 调试技巧
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看配置
from config_manager import Config
config = Config()
print(config.to_dict())

# 导出指标
from metrics_collector import metrics
print(metrics.export_metrics())
```

### 2. 性能优化
- 使用缓存减少重复API调用
- 启用连接池复用
- 实现请求批处理
- 监控慢查询

### 3. 成本控制
```python
from cost_optimizer import TokenManager, CostTracker

# Token计数
token_manager = TokenManager("gpt-4")
tokens = token_manager.count_tokens(text)

# 成本追踪
tracker = CostTracker()
tracker.record_usage("gpt-4", 1000, 500)
print(f"总成本: ${tracker.total_cost:.4f}")
```

### 4. 错误排查
```python
# 查看错误统计
from error_handler import ErrorHandler
handler = ErrorHandler()
stats = handler.get_error_stats()
print(stats)

# 检查熔断器状态
from circuit_breaker import CircuitBreaker
breaker = CircuitBreaker("service")
print(breaker.get_stats())
```

---

## ❓ 常见问题

### Q1: 如何配置Redis缓存？
```python
from cache_system import RedisCache, MultiLevelCache

redis_cache = RedisCache(
    host="localhost",
    port=6379,
    password="your-password"
)

cache = MultiLevelCache(l2_cache=redis_cache)
```

### Q2: 如何添加自定义指标？
```python
from prometheus_client import Counter

custom_metric = Counter('my_custom_metric', 'Description')
custom_metric.inc()
```

### Q3: 如何集成LLM API？
参考 `01-project-structure/src/base_agent.py` 中的 `execute` 方法，添加实际的API调用：

```python
async def execute(self, input_data):
    # 使用OpenAI
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key="your-key")
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": input_data["query"]}]
    )
    
    return {"response": response.choices[0].message.content}
```

### Q4: 如何运行多个Agent实例？
```python
import asyncio

agents = [MyAgent(f"agent-{i}", config={}) for i in range(10)]
tasks = [agent.run(data) for agent in agents]
results = await asyncio.gather(*tasks)
```

---

## 📞 获取帮助

如果遇到问题：
1. 查看模块中的使用示例
2. 阅读代码注释
3. 运行 `python <module>.py` 查看演示输出
4. 检查 `requirements.txt` 确保依赖已安装

---

## 🎓 下一步

1. **完成入门**: 运行所有示例，理解每个模块的功能
2. **深入学习**: 阅读源代码，理解实现细节
3. **动手实践**: 修改代码，添加自己的功能
4. **构建项目**: 基于模板创建自己的AI Agent
5. **部署上线**: 将项目部署到生产环境

---

**祝你学习愉快！🚀**
