from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import CodeRequest, TaskType
from core.agent import CodexAgent
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Codex", description="AI代码生成与项目构建系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = None


@app.on_event("startup")
async def startup():
    global agent
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise RuntimeError("请设置DEEPSEEK_API_KEY环境变量")
    agent = CodexAgent(api_key, base_url)


@app.post("/api/chat")
async def chat(request: CodeRequest):
    """对话接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    request.task_type = TaskType.CHAT
    result = await agent.process(request)
    return result


@app.post("/api/generate")
async def generate(request: CodeRequest):
    """代码生成接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    result = await agent.process(request)
    return result


@app.post("/api/complete")
async def complete(request: CodeRequest):
    """代码补全接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    request.task_type = TaskType.COMPLETE
    result = await agent.process(request)
    return result


@app.post("/api/explain")
async def explain(request: CodeRequest):
    """代码解释接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    request.task_type = TaskType.EXPLAIN
    result = await agent.process(request)
    return result


@app.post("/api/refactor")
async def refactor(request: CodeRequest):
    """代码重构接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    request.task_type = TaskType.REFACTOR
    result = await agent.process(request)
    return result


@app.post("/api/debug")
async def debug(request: CodeRequest):
    """代码调试接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    request.task_type = TaskType.DEBUG
    result = await agent.process(request)
    return result


@app.post("/api/project")
async def project(request: CodeRequest):
    """项目生成接口"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    request.task_type = TaskType.PROJECT
    result = await agent.process(request)
    return result


@app.get("/api/history")
async def get_history():
    """获取对话历史"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    history = agent.history.get_recent(100)
    return {"history": history}


@app.delete("/api/history")
async def clear_history():
    """清空对话历史"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    agent.history.clear()
    return {"status": "success"}


@app.get("/api/files")
async def list_files():
    """列出工作区文件"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    files = await agent.get_workspace_files()
    return {"files": files}


@app.get("/api/files/{path:path}")
async def read_file(path: str):
    """读取文件内容"""
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    try:
        content = await agent.read_file(path)
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端界面"""
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
