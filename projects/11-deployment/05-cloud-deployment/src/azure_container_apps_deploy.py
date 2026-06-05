"""
Azure Container Apps 部署脚本
将容器化应用部署到 Azure Container Apps
"""

import subprocess
import sys
import json
from typing import Dict, Optional


# 配置
RESOURCE_GROUP = "ai-agent-rg"
LOCATION = "eastus"
CONTAINER_APP_ENV = "ai-agent-env"
CONTAINER_APP_NAME = "ai-agent"
CONTAINER_REGISTRY = "youracr.azurecr.io"
IMAGE_NAME = f"{CONTAINER_REGISTRY}/ai-agent"
CPU = "1.0"
MEMORY = "2.0Gi"
MIN_REPLICAS = 1
MAX_REPLICAS = 10


class AzureContainerAppsDeployer:
    """Azure Container Apps 部署器"""

    def __init__(
        self,
        resource_group: str = RESOURCE_GROUP,
        location: str = LOCATION
    ):
        self.resource_group = resource_group
        self.location = location

    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """执行 Azure CLI 命令"""
        print(f"执行: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if check and result.returncode != 0:
            print(f"❌ 命令执行失败: {result.stderr}")
            sys.exit(1)

        return result

    def create_resource_group(self):
        """创建资源组"""
        print(f"📦 创建资源组: {self.resource_group}")

        cmd = f"az group create " \
              f"--name {self.resource_group} " \
              f"--location {self.location}"

        self.run_command(cmd)
        print("✅ 资源组创建成功")

    def create_container_app_environment(self):
        """创建 Container App 环境"""
        print(f"🌐 创建 Container App 环境: {CONTAINER_APP_ENV}")

        cmd = f"az containerapp env create " \
              f"--name {CONTAINER_APP_ENV} " \
              f"--resource-group {self.resource_group} " \
              f"--location {self.location}"

        self.run_command(cmd)
        print("✅ 环境创建成功")

    def push_image_to_acr(self, local_image: str = "ai-agent:latest", tag: str = "latest"):
        """推送镜像到 Azure Container Registry"""
        print(f"📦 推送镜像到 ACR...")

        # 登录 ACR
        registry_name = CONTAINER_REGISTRY.split('.')[0]
        login_cmd = f"az acr login --name {registry_name}"
        self.run_command(login_cmd)

        # 标记镜像
        image_uri = f"{IMAGE_NAME}:{tag}"
        tag_cmd = f"docker tag {local_image} {image_uri}"
        self.run_command(tag_cmd)

        # 推送镜像
        push_cmd = f"docker push {image_uri}"
        self.run_command(push_cmd)

        print(f"✅ 镜像推送成功: {image_uri}")
        return image_uri

    def create_container_app(
        self,
        image_uri: str,
        env_vars: Optional[Dict[str, str]] = None,
        secrets: Optional[Dict[str, str]] = None
    ):
        """创建或更新 Container App"""
        print(f"🚀 部署 Container App: {CONTAINER_APP_NAME}")

        cmd_parts = [
            "az containerapp create",
            f"--name {CONTAINER_APP_NAME}",
            f"--resource-group {self.resource_group}",
            f"--environment {CONTAINER_APP_ENV}",
            f"--image {image_uri}",
            f"--target-port 8000",
            "--ingress external",
            f"--cpu {CPU}",
            f"--memory {MEMORY}",
            f"--min-replicas {MIN_REPLICAS}",
            f"--max-replicas {MAX_REPLICAS}",
        ]

        # 添加环境变量
        if env_vars:
            for key, value in env_vars.items():
                cmd_parts.append(f"--env-vars {key}={value}")

        # 添加密钥
        if secrets:
            for key, value in secrets.items():
                cmd_parts.append(f"--secrets {key}={value}")

        cmd = " ".join(cmd_parts)
        self.run_command(cmd)

        print("✅ Container App 创建成功")

    def update_container_app(self, image_uri: str):
        """更新现有的 Container App"""
        print(f"🔄 更新 Container App: {CONTAINER_APP_NAME}")

        cmd = f"az containerapp update " \
              f"--name {CONTAINER_APP_NAME} " \
              f"--resource-group {self.resource_group} " \
              f"--image {image_uri}"

        self.run_command(cmd)
        print("✅ Container App 更新成功")

    def get_app_url(self) -> str:
        """获取应用 URL"""
        cmd = f"az containerapp show " \
              f"--name {CONTAINER_APP_NAME} " \
              f"--resource-group {self.resource_group} " \
              f"--query properties.configuration.ingress.fqdn " \
              f"--output tsv"

        result = self.run_command(cmd)
        fqdn = result.stdout.strip()
        url = f"https://{fqdn}"

        print(f"🌐 应用 URL: {url}")
        return url

    def full_deploy(self, local_image: str = "ai-agent:latest", tag: str = "latest"):
        """完整的部署流程"""
        print("=" * 60)
        print("🚀 开始 Azure Container Apps 部署")
        print("=" * 60)

        try:
            # 1. 创建资源组（如果不存在）
            self.create_resource_group()

            # 2. 创建环境（如果不存在）
            self.create_container_app_environment()

            # 3. 推送镜像到 ACR
            image_uri = self.push_image_to_acr(local_image, tag)

            # 4. 创建或更新 Container App
            env_vars = {
                "ENV": "production",
                "LOG_LEVEL": "INFO"
            }

            secrets = {
                "openai-key": "your-openai-key",
                "database-url": "your-database-url"
            }

            # 尝试更新，如果失败则创建
            try:
                self.update_container_app(image_uri)
            except:
                self.create_container_app(image_uri, env_vars, secrets)

            # 5. 获取应用 URL
            self.get_app_url()

            # 6. 健康检查
            self.health_check()

            print("=" * 60)
            print("✅ 部署成功完成！")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 部署失败: {str(e)}")
            sys.exit(1)

    def health_check(self):
        """健康检查"""
        import time
        import requests

        print("🏥 执行健康检查...")

        url = self.get_app_url()
        health_url = f"{url}/health"

        for i in range(5):
            try:
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ 健康检查通过: {response.json()}")
                    return
            except Exception as e:
                print(f"⏳ 等待服务就绪... ({i+1}/5)")
                time.sleep(5)

        print("❌ 健康检查失败")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='部署到 Azure Container Apps')
    parser.add_argument('--resource-group', default=RESOURCE_GROUP, help='资源组名称')
    parser.add_argument('--location', default=LOCATION, help='部署位置')
    parser.add_argument('--image', default='ai-agent:latest', help='本地镜像名称')
    parser.add_argument('--tag', default='latest', help='镜像标签')

    args = parser.parse_args()

    deployer = AzureContainerAppsDeployer(
        resource_group=args.resource_group,
        location=args.location
    )
    deployer.full_deploy(local_image=args.image, tag=args.tag)
