import json
import os
from datetime import datetime
from typing import List, Optional


class ChatHistory:
    def __init__(self, storage_dir: str = "history"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.history_file = os.path.join(storage_dir, "chat_history.json")
        self._load()
    
    def _load(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []
    
    def _save(self):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add(self, user_msg: str, ai_msg: str, task_type: str = "chat", 
            code: str = None, saved_file: str = None):
        """添加一条对话记录"""
        record = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "ai": ai_msg,
            "task_type": task_type,
            "code": code,
            "saved_file": saved_file
        }
        self.history.append(record)
        self._save()
        return record
    
    def get_all(self) -> List[dict]:
        """获取所有历史记录"""
        return self.history
    
    def get_recent(self, limit: int = 50) -> List[dict]:
        """获取最近的记录"""
        return self.history[-limit:]
    
    def clear(self):
        """清空历史记录"""
        self.history = []
        self._save()
    
    def delete(self, record_id: int):
        """删除指定记录"""
        self.history = [r for r in self.history if r["id"] != record_id]
        self._save()
