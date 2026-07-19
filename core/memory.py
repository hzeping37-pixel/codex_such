from typing import List, Dict, Optional


class ConversationMemory:
    def __init__(self, max_turns: int = 30):
        self.messages: List[Dict] = []
        self.max_turns = max_turns

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_call(self, tool_call_id: str, name: str, args: dict):
        pass

    def get_messages(self, system_prompt: str = None) -> List[Dict]:
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        result.extend(self.messages[-self.max_turns * 4:])
        return result

    def clear(self):
        self.messages.clear()
