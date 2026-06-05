"""
LangChain 基础教程 - 07: 错误处理与重试机制

本模块演示：
1. 基本的错误处理
2. 自动重试机制
3. 超时处理
4. 降级策略（Fallback）
5. 错误日志记录
"""

import os
import time
from typing import Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


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


def demo_basic_error_handling():
    """示例1: 基本的错误处理"""
    print_section("示例1: 基本的错误处理")

    # 故意使用无效的 API Key
    llm = ChatOpenAI(
        model="deepseek-v4-flash",
        api_key="invalid_key_12345",
        base_url="https://api.deepseek.com/v1"
    )

    prompt = "你好"

    print("尝试使用无效的 API Key...\n")

    try:
        response = llm.invoke(prompt)
        print(f"成功: {response.content}")
    except Exception as e:
        print(f"❌ 捕获到错误:")
        print(f"   类型: {type(e).__name__}")
        print(f"   消息: {str(e)[:200]}")
        print(f"\n✓ 错误已被妥善处理，程序继续运行")


def demo_retry_mechanism():
    """示例2: 重试机制"""
    print_section("示例2: 重试机制")

    print("模拟不稳定的网络环境，实现重试机制\n")

    class RetryLLM:
        """带重试功能的 LLM 包装器"""

        def __init__(self, llm, max_retries=3, retry_delay=1):
            self.llm = llm
            self.max_retries = max_retries
            self.retry_delay = retry_delay

        def invoke(self, prompt: str) -> str:
            """带重试的调用"""
            for attempt in range(1, self.max_retries + 1):
                try:
                    print(f"尝试 {attempt}/{self.max_retries}...")
                    response = self.llm.invoke(prompt)
                    print(f"✓ 成功!\n")
                    return response.content
                except Exception as e:
                    print(f"✗ 失败: {type(e).__name__}")

                    if attempt < self.max_retries:
                        print(f"等待 {self.retry_delay} 秒后重试...\n")
                        time.sleep(self.retry_delay)
                    else:
                        print(f"❌ 达到最大重试次数，放弃")
                        raise

    # 使用正常的 LLM 进行测试
    llm = init_llm()
    retry_llm = RetryLLM(llm, max_retries=3, retry_delay=1)

    result = retry_llm.invoke("用一句话介绍 Python")
    print(f"最终结果: {result}")


def demo_timeout_handling():
    """示例3: 超时处理"""
    print_section("示例3: 超时处理")

    llm = init_llm()

    # 设置较短的超时时间
    llm_with_timeout = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        temperature=0.7,
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        request_timeout=5  # 5秒超时
    )

    prompt = "请写一篇关于人工智能的长文章"

    print(f"提示: {prompt}")
    print(f"超时设置: 5秒\n")

    try:
        start_time = time.time()
        response = llm_with_timeout.invoke(prompt)
        duration = time.time() - start_time

        print(f"✓ 成功完成 ({duration:.2f}秒)")
        print(f"回复长度: {len(response.content)} 字符")
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ 超时或错误 ({duration:.2f}秒)")
        print(f"错误: {type(e).__name__}")


def demo_fallback_strategy():
    """示例4: 降级策略"""
    print_section("示例4: 降级策略")

    # 主 LLM（可能失败）
    primary_llm = ChatOpenAI(
        model="gpt-4",
        api_key="invalid_key",  # 故意使用无效 key
        base_url="https://api.openai.com/v1"
    )

    # 备用 LLM
    fallback_llm = init_llm()

    prompt = ChatPromptTemplate.from_template("用一句话介绍 {topic}")

    # 创建带降级的 chain
    primary_chain = prompt | primary_llm
    fallback_chain = prompt | fallback_llm

    # 使用 with_fallbacks
    chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])

    print("尝试使用主模型（GPT-4），如果失败则降级到备用模型...\n")

    try:
        result = chain_with_fallback.invoke({"topic": "机器学习"})
        print(f"✓ 成功获得回复:")
        print(f"  {result.content}")
        print(f"\n（实际使用了备用模型）")
    except Exception as e:
        print(f"❌ 所有模型都失败了: {str(e)}")


def demo_multiple_fallbacks():
    """示例5: 多级降级"""
    print_section("示例5: 多级降级")

    print("设置多级降级策略: GPT-4 -> GPT-3.5 -> DeepSeek -> 默认回复\n")

    # 默认回复函数
    def default_response(input_dict: dict) -> dict:
        """当所有 LLM 都失败时的默认回复"""
        return {
            "content": "抱歉，服务暂时不可用，请稍后再试。"
        }

    # 尝试构建多级降级
    try:
        # 主模型（会失败）
        llm1 = ChatOpenAI(model="gpt-4", api_key="invalid1")

        # 备用模型1（会失败）
        llm2 = ChatOpenAI(model="gpt-3.5-turbo", api_key="invalid2")

        # 备用模型2（成功）
        llm3 = init_llm()

        # 默认回复
        default_chain = RunnableLambda(default_response)

        prompt = ChatPromptTemplate.from_template("{input}")

        # 构建多级降级链
        chain = (prompt | llm1).with_fallbacks([
            prompt | llm2,
            prompt | llm3,
            default_chain
        ])

        result = chain.invoke({"input": "你好"})

        print(f"✓ 获得回复: {result.content}")
        print(f"（使用了第3个备用方案）")

    except Exception as e:
        print(f"配置错误: {str(e)}")


def demo_error_logging():
    """示例6: 错误日志记录"""
    print_section("示例6: 错误日志记录")

    import logging

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    class LoggingLLM:
        """带日志记录的 LLM 包装器"""

        def __init__(self, llm, name="LLM"):
            self.llm = llm
            self.name = name
            self.success_count = 0
            self.error_count = 0

        def invoke(self, prompt: str):
            """带日志的调用"""
            try:
                logger.info(f"{self.name} - 开始调用")
                start_time = time.time()

                response = self.llm.invoke(prompt)

                duration = time.time() - start_time
                self.success_count += 1

                logger.info(
                    f"{self.name} - 成功 "
                    f"(耗时: {duration:.2f}秒, "
                    f"成功次数: {self.success_count})"
                )

                return response

            except Exception as e:
                self.error_count += 1

                logger.error(
                    f"{self.name} - 失败 "
                    f"(错误: {type(e).__name__}, "
                    f"失败次数: {self.error_count})"
                )

                raise

        def get_stats(self):
            """获取统计信息"""
            total = self.success_count + self.error_count
            success_rate = (
                self.success_count / total * 100 if total > 0 else 0
            )

            return {
                "success": self.success_count,
                "error": self.error_count,
                "total": total,
                "success_rate": success_rate
            }

    llm = init_llm()
    logging_llm = LoggingLLM(llm, name="DeepSeek")

    # 执行多次调用
    prompts = [
        "什么是Python?",
        "什么是Java?",
        "什么是JavaScript?"
    ]

    print("执行多次调用并记录日志...\n")

    for prompt in prompts:
        try:
            response = logging_llm.invoke(prompt)
            print(f"✓ {prompt} -> {response.content[:50]}...\n")
        except Exception as e:
            print(f"✗ {prompt} -> 失败\n")

    # 打印统计信息
    stats = logging_llm.get_stats()
    print(f"\n【统计信息】")
    print(f"  成功: {stats['success']}")
    print(f"  失败: {stats['error']}")
    print(f"  总计: {stats['total']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")


def demo_graceful_degradation():
    """示例7: 优雅降级"""
    print_section("示例7: 优雅降级")

    print("实现优雅降级：完整功能 -> 简化功能 -> 静态回复\n")

    llm = init_llm()

    def full_feature_response(topic: str) -> str:
        """完整功能：详细回答"""
        try:
            prompt = f"详细介绍 {topic}，包括定义、应用和未来发展（100字左右）"
            response = llm.invoke(prompt)
            return f"[完整回复] {response.content}"
        except Exception:
            raise

    def simplified_response(topic: str) -> str:
        """简化功能：简短回答"""
        try:
            prompt = f"用一句话介绍 {topic}"
            response = llm.invoke(prompt)
            return f"[简化回复] {response.content}"
        except Exception:
            raise

    def static_response(topic: str) -> str:
        """静态回复：预设答案"""
        responses = {
            "人工智能": "人工智能是计算机科学的一个分支，致力于创造智能机器。",
            "机器学习": "机器学习是人工智能的子领域，让计算机从数据中学习。",
        }
        return f"[静态回复] {responses.get(topic, f'关于{topic}的信息暂时不可用。')}"

    def smart_query(topic: str) -> str:
        """智能查询：自动降级"""
        # 尝试完整功能
        try:
            return full_feature_response(topic)
        except Exception as e:
            print(f"⚠️  完整功能失败: {type(e).__name__}")

        # 尝试简化功能
        try:
            return simplified_response(topic)
        except Exception as e:
            print(f"⚠️  简化功能失败: {type(e).__name__}")

        # 使用静态回复
        print(f"ℹ️  使用静态回复")
        return static_response(topic)

    # 测试
    topics = ["人工智能", "区块链"]

    for topic in topics:
        print(f"查询: {topic}")
        result = smart_query(topic)
        print(f"{result}\n")


def main():
    """运行所有示例"""
    try:
        demo_basic_error_handling()
        demo_retry_mechanism()
        demo_timeout_handling()
        demo_fallback_strategy()
        demo_multiple_fallbacks()
        demo_error_logging()
        demo_graceful_degradation()

        print_section("所有示例执行完成")
        print("完善的错误处理和重试机制是构建可靠 AI 应用的关键！")
        print("通过合理的降级策略，可以确保服务的高可用性。")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
