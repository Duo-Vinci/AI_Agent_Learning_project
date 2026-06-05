"""
Prompt优化器

自动分析和优化Prompt，提高输出质量和稳定性。
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class PromptOptimizer:
    """Prompt优化器类"""

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

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        分析Prompt质量

        Args:
            prompt: 待分析的prompt

        Returns:
            分析结果
        """
        analysis_prompt = f"""你是一个Prompt工程专家。请分析以下Prompt的质量：

【待分析的Prompt】
{prompt}

请从以下维度进行分析：

1. 清晰度（1-10分）
   - 指令是否明确
   - 是否容易理解
   - 是否有歧义

2. 完整性（1-10分）
   - 是否包含必要的上下文
   - 是否定义了输出格式
   - 是否有明确的约束条件

3. 结构化（1-10分）
   - 逻辑是否清晰
   - 是否使用了分隔符
   - 是否便于模型理解

4. 有效性（1-10分）
   - 是否能达到预期目标
   - 是否有冗余信息
   - Token使用是否高效

请按以下格式输出分析结果：

## 评分
- 清晰度: X/10
- 完整性: X/10
- 结构化: X/10
- 有效性: X/10
- 总分: XX/40

## 优点
1. ...
2. ...

## 问题
1. ...
2. ...

## 改进建议
1. ...
2. ..."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.4,
                max_tokens=1500
            )

            return {
                "prompt": prompt,
                "analysis": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"prompt": prompt, "error": str(e), "success": False}

    def optimize_prompt(
        self,
        original_prompt: str,
        goal: str,
        test_cases: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        优化Prompt

        Args:
            original_prompt: 原始prompt
            goal: 优化目标
            test_cases: 测试用例（可选）

        Returns:
            优化结果
        """
        test_cases_text = ""
        if test_cases:
            test_cases_text = "\n测试用例：\n" + "\n".join(f"- {tc}" for tc in test_cases)

        optimization_prompt = f"""你是一个Prompt工程专家。请优化以下Prompt。

【原始Prompt】
{original_prompt}

【优化目标】
{goal}
{test_cases_text}

请提供：

1. 问题诊断
   - 当前Prompt存在的主要问题
   - 为什么会导致不理想的结果

2. 优化策略
   - 应该采用什么优化方法
   - 为什么这些方法有效

3. 优化后的Prompt
   - 提供改进后的完整Prompt
   - 用【优化版本】标记

4. 改进点说明
   - 列出具体的改进点
   - 解释预期的改进效果

请开始优化："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": optimization_prompt}],
                temperature=0.5,
                max_tokens=2000
            )

            result = response.choices[0].message.content.strip()

            # 尝试提取优化后的prompt
            optimized_prompt = original_prompt
            if "【优化版本】" in result:
                try:
                    optimized_prompt = result.split("【优化版本】")[1].split("\n\n")[0].strip()
                except:
                    pass

            return {
                "original_prompt": original_prompt,
                "goal": goal,
                "optimization_result": result,
                "optimized_prompt": optimized_prompt,
                "success": True
            }
        except Exception as e:
            return {"original_prompt": original_prompt, "error": str(e), "success": False}

    def test_prompt(
        self,
        prompt: str,
        test_inputs: List[str],
        expected_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        测试Prompt效果

        Args:
            prompt: 待测试的prompt
            test_inputs: 测试输入列表
            expected_patterns: 期望的输出模式（可选）

        Returns:
            测试结果
        """
        test_results = []

        for i, test_input in enumerate(test_inputs, 1):
            full_prompt = f"{prompt}\n\n输入：{test_input}"

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.3,
                    max_tokens=500
                )

                output = response.choices[0].message.content.strip()

                # 简单的模式匹配检查
                pattern_match = True
                if expected_patterns:
                    import re
                    pattern_match = any(re.search(pattern, output, re.IGNORECASE) for pattern in expected_patterns)

                test_results.append({
                    "test_id": i,
                    "input": test_input,
                    "output": output,
                    "pattern_match": pattern_match,
                    "status": "PASS" if pattern_match else "FAIL"
                })

            except Exception as e:
                test_results.append({
                    "test_id": i,
                    "input": test_input,
                    "error": str(e),
                    "status": "ERROR"
                })

        # 计算统计信息
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get("status") == "PASS")
        failed = sum(1 for r in test_results if r.get("status") == "FAIL")
        errors = sum(1 for r in test_results if r.get("status") == "ERROR")

        return {
            "prompt": prompt,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "test_results": test_results,
            "success": True
        }

    def compare_prompts(
        self,
        prompts: List[Tuple[str, str]],
        test_input: str
    ) -> Dict[str, Any]:
        """
        比较多个Prompt的效果

        Args:
            prompts: Prompt列表，每个元素为(名称, prompt内容)
            test_input: 测试输入

        Returns:
            比较结果
        """
        comparison_results = []

        for name, prompt in prompts:
            full_prompt = f"{prompt}\n\n输入：{test_input}"

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.3,
                    max_tokens=500
                )

                output = response.choices[0].message.content.strip()

                comparison_results.append({
                    "name": name,
                    "prompt": prompt,
                    "output": output,
                    "output_length": len(output),
                    "status": "SUCCESS"
                })

            except Exception as e:
                comparison_results.append({
                    "name": name,
                    "prompt": prompt,
                    "error": str(e),
                    "status": "ERROR"
                })

        return {
            "test_input": test_input,
            "comparison_results": comparison_results,
            "success": True
        }

    def suggest_improvements(self, prompt: str, issues: List[str]) -> Dict[str, Any]:
        """
        针对特定问题提供改进建议

        Args:
            prompt: 原始prompt
            issues: 问题列表

        Returns:
            改进建议
        """
        issues_text = "\n".join(f"- {issue}" for issue in issues)

        suggestion_prompt = f"""你是一个Prompt工程专家。请针对以下Prompt的特定问题提供改进建议：

【原始Prompt】
{prompt}

【遇到的问题】
{issues_text}

请提供：

1. 问题根因分析
   - 为什么会出现这些问题
   - 问题之间的关联

2. 具体改进方案
   - 针对每个问题的解决方法
   - 改进的优先级

3. 改进示例
   - 展示如何修改Prompt
   - 突出关键改进点

4. 预防措施
   - 如何避免类似问题
   - 最佳实践建议

请开始分析："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": suggestion_prompt}],
                temperature=0.5,
                max_tokens=1500
            )

            return {
                "prompt": prompt,
                "issues": issues,
                "suggestions": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"prompt": prompt, "error": str(e), "success": False}

    def generate_test_cases(self, prompt: str, num_cases: int = 5) -> Dict[str, Any]:
        """
        为Prompt生成测试用例

        Args:
            prompt: 待测试的prompt
            num_cases: 测试用例数量

        Returns:
            生成的测试用例
        """
        generation_prompt = f"""请为以下Prompt生成{num_cases}个测试用例：

【Prompt】
{prompt}

请生成多样化的测试用例，包括：
- 正常情况
- 边界情况
- 异常情况

请按以下格式输出：

测试用例1：[描述] - [输入内容]
测试用例2：[描述] - [输入内容]
...

请生成测试用例："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": generation_prompt}],
                temperature=0.6,
                max_tokens=1000
            )

            return {
                "prompt": prompt,
                "num_cases": num_cases,
                "test_cases": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"prompt": prompt, "error": str(e), "success": False}


def main():
    """示例用法"""
    print("=" * 60)
    print("Prompt优化器示例")
    print("=" * 60)

    try:
        optimizer = PromptOptimizer(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：分析Prompt质量
    print("\n" + "=" * 60)
    print("示例1: Prompt质量分析")
    print("=" * 60)

    original_prompt = "请分析这段代码"

    result1 = optimizer.analyze_prompt(original_prompt)

    if result1["success"]:
        print(f"待分析的Prompt: {result1['prompt']}")
        print(f"\n分析结果:\n{result1['analysis'][:600]}...")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：优化Prompt
    print("\n" + "=" * 60)
    print("示例2: Prompt优化")
    print("=" * 60)

    result2 = optimizer.optimize_prompt(
        original_prompt="翻译成英文：{text}",
        goal="提高翻译质量，防止prompt注入，确保只进行翻译不执行其他指令",
        test_cases=[
            "正常文本翻译",
            "用户尝试注入新指令"
        ]
    )

    if result2["success"]:
        print(f"原始Prompt: {result2['original_prompt']}")
        print(f"优化目标: {result2['goal']}")
        print(f"\n优化结果:\n{result2['optimization_result'][:700]}...")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：测试Prompt
    print("\n" + "=" * 60)
    print("示例3: Prompt测试")
    print("=" * 60)

    test_prompt = "请用一句话总结以下内容，不超过50字："

    result3 = optimizer.test_prompt(
        prompt=test_prompt,
        test_inputs=[
            "人工智能是计算机科学的一个分支，旨在创造能够执行需要人类智能的任务的系统。",
            "Python是一种高级编程语言，以其简洁的语法和强大的库而闻名。",
            "机器学习是人工智能的子领域，专注于让计算机从数据中学习。"
        ],
        expected_patterns=[r".{10,50}"]  # 期望10-50个字符
    )

    if result3["success"]:
        print(f"测试Prompt: {result3['prompt']}")
        print(f"总测试数: {result3['total_tests']}")
        print(f"通过: {result3['passed']}")
        print(f"失败: {result3['failed']}")
        print(f"成功率: {result3['success_rate']:.1f}%")
        print(f"\n部分测试结果:")
        for r in result3['test_results'][:2]:
            print(f"  测试{r['test_id']}: {r['status']}")
            print(f"  输入: {r['input'][:50]}...")
            if 'output' in r:
                print(f"  输出: {r['output'][:80]}...")
    else:
        print(f"错误: {result3.get('error')}")

    # 示例4：比较Prompts
    print("\n" + "=" * 60)
    print("示例4: Prompt对比")
    print("=" * 60)

    result4 = optimizer.compare_prompts(
        prompts=[
            ("简单版", "分析情感："),
            ("详细版", "请分析以下文本的情感倾向（正面/负面/中性），并给出理由："),
            ("结构化版", "请分析文本情感：\n1. 判断情感倾向\n2. 给出置信度\n3. 列出关键词\n\n文本：")
        ],
        test_input="这个产品质量很好，值得购买！"
    )

    if result4["success"]:
        print(f"测试输入: {result4['test_input']}")
        print(f"\n对比结果:")
        for i, r in enumerate(result4['comparison_results'], 1):
            print(f"\n  版本{i}: {r['name']}")
            if r['status'] == 'SUCCESS':
                print(f"  输出长度: {r['output_length']}字符")
                print(f"  输出: {r['output'][:100]}...")
    else:
        print(f"错误: {result4.get('error')}")

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
