"""
配置文件 - 统一管理LLM配置
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMConfig:
    """LLM配置类"""

    def __init__(self):
        # OpenAI配置
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

        # DeepSeek配置
        self.deepseek_api_key: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url: str = "https://api.deepseek.com/v1"
        self.deepseek_model: str = "deepseek-chat"

        # 默认使用的提供商
        self.default_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

        # 通用配置
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
        self.timeout: int = int(os.getenv("TIMEOUT", "60"))

    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """获取指定提供商的API Key"""
        provider = provider or self.default_provider

        if provider.lower() == "deepseek":
            return self.deepseek_api_key
        elif provider.lower() == "openai":
            return self.openai_api_key
        else:
            return self.openai_api_key

    def get_base_url(self, provider: Optional[str] = None) -> str:
        """获取指定提供商的Base URL"""
        provider = provider or self.default_provider

        if provider.lower() == "deepseek":
            return self.deepseek_base_url
        elif provider.lower() == "openai":
            return self.openai_base_url
        else:
            return self.openai_base_url

    def get_model(self, provider: Optional[str] = None) -> str:
        """获取指定提供商的模型名称"""
        provider = provider or self.default_provider

        if provider.lower() == "deepseek":
            return self.deepseek_model
        elif provider.lower() == "openai":
            return self.openai_model
        else:
            return self.openai_model

    def validate(self) -> bool:
        """验证配置是否完整"""
        api_key = self.get_api_key()
        if not api_key:
            print(f"错误: 未找到 {self.default_provider} 的 API Key")
            print("请在 .env 文件中配置相应的API Key")
            return False
        return True


# 全局配置实例
config = LLMConfig()
