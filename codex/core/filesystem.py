import os
import aiofiles
from typing import List
from models.schemas import FileOperation


class FileSystem:
    def __init__(self, workspace: str = "workspace"):
        self.workspace = workspace
        os.makedirs(workspace, exist_ok=True)
    
    async def execute_operations(self, operations: List[FileOperation]) -> List[dict]:
        """执行文件操作"""
        results = []
        for op in operations:
            try:
                if op.action == "create":
                    await self._create_file(op.path, op.content)
                    results.append({"path": op.path, "status": "created"})
                elif op.action == "update":
                    await self._update_file(op.path, op.content)
                    results.append({"path": op.path, "status": "updated"})
                elif op.action == "delete":
                    await self._delete_file(op.path)
                    results.append({"path": op.path, "status": "deleted"})
            except Exception as e:
                results.append({"path": op.path, "status": "error", "error": str(e)})
        return results
    
    async def _create_file(self, path: str, content: str):
        """创建文件"""
        full_path = os.path.join(self.workspace, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def _update_file(self, path: str, content: str):
        """更新文件"""
        await self._create_file(path, content)
    
    async def _delete_file(self, path: str):
        """删除文件"""
        full_path = os.path.join(self.workspace, path)
        if os.path.exists(full_path):
            os.remove(full_path)
    
    async def read_file(self, path: str) -> str:
        """读取文件"""
        full_path = os.path.join(self.workspace, path)
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def list_files(self) -> List[str]:
        """列出所有文件"""
        files = []
        for root, dirs, filenames in os.walk(self.workspace):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), self.workspace)
                files.append(rel_path)
        return files
    
    async def get_file_tree(self) -> dict:
        """获取文件树"""
        tree = {"name": "workspace", "type": "directory", "children": []}
        for root, dirs, filenames in os.walk(self.workspace):
            level = root.replace(self.workspace, '').count(os.sep)
            indent = '  ' * (level - 1)
            dirname = os.path.basename(root)
            
            if level > 0:
                node = {"name": dirname, "type": "directory", "children": []}
                tree["children"].append(node)
            
            for filename in filenames:
                file_node = {"name": filename, "type": "file"}
                if level == 0:
                    tree["children"].append(file_node)
        
        return tree
