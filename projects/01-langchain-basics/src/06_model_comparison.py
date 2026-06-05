"""
LangChain 基础教程 - 06: 不同模型对比

本模块演示：
1. 配置多个不同的模型
2. 对比不同模型的输出
3. 对比不同温度参数
4. 对比响应时间
5. 成本估算
"""

import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def init_models() -> List[Dict]:
    """初始化多个模型进行对比"""
    load_dotenv()

    models = []

    # DeepSeek 模型
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        models.append({
            "name": "DeepSeek V4 Flash",
            "llm": ChatOpenAI(
                model="deepseek-v4-flash",
                temperature=0.7,
                api_key=deepseek_key,
                base_url="https://api.deepseek.com/v1"
            )
        })

    # OpenAI 模型
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        models.append({
            "name": "GPT-3.5 Turbo",
            "llm": ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=openai_key,
                base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
        })

        models.append({
            "name": "GPT-4",
            "llm": ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=openai_key,
                base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
        })

    if not models:
        raise ValueError("未找到任何可用的 API Key")

    return models


def demo_model_comparison():
    """示例1: 不同模型输出对比"""
    print_section("示例1: 不同模型输出对比")

    try:
        models = init_models()
    except ValueError as e:
        print(f"错误: {str(e)}")
        print("请至少配置一个 API Key")
        return

    prompt = "用一句话介绍量子计算"
    print(f"提示: {prompt}\n")

    for model_info in models:
        print(f"【{model_info['name']}】")
        try:
            start_time = time.time()
            response = model_info['llm'].invoke(prompt)
            duration = time.time() - start_time

            print(f"回复: {response.content}")
            print(f"耗时: {duration:.2f}秒")
            print()
        except Exception as e:
            print(f"错误: {str(e)}\n")


def demo_temperature_comparison():
    """示例2: 不同温度参数对比"""
    print_section("示例2: 不同温度参数对比")

    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        print("未找到 API Key")
        return

    temperatures = [0.0, 0.5, 1.0, 1.5]
    prompt = "写一个关于 AI 的创意标语"

    print(f"提示: {prompt}\n")
    print("温度越高，输出越有创意和随机性\n")

    for temp in temperatures:
        llm = ChatOpenAI(
            model=model_name,
            temperature=temp,
            api_key=api_key,
            base_url=api_base
        )

        print(f"【温度 = {temp}】")
        response = llm.invoke(prompt)
        print(f"输出: {response.content}\n")


def demo_consistency_test():
    """示例3: 模型一致性测试"""
    print_section("示例3: 模型一致性测试")

    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        print("未找到 API Key")
        return

    prompt = "计算 15 * 23 = ?"

    print(f"提示: {prompt}\n")
    print("使用温度=0，测试模型的一致性\n")

    llm_deterministic = ChatOpenAI(
        model=model_name,
        temperature=0.0,  # 完全确定性
        api_key=api_key,
        base_url=api_base
    )

    print("【5次运行结果】")
    for i in range(5):
        response = llm_deterministic.invoke(prompt)
        print(f"第{i+1}次: {response.content}")

    print("\n温度=0 时，相同输入应该得到相同（或非常相似）的输出")


def demo_performance_comparison():
    """示例4: 性能对比"""
    print_section("示例4: 性能对比")

    try:
        models = init_models()
    except ValueError as e:
        print(f"错误: {str(e)}")
        return

    prompts = [
        "什么是机器学习？",
        "什么是深度学习？",
        "什么是自然语言处理？"
    ]

    print(f"测试任务: {len(prompts)} 个问题\n")

    results = []

    for model_info in models:
        print(f"【{model_info['name']}】")

        total_time = 0
        responses = []

        for prompt in prompts:
            try:
                start_time = time.time()
                response = model_info['llm'].invoke(prompt)
                duration = time.time() - start_time

                total_time += duration
                responses.append(len(response.content))

                print(f"  {prompt[:20]}... 耗时 {duration:.2f}秒")
            except Exception as e:
                print(f"  错误: {str(e)}")
                continue

        avg_time = total_time / len(prompts) if prompts else 0
        avg_length = sum(responses) / len(responses) if responses else 0

        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  平均耗时: {avg_time:.2f}秒")
        print(f"  平均回复长度: {avg_length:.0f}字符\n")

        results.append({
            "model": model_info['name'],
            "total_time": total_time,
            "avg_time": avg_time,
            "avg_length": avg_length
        })

    # 对比总结
    if results:
        print("【性能总结】")
        fastest = min(results, key=lambda x: x['avg_time'])
        print(f"最快的模型: {fastest['model']} ({fastest['avg_time']:.2f}秒)")


def demo_task_suitability():
    """示例5: 不同任务的模型适用性"""
    print_section("示例5: 不同任务的模型适用性")

    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        print("未找到 API Key")
        return

    tasks = [
        {
            "name": "事实性问答",
            "prompt": "地球的半径是多少？",
            "recommended_temp": 0.0,
            "reason": "需要准确的事实，使用低温度"
        },
        {
            "name": "创意写作",
            "prompt": "写一个关于时间旅行的开头",
            "recommended_temp": 1.0,
            "reason": "需要创意和多样性，使用高温度"
        },
        {
            "name": "代码生成",
            "prompt": "写一个Python函数计算斐波那契数列",
            "recommended_temp": 0.2,
            "reason": "需要准确性但允许一些灵活性"
        },
        {
            "name": "翻译",
            "prompt": "将'Hello World'翻译成中文",
            "recommended_temp": 0.1,
            "reason": "翻译需要准确性，使用很低的温度"
        }
    ]

    for task in tasks:
        print(f"【{task['name']}】")
        print(f"提示: {task['prompt']}")
        print(f"推荐温度: {task['recommended_temp']}")
        print(f"原因: {task['reason']}")

        llm = ChatOpenAI(
            model=model_name,
            temperature=task['recommended_temp'],
            api_key=api_key,
            base_url=api_base
        )

        response = llm.invoke(task['prompt'])
        print(f"回复: {response.content}\n")


def demo_cost_estimation():
    """示例6: 成本估算"""
    print_section("示例6: 成本估算")

    # 价格表（仅供参考，实际价格请查看官方文档）
    pricing = {
        "DeepSeek V4 Flash": {
            "input": 0.0001,   # 每1K tokens
            "output": 0.0002,
        },
        "GPT-3.5 Turbo": {
            "input": 0.0005,
            "output": 0.0015,
        },
        "GPT-4": {
            "input": 0.03,
            "output": 0.06,
        }
    }

    print("假设场景:")
    print("  - 每天处理 10,000 个请求")
    print("  - 平均输入: 100 tokens")
    print("  - 平均输出: 200 tokens\n")

    daily_requests = 10000
    avg_input_tokens = 100
    avg_output_tokens = 200

    print("【每日成本估算】\n")

    for model_name, price in pricing.items():
        input_cost = (daily_requests * avg_input_tokens / 1000) * price['input']
        output_cost = (daily_requests * avg_output_tokens / 1000) * price['output']
        total_cost = input_cost + output_cost
        monthly_cost = total_cost * 30

        print(f"{model_name}:")
        print(f"  每日成本: ${total_cost:.2f}")
        print(f"  每月成本: ${monthly_cost:.2f}")
        print()


def demo_model_selection_guide():
    """示例7: 模型选择指南"""
    print_section("示例7: 模型选择指南")

    guide = """
模型选择指南
============

1. DeepSeek V4 Flash
   ✓ 优势: 速度快、成本低、中文理解好
   ✗ 劣势: 可能不如 GPT-4 全面
   适用: 日常对话、中文任务、大规模部署

2. GPT-3.5 Turbo
   ✓ 优势: 性价比高、响应快、能力全面
   ✗ 劣势: 复杂推理能力不如 GPT-4
   适用: 一般任务、客服机器人、内容生成

3. GPT-4
   ✓ 优势: 能力最强、推理能力好、可靠性高
   ✗ 劣势: 成本高、速度较慢
   适用: 复杂推理、专业任务、高质量要求

选择建议
--------
- 成本敏感 → DeepSeek / GPT-3.5
- 性能优先 → GPT-4
- 中文为主 → DeepSeek
- 速度优先 → DeepSeek V4 Flash / GPT-3.5 Turbo
- 推理复杂 → GPT-4

温度参数设置
----------
- 事实性任务: 0.0 - 0.3
- 一般对话: 0.5 - 0.7
- 创意写作: 0.8 - 1.2
- 代码生成: 0.1 - 0.3
"""

    print(guide)


def main():
    """运行所有示例"""
    try:
        demo_model_comparison()
        demo_temperature_comparison()
        demo_consistency_test()
        demo_performance_comparison()
        demo_task_suitability()
        demo_cost_estimation()
        demo_model_selection_guide()

        print_section("所有示例执行完成")
        print("选择合适的模型和参数对于构建高效的 AI 应用至关重要！")
        print("根据具体任务需求、预算和性能要求做出明智的选择。")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
