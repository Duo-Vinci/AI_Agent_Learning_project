"""
高级类型注解
===========

本模块介绍Python高级类型注解：
- 泛型（Generics）
- 协议（Protocol）
- TypedDict
- Literal
- Final
- 类型守卫（Type Guards）

这些是构建类型安全的AI系统的关键技术。
"""

from typing import (
    TypeVar, Generic, Protocol,
    Literal, Final, get_args, get_origin,
    cast, overload, TypedDict
)
from typing_extensions import TypeAlias  # Python 3.10+
from dataclasses import dataclass


# ============================================================================
# 1. 泛型（Generics）
# ============================================================================

# 定义类型变量
T = TypeVar('T')  # 任意类型
K = TypeVar('K')  # 键类型
V = TypeVar('V')  # 值类型


class Stack(Generic[T]):
    """
    泛型栈

    Generic[T] 表示这是一个泛型类
    T 是类型参数，使用时可以指定具体类型
    """

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """压入元素"""
        self._items.append(item)

    def pop(self) -> T:
        """弹出元素"""
        if not self._items:
            raise IndexError("栈为空")
        return self._items.pop()

    def peek(self) -> T:
        """查看栈顶元素"""
        if not self._items:
            raise IndexError("栈为空")
        return self._items[-1]

    def is_empty(self) -> bool:
        """判断是否为空"""
        return len(self._items) == 0

    def size(self) -> int:
        """获取大小"""
        return len(self._items)


def first_element(items: list[T]) -> T:
    """
    获取列表第一个元素

    泛型函数：返回类型与输入类型相同
    """
    if not items:
        raise ValueError("列表为空")
    return items[0]


def generics_example():
    """泛型示例"""
    print("\n【示例1】泛型（Generics）")
    print("=" * 60)

    # 整数栈
    int_stack: Stack[int] = Stack()
    int_stack.push(1)
    int_stack.push(2)
    int_stack.push(3)
    print(f"整数栈: {int_stack.pop()}")  # 3

    # 字符串栈
    str_stack: Stack[str] = Stack()
    str_stack.push("hello")
    str_stack.push("world")
    print(f"字符串栈: {str_stack.pop()}")  # world

    # 泛型函数
    numbers = [1, 2, 3]
    names = ["Alice", "Bob"]

    print(f"first_element([1,2,3]): {first_element(numbers)}")
    print(f"first_element(['Alice','Bob']): {first_element(names)}")


# ============================================================================
# 2. 协议（Protocol）
# ============================================================================

class Drawable(Protocol):
    """
    可绘制协议

    Protocol 定义接口（结构化类型）
    任何实现了这些方法的类都满足这个协议
    不需要显式继承
    """

    def draw(self) -> str:
        """绘制方法"""
        ...


class Circle:
    """圆形（实现 Drawable 协议）"""

    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"绘制半径为 {self.radius} 的圆"


class Rectangle:
    """矩形（实现 Drawable 协议）"""

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def draw(self) -> str:
        return f"绘制 {self.width}x{self.height} 的矩形"


def render(shape: Drawable) -> None:
    """
    渲染图形

    接受任何实现了 Drawable 协议的对象
    """
    print(f"  {shape.draw()}")


class LLMProvider(Protocol):
    """
    LLM提供者协议

    定义LLM必须实现的接口
    """

    def generate(self, prompt: str) -> str:
        """生成文本"""
        ...

    def get_model_name(self) -> str:
        """获取模型名称"""
        ...


class GPTProvider:
    """GPT提供者"""

    def generate(self, prompt: str) -> str:
        return f"GPT响应: {prompt}"

    def get_model_name(self) -> str:
        return "gpt-4"


class ClaudeProvider:
    """Claude提供者"""

    def generate(self, prompt: str) -> str:
        return f"Claude响应: {prompt}"

    def get_model_name(self) -> str:
        return "claude-3"


def call_llm(provider: LLMProvider, prompt: str) -> str:
    """
    调用LLM

    接受任何实现了 LLMProvider 协议的提供者
    """
    model = provider.get_model_name()
    response = provider.generate(prompt)
    return f"[{model}] {response}"


def protocol_example():
    """协议示例"""
    print("\n【示例2】协议（Protocol）")
    print("=" * 60)

    # 图形协议
    print("\n图形渲染:")
    circle = Circle(5.0)
    rectangle = Rectangle(10.0, 20.0)

    render(circle)
    render(rectangle)

    # LLM协议
    print("\nLLM调用:")
    gpt = GPTProvider()
    claude = ClaudeProvider()

    result1 = call_llm(gpt, "Hello")
    result2 = call_llm(claude, "Hello")

    print(f"  {result1}")
    print(f"  {result2}")


# ============================================================================
# 3. TypedDict
# ============================================================================

class UserDict(TypedDict):
    """
    用户字典类型

    TypedDict 为字典定义精确的键和类型
    比普通的 Dict[str, Any] 更精确
    """
    name: str
    age: int
    email: str


class MessageDict(TypedDict):
    """消息字典"""
    role: Literal["user", "assistant", "system"]
    content: str


class LLMResponseDict(TypedDict, total=False):
    """
    LLM响应字典

    total=False 表示所有字段都是可选的
    """
    text: str
    tokens: int
    model: str
    finish_reason: str


def create_user(name: str, age: int, email: str) -> UserDict:
    """创建用户"""
    return {
        "name": name,
        "age": age,
        "email": email
    }


def process_messages(messages: list[MessageDict]) -> str:
    """处理消息列表"""
    result = []
    for msg in messages:
        result.append(f"[{msg['role']}] {msg['content']}")
    return "\n".join(result)


def typeddict_example():
    """TypedDict 示例"""
    print("\n【示例3】TypedDict")
    print("=" * 60)

    # 用户字典
    user: UserDict = create_user("Alice", 25, "alice@example.com")
    print(f"\n用户: {user}")

    # 消息字典
    messages: list[MessageDict] = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    print(f"\n消息处理:")
    print(process_messages(messages))

    # LLM响应（部分字段）
    response: LLMResponseDict = {
        "text": "这是响应",
        "tokens": 150
    }
    print(f"\nLLM响应: {response}")


# ============================================================================
# 4. Literal 类型
# ============================================================================

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    """
    设置日志级别

    Literal 限制参数只能是指定的几个值
    """
    print(f"  日志级别设置为: {level}")


def get_llm_model(
    provider: Literal["openai", "anthropic", "google"]
) -> str:
    """
    获取LLM模型

    使用 Literal 确保提供者名称正确
    """
    models = {
        "openai": "gpt-4",
        "anthropic": "claude-3",
        "google": "gemini-pro"
    }
    return models[provider]


# 类型别名与 Literal
ModelProvider: TypeAlias = Literal["openai", "anthropic", "google"]
LogLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


def call_model(provider: ModelProvider, prompt: str) -> str:
    """使用类型别名的函数"""
    model = get_llm_model(provider)
    return f"[{model}] 响应: {prompt}"


def literal_example():
    """Literal 示例"""
    print("\n【示例4】Literal 类型")
    print("=" * 60)

    # 日志级别
    print("\n设置日志级别:")
    set_log_level("INFO")
    set_log_level("ERROR")

    # LLM提供者
    print("\nLLM模型:")
    print(f"  OpenAI: {get_llm_model('openai')}")
    print(f"  Anthropic: {get_llm_model('anthropic')}")

    # 使用类型别名
    print("\n使用类型别名:")
    result = call_model("openai", "Hello")
    print(f"  {result}")


# ============================================================================
# 5. Final 类型
# ============================================================================

# 常量
MAX_TOKENS: Final[int] = 4096
MODEL_NAME: Final[str] = "gpt-4"
API_VERSION: Final[str] = "v1"


class Config:
    """配置类"""

    MAX_RETRIES: Final[int] = 3
    TIMEOUT: Final[float] = 30.0

    def __init__(self):
        # Final 实例变量（不能被重新赋值）
        self.api_key: Final[str] = "sk-xxxxxxxxxxxx"


def final_example():
    """Final 示例"""
    print("\n【示例5】Final 类型")
    print("=" * 60)

    print(f"\n模块级常量:")
    print(f"  MAX_TOKENS: {MAX_TOKENS}")
    print(f"  MODEL_NAME: {MODEL_NAME}")
    print(f"  API_VERSION: {API_VERSION}")

    print(f"\n类级常量:")
    print(f"  Config.MAX_RETRIES: {Config.MAX_RETRIES}")
    print(f"  Config.TIMEOUT: {Config.TIMEOUT}")

    config = Config()
    print(f"\n实例常量:")
    print(f"  config.api_key: {config.api_key[:8]}...")

    print("\n注意: Final 表示不应该被重新赋值")
    print("      这是类型检查器的提示，运行时不会强制")


# ============================================================================
# 6. 类型守卫（Type Guards）
# ============================================================================

def is_string_list(value: list) -> bool:
    """
    类型守卫：检查是否是字符串列表

    使用 isinstance 进行运行时类型检查
    """
    return all(isinstance(item, str) for item in value)


def process_list(items: list) -> str:
    """
    处理列表

    使用类型守卫确保类型安全
    """
    if is_string_list(items):
        # 在这个分支，类型检查器知道 items 是 list[str]
        return ", ".join(items)
    else:
        return f"非字符串列表: {items}"


def is_valid_message(data: dict) -> bool:
    """检查是否是有效的消息字典"""
    return (
        isinstance(data, dict) and
        "role" in data and
        "content" in data and
        isinstance(data["role"], str) and
        isinstance(data["content"], str)
    )


def type_guard_example():
    """类型守卫示例"""
    print("\n【示例6】类型守卫")
    print("=" * 60)

    # 字符串列表
    list1 = ["a", "b", "c"]
    list2 = [1, 2, 3]

    print(f"\n{list1}: {process_list(list1)}")
    print(f"{list2}: {process_list(list2)}")

    # 消息验证
    msg1 = {"role": "user", "content": "Hello"}
    msg2 = {"invalid": "data"}

    print(f"\n消息验证:")
    print(f"  {msg1}: {is_valid_message(msg1)}")
    print(f"  {msg2}: {is_valid_message(msg2)}")


# ============================================================================
# 7. 函数重载（Overload）
# ============================================================================

@overload
def process(value: str) -> str: ...

@overload
def process(value: int) -> int: ...

@overload
def process(value: list[str]) -> list[str]: ...


def process(value):
    """
    处理不同类型的值

    使用 @overload 为函数提供多个类型签名
    实际实现不需要类型注解
    """
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, int):
        return value * 2
    elif isinstance(value, list):
        return [item.upper() for item in value]
    else:
        raise TypeError(f"不支持的类型: {type(value)}")


def overload_example():
    """函数重载示例"""
    print("\n【示例7】函数重载")
    print("=" * 60)

    result1 = process("hello")
    result2 = process(42)
    result3 = process(["a", "b", "c"])

    print(f"\nprocess('hello'): {result1}")
    print(f"process(42): {result2}")
    print(f"process(['a','b','c']): {result3}")


# ============================================================================
# 8. AI应用：完整的类型系统
# ============================================================================

# 定义AI相关的类型
Role = Literal["user", "assistant", "system"]
ModelName = Literal["gpt-4", "gpt-3.5-turbo", "claude-3"]


class Message(TypedDict):
    """消息类型"""
    role: Role
    content: str


class CompletionRequest(TypedDict):
    """完成请求类型"""
    model: ModelName
    messages: list[Message]
    temperature: float
    max_tokens: int


class CompletionResponse(TypedDict):
    """完成响应类型"""
    content: str
    tokens: int
    finish_reason: str


@dataclass
class Agent(Generic[T]):
    """
    泛型Agent类

    T 是Agent处理的数据类型
    """
    name: str
    model: ModelName
    temperature: float = 0.7

    def process(self, input_data: T) -> T:
        """处理输入数据"""
        print(f"  [{self.name}] 处理数据: {input_data}")
        return input_data


class LLMClient(Protocol):
    """LLM客户端协议"""

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """完成请求"""
        ...


class MockLLMClient:
    """模拟LLM客户端"""

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """实现完成请求"""
        model = request["model"]
        message_count = len(request["messages"])

        return {
            "content": f"[{model}] 响应 ({message_count} 条消息)",
            "tokens": 150,
            "finish_reason": "stop"
        }


def create_completion_request(
    model: ModelName,
    prompt: str,
    temperature: float = 0.7
) -> CompletionRequest:
    """创建完成请求"""
    return {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 1000
    }


def ai_type_system_example():
    """AI应用的完整类型系统"""
    print("\n【示例8】AI应用的完整类型系统")
    print("=" * 60)

    # 创建请求
    request = create_completion_request(
        model="gpt-4",
        prompt="什么是类型注解?",
        temperature=0.7
    )

    print(f"\n请求:")
    print(f"  模型: {request['model']}")
    print(f"  消息数: {len(request['messages'])}")
    print(f"  温度: {request['temperature']}")

    # 调用LLM
    client: LLMClient = MockLLMClient()
    response = client.complete(request)

    print(f"\n响应:")
    print(f"  内容: {response['content']}")
    print(f"  Tokens: {response['tokens']}")
    print(f"  完成原因: {response['finish_reason']}")

    # 泛型Agent
    print(f"\n泛型Agent:")
    str_agent: Agent[str] = Agent("文本Agent", "gpt-4")
    str_agent.process("输入文本")

    int_agent: Agent[int] = Agent("数字Agent", "gpt-3.5-turbo")
    int_agent.process(42)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("Python 高级类型注解")
    print("=" * 60)

    generics_example()
    protocol_example()
    typeddict_example()
    literal_example()
    final_example()
    type_guard_example()
    overload_example()
    ai_type_system_example()

    print("\n" + "=" * 60)
    print("高级类型注解总结")
    print("=" * 60)
    print("1. Generic[T] - 泛型，提供类型参数化")
    print("2. Protocol - 协议，定义结构化接口")
    print("3. TypedDict - 为字典定义精确的键和类型")
    print("4. Literal - 限制值为特定的字面量")
    print("5. Final - 标记常量，不应重新赋值")
    print("6. 类型守卫 - 运行时类型检查")
    print("7. @overload - 函数重载，提供多个类型签名")
    print("8. 在AI系统中，类型系统确保代码健壮性")
    print("\n推荐工具:")
    print("  - mypy: 静态类型检查")
    print("  - pyright: 微软的类型检查器")
    print("  - pydantic: 运行时数据验证")


if __name__ == "__main__":
    main()
