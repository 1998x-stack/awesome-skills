# Notion 数据库过滤器参考

## 目录
1. [基本过滤器结构](#基本过滤器结构)
2. [复合过滤器](#复合过滤器)
3. [各属性类型过滤器](#各属性类型过滤器)
4. [常见过滤模式](#常见过滤模式)

---

## 基本过滤器结构

```python
filter = {
    "property": "属性名称",
    "属性类型": {
        "条件": "值"
    }
}
```

---

## 复合过滤器

**AND 条件**：
```python
filter = {
    "and": [
        {"property": "Status", "select": {"equals": "进行中"}},
        {"property": "Priority", "select": {"equals": "高"}}
    ]
}
```

**OR 条件**：
```python
filter = {
    "or": [
        {"property": "Status", "select": {"equals": "待办"}},
        {"property": "Status", "select": {"equals": "进行中"}}
    ]
}
```

**嵌套条件**：
```python
filter = {
    "and": [
        {"property": "Archived", "checkbox": {"equals": False}},
        {
            "or": [
                {"property": "Status", "select": {"equals": "紧急"}},
                {"property": "Priority", "select": {"equals": "高"}}
            ]
        }
    ]
}
```

---

## 各属性类型过滤器

### Title / Rich Text

| 条件 | 示例 |
|------|------|
| `equals` | `{"title": {"equals": "精确标题"}}` |
| `does_not_equal` | `{"title": {"does_not_equal": "排除标题"}}` |
| `contains` | `{"rich_text": {"contains": "关键词"}}` |
| `does_not_contain` | `{"rich_text": {"does_not_contain": "排除词"}}` |
| `starts_with` | `{"title": {"starts_with": "前缀"}}` |
| `ends_with` | `{"title": {"ends_with": "后缀"}}` |
| `is_empty` | `{"title": {"is_empty": True}}` |
| `is_not_empty` | `{"title": {"is_not_empty": True}}` |

### Number

| 条件 | 示例 |
|------|------|
| `equals` | `{"number": {"equals": 100}}` |
| `does_not_equal` | `{"number": {"does_not_equal": 0}}` |
| `greater_than` | `{"number": {"greater_than": 50}}` |
| `less_than` | `{"number": {"less_than": 100}}` |
| `greater_than_or_equal_to` | `{"number": {"greater_than_or_equal_to": 10}}` |
| `less_than_or_equal_to` | `{"number": {"less_than_or_equal_to": 99}}` |
| `is_empty` | `{"number": {"is_empty": True}}` |
| `is_not_empty` | `{"number": {"is_not_empty": True}}` |

### Select

| 条件 | 示例 |
|------|------|
| `equals` | `{"select": {"equals": "选项名"}}` |
| `does_not_equal` | `{"select": {"does_not_equal": "排除选项"}}` |
| `is_empty` | `{"select": {"is_empty": True}}` |
| `is_not_empty` | `{"select": {"is_not_empty": True}}` |

### Multi-select

| 条件 | 示例 |
|------|------|
| `contains` | `{"multi_select": {"contains": "标签A"}}` |
| `does_not_contain` | `{"multi_select": {"does_not_contain": "标签B"}}` |
| `is_empty` | `{"multi_select": {"is_empty": True}}` |
| `is_not_empty` | `{"multi_select": {"is_not_empty": True}}` |

### Date

| 条件 | 示例 |
|------|------|
| `equals` | `{"date": {"equals": "2025-01-29"}}` |
| `before` | `{"date": {"before": "2025-02-01"}}` |
| `after` | `{"date": {"after": "2025-01-01"}}` |
| `on_or_before` | `{"date": {"on_or_before": "2025-01-31"}}` |
| `on_or_after` | `{"date": {"on_or_after": "2025-01-01"}}` |
| `is_empty` | `{"date": {"is_empty": True}}` |
| `is_not_empty` | `{"date": {"is_not_empty": True}}` |
| `past_week` | `{"date": {"past_week": {}}}` |
| `past_month` | `{"date": {"past_month": {}}}` |
| `past_year` | `{"date": {"past_year": {}}}` |
| `this_week` | `{"date": {"this_week": {}}}` |
| `next_week` | `{"date": {"next_week": {}}}` |
| `next_month` | `{"date": {"next_month": {}}}` |
| `next_year` | `{"date": {"next_year": {}}}` |

### Checkbox

| 条件 | 示例 |
|------|------|
| `equals` | `{"checkbox": {"equals": True}}` |
| `does_not_equal` | `{"checkbox": {"does_not_equal": False}}` |

### People

| 条件 | 示例 |
|------|------|
| `contains` | `{"people": {"contains": "user_id"}}` |
| `does_not_contain` | `{"people": {"does_not_contain": "user_id"}}` |
| `is_empty` | `{"people": {"is_empty": True}}` |
| `is_not_empty` | `{"people": {"is_not_empty": True}}` |

### Relation

| 条件 | 示例 |
|------|------|
| `contains` | `{"relation": {"contains": "page_id"}}` |
| `does_not_contain` | `{"relation": {"does_not_contain": "page_id"}}` |
| `is_empty` | `{"relation": {"is_empty": True}}` |
| `is_not_empty` | `{"relation": {"is_not_empty": True}}` |

### Formula

根据公式返回类型使用对应过滤器：
- 返回文本：使用 `rich_text` 条件
- 返回数字：使用 `number` 条件
- 返回日期：使用 `date` 条件
- 返回布尔：使用 `checkbox` 条件

---

## 常见过滤模式

**未完成任务**：
```python
{"property": "Done", "checkbox": {"equals": False}}
```

**本周到期**：
```python
{"property": "Due Date", "date": {"this_week": {}}}
```

**特定负责人的高优先级任务**：
```python
{
    "and": [
        {"property": "Assignee", "people": {"contains": "user_id"}},
        {"property": "Priority", "select": {"equals": "高"}}
    ]
}
```

**包含特定标签**：
```python
{
    "or": [
        {"property": "Tags", "multi_select": {"contains": "重要"}},
        {"property": "Tags", "multi_select": {"contains": "紧急"}}
    ]
}
```

**过期但未完成**：
```python
{
    "and": [
        {"property": "Due Date", "date": {"before": "2025-01-29"}},
        {"property": "Status", "select": {"does_not_equal": "已完成"}}
    ]
}
```
