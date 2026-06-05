"""
输出格式控制模块

提供多种输出格式控制方法，包括JSON、XML、Markdown等。
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from config import config


class OutputFormatter:
    """输出格式控制类"""

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

    def json_output(self, task: str, schema: Dict[str, Any], input_data: str) -> Dict[str, Any]:
        """
        生成JSON格式输出

        Args:
            task: 任务描述
            schema: JSON结构示例
            input_data: 输入数据

        Returns:
            包含JSON输出的结果
        """
        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)

        prompt = f"""{task}

请严格按照以下JSON格式输出结果：

{schema_str}

输入数据：
{input_data}

请只输出JSON，不要包含其他内容："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试提取JSON（移除markdown代码块标记）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # 验证JSON格式
            try:
                parsed_json = json.loads(result_text)
                return {
                    "task": task,
                    "input": input_data,
                    "output": parsed_json,
                    "raw_output": result_text,
                    "valid_json": True,
                    "success": True
                }
            except json.JSONDecodeError as je:
                return {
                    "task": task,
                    "input": input_data,
                    "output": result_text,
                    "valid_json": False,
                    "error": f"JSON解析失败: {str(je)}",
                    "success": False
                }

        except Exception as e:
            return {"task": task, "error": str(e), "success": False}

    def structured_list_output(self, task: str, input_data: str) -> Dict[str, Any]:
        """
        生成结构化列表输出

        Args:
            task: 任务描述
            input_data: 输入数据

        Returns:
            结构化列表结果
        """
        prompt = f"""{task}

请按以下格式输出结构化列表：

## 主要内容
1. [项目名称] - [描述] - [优先级：高/中/低]
2. [项目名称] - [描述] - [优先级：高/中/低]
...

## 详细说明
### 项目1
- 具体内容
- 相关信息

### 项目2
- 具体内容
- 相关信息

输入数据：
{input_data}

请按格式输出："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1500
            )

            return {
                "task": task,
                "input": input_data,
                "output": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"task": task, "error": str(e), "success": False}

    def table_output(self, task: str, columns: List[str], input_data: str) -> Dict[str, Any]:
        """
        生成表格格式输出

        Args:
            task: 任务描述
            columns: 列名列表
            input_data: 输入数据

        Returns:
            表格格式结果
        """
        columns_str = " | ".join(columns)
        separator = " | ".join(["---"] * len(columns))

        prompt = f"""{task}

请按以下Markdown表格格式输出：

| {columns_str} |
| {separator} |
| 数据1 | 数据2 | ... |
| 数据1 | 数据2 | ... |

输入数据：
{input_data}

请按格式输出表格："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )

            return {
                "task": task,
                "input": input_data,
                "columns": columns,
                "output": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"task": task, "error": str(e), "success": False}

    def xml_output(self, task: str, root_element: str, input_data: str) -> Dict[str, Any]:
        """
        生成XML格式输出

        Args:
            task: 任务描述
            root_element: XML根元素名称
            input_data: 输入数据

        Returns:
            XML格式结果
        """
        prompt = f"""{task}

请按以下XML格式输出：

<{root_element}>
  <item>
    <field1>值1</field1>
    <field2>值2</field2>
  </item>
  ...
</{root_element}>

输入数据：
{input_data}

请按格式输出XML："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1500
            )

            return {
                "task": task,
                "input": input_data,
                "root_element": root_element,
                "output": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"task": task, "error": str(e), "success": False}

    def code_output(self, task: str, language: str, input_data: str) -> Dict[str, Any]:
        """
        生成代码格式输出

        Args:
            task: 任务描述
            language: 编程语言
            input_data: 输入数据

        Returns:
            代码格式结果
        """
        prompt = f"""{task}

请生成{language}代码，要求：
1. 代码完整可运行
2. 包含必要的注释
3. 遵循最佳实践
4. 代码格式规范

输入需求：
{input_data}

请输出代码："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )

            return {
                "task": task,
                "input": input_data,
                "language": language,
                "output": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"task": task, "error": str(e), "success": False}

    def multi_section_output(
        self,
        task: str,
        sections: List[str],
        input_data: str
    ) -> Dict[str, Any]:
        """
        生成多段落结构化输出

        Args:
            task: 任务描述
            sections: 章节列表
            input_data: 输入数据

        Returns:
            多段落结果
        """
        sections_template = "\n\n".join(f"## {section}\n[此处填写{section}的内容]" for section in sections)

        prompt = f"""{task}

请按以下结构输出：

{sections_template}

输入数据：
{input_data}

请按结构输出内容："""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )

            return {
                "task": task,
                "input": input_data,
                "sections": sections,
                "output": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {"task": task, "error": str(e), "success": False}


def main():
    """示例用法"""
    print("=" * 60)
    print("输出格式控制示例")
    print("=" * 60)

    try:
        formatter = OutputFormatter(provider=config.default_provider)
        print(f"\n✓ 使用提供商: {config.default_provider}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return

    # 示例1：JSON格式输出
    print("\n" + "=" * 60)
    print("示例1: JSON格式输出")
    print("=" * 60)

    json_schema = {
        "name": "姓名",
        "age": "年龄（数字）",
        "skills": ["技能1", "技能2"],
        "experience": {
            "years": "工作年限",
            "companies": ["公司1", "公司2"]
        }
    }

    result1 = formatter.json_output(
        task="从以下文本中提取人物信息，并以JSON格式输出。",
        schema=json_schema,
        input_data="张三，28岁，精通Python和JavaScript，有5年工作经验，曾在阿里巴巴和腾讯工作。"
    )

    if result1["success"]:
        print(f"任务: {result1['task']}")
        print(f"输入: {result1['input']}")
        if result1.get("valid_json"):
            print(f"\nJSON输出:")
            print(json.dumps(result1['output'], ensure_ascii=False, indent=2))
        else:
            print(f"\n原始输出:\n{result1['output']}")
            print(f"警告: {result1.get('error', 'JSON格式不正确')}")
    else:
        print(f"错误: {result1['error']}")

    # 示例2：表格格式输出
    print("\n" + "=" * 60)
    print("示例2: 表格格式输出")
    print("=" * 60)

    result2 = formatter.table_output(
        task="将以下编程语言信息整理成表格。",
        columns=["语言", "类型", "难度", "主要用途"],
        input_data="Python是动态类型语言，难度中等，用于数据分析和Web开发。Java是静态类型语言，难度较高，用于企业级应用。JavaScript是动态类型语言，难度中等，用于前端开发。"
    )

    if result2["success"]:
        print(f"任务: {result2['task']}")
        print(f"\n表格输出:\n{result2['output']}")
    else:
        print(f"错误: {result2['error']}")

    # 示例3：结构化列表输出
    print("\n" + "=" * 60)
    print("示例3: 结构化列表输出")
    print("=" * 60)

    result3 = formatter.structured_list_output(
        task="将以下项目需求整理成结构化的任务列表。",
        input_data="需要开发一个用户管理系统，包括用户注册、登录、权限管理和数据统计功能。"
    )

    if result3["success"]:
        print(f"任务: {result3['task']}")
        print(f"\n列表输出:\n{result3['output'][:500]}...")
    else:
        print(f"错误: {result3['error']}")

    # 示例4：代码格式输出
    print("\n" + "=" * 60)
    print("示例4: 代码格式输出")
    print("=" * 60)

    result4 = formatter.code_output(
        task="编写一个Python函数",
        language="Python",
        input_data="实现一个函数，计算列表中所有数字的平均值，要求处理空列表和非数字元素的情况。"
    )

    if result4["success"]:
        print(f"任务: {result4['task']}")
        print(f"语言: {result4['language']}")
        print(f"\n代码输出:\n{result4['output'][:500]}...")
    else:
        print(f"错误: {result4['error']}")

    # 示例5：多段落输出
    print("\n" + "=" * 60)
    print("示例5: 多段落结构化输出")
    print("=" * 60)

    result5 = formatter.multi_section_output(
        task="撰写一篇技术文章",
        sections=["概述", "核心功能", "技术架构", "应用场景", "总结"],
        input_data="介绍Docker容器技术"
    )

    if result5["success"]:
        print(f"任务: {result5['task']}")
        print(f"\n文章输出:\n{result5['output'][:500]}...")
    else:
        print(f"错误: {result5['error']}")

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
