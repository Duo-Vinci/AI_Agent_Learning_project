from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv()

def create_rag_system():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    embeddings = OpenAIEmbeddings()
    
    with open("data/document.txt", "w", encoding="utf-8") as f:
        f.write("""LangChain是一个用于构建LLM应用的框架。
它提供了多种组件，包括：
1. 模型集成 - 支持多种LLM提供商
2. 提示词模板 - 方便构建提示词
3. 链 - 组合多个组件
4. 向量数据库 - 支持RAG应用
5. 工具调用 - 让AI能够调用外部工具
6. Agent - 构建自主智能体
""")
    
    loader = TextLoader("data/document.txt", encoding="utf-8")
    documents = loader.load()
    
    db = FAISS.from_documents(documents, embeddings)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever()
    )
    
    question = "LangChain提供了哪些组件？"
    result = qa_chain.invoke({"query": question})
    print("问题:", question)
    print("回答:", result["result"])

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    create_rag_system()