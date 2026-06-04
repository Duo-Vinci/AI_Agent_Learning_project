import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    logger.debug(f"get_weather 工具被调用，城市: {city}")
    weather_data = {
        "北京": "晴天，温度25°C",
        "上海": "多云，温度28°C",
        "广州": "下雨，温度30°C",
        "深圳": "阴天，温度27°C"
    }
    result = weather_data.get(city, f"暂未获取到{city}的天气信息")
    logger.debug(f"get_weather 返回结果: {result}")
    return result

def tool_demo():
    logger.info("=== 开始工具调用示例 ===")
    
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
    tools = [get_weather]
    logger.debug(f"注册的工具列表: {[t.name for t in tools]}")
    
    # 4. 创建 Agent
    logger.info("步骤4: 创建 Agent")
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    logger.info("Agent 创建成功")
    
    # 5. 执行查询
    logger.info("步骤5: 执行查询")
    question = "北京今天的天气怎么样？"
    logger.debug(f"用户问题: {question}")
    
    try:
        result = agent.invoke(question)
        logger.info("Agent 执行成功")
        logger.debug(f"完整响应: {result}")
        print("\n最终回答:", result["output"])
    except Exception as e:
        logger.error(f"Agent 执行失败: {str(e)}", exc_info=True)
        raise
    
    logger.info("=== 工具调用示例执行完成 ===")

if __name__ == "__main__":
    tool_demo()