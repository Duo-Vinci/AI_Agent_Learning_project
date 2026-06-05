"""
LangChain 基础教程 - 04: 输出解析器详解

本模块演示：
1. 字符串输出解析器
2. JSON 输出解析器
3. Pydantic 输出解析器
4. 列表输出解析器
5. 结构化输出解析器
6. 自定义输出解析器
"""

import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    PydanticOutputParser,
    CommaSeparatedListOutputParser,
    StructuredOutputParser,
)
from langchain_core.output_parsers.base import BaseOutputParser
from pydantic import BaseModel, Field


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


def demo_string_parser():
    """示例1: 字符串输出解析器"""
    print_section("示例1: 字符串输出解析器")

    llm = init_llm()

    prompt = ChatPromptTemplate.from_template("用一句话介绍 {topic}")
    parser = StrOutputParser()

    chain = prompt | llm | parser

    result = chain.invoke({"topic": "量子计算"})

    print(f"返回类型: {type(result)}")
    print(f"返回内容: {result}")


def demo_json_parser():
    """示例2: JSON 输出解析器"""
    print_section("示例2: JSON 输出解析器")

    llm = init_llm()

    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个数据提取助手。请始终返回 JSON 格式的数据。"),
        ("user", "请提取以下信息并以 JSON 格式返回：姓名、年龄、职业\n\n{text}")
    ])

    chain = prompt | llm | parser

    text = "我叫张三，今年28岁，是一名软件工程师。"
    result = chain.invoke({"text": text})

    print(f"输入: {text}")
    print(f"返回类型: {type(result)}")
    print(f"返回内容: {result}")


def demo_pydantic_parser():
    """示例3: Pydantic 输出解析器"""
    print_section("示例3: Pydantic 输出解析器")

    # 定义数据模型
    class Person(BaseModel):
        """人物信息"""
        name: str = Field(description="姓名")
        age: int = Field(description="年龄")
        occupation: str = Field(description="职业")
        hobbies: List[str] = Field(description="爱好列表")

    llm = init_llm()

    parser = PydanticOutputParser(pydantic_object=Person)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个数据提取助手。\n{format_instructions}"),
        ("user", "请从以下文本中提取人物信息：\n\n{text}")
    ])

    chain = prompt | llm | parser

    text = "李四今年30岁，是一名数据科学家。他喜欢跑步、阅读和摄影。"

    result = chain.invoke({
        "text": text,
        "format_instructions": parser.get_format_instructions()
    })

    print(f"输入: {text}\n")
    print(f"返回类型: {type(result)}")
    print(f"返回对象: {result}")
    print(f"\n访问字段:")
    print(f"  姓名: {result.name}")
    print(f"  年龄: {result.age}")
    print(f"  职业: {result.occupation}")
    print(f"  爱好: {', '.join(result.hobbies)}")


def demo_list_parser():
    """示例4: 列表输出解析器"""
    print_section("示例4: 列表输出解析器")

    llm = init_llm()

    parser = CommaSeparatedListOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个助手。{format_instructions}"),
        ("user", "请列出 {count} 个 {category}")
    ])

    chain = prompt | llm | parser

    result = chain.invoke({
        "count": 5,
        "category": "编程语言",
        "format_instructions": parser.get_format_instructions()
    })

    print(f"返回类型: {type(result)}")
    print(f"返回内容: {result}")
    print(f"\n遍历列表:")
    for i, item in enumerate(result, 1):
        print(f"  {i}. {item.strip()}")


def demo_structured_parser():
    """示例5: 结构化输出解析器"""
    print_section("示例5: 结构化输出解析器")

    from langchain_core.output_parsers import ResponseSchema

    llm = init_llm()

    # 定义输出结构
    response_schemas = [
        ResponseSchema(name="title", description="书籍标题"),
        ResponseSchema(name="author", description="作者姓名"),
        ResponseSchema(name="year", description="出版年份"),
        ResponseSchema(name="summary", description="一句话简介")
    ]

    parser = StructuredOutputParser.from_response_schemas(response_schemas)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个图书信息提取助手。\n{format_instructions}"),
        ("user", "请提取以下书籍信息：\n\n{text}")
    ])

    chain = prompt | llm | parser

    text = "《三体》是刘慈欣创作的科幻小说，2008年出版。这是一部描述人类文明与外星文明接触的史诗级作品。"

    result = chain.invoke({
        "text": text,
        "format_instructions": parser.get_format_instructions()
    })

    print(f"输入: {text}\n")
    print(f"返回类型: {type(result)}")
    print(f"返回内容:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def demo_custom_parser():
    """示例6: 自定义输出解析器"""
    print_section("示例6: 自定义输出解析器")

    class SentimentParser(BaseOutputParser[dict]):
        """自定义情感分析解析器"""

        def parse(self, text: str) -> dict:
            """解析情感分析结果"""
            text = text.lower().strip()

            # 简单的情感判断
            if "积极" in text or "正面" in text or "positive" in text:
                sentiment = "positive"
                score = 0.8
            elif "消极" in text or "负面" in text or "negative" in text:
                sentiment = "negative"
                score = 0.2
            else:
                sentiment = "neutral"
                score = 0.5

            return {
                "sentiment": sentiment,
                "score": score,
                "raw_text": text
            }

        @property
        def _type(self) -> str:
            return "sentiment_parser"

    llm = init_llm()
    parser = SentimentParser()

    prompt = ChatPromptTemplate.from_template(
        "分析以下文本的情感倾向（积极/消极/中性）：\n\n{text}\n\n只回答情感倾向，不要解释。"
    )

    chain = prompt | llm | parser

    test_texts = [
        "这部电影太棒了，我非常喜欢！",
        "糟糕的体验，完全浪费时间。",
        "还可以，没什么特别的。"
    ]

    for text in test_texts:
        result = chain.invoke({"text": text})
        print(f"文本: {text}")
        print(f"情感: {result['sentiment']}, 分数: {result['score']}")
        print(f"原始输出: {result['raw_text']}\n")


def demo_parser_with_retry():
    """示例7: 带重试的解析器"""
    print_section("示例7: 带重试的解析器")

    from langchain.output_parsers import RetryWithErrorOutputParser

    class BookInfo(BaseModel):
        """书籍信息"""
        title: str = Field(description="书名")
        rating: float = Field(description="评分（0-10）")

    llm = init_llm()

    parser = PydanticOutputParser(pydantic_object=BookInfo)
    retry_parser = RetryWithErrorOutputParser.from_llm(
        parser=parser,
        llm=llm
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "提取书籍信息。\n{format_instructions}"),
        ("user", "{text}")
    ])

    # 第一次尝试：可能格式不正确
    chain = prompt | llm

    text = "《活着》是一本很好的书，我给它打 9 分。"

    print(f"输入: {text}\n")

    try:
        # 先尝试正常解析
        completion = chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        result = parser.parse(completion.content)
        print(f"解析成功: {result}")
    except Exception as e:
        print(f"初次解析失败: {str(e)[:100]}...")
        print("\n使用重试解析器...")

        # 使用重试解析器
        result = retry_parser.parse_with_prompt(
            completion.content,
            prompt.format(
                text=text,
                format_instructions=parser.get_format_instructions()
            )
        )
        print(f"重试解析成功: {result}")


def demo_parser_comparison():
    """示例8: 不同解析器对比"""
    print_section("示例8: 不同解析器对比")

    llm = init_llm()

    prompt_template = "列出 3 个著名的科学家"

    # 1. 不使用解析器
    print("【不使用解析器】")
    response = llm.invoke(prompt_template)
    print(f"类型: {type(response)}")
    print(f"内容: {response.content[:100]}...\n")

    # 2. 使用字符串解析器
    print("【字符串解析器】")
    chain_str = ChatPromptTemplate.from_template(prompt_template) | llm | StrOutputParser()
    result_str = chain_str.invoke({})
    print(f"类型: {type(result_str)}")
    print(f"内容: {result_str[:100]}...\n")

    # 3. 使用列表解析器
    print("【列表解析器】")
    list_parser = CommaSeparatedListOutputParser()
    chain_list = (
        ChatPromptTemplate.from_template(
            prompt_template + "\n\n{format_instructions}"
        )
        | llm
        | list_parser
    )
    result_list = chain_list.invoke({
        "format_instructions": list_parser.get_format_instructions()
    })
    print(f"类型: {type(result_list)}")
    print(f"内容: {result_list}\n")

    print("总结:")
    print("  - 不使用解析器: 返回 AIMessage 对象，需要手动访问 .content")
    print("  - 字符串解析器: 直接返回字符串，最简单")
    print("  - 列表解析器: 返回结构化的列表，便于后续处理")


def main():
    """运行所有示例"""
    try:
        demo_string_parser()
        demo_json_parser()
        demo_pydantic_parser()
        demo_list_parser()
        demo_structured_parser()
        demo_custom_parser()
        demo_parser_with_retry()
        demo_parser_comparison()

        print_section("所有示例执行完成")
        print("输出解析器可以将 LLM 的文本输出转换为结构化数据，")
        print("让你的应用能够更方便地处理和使用 AI 的输出！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
