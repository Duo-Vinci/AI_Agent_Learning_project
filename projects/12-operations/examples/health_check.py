"""
健康检查和问题诊断工具
"""

import psutil
import requests
import redis
import psycopg2
from typing import Dict, List
from datetime import datetime
import subprocess


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.checks = []

    async def check_all(self) -> Dict:
        """执行所有健康检查"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {},
            'overall_status': 'healthy'
        }

        # 系统资源检查
        results['checks']['system'] = self.check_system_resources()

        # 数据库检查
        results['checks']['database'] = await self.check_database()

        # Redis 检查
        results['checks']['redis'] = self.check_redis()

        # HTTP 服务检查
        results['checks']['services'] = self.check_services()

        # 磁盘空间检查
        results['checks']['disk'] = self.check_disk_space()

        # 判断整体状态
        for check_name, check_result in results['checks'].items():
            if check_result.get('status') == 'unhealthy':
                results['overall_status'] = 'unhealthy'
                break
            elif check_result.get('status') == 'degraded':
                results['overall_status'] = 'degraded'

        return results

    def check_system_resources(self) -> Dict:
        """检查系统资源"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        status = 'healthy'
        issues = []

        if cpu_percent > 80:
            status = 'degraded'
            issues.append(f'CPU 使用率过高: {cpu_percent}%')

        if memory.percent > 85:
            status = 'degraded'
            issues.append(f'内存使用率过高: {memory.percent}%')

        return {
            'status': status,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'issues': issues
        }

    async def check_database(self) -> Dict:
        """检查 PostgreSQL 数据库"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                user='postgres',
                database='agentdb',
                connect_timeout=5
            )

            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()

            cursor.close()
            conn.close()

            return {
                'status': 'healthy',
                'message': 'Database connection successful'
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_redis(self) -> Dict:
        """检查 Redis"""
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=5)
            r.ping()

            info = r.info()
            memory_used_mb = info['used_memory'] / (1024 * 1024)

            return {
                'status': 'healthy',
                'memory_used_mb': memory_used_mb,
                'connected_clients': info['connected_clients']
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_services(self) -> Dict:
        """检查 HTTP 服务"""
        services = {
            'prometheus': 'http://localhost:9090/-/healthy',
            'grafana': 'http://localhost:3000/api/health',
            'jaeger': 'http://localhost:16686',
        }

        results = {}

        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                results[name] = {
                    'status': 'healthy' if response.status_code == 200 else 'degraded',
                    'status_code': response.status_code
                }
            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }

        overall_status = 'healthy'
        if any(r['status'] == 'unhealthy' for r in results.values()):
            overall_status = 'unhealthy'

        return {
            'status': overall_status,
            'services': results
        }

    def check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        disk = psutil.disk_usage('/')

        status = 'healthy'
        if disk.percent > 90:
            status = 'unhealthy'
        elif disk.percent > 80:
            status = 'degraded'

        return {
            'status': status,
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': disk.percent
        }


class DiagnosticTool:
    """诊断工具"""

    def diagnose_high_latency(self) -> List[str]:
        """诊断高延迟问题"""
        suggestions = []

        # 检查 CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            suggestions.append(
                f"CPU 使用率过高 ({cpu_percent}%)，考虑: "
                "1) 优化代码性能 2) 增加服务器资源 3) 实现负载均衡"
            )

        # 检查内存
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            suggestions.append(
                f"内存使用率过高 ({memory.percent}%)，考虑: "
                "1) 检查内存泄漏 2) 增加服务器内存 3) 优化缓存策略"
            )

        # 检查磁盘 I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            suggestions.append(
                "检查磁盘 I/O 性能，考虑: "
                "1) 使用 SSD 2) 优化数据库查询 3) 增加缓存"
            )

        return suggestions or ["系统资源正常，延迟可能由网络或外部服务引起"]

    def diagnose_high_error_rate(self) -> List[str]:
        """诊断高错误率问题"""
        return [
            "检查应用日志中的错误模式",
            "验证外部 API (LLM, 数据库) 的可用性",
            "检查网络连接和超时设置",
            "审查最近的代码变更",
            "验证配置文件和环境变量"
        ]

    def diagnose_high_cost(self) -> List[str]:
        """诊断 LLM 成本过高"""
        return [
            "启用响应缓存，减少重复调用",
            "优化 Prompt，减少 Token 使用",
            "考虑使用更便宜的模型 (如 GPT-3.5)",
            "实现智能路由，根据任务复杂度选择模型",
            "设置成本预算和告警"
        ]


# 使用示例
if __name__ == "__main__":
    import asyncio

    print("=== AI Agent 健康检查 ===\n")

    checker = HealthChecker()

    async def run_checks():
        results = await checker.check_all()

        print(f"整体状态: {results['overall_status'].upper()}")
        print(f"检查时间: {results['timestamp']}\n")

        for check_name, check_result in results['checks'].items():
            status_icon = {
                'healthy': '✓',
                'degraded': '⚠',
                'unhealthy': '✗'
            }.get(check_result.get('status'), '?')

            print(f"{status_icon} {check_name}: {check_result.get('status', 'unknown')}")

            if 'issues' in check_result and check_result['issues']:
                for issue in check_result['issues']:
                    print(f"    - {issue}")

        print("\n=== 诊断建议 ===\n")

        diagnostic = DiagnosticTool()

        print("高延迟问题诊断:")
        for suggestion in diagnostic.diagnose_high_latency():
            print(f"  • {suggestion}")

    asyncio.run(run_checks())
