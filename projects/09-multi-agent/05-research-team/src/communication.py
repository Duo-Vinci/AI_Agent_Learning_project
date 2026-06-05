"""
Agent通信机制
实现消息传递、消息总线和通信协议
"""

import time
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
from queue import Queue, Empty
from langchain_openai import ChatOpenAI


class MessageType(Enum):
    """消息类型枚举"""
    TASK = "task"           # 任务分配
    RESULT = "result"       # 任务结果
    QUERY = "query"         # 查询请求
    RESPONSE = "response"   # 查询响应
    BROADCAST = "broadcast" # 广播消息
    STATUS = "status"       # 状态更新


@dataclass
class Message:
    """Agent间的消息"""
    sender: str
    receiver: str
    type: MessageType
    content: Any
    timestamp: float
    message_id: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'type': self.type.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'message_id': self.message_id
        }


class MessageBus:
    """消息总线：管理Agent间的通信"""

    def __init__(self):
        """初始化消息总线"""
        self.queues: Dict[str, Queue] = {}
        self.message_history: List[Message] = []
        self.message_count = 0

    def register_agent(self, agent_id: str):
        """
        注册Agent到消息总线

        Args:
            agent_id: Agent唯一标识
        """
        if agent_id not in self.queues:
            self.queues[agent_id] = Queue()
            print(f"✓ Agent '{agent_id}' 已注册到消息总线")

    def unregister_agent(self, agent_id: str):
        """
        注销Agent

        Args:
            agent_id: Agent唯一标识
        """
        if agent_id in self.queues:
            del self.queues[agent_id]
            print(f"✓ Agent '{agent_id}' 已从消息总线注销")

    def send_message(self, message: Message):
        """
        发送消息

        Args:
            message: 消息对象
        """
        if message.receiver not in self.queues:
            print(f"✗ 接收者 '{message.receiver}' 未注册")
            return

        # 生成消息ID
        if not message.message_id:
            self.message_count += 1
            message.message_id = f"msg_{self.message_count}"

        # 发送到接收者队列
        self.queues[message.receiver].put(message)

        # 记录到历史
        self.message_history.append(message)

        print(f"📤 [{message.sender}] -> [{message.receiver}] ({message.type.value})")

    def receive_message(self, agent_id: str, timeout: float = None) -> Optional[Message]:
        """
        接收消息（阻塞）

        Args:
            agent_id: Agent唯一标识
            timeout: 超时时间（秒），None表示永久等待

        Returns:
            消息对象，超时返回None
        """
        if agent_id not in self.queues:
            print(f"✗ Agent '{agent_id}' 未注册")
            return None

        try:
            message = self.queues[agent_id].get(timeout=timeout)
            print(f"📥 [{agent_id}] 收到消息 ({message.type.value})")
            return message
        except Empty:
            return None

    def broadcast(self, sender: str, message_type: MessageType, content: Any):
        """
        广播消息给所有Agent

        Args:
            sender: 发送者ID
            message_type: 消息类型
            content: 消息内容
        """
        print(f"📢 [{sender}] 广播消息")
        for agent_id in self.queues.keys():
            if agent_id != sender:
                msg = Message(
                    sender=sender,
                    receiver=agent_id,
                    type=message_type,
                    content=content,
                    timestamp=time.time()
                )
                self.send_message(msg)

    def get_message_history(self, agent_id: Optional[str] = None) -> List[Message]:
        """
        获取消息历史

        Args:
            agent_id: 如果指定，只返回与该Agent相关的消息

        Returns:
            消息列表
        """
        if agent_id:
            return [
                msg for msg in self.message_history
                if msg.sender == agent_id or msg.receiver == agent_id
            ]
        return self.message_history

    def get_statistics(self) -> Dict:
        """
        获取消息统计信息

        Returns:
            统计信息字典
        """
        return {
            'total_agents': len(self.queues),
            'total_messages': len(self.message_history),
            'message_types': {
                msg_type.value: len([m for m in self.message_history if m.type == msg_type])
                for msg_type in MessageType
            }
        }


class CommunicatingAgent:
    """支持通信的Agent基类"""

    def __init__(self, agent_id: str, message_bus: MessageBus, llm: Optional[ChatOpenAI] = None):
        """
        初始化通信Agent

        Args:
            agent_id: Agent唯一标识
            message_bus: 消息总线实例
            llm: 语言模型实例
        """
        self.agent_id = agent_id
        self.bus = message_bus
        self.llm = llm or ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        self.running = False

        # 注册到消息总线
        self.bus.register_agent(agent_id)

    def send_to(self, receiver: str, message_type: MessageType, content: Any):
        """
        发送消息给指定Agent

        Args:
            receiver: 接收者ID
            message_type: 消息类型
            content: 消息内容
        """
        msg = Message(
            sender=self.agent_id,
            receiver=receiver,
            type=message_type,
            content=content,
            timestamp=time.time()
        )
        self.bus.send_message(msg)

    def receive(self, timeout: float = None) -> Optional[Message]:
        """
        接收消息

        Args:
            timeout: 超时时间

        Returns:
            消息对象
        """
        return self.bus.receive_message(self.agent_id, timeout)

    def broadcast(self, message_type: MessageType, content: Any):
        """
        广播消息

        Args:
            message_type: 消息类型
            content: 消息内容
        """
        self.bus.broadcast(self.agent_id, message_type, content)

    def process_message(self, message: Message) -> Any:
        """
        处理收到的消息（子类应重写此方法）

        Args:
            message: 消息对象

        Returns:
            处理结果
        """
        if message.type == MessageType.TASK:
            return self.execute_task(message.content)
        elif message.type == MessageType.QUERY:
            return self.answer_query(message.content)
        else:
            return f"不支持的消息类型: {message.type}"

    def execute_task(self, task: str) -> str:
        """
        执行任务

        Args:
            task: 任务描述

        Returns:
            执行结果
        """
        prompt = f"""你是 {self.agent_id}。请完成以下任务：

任务：{task}

执行结果："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            return result
        except Exception as e:
            return f"任务执行失败: {str(e)}"

    def answer_query(self, query: str) -> str:
        """
        回答查询

        Args:
            query: 查询内容

        Returns:
            回答
        """
        prompt = f"""你是 {self.agent_id}。请回答以下问题：

问题：{query}

回答："""

        try:
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            return result
        except Exception as e:
            return f"回答失败: {str(e)}"

    def start(self):
        """启动Agent，开始监听消息"""
        self.running = True
        print(f"🚀 [{self.agent_id}] 已启动，正在监听消息...")

    def stop(self):
        """停止Agent"""
        self.running = False
        print(f"🛑 [{self.agent_id}] 已停止")

    def run_once(self, timeout: float = 5.0):
        """
        运行一次消息处理循环

        Args:
            timeout: 等待消息的超时时间
        """
        message = self.receive(timeout=timeout)
        if message:
            print(f"\n[{self.agent_id}] 处理消息...")
            result = self.process_message(message)

            # 根据消息类型发送响应
            if message.type == MessageType.TASK:
                self.send_to(message.sender, MessageType.RESULT, result)
            elif message.type == MessageType.QUERY:
                self.send_to(message.sender, MessageType.RESPONSE, result)


class CoordinatorAgent(CommunicatingAgent):
    """协调者Agent：负责任务分配和结果收集"""

    def __init__(self, agent_id: str, message_bus: MessageBus, llm: Optional[ChatOpenAI] = None):
        """初始化协调者"""
        super().__init__(agent_id, message_bus, llm)
        self.workers: List[str] = []
        self.pending_tasks: Dict[str, Any] = {}

    def add_worker(self, worker_id: str):
        """
        添加工作者

        Args:
            worker_id: 工作者ID
        """
        self.workers.append(worker_id)
        print(f"✓ [{self.agent_id}] 添加工作者: {worker_id}")

    def assign_task(self, task: str) -> Dict[str, str]:
        """
        分配任务给所有工作者

        Args:
            task: 任务描述

        Returns:
            结果字典 {worker_id: result}
        """
        print(f"\n[{self.agent_id}] 开始分配任务...")
        print(f"任务: {task}")
        print(f"工作者数量: {len(self.workers)}\n")

        results = {}

        # 发送任务给所有工作者
        for worker_id in self.workers:
            self.send_to(worker_id, MessageType.TASK, task)

        # 收集结果
        for _ in self.workers:
            message = self.receive(timeout=30.0)
            if message and message.type == MessageType.RESULT:
                results[message.sender] = message.content
                print(f"✓ 收到 {message.sender} 的结果")

        return results

    def query_workers(self, query: str) -> Dict[str, str]:
        """
        查询所有工作者

        Args:
            query: 查询内容

        Returns:
            响应字典 {worker_id: response}
        """
        print(f"\n[{self.agent_id}] 查询所有工作者...")
        print(f"查询: {query}\n")

        responses = {}

        # 发送查询
        for worker_id in self.workers:
            self.send_to(worker_id, MessageType.QUERY, query)

        # 收集响应
        for _ in self.workers:
            message = self.receive(timeout=30.0)
            if message and message.type == MessageType.RESPONSE:
                responses[message.sender] = message.content
                print(f"✓ 收到 {message.sender} 的响应")

        return responses
