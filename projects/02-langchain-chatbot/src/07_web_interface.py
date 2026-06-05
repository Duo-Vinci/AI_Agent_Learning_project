"""
Web聊天界面

这个模块展示了如何为聊天机器人创建Web界面：
1. Streamlit基础聊天界面
2. 会话状态管理
3. 流式响应显示
4. 对话历史展示
5. 界面样式定制
6. 清除历史功能
7. 完整的Web聊天应用
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage

# 加载环境变量
load_dotenv()


# ==================== 示例1: Streamlit流式回调处理器 ====================
class StreamlitCallbackHandler(BaseCallbackHandler):
    """
    自定义回调处理器，用于在Streamlit中显示流式响应

    这个处理器会实时更新Streamlit的UI，展示模型生成的token
    """

    def __init__(self, container):
        """
        初始化回调处理器

        Args:
            container: Streamlit容器，用于显示流式内容
        """
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        当接收到新token时调用

        Args:
            token: 新生成的token
        """
        self.text += token
        self.container.markdown(self.text)


def example_streamlit_callback():
    """示例1: 演示Streamlit流式回调处理器的基本用法"""
    print("=== 示例1: Streamlit流式回调处理器 ===")
    print("这个示例需要在Streamlit应用中运行")
    print("回调处理器会实时更新UI，展示生成的文本\n")


# ==================== 示例2: 基础会话状态管理 ====================
def initialize_session_state():
    """
    初始化Streamlit会话状态

    会话状态用于在页面刷新之间保持数据
    """
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 初始化对话链
    if "conversation" not in st.session_state:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            streaming=True
        )

        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history"
        )

        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=False
        )

    # 初始化其他状态
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0


def example_session_state():
    """示例2: 演示会话状态管理的基本概念"""
    print("=== 示例2: 会话状态管理 ===")
    print("会话状态管理的关键点：")
    print("1. messages: 存储聊天历史")
    print("2. conversation: 存储对话链实例")
    print("3. total_tokens: 跟踪token使用量")
    print("4. 使用st.session_state在页面刷新间保持数据\n")


# ==================== 示例3: 简单的Streamlit聊天界面 ====================
def create_simple_chat_interface():
    """
    创建一个简单的Streamlit聊天界面

    这是最基础的聊天界面实现
    """
    st.title("💬 简单聊天机器人")

    # 初始化会话状态
    initialize_session_state()

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 聊天输入
    if prompt := st.chat_input("请输入您的消息..."):
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成助手响应
        with st.chat_message("assistant"):
            response_container = st.empty()

            # 调用对话链
            response = st.session_state.conversation.predict(input=prompt)
            response_container.markdown(response)

            # 添加助手消息
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })


def example_simple_chat_interface():
    """示例3: 演示简单聊天界面的结构"""
    print("=== 示例3: 简单聊天界面 ===")
    print("界面组件：")
    print("1. st.title(): 页面标题")
    print("2. st.chat_message(): 聊天消息容器")
    print("3. st.chat_input(): 用户输入框")
    print("4. st.empty(): 用于流式更新的占位符\n")


# ==================== 示例4: 带流式响应的聊天界面 ====================
def create_streaming_chat_interface():
    """
    创建带流式响应的聊天界面

    实时显示模型生成的内容，提升用户体验
    """
    st.title("⚡ 流式聊天机器人")

    # 侧边栏设置
    with st.sidebar:
        st.header("⚙️ 设置")
        temperature = st.slider(
            "温度",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1
        )

        max_tokens = st.slider(
            "最大Token数",
            min_value=100,
            max_value=2000,
            value=500,
            step=100
        )

        if st.button("🗑️ 清除历史"):
            st.session_state.messages = []
            st.session_state.conversation.memory.clear()
            st.rerun()

    # 初始化会话状态
    initialize_session_state()

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 聊天输入
    if prompt := st.chat_input("请输入您的消息..."):
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成助手响应（流式）
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""

            # 使用流式回调
            for chunk in st.session_state.conversation.llm.stream(prompt):
                full_response += chunk.content
                response_container.markdown(full_response + "▌")

            response_container.markdown(full_response)

            # 添加助手消息
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })


def example_streaming_chat_interface():
    """示例4: 演示流式响应聊天界面的特点"""
    print("=== 示例4: 流式响应聊天界面 ===")
    print("流式响应的优势：")
    print("1. 实时显示生成内容")
    print("2. 降低用户等待感")
    print("3. 提升用户体验")
    print("4. 显示光标动画(▌)表示正在生成\n")


# ==================== 示例5: 美化的聊天界面 ====================
def create_styled_chat_interface():
    """
    创建美化的聊天界面

    添加自定义样式和更多交互元素
    """
    # 自定义CSS
    st.markdown("""
        <style>
        .main {
            background-color: #f5f5f5;
        }
        .stChatMessage {
            background-color: white;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stats-box {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.markdown("""
        <div class="chat-header">
            <h1>🤖 智能对话助手</h1>
            <p>基于GPT-3.5的智能聊天机器人</p>
        </div>
    """, unsafe_allow_html=True)

    # 侧边栏
    with st.sidebar:
        st.header("📊 统计信息")

        # 显示统计
        if "messages" in st.session_state:
            message_count = len(st.session_state.messages)
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("总消息数", message_count)
            with col2:
                st.metric("对话轮数", user_messages)

        st.divider()

        st.header("⚙️ 模型设置")

        model = st.selectbox(
            "选择模型",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        )

        temperature = st.slider(
            "创造性 (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="较低的值使输出更确定，较高的值使输出更随机"
        )

        st.divider()

        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 清除历史", use_container_width=True):
                st.session_state.messages = []
                if "conversation" in st.session_state:
                    st.session_state.conversation.memory.clear()
                st.rerun()

        with col2:
            if st.button("💾 导出对话", use_container_width=True):
                st.info("导出功能开发中...")

    # 初始化会话状态
    initialize_session_state()

    # 主聊天区域
    chat_container = st.container()

    with chat_container:
        # 显示欢迎消息
        if len(st.session_state.messages) == 0:
            st.info("👋 您好！我是您的AI助手，有什么可以帮您的吗？")

        # 显示聊天历史
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # 显示时间戳
                if "timestamp" in message:
                    st.caption(f"🕐 {message['timestamp']}")

    # 聊天输入
    if prompt := st.chat_input("💭 输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 生成助手响应
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = st.session_state.conversation.predict(input=prompt)
                st.markdown(response)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"🕐 {timestamp}")

                # 添加助手消息
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": timestamp
                })


def example_styled_chat_interface():
    """示例5: 演示美化聊天界面的特点"""
    print("=== 示例5: 美化的聊天界面 ===")
    print("美化要素：")
    print("1. 自定义CSS样式")
    print("2. 渐变色标题")
    print("3. 统计信息展示")
    print("4. 模型参数设置")
    print("5. 时间戳显示")
    print("6. 图标和表情符号\n")


# ==================== 示例6: 多功能聊天界面 ====================
def create_advanced_chat_interface():
    """
    创建多功能聊天界面

    集成更多高级功能
    """
    # 页面配置
    st.set_page_config(
        page_title="AI聊天助手",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 标题
    st.title("🤖 高级AI聊天助手")
    st.markdown("---")

    # 侧边栏
    with st.sidebar:
        st.header("🎯 功能选择")

        mode = st.radio(
            "选择模式",
            ["💬 普通对话", "📝 文本生成", "🔍 问答助手", "💡 创意写作"]
        )

        st.divider()

        st.header("⚙️ 高级设置")

        # 模型设置
        with st.expander("🤖 模型配置", expanded=False):
            model = st.selectbox("模型", ["gpt-3.5-turbo", "gpt-4"])
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
            max_tokens = st.slider("Max Tokens", 100, 2000, 500, 100)

        # 记忆设置
        with st.expander("🧠 记忆配置", expanded=False):
            memory_type = st.selectbox(
                "记忆类型",
                ["缓冲记忆", "摘要记忆", "窗口记忆"]
            )

            if memory_type == "窗口记忆":
                window_size = st.slider("窗口大小", 1, 10, 5)

        # 显示设置
        with st.expander("🎨 显示设置", expanded=False):
            show_timestamp = st.checkbox("显示时间戳", value=True)
            show_tokens = st.checkbox("显示Token统计", value=True)
            enable_streaming = st.checkbox("启用流式响应", value=True)

        st.divider()

        # 操作按钮
        st.header("🔧 操作")

        if st.button("🗑️ 清除历史", use_container_width=True):
            st.session_state.messages = []
            if "conversation" in st.session_state:
                st.session_state.conversation.memory.clear()
            st.success("历史已清除！")
            st.rerun()

        if st.button("💾 导出对话", use_container_width=True):
            if "messages" in st.session_state and st.session_state.messages:
                # 生成导出内容
                export_text = "\n\n".join([
                    f"{m['role'].upper()}: {m['content']}"
                    for m in st.session_state.messages
                ])
                st.download_button(
                    label="📥 下载对话记录",
                    data=export_text,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("暂无对话记录")

        if st.button("🔄 重新开始", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()

        # 统计信息
        st.header("📊 统计")
        if "messages" in st.session_state and st.session_state.messages:
            stats_col1, stats_col2 = st.columns(2)
            with stats_col1:
                st.metric("消息数", len(st.session_state.messages))
            with stats_col2:
                user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
                st.metric("对话轮", user_count)

    # 初始化会话状态
    initialize_session_state()

    # 主聊天区域
    tabs = st.tabs(["💬 聊天", "📜 历史", "ℹ️ 帮助"])

    with tabs[0]:  # 聊天标签
        # 显示模式提示
        st.info(f"当前模式: {mode}")

        # 聊天容器
        chat_container = st.container()

        with chat_container:
            # 显示聊天历史
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

                    # 显示元信息
                    if show_timestamp and "timestamp" in message:
                        st.caption(f"⏰ {message['timestamp']}")

        # 聊天输入
        if prompt := st.chat_input("请输入您的消息..."):
            # 添加用户消息
            user_message = {
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.messages.append(user_message)

            with st.chat_message("user"):
                st.markdown(prompt)
                if show_timestamp:
                    st.caption(f"⏰ {user_message['timestamp']}")

            # 生成助手响应
            with st.chat_message("assistant"):
                with st.spinner("正在思考..."):
                    response = st.session_state.conversation.predict(input=prompt)
                    st.markdown(response)

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if show_timestamp:
                        st.caption(f"⏰ {timestamp}")

                    # 添加助手消息
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": timestamp
                    })

    with tabs[1]:  # 历史标签
        st.subheader("📜 对话历史")

        if "messages" in st.session_state and st.session_state.messages:
            for idx, message in enumerate(st.session_state.messages):
                with st.expander(f"{message['role'].upper()} - {message.get('timestamp', 'N/A')}"):
                    st.write(message["content"])
        else:
            st.info("暂无对话历史")

    with tabs[2]:  # 帮助标签
        st.subheader("ℹ️ 使用帮助")

        st.markdown("""
        ### 功能说明

        #### 💬 普通对话
        - 自由对话模式
        - 适合日常问答

        #### 📝 文本生成
        - 生成文章、邮件等
        - 支持长文本输出

        #### 🔍 问答助手
        - 专注于回答问题
        - 提供详细解释

        #### 💡 创意写作
        - 故事创作
        - 诗歌生成

        ### 快捷键
        - `Ctrl + Enter`: 发送消息
        - `Esc`: 取消输入

        ### 提示
        - 使用清晰的语言描述您的需求
        - 可以随时清除历史重新开始
        - 导出功能可保存对话记录
        """)


def example_advanced_chat_interface():
    """示例6: 演示多功能聊天界面的特点"""
    print("=== 示例6: 多功能聊天界面 ===")
    print("高级功能：")
    print("1. 多种对话模式")
    print("2. 详细的配置选项")
    print("3. 对话导出功能")
    print("4. 统计信息展示")
    print("5. 标签页布局")
    print("6. 帮助文档\n")


# ==================== 示例7: 完整的Web聊天应用 ====================
def main_chat_application():
    """
    完整的Web聊天应用

    这是一个可以直接部署使用的完整应用
    """
    # 页面配置
    st.set_page_config(
        page_title="AI对话助手",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ 请设置OPENAI_API_KEY环境变量！")
        st.stop()

    # 自定义样式
    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stChatMessage {
            background-color: white;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # 标题
    st.title("🤖 AI对话助手")
    st.caption("基于LangChain和GPT的智能聊天机器人")

    # 侧边栏
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100.png?text=AI+Chat+Bot", use_container_width=True)

        st.header("⚙️ 设置")

        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

        st.divider()

        if st.button("🗑️ 清除历史", use_container_width=True):
            st.session_state.messages = []
            if "conversation" in st.session_state:
                st.session_state.conversation.memory.clear()
            st.rerun()

    # 初始化
    initialize_session_state()

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 聊天输入
    if prompt := st.chat_input("请输入您的消息..."):
        # 用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 助手响应
        with st.chat_message("assistant"):
            response = st.session_state.conversation.predict(input=prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


# ==================== 主函数 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("Web聊天界面示例".center(60))
    print("=" * 60)
    print()

    # 运行所有示例
    example_streamlit_callback()
    print()

    example_session_state()
    print()

    example_simple_chat_interface()
    print()

    example_streaming_chat_interface()
    print()

    example_styled_chat_interface()
    print()

    example_advanced_chat_interface()
    print()

    print("=" * 60)
    print("如何运行Streamlit应用".center(60))
    print("=" * 60)
    print()
    print("运行命令：")
    print("  streamlit run 07_web_interface.py")
    print()
    print("提示：")
    print("1. 确保已安装streamlit: pip install streamlit")
    print("2. 设置OPENAI_API_KEY环境变量")
    print("3. 应用会在浏览器中自动打开")
    print("4. 默认地址: http://localhost:8501")
    print()
    print("=" * 60)
