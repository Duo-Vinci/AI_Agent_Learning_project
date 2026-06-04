import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_rag_system():
    logger.info("=== 开始 RAG 示例 ===")
    
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
    
    # 2. 初始化 LLM 和 Embeddings
    logger.info("步骤2: 初始化 LLM 和 Embeddings")
    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=api_key,
        base_url=api_base
    )
    embeddings = OpenAIEmbeddings(api_key=api_key, base_url=api_base)
    logger.info("LLM 和 Embeddings 初始化成功")
    
    # 3. 创建示例文档
    logger.info("步骤3: 创建示例文档")
    os.makedirs("data", exist_ok=True)
    doc_content = """LangChain是一个用于构建LLM应用的框架。
它提供了多种组件，包括：
1. 模型集成 - 支持多种LLM提供商
2. 提示词模板 - 方便构建提示词
3. 链 - 组合多个组件
4. 向量数据库 - 支持RAG应用
5. 工具调用 - 让AI能够调用外部工具
6. Agent - 构建自主智能体
"""
    with open("data/document.txt", "w", encoding="utf-8") as f:
        f.write(doc_content)
    logger.debug(f"文档内容已保存到 data/document.txt")
    logger.debug(f"文档内容: {doc_content}")
    
    # 4. 加载文档
    logger.info("步骤4: 加载文档")
    loader = TextLoader("data/document.txt", encoding="utf-8")
    documents = loader.load()
    logger.debug(f"加载了 {len(documents)} 个文档")
    logger.debug(f"第一个文档内容: {documents[0].page_content[:100]}...")
    
    # 5. 构建向量数据库
    logger.info("步骤5: 构建向量数据库")
    db = FAISS.from_documents(documents, embeddings)
    logger.info("向量数据库构建成功")
    
    # 6. 创建 RAG 链
    logger.info("步骤6: 创建 RAG 链")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever()
    )
    logger.debug(f"RAG 链创建完成")
    
    # 7. 执行查询
    logger.info("步骤7: 执行查询")
    question = "LangChain提供了哪些组件?"
    logger.debug(f"查询问题: {question}")
    
    try:
        result = qa_chain.invoke({"query": question})
        logger.info("查询成功")
        logger.debug(f"完整响应: {result}")
        print("问题:", question)
        print("回答:", result["result"])
    except Exception as e:
        logger.error(f"查询失败: {str(e)}", exc_info=True)
        raise
    
    logger.info("=== RAG 示例执行完成 ===")

if __name__ == "__main__":
    create_rag_system()