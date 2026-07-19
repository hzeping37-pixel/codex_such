from typing import Dict, Any
from .file_ops import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool, DeleteFileTool
from .shell import ShellTool
from .search import SearchCodeTool, ListFilesTool
from . import Tool


class ToolRegistry:
    def __init__(self, workdir: str = None):
        self.tools: Dict[str, Tool] = {}
        self._register_all(workdir)

    def _register_all(self, workdir: str = None):
        self.register(ReadFileTool())
        self.register(WriteFileTool())
        self.register(EditFileTool())
        self.register(ListDirTool())
        self.register(DeleteFileTool())
        self.register(ShellTool(workdir))
        self.register(SearchCodeTool())
        self.register(ListFilesTool())

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self.tools.get(name)

    def execute(self, name: str, **kwargs) -> str:
        tool = self.tools.get(name)
        if not tool:
            return f"错误: 未知工具 '{name}'"
        return tool.execute(**kwargs)

    def definitions(self) -> list:
        return [tool.to_schema() for tool in self.tools.values()]

    def list_names(self) -> list:
        return list(self.tools.keys())
