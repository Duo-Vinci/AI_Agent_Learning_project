from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，例如：2 + 3 * 4"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def agent_demo():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    tools = [calculate, get_time]
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    print("=== 测试1: 数学计算 ===")
    agent.invoke("计算 100 + 200 * 3 的结果")
    
    print("\n=== 测试2: 获取时间 ===")
    agent.invoke("现在几点了？")

if __name__ == "__main__":
    agent_demo()