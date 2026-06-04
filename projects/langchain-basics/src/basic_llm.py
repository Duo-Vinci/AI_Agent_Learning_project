from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

def basic_chat():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个乐于助人的AI助手。"),
        ("user", "{question}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({"question": "什么是LangChain?"})
    print("AI回答:", response.content)

if __name__ == "__main__":
    basic_chat()