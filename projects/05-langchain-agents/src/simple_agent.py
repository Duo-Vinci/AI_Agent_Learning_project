import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，例如：2 + 3 * 4"""
    logger.debug(f"calculate 工具被调用，表达式: {expression}")
    try:
        result = eval(expression)
        logger.debug(f"calculate 返回结果: {result}")
        return f"计算结果: {result}"
    except Exception as e:
        error_msg = f"计算错误: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def get_time() -> str:
    """获取当前时间"""
    logger.debug("get_time 工具被调用")
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = f"当前时间: {time_str}"
    logger.debug(f"get_time 返回结果: {result}")
    return result

def agent_demo():
    logger.info("=== 开始 Agent 示例 ===")
    
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
        temperature=0,
        api_key=api_key,
        base_url=api_base
    )
    logger.info("LLM 初始化成功")
    
    # 3. 定义工具
    logger.info("步骤3: 定义工具")
    tools = [calculate, get_time]
    logger.debug(f"注册的工具列表: {[t.name for t in tools]}")
    
    # 4. 创建 Agent (使用 LangGraph)
    logger.info("步骤4: 创建 Agent")
    agent_executor = create_react_agent(llm, tools)
    logger.info("Agent 创建成功")
    
    # 5. 测试1: 数学计算
    logger.info("=== 测试1: 数学计算 ===")
    question1 = "计算 100 + 200 * 3 的结果"
    logger.debug(f"问题1: {question1}")
    try:
        result1 = agent_executor.invoke({"messages": [("user", question1)]})
        logger.info("测试1 执行成功")
        logger.debug(f"测试1 完整响应: {result1}")
        print("=== 测试1: 数学计算 ===")
        print(f"回答: {result1['messages'][-1].content}")
    except Exception as e:
        logger.error(f"测试1 执行失败: {str(e)}", exc_info=True)
    
    # 6. 测试2: 获取时间
    logger.info("\n=== 测试2: 获取时间 ===")
    question2 = "现在几点了？"
    logger.debug(f"问题2: {question2}")
    try:
        result2 = agent_executor.invoke({"messages": [("user", question2)]})
        logger.info("测试2 执行成功")
        logger.debug(f"测试2 完整响应: {result2}")
        print("\n=== 测试2: 获取时间 ===")
        print(f"回答: {result2['messages'][-1].content}")
    except Exception as e:
        logger.error(f"测试2 执行失败: {str(e)}", exc_info=True)
    
    logger.info("=== Agent 示例执行完成 ===")

if __name__ == "__main__":
    agent_demo()
