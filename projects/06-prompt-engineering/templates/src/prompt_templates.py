"""
Prompt模板库

提供常用的Prompt模板，方便快速使用。
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class PromptTemplateLibrary:
    """Prompt模板库类"""

    def __init__(self, provider: str = "openai"):
        """初始化"""
        self.provider = provider

        if not config.validate():
            raise ValueError(f"配置验证失败")

        self.client = OpenAI(
            api_key=config.get_api_key(provider),
            base_url=config.get_base_url(provider)
        )
        self.model = config.get_model(provider)

        # 初始化模板库
        self._init_templates()

    def _init_templates(self):
        """初始化模板"""
        self.templates = {
            "code_review": {
                "name": "代码审查",
                "template": """你是一个资深代码审查专家。请审查以下代码：

```{language}
{code}
```

请从以下维度进行审查：
1. 代码规范性（命名、格式、注释）
2. 逻辑正确性（是否有bug）
3. 性能问题（时间和空间复杂度）
4. 安全隐患（输入验证、错误处理）
5. 可维护性（模块化、可读性）

请提供具体的改进建议和优化后的代码示例。""",
                "variables": ["language", "code"],
                "category": "开发"
            },

            "text_summary": {
                "name": "文本摘要",
                "template": """请为以下文本生成摘要：

文本：
{text}

要求：
- 摘要长度：{length}字以内
- 保留核心信息和关键观点
- 语言简洁流畅
- 不添加原文没有的内容

摘要：""",
                "variables": ["text", "length"],
                "category": "文本处理"
            },

            "data_extraction": {
                "name": "数据提取",
                "template": """请从以下文本中提取信息，并以JSON格式输出：

文本：
{text}

请提取：
{fields}

JSON格式：
{{
{schema}
}}

请只输出JSON：""",
                "variables": ["text", "fields", "schema"],
                "category": "数据处理"
            },

            "email_writer": {
                "name": "邮件撰写",
                "template": """请撰写一封{tone}的{type}邮件。

收件人：{recipient}
主题：{subject}
关键内容：
{content}

要求：
- 语气{tone}
- 格式规范
- 逻辑清晰
- 包含适当的称呼和结尾

邮件内容：""",
                "variables": ["tone", "type", "recipient", "subject", "content"],
                "category": "写作"
            },

            "problem_solver": {
                "name": "问题解决",
                "template": """请帮助解决以下问题，使用思维链方法逐步分析：

问题：
{problem}

请按以下步骤思考：
1. 理解问题：明确问题的核心和目标
2. 分析现状：识别当前的情况和约束
3. 提出方案：列出可能的解决方案
4. 评估方案：分析各方案的优缺点
5. 推荐方案：给出最佳方案及理由
6. 实施建议：提供具体的行动步骤

让我们开始分析：""",
                "variables": ["problem"],
                "category": "分析"
            },

            "learning_tutor": {
                "name": "学习辅导",
                "template": """你是一位{subject}领域的资深导师。

学生问题：
{question}

请用以下方式回答：
1. 简明扼要地解释概念
2. 用生动的比喻或例子帮助理解
3. 提供实践建议或练习题
4. 指出常见的误区
5. 鼓励学生深入思考

你的回答：""",
                "variables": ["subject", "question"],
                "category": "教育"
            },

            "creative_writing": {
                "name": "创意写作",
                "template": """请创作一篇{genre}风格的短文。

主题：{topic}
风格：{style}
长度：约{length}字

要求：
- 内容{genre}
- 风格{style}
- 语言优美，富有感染力
- 结构完整，有开头、发展和结尾

创作：""",
                "variables": ["genre", "topic", "style", "length"],
                "category": "写作"
            },

            "translation": {
                "name": "翻译",
                "template": """你是一位专业的{source_lang}到{target_lang}翻译专家。

请翻译以下文本：

{source_lang}原文：
{text}

翻译要求：
- 准确传达原文含义
- 符合{target_lang}表达习惯
- 保持原文的语气和风格
- 专业术语翻译准确

{target_lang}译文：""",
                "variables": ["source_lang", "target_lang", "text"],
                "category": "翻译"
            },

            "brainstorming": {
                "name": "头脑风暴",
                "template": """让我们为以下主题进行头脑风暴：

主题：{topic}
目标：{goal}

请提供：
1. 5-10个创新想法
2. 每个想法的简要说明
3. 可行性评估（高/中/低）
4. 潜在的挑战

思维发散，欢迎大胆创新！

头脑风暴结果：""",
                "variables": ["topic", "goal"],
                "category": "创新"
            },

            "comparison": {
                "name": "对比分析",
                "template": """请对比分析以下{category}：

项目A：{item_a}
项目B：{item_b}

对比维度：
{dimensions}

请以表格形式输出对比结果，并给出：
1. 各维度的详细对比
2. 优缺点总结
3. 适用场景分析
4. 选择建议

对比分析：""",
                "variables": ["category", "item_a", "item_b", "dimensions"],
                "category": "分析"
            }
        }

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出可用模板

        Args:
            category: 类别筛选（可选）

        Returns:
            模板列表
        """
        templates = []
        for key, template in self.templates.items():
            if category is None or template["category"] == category:
                templates.append({
                    "key": key,
                    "name": template["name"],
                    "category": template["category"],
                    "variables": template["variables"]
                })
        return templates

    def get_template(self, template_key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模板

        Args:
            template_key: 模板键名

        Returns:
            模板信息
        """
        return self.templates.get(template_key)

    def render_template(
        self,
        template_key: str,
        variables: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        渲染模板

        Args:
            template_key: 模板键名
            variables: 变量字典

        Returns:
            渲染结果
        """
        template = self.templates.get(template_key)

        if not template:
            return {
                "error": f"模板 '{template_key}' 不存在",
                "success": False
            }

        # 检查必需变量
        missing_vars = [v for v in template["variables"] if v not in variables]
        if missing_vars:
            return {
                "error": f"缺少必需变量: {', '.join(missing_vars)}",
                "required_variables": template["variables"],
                "success": False
            }

        # 渲染模板
        try:
            rendered_prompt = template["template"].format(**variables)
            return {
                "template_key": template_key,
                "template_name": template["name"],
                "prompt": rendered_prompt,
                "success": True
            }
        except KeyError as e:
            return {
                "error": f"变量错误: {str(e)}",
                "success": False
            }

    def execute_template(
        self,
        template_key: str,
        variables: Dict[str, str],
        temperature: float = 0.5
    ) -> Dict[str, Any]:
        """
        执行模板（渲染并调用LLM）

        Args:
            template_key: 模板键名
            variables: 变量字典
            temperature: 温度参数

        Returns:
            执行结果
        """
        # 渲染模板
        render_result = self.render_template(template_key, variables)

        if not render_result["success"]:
            return render_result

        # 调用LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": render_result["prompt"]}],
                temperature=temperature,
                max_tokens=2000
            )

            return {
                "template_key": template_key,
                "template_name": render_result["template_name"],
                "prompt": render_result["prompt"],
                "output": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {
                "template_key": template_key,
                "error": str(e),
                "success": False
            }

    def add_custom_template(
        self,
        key: str,
        name: str,
        template: str,
        variables: List[str],
        category: str = "自定义"
    ) -> Dict[str, Any]:
        """
        添加自定义模板

        Args:
            key: 模板键名
            name: 模板名称
            template: 模板内容
            variables: 变量列表
            category: 类别

        Returns:
            添加结果
        """
        if key in self.templates:
            return {
                "error": f"模板 '{key}' 已存在",
                "success": False
            }

        self.templates[key] = {
            "name": name,
            "template": template,
            "variables": variables,
            "category": category
        }

        return {
            "message": f"模板 '{name}' 添加成功",
            "key": key,
            "success": True
        }


def main():
    """示例用法"""
    print("=" * 60)
    print("Prompt模板库示例")
    print("=" * 60)

    try:
        library = PromptTemplateLibrary(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：列出所有模板
    print("\n" + "=" * 60)
    print("示例1: 列出可用模板")
    print("=" * 60)

    templates = library.list_templates()
    print(f"共有 {len(templates)} 个模板：\n")

    for i, t in enumerate(templates, 1):
        print(f"{i}. {t['name']} ({t['category']})")
        print(f"   键名: {t['key']}")
        print(f"   变量: {', '.join(t['variables'])}\n")

    # 示例2：使用文本摘要模板
    print("\n" + "=" * 60)
    print("示例2: 使用文本摘要模板")
    print("=" * 60)

    result2 = library.execute_template(
        template_key="text_summary",
        variables={
            "text": """人工智能（AI）正在迅速改变我们的世界。从智能手机到自动驾驶汽车，
从医疗诊断到金融分析，AI技术已经渗透到生活的方方面面。机器学习和深度学习的突破
使得计算机能够从大量数据中学习模式，并做出智能决策。然而，AI的发展也带来了诸多挑战，
包括隐私保护、就业影响和伦理问题。如何在推动技术进步的同时确保其安全和负责任的使用，
是我们面临的重要课题。""",
            "length": "100"
        },
        temperature=0.5
    )

    if result2["success"]:
        print(f"模板: {result2['template_name']}")
        print(f"\n生成的摘要:\n{result2['output']}")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：使用代码审查模板
    print("\n" + "=" * 60)
    print("示例3: 使用代码审查模板")
    print("=" * 60)

    code_sample = """
def calculate_average(numbers):
    sum = 0
    for i in range(len(numbers)):
        sum = sum + numbers[i]
    return sum / len(numbers)
"""

    result3 = library.execute_template(
        template_key="code_review",
        variables={
            "language": "python",
            "code": code_sample
        },
        temperature=0.4
    )

    if result3["success"]:
        print(f"模板: {result3['template_name']}")
        print(f"\n审查结果:\n{result3['output'][:500]}...")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：添加自定义模板
    print("\n" + "=" * 60)
    print("示例4: 添加自定义模板")
    print("=" * 60)

    add_result = library.add_custom_template(
        key="meeting_notes",
        name="会议纪要",
        template="""请根据以下会议记录整理会议纪要：

会议主题：{topic}
参会人员：{participants}
会议内容：
{content}

请按以下格式整理：
## 会议纪要

**会议主题**:
**时间**:
**参会人员**:

### 讨论要点
1. ...

### 决议事项
1. ...

### 待办事项
1. ...""",
        variables=["topic", "participants", "content"],
        category="办公"
    )

    if add_result["success"]:
        print(f"✓ {add_result['message']}")
        print(f"模板键名: {add_result['key']}")
    else:
        print(f"✗ {add_result['error']}")

    # 示例5：渲染模板（不执行）
    print("\n" + "=" * 60)
    print("示例5: 渲染模板（查看生成的Prompt）")
    print("=" * 60)

    result5 = library.render_template(
        template_key="translation",
        variables={
            "source_lang": "中文",
            "target_lang": "英文",
            "text": "机器学习是人工智能的核心技术之一。"
        }
    )

    if result5["success"]:
        print(f"模板: {result5['template_name']}")
        print(f"\n渲染的Prompt:\n{result5['prompt']}")
    else:
        print(f"错误: {result5['error']}")

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
