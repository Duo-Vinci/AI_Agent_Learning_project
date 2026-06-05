"""
LangChain 基础教程 - 05: 回调系统详解

本模块演示：
1. 基本的回调处理器
2. 自定义回调处理器
3. 多个回调处理器
4. 回调中的错误处理
5. 性能监控回调
"""

import os
import time
from typing import Any, Dict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import (
    BaseCallbackHandler,
    StdOutCallbackHandler,
    StreamingStdOutCallbackHandler,
)
from langchain_core.outputs import LLMResult


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def init_llm(callbacks=None):
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
        callbacks=callbacks
    )


def demo_stdout_callback():
    """示例1: 标准输出回调"""
    print_section("示例1: 标准输出回调")

    # 使用标准输出回调
    llm = init_llm(callbacks=[StdOutCallbackHandler()])

    prompt = "请用一句话介绍 Python"
    print(f"提示: {prompt}\n")
    print("【回调信息】")

    response = llm.invoke(prompt)

    print(f"\n【最终结果】")
    print(response.content)


def demo_streaming_callback():
    """示例2: 流式输出回调"""
    print_section("示例2: 流式输出回调")

    # 使用流式输出回调
    llm = init_llm(callbacks=[StreamingStdOutCallbackHandler()])

    prompt = "请写一首关于编程的小诗（四句话）"
    print(f"提示: {prompt}\n")
    print("AI 回复（流式）:")

    llm.invoke(prompt)
    print("\n")


class LoggingCallbackHandler(BaseCallbackHandler):
    """自定义日志回调处理器"""

    def __init__(self):
        self.logs = []

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """LLM 开始时调用"""
        log = f"[LLM Start] 提示词数量: {len(prompts)}"
        self.logs.append(log)
        print(log)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """LLM 结束时调用"""
        log = f"[LLM End] 生成数量: {len(response.generations)}"
        self.logs.append(log)
        print(log)

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """LLM 出错时调用"""
        log = f"[LLM Error] {str(error)}"
        self.logs.append(log)
        print(log)

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Chain 开始时调用"""
        log = f"[Chain Start] 输入: {list(inputs.keys())}"
        self.logs.append(log)
        print(log)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Chain 结束时调用"""
        log = f"[Chain End] 输出: {list(outputs.keys())}"
        self.logs.append(log)
        print(log)


def demo_custom_callback():
    """示例3: 自定义回调处理器"""
    print_section("示例3: 自定义回调处理器")

    callback = LoggingCallbackHandler()
    llm = init_llm(callbacks=[callback])

    prompt = ChatPromptTemplate.from_template("用一句话介绍 {topic}")
    chain = prompt | llm

    print("执行 Chain...\n")
    result = chain.invoke({"topic": "机器学习"})

    print(f"\n【AI 回复】")
    print(result.content)

    print(f"\n【回调日志】")
    for log in callback.logs:
        print(f"  {log}")


class PerformanceCallbackHandler(BaseCallbackHandler):
    """性能监控回调处理器"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.token_count = 0

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """记录开始时间"""
        self.start_time = time.time()
        print(f"⏱️  开始时间: {time.strftime('%H:%M:%S')}")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """统计 token"""
        self.token_count += 1

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """记录结束时间并计算性能"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        print(f"⏱️  结束时间: {time.strftime('%H:%M:%S')}")
        print(f"⏱️  总耗时: {duration:.2f} 秒")

        if self.token_count > 0:
            print(f"📊 Token 数量: {self.token_count}")
            print(f"📊 平均速度: {self.token_count / duration:.2f} tokens/秒")


def demo_performance_callback():
    """示例4: 性能监控回调"""
    print_section("示例4: 性能监控回调")

    perf_callback = PerformanceCallbackHandler()

    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        temperature=0.7,
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        streaming=True,
        callbacks=[perf_callback]
    )

    prompt = "请列出学习数据科学的 5 个步骤"
    print(f"提示: {prompt}\n")

    response = llm.invoke(prompt)

    print(f"\n【AI 回复】")
    print(response.content)


class DetailedCallbackHandler(BaseCallbackHandler):
    """详细信息回调处理器"""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        print(f"\n🚀 LLM 启动")
        print(f"   提示词数量: {len(prompts)}")
        print(f"   第一个提示: {prompts[0][:100]}...")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        print(f"\n✅ LLM 完成")
        print(f"   生成数量: {len(response.generations)}")
        if response.llm_output:
            print(f"   Token 使用: {response.llm_output.get('token_usage', 'N/A')}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        print(f"\n⛓️  Chain 启动")
        print(f"   输入键: {list(inputs.keys())}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        print(f"\n✅ Chain 完成")
        print(f"   输出键: {list(outputs.keys())}")


def demo_multiple_callbacks():
    """示例5: 多个回调处理器"""
    print_section("示例5: 多个回调处理器")

    # 同时使用多个回调
    callbacks = [
        DetailedCallbackHandler(),
        PerformanceCallbackHandler()
    ]

    llm = init_llm(callbacks=callbacks)

    prompt = ChatPromptTemplate.from_template("用一句话介绍 {topic}")
    chain = prompt | llm

    result = chain.invoke({"topic": "深度学习"})

    print(f"\n【最终结果】")
    print(result.content)


class ErrorHandlingCallbackHandler(BaseCallbackHandler):
    """错误处理回调处理器"""

    def __init__(self):
        self.errors = []

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """捕获并记录错误"""
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "time": time.strftime("%H:%M:%S")
        }
        self.errors.append(error_info)
        print(f"\n❌ LLM 错误")
        print(f"   类型: {error_info['type']}")
        print(f"   消息: {error_info['message']}")
        print(f"   时间: {error_info['time']}")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """捕获并记录 Chain 错误"""
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "time": time.strftime("%H:%M:%S")
        }
        self.errors.append(error_info)
        print(f"\n❌ Chain 错误")
        print(f"   类型: {error_info['type']}")
        print(f"   消息: {error_info['message']}")
        print(f"   时间: {error_info['time']}")


def demo_error_callback():
    """示例6: 错误处理回调"""
    print_section("示例6: 错误处理回调")

    error_callback = ErrorHandlingCallbackHandler()

    # 故意使用错误的 API Key 来触发错误
    try:
        llm = ChatOpenAI(
            model="deepseek-v4-flash",
            temperature=0.7,
            api_key="invalid_key",
            base_url="https://api.deepseek.com/v1",
            callbacks=[error_callback]
        )

        llm.invoke("测试")
    except Exception as e:
        print(f"\n【异常被捕获】")
        print(f"异常类型: {type(e).__name__}")

    print(f"\n【错误记录】")
    print(f"记录的错误数量: {len(error_callback.errors)}")


class TokenCounterCallback(BaseCallbackHandler):
    """Token 计数回调"""

    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """提取 token 使用信息"""
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.total_tokens += usage.get("total_tokens", 0)
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)

    def print_summary(self):
        """打印统计信息"""
        print(f"\n📊 Token 使用统计")
        print(f"   提示 Token: {self.prompt_tokens}")
        print(f"   完成 Token: {self.completion_tokens}")
        print(f"   总 Token: {self.total_tokens}")


def demo_token_counter():
    """示例7: Token 计数器"""
    print_section("示例7: Token 计数器")

    token_counter = TokenCounterCallback()
    llm = init_llm(callbacks=[token_counter])

    prompts = [
        "什么是人工智能？",
        "什么是机器学习？",
        "什么是深度学习？"
    ]

    print("执行多个查询...\n")
    for prompt in prompts:
        print(f"提示: {prompt}")
        response = llm.invoke(prompt)
        print(f"回复: {response.content[:50]}...\n")

    token_counter.print_summary()


def main():
    """运行所有示例"""
    try:
        demo_stdout_callback()
        demo_streaming_callback()
        demo_custom_callback()
        demo_performance_callback()
        demo_multiple_callbacks()
        demo_error_callback()
        demo_token_counter()

        print_section("所有示例执行完成")
        print("回调系统让你能够监控和控制 LLM 的执行过程，")
        print("对于调试、性能优化和错误处理都非常有用！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
