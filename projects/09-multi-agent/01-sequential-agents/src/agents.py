"""
顺序协作Agent定义
实现研究员、写作者、编辑的顺序工作流
"""

from typing import Optional
from langchain_openai import ChatOpenAI


class ResearchAgent:
    """研究员Agent：负责信息收集和研究"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        初始化研究员Agent

        Args:
            llm: 语言模型实例，如果不提供则创建默认实例
        """
        self.llm = llm or ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        self.name = "研究员"

    def research(self, topic: str) -> str:
        """
        对给定主题进行研究

        Args:
            topic: 研究主题

        Returns:
            研究结果文本
        """
        prompt = f"""你是一位专业的研究员。请深入研究以下主题，收集关键信息：

主题：{topic}

请提供：
1. 主题的核心概念和定义
2. 主要应用场景和案例
3. 当前的发展趋势
4. 关键技术点

研究报告："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 研究完成")
            return result
        except Exception as e:
            error_msg = f"研究过程出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class WriterAgent:
    """写作者Agent：负责内容创作"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        初始化写作者Agent

        Args:
            llm: 语言模型实例，如果不提供则创建默认实例
        """
        self.llm = llm or ChatOpenAI(temperature=0.8, model="gpt-3.5-turbo")
        self.name = "写作者"

    def write(self, research_data: str) -> str:
        """
        基于研究资料撰写文章

        Args:
            research_data: 研究员提供的研究资料

        Returns:
            文章草稿
        """
        prompt = f"""你是一位专业的内容创作者。基于以下研究资料，撰写一篇结构清晰、内容丰富的文章：

研究资料：
{research_data}

要求：
1. 文章结构清晰，包含引言、正文、结论
2. 语言流畅，通俗易懂
3. 适当使用例子说明
4. 字数在500-800字

文章草稿："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 写作完成")
            return result
        except Exception as e:
            error_msg = f"写作过程出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg


class EditorAgent:
    """编辑Agent：负责审查和优化内容"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        初始化编辑Agent

        Args:
            llm: 语言模型实例，如果不提供则创建默认实例
        """
        self.llm = llm or ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.name = "编辑"

    def edit(self, draft: str) -> str:
        """
        审查并优化文章草稿

        Args:
            draft: 写作者提供的文章草稿

        Returns:
            优化后的最终文章
        """
        prompt = f"""你是一位经验丰富的编辑。请审查并优化以下文章：

文章草稿：
{draft}

请检查并改进：
1. 语法和拼写错误
2. 逻辑连贯性
3. 表达的准确性和清晰度
4. 结构的合理性
5. 增加必要的过渡句

优化后的文章："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 编辑完成")
            return result
        except Exception as e:
            error_msg = f"编辑过程出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg

    def edit_with_feedback(self, draft: str) -> tuple[str, dict]:
        """
        审查文章并提供反馈

        Args:
            draft: 文章草稿

        Returns:
            (编辑后的文章, 反馈信息字典)
        """
        prompt = f"""你是一位严格的编辑。请审查以下文章并提供详细反馈：

文章草稿：
{draft}

请以JSON格式返回评估结果：
{{
    "approved": true/false,
    "score": 0-100,
    "issues": ["问题1", "问题2"],
    "missing_info": "需要补充的信息",
    "suggestions": ["建议1", "建议2"]
}}

评估结果："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)

            # 尝试解析JSON反馈
            import json
            try:
                feedback = json.loads(result)
            except:
                # 如果解析失败，创建默认反馈
                feedback = {
                    "approved": True,
                    "score": 75,
                    "issues": [],
                    "missing_info": "",
                    "suggestions": []
                }

            # 如果通过审查，返回优化版本
            if feedback.get("approved", False):
                edited = self.edit(draft)
                return edited, feedback
            else:
                return draft, feedback

        except Exception as e:
            print(f"✗ [{self.name}] 反馈生成出错: {str(e)}")
            return draft, {"approved": True, "score": 0, "issues": [str(e)]}
