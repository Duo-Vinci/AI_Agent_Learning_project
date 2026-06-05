"""
LangChain 基础教程 - 08: 完整的应用示例

本模块展示一个完整的 LangChain 应用，整合了前面学习的所有概念：
- 提示词模板
- Chain 组合
- 流式输出
- 输出解析
- 错误处理
- 回调系统
"""

import os
import time
from typing import List, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


class Article(BaseModel):
    """文章数据模型"""
    title: str = Field(description="文章标题")
    outline: List[str] = Field(description="文章大纲（每个要点）")
    content: str = Field(description="完整文章内容")
    tags: List[str] = Field(description="文章标签")


class ProgressCallback(BaseCallbackHandler):
    """进度回调处理器"""

    def __init__(self):
        self.current_step = 0
        self.total_steps = 4
        self.start_time = None

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Chain 开始"""
        if self.start_time is None:
            self.start_time = time.time()
        self.current_step += 1
        print(f"\n[{self.current_step}/{self.total_steps}] 处理中...")

    def on_chain_end(self, outputs, **kwargs):
        """Chain 结束"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"✓ 完成 (耗时: {elapsed:.1f}秒)")


class ArticleGenerator:
    """文章生成器 - 完整应用示例"""

    def __init__(self, model_name: Optional[str] = None):
        """初始化生成器"""
        load_dotenv()

        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        model_name = model_name or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

        if not api_key:
            raise ValueError("未找到 API Key，请配置 .env 文件")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=api_key,
            base_url=api_base
        )

        self.callback = ProgressCallback()
        self._setup_chains()

    def _setup_chains(self):
        """设置处理链"""

        # 步骤1：生成标题
        self.title_prompt = ChatPromptTemplate.from_template(
            "为一篇关于'{topic}'的文章生成一个吸引人的标题。"
            "只返回标题，不要其他内容。"
        )
        self.title_chain = (
            self.title_prompt
            | self.llm.with_config(callbacks=[self.callback])
            | StrOutputParser()
        )

        # 步骤2：生成大纲
        self.outline_prompt = ChatPromptTemplate.from_template(
            "为题为'{title}'的文章生成一个详细大纲。"
            "列出5个主要观点，每个观点一行。"
            "只返回大纲要点，不要编号和额外说明。"
        )
        self.outline_chain = (
            self.outline_prompt
            | self.llm.with_config(callbacks=[self.callback])
            | StrOutputParser()
        )

        # 步骤3：生成内容
        self.content_prompt = ChatPromptTemplate.from_template(
            "根据以下标题和大纲，写一篇完整的文章（约300字）：\n\n"
            "标题：{title}\n\n"
            "大纲：\n{outline}\n\n"
            "要求：内容充实，语言流畅，逻辑清晰。"
        )
        self.content_chain = (
            self.content_prompt
            | self.llm.with_config(callbacks=[self.callback])
            | StrOutputParser()
        )

        # 步骤4：生成标签
        self.tags_prompt = ChatPromptTemplate.from_template(
            "为以下文章生成5个相关标签（用逗号分隔）：\n\n"
            "{content}\n\n"
            "只返回标签，不要其他内容。"
        )
        self.tags_chain = (
            self.tags_prompt
            | self.llm.with_config(callbacks=[self.callback])
            | StrOutputParser()
        )

    def generate(self, topic: str, stream: bool = False) -> Article:
        """
        生成文章

        Args:
            topic: 文章主题
            stream: 是否使用流式输出

        Returns:
            Article: 生成的文章对象
        """
        print_section(f"开始生成文章: {topic}")

        self.callback.start_time = None
        self.callback.current_step = 0

        try:
            # 步骤1：生成标题
            print("\n[1/4] 生成标题...")
            title = self.title_chain.invoke({"topic": topic})
            print(f"✓ 标题: {title}")

            # 步骤2：生成大纲
            print("\n[2/4] 生成大纲...")
            outline_text = self.outline_chain.invoke({"title": title})
            outline = [line.strip() for line in outline_text.split('\n') if line.strip()]
            print(f"✓ 大纲: {len(outline)} 个要点")
            for i, point in enumerate(outline, 1):
                print(f"   {i}. {point}")

            # 步骤3：生成内容
            print("\n[3/4] 生成文章内容...")
            if stream:
                print("AI 正在写作（流式输出）:\n")
                content = ""
                for chunk in self.content_chain.stream({
                    "title": title,
                    "outline": outline_text
                }):
                    print(chunk, end="", flush=True)
                    content += chunk
                print("\n")
            else:
                content = self.content_chain.invoke({
                    "title": title,
                    "outline": outline_text
                })
                print(f"✓ 内容长度: {len(content)} 字符")

            # 步骤4：生成标签
            print("\n[4/4] 生成标签...")
            tags_text = self.tags_chain.invoke({"content": content})
            tags = [tag.strip() for tag in tags_text.split(',')]
            print(f"✓ 标签: {', '.join(tags)}")

            # 构建文章对象
            article = Article(
                title=title,
                outline=outline,
                content=content,
                tags=tags
            )

            print_section("文章生成完成")
            return article

        except Exception as e:
            print(f"\n❌ 生成失败: {str(e)}")
            raise

    def generate_batch(self, topics: List[str]) -> List[Article]:
        """
        批量生成文章

        Args:
            topics: 主题列表

        Returns:
            List[Article]: 生成的文章列表
        """
        print_section(f"批量生成 {len(topics)} 篇文章")

        articles = []
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*70}")
            print(f"  处理 {i}/{len(topics)}: {topic}")
            print(f"{'='*70}")

            try:
                article = self.generate(topic, stream=False)
                articles.append(article)
            except Exception as e:
                print(f"❌ 生成失败: {str(e)}")

        print_section("批量生成完成")
        print(f"成功: {len(articles)}/{len(topics)}")

        return articles

    def save_article(self, article: Article, filename: str):
        """保存文章到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {article.title}\n\n")
            f.write(f"**标签**: {', '.join(article.tags)}\n\n")
            f.write("## 大纲\n\n")
            for i, point in enumerate(article.outline, 1):
                f.write(f"{i}. {point}\n")
            f.write(f"\n## 正文\n\n")
            f.write(article.content)
            f.write(f"\n")

        print(f"\n✓ 文章已保存到: {filename}")


def demo_single_article():
    """示例1: 生成单篇文章"""
    print_section("示例1: 生成单篇文章")

    generator = ArticleGenerator()
    article = generator.generate("人工智能在医疗领域的应用", stream=False)

    print("\n【生成的文章】")
    print(f"\n标题: {article.title}")
    print(f"\n大纲:")
    for i, point in enumerate(article.outline, 1):
        print(f"  {i}. {point}")
    print(f"\n标签: {', '.join(article.tags)}")
    print(f"\n内容:\n{article.content}")


def demo_streaming_article():
    """示例2: 流式生成文章"""
    print_section("示例2: 流式生成文章")

    generator = ArticleGenerator()
    article = generator.generate("可持续发展与绿色能源", stream=True)

    print("\n【最终结果】")
    print(f"标题: {article.title}")
    print(f"标签: {', '.join(article.tags)}")


def demo_batch_generation():
    """示例3: 批量生成文章"""
    print_section("示例3: 批量生成文章")

    topics = [
        "远程工作的优势与挑战",
        "健康饮食的重要性",
        "数字化转型趋势"
    ]

    generator = ArticleGenerator()
    articles = generator.generate_batch(topics)

    print("\n【生成结果总结】")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.title}")
        print(f"   标签: {', '.join(article.tags)}")
        print(f"   长度: {len(article.content)} 字符")


def demo_save_article():
    """示例4: 保存文章"""
    print_section("示例4: 保存文章到文件")

    generator = ArticleGenerator()
    article = generator.generate("Python编程最佳实践", stream=False)

    # 创建输出目录
    os.makedirs("output", exist_ok=True)

    # 保存文章
    filename = f"output/{article.title[:20]}.md"
    generator.save_article(article, filename)


def demo_error_recovery():
    """示例5: 错误恢复"""
    print_section("示例5: 错误恢复机制")

    print("模拟带错误恢复的生成过程\n")

    topics = [
        "机器学习基础",
        "深度学习应用",
        "自然语言处理"
    ]

    generator = ArticleGenerator()

    for topic in topics:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                print(f"\n尝试生成: {topic} (第 {attempt} 次)")
                article = generator.generate(topic, stream=False)
                print(f"✓ 成功生成: {article.title}")
                break
            except Exception as e:
                print(f"✗ 失败: {str(e)[:100]}")
                if attempt < max_retries:
                    print(f"等待后重试...")
                    time.sleep(2)
                else:
                    print(f"❌ 达到最大重试次数，跳过")


def main():
    """运行所有示例"""
    try:
        # 运行演示
        demo_single_article()
        demo_streaming_article()
        demo_batch_generation()
        demo_save_article()
        demo_error_recovery()

        print_section("所有示例执行完成")
        print("这个完整的应用示例展示了如何整合 LangChain 的各种功能：")
        print("  ✓ 提示词模板")
        print("  ✓ Chain 组合")
        print("  ✓ 流式输出")
        print("  ✓ 输出解析")
        print("  ✓ 回调系统")
        print("  ✓ 错误处理")
        print("\n你可以基于这个模板构建更复杂的应用！")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
