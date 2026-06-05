"""
Agent记忆系统

Agent记忆系统是让Agent能够记住历史交互和知识的关键组件。
完善的记忆系统可以让Agent进行更自然、更智能的多轮对话。

记忆类型：
1. 短期记忆（工作记忆）：当前对话上下文
2. 长期记忆：跨会话的持久化知识
3. 向量记忆：基于向量检索的知识库
4. 实体记忆：关于特定实体的结构化信息

适用场景：
- 多轮对话系统
- 个性化助手
- 知识积累型应用
- 上下文感知的任务处理
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    ConversationTokenBufferMemory,
    VectorStoreRetrieverMemory
)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# ============ 工具定义 ============

@tool
def save_fact(fact: str) -> str:
    """
    保存一个事实到知识库

    Args:
        fact: 要保存的事实

    Returns:
        保存结果
    """
    # 这里简化处理，实际应该保存到数据库
    return f"✅ 已保存事实: {fact}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============ 示例函数 ============

def example_1_conversation_buffer_memory():
    """示例1: 对话缓冲记忆"""
    print("\n" + "="*60)
    print("示例1: ConversationBufferMemory - 完整对话历史")
    print("="*60)

    print("\n💡 说明:")
    print("ConversationBufferMemory保存完整的对话历史")
    print("适合短对话，但会消耗较多tokens\n")

    # 初始化记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False
    )

    # 模拟对话
    conversations = [
        ("human", "我叫张三"),
        ("ai", "你好张三！很高兴认识你。"),
        ("human", "我今年25岁"),
        ("ai", "知道了，你25岁。"),
        ("human", "我叫什么名字？"),
    ]

    # 添加对话历史
    for role, message in conversations[:-1]:
        if role == "human":
            memory.chat_memory.add_user_message(message)
        else:
            memory.chat_memory.add_ai_message(message)

    # 检查记忆
    print("💾 当前记忆内容:")
    print(memory.load_memory_variables({})['chat_history'])

    print("\n✅ 优点: 保留完整上下文，准确度高")
    print("⚠️  缺点: 长对话会消耗大量tokens")


def example_2_conversation_window_memory():
    """示例2: 窗口记忆"""
    print("\n" + "="*60)
    print("示例2: ConversationBufferWindowMemory - 窗口记忆")
    print("="*60)

    print("\n💡 说明:")
    print("只保留最近N轮对话，节省tokens\n")

    # 初始化记忆（只保留最近2轮）
    memory = ConversationBufferWindowMemory(
        k=2,  # 保留最近2轮对话
        memory_key="chat_history",
        return_messages=False
    )

    # 模拟5轮对话
    conversations = [
        ("我在北京工作", "好的，知道了。"),
        ("我是软件工程师", "明白，你是工程师。"),
        ("我喜欢Python", "Python确实很棒。"),
        ("我在哪里工作？", ""),  # 测试：应该记不住了
    ]

    for i, (user_msg, ai_msg) in enumerate(conversations[:-1], 1):
        memory.chat_memory.add_user_message(user_msg)
        if ai_msg:
            memory.chat_memory.add_ai_message(ai_msg)
        print(f"第{i}轮对话已添加")

    print("\n💾 当前记忆内容（只保留最近2轮）:")
    print(memory.load_memory_variables({})['chat_history'])

    print("\n✅ 优点: 节省tokens，控制成本")
    print("⚠️  缺点: 会忘记早期的对话")


def example_3_conversation_summary_memory():
    """示例3: 摘要记忆"""
    print("\n" + "="*60)
    print("示例3: ConversationSummaryMemory - 摘要记忆")
    print("="*60)

    print("\n💡 说明:")
    print("将对话历史压缩为摘要，大幅节省tokens")
    print("适合长对话场景\n")

    # 初始化LLM和记忆
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    memory = ConversationSummaryMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=False
    )

    # 模拟对话
    print("模拟对话场景...")
    memory.chat_memory.add_user_message("我叫李四，今年30岁，住在上海")
    memory.chat_memory.add_ai_message("你好李四！")
    memory.chat_memory.add_user_message("我是一名数据科学家，喜欢机器学习")
    memory.chat_memory.add_ai_message("很高兴认识你！")

    # 生成摘要
    try:
        summary = memory.load_memory_variables({})['chat_history']
        print(f"\n💾 对话摘要:\n{summary}")

        print("\n✅ 优点: 大幅节省tokens，适合长对话")
        print("⚠️  缺点: 可能丢失细节，需要额外LLM调用")
    except Exception as e:
        print(f"⚠️  摘要生成失败（需要API Key）: {e}")


def example_4_token_buffer_memory():
    """示例4: Token限制记忆"""
    print("\n" + "="*60)
    print("示例4: ConversationTokenBufferMemory - Token限制")
    print("="*60)

    print("\n💡 说明:")
    print("根据Token数量限制记忆大小")
    print("自动截断超出限制的对话\n")

    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        memory = ConversationTokenBufferMemory(
            llm=llm,
            max_token_limit=100,  # 最多100个tokens
            memory_key="chat_history",
            return_messages=False
        )

        # 添加对话
        memory.chat_memory.add_user_message("这是一段很长的对话内容，用于测试token限制功能。")
        memory.chat_memory.add_ai_message("我明白了。")
        memory.chat_memory.add_user_message("继续添加更多内容来触发token限制。")
        memory.chat_memory.add_ai_message("好的。")

        print("💾 记忆内容（自动截断）:")
        print(memory.load_memory_variables({})['chat_history'])

        print("\n✅ 优点: 精确控制token使用")
        print("⚠️  缺点: 需要LLM计算tokens")
    except Exception as e:
        print(f"⚠️  需要API Key: {e}")


def example_5_vector_store_memory():
    """示例5: 向量存储记忆"""
    print("\n" + "="*60)
    print("示例5: VectorStoreRetrieverMemory - 向量记忆")
    print("="*60)

    print("\n💡 说明:")
    print("使用向量相似度检索相关记忆")
    print("适合大规模知识库场景\n")

    try:
        # 初始化Embedding模型
        print("初始化向量存储...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 创建向量存储
        texts = [
            "我喜欢吃披萨",
            "我的生日是5月10日",
            "我在北京工作",
            "我的爱好是摄影",
        ]

        vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=embeddings
        )

        # 创建向量记忆
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        memory = VectorStoreRetrieverMemory(retriever=retriever)

        # 保存新记忆
        memory.save_context(
            {"input": "我喜欢什么运动？"},
            {"output": "你喜欢打篮球"}
        )

        # 检索相关记忆
        query = "我的爱好是什么？"
        relevant_memories = memory.load_memory_variables({"prompt": query})

        print(f"查询: {query}")
        print(f"相关记忆: {relevant_memories}")

        print("\n✅ 优点: 智能检索，适合大规模知识")
        print("⚠️  缺点: 需要Embedding模型，略慢")
    except Exception as e:
        print(f"⚠️  初始化失败: {e}")


def example_6_entity_memory():
    """示例6: 实体记忆"""
    print("\n" + "="*60)
    print("示例6: Entity Memory - 实体记忆")
    print("="*60)

    print("\n💡 说明:")
    print("EntityMemory专注于记住特定实体（人、地点、事物）的信息\n")

    # 模拟实体记忆结构
    entity_memory = {
        "张三": {
            "name": "张三",
            "age": 25,
            "city": "北京",
            "job": "工程师",
            "last_updated": datetime.now()
        },
        "Python": {
            "type": "编程语言",
            "creator": "Guido van Rossum",
            "year": 1991
        }
    }

    print("💾 实体记忆库:")
    for entity, info in entity_memory.items():
        print(f"\n实体: {entity}")
        for key, value in info.items():
            if key != "last_updated":
                print(f"  {key}: {value}")

    print("\n✅ 优点: 结构化信息，易于查询")
    print("⚠️  缺点: 需要实体识别")


def example_7_memory_strategies():
    """示例7: 记忆策略选择"""
    print("\n" + "="*60)
    print("示例7: 如何选择记忆策略")
    print("="*60)

    print("\n📌 记忆策略对比:\n")

    strategies = {
        "ConversationBufferMemory": {
            "适用": "短对话（<10轮）",
            "优点": "完整上下文",
            "缺点": "消耗tokens多",
            "成本": "💰💰💰"
        },
        "ConversationWindowMemory": {
            "适用": "中等对话",
            "优点": "控制成本",
            "缺点": "丢失早期信息",
            "成本": "💰💰"
        },
        "ConversationSummaryMemory": {
            "适用": "长对话",
            "优点": "大幅节省tokens",
            "缺点": "可能丢失细节",
            "成本": "💰"
        },
        "VectorStoreMemory": {
            "适用": "知识库型应用",
            "优点": "智能检索",
            "缺点": "需要向量模型",
            "成本": "💰💰"
        },
    }

    for name, info in strategies.items():
        print(f"{name}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()

    print("💡 选择建议:")
    print("1. 客服机器人: WindowMemory（k=5）")
    print("2. 个人助手: SummaryMemory")
    print("3. 知识问答: VectorStoreMemory")
    print("4. 简单对话: BufferMemory")


def example_8_memory_best_practices():
    """示例8: 记忆系统最佳实践"""
    print("\n" + "="*60)
    print("示例8: 记忆系统最佳实践")
    print("="*60)

    print("\n📚 最佳实践:\n")

    print("1. 记忆管理")
    print("   - 定期清理过期记忆")
    print("   - 设置记忆上限")
    print("   - 压缩历史对话")
    print()

    print("2. 性能优化")
    print("   - 使用合适的记忆类型")
    print("   - 异步处理摘要生成")
    print("   - 缓存向量结果")
    print()

    print("3. 数据安全")
    print("   - 加密敏感信息")
    print("   - 实现访问控制")
    print("   - 定期备份记忆数据")
    print()

    print("4. 用户体验")
    print("   - 提供记忆清除功能")
    print("   - 显示记忆状态")
    print("   - 支持记忆导入导出")
    print()

    print("5. 混合策略")
    print("   - 短期用WindowMemory")
    print("   - 长期用SummaryMemory")
    print("   - 知识库用VectorMemory")
    print("   - 根据场景动态切换")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*18 + "Agent记忆系统教程")
    print("="*60)

    # 运行示例
    example_1_conversation_buffer_memory()
    example_2_conversation_window_memory()
    example_3_conversation_summary_memory()
    example_4_token_buffer_memory()
    example_5_vector_store_memory()
    example_6_entity_memory()
    example_7_memory_strategies()
    example_8_memory_best_practices()

    print("\n" + "="*60)
    print("✅ 教程完成")
    print("="*60)
    print("\n💡 关键要点:")
    print("- 根据场景选择合适的记忆类型")
    print("- 平衡记忆完整性和成本")
    print("- 实现记忆管理和优化策略")
    print("- 注意数据安全和用户隐私")
