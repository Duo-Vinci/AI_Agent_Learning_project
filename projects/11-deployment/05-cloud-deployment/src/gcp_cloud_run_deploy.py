"""
Google Cloud Run 部署脚本
将容器化应用部署到 Google Cloud Run (Serverless)
"""

import subprocess
import sys
import json
from typing import Dict, Optional

# 配置
PROJECT_ID = "your-gcp-project-id"
REGION = "us-central1"
SERVICE_NAME = "ai-agent"
IMAGE_NAME = "gcr.io/{}/{}".format(PROJECT_ID, SERVICE_NAME)
MIN_INSTANCES = 1
MAX_INSTANCES = 10
MEMORY = "2Gi"
CPU = "2"


class CloudRunDeployer:
    """Google Cloud Run 部署器"""

    def __init__(self, project_id: str = PROJECT_ID, region: str = REGION):
        self.project_id = project_id
        self.region = region

    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """执行命令"""
        print(f"执行: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if check and result.returncode != 0:
            print(f"❌ 命令执行失败: {result.stderr}")
            sys.exit(1)

        return result

    def build_image(self, tag: str = "latest"):
        """使用 Cloud Build 构建镜像"""
        print(f"📦 使用 Cloud Build 构建镜像...")

        image_uri = f"{IMAGE_NAME}:{tag}"

        # 使用 Cloud Build
        cmd = f"gcloud builds submit --tag {image_uri} --project {self.project_id}"
        self.run_command(cmd)

        print(f"✅ 镜像构建成功: {image_uri}")
        return image_uri

    def deploy(
        self,
        image_uri: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        secrets: Optional[Dict[str, str]] = None
    ):
        """部署到 Cloud Run"""
        print(f"🚀 部署到 Cloud Run: {SERVICE_NAME}")

        if not image_uri:
            image_uri = f"{IMAGE_NAME}:latest"

        # 构建部署命令
        cmd_parts = [
            "gcloud run deploy",
            SERVICE_NAME,
            f"--image {image_uri}",
            f"--platform managed",
            f"--region {self.region}",
            f"--project {self.project_id}",
            f"--memory {MEMORY}",
            f"--cpu {CPU}",
            f"--min-instances {MIN_INSTANCES}",
            f"--max-instances {MAX_INSTANCES}",
            "--allow-unauthenticated",  # 允许未认证访问
            "--port 8000",
        ]

        # 添加环境变量
        if env_vars:
            env_str = ",".join([f"{k}={v}" for k, v in env_vars.items()])
            cmd_parts.append(f"--set-env-vars {env_str}")

        # 添加密钥引用
        if secrets:
            secret_str = ",".join([f"{k}={v}" for k, v in secrets.items()])
            cmd_parts.append(f"--set-secrets {secret_str}")

        cmd = " ".join(cmd_parts)
        self.run_command(cmd)

        print("✅ 部署完成")

        # 获取服务 URL
        self.get_service_url()

    def get_service_url(self) -> str:
        """获取服务 URL"""
        cmd = f"gcloud run services describe {SERVICE_NAME} " \
              f"--region {self.region} " \
              f"--project {self.project_id} " \
              f"--format 'value(status.url)'"

        result = self.run_command(cmd)
        url = result.stdout.strip()

        print(f"🌐 服务 URL: {url}")
        return url

    def full_deploy(self, tag: str = "latest"):
        """完整的构建和部署流程"""
        print("=" * 60)
        print("🚀 开始 Google Cloud Run 部署")
        print("=" * 60)

        try:
            # 1. 构建镜像
            image_uri = self.build_image(tag)

            # 2. 部署服务
            env_vars = {
                "ENV": "production",
                "LOG_LEVEL": "INFO"
            }

            secrets = {
                "OPENAI_API_KEY": "openai-api-key:latest",
                "DATABASE_URL": "database-url:latest"
            }

            self.deploy(image_uri, env_vars, secrets)

            # 3. 健康检查
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

        url = self.get_service_url()
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
        sys.exit(1)

    def rollback(self, revision: str):
        """回滚到指定版本"""
        print(f"⏮️ 回滚到版本: {revision}")

        cmd = f"gcloud run services update-traffic {SERVICE_NAME} " \
              f"--to-revisions {revision}=100 " \
              f"--region {self.region} " \
              f"--project {self.project_id}"

        self.run_command(cmd)
        print("✅ 回滚完成")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='部署到 Google Cloud Run')
    parser.add_argument('--project-id', default=PROJECT_ID, help='GCP 项目 ID')
    parser.add_argument('--region', default=REGION, help='部署区域')
    parser.add_argument('--service', default=SERVICE_NAME, help='服务名称')
    parser.add_argument('--tag', default='latest', help='镜像标签')
    parser.add_argument('--rollback', help='回滚到指定版本')

    args = parser.parse_args()

    deployer = CloudRunDeployer(project_id=args.project_id, region=args.region)

    if args.rollback:
        deployer.rollback(args.rollback)
    else:
        deployer.full_deploy(tag=args.tag)
