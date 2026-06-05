"""
Zero-shot（零样本）模式实现

零样本学习是指不提供任何示例，直接给出指令让模型完成任务。
适用于简单、常见的任务，如文本分类、摘要生成等。
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class ZeroShotPattern:
    """零样本模式类"""

    def __init__(self, provider: str = "openai"):
        """
        初始化零样本模式

        Args:
            provider: LLM提供商，支持 'openai' 或 'deepseek'
        """
        self.provider = provider

        # 验证配置
        if not config.validate():
            raise ValueError(f"配置验证失败，请检查 {provider} 的API配置")

        # 初始化OpenAI客户端（兼容DeepSeek）
        self.client = OpenAI(
            api_key=config.get_api_key(provider),
            base_url=config.get_base_url(provider)
        )
        self.model = config.get_model(provider)

    def text_classification(self, text: str, categories: list[str]) -> Dict[str, Any]:
        """
        文本分类任务

        Args:
            text: 待分类的文本
            categories: 分类类别列表

        Returns:
            包含分类结果的字典
        """
        categories_str = "、".join(categories)

        prompt = f"""你是一个专业的文本分类器。
请将以下文本分类到这些类别中的一个：{categories_str}

文本：{text}

请直接输出分类结果（只输出类别名称）："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50
            )

            result = response.choices[0].message.content.strip()

            return {
                "text": text,
                "category": result,
                "categories": categories,
                "success": True
            }
        except Exception as e:
            return {
                "text": text,
                "error": str(e),
                "success": False
            }

    def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        情感分析任务

        Args:
            text: 待分析的文本

        Returns:
            包含情感分析结果的字典
        """
        prompt = f"""你是一个情感分析专家。
请分析以下文本的情感倾向，并给出置信度。

文本：{text}

请按以下格式输出：
情感：[正面/负面/中性]
置信度：[0.0-1.0之间的数字]
原因：[简要说明判断理由]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )

            result = response.choices[0].message.content.strip()

            return {
                "text": text,
                "analysis": result,
                "success": True
            }
        except Exception as e:
            return {
                "text": text,
                "error": str(e),
                "success": False
            }

    def text_summarization(self, text: str, max_length: int = 100) -> Dict[str, Any]:
        """
        文本摘要任务

        Args:
            text: 待摘要的文本
            max_length: 摘要最大字数

        Returns:
            包含摘要结果的字典
        """
        prompt = f"""你是一个专业的文本摘要生成器。
请为以下文本生成简洁的摘要。

要求：
- 不超过{max_length}字
- 保留核心信息
- 语言简洁流畅
- 不添加原文没有的内容

文本：
{text}

摘要："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=max_length * 2
            )

            summary = response.choices[0].message.content.strip()

            return {
                "original_text": text,
                "summary": summary,
                "max_length": max_length,
                "success": True
            }
        except Exception as e:
            return {
                "original_text": text,
                "error": str(e),
                "success": False
            }

    def question_answering(self, context: str, question: str) -> Dict[str, Any]:
        """
        问答任务

        Args:
            context: 上下文信息
            question: 问题

        Returns:
            包含答案的字典
        """
        prompt = f"""根据以下上下文回答问题。

上下文：
{context}

问题：{question}

答案："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )

            answer = response.choices[0].message.content.strip()

            return {
                "context": context,
                "question": question,
                "answer": answer,
                "success": True
            }
        except Exception as e:
            return {
                "context": context,
                "question": question,
                "error": str(e),
                "success": False
            }

    def translation(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        翻译任务

        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            包含翻译结果的字典
        """
        prompt = f"""你是一个专业的翻译专家。
请将以下{source_lang}文本翻译成{target_lang}。

要求：
- 准确传达原文含义
- 符合目标语言习惯
- 保持原文风格和语气

{source_lang}文本：
{text}

{target_lang}翻译："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=len(text) * 3
            )

            translation = response.choices[0].message.content.strip()

            return {
                "original_text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "translation": translation,
                "success": True
            }
        except Exception as e:
            return {
                "original_text": text,
                "error": str(e),
                "success": False
            }


def main():
    """示例用法"""
    print("=" * 50)
    print("零样本模式（Zero-Shot Pattern）示例")
    print("=" * 50)

    # 初始化（可以选择使用DeepSeek或OpenAI）
    try:
        pattern = ZeroShotPattern(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：文本分类
    print("\n" + "=" * 50)
    print("示例1: 文本分类")
    print("=" * 50)

    result1 = pattern.text_classification(
        text="这款手机拍照效果很好，电池续航也不错，值得购买！",
        categories=["正面评价", "负面评价", "中性评价"]
    )

    if result1["success"]:
        print(f"文本: {result1['text']}")
        print(f"分类结果: {result1['category']}")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：情感分析
    print("\n" + "=" * 50)
    print("示例2: 情感分析")
    print("=" * 50)

    result2 = pattern.sentiment_analysis(
        text="今天天气真好，心情也很愉快！"
    )

    if result2["success"]:
        print(f"文本: {result2['text']}")
        print(f"分析结果:\n{result2['analysis']}")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：文本摘要
    print("\n" + "=" * 50)
    print("示例3: 文本摘要")
    print("=" * 50)

    long_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
    它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
    可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
    """

    result3 = pattern.text_summarization(text=long_text, max_length=50)

    if result3["success"]:
        print(f"原文: {result3['original_text'][:100]}...")
        print(f"摘要: {result3['summary']}")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：翻译
    print("\n" + "=" * 50)
    print("示例4: 翻译")
    print("=" * 50)

    result4 = pattern.translation(
        text="机器学习是人工智能的一个重要分支。",
        source_lang="中文",
        target_lang="英文"
    )

    if result4["success"]:
        print(f"原文({result4['source_lang']}): {result4['original_text']}")
        print(f"译文({result4['target_lang']}): {result4['translation']}")
    else:
        print(f"错误: {result4['error']}")

    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
