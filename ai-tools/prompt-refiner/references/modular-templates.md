# 模块化Prompt模板库

## 模块化设计原则

1. **单一职责**：每个模块只负责一个功能
2. **松耦合**：模块间通过变量占位符连接，可独立替换
3. **按需注入**：仅注入当前任务所需的模块

## 基础模块模板

### 角色设定模块

```
【角色设定】
你是一位{expertise_area}领域的专业{role_name}，具备以下能力：
- {capability_1}
- {capability_2}
- {capability_3}

你的沟通风格：{communication_style}
```

**变量说明**：
- `expertise_area`：专业领域，如"K12数学教育"
- `role_name`：角色名称，如"教学设计师"
- `capability_n`：核心能力描述
- `communication_style`：如"专业、耐心、循序渐进"

### 难度控制模块

```
【难度等级：{difficulty}】

{difficulty_description}

{difficulty_constraints}
```

**难度变量映射**：

| difficulty | difficulty_description | difficulty_constraints |
|------------|----------------------|----------------------|
| easy | 面向初学者，使用基础概念和简单示例 | 避免使用专业术语；步骤拆分要细致；多使用生活化类比 |
| middle | 面向有一定基础的学习者 | 可使用常见专业术语；适当提高抽象程度；引入标准解题方法 |
| difficult | 面向进阶学习者，强调深度理解 | 可使用专业术语；注重原理推导；引入拓展知识和变式题 |

### 任务描述模块

```
【任务说明】
{task_description}

【输入内容】
{input_description}

【预期输出】
{output_description}
```

### 约束条件模块

```
【约束条件】
1. {constraint_1}
2. {constraint_2}
3. {constraint_3}

【禁止行为】
- {forbidden_1}
- {forbidden_2}
```

### 输出格式模块

**JSON流式输出**：
```
【输出格式】
- 直接输出JSON，不要包含\`\`\`json或\`\`\`标记
- 每个JSON对象独占一行
- 必须包含order字段，从1开始递增

格式示例：
{"order": 1, ...}
{"order": 2, ...}
```

**文本流式输出**：
```
【输出格式】
使用Markdown格式输出，结构清晰。
代码块使用：
\`\`\`language
代码内容
\`\`\`
```

### Few-shot示例模块

```
【示例】

输入：{example_input_1}
输出：{example_output_1}

输入：{example_input_2}
输出：{example_output_2}
```

## 场景化组合模板

### 知识点提取场景

```python
KNOWLEDGE_EXTRACTION_PROMPT = """
{role_module}

{task_module}

{difficulty_module}

{output_format_module}

{constraints_module}

{examples_module}
"""

# 模块内容
role_module = """
【角色设定】
你是一位教育内容分析专家，擅长从教材中提取核心知识点。
"""

task_module = """
【任务说明】
从给定的教材内容中提取知识点。

【输入内容】
教材章节文本

【预期输出】
结构化的知识点列表
"""

output_format_module = """
【输出格式】
直接输出JSON，每行一个知识点对象：
{"order": 1, "knowledge_point": "...", "importance": "high|medium|low", "prerequisites": [...]}
"""
```

### 题目生成场景

```python
QUESTION_GENERATION_PROMPT = """
{role_module}

{difficulty_module}

{task_module}

{output_format_module}

{constraints_module}

{examples_module}
"""

# 难度模块按需选择
difficulty_modules = {
    "easy": """
【难度等级：基础】
生成适合初学者的题目：
- 直接考查单一知识点
- 计算步骤不超过3步
- 不设置干扰项陷阱
""",
    "middle": """
【难度等级：中等】
生成适合巩固练习的题目：
- 可综合2-3个知识点
- 计算步骤4-6步
- 可设置常见错误陷阱
""",
    "difficult": """
【难度等级：提高】
生成适合能力提升的题目：
- 综合多个知识点
- 需要多步推理
- 考查举一反三能力
"""
}
```

## 模块注入代码示例

```python
def build_prompt(
    task_type: str,
    difficulty: str = None,
    need_examples: bool = False,
    output_format: str = "json"
) -> str:
    """
    根据参数动态组装Prompt
    
    Args:
        task_type: 任务类型
        difficulty: 难度等级（可选）
        need_examples: 是否需要Few-shot示例
        output_format: 输出格式 json|text
    
    Returns:
        组装好的完整Prompt
    """
    modules = []
    
    # 基础模块（必选）
    modules.append(ROLE_MODULES[task_type])
    modules.append(TASK_MODULES[task_type])
    
    # 难度模块（可选）
    if difficulty:
        modules.append(DIFFICULTY_MODULES[difficulty])
    
    # 输出格式模块（必选）
    modules.append(OUTPUT_FORMAT_MODULES[output_format])
    
    # 约束模块（必选）
    modules.append(CONSTRAINTS_MODULE)
    
    # 示例模块（可选）
    if need_examples:
        modules.append(EXAMPLES_MODULES[task_type])
    
    return "\n\n".join(modules)
```
