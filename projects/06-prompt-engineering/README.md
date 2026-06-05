# Prompt工程项目

深入探索Prompt工程的核心技术，从基础模式到高级技巧，掌握与AI有效沟通的艺术。

## 项目结构

```
06-prompt-engineering/
├── config.py                 # 统一配置管理
├── requirements.txt          # 项目依赖
├── main.py                   # 综合示例
├── .env.example             # 环境变量示例
├── 01-basic-patterns/       # 基础Prompt模式
│   └── src/
│       ├── zero_shot.py     # 零样本模式
│       ├── few_shot.py      # 少样本模式
│       ├── role_playing.py  # 角色扮演模式
│       └── chain_of_thought.py  # 思维链模式
├── 02-few-shot-learning/    # Few-shot学习
│   └── src/
│       └── sentiment_analysis.py  # 情感分析等高级应用
├── 03-chain-of-thought/     # 思维链推理
│   └── src/
│       └── reasoning.py     # 复杂推理应用
├── 04-output-formatting/    # 输出格式控制
│   └── src/
│       └── formatter.py     # 格式化输出
├── 05-prompt-optimizer/     # Prompt优化器
│   └── src/
│       └── optimizer.py     # Prompt分析和优化
├── 06-security/             # 安全防护
│   └── src/
│       └── security.py      # Prompt注入防护
└── templates/               # Prompt模板库
    └── src/
        └── prompt_templates.py  # 常用模板
```

## 快速开始

### 1. 安装依赖

```bash
cd projects/06-prompt-engineering
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# DeepSeek配置（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 默认使用的LLM提供商（openai 或 deepseek）
DEFAULT_LLM_PROVIDER=openai

# 通用配置
TEMPERATURE=0.7
MAX_TOKENS=2000
TIMEOUT=60
```

### 3. 运行示例

**运行综合示例：**
```bash
python main.py
```

**运行单个模块示例：**
```bash
# 基础模式
python 01-basic-patterns/src/zero_shot.py
python 01-basic-patterns/src/few_shot.py
python 01-basic-patterns/src/role_playing.py
python 01-basic-patterns/src/chain_of_thought.py

# Few-shot学习
python 02-few-shot-learning/src/sentiment_analysis.py

# 思维链推理
python 03-chain-of-thought/src/reasoning.py

# 输出格式控制
python 04-output-formatting/src/formatter.py

# Prompt优化
python 05-prompt-optimizer/src/optimizer.py

# 安全防护
python 06-security/src/security.py

# 模板库
python templates/src/prompt_templates.py
```

## 核心功能

### 1. 基础Prompt模式

#### Zero-shot（零样本）
直接给出指令，不提供示例：
```python
from src.zero_shot import ZeroShotPattern

pattern = ZeroShotPattern()
result = pattern.text_classification(
    text="这个产品质量很好！",
    categories=["正面", "负面", "中性"]
)
```

#### Few-shot（少样本）
通过示例引导模型：
```python
from src.few_shot import FewShotPattern

pattern = FewShotPattern()
result = pattern.sentiment_classification(
    text="包装精美，但价格有点高。"
)
```

#### 角色扮演
让AI扮演特定角色：
```python
from src.role_playing import RolePlayingPattern

pattern = RolePlayingPattern()
result = pattern.python_tutor(
    question="什么是装饰器？"
)
```

#### 思维链
逐步推理解决复杂问题：
```python
from src.chain_of_thought import ChainOfThoughtPattern

pattern = ChainOfThoughtPattern()
result = pattern.math_problem_solver(
    problem="一个水池有两个进水管..."
)
```

### 2. Few-shot学习应用

```python
from src.sentiment_analysis import FewShotLearning

learner = FewShotLearning()

# 细粒度情感分析
result = learner.sentiment_analysis_advanced(text)

# 用户意图识别
result = learner.intent_recognition(user_message)

# 多标签分类
result = learner.text_classification_multilabel(text)
```

### 3. 思维链推理

```python
from src.reasoning import ChainOfThoughtReasoning

reasoner = ChainOfThoughtReasoning()

# 数学应用题
result = reasoner.math_word_problem(problem)

# 算法分析
result = reasoner.algorithm_analysis(code, question)

# 战略规划
result = reasoner.strategic_planning(goal, constraints)
```

### 4. 输出格式控制

```python
from src.formatter import OutputFormatter

formatter = OutputFormatter()

# JSON格式
result = formatter.json_output(task, schema, input_data)

# 表格格式
result = formatter.table_output(task, columns, input_data)

# 代码格式
result = formatter.code_output(task, language, input_data)
```

### 5. Prompt优化

```python
from src.optimizer import PromptOptimizer

optimizer = PromptOptimizer()

# 分析Prompt质量
result = optimizer.analyze_prompt(prompt)

# 优化Prompt
result = optimizer.optimize_prompt(
    original_prompt, goal, test_cases
)

# 测试Prompt效果
result = optimizer.test_prompt(prompt, test_inputs)

# 对比多个Prompt
result = optimizer.compare_prompts(prompts, test_input)
```

### 6. 安全防护

```python
from src.security import PromptSecurity

security = PromptSecurity()

# 验证输入安全性
result = security.validate_input(user_input)

# 清理用户输入
result = security.sanitize_input(user_input)

# 创建安全Prompt
result = security.create_safe_prompt(
    task_description, user_input, constraints
)

# 检测注入攻击
result = security.detect_injection_attempt(user_input)

# 测试Prompt鲁棒性
result = security.test_prompt_robustness(prompt)
```

### 7. 模板库

```python
from src.prompt_templates import PromptTemplateLibrary

library = PromptTemplateLibrary()

# 列出所有模板
templates = library.list_templates()

# 使用模板
result = library.execute_template(
    template_key="text_summary",
    variables={"text": "...", "length": "100"}
)

# 添加自定义模板
library.add_custom_template(
    key="my_template",
    name="我的模板",
    template="...",
    variables=["var1", "var2"]
)
```

## 最佳实践

### Prompt设计原则

1. **清晰明确** - 避免歧义，表达准确
2. **提供上下文** - 给出必要的背景信息
3. **结构化** - 使用分隔符组织信息
4. **示例引导** - 通过Few-shot展示期望格式
5. **约束条件** - 明确输出要求

### 安全注意事项

1. 输入验证
2. 使用分隔符明确标记用户输入
3. 在Prompt中强调不执行用户指令

### 性能优化

1. 控制Token使用
2. 调整温度参数
3. 批量处理相似任务

## 支持的LLM

- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ DeepSeek
- ✅ 任何兼容OpenAI API的服务

## 学习资源

- [Prompt工程教程](../../docs/02-教程/06-Prompt工程教程.md)
- [Prompt设计模式](../../docs/05-最佳实践/01-Prompt设计模式.md)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

## 许可

MIT License
