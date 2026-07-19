"""
测试 qCreateRunPrompt 模块
"""
from prompts.create_run import CreateRunPrompt, PromptTemplate


def test_basic():
    """基本功能测试"""
    crp = CreateRunPrompt()
    
    # 1. 创建模板
    pt = crp.create_template(
        name="hello_world",
        template="用 {language} 写一个 {task} 程序",
        description="Hello World 生成器"
    )
    print(f"[✓] 创建模板: {pt.name}")
    print(f"    模板内容: {pt.template}")
    print(f"    变量: {pt.variables}")
    
    # 2. 渲染模板
    prompt = crp.render_prompt("hello_world", language="Python", task="Hello World")
    print(f"[✓] 渲染结果: {prompt}")
    assert prompt == "用 Python 写一个 Hello World 程序", f"渲染结果不对: {prompt}"
    
    # 3. 列出模板
    templates = crp.list_templates()
    print(f"[✓] 模板列表: {[t['name'] for t in templates]}")
    assert any(t['name'] == 'hello_world' for t in templates)
    
    # 4. 更新模板
    crp.update_template("hello_world", description="更新后的描述")
    pt2 = crp.get_template("hello_world")
    print(f"[✓] 更新描述: {pt2.description}")
    assert pt2.description == "更新后的描述"
    
    # 5. 删除模板
    crp.delete_template("hello_world")
    assert crp.get_template("hello_world") is None
    print(f"[✓] 删除模板成功")
    
    print("\n=== 所有基本测试通过! ===\n")


def test_default_templates():
    """内置模板测试"""
    crp = CreateRunPrompt()
    crp.init_default_templates()
    
    templates = crp.list_templates()
    print(f"[✓] 内置模板数量: {len(templates)}")
    
    for t in templates:
        print(f"    - {t['name']}: {t['description']} (变量: {t['variables']})")
    
    # 测试代码生成模板
    prompt = crp.render_prompt(
        "code_generate",
        language="Python",
        task="计算器"
    )
    print(f"\n[✓] code_generate 渲染结果:\n{prompt}\n")
    assert "Python" in prompt
    assert "计算器" in prompt
    
    print("=== 内置模板测试通过! ===\n")


def test_error_handling():
    """错误处理测试"""
    crp = CreateRunPrompt()
    
    # 重复创建
    crp.create_template("dup", "test {x}")
    try:
        crp.create_template("dup", "another")
        print("[✗] 应该抛出重复模板异常")
    except ValueError as e:
        print(f"[✓] 重复创建检测: {e}")
    
    # 获取不存在的模板
    assert crp.get_template("nonexistent") is None
    print(f"[✓] 获取不存在的模板返回 None")
    
    # 渲染缺少变量
    try:
        crp.render_prompt("dup")
        print("[✗] 应该抛出缺少变量异常")
    except ValueError as e:
        print(f"[✓] 缺少变量检测: {e}")
    
    # 空名称
    try:
        crp.create_template("", "test")
        print("[✗] 应该抛出空名称异常")
    except ValueError as e:
        print(f"[✓] 空名称检测: {e}")
    
    # 删除不存在的模板
    assert not crp.delete_template("nonexistent")
    print(f"[✓] 删除不存在的模板返回 False")
    
    print("=== 错误处理测试通过! ===\n")


def test_prompt_template_class():
    """PromptTemplate 类测试"""
    # 变量提取
    pt = PromptTemplate("test", "Hello {name}, you are {age} years old")
    assert pt.variables == ["name", "age"], f"变量提取失败: {pt.variables}"
    print(f"[✓] 变量提取: {pt.variables}")
    
    # 序列化
    data = pt.to_dict()
    assert data["name"] == "test"
    assert data["variables"] == ["name", "age"]
    print(f"[✓] 序列化: {data}")
    
    # 反序列化
    pt2 = PromptTemplate.from_dict(data)
    assert pt2.name == "test"
    assert pt2.variables == ["name", "age"]
    print(f"[✓] 反序列化: {pt2.name}, {pt2.variables}")
    
    print("=== PromptTemplate 类测试通过! ===\n")


if __name__ == "__main__":
    print("=" * 50)
    print("  qCreateRunPrompt 测试套件")
    print("=" * 50)
    print()
    
    test_basic()
    test_default_templates()
    test_error_handling()
    test_prompt_template_class()
    
    print("=" * 50)
    print("  全部测试通过! ✅")
    print("=" * 50)
