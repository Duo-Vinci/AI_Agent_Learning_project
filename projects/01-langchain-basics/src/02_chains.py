"""
LangChain 基础教程 - 02: Chain（链）详解

本模块演示：
1. 简单的 LLM Chain
2. 顺序链（Sequential Chain）
3. LCEL（LangChain Expression Language）
4. 条件分支链
5. 并行链
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel


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


def demo_simple_chain():
    """示例1: 简单的 LLM Chain"""
    print_section("示例1: 简单的 LLM Chain")

    llm = init_llm()

    # 创建提示词模板
    prompt = ChatPromptTemplate.from_template("用一句话介绍 {topic}")

    # 使用 LCEL 构建链: prompt -> llm -> output_parser
    chain = prompt | llm | StrOutputParser()

    print("Chain 结构: Prompt -> LLM -> OutputParser")

    # 执行链
    result = chain.invoke({"topic": "机器学习"})
    print(f"\n输入: 机器学习")
    print(f"输出: {result}")

    # 批量执行
    print("\n批量执行:")
    topics = [{"topic": "深度学习"}, {"topic": "自然语言处理"}, {"topic": "计算机视觉"}]
    results = chain.batch(topics)
    for topic, result in zip(topics, results):
        print(f"  {topic['topic']}: {result}")


def demo_sequential_chain():
    """示例2: 顺序链（多步处理）"""
    print_section("示例2: 顺序链")

    llm = init_llm()

    # 第一步：生成故事大纲
    outline_prompt = ChatPromptTemplate.from_template(
        "为一个关于{theme}的短故事写一个简短的大纲（3-4行）"
    )
    outline_chain = outline_prompt | llm | StrOutputParser()

    # 第二步：根据大纲写故事
    story_prompt = ChatPromptTemplate.from_template(
        "根据以下大纲，写一个简短的故事（100字左右）：\n\n{outline}"
    )
    story_chain = story_prompt | llm | StrOutputParser()

    # 组合成顺序链
    full_chain = (
        {"outline": outline_chain}
        | RunnablePassthrough.assign(story=lambda x: story_chain.invoke({"outline": x["outline"]}))
    )

    # 执行链
    result = full_chain.invoke({"theme": "太空探险"})
    print(f"主题: 太空探险")
    print(f"\n步骤1 - 大纲:\n{result['outline']}")
    print(f"\n步骤2 - 完整故事:\n{result['story']}")


def demo_lcel_features():
    """示例3: LCEL 高级特性"""
    print_section("示例3: LCEL 高级特性")

    llm = init_llm()

    # 自定义处理函数
    def uppercase_first_letter(text: str) -> str:
        """将首字母大写"""
        return text[0].upper() + text[1:] if text else text

    def add_prefix(text: str) -> str:
        """添加前缀"""
        return f"[AI回答] {text}"

    # 构建包含自定义处理的链
    prompt = ChatPromptTemplate.from_template("用一句话解释 {term}")

    chain = (
        prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(uppercase_first_letter)
        | RunnableLambda(add_prefix)
    )

    print("Chain 结构: Prompt -> LLM -> Parser -> Uppercase -> AddPrefix")

    result = chain.invoke({"term": "区块链"})
    print(f"\n输出: {result}")

    # 使用 RunnablePassthrough 保留原始输入
    print("\n使用 RunnablePassthrough 保留输入:")
    chain_with_input = (
        RunnablePassthrough.assign(
            answer=prompt | llm | StrOutputParser()
        )
    )

    result = chain_with_input.invoke({"term": "量子计算"})
    print(f"输入: {result['term']}")
    print(f"输出: {result['answer']}")


def demo_parallel_chain():
    """示例4: 并行链"""
    print_section("示例4: 并行链")

    llm = init_llm()

    # 创建多个并行任务
    summary_prompt = ChatPromptTemplate.from_template(
        "用一句话总结 {topic}"
    )
    pros_prompt = ChatPromptTemplate.from_template(
        "列出 {topic} 的3个优点（用逗号分隔）"
    )
    cons_prompt = ChatPromptTemplate.from_template(
        "列出 {topic} 的3个缺点（用逗号分隔）"
    )

    # 使用 RunnableParallel 并行执行
    parallel_chain = RunnableParallel(
        summary=summary_prompt | llm | StrOutputParser(),
        pros=pros_prompt | llm | StrOutputParser(),
        cons=cons_prompt | llm | StrOutputParser()
    )

    print("并行执行三个任务: 总结、优点、缺点")

    result = parallel_chain.invoke({"topic": "远程工作"})
    print(f"\n主题: 远程工作")
    print(f"\n总结:\n{result['summary']}")
    print(f"\n优点:\n{result['pros']}")
    print(f"\n缺点:\n{result['cons']}")


def demo_conditional_chain():
    """示例5: 条件分支链"""
    print_section("示例5: 条件分支链")

    llm = init_llm()

    # 根据情绪选择不同的回复策略
    def route_by_sentiment(input_dict):
        """根据关键词判断情绪"""
        text = input_dict["text"].lower()

        if any(word in text for word in ["开心", "高兴", "快乐", "好"]):
            return "positive"
        elif any(word in text for word in ["难过", "伤心", "不好", "糟糕"]):
            return "negative"
        else:
            return "neutral"

    # 不同情绪的回复模板
    positive_prompt = ChatPromptTemplate.from_template(
        "用户说：{text}\n\n请给出一个积极、鼓励的回复（20字内）"
    )

    negative_prompt = ChatPromptTemplate.from_template(
        "用户说：{text}\n\n请给出一个安慰、支持的回复（20字内）"
    )

    neutral_prompt = ChatPromptTemplate.from_template(
        "用户说：{text}\n\n请给出一个友好、中立的回复（20字内）"
    )

    # 创建条件链
    positive_chain = positive_prompt | llm | StrOutputParser()
    negative_chain = negative_prompt | llm | StrOutputParser()
    neutral_chain = neutral_prompt | llm | StrOutputParser()

    # 路由函数
    def conditional_chain(input_dict):
        sentiment = route_by_sentiment(input_dict)
        print(f"检测到情绪: {sentiment}")

        if sentiment == "positive":
            return positive_chain.invoke(input_dict)
        elif sentiment == "negative":
            return negative_chain.invoke(input_dict)
        else:
            return neutral_chain.invoke(input_dict)

    # 测试不同情绪的输入
    test_cases = [
        "我今天很开心！",
        "我感觉很难过...",
        "今天天气不错"
    ]

    for text in test_cases:
        print(f"\n输入: {text}")
        result = conditional_chain({"text": text})
        print(f"回复: {result}")


def demo_chain_error_handling():
    """示例6: Chain 错误处理"""
    print_section("示例6: Chain 错误处理")

    llm = init_llm()

    # 创建可能出错的处理函数
    def parse_number(text: str) -> int:
        """尝试从文本中提取数字"""
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        raise ValueError(f"无法从文本中提取数字: {text}")

    prompt = ChatPromptTemplate.from_template("随机说一个1-100之间的数字")

    chain = prompt | llm | StrOutputParser() | RunnableLambda(parse_number)

    # 尝试执行并处理错误
    try:
        result = chain.invoke({})
        print(f"提取到的数字: {result}")
        print(f"数字类型: {type(result)}")
    except Exception as e:
        print(f"错误: {str(e)}")

    # 使用 fallback 处理错误
    print("\n使用 fallback 机制:")

    safe_chain = chain.with_fallbacks(
        [RunnableLambda(lambda x: 0)]  # 如果失败，返回 0
    )

    result = safe_chain.invoke({})
    print(f"结果: {result}")


def main():
    """运行所有示例"""
    try:
        demo_simple_chain()
        demo_sequential_chain()
        demo_lcel_features()
        demo_parallel_chain()
        demo_conditional_chain()
        demo_chain_error_handling()

        print_section("所有示例执行完成")
        print("Chain 是 LangChain 的核心概念，通过链式组合不同组件，")
        print("可以构建强大而灵活的 AI 应用！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
