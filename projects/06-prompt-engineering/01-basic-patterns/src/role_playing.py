"""
角色扮演模式实现

通过让AI扮演特定角色来获得专业领域的回答。
适用于需要特定专业知识或风格的任务。
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class RolePlayingPattern:
    """角色扮演模式类"""

    def __init__(self, provider: str = "openai"):
        """
        初始化角色扮演模式

        Args:
            provider: LLM提供商
        """
        self.provider = provider

        if not config.validate():
            raise ValueError(f"配置验证失败，请检查 {provider} 的API配置")

        self.client = OpenAI(
            api_key=config.get_api_key(provider),
            base_url=config.get_base_url(provider)
        )
        self.model = config.get_model(provider)

    def create_role_prompt(
        self,
        role: str,
        expertise: str,
        characteristics: List[str],
        question: str
    ) -> str:
        """
        创建角色扮演prompt

        Args:
            role: 角色名称
            expertise: 专业领域
            characteristics: 角色特征列表
            question: 问题

        Returns:
            完整的prompt
        """
        characteristics_text = "\n".join(f"- {char}" for char in characteristics)

        prompt = f"""你是一位{role}，专精于{expertise}。

你的特点：
{characteristics_text}

请以{role}的身份回答以下问题：
{question}

你的回答："""

        return prompt

    def ask_expert(
        self,
        role: str,
        expertise: str,
        characteristics: List[str],
        question: str,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        向专家角色提问

        Args:
            role: 角色名称
            expertise: 专业领域
            characteristics: 角色特征列表
            question: 问题
            temperature: 温度参数

        Returns:
            回答结果字典
        """
        prompt = self.create_role_prompt(role, expertise, characteristics, question)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"你是一位{role}，擅长{expertise}。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()

            return {
                "role": role,
                "expertise": expertise,
                "question": question,
                "answer": answer,
                "success": True
            }
        except Exception as e:
            return {
                "role": role,
                "question": question,
                "error": str(e),
                "success": False
            }

    def python_tutor(self, question: str) -> Dict[str, Any]:
        """
        Python导师角色

        Args:
            question: 学生的问题

        Returns:
            回答结果
        """
        return self.ask_expert(
            role="资深Python导师",
            expertise="Python编程教学",
            characteristics=[
                "有10年以上的Python开发和教学经验",
                "善于用简单易懂的语言解释复杂概念",
                "喜欢用生动的比喻和实际例子",
                "注重培养学生的编程思维",
                "鼓励学生动手实践"
            ],
            question=question,
            temperature=0.7
        )

    def system_architect(self, question: str) -> Dict[str, Any]:
        """
        系统架构师角色

        Args:
            question: 架构问题

        Returns:
            回答结果
        """
        return self.ask_expert(
            role="资深系统架构师",
            expertise="大规模分布式系统设计",
            characteristics=[
                "有15年以上的系统架构经验",
                "精通微服务、高并发、高可用设计",
                "注重系统的可扩展性和可维护性",
                "善于权衡技术选型的利弊",
                "考虑问题全面，包括性能、成本、团队能力等"
            ],
            question=question,
            temperature=0.6
        )

    def code_reviewer(self, code: str) -> Dict[str, Any]:
        """
        代码审查专家角色

        Args:
            code: 待审查的代码

        Returns:
            审查结果
        """
        question = f"""请审查以下代码：

```python
{code}
```

请从以下维度提供审查意见：
1. 代码规范性
2. 性能问题
3. 安全隐患
4. 可维护性
5. 改进建议"""

        return self.ask_expert(
            role="资深代码审查专家",
            expertise="代码质量评估和优化",
            characteristics=[
                "注重代码规范和最佳实践",
                "善于发现潜在的bug和性能问题",
                "提供具体可行的改进建议",
                "考虑代码的可读性和可维护性"
            ],
            question=question,
            temperature=0.5
        )

    def product_manager(self, requirement: str) -> Dict[str, Any]:
        """
        产品经理角色

        Args:
            requirement: 产品需求

        Returns:
            分析结果
        """
        question = f"""请分析以下产品需求：

{requirement}

请提供：
1. 需求分析（核心价值、目标用户）
2. 功能设计建议
3. 优先级排序
4. 潜在风险和挑战
5. 成功指标建议"""

        return self.ask_expert(
            role="资深产品经理",
            expertise="互联网产品设计和规划",
            characteristics=[
                "有丰富的产品设计和管理经验",
                "善于从用户角度思考问题",
                "注重数据驱动决策",
                "平衡用户需求和技术实现",
                "考虑商业价值和用户体验"
            ],
            question=question,
            temperature=0.7
        )

    def data_scientist(self, question: str) -> Dict[str, Any]:
        """
        数据科学家角色

        Args:
            question: 数据分析问题

        Returns:
            回答结果
        """
        return self.ask_expert(
            role="资深数据科学家",
            expertise="数据分析和机器学习",
            characteristics=[
                "精通统计学和机器学习算法",
                "擅长数据可视化和洞察提取",
                "注重数据质量和特征工程",
                "善于选择合适的模型和评估方法",
                "考虑模型的可解释性和业务价值"
            ],
            question=question,
            temperature=0.6
        )

    def security_expert(self, question: str) -> Dict[str, Any]:
        """
        安全专家角色

        Args:
            question: 安全问题

        Returns:
            回答结果
        """
        return self.ask_expert(
            role="网络安全专家",
            expertise="应用安全和渗透测试",
            characteristics=[
                "深入了解常见安全漏洞和攻击手段",
                "熟悉OWASP Top 10和安全最佳实践",
                "善于发现系统的安全隐患",
                "提供实用的安全加固建议",
                "注重安全与可用性的平衡"
            ],
            question=question,
            temperature=0.5
        )

    def creative_writer(self, topic: str, style: str = "生动有趣") -> Dict[str, Any]:
        """
        创意写作者角色

        Args:
            topic: 写作主题
            style: 写作风格

        Returns:
            创作结果
        """
        question = f"请以{style}的风格创作一篇关于'{topic}'的短文（300字左右）。"

        return self.ask_expert(
            role="创意写作专家",
            expertise="文学创作和故事讲述",
            characteristics=[
                "文笔优美，富有感染力",
                "善于运用修辞手法",
                "擅长营造氛围和情感",
                "注重故事的节奏和结构",
                "能够适应不同的写作风格"
            ],
            question=question,
            temperature=0.8
        )


def main():
    """示例用法"""
    print("=" * 50)
    print("角色扮演模式（Role-Playing Pattern）示例")
    print("=" * 50)

    try:
        pattern = RolePlayingPattern(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：Python导师
    print("\n" + "=" * 50)
    print("示例1: Python导师角色")
    print("=" * 50)

    result1 = pattern.python_tutor(
        question="请解释Python中的装饰器是什么，以及如何使用？"
    )

    if result1["success"]:
        print(f"角色: {result1['role']}")
        print(f"问题: {result1['question']}")
        print(f"\n回答:\n{result1['answer']}")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：系统架构师
    print("\n" + "=" * 50)
    print("示例2: 系统架构师角色")
    print("=" * 50)

    result2 = pattern.system_architect(
        question="如何设计一个支持千万级用户的电商系统？"
    )

    if result2["success"]:
        print(f"角色: {result2['role']}")
        print(f"问题: {result2['question']}")
        print(f"\n回答:\n{result2['answer'][:500]}...")  # 显示前500字符
    else:
        print(f"错误: {result2['error']}")

    # 示例3：代码审查专家
    print("\n" + "=" * 50)
    print("示例3: 代码审查专家角色")
    print("=" * 50)

    code_sample = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
"""

    result3 = pattern.code_reviewer(code_sample)

    if result3["success"]:
        print(f"角色: {result3['role']}")
        print(f"\n审查结果:\n{result3['answer'][:500]}...")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：产品经理
    print("\n" + "=" * 50)
    print("示例4: 产品经理角色")
    print("=" * 50)

    result4 = pattern.product_manager(
        requirement="开发一个智能学习助手APP，帮助学生提高学习效率。"
    )

    if result4["success"]:
        print(f"角色: {result4['role']}")
        print(f"\n分析结果:\n{result4['answer'][:500]}...")
    else:
        print(f"错误: {result4['error']}")

    # 示例5：创意写作者
    print("\n" + "=" * 50)
    print("示例5: 创意写作者角色")
    print("=" * 50)

    result5 = pattern.creative_writer(
        topic="未来的AI世界",
        style="科幻且富有想象力"
    )

    if result5["success"]:
        print(f"角色: {result5['role']}")
        print(f"\n创作:\n{result5['answer']}")
    else:
        print(f"错误: {result5['error']}")

    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
