"""
自主协作团队主工作流
整合AutoGen和CrewAI示例
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60 + "\n")


def main():
    """主函数"""
    load_dotenv()

    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请在.env文件中设置OPENAI_API_KEY")
        return

    print_section("多Agent框架示例集")
    print("本模块展示如何使用主流框架实现多Agent协作")
    print("包含：AutoGen 和 CrewAI\n")

    # AutoGen示例
    print_section("第一部分：AutoGen框架示例")
    print("AutoGen是微软开发的对话式AI框架")
    print("特点：支持代码执行、群聊、自动回复等\n")

    try:
        from src.autogen_example import AUTOGEN_AVAILABLE
        if AUTOGEN_AVAILABLE:
            print("✓ AutoGen已安装")
            print("\n运行AutoGen示例:")
            print("  python src/autogen_example.py")
        else:
            print("⚠ AutoGen未安装")
            print("安装命令: pip install autogen-agentchat")
    except Exception as e:
        print(f"⚠ AutoGen检查失败: {str(e)}")

    # CrewAI示例
    print_section("第二部分：CrewAI框架示例")
    print("CrewAI是专为角色扮演和任务协作设计的框架")
    print("特点：角色定义、任务编排、顺序/并行执行\n")

    try:
        from src.crewai_example import CREWAI_AVAILABLE
        if CREWAI_AVAILABLE:
            print("✓ CrewAI已安装")
            print("\n运行CrewAI示例:")
            print("  python src/crewai_example.py")
        else:
            print("⚠ CrewAI未安装")
            print("安装命令: pip install crewai crewai-tools")
    except Exception as e:
        print(f"⚠ CrewAI检查失败: {str(e)}")

    # 框架对比
    print_section("框架对比")
    print("""
┌─────────────┬──────────────────────┬──────────────────────┐
│   特性      │      AutoGen         │       CrewAI         │
├─────────────┼──────────────────────┼──────────────────────┤
│ 开发者      │ Microsoft            │ CrewAI Inc.          │
│ 核心特点    │ 对话式、代码执行     │ 角色扮演、任务编排   │
│ 使用场景    │ 编程助手、群聊       │ 内容创作、研究团队   │
│ 学习曲线    │ 中等                 │ 较简单               │
│ 自定义能力  │ 高                   │ 中                   │
│ 代码执行    │ ✓                    │ ✗                    │
│ 任务编排    │ ✓                    │ ✓                    │
│ 工具集成    │ 灵活                 │ 内置工具             │
└─────────────┴──────────────────────┴──────────────────────┘
    """)

    # 使用建议
    print_section("使用建议")
    print("""
1. 选择AutoGen如果你需要：
   - Agent自动编写和执行代码
   - 复杂的多轮对话
   - 高度自定义的Agent行为

2. 选择CrewAI如果你需要：
   - 明确的角色分工
   - 简单的任务编排
   - 快速原型开发

3. 混合使用：
   - 根据不同场景选择合适的框架
   - 在同一项目中可以结合两者的优势
    """)

    # 快速开始指南
    print_section("快速开始")
    print("""
步骤1: 安装依赖
  pip install -r requirements.txt

步骤2: 设置环境变量
  在.env文件中设置OPENAI_API_KEY

步骤3: 运行示例
  # AutoGen示例
  python 07-autonomous-team/src/autogen_example.py

  # CrewAI示例
  python 07-autonomous-team/src/crewai_example.py

步骤4: 查看其他模块
  # 顺序协作
  python 01-sequential-agents/src/workflow.py

  # 并行协作
  python 02-parallel-agents/src/workflow.py

  # 层级协作
  python 03-hierarchical-agents/src/workflow.py

  # 辩论模式
  python 04-debate-agents/src/workflow.py

  # 通信机制
  python 05-research-team/src/workflow.py

  # 共享记忆
  python 06-code-review-team/src/workflow.py
    """)

    print_section("完成")
    print("选择一个框架开始你的多Agent之旅吧！\n")


if __name__ == "__main__":
    main()
