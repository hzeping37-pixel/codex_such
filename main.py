import os
import sys
import json
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("CODEX_MODEL", "deepseek-chat")
    if not api_key:
        print("[Codex] ERROR: DEEPSEEK_API_KEY not set — API calls will fail")
    else:
        workdir = os.getcwd()
        try:
            from core.agent_new import CodexAgent
            agent = CodexAgent(api_key, base_url, model, workdir)
            print(f"[Codex] Agent initialized — model={model}, workdir={workdir}")
        except Exception as e:
            print(f"[Codex] Failed to initialize agent: {e}")
    yield


app = FastAPI(title="Codex", description="AI 编程助手", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
async def health():
    return {
        "status": "ok" if agent else "no_agent",
        "model": agent.model if agent else None,
        "tools": len(agent.tools.list_names()) if agent else 0,
    }


@app.post("/api/chat")
async def chat(chat_request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")

    async def generate():
        try:
            async for chunk in agent.run(chat_request.message):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'\\n[错误] {str(e)}\\n'}, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/chat/sync")
async def chat_sync(chat_request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    result = await agent.chat(chat_request.message)
    return {"response": result}


@app.get("/api/history")
async def get_history():
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    messages = agent.memory.get_messages()
    return {"messages": messages}


@app.delete("/api/history")
async def clear_history():
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    agent.clear_history()
    return {"status": "success"}


@app.get("/api/tools")
async def list_tools():
    if not agent:
        raise HTTPException(status_code=500, detail="服务未初始化")
    return {"tools": agent.tools.list_names()}


# ── Entry point ──
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from cli import main as cli_main
        asyncio.run(cli_main())
    else:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
