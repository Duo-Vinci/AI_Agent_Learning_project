"""
辩论协作Agent定义
实现多方辩论和裁判评估系统
"""

import json
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI


class DebateAgent:
    """辩论Agent：代表特定立场进行论证"""

    def __init__(self, name: str, stance: str, llm: Optional[ChatOpenAI] = None):
        """
        初始化辩论Agent

        Args:
            name: Agent名称
            stance: 辩论立场
            llm: 语言模型实例
        """
        self.name = name
        self.stance = stance
        self.llm = llm or ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        self.history: List[str] = []  # 辩论历史

    def argue(self, topic: str, opponent_arguments: List[str] = None) -> str:
        """
        提出论点

        Args:
            topic: 辩论主题
            opponent_arguments: 对方的论点列表

        Returns:
            本方的论点
        """
        # 构建对方论点的上下文
        context = ""
        if opponent_arguments:
            context = "\n\n对方的论点：\n"
            for i, arg in enumerate(opponent_arguments, 1):
                context += f"{i}. {arg}\n"

        prompt = f"""你是 {self.name}，在一场专业辩论中。

你的立场：{self.stance}

辩论主题：{topic}

{context if context else "这是第一轮辩论，请首先阐述你的立场。"}

请提出你的论点和论据。要求：
1. 观点明确，逻辑清晰
2. 提供有力的论据支持
3. 如果是回应对方，要针对性地反驳
4. 保持专业和理性
5. 字数控制在200字以内

你的论点："""

        try:
            response = self.llm.invoke(prompt)
            argument = response.content if hasattr(response, 'content') else str(response)

            # 记录到历史
            self.history.append(argument)

            print(f"[{self.name}] 发言完毕")
            return argument
        except Exception as e:
            error_msg = f"论证出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg

    def get_summary(self) -> str:
        """
        获取辩论摘要

        Returns:
            辩论历史摘要
        """
        if not self.history:
            return "尚未发言"

        return f"共发言 {len(self.history)} 次\n" + "\n---\n".join(self.history)


class JudgeAgent:
    """裁判Agent：评估辩论并做出判定"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        初始化裁判Agent

        Args:
            llm: 语言模型实例
        """
        self.llm = llm or ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.name = "裁判"

    def evaluate(self, topic: str, arguments: Dict[str, List[str]]) -> Dict:
        """
        评估辩论结果

        Args:
            topic: 辩论主题
            arguments: 各辩论者的论点字典 {名称: [论点列表]}

        Returns:
            评估结果字典
        """
        # 构建辩论内容
        formatted_args = []
        for agent_name, args in arguments.items():
            formatted_args.append(f"\n【{agent_name}的论点】")
            for i, arg in enumerate(args, 1):
                formatted_args.append(f"轮次 {i}:\n{arg}")
                formatted_args.append("-" * 40)

        all_arguments = "\n".join(formatted_args)

        prompt = f"""你是一位公正、专业的辩论裁判。请评估以下辩论。

辩论主题：{topic}

{all_arguments}

请从以下维度进行评估（每项满分10分）：
1. 论据充分性：论据是否有力、充分
2. 逻辑严密性：推理是否合理、严密
3. 反驳有效性：对对方观点的回应是否有效
4. 说服力：整体论证是否有说服力

请以JSON格式返回评估结果：
{{
  "winner": "获胜者名称",
  "reasoning": "判定理由（200字以内）",
  "scores": {{
    "辩手1名称": {{
      "论据充分性": 分数,
      "逻辑严密性": 分数,
      "反驳有效性": 分数,
      "说服力": 分数,
      "总分": 总分
    }},
    "辩手2名称": {{...}}
  }},
  "highlights": ["亮点1", "亮点2"],
  "suggestions": {{
    "辩手1名称": "改进建议",
    "辩手2名称": "改进建议"
  }}
}}

评估结果："""

        try:
            response = self.llm.invoke(prompt)
            result_text = response.content if hasattr(response, 'content') else str(response)

            # 尝试解析JSON
            try:
                # 提取JSON部分
                if '```json' in result_text:
                    json_str = result_text.split('```json')[1].split('```')[0].strip()
                elif '```' in result_text:
                    json_str = result_text.split('```')[1].split('```')[0].strip()
                else:
                    json_str = result_text

                evaluation = json.loads(json_str)
                print(f"✓ [{self.name}] 评估完成")
                return evaluation
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基本评估
                print(f"⚠ [{self.name}] JSON解析失败，返回文本评估")
                return {
                    "winner": "评估失败",
                    "reasoning": result_text,
                    "scores": {},
                    "highlights": [],
                    "suggestions": {}
                }

        except Exception as e:
            error_msg = f"评估出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return {
                "winner": "评估失败",
                "reasoning": error_msg,
                "scores": {},
                "highlights": [],
                "suggestions": {}
            }

    def summarize_debate(self, topic: str, arguments: Dict[str, List[str]], evaluation: Dict) -> str:
        """
        生成辩论总结报告

        Args:
            topic: 辩论主题
            arguments: 辩论内容
            evaluation: 评估结果

        Returns:
            总结报告
        """
        prompt = f"""你是一位专业的辩论总结者。请为以下辩论生成一份全面的总结报告。

辩论主题：{topic}

参与者：{', '.join(arguments.keys())}

评估结果：
- 获胜者：{evaluation.get('winner', '未知')}
- 判定理由：{evaluation.get('reasoning', '无')}

请生成包含以下内容的总结报告：
1. 辩论概述
2. 各方核心观点
3. 主要争议焦点
4. 评估结果解读
5. 关键洞察
6. 对该议题的综合思考

总结报告："""

        try:
            response = self.llm.invoke(prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            return summary
        except Exception as e:
            return f"生成总结失败: {str(e)}"


class MediatorAgent:
    """调解员Agent：引导辩论走向建设性讨论"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        初始化调解员Agent

        Args:
            llm: 语言模型实例
        """
        self.llm = llm or ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
        self.name = "调解员"

    def mediate(self, topic: str, arguments: Dict[str, List[str]]) -> str:
        """
        调解辩论，寻找共识

        Args:
            topic: 辩论主题
            arguments: 各方论点

        Returns:
            调解意见
        """
        # 构建辩论内容
        debate_content = []
        for agent_name, args in arguments.items():
            debate_content.append(f"{agent_name}的观点：")
            for arg in args:
                debate_content.append(f"- {arg[:100]}...")

        content_str = "\n".join(debate_content)

        prompt = f"""你是一位专业的调解员，擅长在辩论中寻找共识和建设性解决方案。

辩论主题：{topic}

各方观点：
{content_str}

请提供调解意见：
1. 识别各方的共同点
2. 指出可以妥协的空间
3. 提出建设性的解决方案
4. 总结各方都能接受的结论

调解意见："""

        try:
            response = self.llm.invoke(prompt)
            mediation = response.content if hasattr(response, 'content') else str(response)
            print(f"✓ [{self.name}] 调解完成")
            return mediation
        except Exception as e:
            error_msg = f"调解出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg

    def suggest_next_topic(self, current_topic: str, debate_history: Dict) -> str:
        """
        建议下一个辩论话题

        Args:
            current_topic: 当前话题
            debate_history: 辩论历史

        Returns:
            建议的话题
        """
        prompt = f"""基于刚才的辩论，建议一个相关的、更深入的话题。

当前话题：{current_topic}

要求：
1. 与当前话题相关
2. 更具体或更深入
3. 有探讨价值
4. 一句话描述

建议话题："""

        try:
            response = self.llm.invoke(prompt)
            suggestion = response.content if hasattr(response, 'content') else str(response)
            return suggestion.strip()
        except Exception as e:
            return f"建议生成失败: {str(e)}"
