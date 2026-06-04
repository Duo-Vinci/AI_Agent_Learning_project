# 数据分析Agent案例

## 一、项目背景

业务团队需要快速分析数据，但不懂SQL。需求：
- 自然语言查询数据
- 自动生成SQL
- 数据可视化
- 生成分析报告

---

## 二、技术架构

### 核心组件
- **LLM**: GPT-4 (SQL生成)
- **数据库**: PostgreSQL
- **可视化**: Plotly
- **框架**: LangChain + Pandas

---

## 三、核心功能

### 3.1 SQL生成Agent

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool

class SQLGeneratorAgent:
    def __init__(self, db_schema: str):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.db_schema = db_schema
    
    async def generate_sql(self, natural_query: str) -> str:
        prompt = f"""根据数据库schema生成SQL查询。

数据库Schema：
{self.db_schema}

用户查询：{natural_query}

要求：
1. 生成标准SQL（PostgreSQL）
2. 只返回SQL，不要解释
3. 确保SQL安全（防注入）

SQL："""
        
        result = await self.llm.agenerate(prompt)
        return result.strip()
```

### 3.2 数据查询执行

```python
import psycopg2
import pandas as pd

class DataQueryExecutor:
    def __init__(self, db_config: dict):
        self.conn = psycopg2.connect(**db_config)
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """安全执行SQL"""
        # 验证SQL（只允许SELECT）
        if not sql.strip().upper().startswith('SELECT'):
            raise ValueError("只支持SELECT查询")
        
        # 执行查询
        df = pd.read_sql_query(sql, self.conn)
        return df
    
    def get_schema(self) -> str:
        """获取数据库schema"""
        schema_query = """
        SELECT 
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """
        
        df = pd.read_sql_query(schema_query, self.conn)
        return df.to_string()
```

### 3.3 数据可视化

```python
import plotly.express as px
import plotly.graph_objects as go

class DataVisualizer:
    def auto_visualize(self, df: pd.DataFrame, query_intent: str):
        """自动选择合适的可视化"""
        
        # 判断可视化类型
        if 'trend' in query_intent or 'time' in query_intent:
            return self.create_line_chart(df)
        
        elif 'compare' in query_intent or 'distribution' in query_intent:
            return self.create_bar_chart(df)
        
        elif 'proportion' in query_intent:
            return self.create_pie_chart(df)
        
        else:
            return self.create_table(df)
    
    def create_line_chart(self, df: pd.DataFrame):
        fig = px.line(df, x=df.columns[0], y=df.columns[1])
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame):
        fig = px.bar(df, x=df.columns[0], y=df.columns[1])
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame):
        fig = px.pie(df, names=df.columns[0], values=df.columns[1])
        return fig
```

### 3.4 报告生成

```python
class ReportGenerator:
    async def generate_insight(self, df: pd.DataFrame, query: str):
        """生成数据洞察"""
        
        # 计算基础统计
        stats = df.describe().to_string()
        
        prompt = f"""分析以下数据，提供业务洞察：

用户查询：{query}

数据统计：
{stats}

数据样本：
{df.head(10).to_string()}

请提供：
1. 关键发现（3-5条）
2. 异常点分析
3. 业务建议

分析报告："""
        
        return await self.llm.agenerate(prompt)
```

---

## 四、完整流程

```python
class DataAnalysisAgent:
    def __init__(self, db_config: dict):
        self.executor = DataQueryExecutor(db_config)
        schema = self.executor.get_schema()
        
        self.sql_generator = SQLGeneratorAgent(schema)
        self.visualizer = DataVisualizer()
        self.report_generator = ReportGenerator()
    
    async def analyze(self, natural_query: str):
        """完整分析流程"""
        
        # 1. 生成SQL
        sql = await self.sql_generator.generate_sql(natural_query)
        print(f"生成的SQL: {sql}")
        
        # 2. 执行查询
        df = self.executor.execute_query(sql)
        print(f"查询结果: {len(df)}行")
        
        # 3. 可视化
        chart = self.visualizer.auto_visualize(df, natural_query)
        
        # 4. 生成洞察
        insights = await self.report_generator.generate_insight(df, natural_query)
        
        return {
            'sql': sql,
            'data': df,
            'chart': chart,
            'insights': insights
        }

# 使用示例
agent = DataAnalysisAgent({
    'host': 'localhost',
    'database': 'sales_db',
    'user': 'analyst',
    'password': 'xxx'
})

result = await agent.analyze("过去30天每天的销售额趋势")
```

---

## 五、安全考虑

### 5.1 SQL注入防护

```python
def validate_sql(sql: str) -> bool:
    """验证SQL安全性"""
    
    # 只允许SELECT
    if not sql.strip().upper().startswith('SELECT'):
        return False
    
    # 禁止危险操作
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT',
        'TRUNCATE', 'ALTER', 'CREATE', 'EXEC'
    ]
    
    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False
    
    return True
```

### 5.2 权限控制

```python
class PermissionManager:
    def __init__(self):
        self.user_permissions = {
            'analyst': ['sales', 'products'],  # 只能访问这些表
            'manager': ['sales', 'products', 'customers'],
            'admin': ['*']  # 所有表
        }
    
    def check_permission(self, user_role: str, sql: str) -> bool:
        """检查用户权限"""
        allowed_tables = self.user_permissions.get(user_role, [])
        
        if '*' in allowed_tables:
            return True
        
        # 从SQL中提取表名
        tables_in_query = extract_tables_from_sql(sql)
        
        # 检查是否都在允许列表中
        return all(table in allowed_tables for table in tables_in_query)
```

---

## 六、效果评估

### 指标

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 查询响应时间 | 需要找开发 | 即时 | - |
| 数据分析效率 | 1天 | 5分钟 | 99% |
| SQL错误率 | 业务不懂 | 5% | - |
| 分析报告质量 | 人工撰写 | 自动生成 | +80% |

### 业务价值
- 业务团队可以自主分析数据
- 减少对数据团队的依赖
- 决策响应速度提升10倍

---

## 七、经验总结

**成功关键**：
1. 准确的SQL生成（GPT-4质量高）
2. 完善的Schema信息
3. 严格的安全控制
4. 智能的可视化选择

**遇到的问题**：
1. 复杂查询生成不准确
   - 解决：添加few-shot示例

2. SQL执行超时
   - 解决：设置超时限制，优化查询

3. 数据安全风险
   - 解决：严格权限控制，日志审计

---

**让数据分析更简单，让业务决策更快速！**
