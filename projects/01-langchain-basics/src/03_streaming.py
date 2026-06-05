"""
LangChain 基础教程 - 03: 流式输出详解

本模块演示：
1. 基本的流式输出
2. 流式输出的 token 计数
3. 流式输出与 Chain 结合
4. 流式输出的实时显示
5. 异步流式输出
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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
        base_url=api_base,
        streaming=True  # 启用流式输出
    )


def demo_basic_streaming():
    """示例1: 基本的流式输出"""
    print_section("示例1: 基本的流式输出")

    llm = init_llm()

    prompt = "请写一个关于人工智能的小故事（100字左右）"
    print(f"提示: {prompt}\n")
    print("AI 回复（流式）:")

    # 使用 stream 方法获取流式输出
    for chunk in llm.stream(prompt):
        print(chunk.content, end="", flush=True)

    print("\n")


def demo_streaming_with_chain():
    """示例2: 流式输出与 Chain 结合"""
    print_section("示例2: 流式输出与 Chain 结合")

    llm = init_llm()

    # 创建 Chain
    prompt = ChatPromptTemplate.from_template(
        "请用{language}语言介绍{topic}（50字左右）"
    )
    chain = prompt | llm | StrOutputParser()

    print(f"主题: 机器学习")
    print(f"语言: 中文\n")
    print("AI 回复（流式）:")

    # Chain 也支持流式输出
    for chunk in chain.stream({"topic": "机器学习", "language": "中文"}):
        print(chunk, end="", flush=True)

    print("\n")


def demo_streaming_with_callback():
    """示例3: 流式输出与回调函数"""
    print_section("示例3: 流式输出与回调函数")

    from langchain_core.callbacks import StreamingStdOutCallbackHandler

    # 创建带回调的 LLM
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        temperature=0.7,
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]  # 自动打印到标准输出
    )

    prompt = "请列出学习 Python 的 5 个理由"
    print(f"提示: {prompt}\n")
    print("AI 回复（使用回调）:")

    # 使用 invoke 而不是 stream，回调会自动处理流式输出
    response = llm.invoke(prompt)

    print("\n")


def demo_token_counting():
    """示例4: 统计流式输出的 token"""
    print_section("示例4: 统计流式输出的 token")

    llm = init_llm()

    prompt = "请用一段话介绍深度学习"
    print(f"提示: {prompt}\n")
    print("AI 回复:")

    token_count = 0
    full_response = ""

    for chunk in llm.stream(prompt):
        content = chunk.content
        print(content, end="", flush=True)
        full_response += content
        token_count += 1  # 简化的 token 计数（实际应使用 tiktoken）

    print(f"\n\n统计信息:")
    print(f"  总字符数: {len(full_response)}")
    print(f"  估计 token 数: {token_count}")


def demo_streaming_with_status():
    """示例5: 带状态提示的流式输出"""
    print_section("示例5: 带状态提示的流式输出")

    llm = init_llm()

    prompt = ChatPromptTemplate.from_template(
        "请列出{topic}的{count}个要点"
    )
    chain = prompt | llm | StrOutputParser()

    print("查询中...")

    start_time = __import__('time').time()
    response_started = False

    for chunk in chain.stream({"topic": "健康生活方式", "count": 5}):
        if not response_started:
            print(f"✓ 响应开始（耗时 {__import__('time').time() - start_time:.2f}秒）\n")
            print("AI 回复:")
            response_started = True
        print(chunk, end="", flush=True)

    end_time = __import__('time').time()
    print(f"\n\n✓ 响应完成（总耗时 {end_time - start_time:.2f}秒）")


async def demo_async_streaming():
    """示例6: 异步流式输出"""
    print_section("示例6: 异步流式输出")

    llm = init_llm()

    prompt = "请写一首关于春天的小诗（四句话）"
    print(f"提示: {prompt}\n")
    print("AI 回复（异步流式）:")

    # 使用 astream 进行异步流式输出
    async for chunk in llm.astream(prompt):
        print(chunk.content, end="", flush=True)
        await asyncio.sleep(0.01)  # 模拟异步处理

    print("\n")


async def demo_parallel_streaming():
    """示例7: 并行的多个流式输出"""
    print_section("示例7: 并行的多个流式输出")

    llm = init_llm()

    topics = ["春天", "夏天", "秋天"]

    async def stream_topic(topic: str):
        """为单个主题生成流式输出"""
        print(f"\n[{topic}] 开始生成...")
        prompt = f"用一句话描述{topic}的特点"
        result = ""
        async for chunk in llm.astream(prompt):
            result += chunk.content
        print(f"[{topic}] {result}")

    # 并行执行多个流式输出
    tasks = [stream_topic(topic) for topic in topics]
    await asyncio.gather(*tasks)


def demo_streaming_comparison():
    """示例8: 流式 vs 非流式对比"""
    print_section("示例8: 流式 vs 非流式对比")

    import time

    # 非流式输出
    llm_no_stream = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        temperature=0.7,
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        streaming=False
    )

    prompt = "请列出学习编程的 5 个建议（每个建议一句话）"

    # 测试非流式
    print("【非流式输出】")
    start = time.time()
    response = llm_no_stream.invoke(prompt)
    end = time.time()
    print(response.content)
    print(f"\n耗时: {end - start:.2f}秒")
    print("用户体验: 需要等待全部内容生成完毕才能看到\n")

    # 测试流式
    print("【流式输出】")
    llm_stream = init_llm()
    start = time.time()
    first_token_time = None

    for i, chunk in enumerate(llm_stream.stream(prompt)):
        if i == 0:
            first_token_time = time.time()
            print(f"首个 token 时间: {first_token_time - start:.2f}秒\n")
        print(chunk.content, end="", flush=True)

    end = time.time()
    print(f"\n\n总耗时: {end - start:.2f}秒")
    print("用户体验: 立即看到内容逐步生成，体验更流畅")


def main():
    """运行所有示例"""
    try:
        demo_basic_streaming()
        demo_streaming_with_chain()
        demo_streaming_with_callback()
        demo_token_counting()
        demo_streaming_with_status()

        # 运行异步示例
        print_section("异步示例")
        asyncio.run(demo_async_streaming())
        asyncio.run(demo_parallel_streaming())

        demo_streaming_comparison()

        print_section("所有示例执行完成")
        print("流式输出可以显著提升用户体验，")
        print("让用户能够立即看到 AI 的响应，而不是等待全部内容生成完毕！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
