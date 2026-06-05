# AI Agent 运维监控项目

本项目提供 AI Agent 系统的全面运维监控解决方案。

## 项目结构

```
12-operations/
├── 01-monitoring/          # Prometheus + Grafana 监控
├── 02-logging/            # ELK 日志聚合
├── 03-tracing/            # Jaeger 分布式追踪
├── 04-alerting/           # AlertManager 告警系统
├── 05-performance/        # 性能测试和优化
├── 06-backup/             # 备份和恢复
└── 07-rate-limiting/      # 速率限制
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动监控栈

```bash
# 启动 Prometheus + Grafana
cd 01-monitoring
docker-compose up -d

# 启动 ELK 日志系统
cd 02-logging
docker-compose up -d

# 启动 Jaeger 追踪
cd 03-tracing
docker-compose up -d

# 启动 AlertManager
cd 04-alerting
docker-compose up -d
```

### 3. 访问服务

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Jaeger UI**: http://localhost:16686
- **AlertManager**: http://localhost:9093

## 使用指南

### 指标收集

```python
from monitoring.src.metrics import collector, track_agent_request

# 启动指标服务器
collector.start_server()

# 使用装饰器自动追踪
@track_agent_request("my_agent", "data_analysis")
async def process_task(data):
    # 你的代码
    pass
```

### 结构化日志

```python
from logging.src.structured_logging import logger

# 记录 Agent 请求
logger.log_agent_request(
    agent_id="agent-123",
    task_id="task-456",
    task_type="analysis",
    status="success",
    duration=5.2
)

# 记录 LLM 调用
logger.log_llm_call(
    agent_id="agent-123",
    model="gpt-4",
    prompt_tokens=150,
    completion_tokens=80,
    duration=2.5,
    cost=0.014
)
```

### 分布式追踪

```python
from tracing.src.distributed_tracing import TracingConfig, DistributedTracer

# 初始化追踪
config = TracingConfig(service_name="ai-agent-api")
tracer = DistributedTracer(config)

# 追踪 Agent 执行
with tracer.trace_agent_execution("agent-1", "task-1", "analysis"):
    # LLM 调用
    with tracer.trace_llm_call("gpt-4", 150):
        result = await call_llm(prompt)
    
    # 工具调用
    with tracer.trace_tool_call("web_search"):
        data = await search(query)
```

### 速率限制

```python
from rate_limiting.src.rate_limiter import TokenBucketLimiter

# 创建限流器
limiter = TokenBucketLimiter(rate=10, capacity=20)

# 检查是否允许请求
if limiter.is_allowed(user_id):
    # 处理请求
    process_request()
else:
    # 返回 429 错误
    return "Rate limit exceeded"
```

### 备份和恢复

```bash
# 创建备份
./06-backup/scripts/backup.sh

# 恢复备份
./06-backup/scripts/restore.sh postgres /backups/postgres_20240101_120000.sql.gz

# 使用 Python API
python
>>> from backup.src.backup_manager import BackupManager
>>> manager = BackupManager()
>>> manager.create_backup('postgres')
>>> manager.list_backups()
```

## 性能测试

### 负载测试

```bash
# 使用 Locust 进行负载测试
cd 05-performance
locust -f src/load_test.py --host=http://localhost:8000

# 访问 http://localhost:8089 进行测试
```

### 性能分析

```python
from performance.src.performance_profiler import PerformanceProfiler

profiler = PerformanceProfiler()

@profiler.profile_cpu
@profiler.profile_memory
def my_function():
    # 你的代码
    pass
```

## 告警配置

告警规则已在 `04-alerting/alerts.yml` 中定义：

- **高错误率**: 错误率 > 5%
- **高延迟**: P95 延迟 > 10 秒
- **LLM 成本过高**: 每小时成本 > $10
- **服务宕机**: Agent 服务不可用
- **资源告警**: CPU/内存/磁盘使用率过高

## 监控指标说明

### 核心指标

1. **agent_requests_total**: Agent 请求总数
2. **agent_request_duration_seconds**: 请求处理时长
3. **llm_tokens_total**: LLM Token 使用量
4. **llm_cost_total**: LLM 使用成本
5. **active_agents**: 当前活跃 Agent 数
6. **tool_calls_total**: 工具调用次数
7. **cache_operations_total**: 缓存操作统计

### Grafana 仪表板

预配置的仪表板包含以下面板：

- 请求速率趋势
- 请求延迟分布 (P50/P95/P99)
- LLM Token 使用和成本
- 错误率监控
- 缓存命中率
- 系统资源使用

## 日志查询示例

在 Kibana 中使用以下查询：

```
# 查找错误日志
level: "ERROR"

# 查找特定 Agent 的日志
agent_id: "agent-123"

# 查找慢查询
duration: >10

# 查找 LLM 调用
llm_call.model: "gpt-4"

# 成本分析
llm_call.cost: >1
```

## 故障排查

### 常见问题

1. **Prometheus 无法抓取指标**
   - 检查应用是否启动了 metrics 服务器
   - 验证防火墙规则
   - 查看 Prometheus targets 页面

2. **日志未显示在 Kibana**
   - 检查 Filebeat 是否运行
   - 验证 Logstash 管道配置
   - 检查 Elasticsearch 索引

3. **追踪数据未显示在 Jaeger**
   - 验证 Jaeger agent 是否运行
   - 检查应用的追踪配置
   - 查看 Jaeger 采样率设置

## 最佳实践

1. **监控**
   - 设置合理的告警阈值
   - 定期检查仪表板
   - 关注长期趋势

2. **日志**
   - 使用结构化日志
   - 包含足够的上下文信息
   - 避免记录敏感信息

3. **追踪**
   - 为关键操作添加 span
   - 使用有意义的 span 名称
   - 添加相关属性和事件

4. **性能**
   - 定期进行负载测试
   - 监控资源使用趋势
   - 优化慢查询和热点代码

5. **备份**
   - 自动化备份流程
   - 定期测试恢复过程
   - 异地备份存储

## 技术栈

- **监控**: Prometheus, Grafana, Node Exporter
- **日志**: Elasticsearch, Logstash, Kibana, Filebeat
- **追踪**: Jaeger, OpenTelemetry
- **告警**: AlertManager, Slack, PagerDuty
- **性能**: Locust, cProfile, py-spy
- **备份**: pg_dump, Redis RDB, AWS S3

## 参考资料

- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [ELK Stack 指南](https://www.elastic.co/guide/)
- [Jaeger 文档](https://www.jaegertracing.io/docs/)
- [OpenTelemetry 文档](https://opentelemetry.io/docs/)

## 许可证

MIT License
