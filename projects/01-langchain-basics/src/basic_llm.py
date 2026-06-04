import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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

def basic_chat():
    print_divider("LangChain 基础示例")
    
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
    
    # ============ 步骤2: 初始化大语言模型(LLM) ============
    print_section("步骤2: 初始化大语言模型(LLM)")
    print("解释: 创建一个可以和 AI 模型对话的客户端")
    print("参数说明:")
    print("  - model: 使用哪个AI模型")
    print("  - temperature: 回答的随机性(0=确定, 1=创意)")
    print("  - api_key: 你的API密钥")
    print("  - base_url: API服务地址")
    
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key,
        base_url=api_base
    )
    print("[OK] LLM 初始化成功")
    print(f"  模型: {model_name}")
    print(f"  温度: 0.7")
    print(f"  API地址: {api_base}")
    
    # ============ 步骤3: 创建提示词模板 ============
    print_section("步骤3: 创建提示词模板")
    print("解释: 定义对话的格式和系统角色")
    print("提示词模板包含两部分:")
    print("  1. System Prompt: 告诉AI它是什么角色")
    print("  2. User Prompt: 用户的问题格式")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个乐于助人的AI助手，用中文回答问题。"),
        ("user", "{question}")
    ])
    print("[OK] 提示词模板创建完成")
    
    prompt_info = {
        "系统提示": "你是一个乐于助人的AI助手，用中文回答问题。",
        "用户提示格式": "{question}",
        "输入变量": prompt.input_variables
    }
    print_json(prompt_info, "提示词模板详情")
    
    # ============ 步骤4: 构建执行链(Chain) ============
    print_section("步骤4: 构建执行链(Chain)")
    print("解释: 将提示词模板和LLM连接起来")
    print("Chain 就像一条流水线:")
    print("  用户问题 -> 提示词模板(格式化) -> LLM(生成回答) -> 返回结果")
    
    chain = prompt | llm
    print("[OK] Chain 构建完成")
    print("  结构: ChatPromptTemplate -> ChatOpenAI")
    
    # ============ 步骤5: 执行Chain并获取回答 ============
    print_section("步骤5: 执行Chain")
    question = "什么是LangChain?"
    print(f"用户问题: {question}")
    
    try:
        print("\n[PROCESS] 正在调用 AI API...")
        
        response = chain.invoke({"question": question})
        
        print("\n[OK] Chain 执行成功")
        
        response_info = {
            "回答内容": response.content,
            "元数据": {
                "模型名称": response.response_metadata.get("model_name"),
                "Token使用情况": response.response_metadata.get("token_usage"),
                "结束原因": response.response_metadata.get("finish_reason")
            },
            "使用统计": response.usage_metadata
        }
        print_json(response_info, "完整响应数据")
        
        print_section("最终回答")
        print(response.content)
        print("-" * 30)
        
    except Exception as e:
        print(f"\n[ERROR] 执行失败: {str(e)}")
        raise
    
    print_divider("示例执行完成")

if __name__ == "__main__":
    basic_chat()