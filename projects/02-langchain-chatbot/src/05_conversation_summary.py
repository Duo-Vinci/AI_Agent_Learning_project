"""
LangChain 聊天机器人 - 05: 对话摘要

本模块演示：
1. 对话自动摘要
2. 记忆压缩技术
3. 长对话处理
4. 摘要质量评估
5. 增量摘要生成
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate


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
        raise ValueError("未找到 API Key")

    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )


def demo_basic_summary():
    """示例1: 基本对话摘要"""
    print_section("示例1: 基本对话摘要")

    llm = init_llm()

    # 模拟长对话
    conversation_history = [
        ("用户", "你好，我想了解Python编程"),
        ("助手", "你好！Python是一门简单易学的编程语言。"),
        ("用户", "它有哪些优势？"),
        ("助手", "Python语法简洁、库丰富、应用广泛。"),
        ("用户", "适合初学者吗？"),
        ("助手", "非常适合，Python是最好的入门语言之一。"),
    ]

    print("原始对话:")
    for role, content in conversation_history:
        print(f"  {role}: {content}")

    # 生成摘要
    conversation_text = "\n".join([f"{role}: {content}" for role, content in conversation_history])

    summary_prompt = f"""请将以下对话总结成简短摘要（不超过50字）：

{conversation_text}

摘要："""

    response = llm.invoke([HumanMessage(content=summary_prompt)])
    print(f"\n对话摘要:\n{response.content}")


def demo_incremental_summary():
    """示例2: 增量摘要生成"""
    print_section("示例2: 增量摘要生成")

    class IncrementalSummarizer:
        """增量摘要生成器"""

        def __init__(self):
            self.llm = init_llm()
            self.current_summary = ""
            self.recent_messages = []
            self.summary_threshold = 4  # 每4条消息更新一次摘要

        def add_message(self, role: str, content: str):
            """添加消息"""
            self.recent_messages.append((role, content))

            if len(self.recent_messages) >= self.summary_threshold:
                self._update_summary()

        def _update_summary(self):
            """更新摘要"""
            # 构建新的对话片段
            new_conversation = "\n".join([
                f"{role}: {content}"
                for role, content in self.recent_messages
            ])

            # 生成新摘要
            if self.current_summary:
                prompt = f"""之前的摘要：{self.current_summary}

新的对话：
{new_conversation}

请更新摘要（不超过100字）："""
            else:
                prompt = f"""请总结以下对话（不超过100字）：

{new_conversation}

摘要："""

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                self.current_summary = response.content
                self.recent_messages = []
                print(f"\n[摘要已更新] {self.current_summary[:60]}...")
            except Exception as e:
                print(f"摘要更新失败: {e}")

        def get_summary(self) -> str:
            """获取当前摘要"""
            return self.current_summary

    summarizer = IncrementalSummarizer()

    print("增量摘要示例:\n")

    conversations = [
        ("用户", "我想学习机器学习"),
        ("助手", "机器学习是AI的重要分支"),
        ("用户", "需要什么基础？"),
        ("助手", "需要Python和数学基础"),
        ("用户", "有推荐的学习路径吗？"),
        ("助手", "建议先学Python，再学算法"),
        ("用户", "大概需要多久？"),
        ("助手", "认真学习大约3-6个月"),
    ]

    for i, (role, content) in enumerate(conversations, 1):
        print(f"[{i}] {role}: {content}")
        summarizer.add_message(role, content)

    print(f"\n\n最终摘要:\n{summarizer.get_summary()}")


def demo_summary_compression():
    """示例3: 记忆压缩"""
    print_section("示例3: 记忆压缩")

    class CompressedMemory:
        """压缩记忆管理器"""

        def __init__(self, compression_ratio: int = 10):
            self.llm = init_llm()
            self.compression_ratio = compression_ratio
            self.full_history = []
            self.compressed_summary = ""

        def add_exchange(self, user_msg: str, ai_msg: str):
            """添加一轮对话"""
            self.full_history.append(("用户", user_msg))
            self.full_history.append("助手", ai_msg))

            # 检查是否需要压缩
            if len(self.full_history) >= self.compression_ratio:
                self._compress()

        def _compress(self):
            """压缩历史"""
            # 将旧历史压缩成摘要
            old_history = self.full_history[:-4]  # 保留最近2轮
            self.full_history = self.full_history[-4:]

            if not old_history:
                return

            history_text = "\n".join([f"{role}: {content}" for role, content in old_history])

            prompt = f"""请压缩以下对话历史（保留关键信息）：

{history_text}

压缩后的摘要："""

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                if self.compressed_summary:
                    self.compressed_summary += " " + response.content
                else:
                    self.compressed_summary = response.content

                print(f"[已压缩] {len(old_history)}条消息 -> 摘要")
            except Exception as e:
                print(f"压缩失败: {e}")

        def get_context(self) -> str:
            """获取完整上下文"""
            context = []
            if self.compressed_summary:
                context.append(f"[历史摘要] {self.compressed_summary}")

            for role, content in self.full_history:
                context.append(f"{role}: {content}")

            return "\n".join(context)

    memory = CompressedMemory(compression_ratio=6)

    print("记忆压缩示例:\n")

    conversations = [
        ("介绍一下你自己", "我是AI助手"),
        ("你能做什么？", "我可以回答问题、提供帮助"),
        ("你会编程吗？", "我了解多种编程语言"),
        ("Python怎么样？", "Python很适合初学者"),
        ("现在的天气如何？", "抱歉我无法查询实时天气"),
        ("那你能查什么？", "我可以提供知识和建议"),
    ]

    for user_msg, ai_msg in conversations:
        print(f"用户: {user_msg}")
        print(f"助手: {ai_msg}\n")
        memory.add_exchange(user_msg, ai_msg)

    print("\n完整上下文:")
    print(memory.get_context())


def demo_long_conversation():
    """示例4: 长对话处理"""
    print_section("示例4: 长对话处理")

    class LongConversationHandler:
        """长对话处理器"""

        def __init__(self, max_recent_turns: int = 3):
            self.llm = init_llm()
            self.max_recent_turns = max_recent_turns
            self.summaries = []
            self.recent_messages = []

        def add_turn(self, user_msg: str, ai_msg: str):
            """添加一轮对话"""
            self.recent_messages.append(("用户", user_msg))
            self.recent_messages.append(("助手", ai_msg))

            # 检查是否需要生成摘要
            if len(self.recent_messages) > self.max_recent_turns * 2:
                self._create_summary()

        def _create_summary(self):
            """创建摘要"""
            # 将最旧的对话生成摘要
            to_summarize = self.recent_messages[:2]  # 最旧的一轮
            self.recent_messages = self.recent_messages[2:]

            text = "\n".join([f"{role}: {msg}" for role, msg in to_summarize])
            prompt = f"用一句话总结：{text}"

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                self.summaries.append(response.content)
            except Exception as e:
                print(f"摘要生成失败: {e}")

        def get_full_context(self) -> List[str]:
            """获取完整上下文"""
            context = []

            # 添加摘要
            if self.summaries:
                context.append("[历史摘要]")
                for i, summary in enumerate(self.summaries, 1):
                    context.append(f"  {i}. {summary}")

            # 添加近期对话
            if self.recent_messages:
                context.append("\n[近期对话]")
                for role, msg in self.recent_messages:
                    context.append(f"  {role}: {msg}")

            return context

    handler = LongConversationHandler(max_recent_turns=2)

    print("长对话处理示例:\n")

    conversations = [
        ("第1轮：介绍Python", "Python是一门编程语言"),
        ("第2轮：Python的特点", "简洁、易学、功能强大"),
        ("第3轮：如何开始学习", "从基础语法开始"),
        ("第4轮：推荐学习资源", "可以看官方文档"),
        ("第5轮：学习要多久", "看个人情况，一般3个月"),
    ]

    for user_msg, ai_msg in conversations:
        print(f"{user_msg}")
        handler.add_turn(user_msg, ai_msg)

    print("\n\n完整上下文:")
    for line in handler.get_full_context():
        print(line)


def demo_summary_quality():
    """示例5: 摘要质量评估"""
    print_section("示例5: 摘要质量评估")

    def evaluate_summary(original: str, summary: str) -> Dict[str, float]:
        """评估摘要质量"""
        llm = init_llm()

        eval_prompt = f"""评估以下摘要的质量（1-10分）：

原文：
{original}

摘要：
{summary}

请从以下维度评分：
1. 完整性（是否包含关键信息）
2. 简洁性（是否足够简洁）
3. 准确性（是否准确表达原意）

以JSON格式返回：{{"completeness": 分数, "conciseness": 分数, "accuracy": 分数}}
"""

        try:
            response = llm.invoke([HumanMessage(content=eval_prompt)])
            import json
            scores = json.loads(response.content)
            return scores
        except:
            return {"completeness": 0, "conciseness": 0, "accuracy": 0}

    original_conversation = """
    用户: 我想学习机器学习
    助手: 机器学习是人工智能的一个重要分支
    用户: 需要什么基础？
    助手: 需要Python编程和数学基础
    用户: 大概要学多久？
    助手: 认真学习大约需要3-6个月
    """

    summary = "用户想学机器学习，需要Python和数学基础，学习周期3-6个月。"

    print("原始对话:")
    print(original_conversation)
    print(f"\n摘要:\n{summary}")

    print("\n评估摘要质量...")
    scores = evaluate_summary(original_conversation, summary)

    print("\n质量评分:")
    for dimension, score in scores.items():
        print(f"  {dimension}: {score}/10")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 聊天机器人 - 对话摘要")
    print("="*70)

    try:
        demo_basic_summary()
        demo_incremental_summary()
        demo_summary_compression()
        demo_long_conversation()
        demo_summary_quality()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
