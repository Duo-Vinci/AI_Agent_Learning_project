from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {
        "北京": "晴天，温度25°C",
        "上海": "多云，温度28°C",
        "广州": "下雨，温度30°C",
        "深圳": "阴天，温度27°C"
    }
    return weather_data.get(city, f"暂未获取到{city}的天气信息")

def tool_demo():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    tools = [get_weather]
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    result = agent.invoke("北京今天的天气怎么样？")
    print("\n最终回答:", result["output"])

if __name__ == "__main__":
    tool_demo()