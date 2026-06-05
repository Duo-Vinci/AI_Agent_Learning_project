"""
LangChain 聊天机器人 - 06: 流式聊天回复

本模块演示：
1. 流式输出基础
2. 打字机效果实现
3. 流式回调处理
4. 实时Token计数
5. 流式错误处理
"""

import os
import sys
import time
from typing import AsyncIterator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks import StreamingStdOutCallbackHandler, BaseCallbackHandler
from langchain_core.outputs import LLMResult


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def init_llm(streaming: bool = False, callbacks=None):
    """初始化大语言模型"""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise ValueError("未找到 API Key")

    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base,
        streaming=streaming,
        callbacks=callbacks
    )


def demo_basic_streaming():
    """示例1: 基本流式输出"""
    print_section("示例1: 基本流式输出")

    llm = init_llm(streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

    print("用户: 请介绍一下Python编程语言\n")
    print("AI: ", end="", flush=True)

    response = llm.invoke([HumanMessage(content="请用50字介绍Python编程语言")])

    print("\n\n流式输出完成！")


def demo_typewriter_effect():
    """示例2: 打字机效果"""
    print_section("示例2: 打字机效果")

    class TypewriterCallback(BaseCallbackHandler):
        """打字机效果回调"""

        def __init__(self, delay: float = 0.03):
            self.delay = delay
            self.tokens = []

        def on_llm_new_token(self, token: str, **kwargs):
            """处理新token"""
            sys.stdout.write(token)
            sys.stdout.flush()
            time.sleep(self.delay)
            self.tokens.append(token)

        def on_llm_end(self, response: LLMResult, **kwargs):
            """LLM结束"""
            print()  # 换行

    llm = init_llm(streaming=True, callbacks=[TypewriterCallback(delay=0.05)])

    print("用户: 讲一个短故事\n")
    print("AI: ", end="", flush=True)

    llm.invoke([HumanMessage(content="用30字讲一个关于友谊的短故事")])

    print("\n打字机效果演示完成！")


def demo_token_counter():
    """示例3: 实时Token计数"""
    print_section("示例3: 实时Token计数")

    class TokenCounterCallback(BaseCallbackHandler):
        """Token计数回调"""

        def __init__(self):
            self.token_count = 0
            self.tokens = []

        def on_llm_new_token(self, token: str, **kwargs):
            """计数新token"""
            self.token_count += 1
            self.tokens.append(token)
            sys.stdout.write(token)
            sys.stdout.flush()

        def on_llm_end(self, response: LLMResult, **kwargs):
            """显示统计"""
            print(f"\n\n[统计] 生成了 {self.token_count} 个tokens")
            print(f"[统计] 平均token长度: {sum(len(t) for t in self.tokens) / len(self.tokens):.2f} 字符")

    counter_callback = TokenCounterCallback()
    llm = init_llm(streaming=True, callbacks=[counter_callback])

    print("用户: 解释什么是机器学习\n")
    print("AI: ", end="", flush=True)

    llm.invoke([HumanMessage(content="用一段话解释什么是机器学习")])


def demo_streaming_chat():
    """示例4: 流式聊天机器人"""
    print_section("示例4: 流式聊天机器人")

    class StreamingChatbot:
        """流式聊天机器人"""

        def __init__(self):
            self.callback = StreamingStdOutCallbackHandler()
            self.llm = init_llm(streaming=True, callbacks=[self.callback])
            self.messages = [
                SystemMessage(content="你是一个友好的助手。")
            ]

        def chat(self, user_input: str):
            """进行对话"""
            print(f"\n用户: {user_input}")
            print("AI: ", end="", flush=True)

            self.messages.append(HumanMessage(content=user_input))
            response = self.llm.invoke(self.messages)
            self.messages.append(AIMessage(content=response.content))

            print()  # 换行

    chatbot = StreamingChatbot()

    conversations = [
        "你好！",
        "你能做什么？",
        "给我讲个笑话"
    ]

    for user_input in conversations:
        chatbot.chat(user_input)
        time.sleep(0.5)  # 模拟思考时间


def demo_custom_streaming():
    """示例5: 自定义流式处理"""
    print_section("示例5: 自定义流式处理")

    class CustomStreamHandler(BaseCallbackHandler):
        """自定义流式处理器"""

        def __init__(self):
            self.current_text = ""
            self.word_count = 0
            self.start_time = None

        def on_llm_start(self, serialized, prompts, **kwargs):
            """LLM开始"""
            self.start_time = time.time()
            print("[开始生成]")

        def on_llm_new_token(self, token: str, **kwargs):
            """处理新token"""
            self.current_text += token

            # 计算词数
            if token.strip():
                self.word_count += 1

            # 显示进度
            if self.word_count % 10 == 0:
                elapsed = time.time() - self.start_time
                speed = self.word_count / elapsed if elapsed > 0 else 0
                print(f"\r[进度] {self.word_count} tokens | {speed:.1f} tokens/s", end="", flush=True)

        def on_llm_end(self, response: LLMResult, **kwargs):
            """LLM结束"""
            elapsed = time.time() - self.start_time
            print(f"\n\n[完成] 总计 {self.word_count} tokens，耗时 {elapsed:.2f}秒")
            print(f"\n生成的文本:\n{self.current_text}")

    handler = CustomStreamHandler()
    llm = init_llm(streaming=True, callbacks=[handler])

    print("用户: 介绍人工智能的应用领域\n")

    llm.invoke([HumanMessage(content="用一段话介绍人工智能的应用领域")])


def demo_stream_with_context():
    """示例6: 带上下文的流式输出"""
    print_section("示例6: 带上下文的流式输出")

    class ContextualStreamChatbot:
        """带上下文的流式聊天机器人"""

        def __init__(self, max_history: int = 5):
            self.max_history = max_history
            self.messages = [
                SystemMessage(content="你是一个记忆力很好的助手。")
            ]
            self.callback = StreamingStdOutCallbackHandler()
            self.llm = init_llm(streaming=True, callbacks=[self.callback])

        def chat(self, user_input: str) -> str:
            """进行对话"""
            # 添加用户消息
            self.messages.append(HumanMessage(content=user_input))

            # 限制历史长度
            if len(self.messages) > self.max_history * 2 + 1:
                # 保留系统消息和最近的对话
                self.messages = [self.messages[0]] + self.messages[-(self.max_history * 2):]

            # 流式生成回复
            print(f"\n用户: {user_input}")
            print(f"AI ({len(self.messages)//2}轮): ", end="", flush=True)

            response = self.llm.invoke(self.messages)
            self.messages.append(AIMessage(content=response.content))

            print()  # 换行
            return response.content

    chatbot = ContextualStreamChatbot(max_history=3)

    conversations = [
        "我叫Alice",
        "我喜欢编程",
        "我最喜欢Python",
        "我的名字是什么？我喜欢什么？"
    ]

    for user_input in conversations:
        chatbot.chat(user_input)
        time.sleep(0.3)


def demo_error_handling():
    """示例7: 流式错误处理"""
    print_section("示例7: 流式错误处理")

    class ErrorHandlingCallback(BaseCallbackHandler):
        """错误处理回调"""

        def __init__(self):
            self.error_occurred = False
            self.accumulated_text = ""

        def on_llm_new_token(self, token: str, **kwargs):
            """处理token"""
            try:
                self.accumulated_text += token
                sys.stdout.write(token)
                sys.stdout.flush()
            except Exception as e:
                self.error_occurred = True
                print(f"\n[错误] Token处理失败: {e}")

        def on_llm_error(self, error: Exception, **kwargs):
            """处理LLM错误"""
            print(f"\n[LLM错误] {error}")
            self.error_occurred = True

        def on_llm_end(self, response: LLMResult, **kwargs):
            """结束处理"""
            if not self.error_occurred:
                print("\n[成功] 流式输出完成")
            else:
                print("\n[警告] 输出过程中出现错误")

    callback = ErrorHandlingCallback()
    llm = init_llm(streaming=True, callbacks=[callback])

    print("测试正常流式输出:\n")
    print("AI: ", end="", flush=True)

    try:
        llm.invoke([HumanMessage(content="说一句话")])
    except Exception as e:
        print(f"\n异常捕获: {e}")


def demo_multi_callback():
    """示例8: 多个回调组合"""
    print_section("示例8: 多个回调组合")

    class LogCallback(BaseCallbackHandler):
        """日志回调"""

        def __init__(self):
            self.logs = []

        def on_llm_start(self, serialized, prompts, **kwargs):
            self.logs.append(("START", time.time()))

        def on_llm_new_token(self, token: str, **kwargs):
            self.logs.append(("TOKEN", token))

        def on_llm_end(self, response: LLMResult, **kwargs):
            self.logs.append(("END", time.time()))

        def print_logs(self):
            print("\n\n[日志记录]")
            start_time = self.logs[0][1] if self.logs else 0
            end_time = self.logs[-1][1] if self.logs else 0
            token_count = sum(1 for event, _ in self.logs if event == "TOKEN")
            print(f"  开始时间: {start_time}")
            print(f"  结束时间: {end_time}")
            print(f"  耗时: {end_time - start_time:.2f}秒")
            print(f"  Token数: {token_count}")

    # 组合多个回调
    display_callback = StreamingStdOutCallbackHandler()
    log_callback = LogCallback()

    llm = init_llm(streaming=True, callbacks=[display_callback, log_callback])

    print("用户: 介绍Python\n")
    print("AI: ", end="", flush=True)

    llm.invoke([HumanMessage(content="用一句话介绍Python")])

    log_callback.print_logs()


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 流式聊天回复")
    print("="*70)

    try:
        demo_basic_streaming()
        demo_typewriter_effect()
        demo_token_counter()
        demo_streaming_chat()
        demo_custom_streaming()
        demo_stream_with_context()
        demo_error_handling()
        demo_multi_callback()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
