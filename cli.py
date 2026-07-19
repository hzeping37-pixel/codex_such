import os
import sys
import asyncio
from dotenv import load_dotenv
from core.agent_new import CodexAgent

load_dotenv()


async def main():
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("CODEX_MODEL", "deepseek-chat")

    if not api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("  export DEEPSEEK_API_KEY=sk-xxx")
        sys.exit(1)

    workdir = os.getcwd()
    agent = CodexAgent(api_key, base_url, model, workdir)

    print("=" * 60)
    print("  Codex CLI - AI 编程助手")
    print("  工作目录:", workdir)
    print("  模型:", model)
    print("  输入 'exit' 退出, 'clear' 清空历史")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not user_input:
            continue

        if user_input == "exit":
            print("再见!")
            break

        if user_input == "clear":
            agent.clear_history()
            print("历史已清空")
            continue

        print()

        try:
            async for chunk in agent.run(user_input):
                print(chunk, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f"\n错误: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n再见!")
