"""
qCreateRunPrompt - 创建并运行提示词模块

功能：
1. 创建自定义提示词模板（Create Prompt）
2. 使用提示词模板生成并执行代码（Run Prompt）
3. 管理已创建的提示词模板

使用方式：
    from prompts.create_run import CreateRunPrompt
    
    crp = CreateRunPrompt()
    
    # 创建模板
    crp.create_template("my_template", "用 {language} 写一个 {task} 程序")
    
    # 运行模板
    result = crp.run_template("my_template", language="Python", task="Hello World")
"""

import json
import os
import re
from typing import Dict, Optional, List
from datetime import datetime


# 默认模板存储路径
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


class PromptTemplate:
    """提示词模板类"""
    
    def __init__(self, name: str, template: str, description: str = "", 
                 variables: List[str] = None, created_at: str = None):
        self.name = name
        self.template = template
        self.description = description
        self.variables = variables or self._extract_variables(template)
        self.created_at = created_at or datetime.now().isoformat()
    
    def _extract_variables(self, template: str) -> List[str]:
        """从模板中提取变量名 {var_name}"""
        return re.findall(r'\{(\w+)\}', template)
    
    def render(self, **kwargs) -> str:
        """用传入的参数渲染模板"""
        # 检查是否所有变量都被提供
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"缺少模板变量: {', '.join(missing)}")
        
        # 渲染模板
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"渲染模板时出错: 缺少变量 {e}")
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "variables": self.variables,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PromptTemplate":
        return cls(
            name=data["name"],
            template=data["template"],
            description=data.get("description", ""),
            variables=data.get("variables"),
            created_at=data.get("created_at")
        )


class CreateRunPrompt:
    """
    创建并运行提示词管理器
    
    提供模板的 CRUD 操作和渲染执行功能。
    """
    
    def __init__(self, storage_dir: str = TEMPLATES_DIR):
        self.storage_dir = storage_dir
        self._templates: Dict[str, PromptTemplate] = {}
        os.makedirs(storage_dir, exist_ok=True)
        self._load_templates()
    
    # ── 模板管理 ──
    
    def create_template(self, name: str, template: str, description: str = "") -> PromptTemplate:
        """
        创建一个新的提示词模板
        
        参数:
            name: 模板名称（唯一标识）
            template: 模板内容，使用 {var_name} 作为变量占位符
            description: 模板描述
        
        返回:
            PromptTemplate 对象
        
        示例:
            crp.create_template(
                name="code_gen",
                template="用 {language} 写一个 {task}，要求：{requirements}",
                description="代码生成模板"
            )
        """
        if name in self._templates:
            raise ValueError(f"模板 '{name}' 已存在，请使用 update_template 更新")
        
        if not name.strip():
            raise ValueError("模板名称不能为空")
        
        if not template.strip():
            raise ValueError("模板内容不能为空")
        
        pt = PromptTemplate(name=name, template=template, description=description)
        self._templates[name] = pt
        self._save_template(pt)
        return pt
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取指定名称的模板"""
        return self._templates.get(name)
    
    def update_template(self, name: str, template: str = None, 
                        description: str = None) -> PromptTemplate:
        """更新已有模板"""
        if name not in self._templates:
            raise ValueError(f"模板 '{name}' 不存在")
        
        pt = self._templates[name]
        if template is not None:
            pt.template = template
            pt.variables = pt._extract_variables(template)
        if description is not None:
            pt.description = description
        
        self._save_template(pt)
        return pt
    
    def delete_template(self, name: str) -> bool:
        """删除指定模板"""
        if name not in self._templates:
            return False
        
        del self._templates[name]
        filepath = os.path.join(self.storage_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    
    def list_templates(self) -> List[dict]:
        """列出所有模板"""
        return [pt.to_dict() for pt in self._templates.values()]
    
    # ── 模板执行 ──
    
    def render_prompt(self, name: str, **kwargs) -> str:
        """
        渲染模板生成提示词
        
        参数:
            name: 模板名称
            **kwargs: 模板变量值
        
        返回:
            渲染后的提示词字符串
        
        示例:
            prompt = crp.render_prompt(
                "code_gen", 
                language="Python", 
                task="计算器", 
                requirements="支持加减乘除"
            )
        """
        pt = self.get_template(name)
        if not pt:
            raise ValueError(f"模板 '{name}' 不存在")
        
        return pt.render(**kwargs)
    
    def run_prompt(self, name: str, agent=None, **kwargs) -> str:
        """
        渲染模板并用 Agent 执行
        
        参数:
            name: 模板名称
            agent: CodexAgent 实例（如果提供，会用 agent 执行）
            **kwargs: 模板变量值
        
        返回:
            执行结果字符串
        """
        prompt = self.render_prompt(name, **kwargs)
        
        if agent:
            # 如果有 agent，使用 agent 执行
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(agent.chat(prompt))
            return result
        else:
            # 没有 agent，只返回渲染后的提示词
            return prompt
    
    # ── 持久化 ──
    
    def _save_template(self, pt: PromptTemplate):
        """保存单个模板到文件"""
        filepath = os.path.join(self.storage_dir, f"{pt.name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(pt.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_templates(self):
        """从存储目录加载所有模板"""
        if not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    pt = PromptTemplate.from_dict(data)
                    self._templates[pt.name] = pt
                except Exception as e:
                    print(f"[CreateRunPrompt] 加载模板文件失败 {filename}: {e}")
    
    # ── 内置模板 ──
    
    def init_default_templates(self):
        """初始化一些内置模板"""
        defaults = [
            {
                "name": "code_generate",
                "template": "请用 {language} 编写一个程序，功能：{task}\n\n要求：\n1. 代码完整可运行\n2. 包含必要的注释\n3. 遵循 {language} 最佳实践",
                "description": "代码生成模板"
            },
            {
                "name": "code_debug",
                "template": "请帮我调试以下 {language} 代码：\n\n```{language}\n{code}\n```\n\n错误信息：{error}\n\n请分析原因并修复。",
                "description": "代码调试模板"
            },
            {
                "name": "code_explain",
                "template": "请用中文解释以下 {language} 代码的功能和逻辑：\n\n```{language}\n{code}\n```",
                "description": "代码解释模板"
            },
            {
                "name": "project_create",
                "template": "请帮我创建一个 {language} 项目，项目名称：{project_name}\n\n需求描述：{requirements}\n\n请生成完整的项目文件结构。",
                "description": "项目创建模板"
            },
            {
                "name": "code_refactor",
                "template": "请重构以下 {language} 代码，提高代码质量和可维护性：\n\n```{language}\n{code}\n```\n\n要求：\n1. 保持功能不变\n2. 提高可读性\n3. 优化性能\n4. 添加类型注解",
                "description": "代码重构模板"
            }
        ]
        
        for tpl in defaults:
            if tpl["name"] not in self._templates:
                self.create_template(**tpl)
    
    def __repr__(self) -> str:
        return f"CreateRunPrompt(templates={len(self._templates)})"
