# JSON输出格式规范

## 核心原则

1. **流式友好**：每个JSON对象独占一行，便于逐行解析
2. **无包装标记**：开头结尾不含 \`\`\`json 或 \`\`\`
3. **顺序追踪**：必须包含order字段，从1递增
4. **嵌套标识**：嵌套结构使用qstart/qend标记边界

## 非嵌套结构（推荐）

### Prompt约束模板

```
【输出格式要求】
1. 直接输出JSON内容，开头和结尾不要包含\`\`\`json或\`\`\`等任何标记
2. 每个JSON对象必须独占一行，对象内部不换行
3. 每个对象必须包含order字段，从1开始连续递增
4. 确保JSON格式正确，所有字符串使用双引号

输出示例：
{"order": 1, "type": "xxx", "content": "..."}
{"order": 2, "type": "xxx", "content": "..."}
{"order": 3, "type": "xxx", "content": "..."}
```

### 场景示例

**知识点提取**：
```
{"order": 1, "knowledge_point": "勾股定理", "definition": "直角三角形中，两条直角边的平方和等于斜边的平方", "importance": "high"}
{"order": 2, "knowledge_point": "勾股定理逆定理", "definition": "如果三角形三边满足a²+b²=c²，则该三角形是直角三角形", "importance": "medium"}
```

**题目生成**：
```
{"order": 1, "question_type": "choice", "stem": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "B", "explanation": "..."}
{"order": 2, "question_type": "fill_blank", "stem": "...", "answer": "...", "explanation": "..."}
```

**知识问答**（文本流式，非JSON）：
```
直接输出Markdown格式的回答文本，使用标准代码块格式。
```

## 嵌套结构

### 适用场景

- 章节层级结构
- 树形知识图谱
- 多级目录生成

### Prompt约束模板

```
【输出格式要求】
1. 直接输出JSON内容，开头和结尾不要包含\`\`\`json或\`\`\`等任何标记
2. 每个JSON对象必须独占一行
3. 每个对象必须包含order字段，从1开始连续递增
4. 嵌套开始：添加 "qstart": true
5. 嵌套结束：添加 "qend": true
6. qstart和qend必须配对出现

嵌套示例：
{"order": 1, "qstart": true, "type": "chapter", "title": "第一章"}
{"order": 2, "type": "section", "content": "1.1 节内容"}
{"order": 3, "type": "section", "content": "1.2 节内容"}
{"order": 4, "qend": true}
{"order": 5, "qstart": true, "type": "chapter", "title": "第二章"}
{"order": 6, "type": "section", "content": "2.1 节内容"}
{"order": 7, "qend": true}
```

### 场景示例

**课程大纲生成**：
```
{"order": 1, "qstart": true, "type": "unit", "title": "第一单元：整数的认识", "learning_goals": ["理解整数概念", "掌握整数比较"]}
{"order": 2, "qstart": true, "type": "lesson", "title": "第1课：认识正整数"}
{"order": 3, "type": "activity", "name": "导入活动", "duration": "5min", "description": "..."}
{"order": 4, "type": "activity", "name": "核心讲解", "duration": "15min", "description": "..."}
{"order": 5, "qend": true}
{"order": 6, "qstart": true, "type": "lesson", "title": "第2课：认识负整数"}
{"order": 7, "type": "activity", "name": "导入活动", "duration": "5min", "description": "..."}
{"order": 8, "qend": true}
{"order": 9, "qend": true}
```

## 前端解析参考

### 非嵌套结构解析

```javascript
// 逐行解析
function parseStreamLine(line) {
    if (!line.trim()) return null;
    try {
        return JSON.parse(line);
    } catch (e) {
        console.error('JSON parse error:', e);
        return null;
    }
}

// 流式处理
async function handleStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 保留不完整的行
        
        for (const line of lines) {
            const obj = parseStreamLine(line);
            if (obj) {
                handleObject(obj); // 处理解析出的对象
            }
        }
    }
}
```

### 嵌套结构解析

```javascript
function parseNestedStream(lines) {
    const stack = [];
    const result = [];
    
    for (const line of lines) {
        const obj = JSON.parse(line);
        
        if (obj.qstart) {
            const node = { ...obj, children: [] };
            delete node.qstart;
            
            if (stack.length > 0) {
                stack[stack.length - 1].children.push(node);
            } else {
                result.push(node);
            }
            stack.push(node);
        } else if (obj.qend) {
            stack.pop();
        } else {
            if (stack.length > 0) {
                stack[stack.length - 1].children.push(obj);
            } else {
                result.push(obj);
            }
        }
    }
    
    return result;
}
```

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|-----|-----|---------|
| 前端解析失败 | 输出包含\`\`\`json标记 | Prompt中明确禁止输出标记 |
| JSON格式错误 | 对象内部换行 | 强调每个对象必须单行 |
| 顺序混乱 | 缺少order字段 | 必须要求order从1递增 |
| 嵌套解析错误 | qstart/qend不配对 | 检查Prompt示例是否正确 |
| 数量不符 | 未完整输出 | 添加完整性约束 |
