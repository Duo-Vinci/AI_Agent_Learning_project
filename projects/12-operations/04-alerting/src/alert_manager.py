"""
告警规则测试和管理工具
"""

import yaml
import requests
from typing import List, Dict, Any
from datetime import datetime
import time


class AlertManager:
    """告警管理器客户端"""

    def __init__(self, alertmanager_url: str = "http://localhost:9093"):
        self.base_url = alertmanager_url
        self.api_url = f"{alertmanager_url}/api/v2"

    def get_alerts(self, active: bool = True) -> List[Dict]:
        """
        获取告警列表

        Args:
            active: 只返回活跃告警
        """
        params = {"active": str(active).lower()}
        response = requests.get(f"{self.api_url}/alerts", params=params)
        response.raise_for_status()
        return response.json()

    def get_alert_groups(self) -> List[Dict]:
        """获取告警组"""
        response = requests.get(f"{self.api_url}/alerts/groups")
        response.raise_for_status()
        return response.json()

    def create_silence(
        self,
        matchers: List[Dict[str, str]],
        duration_hours: int = 2,
        created_by: str = "admin",
        comment: str = "Manual silence"
    ) -> Dict:
        """
        创建静默规则

        Args:
            matchers: 匹配器列表，例如 [{"name": "alertname", "value": "HighErrorRate"}]
            duration_hours: 静默持续时间（小时）
            created_by: 创建者
            comment: 备注
        """
        starts_at = datetime.utcnow().isoformat() + "Z"
        ends_at = datetime.utcnow()
        ends_at = ends_at.replace(hour=ends_at.hour + duration_hours)
        ends_at = ends_at.isoformat() + "Z"

        silence_data = {
            "matchers": matchers,
            "startsAt": starts_at,
            "endsAt": ends_at,
            "createdBy": created_by,
            "comment": comment
        }

        response = requests.post(
            f"{self.api_url}/silences",
            json=silence_data
        )
        response.raise_for_status()
        return response.json()

    def get_silences(self) -> List[Dict]:
        """获取所有静默规则"""
        response = requests.get(f"{self.api_url}/silences")
        response.raise_for_status()
        return response.json()

    def delete_silence(self, silence_id: str):
        """删除静默规则"""
        response = requests.delete(f"{self.api_url}/silence/{silence_id}")
        response.raise_for_status()

    def get_status(self) -> Dict:
        """获取 AlertManager 状态"""
        response = requests.get(f"{self.api_url}/status")
        response.raise_for_status()
        return response.json()


class PrometheusAlertTester:
    """Prometheus 告警规则测试器"""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.base_url = prometheus_url

    def query(self, expr: str) -> Dict:
        """执行 PromQL 查询"""
        response = requests.get(
            f"{self.base_url}/api/v1/query",
            params={"query": expr}
        )
        response.raise_for_status()
        return response.json()

    def test_alert_expression(self, expr: str) -> bool:
        """
        测试告警表达式是否会触发

        Returns:
            True: 表达式条件满足（会触发告警）
            False: 表达式条件不满足
        """
        result = self.query(expr)

        if result["status"] != "success":
            raise Exception(f"Query failed: {result}")

        data = result["data"]["result"]

        # 如果有结果，说明条件满足
        return len(data) > 0

    def get_active_alerts(self) -> List[Dict]:
        """获取当前活跃的告警"""
        response = requests.get(f"{self.base_url}/api/v1/alerts")
        response.raise_for_status()

        data = response.json()
        if data["status"] == "success":
            return [
                alert for alert in data["data"]["alerts"]
                if alert["state"] == "firing"
            ]
        return []

    def load_rules_from_file(self, file_path: str) -> Dict:
        """从文件加载告警规则"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_alert_rules(self, rules_file: str) -> List[str]:
        """
        验证告警规则配置

        Returns:
            错误列表（空列表表示验证通过）
        """
        errors = []

        try:
            rules_config = self.load_rules_from_file(rules_file)

            # 检查必需字段
            if "groups" not in rules_config:
                errors.append("Missing 'groups' key in rules file")
                return errors

            for group_idx, group in enumerate(rules_config["groups"]):
                group_name = group.get("name", f"group_{group_idx}")

                # 检查规则组必需字段
                if "name" not in group:
                    errors.append(f"Group {group_idx}: missing 'name'")

                if "rules" not in group:
                    errors.append(f"Group {group_name}: missing 'rules'")
                    continue

                # 检查每个规则
                for rule_idx, rule in enumerate(group["rules"]):
                    rule_name = rule.get("alert", f"rule_{rule_idx}")

                    # 检查规则必需字段
                    required_fields = ["alert", "expr", "labels", "annotations"]
                    for field in required_fields:
                        if field not in rule:
                            errors.append(
                                f"Rule {group_name}.{rule_name}: missing '{field}'"
                            )

                    # 测试表达式语法
                    if "expr" in rule:
                        try:
                            self.query(rule["expr"])
                        except Exception as e:
                            errors.append(
                                f"Rule {group_name}.{rule_name}: invalid expression - {e}"
                            )

        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {e}")
        except Exception as e:
            errors.append(f"Validation error: {e}")

        return errors


# 使用示例
if __name__ == "__main__":
    # AlertManager 客户端
    am = AlertManager("http://localhost:9093")

    print("=== AlertManager 状态 ===")
    try:
        status = am.get_status()
        print(f"版本: {status.get('versionInfo', {}).get('version')}")
        print(f"运行时间: {status.get('uptime')}")
    except Exception as e:
        print(f"无法连接到 AlertManager: {e}")

    print("\n=== 活跃告警 ===")
    try:
        alerts = am.get_alerts(active=True)
        if alerts:
            for alert in alerts[:5]:  # 只显示前5个
                print(f"- {alert['labels'].get('alertname')}: {alert['annotations'].get('summary')}")
        else:
            print("当前没有活跃告警")
    except Exception as e:
        print(f"获取告警失败: {e}")

    print("\n=== 创建静默规则示例 ===")
    # 创建静默规则（对特定告警静默 2 小时）
    try:
        silence = am.create_silence(
            matchers=[
                {"name": "alertname", "value": "HighErrorRate", "isRegex": False}
            ],
            duration_hours=2,
            created_by="admin",
            comment="维护期间静默"
        )
        print(f"静默规则已创建，ID: {silence.get('silenceID')}")
    except Exception as e:
        print(f"创建静默规则失败: {e}")

    print("\n=== Prometheus 告警测试 ===")
    prom = PrometheusAlertTester("http://localhost:9090")

    # 验证告警规则文件
    print("验证告警规则配置...")
    errors = prom.validate_alert_rules("./alerts.yml")

    if errors:
        print("发现以下错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ 告警规则配置验证通过")

    # 检查活跃告警
    print("\n当前触发的告警:")
    try:
        active_alerts = prom.get_active_alerts()
        if active_alerts:
            for alert in active_alerts:
                print(f"  - {alert['labels']['alertname']}: {alert['state']}")
        else:
            print("  没有触发的告警")
    except Exception as e:
        print(f"  获取失败: {e}")

    # 测试特定告警表达式
    print("\n测试告警表达式:")
    test_expressions = [
        ("错误率测试", "rate(agent_requests_total{status=\"error\"}[5m]) > 0"),
        ("延迟测试", "histogram_quantile(0.95, rate(agent_request_duration_seconds_bucket[5m])) > 10"),
    ]

    for name, expr in test_expressions:
        try:
            would_fire = prom.test_alert_expression(expr)
            status = "会触发" if would_fire else "不会触发"
            print(f"  {name}: {status}")
        except Exception as e:
            print(f"  {name}: 测试失败 - {e}")
