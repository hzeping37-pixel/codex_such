# Codex - AI 编程助手

真正的 Coding Agent：能操作文件系统、执行命令、形成闭环。

## 核心能力

| 工具 | 功能 |
|------|------|
| `read_file` | 读取文件内容 |
| `write_file` | 创建/覆盖文件 |
| `edit_file` | 精确替换文件内容 |
| `list_dir` | 列出目录内容 |
| `list_files` | 递归列出所有文件 |
| `delete_file` | 删除文件 |
| `shell` | 执行 Shell 命令 |
| `search_code` | 正则搜索代码库 |

## 闭环流程

```
用户输入需求
    ↓
AI 理解并规划
    ↓
执行工具（读文件/改文件/跑命令）
    ↓
验证结果
    ↓
返回给用户
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-xxx"

# Linux/Mac
export DEEPSEEK_API_KEY=sk-xxx
```

### 3. 运行

**双击启动（推荐）：**
- `启动Codex.bat` - Web 模式，浏览器访问 http://localhost:8000
- `启动CLI.bat` - 终端模式

**命令行启动：**

```bash
# CLI 模式
python main.py cli

# Web 模式
python main.py
```

## 使用示例

### 代码生成并执行

```
>>> 写一个 hello.py 打印 Hello World 并运行它
```

AI 会自动：
1. 创建 `hello.py`
2. 执行 `python hello.py`
3. 返回执行结果

### 读取并修改文件

```
>>> 读取 main.py，把所有 print 改成 logging
```

AI 会自动：
1. 读取文件内容
2. 分析需要修改的地方
3. 逐个替换
4. 验证修改结果

### 运行命令

```
>>> 看看当前目录有什么文件，然后运行 python --version
```

## 项目结构

```
codex/
├── main.py              # 入口（CLI / Web）
├── cli.py               # CLI 界面
├── core/
│   ├── agent_new.py     # Agent 核心（主循环）
│   ├── memory.py        # 对话记忆
│   └── tools/
│       ├── __init__.py  # Tool 基类
│       ├── registry.py  # 工具注册中心
│       ├── file_ops.py  # 文件操作工具
│       ├── shell.py     # Shell 执行工具
│       └── search.py    # 代码搜索工具
├── static/
│   └── index.html       # Web 界面
└── requirements.txt
```

## 与传统代码生成器的区别

| | 传统生成器 | Codex |
|---|-----------|-------|
| 输出 | 代码片段 | 执行结果 |
| 文件操作 | 无 | 读/写/改/删 |
| 命令执行 | 无 | 执行并返回结果 |
| 上下文 | 单轮 | 多轮对话 |
| 验证 | 无 | 自动验证
