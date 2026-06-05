"""
并行协作Agent定义
实现多个Agent同时分析同一任务的不同方面
"""

import asyncio
from typing import Optional, Dict, List
from langchain_openai import ChatOpenAI


class SentimentAnalysisAgent:
    """情感分析Agent"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化情感分析Agent"""
        self.llm = llm or ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.name = "情感分析专家"

    async def analyze(self, text: str) -> str:
        """
        分析文本的情感倾向

        Args:
            text: 待分析文本

        Returns:
            情感分析结果
        """
        prompt = f"""你是一位专业的情感分析专家。请分析以下文本的情感倾向：

文本：
{text}

请提供：
1. 整体情感倾向（积极/中性/消极）
2. 情感强度（1-10分）
3. 主要情感类型（喜悦、愤怒、悲伤、恐惧等）
4. 情感的具体表现

分析结果："""

        try:
            response = await self.llm.ainvoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 分析完成")
            return result
        except Exception as e:
            error_msg = f"分析出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class KeywordExtractionAgent:
    """关键词提取Agent"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化关键词提取Agent"""
        self.llm = llm or ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.name = "关键词提取专家"

    async def extract(self, text: str) -> str:
        """
        提取文本的关键词

        Args:
            text: 待分析文本

        Returns:
            关键词列表
        """
        prompt = f"""你是一位专业的关键词提取专家。请从以下文本中提取关键词：

文本：
{text}

请提供：
1. 核心关键词（5-10个）
2. 每个关键词的重要性评分（1-10）
3. 关键词之间的关系
4. 关键词所属的主题类别

提取结果："""

        try:
            response = await self.llm.ainvoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 提取完成")
            return result
        except Exception as e:
            error_msg = f"提取出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class SummaryAgent:
    """摘要生成Agent"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化摘要生成Agent"""
        self.llm = llm or ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
        self.name = "摘要生成专家"

    async def summarize(self, text: str) -> str:
        """
        生成文本摘要

        Args:
            text: 待摘要文本

        Returns:
            文本摘要
        """
        prompt = f"""你是一位专业的摘要生成专家。请为以下文本生成摘要：

文本：
{text}

请提供：
1. 一句话摘要（不超过30字）
2. 段落摘要（100-150字）
3. 核心观点（3-5个要点）
4. 主要论据

摘要："""

        try:
            response = await self.llm.ainvoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 摘要完成")
            return result
        except Exception as e:
            error_msg = f"摘要生成出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class EntityRecognitionAgent:
    """实体识别Agent"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化实体识别Agent"""
        self.llm = llm or ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")
        self.name = "实体识别专家"

    async def recognize(self, text: str) -> str:
        """
        识别文本中的实体

        Args:
            text: 待分析文本

        Returns:
            实体识别结果
        """
        prompt = f"""你是一位专业的实体识别专家。请识别以下文本中的实体：

文本：
{text}

请识别：
1. 人名（Person）
2. 地名（Location）
3. 机构名（Organization）
4. 时间（Time）
5. 专业术语（Term）

对每个实体，请说明：
- 实体类型
- 在文中的重要性
- 相关上下文

识别结果："""

        try:
            response = await self.llm.ainvoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 识别完成")
            return result
        except Exception as e:
            error_msg = f"识别出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class TopicAnalysisAgent:
    """主题分析Agent"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化主题分析Agent"""
        self.llm = llm or ChatOpenAI(temperature=0.4, model="gpt-3.5-turbo")
        self.name = "主题分析专家"

    async def analyze_topic(self, text: str) -> str:
        """
        分析文本的主题

        Args:
            text: 待分析文本

        Returns:
            主题分析结果
        """
        prompt = f"""你是一位专业的主题分析专家。请分析以下文本的主题：

文本：
{text}

请提供：
1. 主要主题（1-3个）
2. 次要主题
3. 主题之间的关系
4. 主题的深度分析

分析结果："""

        try:
            response = await self.llm.ainvoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 分析完成")
            return result
        except Exception as e:
            error_msg = f"分析出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class AggregatorAgent:
    """聚合Agent：整合多个Agent的分析结果"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化聚合Agent"""
        self.llm = llm or ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
        self.name = "聚合分析专家"

    def aggregate(self, results: Dict[str, str]) -> str:
        """
        聚合多个分析结果

        Args:
            results: 各Agent的分析结果字典

        Returns:
            综合分析报告
        """
        # 构建结果概览
        results_overview = "\n\n".join([
            f"【{key}】\n{value}" for key, value in results.items()
        ])

        prompt = f"""你是一位专业的综合分析专家。请整合以下多个专家的分析结果，生成一份结构化的综合报告：

{results_overview}

请生成综合分析报告，包含：
1. 执行摘要（200字以内）
2. 各维度分析要点整合
3. 发现的关键洞察
4. 各分析结果之间的关联
5. 综合结论和建议

综合报告："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 聚合完成")
            return result
        except Exception as e:
            error_msg = f"聚合出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg
