"""
完整的监控示例
演示如何在实际应用中集成监控、日志和追踪
"""

import asyncio
import random
import time
from typing import Dict, Any

# 导入监控组件
import sys
sys.path.append('../01-monitoring/src')
sys.path.append('../02-logging/src')
sys.path.append('../03-tracing/src')

from metrics import collector, track_agent_request, track_llm_call
from structured_logging import logger
from distributed_tracing import TracingConfig, DistributedTracer


class MonitoredAgent:
    """集成监控的 AI Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

        # 初始化追踪
        tracing_config = TracingConfig(
            service_name=f"agent-{agent_id}",
            jaeger_host="localhost",
            jaeger_port=6831
        )
        self.tracer = DistributedTracer(tracing_config)

    @track_agent_request("demo_agent", "analysis")
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务（集成完整监控）

        特点：
        1. 自动记录 Prometheus 指标
        2. 结构化日志记录
        3. 分布式追踪
        """
        task_id = task.get('task_id', 'unknown')
        task_type = task.get('type', 'general')

        # 记录开始日志
        logger.info(
            f"开始执行任务: {task_type}",
            agent_id=self.agent_id,
            task_id=task_id,
            extra_data={'priority': task.get('priority', 'normal')}
        )

        # 创建追踪 span
        with self.tracer.trace_agent_execution(
            agent_id=self.agent_id,
            task_id=task_id,
            task_type=task_type
        ) as span:

            try:
                # 1. 规划阶段
                with self.tracer.tracer.start_as_current_span("planning"):
                    await asyncio.sleep(0.1)
                    plan = await self._plan_task(task)

                # 2. LLM 调用
                llm_result = await self._call_llm(
                    task_id=task_id,
                    prompt=task.get('prompt', '')
                )

                # 3. 工具调用（如果需要）
                if task.get('use_tools'):
                    tool_result = await self._call_tool(
                        task_id=task_id,
                        tool_name=task.get('tool', 'default')
                    )

                # 4. 合成结果
                result = {
                    'status': 'success',
                    'task_id': task_id,
                    'result': 'Task completed successfully',
                    'llm_tokens': llm_result.get('tokens', 0)
                }

                # 记录成功日志
                logger.log_agent_request(
                    agent_id=self.agent_id,
                    task_id=task_id,
                    task_type=task_type,
                    status='success',
                    duration=time.time() - span.start_time if hasattr(span, 'start_time') else 0
                )

                return result

            except Exception as e:
                # 记录错误
                logger.error(
                    f"任务执行失败: {str(e)}",
                    agent_id=self.agent_id,
                    task_id=task_id,
                    exc_info=True
                )

                # 标记 span 为错误
                self.tracer.set_error(span, e)

                raise

    async def _plan_task(self, task: Dict) -> Dict:
        """任务规划"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return {'steps': 3, 'estimated_time': 5}

    @track_llm_call("gpt-4")
    async def _call_llm(self, task_id: str, prompt: str) -> Dict:
        """调用 LLM"""
        start_time = time.time()

        # 追踪 LLM 调用
        with self.tracer.trace_llm_call(
            model="gpt-4",
            prompt_length=len(prompt)
        ) as llm_span:

            # 模拟 LLM 调用
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # 模拟 token 使用
            prompt_tokens = len(prompt.split()) * 1.3
            completion_tokens = random.randint(50, 200)
            total_tokens = int(prompt_tokens + completion_tokens)

            # 设置 span 属性
            llm_span.set_attribute("llm.prompt_tokens", int(prompt_tokens))
            llm_span.set_attribute("llm.completion_tokens", completion_tokens)
            llm_span.set_attribute("llm.total_tokens", total_tokens)

            duration = time.time() - start_time

            # 记录 LLM 使用指标
            collector.record_llm_usage(
                model="gpt-4",
                prompt_tokens=int(prompt_tokens),
                completion_tokens=completion_tokens,
                duration=duration
            )

            # 记录 LLM 日志
            logger.log_llm_call(
                agent_id=self.agent_id,
                model="gpt-4",
                prompt_tokens=int(prompt_tokens),
                completion_tokens=completion_tokens,
                duration=duration,
                cost=collector._calculate_cost("gpt-4", int(prompt_tokens), completion_tokens),
                task_id=task_id
            )

            return {
                'usage': {
                    'prompt_tokens': int(prompt_tokens),
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens
                },
                'tokens': total_tokens
            }

    async def _call_tool(self, task_id: str, tool_name: str) -> Dict:
        """调用工具"""
        start_time = time.time()

        # 追踪工具调用
        with self.tracer.trace_tool_call(tool_name):

            # 模拟工具调用
            await asyncio.sleep(random.uniform(0.2, 1.0))

            duration = time.time() - start_time
            status = "success" if random.random() > 0.1 else "error"

            # 记录工具调用指标
            collector.record_tool_call(tool_name, duration, status)

            # 记录工具调用日志
            logger.log_tool_call(
                agent_id=self.agent_id,
                tool_name=tool_name,
                duration=duration,
                status=status,
                task_id=task_id
            )

            return {'status': status, 'duration': duration}


async def demo_monitoring():
    """演示完整监控功能"""

    print("="*60)
    print("AI Agent 监控演示")
    print("="*60)
    print()

    # 启动指标服务器
    print("1. 启动 Prometheus 指标服务器...")
    collector.start_server()
    print("   ✓ 指标服务器运行在 http://localhost:8001")
    print()

    # 设置 Agent 信息
    collector.set_agent_info(
        version="1.0.0",
        environment="demo",
        python_version="3.11"
    )

    # 创建监控 Agent
    agent = MonitoredAgent(agent_id="demo-agent-1")

    print("2. 执行监控任务...")
    print()

    # 模拟多个任务
    tasks = [
        {
            'task_id': f'task-{i}',
            'type': 'data_analysis',
            'prompt': f'Analyze data for task {i}',
            'use_tools': i % 2 == 0,
            'tool': 'web_search' if i % 2 == 0 else None,
            'priority': 'high' if i < 3 else 'normal'
        }
        for i in range(10)
    ]

    successful = 0
    failed = 0

    for task in tasks:
        try:
            result = await agent.execute_task(task)
            successful += 1
            print(f"   ✓ {task['task_id']}: {result['status']}")
        except Exception as e:
            failed += 1
            print(f"   ✗ {task['task_id']}: {str(e)}")

        # 短暂延迟
        await asyncio.sleep(0.5)

    print()
    print("3. 任务执行统计:")
    print(f"   成功: {successful}")
    print(f"   失败: {failed}")
    print()

    # 更新系统指标
    print("4. 系统资源指标:")
    collector.update_system_metrics()
    print("   ✓ 已更新系统指标")
    print()

    print("="*60)
    print("监控演示完成！")
    print("="*60)
    print()
    print("访问以下 URL 查看监控数据:")
    print("  • Prometheus 指标: http://localhost:8001")
    print("  • Grafana 仪表板: http://localhost:3000")
    print("  • Jaeger 追踪: http://localhost:16686")
    print()
    print("在 Jaeger UI 中搜索服务: agent-demo-agent-1")
    print()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_monitoring())

    print("按 Ctrl+C 退出...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n演示已停止")
