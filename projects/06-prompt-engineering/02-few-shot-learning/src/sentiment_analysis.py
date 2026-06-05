"""
Few-shot学习专项模块

深入探索少样本学习的各种应用场景和技巧。
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class FewShotLearning:
    """Few-shot学习高级应用类"""

    def __init__(self, provider: str = "openai"):
        """初始化"""
        self.provider = provider

        if not config.validate():
            raise ValueError(f"配置验证失败")

        self.client = OpenAI(
            api_key=config.get_api_key(provider),
            base_url=config.get_base_url(provider)
        )
        self.model = config.get_model(provider)

    def sentiment_analysis_advanced(self, text: str) -> Dict[str, Any]:
        """
        高级情感分析（细粒度情感分类）

        Args:
            text: 待分析文本

        Returns:
            详细的情感分析结果
        """
        examples = [
            {
                "input": "这款手机拍照效果惊艳，电池续航也很给力！",
                "output": """情感：非常积极
维度分析：
- 产品质量：非常满意（拍照效果惊艳）
- 性能表现：满意（电池续航给力）
- 整体评价：强烈推荐
情感强度：0.95
关键词：惊艳、给力"""
            },
            {
                "input": "用了一周，还可以吧，没什么特别的。",
                "output": """情感：轻微积极
维度分析：
- 产品质量：一般（没什么特别）
- 性能表现：达到预期
- 整体评价：可以接受
情感强度：0.55
关键词：还可以、一般"""
            },
            {
                "input": "质量太差了，用了两天就坏了，非常失望！",
                "output": """情感：非常消极
维度分析：
- 产品质量：非常不满（质量差、坏了）
- 性能表现：完全不符合预期
- 整体评价：强烈不推荐
情感强度：0.92
关键词：质量差、坏了、失望"""
            }
        ]

        prompt = self._build_few_shot_prompt(
            task_description="请对以下文本进行细粒度情感分析，包括情感倾向、维度分析、情感强度和关键词。",
            examples=examples,
            input_data=text
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )

            return {
                "text": text,
                "analysis": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"text": text, "error": str(e), "success": False}

    def intent_recognition(self, user_message: str) -> Dict[str, Any]:
        """
        用户意图识别

        Args:
            user_message: 用户消息

        Returns:
            意图识别结果
        """
        examples = [
            {
                "input": "我想查一下我的订单什么时候能到",
                "output": "意图类型：订单查询 | 紧急度：中 | 需要信息：订单号 | 建议操作：查询物流信息"
            },
            {
                "input": "这个产品质量有问题，我要退款！",
                "output": "意图类型：退款申请 | 紧急度：高 | 需要信息：订单号、问题描述 | 建议操作：启动退款流程"
            },
            {
                "input": "你们支持哪些支付方式？",
                "output": "意图类型：信息咨询 | 紧急度：低 | 需要信息：无 | 建议操作：提供支付方式列表"
            },
            {
                "input": "我要修改收货地址",
                "output": "意图类型：订单修改 | 紧急度：中 | 需要信息：订单号、新地址 | 建议操作：验证订单状态后修改"
            }
        ]

        prompt = self._build_few_shot_prompt(
            task_description="请识别用户消息的意图，包括意图类型、紧急度、需要的信息和建议操作。",
            examples=examples,
            input_data=user_message
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )

            return {
                "message": user_message,
                "intent": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"message": user_message, "error": str(e), "success": False}

    def text_classification_multilabel(self, text: str) -> Dict[str, Any]:
        """
        多标签文本分类

        Args:
            text: 待分类文本

        Returns:
            多标签分类结果
        """
        examples = [
            {
                "input": "这篇文章介绍了Python中的机器学习库scikit-learn的使用方法，包括数据预处理和模型训练。",
                "output": "标签：[编程, 机器学习, Python, 教程, 数据科学] | 主标签：机器学习 | 置信度：0.92"
            },
            {
                "input": "最新研究表明，深度学习在医疗影像诊断领域取得了重大突破，准确率达到95%以上。",
                "output": "标签：[人工智能, 深度学习, 医疗, 科研, 影像诊断] | 主标签：医疗 | 置信度：0.88"
            },
            {
                "input": "这个在线课程教你如何使用React和Node.js构建全栈Web应用，适合有一定编程基础的学习者。",
                "output": "标签：[Web开发, 前端, 后端, 教程, JavaScript] | 主标签：Web开发 | 置信度：0.90"
            }
        ]

        prompt = self._build_few_shot_prompt(
            task_description="请对以下文本进行多标签分类，识别所有相关标签，并指出主标签和置信度。",
            examples=examples,
            input_data=text
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )

            return {
                "text": text,
                "classification": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"text": text, "error": str(e), "success": False}

    def response_generation(self, user_query: str, context: str = "") -> Dict[str, Any]:
        """
        客服回复生成

        Args:
            user_query: 用户问题
            context: 上下文信息（可选）

        Returns:
            生成的回复
        """
        examples = [
            {
                "input": "用户：我的订单还没发货，怎么回事？\n上下文：订单状态-待发货，下单时间-2天前",
                "output": """尊敬的客户，您好！

经查询，您的订单目前处于待发货状态。由于您下单时间为2天前，目前在正常的发货周期内（通常为3-5个工作日）。

我们会尽快为您安排发货，预计今明两天内发出。发货后会第一时间为您推送物流信息。

如有其他问题，请随时联系我们。感谢您的耐心等待！"""
            },
            {
                "input": "用户：这个产品有什么优惠活动吗？\n上下文：产品-智能手表，价格-1999元，活动-满1500减200",
                "output": """您好！

这款智能手表目前正在参加优惠活动：
- 原价：1999元
- 活动：满1500减200
- 实付：1799元

此外，现在下单还可以享受：
✓ 免费包邮
✓ 赠送原装充电器

活动时间有限，建议您尽快下单哦！如需了解更多详情，请随时咨询。"""
            }
        ]

        input_text = f"用户：{user_query}"
        if context:
            input_text += f"\n上下文：{context}"

        prompt = self._build_few_shot_prompt(
            task_description="请根据用户问题和上下文信息，生成专业、友好的客服回复。",
            examples=examples,
            input_data=input_text
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=500
            )

            return {
                "query": user_query,
                "context": context,
                "response": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"query": user_query, "error": str(e), "success": False}

    def _build_few_shot_prompt(
        self,
        task_description: str,
        examples: List[Dict[str, str]],
        input_data: str
    ) -> str:
        """
        构建few-shot prompt

        Args:
            task_description: 任务描述
            examples: 示例列表
            input_data: 输入数据

        Returns:
            完整的prompt
        """
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"""
示例{i}：
输入：{example['input']}
输出：{example['output']}
"""

        prompt = f"""{task_description}

以下是一些示例：
{examples_text}

现在请处理以下输入，输出格式与示例保持一致：
输入：{input_data}
输出："""

        return prompt


def main():
    """示例用法"""
    print("=" * 60)
    print("Few-shot学习高级应用示例")
    print("=" * 60)

    try:
        learner = FewShotLearning(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：细粒度情感分析
    print("\n" + "=" * 60)
    print("示例1: 细粒度情感分析")
    print("=" * 60)

    result1 = learner.sentiment_analysis_advanced(
        text="包装很精致，但是价格确实有点贵，性价比一般。"
    )

    if result1["success"]:
        print(f"输入: {result1['text']}")
        print(f"\n分析结果:\n{result1['analysis']}")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：意图识别
    print("\n" + "=" * 60)
    print("示例2: 用户意图识别")
    print("=" * 60)

    result2 = learner.intent_recognition(
        user_message="我买的东西不满意，能换货吗？"
    )

    if result2["success"]:
        print(f"用户消息: {result2['message']}")
        print(f"识别结果: {result2['intent']}")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：多标签分类
    print("\n" + "=" * 60)
    print("示例3: 多标签文本分类")
    print("=" * 60)

    result3 = learner.text_classification_multilabel(
        text="本文详细介绍了如何使用Docker和Kubernetes部署微服务架构，包括容器化、服务编排和监控方案。"
    )

    if result3["success"]:
        print(f"输入: {result3['text']}")
        print(f"分类结果: {result3['classification']}")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：客服回复生成
    print("\n" + "=" * 60)
    print("示例4: 客服回复生成")
    print("=" * 60)

    result4 = learner.response_generation(
        user_query="我想退货，但是已经拆封了，可以退吗？",
        context="产品类型-电子产品，购买时间-5天前，7天无理由退货政策"
    )

    if result4["success"]:
        print(f"用户问题: {result4['query']}")
        print(f"上下文: {result4['context']}")
        print(f"\n生成的回复:\n{result4['response']}")
    else:
        print(f"错误: {result4['error']}")

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
