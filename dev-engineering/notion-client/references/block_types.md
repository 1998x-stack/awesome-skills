# Notion 块类型参考

## 目录
1. [Rich Text 结构](#rich-text-结构)
2. [文本块类型](#文本块类型)
3. [列表块类型](#列表块类型)
4. [媒体块类型](#媒体块类型)
5. [高级块类型](#高级块类型)
6. [完整示例](#完整示例)

---

## Rich Text 结构

所有文本内容使用 rich_text 数组：

```python
rich_text = [
    {
        "type": "text",
        "text": {
            "content": "文本内容",
            "link": {"url": "https://example.com"}  # 可选
        },
        "annotations": {  # 可选，默认全为 False
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default"  # red, blue, green, yellow, orange, pink, purple, gray, brown
        }
    }
]
```

**颜色选项**：`default`, `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`
以及背景色：`gray_background`, `brown_background` 等

---

## 文本块类型

### Paragraph（段落）

```python
{
    "object": "block",
    "type": "paragraph",
    "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "段落内容"}}],
        "color": "default"
    }
}
```

### Heading 1/2/3（标题）

```python
{
    "object": "block",
    "type": "heading_1",  # 或 heading_2, heading_3
    "heading_1": {
        "rich_text": [{"type": "text", "text": {"content": "一级标题"}}],
        "is_toggleable": False,  # True 时可折叠
        "color": "default"
    }
}
```

### Quote（引用）

```python
{
    "object": "block",
    "type": "quote",
    "quote": {
        "rich_text": [{"type": "text", "text": {"content": "引用内容"}}],
        "color": "default"
    }
}
```

### Callout（标注）

```python
{
    "object": "block",
    "type": "callout",
    "callout": {
        "rich_text": [{"type": "text", "text": {"content": "标注内容"}}],
        "icon": {"emoji": "💡"},  # 或 {"external": {"url": "..."}}
        "color": "gray_background"
    }
}
```

### Code（代码块）

```python
{
    "object": "block",
    "type": "code",
    "code": {
        "rich_text": [{"type": "text", "text": {"content": "print('Hello')"}}],
        "language": "python",  # javascript, typescript, java, c, cpp, html, css, sql 等
        "caption": []  # 可选标题
    }
}
```

**支持语言**：`python`, `javascript`, `typescript`, `java`, `c`, `cpp`, `csharp`, `go`, `rust`, `ruby`, `php`, `swift`, `kotlin`, `scala`, `r`, `sql`, `html`, `css`, `json`, `yaml`, `xml`, `markdown`, `bash`, `shell`, `powershell` 等

### Divider（分隔线）

```python
{
    "object": "block",
    "type": "divider",
    "divider": {}
}
```

---

## 列表块类型

### Bulleted List Item（无序列表）

```python
{
    "object": "block",
    "type": "bulleted_list_item",
    "bulleted_list_item": {
        "rich_text": [{"type": "text", "text": {"content": "列表项"}}],
        "color": "default"
    }
}
```

### Numbered List Item（有序列表）

```python
{
    "object": "block",
    "type": "numbered_list_item",
    "numbered_list_item": {
        "rich_text": [{"type": "text", "text": {"content": "列表项"}}],
        "color": "default"
    }
}
```

### To-do（待办事项）

```python
{
    "object": "block",
    "type": "to_do",
    "to_do": {
        "rich_text": [{"type": "text", "text": {"content": "待办事项"}}],
        "checked": False,
        "color": "default"
    }
}
```

### Toggle（折叠块）

```python
{
    "object": "block",
    "type": "toggle",
    "toggle": {
        "rich_text": [{"type": "text", "text": {"content": "点击展开"}}],
        "color": "default"
        # children 通过 blocks.children.append 添加
    }
}
```

---

## 媒体块类型

### Image（图片）

```python
# 外部链接
{
    "object": "block",
    "type": "image",
    "image": {
        "type": "external",
        "external": {"url": "https://example.com/image.png"}
    }
}

# Notion 托管
{
    "object": "block",
    "type": "image",
    "image": {
        "type": "file",
        "file": {"url": "notion_file_url", "expiry_time": "..."}
    }
}
```

### Video（视频）

```python
{
    "object": "block",
    "type": "video",
    "video": {
        "type": "external",
        "external": {"url": "https://www.youtube.com/watch?v=..."}
    }
}
```

### File（文件）

```python
{
    "object": "block",
    "type": "file",
    "file": {
        "type": "external",
        "external": {"url": "https://example.com/doc.pdf"},
        "caption": [],
        "name": "document.pdf"
    }
}
```

### Bookmark（书签）

```python
{
    "object": "block",
    "type": "bookmark",
    "bookmark": {
        "url": "https://example.com",
        "caption": []
    }
}
```

### Embed（嵌入）

```python
{
    "object": "block",
    "type": "embed",
    "embed": {
        "url": "https://twitter.com/..."
    }
}
```

### PDF

```python
{
    "object": "block",
    "type": "pdf",
    "pdf": {
        "type": "external",
        "external": {"url": "https://example.com/doc.pdf"}
    }
}
```

---

## 高级块类型

### Table（表格）

创建表格需要先创建 table 块，再添加 table_row 子块：

```python
# 1. 创建表格
table_block = {
    "object": "block",
    "type": "table",
    "table": {
        "table_width": 3,  # 列数
        "has_column_header": True,
        "has_row_header": False
    }
}

# 2. 添加表格行
table_row = {
    "object": "block",
    "type": "table_row",
    "table_row": {
        "cells": [
            [{"type": "text", "text": {"content": "列1"}}],
            [{"type": "text", "text": {"content": "列2"}}],
            [{"type": "text", "text": {"content": "列3"}}]
        ]
    }
}
```

### Equation（公式）

```python
{
    "object": "block",
    "type": "equation",
    "equation": {
        "expression": "E = mc^2"  # LaTeX 格式
    }
}
```

### Table of Contents（目录）

```python
{
    "object": "block",
    "type": "table_of_contents",
    "table_of_contents": {
        "color": "default"
    }
}
```

### Breadcrumb（面包屑）

```python
{
    "object": "block",
    "type": "breadcrumb",
    "breadcrumb": {}
}
```

### Link to Page（页面链接）

```python
{
    "object": "block",
    "type": "link_to_page",
    "link_to_page": {
        "type": "page_id",
        "page_id": "target_page_id"
    }
}
```

### Column List（分栏）

```python
{
    "object": "block",
    "type": "column_list",
    "column_list": {}
    # children 是 column 块
}

{
    "object": "block",
    "type": "column",
    "column": {}
    # children 是该列的内容块
}
```

### Synced Block（同步块）

```python
# 原始块
{
    "object": "block",
    "type": "synced_block",
    "synced_block": {
        "synced_from": None  # 原始块
    }
}

# 引用块
{
    "object": "block",
    "type": "synced_block",
    "synced_block": {
        "synced_from": {
            "type": "block_id",
            "block_id": "original_block_id"
        }
    }
}
```

---

## 完整示例

创建包含多种块类型的页面：

```python
notion.blocks.children.append(
    block_id="page_id",
    children=[
        # 标题
        {"object": "block", "type": "heading_1", "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "项目概述"}}]
        }},
        # 段落
        {"object": "block", "type": "paragraph", "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": "这是一个"}},
                {"type": "text", "text": {"content": "重要"}, "annotations": {"bold": True}},
                {"type": "text", "text": {"content": "项目。"}}
            ]
        }},
        # 分隔线
        {"object": "block", "type": "divider", "divider": {}},
        # 待办列表
        {"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "待办事项"}}]
        }},
        {"object": "block", "type": "to_do", "to_do": {
            "rich_text": [{"type": "text", "text": {"content": "完成设计"}}],
            "checked": True
        }},
        {"object": "block", "type": "to_do", "to_do": {
            "rich_text": [{"type": "text", "text": {"content": "开发实现"}}],
            "checked": False
        }},
        # 代码块
        {"object": "block", "type": "code", "code": {
            "rich_text": [{"type": "text", "text": {"content": "def hello():\n    print('Hello')"}}],
            "language": "python"
        }},
        # 标注
        {"object": "block", "type": "callout", "callout": {
            "rich_text": [{"type": "text", "text": {"content": "注意：截止日期为下周五"}}],
            "icon": {"emoji": "⚠️"},
            "color": "yellow_background"
        }}
    ]
)
```
