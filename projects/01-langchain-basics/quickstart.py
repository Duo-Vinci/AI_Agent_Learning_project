"""
LangChain 基础教程 - 快速开始

这是一个快速入门脚本，展示 LangChain 的核心功能。
运行这个文件即可快速体验 LangChain 的基本用法。
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main():
    """快速开始示例"""
    print("="*70)
    print("  LangChain 基础教程 - 快速开始")
    print("="*70)

    # 1. 加载环境变量
    print("\n[1] 加载配置...")
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 未找到 API Key")
        print("\n请按以下步骤配置:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 中填入你的 API Key")
        return

    print("✓ 配置加载成功")

    # 2. 初始化模型
    print("\n[2] 初始化 LLM...")
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        temperature=0.7,
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    )
    print("✓ LLM 初始化完成")

    # 3. 创建提示词模板
    print("\n[3] 创建提示词模板...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个乐于助人的AI助手。"),
        ("user", "{question}")
    ])
    print("✓ 提示词模板创建完成")

    # 4. 构建 Chain
    print("\n[4] 构建 Chain...")
    chain = prompt | llm | StrOutputParser()
    print("✓ Chain 构建完成")

    # 5. 执行查询
    print("\n[5] 执行查询...")
    questions = [
        "什么是LangChain？",
        "用一句话介绍Python",
        "列出3个机器学习的应用场景"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n问题{i}: {question}")
        print("回答: ", end="")

        # 流式输出
        for chunk in chain.stream({"question": question}):
            print(chunk, end="", flush=True)
        print("\n")

    print("="*70)
    print("  快速开始完成！")
    print("="*70)
    print("\n接下来你可以:")
    print("  1. 运行 src/01_prompt_templates.py 学习提示词模板")
    print("  2. 运行 src/02_chains.py 学习 Chain 构建")
    print("  3. 运行 src/03_streaming.py 学习流式输出")
    print("  4. 运行 src/04_output_parsers.py 学习输出解析")
    print("  5. 运行 src/05_callbacks.py 学习回调系统")
    print("  6. 运行 src/06_model_comparison.py 对比不同模型")
    print("  7. 运行 src/07_error_handling.py 学习错误处理")
    print("  8. 运行 src/08_complete_example.py 查看完整应用")


if __name__ == "__main__":
    main()
