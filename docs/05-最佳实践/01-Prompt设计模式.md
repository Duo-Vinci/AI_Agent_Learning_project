# Prompt设计模式

## 1. 概述

Prompt工程是AI应用开发的核心技能。本文档总结了常用的Prompt设计模式和技巧，帮助开发者编写更有效的提示词。

## 2. 核心设计原则

### 2.1 清晰性原则
- 明确具体的指令
- 避免歧义表达
- 提供必要的上下文
- 定义期望的输出格式

### 2.2 结构化原则
- 使用标记分隔不同部分
- 逻辑层次清晰
- 便于模型理解和解析

### 2.3 示例引导原则
- 提供少样本示例（Few-shot）
- 示例要有代表性
- 展示期望的输出格式

## 3. 常用Prompt设计模式

### 3.1 角色扮演模式（Role-Playing Pattern）

**适用场景**：需要特定专业领域的回答

**模式结构**：
```
你是一个[专业角色]，具有[专业特长]。
请以[角色身份]的方式回答以下问题：
[具体问题]
```

**代码示例**：
```python
from openai import OpenAI

client = OpenAI()

def role_playing_prompt(role, expertise, question):
    """角色扮演模式"""
    prompt = f"""你是一个{role}，具有{expertise}。
请以专业的角度分析并回答以下问题：

问题：{question}

请提供：
1. 专业分析
2. 具体建议
3. 潜在风险提示
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"你是一个{role}，擅长{expertise}"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# 使用示例
result = role_playing_prompt(
    role="资深Python架构师",
    expertise="微服务架构设计和性能优化",
    question="如何设计一个高并发的用户认证系统？"
)
print(result)
```

### 3.2 思维链模式（Chain-of-Thought Pattern）

**适用场景**：复杂推理、数学问题、逻辑分析

**模式结构**：
```
请一步步分析以下问题：
[问题描述]

分析过程：
1. 理解问题
2. 分解子问题
3. 逐步求解
4. 验证结果
```

**代码示例**：
```python
def chain_of_thought_prompt(problem):
    """思维链模式"""
    prompt = f"""请一步步分析并解决以下问题：

问题：{problem}

请按以下步骤思考：
1. 问题理解：明确问题要求什么
2. 信息提取：识别关键信息和条件
3. 方案设计：设计解决步骤
4. 逐步求解：按步骤计算
5. 结果验证：检查答案合理性

让我们开始：
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个逻辑清晰的问题解决专家"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# 使用示例
problem = """
一个水池有两个进水管和一个出水管。
甲管单独开需要4小时注满，乙管单独开需要6小时注满，
丙管单独开需要12小时放空。
如果三管同时打开，需要多少小时注满？
"""

result = chain_of_thought_prompt(problem)
print(result)
```

### 3.3 少样本学习模式（Few-Shot Learning Pattern）

**适用场景**：格式化输出、分类任务、风格模仿

**模式结构**：
```
以下是一些示例：

示例1：
输入：[示例输入1]
输出：[示例输出1]

示例2：
输入：[示例输入2]
输出：[示例输出2]

现在请处理：
输入：[实际输入]
输出：
```

**代码示例**：
```python
def few_shot_learning(task_description, examples, input_data):
    """少样本学习模式"""
    # 构建示例部分
    examples_text = ""
    for i, example in enumerate(examples, 1):
        examples_text += f"""
示例{i}：
输入：{example['input']}
输出：{example['output']}
"""
    
    prompt = f"""{task_description}

{examples_text}

现在请处理以下输入，输出格式与示例保持一致：
输入：{input_data}
输出："""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    return response.choices[0].message.content

# 使用示例：情感分析
examples = [
    {
        "input": "这个产品质量很好，物流也很快！",
        "output": "积极 | 置信度：0.95 | 关键词：质量好、物流快"
    },
    {
        "input": "服务态度差，东西还贵。",
        "output": "消极 | 置信度：0.92 | 关键词：态度差、贵"
    },
    {
        "input": "还行吧，没什么特别的。",
        "output": "中性 | 置信度：0.88 | 关键词：还行、没特别"
    }
]

result = few_shot_learning(
    task_description="请分析以下评论的情感倾向，并提取关键词",
    examples=examples,
    input_data="包装精美，但价格有点高"
)
print(result)
```

### 3.4 模板填充模式（Template Filling Pattern）

**适用场景**：结构化内容生成、报告生成、代码生成

**模式结构**：
```
请按照以下模板生成内容：

【模板】
部分1：[说明]
部分2：[说明]
部分3：[说明]

【要求】
- 要求1
- 要求2

【输入信息】
[实际数据]
```

**代码示例**：
```python
def template_filling(template, requirements, data):
    """模板填充模式"""
    prompt = f"""请根据以下模板和数据生成内容：

【模板】
{template}

【要求】
{chr(10).join(f"- {req}" for req in requirements)}

【输入数据】
{data}

请严格按照模板格式输出：
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    
    return response.choices[0].message.content

# 使用示例：生成产品文档
template = """
# 产品名称

## 1. 产品概述
[一句话描述产品]

## 2. 核心功能
- 功能1：[描述]
- 功能2：[描述]
- 功能3：[描述]

## 3. 技术特点
[技术亮点]

## 4. 适用场景
[使用场景描述]

## 5. 快速开始
[简要使用说明]
"""

requirements = [
    "语言简洁专业",
    "突出技术优势",
    "包含实际应用场景",
    "适合技术人员阅读"
]

data = """
产品：SmartCache分布式缓存系统
功能：高性能缓存、自动扩缩容、多级缓存、数据持久化
技术：基于Redis集群、支持一致性哈希、提供Go/Python SDK
场景：电商、社交、游戏等高并发场景
"""

result = template_filling(template, requirements, data)
print(result)
```

### 3.5 约束条件模式（Constraint Pattern）

**适用场景**：需要精确控制输出的场景

**模式结构**：
```
请完成以下任务，并严格遵守以下约束：

【任务】
[任务描述]

【约束条件】
1. 必须条件1
2. 必须条件2
3. 禁止条件1
4. 禁止条件2

【输入】
[数据]
```

**代码示例**：
```python
def constraint_prompt(task, constraints, forbidden, input_data):
    """约束条件模式"""
    prompt = f"""请完成以下任务：

【任务】
{task}

【必须遵守的约束】
{chr(10).join(f"{i+1}. {c}" for i, c in enumerate(constraints))}

【严格禁止】
{chr(10).join(f"{i+1}. {f}" for i, f in enumerate(forbidden))}

【输入】
{input_data}

请严格按照约束条件完成任务：
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# 使用示例：生成儿童故事
result = constraint_prompt(
    task="创作一个有教育意义的儿童故事",
    constraints=[
        "故事长度150-200字",
        "必须包含友谊或勇气的主题",
        "语言简单易懂，适合6-8岁儿童",
        "有明确的道德教育意义",
        "结局必须是积极正面的"
    ],
    forbidden=[
        "不能出现暴力场景",
        "不能有恐怖元素",
        "不能使用复杂词汇",
        "不能传递负面价值观"
    ],
    input_data="主角：小兔子和小松鼠，场景：森林"
)
print(result)
```

### 3.6 反思修正模式（Reflection Pattern）

**适用场景**：需要自我检查和改进的任务

**模式结构**：
```
第一步：完成初步方案
第二步：反思并找出问题
第三步：给出改进方案
```

**代码示例**：
```python
def reflection_prompt(task):
    """反思修正模式"""
    prompt = f"""请完成以下任务，并采用三步反思法：

任务：{task}

第一步 - 初步方案：
请先给出你的初步解决方案。

第二步 - 反思分析：
请批判性地审视你的方案，思考：
- 有哪些潜在问题？
- 是否有遗漏的情况？
- 是否有更优的方法？
- 有哪些风险点？

第三步 - 改进方案：
基于反思，给出改进后的最终方案。

请按照以上三步完成任务：
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    
    return response.choices[0].message.content

# 使用示例
result = reflection_prompt(
    "设计一个用户密码安全存储方案"
)
print(result)
```

### 3.7 分步执行模式（Step-by-Step Pattern）

**适用场景**：复杂任务分解、多步骤流程

**代码示例**：
```python
def step_by_step_prompt(task, steps):
    """分步执行模式"""
    steps_text = "\n".join(f"步骤{i+1}：{step}" for i, step in enumerate(steps))
    
    prompt = f"""请完成以下任务，严格按照指定步骤执行：

【任务】
{task}

【执行步骤】
{steps_text}

请逐步执行，每完成一步就输出该步的结果，然后再进行下一步：
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# 使用示例：代码审查
result = step_by_step_prompt(
    task="审查以下Python函数的质量",
    steps=[
        "检查代码规范性（命名、格式、注释）",
        "分析时间和空间复杂度",
        "识别潜在的bug和边界情况",
        "评估可读性和可维护性",
        "提出具体改进建议"
    ]
)
print(result)
```

## 4. 高级技巧

### 4.1 Prompt链式调用

**场景**：将复杂任务分解为多个简单Prompt

```python
class PromptChain:
    """Prompt链式调用"""
    
    def __init__(self, client):
        self.client = client
        self.history = []
    
    def execute_step(self, prompt, context=None):
        """执行单个步骤"""
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.5
        )
        
        result = response.choices[0].message.content
        self.history.append({"prompt": prompt, "result": result})
        return result
    
    def get_context(self, steps_back=1):
        """获取之前步骤的上下文"""
        if not self.history:
            return ""
        return "\n\n".join(
            f"前序步骤{i+1}结果：\n{h['result']}" 
            for i, h in enumerate(self.history[-steps_back:])
        )

# 使用示例：文章写作流程
chain = PromptChain(client)

# 步骤1：生成大纲
outline = chain.execute_step("""
请为"Python异步编程最佳实践"这个主题生成文章大纲。
要求：
- 3-5个主要章节
- 每个章节2-3个小节
- 逻辑清晰，由浅入深
""")

print("大纲：\n", outline)

# 步骤2：扩展第一章
context = chain.get_context(1)
chapter1 = chain.execute_step("""
基于上面的大纲，请详细撰写第一章的内容。
要求：
- 800-1000字
- 包含代码示例
- 通俗易懂
""", context)

print("\n第一章：\n", chapter1)

# 步骤3：生成总结
context = chain.get_context(2)
summary = chain.execute_step("""
请为这篇文章生成一个精炼的总结（200字以内）
""", context)

print("\n总结：\n", summary)
```

### 4.2 动态Prompt生成

**场景**：根据上下文动态调整Prompt

```python
class DynamicPromptGenerator:
    """动态Prompt生成器"""
    
    def __init__(self):
        self.user_level_prompts = {
            "beginner": "请用简单易懂的语言解释，避免使用专业术语",
            "intermediate": "请提供适度技术细节，可以使用常见术语",
            "advanced": "请提供深入的技术分析，包含底层原理"
        }
        
        self.task_type_prompts = {
            "explanation": "请详细解释概念，包含原理和示例",
            "tutorial": "请提供分步教程，包含可运行的代码",
            "comparison": "请对比分析，列出优缺点和适用场景",
            "troubleshooting": "请分析问题原因并提供解决方案"
        }
    
    def generate(self, task_type, user_level, question, extra_requirements=None):
        """生成动态Prompt"""
        base_prompt = f"""
{self.task_type_prompts.get(task_type, '')}
{self.user_level_prompts.get(user_level, '')}

问题：{question}
"""
        
        if extra_requirements:
            base_prompt += f"\n额外要求：\n"
            base_prompt += "\n".join(f"- {req}" for req in extra_requirements)
        
        return base_prompt

# 使用示例
generator = DynamicPromptGenerator()

# 为初学者生成教程
prompt1 = generator.generate(
    task_type="tutorial",
    user_level="beginner",
    question="如何使用Python操作JSON数据？",
    extra_requirements=["包含完整代码示例", "解释每行代码的作用"]
)

# 为高级用户生成对比分析
prompt2 = generator.generate(
    task_type="comparison",
    user_level="advanced",
    question="asyncio vs threading vs multiprocessing",
    extra_requirements=["包含性能测试", "分析底层实现差异"]
)

print("初学者Prompt：\n", prompt1)
print("\n高级Prompt：\n", prompt2)
```

### 4.3 Prompt优化器

**场景**：自动优化和测试Prompt效果

```python
class PromptOptimizer:
    """Prompt优化器"""
    
    def __init__(self, client):
        self.client = client
    
    def optimize(self, original_prompt, test_cases, optimization_goal):
        """优化Prompt"""
        optimization_prompt = f"""
你是一个Prompt工程专家。请优化以下Prompt，使其{optimization_goal}。

【原始Prompt】
{original_prompt}

【测试用例】
{chr(10).join(f"{i+1}. {tc}" for i, tc in enumerate(test_cases))}

请提供：
1. 问题分析：原Prompt存在什么问题？
2. 优化建议：应该如何改进？
3. 优化后的Prompt：给出改进版本
4. 预期改进效果：优化后会有什么提升？
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": optimization_prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def test_prompt(self, prompt, test_inputs):
        """测试Prompt效果"""
        results = []
        for test_input in test_inputs:
            full_prompt = f"{prompt}\n\n输入：{test_input}"
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.3
            )
            results.append({
                "input": test_input,
                "output": response.choices[0].message.content
            })
        return results

# 使用示例
optimizer = PromptOptimizer(client)

original = "请分析这段代码的性能问题"

test_cases = [
    "需要明确输出格式",
    "应该包含具体的改进建议",
    "要考虑不同的性能指标"
]

optimized = optimizer.optimize(
    original_prompt=original,
    test_cases=test_cases,
    optimization_goal="更加具体和可执行"
)

print("优化结果：\n", optimized)
```

## 5. 常见问题和解决方案

### 5.1 输出不稳定

**问题**：相同输入得到不同输出

**解决方案**：
```python
# 1. 降低temperature
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1  # 降低随机性
)

# 2. 使用更明确的约束
prompt = """
请严格按照以下JSON格式输出，不要有任何额外内容：
{
  "result": "分析结果",
  "confidence": 0.95
}
"""

# 3. 使用few-shot示例固定格式
```

### 5.2 输出过长或过短

**问题**：无法控制输出长度

**解决方案**：
```python
prompt = f"""
请用{min_words}-{max_words}字回答以下问题。
要求：
- 字数必须在指定范围内
- 不要为了凑字数而重复
- 保持内容完整性

问题：{question}
"""

# 或使用max_tokens参数
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=500  # 限制最大token数
)
```

### 5.3 理解偏差

**问题**：模型理解错误

**解决方案**：
```python
# 1. 明确定义关键术语
prompt = """
在本任务中：
- "优化"是指提升性能，而非改进功能
- "完成"是指代码可运行，而非产品级质量

任务：{task}
"""

# 2. 提供反例
prompt = """
请提取文本中的日期。

正确示例：
输入："会议定在2024年3月15日"
输出：2024-03-15

错误示例（不要这样）：
输入："大约三天后"
输出：2024-03-18  # 错误！不要推断相对日期

现在请处理：{text}
"""
```

## 6. 最佳实践总结

### 6.1 Prompt编写清单

- [ ] 明确任务目标
- [ ] 提供必要上下文
- [ ] 定义输出格式
- [ ] 设置约束条件
- [ ] 提供示例（如需要）
- [ ] 测试边界情况
- [ ] 迭代优化

### 6.2 质量评估标准

1. **准确性**：输出是否符合预期
2. **稳定性**：多次运行结果是否一致
3. **完整性**：是否涵盖所有要求
4. **效率**：Token使用是否合理
5. **可维护性**：Prompt是否清晰易懂

### 6.3 版本管理

```python
# Prompt版本管理示例
PROMPT_VERSIONS = {
    "v1.0": {
        "prompt": "请分析代码",
        "note": "初始版本，过于简单"
    },
    "v1.1": {
        "prompt": "请分析代码的性能、可读性和安全性",
        "note": "增加了具体维度"
    },
    "v2.0": {
        "prompt": """请从以下维度分析代码：
1. 性能：时间和空间复杂度
2. 可读性：命名、注释、结构
3. 安全性：输入验证、错误处理
4. 可维护性：模块化、可扩展性

每个维度给出：
- 评分（1-10）
- 问题描述
- 改进建议""",
        "note": "结构化输出，更详细的要求"
    }
}

def get_prompt(version="latest"):
    if version == "latest":
        version = max(PROMPT_VERSIONS.keys())
    return PROMPT_VERSIONS[version]["prompt"]
```

## 7. 工具推荐

### 7.1 Prompt测试工具

```python
class PromptTester:
    """Prompt测试工具"""
    
    def __init__(self, client):
        self.client = client
        self.test_results = []
    
    def run_test(self, prompt, test_cases, expected_patterns=None):
        """运行测试"""
        results = {
            "prompt": prompt,
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for i, test_case in enumerate(test_cases):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": f"{prompt}\n\n{test_case['input']}"}],
                    temperature=0.2
                )
                
                output = response.choices[0].message.content
                
                # 检查是否匹配预期模式
                if expected_patterns:
                    import re
                    matched = any(re.search(pattern, output) for pattern in expected_patterns)
                    status = "PASS" if matched else "FAIL"
                else:
                    status = "PASS"
                
                results["details"].append({
                    "case_id": i + 1,
                    "input": test_case["input"],
                    "output": output,
                    "status": status
                })
                
                if status == "PASS":
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                results["details"].append({
                    "case_id": i + 1,
                    "input": test_case["input"],
                    "error": str(e),
                    "status": "ERROR"
                })
                results["failed"] += 1
        
        self.test_results.append(results)
        return results
    
    def generate_report(self):
        """生成测试报告"""
        report = "# Prompt测试报告\n\n"
        for i, result in enumerate(self.test_results, 1):
            total = result["passed"] + result["failed"]
            success_rate = (result["passed"] / total * 100) if total > 0 else 0
            
            report += f"## 测试{i}\n"
            report += f"- 通过：{result['passed']}/{total}\n"
            report += f"- 成功率：{success_rate:.1f}%\n"
            report += f"- Prompt：\n```\n{result['prompt']}\n```\n\n"
        
        return report

# 使用示例
tester = PromptTester(client)

test_cases = [
    {"input": "计算1+1"},
    {"input": "什么是Python"},
    {"input": "解释递归"}
]

result = tester.run_test(
    prompt="请用一句话简洁回答",
    test_cases=test_cases,
    expected_patterns=[r".{10,100}"]  # 期望10-100字符
)

print(tester.generate_report())
```

## 8. 参考资源

- OpenAI Prompt Engineering Guide
- Anthropic Prompt Engineering Tutorial
- LangChain Prompt Templates
- 论文："Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"

---

**更新日期**：2024年3月
**版本**：v2.0
