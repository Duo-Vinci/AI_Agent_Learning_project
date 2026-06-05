"""
类型注解基础
===========

本模块介绍Python类型注解（Type Hints）的基础：
- 基本类型注解
- 复合类型（List, Dict, Tuple等）
- Optional 和 Union
- 函数类型注解
- 类型别名

类型注解在AI开发中非常重要：
- 提高代码可读性
- IDE智能提示
- 静态类型检查（mypy）
- 更好的文档
"""

from typing import (
    List, Dict, Tuple, Set,
    Optional, Union, Any,
    Callable, TypeVar, Generic
)


# ============================================================================
# 1. 基本类型注解
# ============================================================================

def basic_types_example():
    """基本类型注解示例"""
    print("\n【示例1】基本类型注解")
    print("=" * 60)

    # 变量类型注解
    name: str = "Alice"
    age: int = 25
    height: float = 1.75
    is_active: bool = True

    print(f"name: {name} (类型: {type(name).__name__})")
    print(f"age: {age} (类型: {type(age).__name__})")
    print(f"height: {height} (类型: {type(height).__name__})")
    print(f"is_active: {is_active} (类型: {type(is_active).__name__})")


def greet(name: str) -> str:
    """
    问候函数

    Args:
        name: 用户名（字符串）

    Returns:
        问候语（字符串）
    """
    return f"Hello, {name}!"


def add_numbers(a: int, b: int) -> int:
    """两数相加"""
    return a + b


def calculate_average(numbers: list) -> float:
    """计算平均数（不推荐的注解方式）"""
    return sum(numbers) / len(numbers)


def function_annotations_example():
    """函数类型注解示例"""
    print("\n【示例2】函数类型注解")
    print("=" * 60)

    result1 = greet("Bob")
    print(f"greet('Bob'): {result1}")

    result2 = add_numbers(3, 5)
    print(f"add_numbers(3, 5): {result2}")

    result3 = calculate_average([1, 2, 3, 4, 5])
    print(f"calculate_average([1,2,3,4,5]): {result3}")


# ============================================================================
# 2. 复合类型注解
# ============================================================================

def process_names(names: List[str]) -> List[str]:
    """
    处理名字列表

    推荐使用 List[str] 而不是 list
    更精确地描述列表中元素的类型
    """
    return [name.upper() for name in names]


def count_words(text: str) -> Dict[str, int]:
    """
    统计词频

    返回 Dict[str, int] 表示：
    - 键是字符串
    - 值是整数
    """
    words = text.split()
    counts: Dict[str, int] = {}

    for word in words:
        counts[word] = counts.get(word, 0) + 1

    return counts


def get_coordinates() -> Tuple[float, float]:
    """
    获取坐标

    Tuple[float, float] 表示包含两个浮点数的元组
    """
    return (39.9042, 116.4074)  # 北京坐标


def get_unique_tags(texts: List[str]) -> Set[str]:
    """
    获取所有唯一标签

    Set[str] 表示字符串集合
    """
    tags: Set[str] = set()

    for text in texts:
        words = text.split()
        tags.update(words)

    return tags


def compound_types_example():
    """复合类型示例"""
    print("\n【示例3】复合类型注解")
    print("=" * 60)

    # List
    names = ["alice", "bob", "charlie"]
    result1 = process_names(names)
    print(f"处理后的名字: {result1}")

    # Dict
    text = "hello world hello python"
    result2 = count_words(text)
    print(f"词频统计: {result2}")

    # Tuple
    coords = get_coordinates()
    print(f"坐标: {coords}")

    # Set
    texts = ["AI ML", "ML DL", "AI DL"]
    result3 = get_unique_tags(texts)
    print(f"唯一标签: {result3}")


# ============================================================================
# 3. Optional 和 Union
# ============================================================================

def find_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    查找用户

    Optional[T] 等价于 Union[T, None]
    表示可能返回 Dict 或 None
    """
    # 模拟数据库查询
    users = {
        1: {"name": "Alice", "age": 25},
        2: {"name": "Bob", "age": 30}
    }

    return users.get(user_id)


def parse_value(value: str) -> Union[int, float, str]:
    """
    解析值

    Union[int, float, str] 表示返回值可能是：
    - int 或
    - float 或
    - str
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    获取配置

    Optional 用于可能为 None 的参数和返回值
    """
    config = {"debug": "true", "timeout": "30"}
    return config.get(key, default)


def optional_union_example():
    """Optional 和 Union 示例"""
    print("\n【示例4】Optional 和 Union")
    print("=" * 60)

    # Optional
    user1 = find_user(1)
    user2 = find_user(999)
    print(f"find_user(1): {user1}")
    print(f"find_user(999): {user2}")

    # Union
    print(f"\nparse_value('42'): {parse_value('42')} (类型: {type(parse_value('42')).__name__})")
    print(f"parse_value('3.14'): {parse_value('3.14')} (类型: {type(parse_value('3.14')).__name__})")
    print(f"parse_value('hello'): {parse_value('hello')} (类型: {type(parse_value('hello')).__name__})")

    # Optional 参数
    config1 = get_config("debug")
    config2 = get_config("missing", "default_value")
    print(f"\nget_config('debug'): {config1}")
    print(f"get_config('missing', 'default_value'): {config2}")


# ============================================================================
# 4. 类型别名
# ============================================================================

# 定义类型别名
Vector = List[float]
Matrix = List[List[float]]
UserId = int
UserData = Dict[str, Any]

# AI相关的类型别名
Prompt = str
Response = str
TokenCount = int
Message = Dict[str, str]
MessageList = List[Message]


def calculate_dot_product(v1: Vector, v2: Vector) -> float:
    """
    计算向量点积

    使用类型别名使代码更易读
    """
    return sum(a * b for a, b in zip(v1, v2))


def create_user(user_id: UserId, data: UserData) -> bool:
    """
    创建用户

    UserId 和 UserData 是类型别名
    """
    print(f"创建用户 {user_id}: {data}")
    return True


def call_llm(messages: MessageList) -> Response:
    """
    调用LLM

    使用AI领域的类型别名
    """
    prompt_text = " | ".join(m["content"] for m in messages)
    return f"LLM响应: {prompt_text[:30]}..."


def type_alias_example():
    """类型别名示例"""
    print("\n【示例5】类型别名")
    print("=" * 60)

    # Vector
    v1: Vector = [1.0, 2.0, 3.0]
    v2: Vector = [4.0, 5.0, 6.0]
    dot = calculate_dot_product(v1, v2)
    print(f"向量点积: {dot}")

    # 自定义类型
    user_id: UserId = 123
    user_data: UserData = {"name": "Alice", "email": "alice@example.com"}
    create_user(user_id, user_data)

    # AI类型
    messages: MessageList = [
        {"role": "user", "content": "什么是AI?"},
        {"role": "assistant", "content": "AI是人工智能..."}
    ]
    response = call_llm(messages)
    print(f"LLM调用结果: {response}")


# ============================================================================
# 5. Callable 类型
# ============================================================================

def apply_operation(
    x: int,
    y: int,
    operation: Callable[[int, int], int]
) -> int:
    """
    应用运算

    Callable[[int, int], int] 表示：
    - 接收两个 int 参数
    - 返回一个 int 值
    的可调用对象（函数）
    """
    return operation(x, y)


def create_multiplier(factor: int) -> Callable[[int], int]:
    """
    创建乘法器

    返回一个函数：Callable[[int], int]
    """
    def multiply(x: int) -> int:
        return x * factor

    return multiply


def process_with_callback(
    data: List[str],
    callback: Callable[[str], None]
) -> None:
    """
    使用回调处理数据

    Callable[[str], None] 表示：
    - 接收一个 str 参数
    - 无返回值
    """
    for item in data:
        callback(item)


def callable_example():
    """Callable 类型示例"""
    print("\n【示例6】Callable 类型")
    print("=" * 60)

    # 传递函数
    result1 = apply_operation(10, 5, lambda x, y: x + y)
    result2 = apply_operation(10, 5, lambda x, y: x * y)
    print(f"10 + 5 = {result1}")
    print(f"10 * 5 = {result2}")

    # 返回函数
    times_3 = create_multiplier(3)
    print(f"times_3(7) = {times_3(7)}")

    # 回调函数
    print("\n使用回调处理数据:")
    process_with_callback(
        ["item1", "item2", "item3"],
        lambda item: print(f"  处理: {item}")
    )


# ============================================================================
# 6. Any 类型
# ============================================================================

def process_any(data: Any) -> Any:
    """
    处理任意类型

    Any 表示可以是任何类型
    应该谨慎使用，因为会失去类型检查
    """
    print(f"处理数据: {data} (类型: {type(data).__name__})")
    return data


def flexible_function(value: Any) -> str:
    """
    灵活的函数

    有时候必须使用 Any（如处理JSON数据）
    """
    if isinstance(value, str):
        return f"字符串: {value}"
    elif isinstance(value, int):
        return f"整数: {value}"
    elif isinstance(value, dict):
        return f"字典: {len(value)} 个键"
    else:
        return f"其他类型: {type(value).__name__}"


def any_type_example():
    """Any 类型示例"""
    print("\n【示例7】Any 类型")
    print("=" * 60)

    process_any(42)
    process_any("hello")
    process_any([1, 2, 3])

    print(f"\n{flexible_function('text')}")
    print(f"{flexible_function(123)}")
    print(f"{flexible_function({'a': 1, 'b': 2})}")


# ============================================================================
# 7. AI应用：类型注解实践
# ============================================================================

class Agent:
    """
    AI Agent 类

    展示如何在类中使用类型注解
    """

    def __init__(
        self,
        name: str,
        model: str,
        temperature: float = 0.7
    ) -> None:
        """
        初始化Agent

        Args:
            name: Agent名称
            model: 使用的模型
            temperature: 温度参数（0-1）
        """
        self.name: str = name
        self.model: str = model
        self.temperature: float = temperature
        self.history: MessageList = []

    def add_message(self, role: str, content: str) -> None:
        """添加消息到历史"""
        message: Message = {
            "role": role,
            "content": content
        }
        self.history.append(message)

    def generate(self, prompt: Prompt) -> Response:
        """
        生成响应

        Args:
            prompt: 输入提示词

        Returns:
            模型响应
        """
        self.add_message("user", prompt)
        response: Response = f"[{self.model}] 响应: {prompt}"
        self.add_message("assistant", response)
        return response

    def get_history(self) -> MessageList:
        """获取对话历史"""
        return self.history.copy()

    def clear_history(self) -> None:
        """清空历史"""
        self.history.clear()


def process_batch(
    prompts: List[Prompt],
    agent: Agent
) -> List[Response]:
    """
    批量处理提示词

    Args:
        prompts: 提示词列表
        agent: AI Agent

    Returns:
        响应列表
    """
    responses: List[Response] = []

    for prompt in prompts:
        response = agent.generate(prompt)
        responses.append(response)

    return responses


def ai_type_annotations_example():
    """AI应用中的类型注解"""
    print("\n【示例8】AI应用中的类型注解")
    print("=" * 60)

    # 创建Agent
    agent = Agent(
        name="助手",
        model="gpt-4",
        temperature=0.7
    )

    # 单个查询
    response: Response = agent.generate("什么是机器学习?")
    print(f"\n单个查询:")
    print(f"  {response}")

    # 批量处理
    prompts: List[Prompt] = [
        "什么是深度学习?",
        "什么是强化学习?"
    ]

    responses: List[Response] = process_batch(prompts, agent)
    print(f"\n批量处理:")
    for i, resp in enumerate(responses, 1):
        print(f"  {i}. {resp}")

    # 查看历史
    history: MessageList = agent.get_history()
    print(f"\n对话历史 ({len(history)} 条消息):")
    for msg in history:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""

    print("\n" + "=" * 60)
    print("Python 类型注解基础教程")
    print("=" * 60)

    basic_types_example()
    function_annotations_example()
    compound_types_example()
    optional_union_example()
    type_alias_example()
    callable_example()
    any_type_example()
    ai_type_annotations_example()

    print("\n" + "=" * 60)
    print("类型注解总结")
    print("=" * 60)
    print("1. 基本类型: int, str, float, bool")
    print("2. 复合类型: List[T], Dict[K,V], Tuple[T,...], Set[T]")
    print("3. Optional[T] = Union[T, None]")
    print("4. Union[T1, T2, ...] 表示多种可能类型")
    print("5. Callable[[参数类型], 返回类型] 表示函数类型")
    print("6. 类型别名提高代码可读性")
    print("7. Any 应谨慎使用")
    print("8. 在AI开发中，类型注解提升代码质量")
    print("\n运行类型检查: mypy script.py")


if __name__ == "__main__":
    main()
