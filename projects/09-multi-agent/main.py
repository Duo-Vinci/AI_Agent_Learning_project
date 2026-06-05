"""
多Agent系统项目 - 主入口
统一的入口程序，方便运行所有示例
"""

import os
import sys
from dotenv import load_dotenv


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_menu():
    """打印菜单"""
    print_header("多Agent系统示例集")
    print("\n本项目包含7个模块，涵盖多种多Agent协作模式：\n")

    modules = [
        ("1", "顺序协作模式 (Sequential)", "01-sequential-agents/src/workflow.py"),
        ("2", "并行协作模式 (Parallel)", "02-parallel-agents/src/workflow.py"),
        ("3", "层级协作模式 (Hierarchical)", "03-hierarchical-agents/src/workflow.py"),
        ("4", "辩论协作模式 (Debate)", "04-debate-agents/src/workflow.py"),
        ("5", "通信机制示例 (Communication)", "05-research-team/src/workflow.py"),
        ("6", "共享记忆示例 (Shared Memory)", "06-code-review-team/src/workflow.py"),
        ("7", "框架示例 (AutoGen & CrewAI)", "07-autonomous-team/src/main.py"),
        ("8", "查看项目说明", "PROJECT_README.md"),
        ("0", "退出", None)
    ]

    for num, title, _ in modules:
        print(f"  [{num}] {title}")

    print("\n" + "-" * 70)


def run_module(module_path: str):
    """运行指定模块"""
    if not module_path:
        return

    if module_path.endswith('.md'):
        # 打开README
        if os.path.exists(module_path):
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("\n" + content)
            input("\n按回车键继续...")
        else:
            print(f"\n文件不存在: {module_path}")
        return

    full_path = os.path.join(os.path.dirname(__file__), module_path)

    if not os.path.exists(full_path):
        print(f"\n✗ 文件不存在: {full_path}")
        return

    print(f"\n▶ 运行: {module_path}\n")
    print("=" * 70)

    try:
        # 动态导入并执行
        import importlib.util
        spec = importlib.util.spec_from_file_location("module", full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    input("\n按回车键继续...")


def check_environment():
    """检查环境配置"""
    print_header("环境检查")

    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✓ OPENAI_API_KEY 已设置")
    else:
        print("✗ OPENAI_API_KEY 未设置")
        print("\n请在项目根目录创建 .env 文件并设置:")
        print("  OPENAI_API_KEY=your_api_key_here\n")
        return False

    # 检查核心依赖
    try:
        import langchain
        import langchain_openai
        print("✓ LangChain 已安装")
    except ImportError:
        print("✗ LangChain 未安装")
        print("  运行: pip install langchain langchain-openai")
        return False

    # 检查可选依赖
    optional_deps = []

    try:
        import autogen
        optional_deps.append("AutoGen")
    except ImportError:
        pass

    try:
        import crewai
        optional_deps.append("CrewAI")
    except ImportError:
        pass

    if optional_deps:
        print(f"✓ 可选框架已安装: {', '.join(optional_deps)}")
    else:
        print("⚠ 未安装可选框架 (AutoGen, CrewAI)")
        print("  这不影响其他模块的运行")

    print("\n环境检查完成！")
    return True


def show_quick_start():
    """显示快速开始指南"""
    print_header("快速开始指南")

    print("""
1. 环境准备
   ├─ 安装依赖: pip install -r requirements.txt
   └─ 设置API密钥: 在 .env 文件中设置 OPENAI_API_KEY

2. 模块说明
   ├─ 模块1-4: 基础协作模式 (顺序、并行、层级、辩论)
   ├─ 模块5-6: 高级特性 (通信机制、共享记忆)
   └─ 模块7: 框架应用 (AutoGen、CrewAI)

3. 学习路径
   ├─ 新手: 从模块1开始，按顺序学习
   ├─ 进阶: 直接学习感兴趣的模块
   └─ 高级: 学习模块7的框架应用

4. 运行方式
   ├─ 交互式: python main.py (当前方式)
   └─ 直接运行: python 01-sequential-agents/src/workflow.py

5. 获取帮助
   └─ 查看 PROJECT_README.md 了解详细说明
    """)

    input("\n按回车键继续...")


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 显示欢迎信息
    print("\n" + "🎯" * 35)
    print_header("多Agent系统学习项目")
    print("🎯" * 35)

    # 环境检查
    if not check_environment():
        print("\n请先完成环境配置，然后重新运行。")
        return

    # 显示快速开始
    show_quick_start()

    # 模块路径映射
    modules = {
        "1": "01-sequential-agents/src/workflow.py",
        "2": "02-parallel-agents/src/workflow.py",
        "3": "03-hierarchical-agents/src/workflow.py",
        "4": "04-debate-agents/src/workflow.py",
        "5": "05-research-team/src/workflow.py",
        "6": "06-code-review-team/src/workflow.py",
        "7": "07-autonomous-team/src/main.py",
        "8": "PROJECT_README.md"
    }

    # 主循环
    while True:
        print_menu()
        choice = input("\n请选择要运行的模块 (输入编号): ").strip()

        if choice == "0":
            print("\n感谢使用！再见！\n")
            break

        if choice in modules:
            run_module(modules[choice])
        else:
            print("\n✗ 无效的选择，请重新输入。")
            input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断。再见！\n")
    except Exception as e:
        print(f"\n✗ 程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
