# Python 程序入口与异步编程基础

## 问题1：Python程序从哪里开始运行？

### 答案
Python程序从文件的**第一行**开始**逐行执行**，但只有遇到`if __name__ == "__main__":`时，才会执行该条件块内的代码。

### 执行流程
1. **导入阶段**：Python解释器先执行所有`import`语句
2. **定义阶段**：执行所有函数和类的定义（不执行函数体）
3. **执行阶段**：从文件开头逐行执行，遇到`if __name__ == "__main__":`时执行主程序逻辑

---

## 问题2：定义函数的时候发生了什么？

### 答案
当Python执行`def`或`async def`语句时，**不会执行函数体内部的代码**，而是创建一个**函数对象**并将其绑定到函数名上。

### 示例
```python
async def main():
    print("Hello")  # 这里不会立即执行
    
# 此时只是创建了名为 main 的函数对象，函数体未执行
```

### 关键点
- **函数定义是声明**：告诉Python"这里有一个函数"
- **函数体延迟执行**：只有调用函数时才执行内部代码
- **协程函数**：`async def`定义的是协程函数，调用时返回协程对象，而非执行函数体

---

## 问题3：`if __name__ == "__main__":` 是什么意思？

### 答案
这是Python的**程序入口模式**，用于判断当前脚本是作为**主程序运行**还是作为**模块被导入**。

### 工作原理
- `__name__`是Python内置变量
- 当脚本**直接运行**时：`__name__`的值为`"__main__"`
- 当脚本**被导入**时：`__name__`的值为模块名

### 作用
```python
if __name__ == "__main__":
    # 只有直接运行时才执行这里的代码
    # 如果被import，这部分会被跳过
    asyncio.run(main())
```

---

## 问题4：asyncio是什么？

### 答案
`asyncio`是Python标准库中用于**异步I/O编程**的模块，提供了：

1. **事件循环**（Event Loop）：协程的调度器
2. **协程支持**：`async/await`语法
3. **并发工具**：`gather()`、`create_task()`等

### 核心概念
| 概念 | 说明 |
|------|------|
| 协程（Coroutine） | 可暂停的函数，使用`async def`定义 |
| 事件循环 | 负责调度和执行协程 |
| await | 暂停当前协程，等待另一个协程完成 |
| Task | 封装协程的对象，由事件循环调度 |

---

## 问题5：为什么要用`asyncio.run()`来运行main函数？

### 答案
`asyncio.run()`是Python 3.7+推荐的**异步程序启动方式**，它会：

1. **创建事件循环**
2. **运行指定的协程**
3. **运行完毕后关闭事件循环**

### 代码解析
```python
asyncio.run(main())
# 等价于手动操作：
# loop = asyncio.new_event_loop()
# loop.run_until_complete(main())
# loop.close()
```

### 为什么不能直接调用`main()`？
```python
main()  # 返回协程对象，不会执行！
# <coroutine object main at 0x...>

asyncio.run(main())  # 真正执行协程
```

### 关键要点
- 协程函数调用返回**协程对象**，而非执行结果
- 需要事件循环来驱动协程执行
- `asyncio.run()`是最简、最安全的启动方式

---

## 代码引用

参考代码：[01_basic_async.py](file:///z:/Agent_WorkSpace/AI_Agent_Learning_project/projects/00-python-fundamentals/01-async-programming/src/01_basic_async.py#L316-L319)

```python
if __name__ == "__main__":
    # 运行异步主函数
    # asyncio.run() 是Python 3.7+ 推荐的运行方式
    asyncio.run(main())
```

---

## 相关链接

- [[Python异步编程在AI中的应用]]
- [[入门指南]]
