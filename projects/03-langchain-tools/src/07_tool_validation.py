"""
LangChain 工具使用 - 07: 工具参数验证

本模块演示：
1. Pydantic模型验证基础
2. 输入参数类型验证
3. 自定义验证器（validator）
4. 字段约束（Field constraints）
5. 验证错误处理
6. 复杂数据结构验证
7. 验证装饰器的使用
"""

import os
from typing import Optional, Type, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

from langchain.tools import BaseTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field, validator, root_validator, EmailStr, HttpUrl, constr, conint, confloat


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ==================== 示例1: 基本类型验证 ====================

class BasicValidationInput(BaseModel):
    """基本类型验证"""
    name: str = Field(description="姓名，必填字符串")
    age: int = Field(description="年龄，必填整数", ge=0, le=150)
    email: EmailStr = Field(description="邮箱地址")
    score: float = Field(description="分数", ge=0.0, le=100.0)
    is_active: bool = Field(default=True, description="是否激活")


class BasicValidationTool(BaseTool):
    """基本类型验证工具"""

    name: str = "basic_validation"
    description: str = """
    演示基本类型验证：字符串、整数、浮点数、布尔值、邮箱。

    示例:
    - name: "张三"
    - age: 25 (0-150)
    - email: "zhangsan@example.com"
    - score: 85.5 (0.0-100.0)
    - is_active: True
    """
    args_schema: Type[BaseModel] = BasicValidationInput

    def _run(
        self,
        name: str,
        age: int,
        email: EmailStr,
        score: float,
        is_active: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        output = "✓ 验证通过！\n\n"
        output += f"姓名: {name}\n"
        output += f"年龄: {age}\n"
        output += f"邮箱: {email}\n"
        output += f"分数: {score}\n"
        output += f"状态: {'激活' if is_active else '未激活'}"
        return output


def demo_basic_validation():
    """示例1: 基本类型验证"""
    print_section("示例1: 基本类型验证")

    tool = BasicValidationTool()

    # 测试1: 有效输入
    print("测试1: 有效输入")
    try:
        result = tool.invoke({
            "name": "张三",
            "age": 25,
            "email": "zhangsan@example.com",
            "score": 85.5,
            "is_active": True
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 年龄超出范围
    print("\n测试2: 年龄超出范围（应该失败）")
    try:
        result = tool.invoke({
            "name": "李四",
            "age": 200,  # 超出范围
            "email": "lisi@example.com",
            "score": 90.0
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试3: 无效邮箱
    print("\n测试3: 无效邮箱（应该失败）")
    try:
        result = tool.invoke({
            "name": "王五",
            "age": 30,
            "email": "invalid-email",  # 无效邮箱
            "score": 75.0
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")


# ==================== 示例2: 字符串约束验证 ====================

class StringConstraintsInput(BaseModel):
    """字符串约束验证"""
    username: constr(min_length=3, max_length=20, regex=r'^[a-zA-Z0-9_]+$') = Field(
        description="用户名：3-20个字符，只能包含字母、数字和下划线"
    )
    password: constr(min_length=8) = Field(
        description="密码：至少8个字符"
    )
    phone: constr(regex=r'^1[3-9]\d{9}$') = Field(
        description="手机号：11位数字，1开头"
    )
    code: constr(to_upper=True, min_length=4, max_length=4) = Field(
        description="验证码：4位字符，自动转大写"
    )


class StringConstraintsTool(BaseTool):
    """字符串约束验证工具"""

    name: str = "string_constraints"
    description: str = """
    演示字符串约束验证：长度、正则表达式、大小写转换。

    示例:
    - username: "user123" (3-20字符，字母数字下划线)
    - password: "securepass123" (至少8字符)
    - phone: "13812345678" (11位手机号)
    - code: "abcd" (4位验证码，自动转大写)
    """
    args_schema: Type[BaseModel] = StringConstraintsInput

    def _run(
        self,
        username: str,
        password: str,
        phone: str,
        code: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        output = "✓ 验证通过！\n\n"
        output += f"用户名: {username}\n"
        output += f"密码: {'*' * len(password)}\n"
        output += f"手机号: {phone}\n"
        output += f"验证码: {code}"
        return output


def demo_string_constraints():
    """示例2: 字符串约束验证"""
    print_section("示例2: 字符串约束验证")

    tool = StringConstraintsTool()

    # 测试1: 有效输入
    print("测试1: 有效输入")
    try:
        result = tool.invoke({
            "username": "user123",
            "password": "securepass123",
            "phone": "13812345678",
            "code": "abcd"
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 用户名包含非法字符
    print("\n测试2: 用户名包含非法字符（应该失败）")
    try:
        result = tool.invoke({
            "username": "user@123",  # 包含@
            "password": "securepass123",
            "phone": "13812345678",
            "code": "abcd"
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 用户名只能包含字母、数字和下划线")

    # 测试3: 密码太短
    print("\n测试3: 密码太短（应该失败）")
    try:
        result = tool.invoke({
            "username": "user123",
            "password": "123",  # 少于8字符
            "phone": "13812345678",
            "code": "abcd"
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 密码至少需要8个字符")


# ==================== 示例3: 数值约束验证 ====================

class NumberConstraintsInput(BaseModel):
    """数值约束验证"""
    quantity: conint(ge=1, le=100) = Field(
        description="数量：1-100之间的整数"
    )
    price: confloat(gt=0.0, le=99999.99) = Field(
        description="价格：大于0，不超过99999.99"
    )
    discount: confloat(ge=0.0, le=1.0) = Field(
        default=0.0,
        description="折扣：0.0-1.0之间"
    )
    rating: conint(ge=1, le=5) = Field(
        description="评分：1-5星"
    )


class NumberConstraintsTool(BaseTool):
    """数值约束验证工具"""

    name: str = "number_constraints"
    description: str = """
    演示数值约束验证：整数范围、浮点数范围、精度控制。

    示例:
    - quantity: 10 (1-100)
    - price: 99.99 (>0, <=99999.99)
    - discount: 0.2 (0.0-1.0)
    - rating: 5 (1-5)
    """
    args_schema: Type[BaseModel] = NumberConstraintsInput

    def _run(
        self,
        quantity: int,
        price: float,
        discount: float,
        rating: int,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        final_price = price * (1 - discount)
        total = final_price * quantity

        output = "✓ 验证通过！\n\n"
        output += f"数量: {quantity}\n"
        output += f"单价: ¥{price:.2f}\n"
        output += f"折扣: {discount * 100:.0f}%\n"
        output += f"折后价: ¥{final_price:.2f}\n"
        output += f"总价: ¥{total:.2f}\n"
        output += f"评分: {'⭐' * rating}"
        return output


def demo_number_constraints():
    """示例3: 数值约束验证"""
    print_section("示例3: 数值约束验证")

    tool = NumberConstraintsTool()

    # 测试1: 有效输入
    print("测试1: 有效计算")
    try:
        result = tool.invoke({
            "quantity": 5,
            "price": 99.99,
            "discount": 0.2,
            "rating": 5
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 数量超出范围
    print("\n测试2: 数量超出范围（应该失败）")
    try:
        result = tool.invoke({
            "quantity": 150,  # 超过100
            "price": 99.99,
            "discount": 0.0,
            "rating": 5
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 数量必须在1-100之间")


# ==================== 示例4: 自定义验证器 ====================

class CustomValidatorInput(BaseModel):
    """自定义验证器示例"""
    birth_date: date = Field(description="出生日期")
    start_date: date = Field(description="开始日期")
    end_date: date = Field(description="结束日期")
    tags: List[str] = Field(description="标签列表")

    @validator('birth_date')
    def validate_birth_date(cls, v):
        """验证出生日期不能是未来日期"""
        if v > date.today():
            raise ValueError('出生日期不能是未来日期')

        # 验证年龄不能小于18岁
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError(f'年龄必须至少18岁（当前{age}岁）')

        return v

    @validator('tags')
    def validate_tags(cls, v):
        """验证标签列表"""
        if not v:
            raise ValueError('至少需要一个标签')

        if len(v) > 5:
            raise ValueError('标签数量不能超过5个')

        # 去重并转小写
        return list(set(tag.lower() for tag in v))

    @root_validator
    def validate_date_range(cls, values):
        """验证日期范围的根验证器"""
        start = values.get('start_date')
        end = values.get('end_date')

        if start and end:
            if start > end:
                raise ValueError('开始日期不能晚于结束日期')

            # 验证日期范围不超过1年
            days = (end - start).days
            if days > 365:
                raise ValueError(f'日期范围不能超过1年（当前{days}天）')

        return values


class CustomValidatorTool(BaseTool):
    """自定义验证器工具"""

    name: str = "custom_validator"
    description: str = """
    演示自定义验证器：日期验证、列表验证、根验证器。

    示例:
    - birth_date: "1990-01-01"
    - start_date: "2024-01-01"
    - end_date: "2024-12-31"
    - tags: ["python", "langchain", "ai"]
    """
    args_schema: Type[BaseModel] = CustomValidatorInput

    def _run(
        self,
        birth_date: date,
        start_date: date,
        end_date: date,
        tags: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        age = (date.today() - birth_date).days // 365
        duration = (end_date - start_date).days

        output = "✓ 验证通过！\n\n"
        output += f"出生日期: {birth_date} (年龄: {age}岁)\n"
        output += f"开始日期: {start_date}\n"
        output += f"结束日期: {end_date}\n"
        output += f"持续时间: {duration}天\n"
        output += f"标签: {', '.join(tags)}"
        return output


def demo_custom_validator():
    """示例4: 自定义验证器"""
    print_section("示例4: 自定义验证器")

    tool = CustomValidatorTool()

    # 测试1: 有效输入
    print("测试1: 有效输入")
    try:
        result = tool.invoke({
            "birth_date": "1990-01-01",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "tags": ["Python", "LangChain", "AI", "Python"]  # 包含重复
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 未来出生日期
    print("\n测试2: 未来出生日期（应该失败）")
    try:
        result = tool.invoke({
            "birth_date": "2030-01-01",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "tags": ["test"]
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 出生日期不能是未来日期")

    # 测试3: 日期范围错误
    print("\n测试3: 开始日期晚于结束日期（应该失败）")
    try:
        result = tool.invoke({
            "birth_date": "1990-01-01",
            "start_date": "2024-12-31",
            "end_date": "2024-01-01",  # 早于开始日期
            "tags": ["test"]
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 开始日期不能晚于结束日期")


# ==================== 示例5: 枚举类型验证 ====================

class Priority(str, Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    """状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnumValidationInput(BaseModel):
    """枚举类型验证"""
    title: str = Field(description="任务标题")
    priority: Priority = Field(description="优先级")
    status: Status = Field(default=Status.PENDING, description="状态")
    category: str = Field(description="分类", regex="^(work|personal|study)$")


class EnumValidationTool(BaseTool):
    """枚举类型验证工具"""

    name: str = "enum_validation"
    description: str = """
    演示枚举类型验证：限定可选值。

    示例:
    - title: "完成报告"
    - priority: "high" (low/medium/high/urgent)
    - status: "in_progress" (pending/in_progress/completed/cancelled)
    - category: "work" (work/personal/study)
    """
    args_schema: Type[BaseModel] = EnumValidationInput

    def _run(
        self,
        title: str,
        priority: Priority,
        status: Status,
        category: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        priority_icons = {
            Priority.LOW: "🟢",
            Priority.MEDIUM: "🟡",
            Priority.HIGH: "🟠",
            Priority.URGENT: "🔴"
        }

        output = "✓ 验证通过！\n\n"
        output += f"标题: {title}\n"
        output += f"优先级: {priority_icons.get(priority, '')} {priority.value}\n"
        output += f"状态: {status.value}\n"
        output += f"分类: {category}"
        return output


def demo_enum_validation():
    """示例5: 枚举类型验证"""
    print_section("示例5: 枚举类型验证")

    tool = EnumValidationTool()

    # 测试1: 有效输入
    print("测试1: 有效输入")
    try:
        result = tool.invoke({
            "title": "完成季度报告",
            "priority": "high",
            "status": "in_progress",
            "category": "work"
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 无效优先级
    print("\n测试2: 无效优先级（应该失败）")
    try:
        result = tool.invoke({
            "title": "学习Python",
            "priority": "critical",  # 不在枚举中
            "status": "pending",
            "category": "study"
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 优先级必须是 low/medium/high/urgent")


# ==================== 示例6: 嵌套模型验证 ====================

class Address(BaseModel):
    """地址模型"""
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    province: str = Field(description="省份")
    postal_code: constr(regex=r'^\d{6}$') = Field(description="邮政编码（6位数字）")


class ContactInfo(BaseModel):
    """联系信息模型"""
    phone: constr(regex=r'^1[3-9]\d{9}$') = Field(description="手机号")
    email: EmailStr = Field(description="邮箱")
    address: Address = Field(description="地址信息")


class NestedValidationInput(BaseModel):
    """嵌套模型验证"""
    name: str = Field(description="姓名")
    age: conint(ge=18, le=100) = Field(description="年龄")
    contact: ContactInfo = Field(description="联系信息")


class NestedValidationTool(BaseTool):
    """嵌套模型验证工具"""

    name: str = "nested_validation"
    description: str = """
    演示嵌套模型验证：复杂数据结构。

    示例:
    - name: "张三"
    - age: 25
    - contact: {
        "phone": "13812345678",
        "email": "zhangsan@example.com",
        "address": {
          "street": "中关村大街1号",
          "city": "北京",
          "province": "北京市",
          "postal_code": "100000"
        }
      }
    """
    args_schema: Type[BaseModel] = NestedValidationInput

    def _run(
        self,
        name: str,
        age: int,
        contact: ContactInfo,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        output = "✓ 验证通过！\n\n"
        output += f"姓名: {name}\n"
        output += f"年龄: {age}\n\n"
        output += "联系信息:\n"
        output += f"  手机: {contact.phone}\n"
        output += f"  邮箱: {contact.email}\n\n"
        output += "地址:\n"
        output += f"  {contact.address.province} {contact.address.city}\n"
        output += f"  {contact.address.street}\n"
        output += f"  邮编: {contact.address.postal_code}"
        return output


def demo_nested_validation():
    """示例6: 嵌套模型验证"""
    print_section("示例6: 嵌套模型验证")

    tool = NestedValidationTool()

    # 测试1: 有效输入
    print("测试1: 有效输入")
    try:
        result = tool.invoke({
            "name": "张三",
            "age": 25,
            "contact": {
                "phone": "13812345678",
                "email": "zhangsan@example.com",
                "address": {
                    "street": "中关村大街1号",
                    "city": "北京",
                    "province": "北京市",
                    "postal_code": "100000"
                }
            }
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 无效邮政编码
    print("\n测试2: 无效邮政编码（应该失败）")
    try:
        result = tool.invoke({
            "name": "李四",
            "age": 30,
            "contact": {
                "phone": "13912345678",
                "email": "lisi@example.com",
                "address": {
                    "street": "人民路100号",
                    "city": "上海",
                    "province": "上海市",
                    "postal_code": "12345"  # 只有5位
                }
            }
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: 邮政编码必须是6位数字")


# ==================== 示例7: 可选字段和默认值 ====================

class OptionalFieldsInput(BaseModel):
    """可选字段验证"""
    title: str = Field(description="标题（必填）")
    description: Optional[str] = Field(default=None, description="描述（可选）")
    tags: List[str] = Field(default_factory=list, description="标签（可选）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据（可选）")
    priority: int = Field(default=3, ge=1, le=5, description="优先级（默认3）")


class OptionalFieldsTool(BaseTool):
    """可选字段工具"""

    name: str = "optional_fields"
    description: str = """
    演示可选字段和默认值处理。

    必填字段:
    - title: 标题

    可选字段:
    - description: 描述
    - tags: 标签列表
    - metadata: 元数据字典
    - priority: 优先级（默认3）
    """
    args_schema: Type[BaseModel] = OptionalFieldsInput

    def _run(
        self,
        title: str,
        description: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        priority: int = 3,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行验证"""
        output = "✓ 验证通过！\n\n"
        output += f"标题: {title}\n"
        output += f"描述: {description or '(无)'}\n"
        output += f"标签: {', '.join(tags) if tags else '(无)'}\n"
        output += f"元数据: {metadata if metadata else '(无)'}\n"
        output += f"优先级: {priority}"
        return output


def demo_optional_fields():
    """示例7: 可选字段和默认值"""
    print_section("示例7: 可选字段和默认值")

    tool = OptionalFieldsTool()

    # 测试1: 只提供必填字段
    print("测试1: 只提供必填字段")
    try:
        result = tool.invoke({
            "title": "简单任务"
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")

    # 测试2: 提供所有字段
    print("\n测试2: 提供所有字段")
    try:
        result = tool.invoke({
            "title": "复杂任务",
            "description": "这是一个详细的任务描述",
            "tags": ["urgent", "important"],
            "metadata": {"assignee": "张三", "department": "技术部"},
            "priority": 5
        })
        print(result)
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangChain 工具使用 - 07: 工具参数验证")
    print("="*70)

    try:
        # 示例1: 基本类型验证
        demo_basic_validation()

        # 示例2: 字符串约束
        demo_string_constraints()

        # 示例3: 数值约束
        demo_number_constraints()

        # 示例4: 自定义验证器
        demo_custom_validator()

        # 示例5: 枚举类型
        demo_enum_validation()

        # 示例6: 嵌套模型
        demo_nested_validation()

        # 示例7: 可选字段
        demo_optional_fields()

        print("\n" + "="*70)
        print("  所有示例运行完成！")
        print("="*70)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
