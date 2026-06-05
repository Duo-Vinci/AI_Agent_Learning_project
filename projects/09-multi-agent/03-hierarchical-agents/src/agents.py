"""
层级协作Agent定义
实现Manager-Worker模式的多Agent系统
"""

import json
from typing import List, Dict, Tuple, Optional
from langchain_openai import ChatOpenAI


class WorkerAgent:
    """工作者Agent：执行具体任务"""

    def __init__(self, name: str, skills: List[str], llm: Optional[ChatOpenAI] = None):
        """
        初始化工作者Agent

        Args:
            name: Agent名称
            skills: 技能列表
            llm: 语言模型实例
        """
        self.name = name
        self.skills = skills
        self.llm = llm or ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        self.completed_tasks = []

    def can_handle(self, required_skill: str) -> bool:
        """
        检查是否具备所需技能

        Args:
            required_skill: 所需技能

        Returns:
            是否具备该技能
        """
        return required_skill.lower() in [s.lower() for s in self.skills]

    def execute(self, task: str) -> str:
        """
        执行任务

        Args:
            task: 任务描述

        Returns:
            执行结果
        """
        prompt = f"""你是一个专业的 {', '.join(self.skills)} 专家。
你的名字是 {self.name}。

请完成以下任务：
{task}

要求：
1. 充分发挥你的专业能力
2. 提供详细的执行过程
3. 给出高质量的结果

执行结果："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)

            # 记录完成的任务
            self.completed_tasks.append({
                'task': task,
                'result': result
            })

            print(f"✓ [{self.name}] 任务完成")
            return result
        except Exception as e:
            error_msg = f"任务执行出错: {str(e)}"
            print(f"✗ [{self.name}] {error_msg}")
            return error_msg

    def get_status(self) -> Dict:
        """
        获取Agent状态

        Returns:
            状态信息字典
        """
        return {
            'name': self.name,
            'skills': self.skills,
            'completed_tasks': len(self.completed_tasks)
        }


class ManagerAgent:
    """管理者Agent：负责任务分解、分配和结果整合"""

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        初始化管理者Agent

        Args:
            llm: 语言模型实例
        """
        self.llm = llm or ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
        self.name = "项目经理"
        self.workers: List[WorkerAgent] = []

    def add_worker(self, worker: WorkerAgent):
        """
        添加工作者

        Args:
            worker: 工作者Agent实例
        """
        self.workers.append(worker)
        print(f"✓ 添加工作者: {worker.name} (技能: {', '.join(worker.skills)})")

    def decompose_task(self, task: str) -> List[Dict]:
        """
        分解任务为子任务

        Args:
            task: 主任务描述

        Returns:
            子任务列表
        """
        # 获取可用技能
        available_skills = []
        for worker in self.workers:
            available_skills.extend(worker.skills)
        available_skills = list(set(available_skills))

        prompt = f"""你是一个项目经理。请将以下任务分解为可以并行执行的子任务。

主任务：{task}

可用的技能：{', '.join(available_skills)}

请将任务分解为3-5个子任务，并以JSON格式输出：
[
  {{
    "id": "1",
    "description": "子任务的详细描述",
    "required_skill": "所需技能（必须从可用技能中选择）",
    "priority": "high/medium/low",
    "estimated_time": "预计时间"
  }}
]

注意：
1. 每个子任务应该清晰、具体、可执行
2. required_skill必须是可用技能之一
3. 子任务之间应该相对独立

子任务列表："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)

            # 尝试解析JSON
            try:
                # 提取JSON部分
                if '```json' in result:
                    json_str = result.split('```json')[1].split('```')[0].strip()
                elif '```' in result:
                    json_str = result.split('```')[1].split('```')[0].strip()
                else:
                    json_str = result

                subtasks = json.loads(json_str)
                print(f"✓ [{self.name}] 任务分解完成，共 {len(subtasks)} 个子任务")
                return subtasks
            except json.JSONDecodeError as e:
                print(f"⚠ [{self.name}] JSON解析失败: {str(e)}")
                # 返回默认的子任务
                return self._create_default_subtasks(task, available_skills)

        except Exception as e:
            print(f"✗ [{self.name}] 任务分解出错: {str(e)}")
            return self._create_default_subtasks(task, available_skills)

    def _create_default_subtasks(self, task: str, skills: List[str]) -> List[Dict]:
        """创建默认的子任务列表"""
        return [
            {
                "id": "1",
                "description": f"研究和分析：{task}",
                "required_skill": skills[0] if skills else "research",
                "priority": "high"
            },
            {
                "id": "2",
                "description": f"执行核心工作：{task}",
                "required_skill": skills[1] if len(skills) > 1 else skills[0],
                "priority": "high"
            },
            {
                "id": "3",
                "description": f"质量检查和优化：{task}",
                "required_skill": skills[-1] if skills else "review",
                "priority": "medium"
            }
        ]

    def assign_tasks(self, subtasks: List[Dict]) -> List[Tuple[WorkerAgent, Dict]]:
        """
        分配任务给合适的Worker

        Args:
            subtasks: 子任务列表

        Returns:
            (Worker, 子任务)的配对列表
        """
        assignments = []

        for subtask in subtasks:
            required_skill = subtask.get('required_skill', '')
            best_worker = self._find_best_worker(required_skill)

            if best_worker:
                assignments.append((best_worker, subtask))
                print(f"  ├─ 子任务 {subtask['id']}: {subtask['description'][:50]}...")
                print(f"  │  分配给: {best_worker.name}")
            else:
                print(f"  ├─ ⚠ 子任务 {subtask['id']}: 没有合适的Worker")

        return assignments

    def _find_best_worker(self, required_skill: str) -> Optional[WorkerAgent]:
        """
        根据技能选择最佳Worker

        Args:
            required_skill: 所需技能

        Returns:
            最合适的Worker，如果没有则返回None
        """
        # 首先查找完全匹配的
        for worker in self.workers:
            if worker.can_handle(required_skill):
                # 选择任务最少的
                return min(
                    [w for w in self.workers if w.can_handle(required_skill)],
                    key=lambda w: len(w.completed_tasks)
                )

        # 如果没有完全匹配，返回任务最少的Worker
        if self.workers:
            return min(self.workers, key=lambda w: len(w.completed_tasks))

        return None

    def execute_plan(self, task: str) -> str:
        """
        执行完整的任务计划

        Args:
            task: 主任务描述

        Returns:
            最终整合的结果
        """
        print(f"\n[{self.name}] 开始规划任务...")
        print("=" * 60)

        # 步骤1: 分解任务
        print(f"\n[步骤 1/3] 任务分解")
        print("-" * 60)
        subtasks = self.decompose_task(task)

        # 步骤2: 分配任务
        print(f"\n[步骤 2/3] 任务分配")
        print("-" * 60)
        assignments = self.assign_tasks(subtasks)

        if not assignments:
            return "错误: 没有可用的Worker来执行任务"

        # 步骤3: 执行子任务
        print(f"\n[步骤 3/3] 执行任务")
        print("-" * 60)
        results = []

        for i, (worker, subtask) in enumerate(assignments, 1):
            print(f"\n执行子任务 {i}/{len(assignments)}: {subtask['description'][:60]}...")
            result = worker.execute(subtask['description'])
            results.append({
                'subtask_id': subtask['id'],
                'subtask_description': subtask['description'],
                'worker': worker.name,
                'result': result
            })

        # 步骤4: 整合结果
        print(f"\n[{self.name}] 整合结果...")
        print("-" * 60)
        final_result = self._integrate_results(task, results)

        print(f"✓ [{self.name}] 任务完成！")
        return final_result

    def _integrate_results(self, original_task: str, results: List[Dict]) -> str:
        """
        整合所有子任务的结果

        Args:
            original_task: 原始任务
            results: 所有子任务的执行结果

        Returns:
            整合后的最终结果
        """
        # 构建结果概览
        results_summary = "\n\n".join([
            f"子任务 {r['subtask_id']} ({r['worker']}):\n{r['subtask_description']}\n结果:\n{r['result']}"
            for r in results
        ])

        prompt = f"""你是一个项目经理，需要整合团队成员的工作成果。

原始任务：{original_task}

团队成员的工作成果：
{results_summary}

请整合以上所有成果，生成一份完整的、连贯的最终报告。要求：
1. 综合所有子任务的结果
2. 确保内容连贯、逻辑清晰
3. 突出关键发现和结论
4. 结构化呈现（使用标题、列表等）

最终报告："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            return result
        except Exception as e:
            return f"整合结果时出错: {str(e)}\n\n原始结果:\n{results_summary}"

    def get_team_status(self) -> Dict:
        """
        获取团队状态

        Returns:
            团队状态信息
        """
        return {
            'manager': self.name,
            'total_workers': len(self.workers),
            'workers': [w.get_status() for w in self.workers]
        }
