import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def chatbot():
    logger.info("=== 开始聊天机器人示例 ===")
    
    # 1. 加载环境变量
    logger.info("步骤1: 加载环境变量")
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    
    if api_key:
        logger.info(f"使用 DeepSeek API (base: {api_base}, model: {model_name})")
        logger.debug(f"DEEPSEEK_API_KEY 已加载 (长度: {len(api_key)})")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if api_key:
            logger.info(f"使用 OpenAI API (base: {api_base}, model: {model_name})")
            logger.debug(f"OPENAI_API_KEY 已加载 (长度: {len(api_key)})")
        else:
            logger.error("未找到 API Key，请检查 .env 文件")
            return
    
    # 2. 初始化 LLM
    logger.info("步骤2: 初始化 LLM")
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )
    logger.info("LLM 初始化成功")
    
    # 3. 初始化对话历史
    logger.info("步骤3: 初始化对话历史")
    messages = [
        SystemMessage(content="你是一个友好的聊天机器人，用中文回答问题。")
    ]
    logger.debug(f"初始消息: {messages}")
    
    # 4. 开始对话循环
    logger.info("步骤4: 开始对话循环")
    print("欢迎使用聊天机器人！输入 'exit' 退出。")
    
    while True:
        user_input = input("你: ")
        
        if user_input.lower() == 'exit':
            logger.info("用户退出对话")
            print("再见！")
            break
        
        logger.debug(f"收到用户输入: {user_input}")
        messages.append(HumanMessage(content=user_input))
        logger.debug(f"当前对话历史长度: {len(messages)}")
        
        try:
            logger.info("调用 LLM 生成回复")
            response = llm.invoke(messages)
            logger.info("LLM 回复生成成功")
            logger.debug(f"AI 回复内容: {response.content}")
            messages.append(AIMessage(content=response.content))
            print("AI:", response.content)
        except Exception as e:
            logger.error(f"调用 LLM 失败: {str(e)}", exc_info=True)
    
    logger.info("=== 聊天机器人示例结束 ===")

if __name__ == "__main__":
    chatbot()