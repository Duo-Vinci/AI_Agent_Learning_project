"""
LangChain 基础教程 - 01: 提示词模板详解

本模块演示：
1. 基本的提示词模板使用
2. 多变量提示词模板
3. 对话提示词模板
4. Few-shot 提示词模板
5. 提示词模板组合
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    FewShotPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def init_llm():
    """初始化大语言模型"""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise ValueError("未找到 API Key，请配置 .env 文件")

    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )


def demo_basic_template():
    """示例1: 基本提示词模板"""
    print_section("示例1: 基本提示词模板")

    # 创建简单的提示词模板
    template = "请用{language}语言介绍{topic}，不超过{word_count}字。"
    prompt = PromptTemplate.from_template(template)

    print(f"模板内容: {template}")
    print(f"输入变量: {prompt.input_variables}")

    # 格式化提示词
    formatted = prompt.format(language="中文", topic="人工智能", word_count=100)
    print(f"\n格式化后的提示词:\n{formatted}")

    # 实际调用 LLM
    llm = init_llm()
    chain = prompt | llm
    response = chain.invoke({
        "language": "中文",
        "topic": "机器学习",
        "word_count": 50
    })
    print(f"\nAI 回复:\n{response.content}")


def demo_chat_template():
    """示例2: 对话提示词模板"""
    print_section("示例2: 对话提示词模板")

    # 创建对话模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位{role}，擅长{expertise}。"),
        ("user", "请帮我{task}"),
        ("assistant", "好的，我会尽力帮助你。"),
        ("user", "{question}")
    ])

    print(f"输入变量: {prompt.input_variables}")

    # 格式化提示词
    messages = prompt.format_messages(
        role="Python编程专家",
        expertise="数据处理和自动化",
        task="解决一个编程问题",
        question="如何高效读取大型CSV文件？"
    )

    print("\n格式化后的消息序列:")
    for msg in messages:
        print(f"  {msg.__class__.__name__}: {msg.content}")

    # 实际调用 LLM
    llm = init_llm()
    chain = prompt | llm
    response = chain.invoke({
        "role": "数据科学家",
        "expertise": "数据分析和可视化",
        "task": "分析数据",
        "question": "如何用Python绘制热力图？"
    })
    print(f"\nAI 回复:\n{response.content}")


def demo_few_shot_template():
    """示例3: Few-shot 提示词模板"""
    print_section("示例3: Few-shot 提示词模板")

    # 定义示例
    examples = [
        {"input": "开心", "output": "happy"},
        {"input": "悲伤", "output": "sad"},
        {"input": "愤怒", "output": "angry"},
    ]

    # 创建示例模板
    example_template = """
输入: {input}
输出: {output}
"""
    example_prompt = PromptTemplate.from_template(example_template)

    # 创建 Few-shot 模板
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="将以下中文情感词翻译成英文：",
        suffix="输入: {input}\n输出:",
        input_variables=["input"]
    )

    # 格式化提示词
    formatted = few_shot_prompt.format(input="兴奋")
    print(f"完整提示词:\n{formatted}")

    # 实际调用 LLM
    llm = init_llm()
    response = llm.invoke(formatted)
    print(f"\nAI 回复:\n{response.content}")


def demo_template_composition():
    """示例4: 提示词模板组合"""
    print_section("示例4: 提示词模板组合")

    # 创建系统消息模板
    system_template = SystemMessagePromptTemplate.from_template(
        "你是一位{profession}，有{years}年经验。你的风格是{style}。"
    )

    # 创建用户消息模板
    human_template = HumanMessagePromptTemplate.from_template(
        "请针对{topic}给出{advice_type}建议。"
    )

    # 组合成完整的对话模板
    chat_prompt = ChatPromptTemplate.from_messages([
        system_template,
        human_template
    ])

    print(f"输入变量: {chat_prompt.input_variables}")

    # 实际调用 LLM
    llm = init_llm()
    chain = chat_prompt | llm
    response = chain.invoke({
        "profession": "健身教练",
        "years": 10,
        "style": "科学严谨",
        "topic": "初学者增肌",
        "advice_type": "训练计划"
    })
    print(f"\nAI 回复:\n{response.content}")


def demo_partial_variables():
    """示例5: 部分变量预填充"""
    print_section("示例5: 部分变量预填充")

    # 创建模板
    prompt = PromptTemplate.from_template(
        "使用{language}语言，以{tone}的语气，介绍{topic}。"
    )

    # 预填充部分变量
    partial_prompt = prompt.partial(language="中文", tone="专业")

    print(f"原始输入变量: {prompt.input_variables}")
    print(f"预填充后输入变量: {partial_prompt.input_variables}")

    # 只需提供剩余变量
    formatted = partial_prompt.format(topic="区块链技术")
    print(f"\n格式化后的提示词:\n{formatted}")

    # 实际调用 LLM
    llm = init_llm()
    chain = partial_prompt | llm
    response = chain.invoke({"topic": "量子计算"})
    print(f"\nAI 回复:\n{response.content}")


def main():
    """运行所有示例"""
    try:
        demo_basic_template()
        demo_chat_template()
        demo_few_shot_template()
        demo_template_composition()
        demo_partial_variables()

        print_section("所有示例执行完成")
        print("提示词模板是 LangChain 的核心组件之一，")
        print("掌握好模板的使用可以让你的应用更加灵活和强大！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
