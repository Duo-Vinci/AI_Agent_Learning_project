"""
AWS ECS 部署脚本
将 Docker 镜像部署到 AWS ECS (Elastic Container Service)
"""

import boto3
import time
import sys
from typing import Dict, Any

# 配置
AWS_REGION = "us-east-1"
ECR_REPOSITORY = "ai-agent"
ECS_CLUSTER = "ai-agent-cluster"
ECS_SERVICE = "ai-agent-service"
TASK_FAMILY = "ai-agent-task"
IMAGE_TAG = "latest"


class ECSDeployer:
    """AWS ECS 部署器"""

    def __init__(self, region: str = AWS_REGION):
        self.region = region
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.ecs_client = boto3.client('ecs', region_name=region)
        self.account_id = boto3.client('sts').get_caller_identity()['Account']

    def get_ecr_login(self) -> str:
        """获取 ECR 登录令牌"""
        print("🔑 获取 ECR 登录凭证...")

        response = self.ecr_client.get_authorization_token()
        token = response['authorizationData'][0]['authorizationToken']

        import base64
        username, password = base64.b64decode(token).decode().split(':')

        return password

    def push_image_to_ecr(self, local_image: str, tag: str = IMAGE_TAG):
        """推送 Docker 镜像到 ECR"""
        import subprocess

        ecr_url = f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com"
        repository_url = f"{ecr_url}/{ECR_REPOSITORY}"

        print(f"📦 推送镜像到 ECR: {repository_url}:{tag}")

        # 登录 ECR
        password = self.get_ecr_login()
        login_cmd = f"docker login -u AWS -p {password} {ecr_url}"
        subprocess.run(login_cmd, shell=True, check=True)

        # 标记镜像
        tag_cmd = f"docker tag {local_image} {repository_url}:{tag}"
        subprocess.run(tag_cmd, shell=True, check=True)

        # 推送镜像
        push_cmd = f"docker push {repository_url}:{tag}"
        subprocess.run(push_cmd, shell=True, check=True)

        print(f"✅ 镜像推送成功: {repository_url}:{tag}")

        return f"{repository_url}:{tag}"

    def register_task_definition(self, image_uri: str) -> str:
        """注册新的 ECS 任务定义"""
        print("📝 注册新的任务定义...")

        task_definition = {
            'family': TASK_FAMILY,
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': '1024',  # 1 vCPU
            'memory': '2048',  # 2 GB
            'executionRoleArn': f'arn:aws:iam::{self.account_id}:role/ecsTaskExecutionRole',
            'containerDefinitions': [
                {
                    'name': 'agent-api',
                    'image': image_uri,
                    'essential': True,
                    'portMappings': [
                        {
                            'containerPort': 8000,
                            'protocol': 'tcp'
                        }
                    ],
                    'environment': [
                        {'name': 'ENV', 'value': 'production'},
                        {'name': 'LOG_LEVEL', 'value': 'INFO'}
                    ],
                    'secrets': [
                        {
                            'name': 'OPENAI_API_KEY',
                            'valueFrom': f'arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:ai-agent/api-keys'
                        }
                    ],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': f'/ecs/{TASK_FAMILY}',
                            'awslogs-region': self.region,
                            'awslogs-stream-prefix': 'ecs'
                        }
                    },
                    'healthCheck': {
                        'command': ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
                        'interval': 30,
                        'timeout': 5,
                        'retries': 3,
                        'startPeriod': 60
                    }
                }
            ]
        }

        response = self.ecs_client.register_task_definition(**task_definition)

        task_def_arn = response['taskDefinition']['taskDefinitionArn']
        print(f"✅ 任务定义注册成功: {task_def_arn}")

        return task_def_arn

    def update_service(self, task_definition_arn: str):
        """更新 ECS 服务"""
        print(f"🚀 更新 ECS 服务: {ECS_SERVICE}")

        response = self.ecs_client.update_service(
            cluster=ECS_CLUSTER,
            service=ECS_SERVICE,
            taskDefinition=task_definition_arn,
            forceNewDeployment=True,
            deploymentConfiguration={
                'maximumPercent': 200,
                'minimumHealthyPercent': 100,
                'deploymentCircuitBreaker': {
                    'enable': True,
                    'rollback': True
                }
            }
        )

        print("✅ 服务更新请求已发送")

        return response

    def wait_for_deployment(self, timeout: int = 600):
        """等待部署完成"""
        print("⏳ 等待部署完成...")

        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print("❌ 部署超时")
                sys.exit(1)

            response = self.ecs_client.describe_services(
                cluster=ECS_CLUSTER,
                services=[ECS_SERVICE]
            )

            service = response['services'][0]
            deployments = service['deployments']

            # 检查是否只有一个部署且状态为 PRIMARY
            if len(deployments) == 1 and deployments[0]['status'] == 'PRIMARY':
                running_count = deployments[0]['runningCount']
                desired_count = deployments[0]['desiredCount']

                if running_count == desired_count:
                    print(f"✅ 部署完成！运行实例数: {running_count}/{desired_count}")
                    break

            print(f"   部署中... {len(deployments)} 个部署活跃")
            time.sleep(10)

    def deploy(self, local_image: str = "ai-agent:latest", tag: str = IMAGE_TAG):
        """执行完整部署流程"""
        print("=" * 60)
        print("🚀 开始 AWS ECS 部署")
        print("=" * 60)

        try:
            # 1. 推送镜像到 ECR
            image_uri = self.push_image_to_ecr(local_image, tag)

            # 2. 注册新的任务定义
            task_def_arn = self.register_task_definition(image_uri)

            # 3. 更新服务
            self.update_service(task_def_arn)

            # 4. 等待部署完成
            self.wait_for_deployment()

            print("=" * 60)
            print("✅ 部署成功完成！")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 部署失败: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='部署到 AWS ECS')
    parser.add_argument('--image', default='ai-agent:latest', help='本地镜像名称')
    parser.add_argument('--tag', default='latest', help='镜像标签')
    parser.add_argument('--region', default=AWS_REGION, help='AWS 区域')

    args = parser.parse_args()

    deployer = ECSDeployer(region=args.region)
    deployer.deploy(local_image=args.image, tag=args.tag)
