# Notion 属性类型参考

## 目录
1. [属性值写入格式](#属性值写入格式)
2. [属性值读取格式](#属性值读取格式)
3. [数据库属性定义](#数据库属性定义)

---

## 属性值写入格式

用于 `pages.create()` 和 `pages.update()` 的 properties 参数。

### Title（标题）- 必需

```python
"Name": {
    "title": [
        {"text": {"content": "页面标题"}}
    ]
}
```

### Rich Text（富文本）

```python
"Description": {
    "rich_text": [
        {"text": {"content": "文本内容"}},
        {"text": {"content": "粗体"}, "annotations": {"bold": True}}
    ]
}
```

### Number（数字）

```python
"Price": {"number": 99.99}
"Count": {"number": 42}
"Empty": {"number": None}  # 清空
```

### Select（单选）

```python
"Status": {"select": {"name": "进行中"}}
"Category": {"select": None}  # 清空
```

### Multi-select（多选）

```python
"Tags": {
    "multi_select": [
        {"name": "标签A"},
        {"name": "标签B"}
    ]
}
"Tags": {"multi_select": []}  # 清空
```

### Date（日期）

```python
# 单日期
"Due Date": {
    "date": {"start": "2025-01-29"}
}

# 带时间
"Meeting": {
    "date": {"start": "2025-01-29T14:00:00"}
}

# 日期范围
"Duration": {
    "date": {
        "start": "2025-01-29",
        "end": "2025-02-05"
    }
}

# 带时区
"Event": {
    "date": {
        "start": "2025-01-29T14:00:00",
        "time_zone": "Asia/Shanghai"
    }
}

# 清空
"Due Date": {"date": None}
```

### Checkbox（复选框）

```python
"Done": {"checkbox": True}
"Active": {"checkbox": False}
```

### URL

```python
"Website": {"url": "https://example.com"}
"Link": {"url": None}  # 清空
```

### Email

```python
"Contact": {"email": "user@example.com"}
```

### Phone Number

```python
"Phone": {"phone_number": "+86 138 0000 0000"}
```

### People（人员）

```python
"Assignee": {
    "people": [
        {"id": "user_id_1"},
        {"id": "user_id_2"}
    ]
}
```

### Files（文件）

```python
"Attachments": {
    "files": [
        {
            "name": "document.pdf",
            "type": "external",
            "external": {"url": "https://example.com/doc.pdf"}
        }
    ]
}
```

### Relation（关联）

```python
"Related Tasks": {
    "relation": [
        {"id": "page_id_1"},
        {"id": "page_id_2"}
    ]
}
```

### Status（状态）- 特殊类型

```python
"Status": {
    "status": {"name": "In Progress"}
}
```

---

## 属性值读取格式

从 `pages.retrieve()` 返回的 properties 结构。

### Title

```python
page["properties"]["Name"]["title"][0]["text"]["content"]
# 或安全访问
title_array = page["properties"]["Name"]["title"]
title = title_array[0]["text"]["content"] if title_array else ""
```

### Rich Text

```python
rich_text_array = page["properties"]["Description"]["rich_text"]
text = "".join([rt["text"]["content"] for rt in rich_text_array])
```

### Number

```python
value = page["properties"]["Price"]["number"]  # float 或 None
```

### Select

```python
select_obj = page["properties"]["Status"]["select"]
value = select_obj["name"] if select_obj else None
```

### Multi-select

```python
multi = page["properties"]["Tags"]["multi_select"]
tags = [item["name"] for item in multi]
```

### Date

```python
date_obj = page["properties"]["Due Date"]["date"]
if date_obj:
    start = date_obj["start"]
    end = date_obj.get("end")
```

### Checkbox

```python
checked = page["properties"]["Done"]["checkbox"]  # bool
```

### URL / Email / Phone

```python
url = page["properties"]["Website"]["url"]
email = page["properties"]["Contact"]["email"]
phone = page["properties"]["Phone"]["phone_number"]
```

### People

```python
people = page["properties"]["Assignee"]["people"]
user_ids = [p["id"] for p in people]
```

### Relation

```python
relations = page["properties"]["Related"]["relation"]
page_ids = [r["id"] for r in relations]
```

### Formula（只读）

根据返回类型：
```python
formula = page["properties"]["Computed"]["formula"]
# formula["type"] 可能是 "string", "number", "boolean", "date"
value = formula[formula["type"]]
```

### Rollup（只读）

```python
rollup = page["properties"]["Total"]["rollup"]
# rollup["type"] 可能是 "number", "date", "array"
```

### Created/Last Edited Time（只读）

```python
created = page["properties"]["Created"]["created_time"]
edited = page["properties"]["Modified"]["last_edited_time"]
```

### Created/Last Edited By（只读）

```python
creator = page["properties"]["Creator"]["created_by"]
editor = page["properties"]["Editor"]["last_edited_by"]
```

---

## 数据库属性定义

用于 `databases.create()` 的属性 Schema 定义。

### 基本属性

```python
properties = {
    # Title - 必需，每个数据库都有
    "Name": {"title": {}},
    
    # Rich Text
    "Description": {"rich_text": {}},
    
    # Number
    "Price": {
        "number": {
            "format": "dollar"  # number, number_with_commas, percent, dollar, euro, etc.
        }
    },
    
    # Checkbox
    "Done": {"checkbox": {}},
    
    # URL
    "Website": {"url": {}},
    
    # Email
    "Contact": {"email": {}},
    
    # Phone
    "Phone": {"phone_number": {}},
    
    # Date
    "Due Date": {"date": {}},
    
    # People
    "Assignee": {"people": {}},
    
    # Files
    "Attachments": {"files": {}}
}
```

### Select / Multi-select

```python
properties = {
    "Status": {
        "select": {
            "options": [
                {"name": "待办", "color": "gray"},
                {"name": "进行中", "color": "blue"},
                {"name": "已完成", "color": "green"}
            ]
        }
    },
    "Tags": {
        "multi_select": {
            "options": [
                {"name": "重要", "color": "red"},
                {"name": "紧急", "color": "orange"},
                {"name": "常规", "color": "default"}
            ]
        }
    }
}
```

**可用颜色**：`default`, `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`

### Relation

```python
properties = {
    "Projects": {
        "relation": {
            "database_id": "related_database_id",
            "type": "single_property"  # 或 "dual_property"
        }
    }
}
```

### Formula

```python
properties = {
    "Days Until Due": {
        "formula": {
            "expression": "dateBetween(prop(\"Due Date\"), now(), \"days\")"
        }
    }
}
```

### Rollup

```python
properties = {
    "Total Tasks": {
        "rollup": {
            "relation_property_name": "Tasks",
            "rollup_property_name": "Name",
            "function": "count"  # sum, average, min, max, count, etc.
        }
    }
}
```

---

## 完整示例

### 创建任务数据库

```python
notion.databases.create(
    parent={"page_id": "parent_page_id"},
    title=[{"type": "text", "text": {"content": "任务管理"}}],
    initial_data_source={
        "properties": {
            "Task": {"title": {}},
            "Description": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "待办", "color": "gray"},
                        {"name": "进行中", "color": "blue"},
                        {"name": "已完成", "color": "green"}
                    ]
                }
            },
            "Priority": {
                "select": {
                    "options": [
                        {"name": "高", "color": "red"},
                        {"name": "中", "color": "yellow"},
                        {"name": "低", "color": "green"}
                    ]
                }
            },
            "Due Date": {"date": {}},
            "Assignee": {"people": {}},
            "Tags": {"multi_select": {}},
            "Done": {"checkbox": {}},
            "Effort": {"number": {"format": "number"}}
        }
    }
)
```

### 创建任务页面

```python
notion.pages.create(
    parent={"database_id": "database_id"},
    properties={
        "Task": {"title": [{"text": {"content": "完成 API 集成"}}]},
        "Description": {"rich_text": [{"text": {"content": "集成 Notion API"}}]},
        "Status": {"select": {"name": "进行中"}},
        "Priority": {"select": {"name": "高"}},
        "Due Date": {"date": {"start": "2025-02-01"}},
        "Tags": {"multi_select": [{"name": "开发"}, {"name": "API"}]},
        "Done": {"checkbox": False},
        "Effort": {"number": 8}
    }
)
```
