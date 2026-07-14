# Codex - AI代码助手

一个功能完整的AI代码生成与项目构建系统。

## 功能特点

| 功能 | 说明 |
|------|------|
| 项目生成 | 一键生成完整项目结构 |
| 代码生成 | 根据需求生成代码 |
| 代码补全 | 根据上下文补全代码 |
| 代码解释 | 解释代码功能和逻辑 |
| 代码重构 | 优化代码质量和可读性 |
| 代码调试 | 自动分析并修复错误 |

## 快速开始

### 双击启动
```
启动Codex.bat
```

### 手动启动
```bash
cd codex
pip install -r requirements.txt
python main.py
```

浏览器访问: http://localhost:8000

## 项目结构

```
codex/
├── main.py              # FastAPI入口
├── core/
│   ├── engine.py        # 代码生成引擎
│   ├── executor.py      # 代码执行器
│   ├── filesystem.py    # 文件系统操作
│   └── agent.py         # 核心代理
├── prompts/
│   └── templates.py     # LLM提示词
├── models/
│   └── schemas.py       # 数据模型
├── static/
│   └── index.html       # 前端界面
├── workspace/           # 生成的代码存放
└── requirements.txt
```

## API接口

| 接口 | 说明 |
|------|------|
| POST /api/project | 生成完整项目 |
| POST /api/generate | 生成代码 |
| POST /api/complete | 代码补全 |
| POST /api/explain | 代码解释 |
| POST /api/refactor | 代码重构 |
| POST /api/debug | 代码调试 |
| GET /api/files | 列出文件 |
| GET /api/files/{path} | 读取文件 |

## 使用示例

### 生成Flask项目
```
生成一个Flask REST API项目，包含用户CRUD操作
```

### 代码解释
```
解释以下代码的功能：
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 代码重构
```
重构以下代码，提高性能和可读性：
[粘贴代码]
```

## 技术栈

- Python 3.10+
- FastAPI
- DeepSeek API
- aiofiles
"# codex_such" 
"# codex_such" 
