import json
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from .tools.registry import ToolRegistry
from .memory import ConversationMemory


SYSTEM_PROMPT = """你是一个专业的 AI 编程助手，可以直接操作文件系统和执行命令来完成编程任务。

你的能力：
1. 读取、创建、编辑、删除文件
2. 执行 Shell 命令
3. 搜索代码库
4. 分析代码并给出建议

工作流程：
1. 理解用户的编程需求
2. 如果需要，先用 list_files 或 read_file 了解项目结构
3. 使用合适的工具来完成任务
4. 验证结果（如执行代码、运行测试）

重要规则：
- 在修改文件前，先读取文件了解现有内容
- 执行命令前，确认命令是安全的
- 如果任务复杂，分步骤执行
- 用中文回复用户"""


class CodexAgent:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat", workdir: str = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.tools = ToolRegistry(workdir)
        self.memory = ConversationMemory()
        self.max_turns = 30

    async def run(self, user_input: str) -> AsyncGenerator[str, None]:
        """流式执行 Agent 循环，逐 token 产出文本"""
        self.memory.add_user(user_input)

        for turn in range(self.max_turns):
            messages = self.memory.get_messages(SYSTEM_PROMPT)
            tool_defs = self.tools.definitions()

            # ── 流式调用 LLM ──
            try:
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tool_defs if tool_defs else None,
                    tool_choice="auto" if tool_defs else None,
                    temperature=0.3,
                    max_tokens=4096,
                    stream=True,
                )
            except Exception as e:
                yield f"\n[错误] API 调用失败: {str(e)}\n"
                return

            # ── 处理流式 chunk ──
            full_content = ""
            tool_call_buffers: dict[int, dict] = {}  # index → {id, function: {name, arguments}}

            async for chunk in stream:
                if chunk.choices is None or len(chunk.choices) == 0:
                    continue

                delta = chunk.choices[0].delta
                if delta is None:
                    continue

                # 文本内容 — 立即产出给前端
                if delta.content:
                    full_content += delta.content
                    yield delta.content

                # 工具调用 delta（流式累积）
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_call_buffers:
                            tool_call_buffers[idx] = {
                                "id": "",
                                "function": {"name": "", "arguments": ""}
                            }
                        buf = tool_call_buffers[idx]
                        if tc_delta.id:
                            buf["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                buf["function"]["name"] += tc_delta.function.name
                            if tc_delta.function.arguments:
                                buf["function"]["arguments"] += tc_delta.function.arguments

            # ── 无工具调用 → 保存文本并结束 ──
            if not tool_call_buffers:
                if full_content:
                    self.memory.add_assistant(full_content)
                return

            # ── 执行工具调用 ──
            tool_messages = []
            assistant_tool_calls = []

            for idx in sorted(tool_call_buffers.keys()):
                tc = tool_call_buffers[idx]
                func_name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                yield f"\n[Tool] {func_name}({json.dumps(args, ensure_ascii=False)[:200]})\n"

                try:
                    result = self.tools.execute(func_name, **args)
                except Exception as e:
                    result = f"工具执行错误: {str(e)}"

                display_result = result[:500] + "..." if len(result) > 500 else result
                yield f"[Result] {display_result}\n"

                self.memory.add_tool_call(tc["id"], func_name, args)
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result
                })
                assistant_tool_calls.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": func_name,
                        "arguments": tc["function"]["arguments"]
                    }
                })

            # ── 将助手消息（含 tool_calls）加入记忆（仅一条）──
            self.memory.messages.append({
                "role": "assistant",
                "content": full_content or None,
                "tool_calls": assistant_tool_calls
            })
            self.memory.messages.extend(tool_messages)

        # 达到最大轮次
        yield "\n[提示] 已达到最大执行轮次，任务可能未完成。\n"

    async def chat(self, user_input: str) -> str:
        """非流式对话，返回完整字符串"""
        result = []
        async for chunk in self.run(user_input):
            result.append(chunk)
        return "".join(result)

    def clear_history(self):
        self.memory.clear()
