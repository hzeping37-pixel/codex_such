import os
import re
from . import Tool


class SearchCodeTool(Tool):
    name = "search_code"
    description = "在代码库中搜索包含指定内容的文件"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "搜索的正则表达式模式"
            },
            "path": {
                "type": "string",
                "description": "搜索目录，默认当前目录"
            },
            "include": {
                "type": "string",
                "description": "文件名过滤，如 '*.py' 或 '*.js'"
            }
        },
        "required": ["pattern"]
    }

    def execute(self, pattern: str, path: str = ".", include: str = None) -> str:
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"错误: 无效的正则表达式 - {e}"

        matches = []
        file_count = 0

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.venv', 'venv')]

            for filename in files:
                if include:
                    import fnmatch
                    if not fnmatch.fnmatch(filename, include):
                        continue

                filepath = os.path.join(root, filename)

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    for i, line in enumerate(content.split("\n"), 1):
                        if regex.search(line):
                            matches.append(f"{filepath}:{i}: {line.strip()[:200]}")
                            file_count += 1
                            if len(matches) >= 50:
                                break

                except (IOError, UnicodeDecodeError):
                    continue

                if len(matches) >= 50:
                    break

            if len(matches) >= 50:
                break

        if not matches:
            return f"未找到匹配 '{pattern}' 的内容"

        result = f"搜索结果 ({len(matches)} 个匹配，来自 {file_count} 个文件):\n\n"
        result += "\n".join(matches)
        if len(matches) >= 50:
            result += "\n\n(结果已限制为 50 条)"
        return result


class ListFilesTool(Tool):
    name = "list_files"
    description = "列出目录下所有文件（递归）"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "目录路径，默认当前目录"
            },
            "include": {
                "type": "string",
                "description": "文件名过滤，如 '*.py'"
            }
        },
        "required": []
    }

    def execute(self, path: str = ".", include: str = None) -> str:
        try:
            files = []
            for root, dirs, filenames in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.venv')]

                for filename in filenames:
                    if include:
                        import fnmatch
                        if not fnmatch.fnmatch(filename, include):
                            continue
                    filepath = os.path.relpath(os.path.join(root, filename), path)
                    files.append(filepath)

            if not files:
                return f"未找到文件: {path}"

            files.sort()
            return f"文件列表 ({len(files)} 个文件):\n" + "\n".join(files[:200])
        except Exception as e:
            return f"错误: {str(e)}"
