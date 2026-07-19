from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class TaskType(str, Enum):
    CHAT = "chat"                   # 日常对话
    GENERATE = "generate"           # 生成新代码
    COMPLETE = "complete"           # 代码补全
    EXPLAIN = "explain"             # 代码解释
    REFACTOR = "refactor"           # 代码重构
    DEBUG = "debug"                 # 调试修复
    PROJECT = "project"             # 生成完整项目


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class FileContent(BaseModel):
    path: str
    content: str


class CodeRequest(BaseModel):
    task_type: TaskType
    prompt: str
    context: Optional[str] = None           # 上下文代码
    files: Optional[List[FileContent]] = None  # 相关文件
    language: str = "python"


class FileOperation(BaseModel):
    action: str  # create, update, delete
    path: str
    content: Optional[str] = None


class ProjectResult(BaseModel):
    status: TaskStatus
    files: List[FileOperation] = []
    explanation: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0


class CodeResult(BaseModel):
    status: TaskStatus
    code: Optional[str] = None
    explanation: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
