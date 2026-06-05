"""
负载测试工具
使用 Locust 进行压力测试
"""

from locust import HttpUser, task, between, events
import random
import time
from typing import Dict, Any


class AgentAPIUser(HttpUser):
    """模拟 Agent API 用户"""

    # 用户等待时间（秒）
    wait_time = between(1, 3)

    def on_start(self):
        """用户开始时执行（类似登录）"""
        self.user_id = f"user_{random.randint(1000, 9999)}"
        print(f"用户 {self.user_id} 开始测试")

    @task(3)  # 权重为 3（更频繁）
    def execute_simple_task(self):
        """执行简单任务"""
        payload = {
            "task_id": f"task_{int(time.time())}",
            "type": "simple_query",
            "prompt": "请帮我总结一下今天的新闻",
            "priority": "normal",
            "user_id": self.user_id
        }

        with self.client.post(
            "/agent/execute",
            json=payload,
            name="/agent/execute [simple]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response.success()
                else:
                    response.failure(f"任务失败: {data}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)  # 权重为 2
    def execute_complex_task(self):
        """执行复杂任务（使用工具）"""
        payload = {
            "task_id": f"task_{int(time.time())}",
            "type": "data_analysis",
            "prompt": "分析最近的市场趋势并给出投资建议",
            "use_tools": True,
            "tool": "web_search",
            "priority": "high",
            "user_id": self.user_id
        }

        with self.client.post(
            "/agent/execute",
            json=payload,
            name="/agent/execute [complex]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)  # 权重为 1（最不频繁）
    def execute_long_running_task(self):
        """执行长时间运行的任务"""
        payload = {
            "task_id": f"task_{int(time.time())}",
            "type": "report_generation",
            "prompt": "生成完整的季度报告，包含所有数据分析和可视化",
            "priority": "low",
            "user_id": self.user_id
        }

        # 设置超时时间
        with self.client.post(
            "/agent/execute",
            json=payload,
            name="/agent/execute [long]",
            timeout=60,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(5)  # 权重为 5（最频繁）
    def health_check(self):
        """健康检查"""
        with self.client.get(
            "/health",
            name="/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    def on_stop(self):
        """用户结束时执行"""
        print(f"用户 {self.user_id} 测试结束")


class AgentLLMUser(HttpUser):
    """模拟高频 LLM 调用用户（压力测试）"""

    wait_time = between(0.1, 0.5)  # 更短的等待时间

    @task
    def rapid_llm_calls(self):
        """快速 LLM 调用"""
        models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]

        payload = {
            "model": random.choice(models),
            "prompt": f"快速查询 {random.randint(1, 1000)}",
            "max_tokens": 100
        }

        self.client.post("/llm/quick", json=payload, name="/llm/quick")


# Locust 事件处理器
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时触发"""
    print("\n" + "="*60)
    print("负载测试开始")
    print(f"目标: {environment.host}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时触发"""
    print("\n" + "="*60)
    print("负载测试完成")
    print("="*60 + "\n")

    # 打印统计信息
    stats = environment.stats
    print(f"总请求数: {stats.total.num_requests}")
    print(f"失败数: {stats.total.num_failures}")
    print(f"平均响应时间: {stats.total.avg_response_time:.2f} ms")
    print(f"P95 响应时间: {stats.total.get_response_time_percentile(0.95):.2f} ms")
    print(f"P99 响应时间: {stats.total.get_response_time_percentile(0.99):.2f} ms")
    print(f"RPS (请求/秒): {stats.total.total_rps:.2f}")


# 自定义形状类（逐步增加负载）
from locust import LoadTestShape

class StagesShape(LoadTestShape):
    """
    阶梯式负载测试
    逐步增加用户数和请求速率
    """

    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},   # 第1分钟: 10用户
        {"duration": 120, "users": 50, "spawn_rate": 5},  # 第2分钟: 50用户
        {"duration": 180, "users": 100, "spawn_rate": 10}, # 第3分钟: 100用户
        {"duration": 240, "users": 200, "spawn_rate": 20}, # 第4分钟: 200用户
        {"duration": 300, "users": 100, "spawn_rate": 10}, # 第5分钟: 降至100用户
    ]

    def tick(self):
        """返回当前时间点的用户数和生成速率"""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None  # 测试结束


# 运行说明
"""
运行负载测试:

1. 基础测试（Web UI）:
   locust -f load_test.py --host=http://localhost:8000

   然后访问 http://localhost:8089 打开 Web 界面

2. 无头模式（命令行）:
   locust -f load_test.py --host=http://localhost:8000 \\
          --users 100 --spawn-rate 10 --run-time 5m --headless

3. 使用自定义负载形状:
   locust -f load_test.py --host=http://localhost:8000 \\
          --headless --shape StagesShape

4. 分布式负载测试:
   # Master 节点
   locust -f load_test.py --master

   # Worker 节点（可多个）
   locust -f load_test.py --worker --master-host=<master-ip>

性能测试检查清单:
- [ ] 设置合理的测试目标（RPS、并发用户数）
- [ ] 确保测试环境与生产环境相似
- [ ] 监控系统资源（CPU、内存、网络）
- [ ] 记录响应时间百分位数（P50, P95, P99）
- [ ] 识别性能瓶颈和错误模式
- [ ] 测试系统在高负载下的稳定性
- [ ] 验证自动扩展策略
- [ ] 测试恢复能力（从故障中恢复）
"""
