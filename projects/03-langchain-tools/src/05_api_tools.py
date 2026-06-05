"""
LangChain 工具使用 - 05: API调用工具

本模块演示：
1. REST API调用工具（GET/POST/PUT/DELETE）
2. API认证（Token, API Key, Bearer）
3. 请求头管理
4. 响应解析（JSON/XML）
5. 错误处理和重试机制
6. 超时控制
7. 实际API集成示例（GitHub, JSONPlaceholder）
"""

import os
import json
import time
from typing import Optional, Type, Dict, Any, List
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== HTTP客户端管理类 ====================

class HTTPClient:
    """HTTP客户端，支持重试和超时控制"""

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        初始化HTTP客户端

        Args:
            base_url: 基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            url: 请求URL
            headers: 请求头
            params: URL参数
            data: 表单数据
            json_data: JSON数据

        Returns:
            响应结果字典
        """
        try:
            # 构建完整URL
            full_url = self.base_url + url if not url.startswith("http") else url

            # 发送请求
            response = self.session.request(
                method=method,
                url=full_url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout
            )

            # 解析响应
            result = {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url
            }

            # 尝试解析JSON
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text

            return result

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时",
                "error_type": "TimeoutError"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "连接错误",
                "error_type": "ConnectionError"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "RequestException"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


# ==================== 示例1: GET请求工具 ====================

class GetRequestInput(BaseModel):
    """GET请求输入模式"""
    url: str = Field(description="请求URL")
    params: Optional[Dict[str, str]] = Field(
        default=None,
        description="URL查询参数"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="请求头"
    )


class GetRequestTool(BaseTool):
    """GET请求工具"""

    name: str = "get_request"
    description: str = """
    发送HTTP GET请求获取数据。

    示例:
    - url: "https://api.example.com/users"
    - params: {"page": "1", "limit": "10"}
    - headers: {"Authorization": "Bearer token123"}
    """
    args_schema: Type[BaseModel] = GetRequestInput
    http_client: HTTPClient = None

    def __init__(self, http_client: Optional[HTTPClient] = None):
        super().__init__()
        self.http_client = http_client or HTTPClient()

    def _run(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行GET请求"""
        result = self.http_client.request(
            method="GET",
            url=url,
            headers=headers,
            params=params
        )

        if result["success"]:
            output = f"✓ 请求成功 (状态码: {result['status_code']})\n"
            output += f"URL: {result['url']}\n\n"
            output += "响应数据:\n"
            output += json.dumps(result["data"], indent=2, ensure_ascii=False)
            return output
        else:
            return f"✗ 请求失败: {result['error']} ({result['error_type']})"


def demo_get_request():
    """示例1: GET请求工具"""
    print_section("示例1: GET请求工具")

    client = HTTPClient(base_url="https://jsonplaceholder.typicode.com")
    get_tool = GetRequestTool(http_client=client)

    # 获取用户列表
    print("1. 获取用户列表（前3条）:")
    result = get_tool.invoke({
        "url": "/users",
        "params": {"_limit": "3"}
    })
    print(result[:500] + "..." if len(result) > 500 else result)

    # 获取单个用户
    print("\n2. 获取ID为1的用户:")
    result = get_tool.invoke({"url": "/users/1"})
    print(result)

    # 获取帖子
    print("\n3. 获取用户1的帖子:")
    result = get_tool.invoke({
        "url": "/posts",
        "params": {"userId": "1", "_limit": "2"}
    })
    print(result[:500] + "..." if len(result) > 500 else result)


# ==================== 示例2: POST请求工具 ====================

class PostRequestInput(BaseModel):
    """POST请求输入模式"""
    url: str = Field(description="请求URL")
    data: Dict[str, Any] = Field(description="要发送的JSON数据")
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="请求头"
    )


class PostRequestTool(BaseTool):
    """POST请求工具"""

    name: str = "post_request"
    description: str = """
    发送HTTP POST请求创建或提交数据。

    示例:
    - url: "https://api.example.com/users"
    - data: {"name": "张三", "email": "zhangsan@example.com"}
    - headers: {"Content-Type": "application/json"}
    """
    args_schema: Type[BaseModel] = PostRequestInput
    http_client: HTTPClient = None

    def __init__(self, http_client: Optional[HTTPClient] = None):
        super().__init__()
        self.http_client = http_client or HTTPClient()

    def _run(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行POST请求"""
        # 设置默认Content-Type
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        result = self.http_client.request(
            method="POST",
            url=url,
            headers=headers,
            json_data=data
        )

        if result["success"]:
            output = f"✓ 请求成功 (状态码: {result['status_code']})\n"
            output += f"URL: {result['url']}\n\n"
            output += "响应数据:\n"
            output += json.dumps(result["data"], indent=2, ensure_ascii=False)
            return output
        else:
            return f"✗ 请求失败: {result['error']} ({result['error_type']})"


def demo_post_request():
    """示例2: POST请求工具"""
    print_section("示例2: POST请求工具")

    client = HTTPClient(base_url="https://jsonplaceholder.typicode.com")
    post_tool = PostRequestTool(http_client=client)

    # 创建帖子
    print("1. 创建新帖子:")
    result = post_tool.invoke({
        "url": "/posts",
        "data": {
            "title": "LangChain学习笔记",
            "body": "今天学习了如何创建API工具",
            "userId": 1
        }
    })
    print(result)

    # 创建评论
    print("\n2. 创建新评论:")
    result = post_tool.invoke({
        "url": "/comments",
        "data": {
            "postId": 1,
            "name": "张三",
            "email": "zhangsan@example.com",
            "body": "这篇文章写得很好！"
        }
    })
    print(result)


# ==================== 示例3: PUT请求工具 ====================

class PutRequestInput(BaseModel):
    """PUT请求输入模式"""
    url: str = Field(description="请求URL")
    data: Dict[str, Any] = Field(description="要更新的JSON数据")
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="请求头"
    )


class PutRequestTool(BaseTool):
    """PUT请求工具"""

    name: str = "put_request"
    description: str = """
    发送HTTP PUT请求更新数据。

    示例:
    - url: "https://api.example.com/users/1"
    - data: {"name": "李四", "email": "lisi@example.com"}
    """
    args_schema: Type[BaseModel] = PutRequestInput
    http_client: HTTPClient = None

    def __init__(self, http_client: Optional[HTTPClient] = None):
        super().__init__()
        self.http_client = http_client or HTTPClient()

    def _run(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行PUT请求"""
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        result = self.http_client.request(
            method="PUT",
            url=url,
            headers=headers,
            json_data=data
        )

        if result["success"]:
            output = f"✓ 请求成功 (状态码: {result['status_code']})\n"
            output += f"URL: {result['url']}\n\n"
            output += "响应数据:\n"
            output += json.dumps(result["data"], indent=2, ensure_ascii=False)
            return output
        else:
            return f"✗ 请求失败: {result['error']} ({result['error_type']})"


def demo_put_request():
    """示例3: PUT请求工具"""
    print_section("示例3: PUT请求工具")

    client = HTTPClient(base_url="https://jsonplaceholder.typicode.com")
    put_tool = PutRequestTool(http_client=client)

    # 更新帖子
    print("1. 更新帖子（ID=1）:")
    result = put_tool.invoke({
        "url": "/posts/1",
        "data": {
            "id": 1,
            "title": "更新后的标题",
            "body": "更新后的内容",
            "userId": 1
        }
    })
    print(result)


# ==================== 示例4: DELETE请求工具 ====================

class DeleteRequestInput(BaseModel):
    """DELETE请求输入模式"""
    url: str = Field(description="请求URL")
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="请求头"
    )


class DeleteRequestTool(BaseTool):
    """DELETE请求工具"""

    name: str = "delete_request"
    description: str = """
    发送HTTP DELETE请求删除数据。

    示例:
    - url: "https://api.example.com/users/1"
    - headers: {"Authorization": "Bearer token123"}

    警告: 删除操作通常不可恢复！
    """
    args_schema: Type[BaseModel] = DeleteRequestInput
    http_client: HTTPClient = None

    def __init__(self, http_client: Optional[HTTPClient] = None):
        super().__init__()
        self.http_client = http_client or HTTPClient()

    def _run(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行DELETE请求"""
        result = self.http_client.request(
            method="DELETE",
            url=url,
            headers=headers
        )

        if result["success"]:
            output = f"✓ 删除成功 (状态码: {result['status_code']})\n"
            output += f"URL: {result['url']}"
            return output
        else:
            return f"✗ 删除失败: {result['error']} ({result['error_type']})"


def demo_delete_request():
    """示例4: DELETE请求工具"""
    print_section("示例4: DELETE请求工具")

    client = HTTPClient(base_url="https://jsonplaceholder.typicode.com")
    delete_tool = DeleteRequestTool(http_client=client)

    # 删除帖子
    print("1. 删除帖子（ID=1）:")
    result = delete_tool.invoke({"url": "/posts/1"})
    print(result)


# ==================== 示例5: API认证工具 ====================

class APIKeyAuthClient(HTTPClient):
    """支持API Key认证的HTTP客户端"""

    def __init__(
        self,
        api_key: str,
        api_key_header: str = "X-API-Key",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.api_key_header = api_key_header

    def request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs):
        """添加API Key到请求头"""
        if headers is None:
            headers = {}
        headers[self.api_key_header] = self.api_key

        return super().request(method, url, headers=headers, **kwargs)


class BearerAuthClient(HTTPClient):
    """支持Bearer Token认证的HTTP客户端"""

    def __init__(self, token: str, **kwargs):
        super().__init__(**kwargs)
        self.token = token

    def request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs):
        """添加Bearer Token到请求头"""
        if headers is None:
            headers = {}
        headers["Authorization"] = f"Bearer {self.token}"

        return super().request(method, url, headers=headers, **kwargs)


def demo_api_authentication():
    """示例5: API认证"""
    print_section("示例5: API认证")

    print("1. API Key认证示例:")
    api_key_client = APIKeyAuthClient(
        api_key="your-api-key-here",
        base_url="https://api.example.com"
    )
    print(f"  API Key客户端已创建")
    print(f"  认证头: X-API-Key")

    print("\n2. Bearer Token认证示例:")
    bearer_client = BearerAuthClient(
        token="your-bearer-token-here",
        base_url="https://api.example.com"
    )
    print(f"  Bearer Token客户端已创建")
    print(f"  认证头: Authorization: Bearer <token>")

    print("\n3. 基本认证示例:")
    session = requests.Session()
    session.auth = ("username", "password")
    print(f"  基本认证已配置")


# ==================== 示例6: 错误处理和重试 ====================

def demo_error_handling():
    """示例6: 错误处理和重试"""
    print_section("示例6: 错误处理和重试")

    # 创建带重试的客户端
    client = HTTPClient(timeout=5, max_retries=3)
    get_tool = GetRequestTool(http_client=client)

    print("1. 测试有效URL:")
    result = get_tool.invoke({
        "url": "https://jsonplaceholder.typicode.com/users/1"
    })
    print(result[:200] + "..." if len(result) > 200 else result)

    print("\n2. 测试无效URL（404错误）:")
    result = get_tool.invoke({
        "url": "https://jsonplaceholder.typicode.com/invalid-endpoint"
    })
    print(result[:200] + "..." if len(result) > 200 else result)

    print("\n3. 测试超时（使用极短超时）:")
    timeout_client = HTTPClient(timeout=0.001, max_retries=1)
    timeout_tool = GetRequestTool(http_client=timeout_client)
    result = timeout_tool.invoke({
        "url": "https://jsonplaceholder.typicode.com/users"
    })
    print(result)


# ==================== 示例7: GitHub API集成示例 ====================

class GitHubAPITool(BaseTool):
    """GitHub API工具（不需要认证的公开API）"""

    name: str = "github_api"
    description: str = """
    查询GitHub公开仓库信息。

    支持的操作:
    - 获取仓库信息
    - 获取用户信息
    - 搜索仓库
    """

    class InputSchema(BaseModel):
        action: str = Field(description="操作类型: repo_info, user_info, search_repos")
        query: str = Field(description="查询参数（仓库名/用户名/搜索词）")

    args_schema: Type[BaseModel] = InputSchema
    http_client: HTTPClient = None

    def __init__(self):
        super().__init__()
        self.http_client = HTTPClient(base_url="https://api.github.com")

    def _run(
        self,
        action: str,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行GitHub API查询"""
        try:
            if action == "repo_info":
                # 获取仓库信息（格式: owner/repo）
                result = self.http_client.request("GET", f"/repos/{query}")

                if result["success"]:
                    data = result["data"]
                    output = f"仓库: {data.get('full_name', 'N/A')}\n"
                    output += f"描述: {data.get('description', 'N/A')}\n"
                    output += f"星标: {data.get('stargazers_count', 0)}\n"
                    output += f"Fork: {data.get('forks_count', 0)}\n"
                    output += f"语言: {data.get('language', 'N/A')}\n"
                    output += f"URL: {data.get('html_url', 'N/A')}"
                    return output
                else:
                    return f"错误: {result['error']}"

            elif action == "user_info":
                # 获取用户信息
                result = self.http_client.request("GET", f"/users/{query}")

                if result["success"]:
                    data = result["data"]
                    output = f"用户: {data.get('login', 'N/A')}\n"
                    output += f"姓名: {data.get('name', 'N/A')}\n"
                    output += f"公开仓库: {data.get('public_repos', 0)}\n"
                    output += f"粉丝: {data.get('followers', 0)}\n"
                    output += f"关注: {data.get('following', 0)}\n"
                    output += f"URL: {data.get('html_url', 'N/A')}"
                    return output
                else:
                    return f"错误: {result['error']}"

            elif action == "search_repos":
                # 搜索仓库
                result = self.http_client.request(
                    "GET",
                    "/search/repositories",
                    params={"q": query, "per_page": 5}
                )

                if result["success"]:
                    data = result["data"]
                    total = data.get("total_count", 0)
                    output = f"找到 {total} 个仓库，显示前5个:\n\n"

                    for i, repo in enumerate(data.get("items", [])[:5], 1):
                        output += f"{i}. {repo['full_name']}\n"
                        output += f"   ⭐ {repo['stargazers_count']} | "
                        output += f"语言: {repo.get('language', 'N/A')}\n"
                        output += f"   {repo['html_url']}\n\n"

                    return output
                else:
                    return f"错误: {result['error']}"

            else:
                return f"不支持的操作: {action}"

        except Exception as e:
            return f"错误: {str(e)}"


def demo_github_api():
    """示例7: GitHub API集成"""
    print_section("示例7: GitHub API集成")

    github_tool = GitHubAPITool()

    # 获取仓库信息
    print("1. 获取仓库信息（langchain-ai/langchain）:")
    result = github_tool.invoke({
        "action": "repo_info",
        "query": "langchain-ai/langchain"
    })
    print(result)

    # 获取用户信息
    print("\n2. 获取用户信息（octocat）:")
    result = github_tool.invoke({
        "action": "user_info",
        "query": "octocat"
    })
    print(result)

    # 搜索仓库
    print("\n3. 搜索仓库（langchain）:")
    result = github_tool.invoke({
        "action": "search_repos",
        "query": "langchain"
    })
    print(result)


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 05: API调用工具")
    print("="*70)

    try:
        # 示例1: GET请求
        demo_get_request()

        # 示例2: POST请求
        demo_post_request()

        # 示例3: PUT请求
        demo_put_request()

        # 示例4: DELETE请求
        demo_delete_request()

        # 示例5: API认证
        demo_api_authentication()

        # 示例6: 错误处理
        demo_error_handling()

        # 示例7: GitHub API
        demo_github_api()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
