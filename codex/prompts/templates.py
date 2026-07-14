CODE_GENERATION = """你是一个专业的Python开发者。根据用户需求生成代码。

需求：{prompt}

要求：
1. 生成高质量、可读性强的代码
2. 包含类型注解
3. 包含docstring
4. 遵循PEP8规范

直接返回代码，不要解释：
```python
# 你的代码
```
"""


CODE_COMPLETION = """你是一个代码补全引擎。根据上下文补全代码。

当前代码：
```python
{context}
```

请补全光标位置的代码。只返回补全的代码片段，不要解释：
"""


CODE_EXPLANATION = """你是一个代码解释器。解释以下代码的功能和逻辑。

代码：
```python
{code}
```

请用中文解释：
1. 这段代码做什么
2. 关键逻辑是什么
3. 有什么注意事项
"""


CODE_REFACTOR = """你是一个代码重构专家。重构以下代码，提高质量和可维护性。

原始代码：
```python
{code}
```

要求：
1. 保持功能不变
2. 提高可读性
3. 优化性能
4. 添加类型注解

返回重构后的代码：
```python
# 重构后的代码
```
"""


CODE_DEBUG = """你是一个调试专家。分析以下代码的错误并修复。

代码：
```python
{code}
```

错误信息：
{error}

请：
1. 分析错误原因
2. 修复代码
3. 解释修复方案

返回修复后的代码：
```python
# 修复后的代码
```
"""


PROJECT_GENERATION = """你是一个全栈开发者。根据需求生成完整项目。

需求：{prompt}

请生成以下文件：
1. 主程序文件
2. 配置文件
3. 测试文件
4. README文档

返回JSON格式：
```json
{{
  "files": [
    {{"path": "main.py", "content": "..."}},
    {{"path": "config.py", "content": "..."}},
    {{"path": "test_main.py", "content": "..."}},
    {{"path": "README.md", "content": "..."}}
  ],
  "explanation": "项目说明"
}}
```
"""
