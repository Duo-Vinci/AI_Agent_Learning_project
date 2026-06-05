"""
密钥管理模块
支持多种密钥管理方案：AWS Secrets Manager、环境变量、本地文件
"""

import os
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger()


class SecretProvider(ABC):
    """密钥提供者抽象基类"""

    @abstractmethod
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """获取密钥"""
        pass


class EnvironmentSecretProvider(SecretProvider):
    """从环境变量获取密钥"""

    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """从环境变量获取密钥"""
        value = os.getenv(secret_name)
        if value is None:
            logger.warning("secret_not_found", secret_name=secret_name)
            return {}

        logger.info("secret_retrieved", secret_name=secret_name, source="environment")
        return {secret_name: value}


class FileSecretProvider(SecretProvider):
    """从文件获取密钥"""

    def __init__(self, secrets_dir: str = "/run/secrets"):
        self.secrets_dir = secrets_dir

    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """从文件读取密钥（Docker Secrets 模式）"""
        secret_path = os.path.join(self.secrets_dir, secret_name)

        try:
            with open(secret_path, 'r') as f:
                content = f.read().strip()

            logger.info("secret_retrieved", secret_name=secret_name, source="file")
            return {secret_name: content}

        except FileNotFoundError:
            logger.warning("secret_file_not_found", secret_path=secret_path)
            return {}
        except Exception as e:
            logger.error("secret_read_error", secret_name=secret_name, error=str(e))
            return {}


class AWSSecretsManagerProvider(SecretProvider):
    """从 AWS Secrets Manager 获取密钥"""

    def __init__(self, region_name: str = "us-east-1"):
        try:
            import boto3
            self.client = boto3.client('secretsmanager', region_name=region_name)
            self.available = True
        except ImportError:
            logger.warning("aws_sdk_not_available", message="boto3 not installed")
            self.available = False
        except Exception as e:
            logger.error("aws_client_init_error", error=str(e))
            self.available = False

    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """从 AWS Secrets Manager 获取密钥"""
        if not self.available:
            return {}

        try:
            response = self.client.get_secret_value(SecretId=secret_name)

            # 解析密钥
            if 'SecretString' in response:
                secret_data = json.loads(response['SecretString'])
            else:
                # 二进制密钥
                import base64
                secret_data = base64.b64decode(response['SecretBinary'])

            logger.info("secret_retrieved", secret_name=secret_name, source="aws_secrets_manager")
            return secret_data

        except self.client.exceptions.ResourceNotFoundException:
            logger.warning("aws_secret_not_found", secret_name=secret_name)
            return {}
        except Exception as e:
            logger.error("aws_secret_error", secret_name=secret_name, error=str(e))
            return {}


class GCPSecretManagerProvider(SecretProvider):
    """从 GCP Secret Manager 获取密钥"""

    def __init__(self, project_id: Optional[str] = None):
        try:
            from google.cloud import secretmanager
            self.client = secretmanager.SecretManagerServiceClient()
            self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
            self.available = True
        except ImportError:
            logger.warning("gcp_sdk_not_available", message="google-cloud-secret-manager not installed")
            self.available = False
        except Exception as e:
            logger.error("gcp_client_init_error", error=str(e))
            self.available = False

    def get_secret(self, secret_name: str, version: str = "latest") -> Dict[str, Any]:
        """从 GCP Secret Manager 获取密钥"""
        if not self.available or not self.project_id:
            return {}

        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": name})

            secret_value = response.payload.data.decode('UTF-8')

            # 尝试解析为 JSON
            try:
                secret_data = json.loads(secret_value)
            except json.JSONDecodeError:
                secret_data = {secret_name: secret_value}

            logger.info("secret_retrieved", secret_name=secret_name, source="gcp_secret_manager")
            return secret_data

        except Exception as e:
            logger.error("gcp_secret_error", secret_name=secret_name, error=str(e))
            return {}


class SecretsManager:
    """统一的密钥管理器"""

    def __init__(self, provider: Optional[SecretProvider] = None):
        """
        初始化密钥管理器

        Args:
            provider: 密钥提供者，如果为 None，则根据环境自动选择
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._auto_select_provider()

        logger.info("secrets_manager_initialized", provider=type(self.provider).__name__)

    def _auto_select_provider(self) -> SecretProvider:
        """根据环境自动选择密钥提供者"""

        # 检查是否在 AWS 环境
        if os.getenv('AWS_EXECUTION_ENV') or os.getenv('AWS_REGION'):
            logger.info("detected_aws_environment")
            return AWSSecretsManagerProvider()

        # 检查是否在 GCP 环境
        if os.getenv('GCP_PROJECT_ID') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            logger.info("detected_gcp_environment")
            return GCPSecretManagerProvider()

        # 检查是否有 Docker Secrets
        if os.path.exists('/run/secrets'):
            logger.info("detected_docker_secrets")
            return FileSecretProvider()

        # 默认使用环境变量
        logger.info("using_environment_variables")
        return EnvironmentSecretProvider()

    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """获取密钥"""
        return self.provider.get_secret(secret_name)

    def get_secret_value(self, secret_name: str, key: Optional[str] = None) -> Optional[str]:
        """
        获取单个密钥值

        Args:
            secret_name: 密钥名称
            key: 如果密钥是 JSON 对象，指定要获取的键

        Returns:
            密钥值或 None
        """
        secret_data = self.get_secret(secret_name)

        if not secret_data:
            return None

        if key:
            return secret_data.get(key)

        # 如果没有指定 key，返回第一个值
        return list(secret_data.values())[0] if secret_data else None


# 全局密钥管理器实例
secrets_manager = SecretsManager()


def get_api_key(service: str) -> Optional[str]:
    """
    便捷函数：获取 API Key

    Args:
        service: 服务名称（如 'openai', 'anthropic'）

    Returns:
        API Key 或 None
    """
    key_name = f"{service.upper()}_API_KEY"

    # 首先尝试从环境变量获取
    api_key = os.getenv(key_name)
    if api_key:
        return api_key

    # 然后尝试从密钥管理器获取
    secret_data = secrets_manager.get_secret("api-keys")
    return secret_data.get(key_name)


if __name__ == "__main__":
    # 测试示例
    print("=== 测试密钥管理器 ===")

    # 测试环境变量
    os.environ['TEST_SECRET'] = 'test_value_123'
    manager = SecretsManager(EnvironmentSecretProvider())
    result = manager.get_secret('TEST_SECRET')
    print(f"环境变量密钥: {result}")

    # 测试获取 API Key
    api_key = get_api_key('openai')
    print(f"OpenAI API Key: {api_key[:10] if api_key else 'Not found'}...")
