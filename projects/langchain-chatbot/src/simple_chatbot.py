from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

def chatbot():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    messages = [
        SystemMessage(content="你是一个友好的聊天机器人，用中文回答问题。")
    ]
    
    print("欢迎使用聊天机器人！输入 'exit' 退出。")
    
    while True:
        user_input = input("你: ")
        if user_input.lower() == 'exit':
            print("再见！")
            break
        
        messages.append(HumanMessage(content=user_input))
        response = llm.invoke(messages)
        messages.append(AIMessage(content=response.content))
        
        print("AI:", response.content)

if __name__ == "__main__":
    chatbot()