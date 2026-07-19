import os
from . import Tool


class ReadFileTool(Tool):
    name = "read_file"
    description = "读取指定路径的文件内容"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件的相对或绝对路径"
            }
        },
        "required": ["path"]
    }

    def execute(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"错误: 文件不存在 - {path}"
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if len(content) > 50000:
                return content[:50000] + f"\n... (文件过大，已截断，共 {len(content)} 字符)"
            return content
        except Exception as e:
            return f"错误: {str(e)}"


class WriteFileTool(Tool):
    name = "write_file"
    description = "创建或覆盖写入文件内容"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "要写入的内容"
            }
        },
        "required": ["path", "content"]
    }

    def execute(self, path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"已写入文件: {path} ({len(content)} 字符)"
        except Exception as e:
            return f"错误: {str(e)}"


class EditFileTool(Tool):
    name = "edit_file"
    description = "在文件中精确替换指定文本"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "old_string": {
                "type": "string",
                "description": "要被替换的原始文本"
            },
            "new_string": {
                "type": "string",
                "description": "替换后的新文本"
            }
        },
        "required": ["path", "old_string", "new_string"]
    }

    def execute(self, path: str, old_string: str, new_string: str) -> str:
        try:
            if not os.path.exists(path):
                return f"错误: 文件不存在 - {path}"
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_string not in content:
                return f"错误: 未找到要替换的文本"
            count = content.count(old_string)
            new_content = content.replace(old_string, new_string, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            msg = f"已替换: {path}"
            if count > 1:
                msg += f" (注意: 该文本出现 {count} 次，仅替换第一次)"
            return msg
        except Exception as e:
            return f"错误: {str(e)}"


class ListDirTool(Tool):
    name = "list_dir"
    description = "列出目录下的文件和子目录"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "目录路径，默认为当前目录"
            }
        },
        "required": []
    }

    def execute(self, path: str = ".") -> str:
        try:
            if not os.path.exists(path):
                return f"错误: 目录不存在 - {path}"
            entries = []
            for entry in sorted(os.listdir(path)):
                full = os.path.join(path, entry)
                if os.path.isdir(full):
                    entries.append(f"  [DIR]  {entry}/")
                else:
                    size = os.path.getsize(full)
                    entries.append(f"  [FILE] {entry} ({size} bytes)")
            if not entries:
                return f"目录为空: {path}"
            return f"目录内容 ({path}):\n" + "\n".join(entries)
        except Exception as e:
            return f"错误: {str(e)}"


class DeleteFileTool(Tool):
    name = "delete_file"
    description = "删除指定文件"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要删除的文件路径"
            }
        },
        "required": ["path"]
    }

    def execute(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"错误: 文件不存在 - {path}"
            if os.path.isdir(path):
                return f"错误: 这是一个目录，不能用 delete_file 删除"
            os.remove(path)
            return f"已删除: {path}"
        except Exception as e:
            return f"错误: {str(e)}"
