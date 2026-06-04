import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def print_divider(title=None):
    print("\n" + "="*70)
    if title:
        print(f" {title} ")
        print("="*70)

def print_section(title):
    print(f"\n【{title}】")
    print("-" * 30)

def print_json(data, title="JSON输出"):
    print(f"\n【{title}】")
    print("-" * 40)
    try:
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False))
    except TypeError:
        print(json.dumps(str(data), ensure_ascii=False, indent=2))
    print("-" * 40)

def chatbot():
    print_divider("聊天机器人示例")
    
    # ============ 步骤1: 加载环境变量 ============
    print_section("步骤1: 加载环境变量")
    print("解释: 从 .env 文件中读取 API Key 和配置信息")
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    
    config_info = {}
    if api_key:
        config_info = {
            "服务商": "DeepSeek",
            "API地址": api_base,
            "模型名称": model_name,
            "API密钥长度": len(api_key)
        }
        print("[OK] 使用 DeepSeek API")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if api_key:
            config_info = {
                "服务商": "OpenAI",
                "API地址": api_base,
                "模型名称": model_name,
                "API密钥长度": len(api_key)
            }
            print("[OK] 使用 OpenAI API")
        else:
            print("[ERROR] 未找到 API Key，请检查 .env 文件")
            return
    
    print_json(config_info, "当前配置信息")
    
    # ============ 步骤2: 初始化 LLM ============
    print_section("步骤2: 初始化大语言模型(LLM)")
    print("解释: 创建一个可以和 AI 模型对话的客户端")
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )
    print("[OK] LLM 初始化成功")
    print(f"  模型: {model_name}")
    print(f"  温度: 0.7")
    
    # ============ 步骤3: 初始化对话历史 ============
    print_section("步骤3: 初始化对话历史")
    print("解释: 设置系统角色和初始消息")
    messages = [
        SystemMessage(content="你是一个友好的聊天机器人，用中文回答问题。")
    ]
    print("[OK] 对话历史初始化完成")
    
    # ============ 步骤4: 开始对话循环 ============
    print_section("步骤4: 开始对话")
    print("欢迎使用聊天机器人！输入 'exit' 退出。")
    print("-" * 30)
    
    while True:
        user_input = input("你: ")
        
        if user_input.lower() == 'exit':
            print("\n[INFO] 用户退出对话")
            print("再见！")
            break
        
        print(f"\n[INFO] 收到用户输入: {user_input}")
        messages.append(HumanMessage(content=user_input))
        print(f"[INFO] 当前对话消息数量: {len(messages)}")
        
        try:
            print("\n[PROCESS] 正在调用 AI API...")
            response = llm.invoke(messages)
            
            print("[OK] AI 回复生成成功")
            messages.append(AIMessage(content=response.content))
            
            print("\n【AI回复】")
            print(response.content)
            print("-" * 30)
            
        except Exception as e:
            print(f"\n[ERROR] 调用失败: {str(e)}")
            break
    
    print_divider("聊天结束")

if __name__ == "__main__":
    chatbot()