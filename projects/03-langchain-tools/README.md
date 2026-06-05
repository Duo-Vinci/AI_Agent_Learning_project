# LangChain 工具使用项目

完整的LangChain工具系统，从基础工具创建到实际应用。

## 项目概述

本项目包含多个示例文件，全面展示LangChain工具的使用：
- **01_tool_basics.py**: 工具基础（装饰器、StructuredTool、BaseTool）
- **02_search_tools.py**: 搜索工具（DuckDuckGo、Wikipedia、自定义搜索）
- **03_calculator_tools.py**: 计算器工具（数学、科学、统计、金融计算）
- **quickstart.py**: 快速入门指南

## 学习目标

- ✅ 理解工具（Tool）的概念和作用
- ✅ 掌握三种创建工具的方法（@tool装饰器、StructuredTool、BaseTool）
- ✅ 学习工具参数验证和错误处理
- ✅ 实现搜索、计算等常用工具
- ✅ 工具与Agent的集成
- ✅ 工具组合和工具链

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 API Key
```

### 3. 运行快速入门

```bash
# 最快的入门方式
python src/quickstart.py
```

## 文件说明

### 01_tool_basics.py (450行)
**工具基础知识**

学习内容：
- 使用@tool装饰器创建简单工具
- 使用StructuredTool创建工具
- 使用BaseTool创建自定义工具类
- 工具参数验证
- 错误处理
- 工具组合

```bash
python src/01_tool_basics.py
```

### 02_search_tools.py (400行)
**搜索工具实现**

学习内容：
- DuckDuckGo搜索工具
- 维基百科搜索工具
- 自定义网页搜索
- 搜索结果处理（过滤、排序、去重）
- 搜索缓存
- 多搜索源聚合

```bash
python src/02_search_tools.py
```

### 03_calculator_tools.py (500行)
**计算器工具集**

学习内容：
- 基础数学运算（加减乘除、幂、平方根）
- 科学计算（三角函数、对数、阶乘）
- 统计计算（平均值、中位数、标准差）
- 表达式求值
- 单位转换（长度、重量、温度）
- 金融计算（复利、贷款月供）

```bash
python src/03_calculator_tools.py
```

## 核心概念

### 1. 三种创建工具的方法

#### 方法1: @tool 装饰器（最简单）

```python
from langchain.tools import tool

@tool
def get_word_length(word: str) -> int:
    """计算单词的长度"""
    return len(word)
```

#### 方法2: StructuredTool（灵活）

```python
from langchain.tools import StructuredTool

def multiply(a: float, b: float) -> float:
    """相乘两个数字"""
    return a * b

tool = StructuredTool.from_function(
    func=multiply,
    name="multiply",
    description="将两个数字相乘"
)
```

#### 方法3: BaseTool（完全自定义）

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class CalculatorInput(BaseModel):
    a: float = Field(description="第一个数")
    b: float = Field(description="第二个数")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "执行数学运算"
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, a: float, b: float) -> float:
        return a + b
```

### 2. 工具与Agent集成

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 创建工具
tools = [calculator, search, ...]

# 创建Agent
llm = ChatOpenAI(model="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_messages([...])
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 执行
result = agent_executor.invoke({"input": "计算 15 * 8"})
```

### 3. 工具描述的重要性

工具描述决定了Agent何时使用该工具，要清晰、具体：

```python
@tool
def search_web(query: str) -> str:
    """
    在互联网上搜索信息。
    
    使用场景：
    - 需要最新信息
    - 需要实时数据
    - 需要查找事实
    
    不适用场景：
    - 数学计算
    - 代码执行
    """
    ...
```

## 使用场景

1. **搜索工具** - 让AI获取实时信息
2. **计算工具** - 精确的数学计算
3. **数据库工具** - 查询和更新数据
4. **API工具** - 调用外部服务
5. **文件工具** - 读写文件操作

## 最佳实践

### 1. 工具命名

- 使用清晰的动词开头：`search_`, `calculate_`, `get_`
- 避免模糊名称：`tool1`, `helper`

### 2. 参数验证

```python
from pydantic import BaseModel, Field, validator

class ToolInput(BaseModel):
    value: int = Field(ge=0, le=100, description="0-100之间的整数")
    
    @validator('value')
    def check_value(cls, v):
        if v < 0:
            raise ValueError("值不能为负")
        return v
```

### 3. 错误处理

```python
@tool
def safe_divide(a: float, b: float) -> str:
    """安全除法"""
    try:
        if b == 0:
            return "错误: 除数不能为0"
        return str(a / b)
    except Exception as e:
        return f"错误: {str(e)}"
```

### 4. 返回值格式

- 简单结果：返回字符串或数字
- 复杂结果：返回JSON格式的字符串
- 错误情况：返回描述性错误消息

## 常见问题

### Q: 工具和Agent的区别？

- **工具（Tool）**：执行特定任务的函数（如搜索、计算）
- **Agent**：使用工具来完成复杂任务的智能体

### Q: 如何让Agent选择正确的工具？

- 编写清晰的工具描述
- 提供使用示例
- 测试不同的查询场景

### Q: 工具执行失败怎么办？

- 实现完善的错误处理
- 返回友好的错误消息
- 考虑添加重试机制

## 注意事项

- ⚠️ 工具描述要清晰，让AI知道何时使用
- ⚠️ 谨慎使用有风险的工具（文件操作、系统命令）
- ⚠️ 验证工具输入，防止注入攻击
- ⚠️ 对外部API调用添加超时和重试
- ✅ 为工具编写单元测试
- ✅ 记录工具的使用情况

## 相关教程

- 对应教程：`docs/02-教程/03-工具调用教程.md`
- LangChain工具文档：https://python.langchain.com/docs/modules/tools/

## 下一步

完成本项目后，可以继续学习：
- **项目04**: RAG检索增强生成
- **项目05**: Agent自主代理系统

## 许可证

MIT License