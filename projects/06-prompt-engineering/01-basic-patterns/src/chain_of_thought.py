"""
Chain-of-Thought（思维链）模式实现

通过引导模型逐步推理来解决复杂问题。
适用于数学问题、逻辑推理、复杂分析等场景。
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class ChainOfThoughtPattern:
    """思维链模式类"""

    def __init__(self, provider: str = "openai"):
        """
        初始化思维链模式

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

    def solve_with_reasoning(
        self,
        problem: str,
        steps: Optional[List[str]] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        使用思维链解决问题

        Args:
            problem: 问题描述
            steps: 推理步骤提示（可选）
            temperature: 温度参数

        Returns:
            解决方案字典
        """
        if steps:
            steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
            prompt = f"""请一步步分析并解决以下问题：

问题：{problem}

请按以下步骤思考：
{steps_text}

让我们开始逐步分析："""
        else:
            prompt = f"""请一步步分析并解决以下问题：

问题：{problem}

请详细展示你的推理过程，包括：
1. 问题理解
2. 信息提取
3. 解决思路
4. 逐步推导
5. 最终答案

让我们开始："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个逻辑清晰的问题解决专家，善于分步推理。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=1500
            )

            reasoning = response.choices[0].message.content.strip()

            return {
                "problem": problem,
                "reasoning": reasoning,
                "success": True
            }
        except Exception as e:
            return {
                "problem": problem,
                "error": str(e),
                "success": False
            }

    def math_problem_solver(self, problem: str) -> Dict[str, Any]:
        """
        数学问题求解器

        Args:
            problem: 数学问题

        Returns:
            求解结果
        """
        steps = [
            "理解问题：明确题目要求什么",
            "提取信息：找出所有已知条件和未知量",
            "建立关系：根据数学原理建立等式或关系式",
            "求解计算：逐步计算得出结果",
            "验证答案：检查答案是否合理"
        ]

        return self.solve_with_reasoning(problem, steps, temperature=0.2)

    def logic_reasoning(self, problem: str) -> Dict[str, Any]:
        """
        逻辑推理问题

        Args:
            problem: 逻辑问题

        Returns:
            推理结果
        """
        steps = [
            "分析条件：列出所有已知条件",
            "建立关系：理解各条件之间的逻辑关系",
            "推理过程：根据逻辑规则逐步推导",
            "得出结论：给出最终答案",
            "反向验证：检查结论是否符合所有条件"
        ]

        return self.solve_with_reasoning(problem, steps, temperature=0.3)

    def code_debug_analysis(self, code: str, error_msg: str) -> Dict[str, Any]:
        """
        代码调试分析

        Args:
            code: 有问题的代码
            error_msg: 错误信息

        Returns:
            调试分析结果
        """
        problem = f"""分析以下代码的错误：

代码：
```python
{code}
```

错误信息：
{error_msg}
"""

        steps = [
            "理解代码：分析代码的意图和逻辑",
            "定位错误：根据错误信息找出问题所在",
            "分析原因：解释为什么会出现这个错误",
            "提供方案：给出具体的修复方法",
            "优化建议：提供代码改进建议"
        ]

        return self.solve_with_reasoning(problem, steps, temperature=0.4)

    def decision_analysis(self, situation: str, options: List[str]) -> Dict[str, Any]:
        """
        决策分析

        Args:
            situation: 决策情境
            options: 可选方案列表

        Returns:
            分析结果
        """
        options_text = "\n".join(f"- 方案{i+1}：{opt}" for i, opt in enumerate(options))

        problem = f"""请分析以下决策场景：

情境：
{situation}

可选方案：
{options_text}
"""

        steps = [
            "理解情境：分析当前面临的问题和约束条件",
            "评估方案：分析每个方案的优缺点",
            "权衡利弊：比较各方案在不同维度的表现",
            "风险分析：识别各方案的潜在风险",
            "推荐决策：给出最优方案及理由"
        ]

        return self.solve_with_reasoning(problem, steps, temperature=0.5)

    def system_design_analysis(self, requirement: str) -> Dict[str, Any]:
        """
        系统设计分析

        Args:
            requirement: 系统需求

        Returns:
            设计分析结果
        """
        problem = f"""请设计以下系统：

需求：
{requirement}
"""

        steps = [
            "需求分析：明确系统的核心功能和非功能需求",
            "架构设计：设计系统的整体架构和主要模块",
            "技术选型：选择合适的技术栈和工具",
            "关键问题：分析可能遇到的技术挑战",
            "实施建议：提供分阶段的实施路线图"
        ]

        return self.solve_with_reasoning(problem, steps, temperature=0.6)

    def text_analysis(self, text: str, analysis_type: str = "全面分析") -> Dict[str, Any]:
        """
        文本深度分析

        Args:
            text: 待分析的文本
            analysis_type: 分析类型

        Returns:
            分析结果
        """
        problem = f"""请{analysis_type}以下文本：

文本：
{text}
"""

        steps = [
            "内容理解：总结文本的主要内容",
            "结构分析：分析文本的组织结构和逻辑",
            "观点提取：识别作者的核心观点和论据",
            "评价分析：评估论证的有效性和说服力",
            "总结归纳：给出综合性的分析结论"
        ]

        return self.solve_with_reasoning(problem, steps, temperature=0.5)

    def problem_decomposition(self, complex_problem: str) -> Dict[str, Any]:
        """
        复杂问题分解

        Args:
            complex_problem: 复杂问题描述

        Returns:
            分解结果
        """
        steps = [
            "问题拆解：将复杂问题分解为多个子问题",
            "依赖分析：分析子问题之间的依赖关系",
            "优先级排序：确定子问题的解决顺序",
            "方案设计：为每个子问题提供解决思路",
            "整合方案：将各部分整合为完整解决方案"
        ]

        return self.solve_with_reasoning(complex_problem, steps, temperature=0.5)


def main():
    """示例用法"""
    print("=" * 50)
    print("思维链模式（Chain-of-Thought Pattern）示例")
    print("=" * 50)

    try:
        pattern = ChainOfThoughtPattern(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：数学问题
    print("\n" + "=" * 50)
    print("示例1: 数学问题求解")
    print("=" * 50)

    math_problem = """
    一个水池有两个进水管和一个出水管。
    甲管单独开需要4小时注满，乙管单独开需要6小时注满，
    丙管单独开需要12小时放空。
    如果三管同时打开，需要多少小时注满？
    """

    result1 = pattern.math_problem_solver(math_problem)

    if result1["success"]:
        print(f"问题: {result1['problem'].strip()}")
        print(f"\n推理过程:\n{result1['reasoning']}")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：逻辑推理
    print("\n" + "=" * 50)
    print("示例2: 逻辑推理")
    print("=" * 50)

    logic_problem = """
    有三个人：张三、李四、王五。
    - 其中一个人说真话，一个人说假话，一个人随机说真话或假话。
    - 张三说："我不是说真话的人。"
    - 李四说："张三说的是假话。"
    - 王五说："我是随机说话的人。"
    问：谁说真话，谁说假话，谁随机说话？
    """

    result2 = pattern.logic_reasoning(logic_problem)

    if result2["success"]:
        print(f"问题: {result2['problem'].strip()}")
        print(f"\n推理过程:\n{result2['reasoning'][:600]}...")  # 显示前600字符
    else:
        print(f"错误: {result2['error']}")

    # 示例3：代码调试
    print("\n" + "=" * 50)
    print("示例3: 代码调试分析")
    print("=" * 50)

    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

result = calculate_average([])
print(result)
"""

    result3 = pattern.code_debug_analysis(
        code=buggy_code,
        error_msg="ZeroDivisionError: division by zero"
    )

    if result3["success"]:
        print(f"\n分析结果:\n{result3['reasoning'][:500]}...")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：决策分析
    print("\n" + "=" * 50)
    print("示例4: 决策分析")
    print("=" * 50)

    result4 = pattern.decision_analysis(
        situation="公司需要选择一个新的数据库系统，考虑因素包括性能、成本、可维护性和团队技能。",
        options=[
            "使用PostgreSQL（开源、团队熟悉）",
            "使用MongoDB（NoSQL、高性能）",
            "使用云数据库服务（托管、高成本）"
        ]
    )

    if result4["success"]:
        print(f"\n分析结果:\n{result4['reasoning'][:500]}...")
    else:
        print(f"错误: {result4['error']}")

    # 示例5：问题分解
    print("\n" + "=" * 50)
    print("示例5: 复杂问题分解")
    print("=" * 50)

    result5 = pattern.problem_decomposition(
        complex_problem="如何构建一个能够支持百万用户同时在线的实时聊天系统？"
    )

    if result5["success"]:
        print(f"问题: {result5['problem']}")
        print(f"\n分解方案:\n{result5['reasoning'][:500]}...")
    else:
        print(f"错误: {result5['error']}")

    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
