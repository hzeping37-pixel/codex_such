import subprocess
import sys
import os
from . import Tool


class ShellTool(Tool):
    name = "shell"
    description = "执行 Shell 命令并返回输出"
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "要执行的 Shell 命令"
            },
            "timeout": {
                "type": "integer",
                "description": "超时时间（秒），默认 30"
            }
        },
        "required": ["command"]
    }

    def __init__(self, workdir: str = None):
        self.workdir = workdir or os.getcwd()
        self.blocked_patterns = [
            "rm -rf /",
            "mkfs",
            "> /dev/sda",
            ":(){ :|:& };:",
            "dd if=/dev/zero",
            "chmod -R 777 /",
        ]

    def execute(self, command: str, timeout: int = 30) -> str:
        for pattern in self.blocked_patterns:
            if pattern in command:
                return f"安全拒绝: 检测到危险命令模式 '{pattern}'"

        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workdir,
                env=env
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n"
                output += result.stderr

            if not output.strip():
                output = "(命令执行成功，无输出)"

            if len(output) > 10000:
                output = output[:10000] + "\n... (输出过长，已截断)"

            returncode_info = f"[返回码: {result.returncode}]"
            return f"{returncode_info}\n{output}"

        except subprocess.TimeoutExpired:
            return f"错误: 命令超时（{timeout}秒限制）"
        except Exception as e:
            return f"错误: {str(e)}"
