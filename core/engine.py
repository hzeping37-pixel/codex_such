import re
import json
from openai import AsyncOpenAI
from prompts.templates import (
    CODE_GENERATION, CODE_COMPLETION, CODE_EXPLANATION,
    CODE_REFACTOR, CODE_DEBUG, PROJECT_GENERATION
)
from models.schemas import TaskType, FileOperation


class CodeEngine:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    async def execute(self, task_type: TaskType, prompt: str, 
                      context: str = None, code: str = None, 
                      error: str = None) -> tuple:
        """执行不同类型的代码任务"""
        
        if task_type == TaskType.CHAT:
            # 智能识别意图
            detected_type = await self._detect_intent(prompt)
            if detected_type != TaskType.CHAT:
                # 识别为其他任务，自动切换
                return await self.execute(detected_type, prompt, context, code, error)
            return await self._chat(prompt)
        elif task_type == TaskType.GENERATE:
            return await self._generate(prompt)
        elif task_type == TaskType.COMPLETE:
            return await self._complete(context or prompt)
        elif task_type == TaskType.EXPLAIN:
            return await self._explain(code or prompt)
        elif task_type == TaskType.REFACTOR:
            return await self._refactor(code or prompt)
        elif task_type == TaskType.DEBUG:
            return await self._debug(code or prompt, error or "")
        elif task_type == TaskType.PROJECT:
            return await self._generate_project(prompt)
        
        return None, "未知任务类型"
    
    async def _detect_intent(self, prompt: str) -> TaskType:
        """智能识别用户意图"""
        prompt_lower = prompt.lower()
        
        # 代码生成相关关键词
        generate_keywords = ['写一个', '写个', '实现', '创建', '生成', '开发', '编写', 
                           '帮我写', '帮我实现', '帮我创建', '帮我写个', '代码', '函数', '类']
        
        # 项目生成相关关键词
        project_keywords = ['项目', '工程', '完整的', '整个', 'web应用', 'api', '网站',
                          'flask项目', 'django项目', 'fastapi项目']
        
        # 代码解释相关关键词
        explain_keywords = ['解释', '说明', '这段代码', '什么意思', '作用', '功能',
                          '这段代码是', '这个函数', '这个类', '这段逻辑']
        
        # 代码重构相关关键词
        refactor_keywords = ['重构', '优化', '改进', '简化', '重构一下', '优化一下',
                          '代码质量', '可读性', '性能']
        
        # 调试相关关键词
        debug_keywords = ['修复', '修复bug', '调试', '出错了', '报错', '错误',
                        '不工作', '有问题', '失败']
        
        # 判断意图
        if any(kw in prompt_lower for kw in project_keywords):
            return TaskType.PROJECT
        elif any(kw in prompt_lower for kw in generate_keywords):
            return TaskType.GENERATE
        elif any(kw in prompt_lower for kw in explain_keywords):
            return TaskType.EXPLAIN
        elif any(kw in prompt_lower for kw in refactor_keywords):
            return TaskType.REFACTOR
        elif any(kw in prompt_lower for kw in debug_keywords):
            return TaskType.DEBUG
        
        return TaskType.CHAT
    
    async def _chat(self, prompt: str) -> tuple[str, str]:
        """日常对话"""
        response = await self._call_llm(
            prompt,
            "你是一个友好的AI助手，擅长编程和日常对话。用中文回答，语气亲切自然。"
        )
        return None, response
    
    async def _generate(self, prompt: str) -> tuple[str, str]:
        """生成代码"""
        response = await self._call_llm(
            CODE_GENERATION.format(prompt=prompt),
            "你是一个专业的Python开发者，只返回代码。"
        )
        code = self._extract_code(response)
        return code, None
    
    async def _complete(self, context: str) -> tuple[str, str]:
        """代码补全"""
        response = await self._call_llm(
            CODE_COMPLETION.format(context=context),
            "你是一个代码补全引擎，只返回补全的代码。"
        )
        code = self._extract_code(response)
        return code, None
    
    async def _explain(self, code: str) -> tuple[str, str]:
        """解释代码"""
        response = await self._call_llm(
            CODE_EXPLANATION.format(code=code),
            "你是一个代码解释专家，用中文解释代码。"
        )
        return None, response
    
    async def _refactor(self, code: str) -> tuple[str, str]:
        """重构代码"""
        response = await self._call_llm(
            CODE_REFACTOR.format(code=code),
            "你是一个代码重构专家，只返回重构后的代码。"
        )
        new_code = self._extract_code(response)
        return new_code, None
    
    async def _debug(self, code: str, error: str) -> tuple[str, str]:
        """调试代码"""
        response = await self._call_llm(
            CODE_DEBUG.format(code=code, error=error),
            "你是一个调试专家，只返回修复后的代码。"
        )
        code = self._extract_code(response)
        return code, None
    
    async def _generate_project(self, prompt: str) -> tuple[list, str]:
        """生成完整项目"""
        response = await self._call_llm(
            PROJECT_GENERATION.format(prompt=prompt),
            "你是一个全栈开发者，返回JSON格式的项目文件。"
        )
        
        try:
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                files = [FileOperation(**f) for f in data.get("files", [])]
                explanation = data.get("explanation", "")
                return files, explanation
        except Exception as e:
            pass
        
        # 如果JSON解析失败，返回代码块
        files = self._extract_files_from_text(response)
        return files, None
    
    async def _call_llm(self, prompt: str, system: str) -> str:
        """调用LLM"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content
    
    def _extract_code(self, text: str) -> str:
        """从响应中提取代码"""
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        return text.strip()
    
    def _extract_files_from_text(self, text: str) -> list:
        """从文本中提取文件"""
        files = []
        # 简单的文件提取逻辑
        code_blocks = re.findall(r'```(?:python|json|md)?\n(.*?)```', text, re.DOTALL)
        for i, block in enumerate(code_blocks):
            files.append(FileOperation(
                action="create",
                path=f"file_{i}.py",
                content=block.strip()
            ))
        return files
