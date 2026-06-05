"""
思维链推理高级应用模块

深入探索Chain-of-Thought在各种复杂问题中的应用。
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class ChainOfThoughtReasoning:
    """思维链推理高级应用类"""

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

    def math_word_problem(self, problem: str) -> Dict[str, Any]:
        """
        数学应用题求解（带思维链示例）

        Args:
            problem: 数学问题

        Returns:
            求解结果
        """
        prompt = f"""请用思维链方法解决以下数学问题。参考示例格式：

示例：
问题：一家商店有苹果和橘子。苹果每个3元，橘子每个2元。小明买了4个苹果和5个橘子，他付了50元，应该找回多少钱？

思维链推理：
步骤1：理解问题
- 已知：苹果3元/个，橘子2元/个，买了4个苹果和5个橘子，付了50元
- 求：找回多少钱

步骤2：计算苹果总价
- 苹果单价 = 3元
- 购买数量 = 4个
- 苹果总价 = 3 × 4 = 12元

步骤3：计算橘子总价
- 橘子单价 = 2元
- 购买数量 = 5个
- 橘子总价 = 2 × 5 = 10元

步骤4：计算总花费
- 总花费 = 苹果总价 + 橘子总价
- 总花费 = 12 + 10 = 22元

步骤5：计算找零
- 付款金额 = 50元
- 找零 = 50 - 22 = 28元

步骤6：验证答案
- 买的东西：12 + 10 = 22元 ✓
- 找零后：22 + 28 = 50元 ✓
- 答案合理

最终答案：应该找回28元

---

现在请用同样的方法解决以下问题：

问题：{problem}

思维链推理："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1500
            )

            return {
                "problem": problem,
                "reasoning": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"problem": problem, "error": str(e), "success": False}

    def algorithm_analysis(self, code: str, question: str) -> Dict[str, Any]:
        """
        算法复杂度分析

        Args:
            code: 算法代码
            question: 分析问题

        Returns:
            分析结果
        """
        prompt = f"""请用思维链方法分析以下算法：

代码：
```python
{code}
```

问题：{question}

请按以下步骤分析：

步骤1：理解算法逻辑
- 分析代码的主要操作
- 识别循环和递归结构
- 理解数据流向

步骤2：分析时间复杂度
- 识别基本操作
- 计算每个操作的执行次数
- 推导总的时间复杂度

步骤3：分析空间复杂度
- 识别使用的额外空间
- 分析递归调用栈（如有）
- 推导总的空间复杂度

步骤4：优化建议
- 指出可能的性能瓶颈
- 提供优化思路

步骤5：结论
- 总结复杂度分析
- 评估算法效率

请开始分析："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )

            return {
                "code": code,
                "question": question,
                "analysis": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"code": code, "error": str(e), "success": False}

    def causal_reasoning(self, scenario: str, question: str) -> Dict[str, Any]:
        """
        因果推理

        Args:
            scenario: 场景描述
            question: 推理问题

        Returns:
            推理结果
        """
        prompt = f"""请用因果推理的思维链方法分析：

场景：
{scenario}

问题：{question}

请按以下步骤推理：

步骤1：识别关键事件和因素
- 列出场景中的主要事件
- 识别相关的因素和变量

步骤2：建立因果关系
- 分析事件之间的因果链
- 识别直接原因和间接原因
- 考虑可能的因果循环

步骤3：评估影响程度
- 评估各因素的重要性
- 分析主要影响和次要影响

步骤4：考虑反事实情况
- 如果某个因素改变会如何
- 识别必要条件和充分条件

步骤5：得出结论
- 总结主要的因果关系
- 回答原问题

请开始推理："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1500
            )

            return {
                "scenario": scenario,
                "question": question,
                "reasoning": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"scenario": scenario, "error": str(e), "success": False}

    def strategic_planning(self, goal: str, constraints: List[str]) -> Dict[str, Any]:
        """
        战略规划推理

        Args:
            goal: 目标
            constraints: 约束条件列表

        Returns:
            规划结果
        """
        constraints_text = "\n".join(f"- {c}" for c in constraints)

        prompt = f"""请用思维链方法进行战略规划：

目标：
{goal}

约束条件：
{constraints_text}

请按以下步骤规划：

步骤1：目标分解
- 将大目标分解为可执行的子目标
- 建立目标层次结构

步骤2：约束分析
- 分析每个约束的影响
- 识别关键约束和次要约束
- 评估约束之间的关联

步骤3：方案设计
- 针对每个子目标设计方案
- 考虑约束条件的限制
- 评估方案的可行性

步骤4：资源分配
- 识别需要的资源
- 制定资源分配策略
- 考虑优先级和依赖关系

步骤5：风险评估
- 识别潜在风险
- 制定应对策略
- 建立监控机制

步骤6：实施路线图
- 制定分阶段实施计划
- 设置里程碑和检查点
- 定义成功指标

请开始规划："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )

            return {
                "goal": goal,
                "constraints": constraints,
                "planning": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"goal": goal, "error": str(e), "success": False}

    def ethical_reasoning(self, dilemma: str) -> Dict[str, Any]:
        """
        伦理推理

        Args:
            dilemma: 伦理困境描述

        Returns:
            推理结果
        """
        prompt = f"""请用思维链方法分析以下伦理困境：

困境：
{dilemma}

请从多个伦理角度分析：

步骤1：理解困境
- 识别涉及的利益相关方
- 明确冲突的价值观
- 理解决策的影响范围

步骤2：后果主义分析
- 分析各种选择的后果
- 评估对不同群体的影响
- 考虑短期和长期效果

步骤3：义务论分析
- 考虑道德义务和原则
- 分析权利和责任
- 评估是否违反基本道德准则

步骤4：美德伦理分析
- 考虑什么样的行为体现美德
- 思考理想的品格特质
- 评估行为对品格的影响

步骤5：权衡与判断
- 综合不同伦理视角
- 识别核心价值冲突
- 寻找可能的平衡点

步骤6：结论与建议
- 提出合理的行动方案
- 说明理由和考虑因素
- 承认决策的局限性

请开始分析："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )

            return {
                "dilemma": dilemma,
                "reasoning": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"dilemma": dilemma, "error": str(e), "success": False}


def main():
    """示例用法"""
    print("=" * 60)
    print("思维链推理高级应用示例")
    print("=" * 60)

    try:
        reasoner = ChainOfThoughtReasoning(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：数学应用题
    print("\n" + "=" * 60)
    print("示例1: 数学应用题求解")
    print("=" * 60)

    result1 = reasoner.math_word_problem(
        problem="一个班有40名学生，其中60%是女生。在期末考试中，80%的女生和70%的男生及格了。请问全班的及格率是多少？"
    )

    if result1["success"]:
        print(f"问题: {result1['problem']}")
        print(f"\n推理过程:\n{result1['reasoning'][:800]}...")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：算法分析
    print("\n" + "=" * 60)
    print("示例2: 算法复杂度分析")
    print("=" * 60)

    code_sample = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

    result2 = reasoner.algorithm_analysis(
        code=code_sample,
        question="请分析这个冒泡排序算法的时间和空间复杂度，并提供优化建议。"
    )

    if result2["success"]:
        print(f"\n分析结果:\n{result2['analysis'][:700]}...")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：战略规划
    print("\n" + "=" * 60)
    print("示例3: 战略规划推理")
    print("=" * 60)

    result3 = reasoner.strategic_planning(
        goal="在一年内将公司产品的市场份额从10%提升到20%",
        constraints=[
            "预算有限，只有500万元",
            "团队规模不能超过现有的50人",
            "必须保持现有客户的满意度",
            "需要符合行业监管要求"
        ]
    )

    if result3["success"]:
        print(f"目标: {result3['goal']}")
        print(f"\n规划方案:\n{result3['planning'][:700]}...")
    else:
        print(f"错误: {result3['error']}")

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
