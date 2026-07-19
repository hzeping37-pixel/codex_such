from models.schemas import (
    TaskType, TaskStatus, CodeRequest, 
    CodeResult, ProjectResult, FileOperation
)
from core.engine import CodeEngine
from core.executor import CodeExecutor
from core.filesystem import FileSystem
from core.history import ChatHistory


class CodexAgent:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.engine = CodeEngine(api_key, base_url)
        self.executor = CodeExecutor()
        self.fs = FileSystem("workspace")
        self.history = ChatHistory("history")
    
    async def process(self, request: CodeRequest) -> dict:
        """处理用户请求"""
        
        if request.task_type == TaskType.CHAT:
            result = await self._handle_chat(request)
        elif request.task_type == TaskType.PROJECT:
            result = await self._handle_project(request)
        else:
            result = await self._handle_code(request)
        
        # 保存对话历史
        ai_response = result.get("explanation", "") or result.get("code", "") or result.get("error", "")
        self.history.add(
            user_msg=request.prompt,
            ai_msg=ai_response[:500],  # 限制长度
            task_type=result.get("task_type", request.task_type.value),
            code=result.get("code"),
            saved_file=result.get("saved_file")
        )
        
        return result
    
    async def _handle_code(self, request: CodeRequest) -> dict:
        """处理代码任务"""
        max_retries = 3
        code = None
        
        for attempt in range(max_retries):
            # 执行任务
            code, explanation = await self.engine.execute(
                request.task_type,
                request.prompt,
                context=request.context,
                code=request.context
            )
            
            # 如果是生成或补全，执行验证
            if request.task_type in [TaskType.GENERATE, TaskType.COMPLETE] and code:
                result = await self.executor.run(code)
                
                if result["success"]:
                    # 生成文件名并保存
                    filename = self._generate_filename(request.prompt, "py")
                    await self.fs._create_file(filename, code)
                    
                    return {
                        "status": TaskStatus.SUCCESS,
                        "code": code,
                        "explanation": explanation,
                        "saved_file": filename,
                        "attempts": attempt + 1
                    }
                else:
                    # 尝试修复
                    if attempt < max_retries - 1:
                        fixed_code, _ = await self.engine.execute(
                            TaskType.DEBUG,
                            request.prompt,
                            code=code,
                            error=result["stderr"]
                        )
                        if fixed_code:
                            code = fixed_code
                    continue
            
            # 解释和重构不需要执行验证
            if explanation:
                # 如果有代码也保存
                saved_file = None
                if code:
                    saved_file = self._generate_filename(request.prompt, "py")
                    await self.fs._create_file(saved_file, code)
                
                return {
                    "status": TaskStatus.SUCCESS,
                    "code": code,
                    "explanation": explanation,
                    "saved_file": saved_file,
                    "attempts": attempt + 1
                }
        
        return {
            "status": TaskStatus.FAILED,
            "code": code,
            "error": "达到最大重试次数",
            "attempts": max_retries
        }
    
    async def _handle_chat(self, request: CodeRequest) -> dict:
        """处理日常对话（带智能意图识别）"""
        # 先检测意图
        detected_type = await self.engine._detect_intent(request.prompt)
        
        # 执行对应任务
        if detected_type != TaskType.CHAT:
            result = await self._handle_code_for_type(detected_type, request.prompt)
            result["task_type"] = detected_type.value
            return result
        
        # 纯对话
        _, explanation = await self.engine.execute(
            TaskType.CHAT,
            request.prompt
        )
        
        return {
            "status": TaskStatus.SUCCESS,
            "task_type": "chat",
            "explanation": explanation,
            "attempts": 1
        }
    
    async def _handle_code_for_type(self, task_type: TaskType, prompt: str) -> dict:
        """根据类型处理代码任务"""
        max_retries = 3
        code = None
        
        for attempt in range(max_retries):
            code, explanation = await self.engine.execute(task_type, prompt)
            
            if task_type == TaskType.GENERATE and code:
                result = await self.executor.run(code)
                if result["success"]:
                    filename = self._generate_filename(prompt, "py")
                    await self.fs._create_file(filename, code)
                    return {
                        "status": TaskStatus.SUCCESS,
                        "code": code,
                        "explanation": explanation,
                        "saved_file": filename,
                        "attempts": attempt + 1
                    }
                else:
                    if attempt < max_retries - 1:
                        fixed_code, _ = await self.engine.execute(
                            TaskType.DEBUG, prompt, code=code, error=result["stderr"]
                        )
                        if fixed_code:
                            code = fixed_code
                    continue
            
            if explanation:
                saved_file = None
                if code and task_type in [TaskType.GENERATE, TaskType.REFACTOR]:
                    saved_file = self._generate_filename(prompt, "py")
                    await self.fs._create_file(saved_file, code)
                return {
                    "status": TaskStatus.SUCCESS,
                    "code": code,
                    "explanation": explanation,
                    "saved_file": saved_file,
                    "attempts": attempt + 1
                }
        
        return {
            "status": TaskStatus.FAILED,
            "code": code,
            "error": "达到最大重试次数",
            "attempts": max_retries
        }
    
    def _generate_filename(self, prompt: str, ext: str) -> str:
        """根据提示生成文件名"""
        import re
        # 提取关键词作为文件名
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', prompt)
        if not words:
            words = ["generated"]
        # 取前3个词作为文件名
        name = "_".join(words[:3]).lower()
        name = re.sub(r'[^a-z0-9_]', '', name)
        return f"{name}.{ext}"
    
    async def _handle_project(self, request: CodeRequest) -> dict:
        """处理项目生成任务"""
        max_retries = 3
        
        for attempt in range(max_retries):
            # 生成项目
            files, explanation = await self.engine.execute(
                TaskType.PROJECT,
                request.prompt
            )
            
            if files:
                # 执行文件操作
                results = await self.fs.execute_operations(files)
                
                # 构建文件内容列表用于显示
                file_contents = []
                for f in files:
                    if f.content:
                        file_contents.append({
                            "path": f.path,
                            "content": f.content
                        })
                
                return {
                    "status": TaskStatus.SUCCESS,
                    "files": [r["path"] for r in results if r["status"] != "error"],
                    "file_contents": file_contents,
                    "explanation": explanation,
                    "attempts": attempt + 1
                }
        
        return {
            "status": TaskStatus.FAILED,
            "error": "项目生成失败",
            "attempts": max_retries
        }
    
    async def get_workspace_files(self) -> list:
        """获取工作区文件列表"""
        return await self.fs.list_files()
    
    async def read_file(self, path: str) -> str:
        """读取文件内容"""
        return await self.fs.read_file(path)
