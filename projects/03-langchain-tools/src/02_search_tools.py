"""
LangChain 工具使用 - 02: 搜索工具

本模块演示：
1. DuckDuckGo搜索工具
2. 维基百科搜索工具
3. 自定义网页搜索
4. 搜索结果处理
5. 搜索过滤和排序
6. 多搜索源聚合
7. 搜索结果缓存
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain.tools import Tool, tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, WikipediaAPIWrapper
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: DuckDuckGo搜索 ====================

def demo_duckduckgo_search():
    """示例1: DuckDuckGo搜索工具"""
    print_section("示例1: DuckDuckGo搜索工具")

    try:
        # 创建搜索包装器
        search = DuckDuckGoSearchAPIWrapper()

        # 创建搜索工具
        search_tool = DuckDuckGoSearchRun(api_wrapper=search)

        print("工具信息:")
        print(f"名称: {search_tool.name}")
        print(f"描述: {search_tool.description}\n")

        # 执行搜索
        queries = [
            "Python编程语言",
            "LangChain框架",
            "人工智能最新进展"
        ]

        for query in queries:
            print(f"搜索: {query}")
            try:
                result = search_tool.invoke(query)
                # 截取前200字符
                print(f"结果: {result[:200]}...\n")
            except Exception as e:
                print(f"搜索失败: {str(e)}\n")

    except ImportError:
        print("⚠️  需要安装: pip install duckduckgo-search")
    except Exception as e:
        print(f"错误: {str(e)}")


# ==================== 示例2: 维基百科搜索 ====================

def demo_wikipedia_search():
    """示例2: 维基百科搜索工具"""
    print_section("示例2: 维基百科搜索工具")

    try:
        # 创建维基百科包装器
        wikipedia = WikipediaAPIWrapper()

        # 创建搜索工具
        wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)

        print("工具信息:")
        print(f"名称: {wiki_tool.name}")
        print(f"描述: {wiki_tool.description}\n")

        # 执行搜索
        queries = [
            "Python (programming language)",
            "Artificial Intelligence",
            "Machine Learning"
        ]

        for query in queries:
            print(f"搜索: {query}")
            try:
                result = wiki_tool.invoke(query)
                # 截取前300字符
                print(f"摘要: {result[:300]}...\n")
            except Exception as e:
                print(f"搜索失败: {str(e)}\n")

    except ImportError:
        print("⚠️  需要安装: pip install wikipedia")
    except Exception as e:
        print(f"错误: {str(e)}")


# ==================== 示例3: 自定义网页搜索工具 ====================

class WebSearchResult(BaseModel):
    """搜索结果模型"""
    title: str = Field(description="标题")
    url: str = Field(description="链接")
    snippet: str = Field(description="摘要")
    source: str = Field(description="来源")


class CustomWebSearchTool:
    """自定义网页搜索工具（模拟）"""

    def __init__(self):
        """初始化搜索工具"""
        # 模拟搜索数据库
        self.mock_database = {
            "python": [
                {
                    "title": "Python官方网站",
                    "url": "https://www.python.org",
                    "snippet": "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言",
                    "source": "official"
                },
                {
                    "title": "Python教程 - 菜鸟教程",
                    "url": "https://www.runoob.com/python",
                    "snippet": "Python是一种易于学习又功能强大的编程语言",
                    "source": "tutorial"
                }
            ],
            "langchain": [
                {
                    "title": "LangChain官方文档",
                    "url": "https://python.langchain.com",
                    "snippet": "LangChain是一个用于开发由语言模型驱动的应用程序的框架",
                    "source": "official"
                },
                {
                    "title": "LangChain快速入门",
                    "url": "https://example.com/langchain-tutorial",
                    "snippet": "学习如何使用LangChain构建AI应用",
                    "source": "tutorial"
                }
            ],
            "ai": [
                {
                    "title": "人工智能简介",
                    "url": "https://example.com/ai-intro",
                    "snippet": "人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新技术科学",
                    "source": "education"
                }
            ]
        }

    def search(self, query: str, max_results: int = 5) -> List[WebSearchResult]:
        """
        执行搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        query_lower = query.lower()

        # 在模拟数据库中搜索
        results = []
        for keyword, items in self.mock_database.items():
            if keyword in query_lower:
                for item in items[:max_results]:
                    results.append(WebSearchResult(**item))

        return results[:max_results]

    def search_and_format(self, query: str) -> str:
        """搜索并格式化结果"""
        results = self.search(query)

        if not results:
            return f"未找到关于 '{query}' 的结果"

        formatted = f"找到 {len(results)} 条关于 '{query}' 的结果:\n\n"

        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.title}\n"
            formatted += f"   URL: {result.url}\n"
            formatted += f"   摘要: {result.snippet}\n"
            formatted += f"   来源: {result.source}\n\n"

        return formatted


def demo_custom_search():
    """示例3: 自定义网页搜索工具"""
    print_section("示例3: 自定义网页搜索工具")

    # 创建自定义搜索工具
    search_engine = CustomWebSearchTool()

    # 包装为LangChain工具
    @tool
    def web_search(query: str) -> str:
        """
        搜索网页内容。

        Args:
            query: 搜索查询

        Returns:
            格式化的搜索结果
        """
        return search_engine.search_and_format(query)

    print("工具信息:")
    print(f"名称: {web_search.name}")
    print(f"描述: {web_search.description}\n")

    # 执行搜索
    queries = ["Python", "LangChain", "AI"]

    for query in queries:
        print(f"{'='*60}")
        result = web_search.invoke({"query": query})
        print(result)


# ==================== 示例4: 搜索结果处理器 ====================

class SearchResultProcessor:
    """搜索结果处理器"""

    @staticmethod
    def filter_by_source(
        results: List[WebSearchResult],
        allowed_sources: List[str]
    ) -> List[WebSearchResult]:
        """按来源过滤结果"""
        return [
            r for r in results
            if r.source in allowed_sources
        ]

    @staticmethod
    def sort_by_relevance(
        results: List[WebSearchResult],
        query: str
    ) -> List[WebSearchResult]:
        """按相关性排序（简单实现）"""
        query_lower = query.lower()

        def relevance_score(result: WebSearchResult) -> int:
            score = 0
            if query_lower in result.title.lower():
                score += 3
            if query_lower in result.snippet.lower():
                score += 2
            if query_lower in result.url.lower():
                score += 1
            return score

        return sorted(results, key=relevance_score, reverse=True)

    @staticmethod
    def deduplicate(
        results: List[WebSearchResult]
    ) -> List[WebSearchResult]:
        """去重"""
        seen_urls = set()
        unique_results = []

        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)

        return unique_results


def demo_result_processing():
    """示例4: 搜索结果处理"""
    print_section("示例4: 搜索结果处理")

    search_engine = CustomWebSearchTool()
    processor = SearchResultProcessor()

    # 获取搜索结果
    results = search_engine.search("python", max_results=10)

    print(f"原始结果: {len(results)} 条\n")

    # 按来源过滤
    filtered = processor.filter_by_source(results, ["official", "tutorial"])
    print(f"过滤后（仅official和tutorial）: {len(filtered)} 条")
    for r in filtered:
        print(f"  - {r.title} ({r.source})")

    # 按相关性排序
    print("\n按相关性排序:")
    sorted_results = processor.sort_by_relevance(results, "python")
    for r in sorted_results:
        print(f"  - {r.title}")


# ==================== 示例5: 搜索结果缓存 ====================

class SearchCache:
    """搜索结果缓存"""

    def __init__(self, ttl_seconds: int = 3600):
        """
        初始化缓存

        Args:
            ttl_seconds: 缓存过期时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, query: str) -> Optional[str]:
        """获取缓存的搜索结果"""
        if query in self.cache:
            entry = self.cache[query]
            if datetime.now() < entry["expires_at"]:
                print(f"  [缓存命中] {query}")
                return entry["result"]
            else:
                # 过期，删除
                del self.cache[query]

        return None

    def set(self, query: str, result: str):
        """设置缓存"""
        self.cache[query] = {
            "result": result,
            "cached_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.ttl_seconds)
        }

    def clear(self):
        """清除所有缓存"""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        now = datetime.now()
        valid_entries = sum(
            1 for entry in self.cache.values()
            if now < entry["expires_at"]
        )

        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries
        }


def demo_search_cache():
    """示例5: 搜索结果缓存"""
    print_section("示例5: 搜索结果缓存")

    search_engine = CustomWebSearchTool()
    cache = SearchCache(ttl_seconds=60)  # 60秒过期

    def cached_search(query: str) -> str:
        """带缓存的搜索"""
        # 尝试从缓存获取
        cached_result = cache.get(query)
        if cached_result:
            return cached_result

        # 执行搜索
        print(f"  [执行搜索] {query}")
        result = search_engine.search_and_format(query)

        # 存入缓存
        cache.set(query, result)

        return result

    # 创建工具
    @tool
    def cached_web_search(query: str) -> str:
        """带缓存的网页搜索工具"""
        return cached_search(query)

    # 测试缓存
    print("第一次搜索 'Python':")
    result1 = cached_search("Python")
    print(f"结果长度: {len(result1)} 字符\n")

    print("第二次搜索 'Python' (应该命中缓存):")
    result2 = cached_search("Python")
    print(f"结果长度: {len(result2)} 字符\n")

    print("搜索 'LangChain':")
    result3 = cached_search("LangChain")
    print(f"结果长度: {len(result3)} 字符\n")

    # 显示缓存统计
    stats = cache.get_stats()
    print(f"缓存统计: {stats}")


# ==================== 示例6: 多搜索源聚合 ====================

class AggregatedSearchTool:
    """聚合多个搜索源的工具"""

    def __init__(self):
        """初始化聚合搜索工具"""
        self.sources = {
            "custom": CustomWebSearchTool(),
        }
        self.cache = SearchCache()

    def search_all(self, query: str, max_per_source: int = 3) -> Dict[str, Any]:
        """
        在所有搜索源中搜索

        Args:
            query: 搜索查询
            max_per_source: 每个源的最大结果数

        Returns:
            聚合的搜索结果
        """
        results = {
            "query": query,
            "sources": {},
            "total_results": 0
        }

        # 自定义搜索
        custom_results = self.sources["custom"].search(query, max_per_source)
        results["sources"]["custom"] = [r.dict() for r in custom_results]
        results["total_results"] += len(custom_results)

        return results

    def format_aggregated_results(self, results: Dict[str, Any]) -> str:
        """格式化聚合结果"""
        output = f"聚合搜索结果: '{results['query']}'\n"
        output += f"总计: {results['total_results']} 条结果\n\n"

        for source_name, source_results in results["sources"].items():
            output += f"--- {source_name.upper()} ({len(source_results)} 条) ---\n"
            for i, result in enumerate(source_results, 1):
                output += f"{i}. {result['title']}\n"
                output += f"   {result['snippet'][:80]}...\n"

            output += "\n"

        return output


def demo_aggregated_search():
    """示例6: 多搜索源聚合"""
    print_section("示例6: 多搜索源聚合")

    aggregator = AggregatedSearchTool()

    queries = ["Python", "LangChain"]

    for query in queries:
        print(f"聚合搜索: {query}")
        print("="*60)

        results = aggregator.search_all(query, max_per_source=2)
        formatted = aggregator.format_aggregated_results(results)

        print(formatted)


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 02: 搜索工具")
    print("="*70)

    try:
        # 示例1: DuckDuckGo搜索
        demo_duckduckgo_search()

        # 示例2: 维基百科搜索
        demo_wikipedia_search()

        # 示例3: 自定义搜索
        demo_custom_search()

        # 示例4: 结果处理
        demo_result_processing()

        # 示例5: 搜索缓存
        demo_search_cache()

        # 示例6: 聚合搜索
        demo_aggregated_search()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
