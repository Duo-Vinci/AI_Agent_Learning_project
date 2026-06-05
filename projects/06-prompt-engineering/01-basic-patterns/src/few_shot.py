"""
Few-shot（少样本）模式实现

少样本学习通过提供几个示例来引导模型学习任务模式。
适用于需要特定格式输出或风格模仿的任务。
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class FewShotPattern:
    """少样本模式类"""

    def __init__(self, provider: str = "openai"):
        """
        初始化少样本模式

        Args:
            provider: LLM提供商，支持 'openai' 或 'deepseek'
        """
        self.provider = provider

        if not config.validate():
            raise ValueError(f"配置验证失败，请检查 {provider} 的API配置")

        self.client = OpenAI(
            api_key=config.get_api_key(provider),
            base_url=config.get_base_url(provider)
        )
        self.model = config.get_model(provider)

    def learn_from_examples(
        self,
        task_description: str,
        examples: List[Dict[str, str]],
        input_data: str,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        基于示例学习并处理新输入

        Args:
            task_description: 任务描述
            examples: 示例列表，每个示例包含 'input' 和 'output' 键
            input_data: 待处理的新输入
            temperature: 温度参数

        Returns:
            处理结果字典
        """
        # 构建示例部分
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"""
示例{i}：
输入：{example['input']}
输出：{example['output']}
"""

        # 构建完整prompt
        prompt = f"""{task_description}

以下是一些示例：
{examples_text}

现在请处理以下输入，输出格式与示例保持一致：
输入：{input_data}
输出："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=500
            )

            result = response.choices[0].message.content.strip()

            return {
                "input": input_data,
                "output": result,
                "num_examples": len(examples),
                "success": True
            }
        except Exception as e:
            return {
                "input": input_data,
                "error": str(e),
                "success": False
            }

    def sentiment_classification(self, text: str) -> Dict[str, Any]:
        """
        情感分类（带示例）

        Args:
            text: 待分类的文本

        Returns:
            分类结果字典
        """
        examples = [
            {
                "input": "这个产品质量很好，物流也很快！",
                "output": "积极 | 置信度：0.95 | 关键词：质量好、物流快"
            },
            {
                "input": "服务态度差，东西还贵。",
                "output": "消极 | 置信度：0.92 | 关键词：态度差、贵"
            },
            {
                "input": "还行吧，没什么特别的。",
                "output": "中性 | 置信度：0.88 | 关键词：还行、没特别"
            }
        ]

        return self.learn_from_examples(
            task_description="请分析以下评论的情感倾向，并提取关键词。",
            examples=examples,
            input_data=text,
            temperature=0.2
        )

    def code_comment_generator(self, code: str) -> Dict[str, Any]:
        """
        代码注释生成器（带示例）

        Args:
            code: 待添加注释的代码

        Returns:
            包含注释的代码字典
        """
        examples = [
            {
                "input": "def add(a, b):\n    return a + b",
                "output": """def add(a, b):
    \"\"\"
    计算两个数的和

    Args:
        a: 第一个加数
        b: 第二个加数

    Returns:
        两数之和
    \"\"\"
    return a + b"""
            },
            {
                "input": "def find_max(nums):\n    return max(nums)",
                "output": """def find_max(nums):
    \"\"\"
    找出列表中的最大值

    Args:
        nums: 数字列表

    Returns:
        列表中的最大值
    \"\"\"
    return max(nums)"""
            }
        ]

        return self.learn_from_examples(
            task_description="请为以下Python函数添加规范的文档字符串注释。",
            examples=examples,
            input_data=code,
            temperature=0.3
        )

    def entity_extraction(self, text: str) -> Dict[str, Any]:
        """
        实体提取（带示例）

        Args:
            text: 待提取实体的文本

        Returns:
            提取结果字典
        """
        examples = [
            {
                "input": "小明在北京大学学习计算机科学，他的导师是李教授。",
                "output": "人名：小明、李教授 | 地名：北京 | 机构：北京大学 | 专业：计算机科学"
            },
            {
                "input": "苹果公司在美国加州库比蒂诺发布了新款iPhone。",
                "output": "公司：苹果公司 | 地名：美国、加州、库比蒂诺 | 产品：iPhone"
            },
            {
                "input": "张三昨天去了上海迪士尼乐园游玩。",
                "output": "人名：张三 | 地名：上海 | 机构：迪士尼乐园 | 时间：昨天"
            }
        ]

        return self.learn_from_examples(
            task_description="请从文本中提取命名实体（人名、地名、机构、产品等）。",
            examples=examples,
            input_data=text,
            temperature=0.2
        )

    def text_style_transfer(self, text: str, target_style: str) -> Dict[str, Any]:
        """
        文本风格转换（带示例）

        Args:
            text: 原文本
            target_style: 目标风格

        Returns:
            转换结果字典
        """
        # 根据目标风格选择示例
        style_examples = {
            "正式": [
                {
                    "input": "这东西真不错，我很喜欢！",
                    "output": "本产品质量优良，使用体验令人满意。"
                },
                {
                    "input": "老板人挺好的，服务也行。",
                    "output": "商家服务态度良好，整体表现令人认可。"
                }
            ],
            "幽默": [
                {
                    "input": "今天天气很热。",
                    "output": "今天的太阳好像把我当成了烤肉，热得我快成人干了！"
                },
                {
                    "input": "我很累。",
                    "output": "我现在累得像被卸了电池的机器人，随时准备原地关机。"
                }
            ],
            "简洁": [
                {
                    "input": "这个问题非常复杂，需要我们仔细思考和分析。",
                    "output": "问题复杂，需深思。"
                },
                {
                    "input": "经过长时间的讨论，我们终于达成了一致意见。",
                    "output": "讨论后达成共识。"
                }
            ]
        }

        examples = style_examples.get(target_style, style_examples["正式"])

        return self.learn_from_examples(
            task_description=f"请将以下文本转换为{target_style}风格。",
            examples=examples,
            input_data=text,
            temperature=0.5
        )

    def data_format_conversion(self, data: str, target_format: str) -> Dict[str, Any]:
        """
        数据格式转换（带示例）

        Args:
            data: 原始数据
            target_format: 目标格式（如JSON、XML、Markdown等）

        Returns:
            转换结果字典
        """
        examples = [
            {
                "input": "姓名：张三，年龄：28，职业：工程师",
                "output": '{"name": "张三", "age": 28, "occupation": "工程师"}'
            },
            {
                "input": "城市：北京，人口：2154万，面积：16410平方公里",
                "output": '{"city": "北京", "population": "2154万", "area": "16410平方公里"}'
            }
        ]

        return self.learn_from_examples(
            task_description=f"请将以下数据转换为{target_format}格式。",
            examples=examples,
            input_data=data,
            temperature=0.2
        )


def main():
    """示例用法"""
    print("=" * 50)
    print("少样本模式（Few-Shot Pattern）示例")
    print("=" * 50)

    try:
        pattern = FewShotPattern(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：情感分类
    print("\n" + "=" * 50)
    print("示例1: 情感分类（带示例学习）")
    print("=" * 50)

    result1 = pattern.sentiment_classification(
        text="包装精美，但价格有点高。"
    )

    if result1["success"]:
        print(f"输入: {result1['input']}")
        print(f"输出: {result1['output']}")
        print(f"使用示例数: {result1['num_examples']}")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：代码注释生成
    print("\n" + "=" * 50)
    print("示例2: 代码注释生成")
    print("=" * 50)

    code = """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)"""

    result2 = pattern.code_comment_generator(code)

    if result2["success"]:
        print(f"输入代码:\n{result2['input']}")
        print(f"\n带注释的代码:\n{result2['output']}")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：实体提取
    print("\n" + "=" * 50)
    print("示例3: 实体提取")
    print("=" * 50)

    result3 = pattern.entity_extraction(
        text="王芳在清华大学攻读人工智能专业，她的导师是陈教授。"
    )

    if result3["success"]:
        print(f"输入: {result3['input']}")
        print(f"输出: {result3['output']}")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：风格转换
    print("\n" + "=" * 50)
    print("示例4: 文本风格转换")
    print("=" * 50)

    result4 = pattern.text_style_transfer(
        text="这个方案挺好的，我觉得可以试试。",
        target_style="正式"
    )

    if result4["success"]:
        print(f"原文: {result4['input']}")
        print(f"转换后: {result4['output']}")
    else:
        print(f"错误: {result4['error']}")

    # 示例5：自定义示例学习
    print("\n" + "=" * 50)
    print("示例5: 自定义示例学习（问题分类）")
    print("=" * 50)

    custom_examples = [
        {
            "input": "我的订单什么时候能到？",
            "output": "物流查询 | 紧急度：中"
        },
        {
            "input": "我要退款！这个东西完全不能用！",
            "output": "退款申请 | 紧急度：高"
        },
        {
            "input": "你们有哪些支付方式？",
            "output": "咨询问题 | 紧急度：低"
        }
    ]

    result5 = pattern.learn_from_examples(
        task_description="请对客户问题进行分类，并评估紧急度。",
        examples=custom_examples,
        input_data="产品有质量问题，需要换货。"
    )

    if result5["success"]:
        print(f"输入: {result5['input']}")
        print(f"输出: {result5['output']}")
    else:
        print(f"错误: {result5['error']}")

    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
