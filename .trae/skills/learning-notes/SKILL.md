---
name: "learning-notes"
description: "Collects and organizes user's learning questions and answers into Obsidian-formatted markdown files. Invoke when user asks to document learning questions or organize study notes."
---

# Learning Notes Skill

## Overview

This skill helps organize learning questions and answers into structured Obsidian-formatted markdown files. It collects user's programming questions, provides clear explanations, and stores them in a dedicated learning folder.

## Features

- Organizes questions by topic/type into separate markdown files
- Uses Obsidian-compatible format with links between related notes
- Supports code references and syntax highlighting
- Maintains consistent structure across all learning notes

## When to Invoke

- User asks programming/technical questions during learning
- User wants to document their study notes
- User asks to organize questions into structured documentation
- User wants to create learning materials with proper formatting

## File Organization

All notes are stored in: `docs/07-干中学/`

Notes are organized by topic:
- **Python基础概念.md** - General Python questions
- **异步编程.md** - Async programming questions
- **AI开发.md** - AI/ML related questions
- **其他主题.md** - Miscellaneous topics

## Question & Answer Format

### Standard Template

```markdown
## 问题X：<问题标题>

### 答案
<简洁明了的回答>

### 详细解释
<深入解释，可包含代码示例、表格、列表等>

### 代码引用
参考代码：[文件名](file:///absolute/path/to/file#Lstart-Lend)

```python
# 相关代码示例
code_here()
```

### 关键点
- 要点1
- 要点2
- 要点3

---
```

### Format Rules

1. **Question Title**: Clear, concise question statement
2. **Answer**: Direct response to the question
3. **Detailed Explanation**: Comprehensive explanation with examples
4. **Code References**: Always include file links using `file:///` protocol
5. **Key Points**: Bullet points summarizing important takeaways
6. **Horizontal Rule**: Separator between questions (`---`)

## Obsidian Linking

When questions are related, add backlinks:

```markdown
## 相关链接

- [[Python基础概念]]
- [[异步编程]]
```

## Example Usage

### Input
```
第一个问题：Python程序从哪里开始运行？这段代码是什么意思？
```

### Output (Written to Python基础概念.md)
```markdown
## 问题1：Python程序从哪里开始运行？

### 答案
Python程序从文件的第一行开始逐行执行，遇到`if __name__ == "__main__":`时执行主程序。

### 详细解释
执行流程分为三个阶段：
1. 导入阶段：执行所有import语句
2. 定义阶段：执行函数/类定义（不执行函数体）
3. 执行阶段：逐行执行，遇到主入口时执行

### 代码引用
参考代码：[01_basic_async.py](file:///path/to/01_basic_async.py#L316-L319)

```python
if __name__ == "__main__":
    asyncio.run(main())
```

### 关键点
- Python解释器逐行执行代码
- `__name__ == "__main__"` 判断是否直接运行
- 函数定义时不执行函数体

---
```

## Best Practices

1. **Consistency**: Use the same format for all questions
2. **Clarity**: Write clear, concise answers
3. **Code References**: Always link to relevant code
4. **Backlinks**: Connect related questions with Obsidian links
5. **Organization**: Group similar questions into appropriate topic files

## Folder Structure

```
docs/
└── 07-干中学/
    ├── Python基础概念.md
    ├── 异步编程.md
    ├── AI开发.md
    └── 其他主题.md
```

## Usage Notes

- If the target folder doesn't exist, it will be created automatically
- Questions are appended to existing files based on topic
- New topics get their own dedicated markdown files
- All file references use absolute paths for cross-platform compatibility
